package com.microservices.pro.paymentservice;

import java.math.BigDecimal;

/**
 * PaymentRequest â€” Session 4.
 */
public record PaymentRequest(String orderId, BigDecimal amount) {}
