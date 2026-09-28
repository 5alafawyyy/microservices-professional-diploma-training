#!/usr/bin/env bash
# verify-environment.sh — checks every tool this training needs, with evidence.
# Usage: ./scripts/verify-environment.sh
# Exit code: 0 = all REQUIRED-for-now tools present, 1 = something required is missing.
set -u

PASS=0; MISS=0; OPT=0

line() { printf '%-30s %-12s %s\n' "$1" "$2" "$3"; }

echo "=============================================================="
echo " Environment verification — $(date '+%Y-%m-%d %H:%M')"
echo " Statuses: PASS | MISSING | OPTIONAL-MISSING (not needed yet)"
echo "=============================================================="
line "TOOL" "STATUS" "DETAIL"
echo "--------------------------------------------------------------"

# --- JDK 21 -----------------------------------------------------
if [ -n "${JAVA_HOME:-}" ] && [ -x "${JAVA_HOME}/bin/java" ]; then
  JVER="$("${JAVA_HOME}/bin/java" -version 2>&1 | head -1)"
  if printf '%s' "$JVER" | grep -q '"21'; then
    line "JDK (via JAVA_HOME)" "PASS" "$JVER"
    PASS=$((PASS+1))
  else
    line "JDK (via JAVA_HOME)" "MISSING" "JAVA_HOME=${JAVA_HOME} — expected 21, got: ${JVER}"
    MISS=$((MISS+1))
  fi
else
  line "JDK (via JAVA_HOME)" "MISSING" "JAVA_HOME not set — install JDK 21 and set JAVA_HOME"
  MISS=$((MISS+1))
fi

# Cosmetic: what plain `java` on PATH resolves to
if command -v java >/dev/null 2>&1; then
  PVER="$(java -version 2>&1 | head -1)"
  case "$PVER" in
    *'"21'*) : ;;
    *) line "java on PATH (cosmetic)" "NOTE" "PATH java differs from JAVA_HOME: ${PVER}" ;;
  esac
fi

# --- Maven ------------------------------------------------------
if command -v mvn >/dev/null 2>&1; then
  MVER="$(mvn -v 2>/dev/null | head -1)"
  MJVER="$(mvn -v 2>/dev/null | grep -i 'Java version' | head -1)"
  if printf '%s' "$MVER" | grep -Eq '3\.(9|[1-9][0-9])'; then
    line "Maven >= 3.9" "PASS" "${MVER} | ${MJVER}"
    PASS=$((PASS+1))
  else
    line "Maven >= 3.9" "MISSING" "${MVER:-mvn found but version unreadable}"
    MISS=$((MISS+1))
  fi
else
  line "Maven >= 3.9" "MISSING" "install Maven and put mvn on PATH"
  MISS=$((MISS+1))
fi

# --- Git --------------------------------------------------------
if command -v git >/dev/null 2>&1; then
  line "Git" "PASS" "$(git --version)"
  PASS=$((PASS+1))
else
  line "Git" "MISSING" "install Git"
  MISS=$((MISS+1))
fi

# --- Docker + Compose ------------------------------------------
if command -v docker >/dev/null 2>&1; then
  line "Docker CLI" "PASS" "$(docker --version)"
  PASS=$((PASS+1))
  if docker info >/dev/null 2>&1; then
    line "Docker daemon" "PASS" "running"
    PASS=$((PASS+1))
  else
    line "Docker daemon" "MISSING" "start Docker Desktop"
    MISS=$((MISS+1))
  fi
  if docker compose version >/dev/null 2>&1; then
    line "Docker Compose v2" "PASS" "$(docker compose version --short 2>/dev/null)"
    PASS=$((PASS+1))
  else
    line "Docker Compose v2" "MISSING" "docker compose plugin not available"
    MISS=$((MISS+1))
  fi
else
  line "Docker CLI" "MISSING" "install Docker Desktop"
  MISS=$((MISS+1))
fi

# --- curl -------------------------------------------------------
if command -v curl >/dev/null 2>&1; then
  line "curl" "PASS" "$(curl --version | head -1 | cut -d' ' -f1-2)"
  PASS=$((PASS+1))
else
  line "curl" "MISSING" "install curl — labs use it for every acceptance check"
  MISS=$((MISS+1))
fi

# --- Optional / later phases -----------------------------------
check_optional() { # name, command, when
  if command -v "$2" >/dev/null 2>&1; then
    line "$1" "PASS" "$(command -v "$2")"
  else
    line "$1" "OPTIONAL-MISSING" "needed $3"
    OPT=$((OPT+1))
  fi
}
check_optional "jq"      jq      "for JSON parsing in checks (nice to have now)"
check_optional "kubectl" kubectl "Phase 2 / Session 15 (Kubernetes)"
check_optional "helm"    helm    "Phase 3 (Helm packaging)"
check_optional "istioctl" istioctl "Phase 3 / Session 21 (Istio)"
check_optional "k6"      k6      "Phase 3 / Session 23 (load testing)"
check_optional "gh"      gh      "optional — GitHub CLI convenience"

# --- Kubernetes cluster (Phase 2) ------------------------------
if command -v kubectl >/dev/null 2>&1; then
  if kubectl config get-contexts -o name 2>/dev/null | grep -q .; then
    line "K8s cluster context" "PASS" "$(kubectl config current-context 2>/dev/null)"
  else
    line "K8s cluster context" "OPTIONAL-MISSING" "no context yet — enable Docker Desktop Kubernetes before Session 15"
    OPT=$((OPT+1))
  fi
fi

# --- Port landscape (informational) ----------------------------
echo "--------------------------------------------------------------"
echo "Ports currently listening (target map: 8080-8085, 8761, 8888, 5432, 6379, 9092):"
for P in 8080 8081 8082 8083 8084 8085 8761 8888 5432 6379 9092 9411; do
  if curl -s -o /dev/null -m 1 "http://localhost:${P}" || curl -s -o /dev/null -m 1 -k "https://localhost:${P}"; then
    echo "  port ${P}: IN USE"
  fi
done
echo "  (ports not listed above are free)"

echo "=============================================================="
echo " SUMMARY: ${PASS} PASS | ${MISS} MISSING (required) | ${OPT} OPTIONAL-MISSING"
if [ "$MISS" -gt 0 ]; then
  echo " RESULT: BLOCKED — install the MISSING tools above before Lab 1."
  echo "  See docs/roadmap/PREREQUISITES.md for exact install commands."
  exit 1
fi
echo " RESULT: PASS — environment ready for Phase 1."
exit 0
