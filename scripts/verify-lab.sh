#!/usr/bin/env bash
# verify-lab.sh — runs the automated slice of a lab's acceptance criteria.
# Usage: ./scripts/verify-lab.sh <lab>      e.g. ./scripts/verify-lab.sh 01
#        SKIP_TESTS=1 ./scripts/verify-lab.sh 01   (skip the mvm test phase)
# Exit code 0 = every automated check PASSed.
#
# Anything that needs a request body or log inspection is printed as MANUAL —
# the full acceptance list for each lab lives in docs/roadmap/SESSION_TO_LAB_MAP.md.
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLATFORM="${ROOT}/platform/ecommerce-platform"
LAB="${1:-}"

PASS=0; FAIL=0; MANUAL=0

status() { printf '  %-62s %s\n' "$1" "$2"; }
ok()     { status "$1" "PASS"; PASS=$((PASS+1)); }
bad()    { status "$1" "FAIL${2:+ ($2)}"; FAIL=$((FAIL+1)); }
manual() { status "$1" "MANUAL"; MANUAL=$((MANUAL+1)); }

http()      { curl -s -o /dev/null -w '%{http_code}' -m 8 "$@"; }
body()      { curl -s -m 8 "$@"; }
port_alive() { curl -s -o /dev/null -m 3 "http://localhost:$1"; }

check_code()  { # description expected actual
  if [ "$2" = "$3" ]; then ok "$1"; else bad "$1" "expected ${2}, got ${3}"; fi
}
check_has()   { # description needle haystack
  case "$3" in *"$2"*) ok "$1" ;; *) bad "$1" "missing '${2}'" ;; esac
}
check_mvn()   { # service-dir-name
  if [ "${SKIP_TESTS:-0}" = "1" ]; then manual "mvn test in $1 (SKIP_TESTS=1)"; return; fi
  if [ ! -d "${PLATFORM}/$1" ]; then bad "mvn test in $1" "directory not found"; return; fi
  if (cd "${PLATFORM}/$1" && mvn -q test >/dev/null 2>&1); then ok "mvn test green in $1"; else bad "mvn test in $1" "tests failed — run mvn test manually for the report"; fi
}
check_eureka() { # APP-NAME
  if body "http://localhost:8761/eureka/apps" | grep -q "$1"; then ok "$1 registered in Eureka"; else bad "$1 registered in Eureka" "not found on :8761"; fi
}
check_compose_healthy() { # service
  if (cd "${PLATFORM}" && docker compose ps "$1" 2>/dev/null | grep -qi healthy); then ok "docker compose: $1 healthy"; else bad "docker compose: $1 healthy" "run docker compose up -d first"; fi
}

hdr() { echo "== Lab ${LAB}: $1 =="; echo "   platform: ${PLATFORM}"; }

case "$LAB" in
"" )
  echo "Usage: ./scripts/verify-lab.sh <lab>"
  echo "Available: 01 02 03 04 05 06 07 08   (Lab 1 … Lab 6A)"
  exit 0 ;;

01 )
  hdr "Product Service + Eureka + Config (Session 1)"
  check_compose_healthy postgres
  check_has "config-server /actuator/health = UP" '"status":"UP"' "$(body http://localhost:8888/actuator/health)"
  check_eureka "PRODUCT-SERVICE"
  check_code "GET /api/v1/products -> 200" 200 "$(http http://localhost:8081/api/v1/products)"
  check_code "POST /api/v1/products -> 201" 201 "$(http -X POST http://localhost:8081/api/v1/products -H 'Content-Type: application/json' -d '{"name":"verify-lab","price":9.99,"quantity":1}')"
  check_code "GET nonexistent id -> 404" 404 "$(http http://localhost:8081/api/v1/products/999999)"
  check_mvn product-service
  manual "commit message: session-01: add-product-service-eureka-config"
  ;;

02 )
  hdr "API Gateway + Product route (Session 2, Lab 2A)"
  check_has "gateway /actuator/health = UP" '"status":"UP"' "$(body http://localhost:8080/actuator/health)"
  check_eureka "API-GATEWAY"
  check_code "GET via gateway /api/v1/products -> 200" 200 "$(http http://localhost:8080/api/v1/products)"
  if curl -s -D - -o /dev/null -m 8 http://localhost:8080/api/v1/products | grep -qi 'x-platform:.*microservices-pro'; then
    ok "response header X-Platform: microservices-pro"
  else
    bad "response header X-Platform: microservices-pro"
  fi
  check_mvn api-gateway
  manual "gateway console shows [GATEWAY] GET /api/v1/products"
  manual "commit message: session-02: add-api-gateway-with-product-route-and-logging-filter"
  ;;

03 )
  hdr "JWT Auth Filter + Rate Limiting (Session 3, Lab 2B)"
  check_code "GET /api/v1/products no token -> 200 (public)" 200 "$(http http://localhost:8080/api/v1/products)"
  check_code "POST /api/v1/products no token -> 401" 401 "$(http -X POST http://localhost:8080/api/v1/products -H 'Content-Type: application/json' -d '{"name":"x","price":1}')"
  JAR="${PLATFORM}/tools/jwt-generator/target/jwt-generator-1.0.0.jar"
  if [ -f "$JAR" ]; then
    TOKEN="$(export JWT_SECRET="${JWT_SECRET:-microservices-pro-course-dev-secret-key-2026-min-256-bits}"; java -jar "$JAR" --username=verify --roles=ROLE_ADMIN 2>/dev/null | tr -d '\r\n' | tail -c 400)"
    if [ -n "$TOKEN" ]; then
      check_code "POST with valid JWT -> 201" 201 "$(http -X POST http://localhost:8080/api/v1/products -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{"name":"jwt-check","price":2}')"
    else
      manual "could not extract token from jwt-generator output"
    fi
  else
    manual "build tools/jwt-generator first (see docs/labs/lab-03-jwt-testing*)"
  fi
  echo "  rate-limit loop (25 requests):"
  CODES=""
  for i in $(seq 1 25); do CODES="${CODES}$(http http://localhost:8080/api/v1/products) "; done
  if printf '%s' "$CODES" | grep -q 429; then ok "rate limiter produced a 429 within 25 requests"; else bad "rate limiter produced a 429 within 25 requests" "codes: ${CODES}"; fi
  manual "GET response shows X-RateLimit-Remaining header"
  check_mvn api-gateway
  manual "commit message: session-03: add-jwt-auth-filter-and-rate-limiting"
  ;;

