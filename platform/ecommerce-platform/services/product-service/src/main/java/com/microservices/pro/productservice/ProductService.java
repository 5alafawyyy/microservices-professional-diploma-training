package com.microservices.pro.productservice;

import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Product bookkeeping.
 *
 * The store is an in-memory map for now: Lab 1 is about wiring the service
 * into the platform (config + discovery), not about persistence. JPA arrives
 * in the Session 6-8 block; the in-memory map is retired there.
 */
@Service
public class ProductService {

    private final Map<Long, Product> products = new ConcurrentHashMap<>();
    private final AtomicLong idSequence = new AtomicLong();

    public List<Product> findAll() {
        return List.copyOf(products.values());
    }

    public Optional<Product> findById(Long id) {
        return Optional.ofNullable(products.get(id));
    }

    public Product save(Product product) {
        Long id = product.id() != null ? product.id() : idSequence.incrementAndGet();
        Product stored = new Product(
                id,
                product.name(),
                product.description(),
                product.price(),
                product.category()
        );
        products.put(id, stored);
        return stored;
    }

    public void deleteById(Long id) {
        products.remove(id);
    }
}
