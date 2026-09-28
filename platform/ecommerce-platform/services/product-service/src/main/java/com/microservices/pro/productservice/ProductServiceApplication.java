package com.microservices.pro.productservice;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Product Service — the first domain microservice of the platform.
 *
 * Registers itself with Eureka and imports its externalized configuration
 * from the Config Server (see application.yml).
 */
@SpringBootApplication
public class ProductServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(ProductServiceApplication.class, args);
    }
}
