package com.microservices.pro.productservice;

import java.math.BigDecimal;

/**
 * Product domain model.
 *
 * Immutable record: the in-memory store keeps these objects as-is, and the
 * "assign an id on save" rule is enforced by {@link ProductService#save}.
 */
public record Product(
        Long id,
        String name,
        String description,
        BigDecimal price,
        String category
) {
}
