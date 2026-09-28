#!/usr/bin/env bash
# reset-lab.sh — returns the environment to a clean state between labs.
#
# Default (safe):      ./scripts/reset-lab.sh              -> stop containers, show git status
# Discard local edits:  ./scripts/reset-lab.sh --discard    -> also git restore + clean (typed confirmation)
# Wipe data volumes:    ./scripts/reset-lab.sh --wipe-data  -> also docker compose down -v (typed confirmation)
#
# The destructive modes demand you type an exact word. Nothing is deleted silently.
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLATFORM="${ROOT}/platform/ecommerce-platform"
MODE="${1:---safe}"

echo "== reset-lab: mode ${MODE} =="

if [ ! -d "${PLATFORM}" ]; then
  echo "platform directory not found: ${PLATFORM}" >&2
  exit 1
fi

# 1. Stop application containers (never removes volumes by default)
if [ -f "${PLATFORM}/docker-compose.yml" ]; then
  echo "-- docker compose down (volumes kept)"
  (cd "${PLATFORM}" && docker compose down) || echo "   (compose down reported an issue — is the daemon running?)"
else
  echo "-- no docker-compose.yml yet (before Lab 1) — skipping containers"
fi

# 2. Show repository state
echo "-- git status"
if git -C "${ROOT}" rev-parse --git-dir >/dev/null 2>&1; then
  git -C "${ROOT}" status --short
  echo "-- last commit"
  git -C "${ROOT}" log -1 --oneline 2>/dev/null || echo "   (no commits yet)"
else
  echo "   repo is not a git repository"
fi

case "$MODE" in
  --safe|"")
    echo
    echo "Safe reset done. Working tree untouched."
    echo "Hints:"
    echo "  - re-run a lab acceptance check:  ./scripts/verify-lab.sh 01"
    echo "  - discard local edits:            ./scripts/reset-lab.sh --discard"
    echo "  - wipe database/cache volumes:    ./scripts/reset-lab.sh --wipe-data"
    ;;

  --discard)
    echo
    echo "About to discard ALL uncommitted changes under ${ROOT}."
    echo "This runs: git restore . && git clean -fd  (untracked files included)."
    read -r -p "Type DISCARD to continue: " CONFIRM
    if [ "${CONFIRM}" = "DISCARD" ]; then
      git -C "${ROOT}" restore . && git -C "${ROOT}" clean -fd
      echo "Working tree reset to the last commit."
      git -C "${ROOT}" status --short
    else
      echo "Aborted — nothing discarded."
      exit 1
    fi
    ;;

  --wipe-data)
    echo
    echo "About to REMOVE docker volumes (postgres data, redis, kafka) via 'docker compose down -v'."
    echo "This deletes local database contents permanently."
    read -r -p "Type WIPE to continue: " CONFIRM
    if [ "${CONFIRM}" = "WIPE" ]; then
      (cd "${PLATFORM}" && docker compose down -v)
      echo "Volumes removed. Next 'docker compose up -d' starts from an empty database."
    else
      echo "Aborted — volumes kept."
      exit 1
    fi
    ;;

  * )
    echo "Unknown mode: ${MODE}" >&2
    echo "Usage: ./scripts/reset-lab.sh [--discard|--wipe-data]" >&2
    exit 2 ;;
esac