04 )
  hdr "Circuit Breaker + Retry on Order→Payment (Session 4, Lab 3A)"
  check_has "order /actuator/health = UP" '"status":"UP"' "$(body http://localhost:8082/actuator/health)"
  check_has "circuitbreaker 'paymentService' exposed" 'paymentService' "$(body http://localhost:8082/actuator/circuitbreakers)"
  manual "POST /api/orders -> CONFIRMED on payment success, PENDING on failure"
  manual "state OPEN visible in /actuator/circuitbreakers after 5+ failures; HALF_OPEN after 5s"
  manual "logs show [RETRY] Attempt #1/#2/#3 with 500ms -> 1000ms gaps"
  check_mvn order-service
  manual "commit message: session-04: add-circuit-breaker-and-retry-on-order-payment"
  ;;

05 )
  hdr "Bulkhead + TimeLimiter (Session 5, Lab 3B)"
  check_has "bulkhead 'paymentService' exposed" 'paymentService' "$(body http://localhost:8082/actuator/bulkheads)"
  check_eureka "ORDER-SERVICE"
  manual "15 concurrent POST /api/orders -> ~10 served, ~5 QUEUED fallbacks"
  manual "payment.delay-ms=3000 -> PENDING within ~2s (TimeLimiter)"
  manual "logs show [BULKHEAD] / [TIMEOUT] prefixes"
  check_mvn order-service
  manual "commit message: session-05: add-bulkhead-and-timelimiter-to-order-payment"
  ;;

06 )
  hdr "Inventory Service + OpenFeign (Session 6, Lab 4A)"
  check_eureka "INVENTORY-SERVICE"
  check_code "GET check PROD-001 qty 5 -> 200" 200 "$(http 'http://localhost:8084/api/v1/inventory/check?productId=PROD-001&quantity=5')"
  check_has "PROD-001 available=true" '"available":true' "$(body 'http://localhost:8084/api/v1/inventory/check?productId=PROD-001&quantity=5')"
  check_code "GET check PROD-003 -> 409" 409 "$(http 'http://localhost:8084/api/v1/inventory/check?productId=PROD-003&quantity=1')"
  manual "POST /api/orders for PROD-003 -> REJECTED 'Insufficient stock'"
  manual "inventory logs show the incoming Authorization header (FeignJwtInterceptor)"
  check_mvn inventory-service
  check_mvn order-service
  manual "commit message: session-06: add-inventory-service-and-feign-client"
  ;;

07 )
  hdr "Saga: Order → Inventory → Payment (Session 7, Lab 5A)"
  check_has "inventory service up" '"status":"UP"' "$(body http://localhost:8084/actuator/health)"
  check_has "payment service up" '"status":"UP"' "$(body http://localhost:8083/actuator/health)"
  manual "POST /api/orders -> PENDING + orderId immediately"
  manual "GET /api/orders/{id}/status -> CONFIRMED (happy path) / CANCELLED when payment.failure-rate=1.0"
  manual "logs show [SAGA] OrderPlaced -> InventoryReserved -> PaymentCompleted -> CONFIRMED"
  manual "consumer groups: order-service, order-service-cancel, inventory-service, inventory-compensation, payment-service"
  check_mvn order-service
  check_mvn inventory-service
  check_mvn payment-service
  manual "commit message: session-07: add-choreography-saga-order-inventory-payment"
  ;;

08 )
  hdr "Redis caching on Product Service (Session 8, Lab 6A)"
  if (cd "${PLATFORM}" && docker compose ps redis 2>/dev/null | grep -qi -e up -e healthy); then ok "redis container up"; else bad "redis container up" "docker compose up -d"; fi
  http http://localhost:8081/api/v1/products >/dev/null
  http http://localhost:8081/api/v1/products >/dev/null
  KEYS="$((cd "${PLATFORM}" && docker compose exec -T redis redis-cli KEYS 'products*') 2>/dev/null)"
  check_has "redis has products::* keys after two GETs" 'products::' "$KEYS"
  TTL="$((cd "${PLATFORM}" && docker compose exec -T redis redis-cli TTL products::all) 2>/dev/null | tr -d '\r')"
  if [ "${TTL:-0}" -gt 0 ] 2>/dev/null; then ok "TTL products::all = ${TTL}s (< 300)"; else manual "TTL products::all — key may not exist yet (save a product, then re-check)"; fi
  manual "after POST: both products::<id> and products::all evicted, next GET is a miss"
  check_mvn product-service
  manual "commit message: session-08: add-redis-caching-to-product-service"
  ;;

* )
  echo "Unknown lab: '$LAB'. Available: 01 02 03 04 05 06 07 08"
  exit 2 ;;
esac

echo "--------------------------------------------------------------"
echo " RESULT: ${PASS} PASS | ${FAIL} FAIL | ${MANUAL} MANUAL"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
