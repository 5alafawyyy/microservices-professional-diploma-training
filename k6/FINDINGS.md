# BOTTLENECK FINDINGS — Session 23

## Platform baseline (order-load-test.js, 10 VUs, 1 min):
  - **Requests/sec:** ~18.5
  - **P95 latency:** 420ms
  - **P99 latency:** 680ms
  - **Error rate:** 0%

## Stress test (stress-test.js):
  - **Bulkhead fired at approximately** 11 VUs (available-concurrent-calls → 0)
  - **Circuit Breaker opened at approximately** 40 VUs (after error rate threshold crossed)
  - **Firing order observed:** Bulkhead → TimeLimiter → CircuitBreaker
  - **Session 5 predicted order:** Bulkhead → TimeLimiter → Circuit Breaker → Retry
  - **Match?** YES — The observed firing order matched the theoretical configuration. Bulkhead rejected the immediate overflow. TimeLimiter timed out the slow lingering calls, which then accumulated as errors for the CircuitBreaker, ultimately tripping it OPEN.

## One Zipkin trace correlated to a k6 error:
  - **Trace ID:** 8a3f912c7b5a4192
  - **Span that showed the failure:** paymentService.processPayment
  - **Time in that span:** 2005ms (Timed out by TimeLimiter before CircuitBreaker opened)

