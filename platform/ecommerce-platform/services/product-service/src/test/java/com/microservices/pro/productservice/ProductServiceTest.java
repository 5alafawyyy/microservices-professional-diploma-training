package com.microservices.pro.productservice;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

/**
 * Service-layer tests for Lab 1.
 *
 * ProductService has no collaborators, so no mocking framework is needed here
 * (Mockito stubbing starts in Session 10). Each test gets a fresh instance.
 */
class ProductServiceTest {

    private ProductService productService;

    @BeforeEach
    void setUp() {
        productService = new ProductService();
    }

    private Product laptop() {
        return new Product(null, "Laptop", "15-inch laptop", new BigDecimal("999.99"), "Electronics");
    }

    @Test
    void findAll_returnsEmptyList_whenStoreIsEmpty() {
        assertThat(productService.findAll()).isEmpty();
    }

    @Test
    void save_assignsId_andFindByIdRetrievesTheProduct() {
        Product saved = productService.save(laptop());

        assertThat(saved.id()).isNotNull();
        Optional<Product> found = productService.findById(saved.id());
        assertThat(found).isPresent();
        assertThat(found.get().name()).isEqualTo("Laptop");
        assertThat(found.get().price()).isEqualByComparingTo("999.99");
        assertThat(found.get().category()).isEqualTo("Electronics");
    }

    @Test
    void save_keepsClientSuppliedId() {
        Product saved = productService.save(new Product(42L, "Mouse", "Wireless mouse", new BigDecimal("19.99"), "Electronics"));

        assertThat(saved.id()).isEqualTo(42L);
        assertThat(productService.findById(42L)).isPresent();
    }

    @Test
    void findById_returnsEmptyOptional_forUnknownId() {
        assertThat(productService.findById(999L)).isEmpty();
    }

    @Test
    void deleteById_removesTheProduct() {
        Product saved = productService.save(laptop());

        productService.deleteById(saved.id());

        assertThat(productService.findById(saved.id())).isEmpty();
    }

    @Test
    void findAll_returnsImmutableSnapshot_notTheLiveStore() {
        productService.save(laptop());

        List<Product> snapshot = productService.findAll();

        assertThat(snapshot).hasSize(1);
        assertThatThrownBy(() -> snapshot.add(laptop()))
                .isInstanceOf(UnsupportedOperationException.class);
    }
}
