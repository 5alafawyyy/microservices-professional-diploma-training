package com.microservices.pro.productservice;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * ProductController — Session 1, Lab 1.
 *
 * Matches the original lab spec exactly:
 *   GET    /api/v1/products       → all products
 *   GET    /api/v1/products/{id}  → product by id (404 if not found)
 *   POST   /api/v1/products       → create a new product (201 Created)
 *   DELETE /api/v1/products/{id}  → delete a product
 */
@RestController
@RequestMapping("/api/v1/products")
public class ProductController {

    private final ProductService productService;
    private final ProductCommandService commandService;
    private final ProductQueryService queryService;


    public ProductController(ProductService productService, ProductCommandService commandService, ProductQueryService queryService) {
        this.productService = productService;
        this.commandService = commandService;
        this.queryService = queryService;
    }



    @GetMapping
    public ResponseEntity<List<ProductSummaryProjection>> getAll() {
        return ResponseEntity.ok(queryService.findAllSummaries());
    }


    @GetMapping("/{id}")
    public ResponseEntity<Product> getById(@PathVariable Long id) {
        return productService.findById(id)
                .map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }


    @PostMapping
    public ResponseEntity<Product> create(@RequestBody Product product) {
        Product saved = commandService.createProduct(product.getName(), product.getDescription(), product.getPrice(), product.getCategory());
        return ResponseEntity.status(HttpStatus.CREATED).body(saved);
    }



    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteById(@PathVariable Long id) {
        commandService.deleteProduct(id);
        return ResponseEntity.noContent().build();
    }

}
