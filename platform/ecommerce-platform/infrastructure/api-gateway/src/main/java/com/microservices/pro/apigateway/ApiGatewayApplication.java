package com.microservices.pro.apigateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * API Gateway — the single entry point of the platform.
 *
 * Routes (product-service today) are declared in application.yml and resolved
 * through Eureka with lb://. Runs on the reactive WebFlux/Netty stack.
 */
@SpringBootApplication
public class ApiGatewayApplication {

    public static void main(String[] args) {
        SpringApplication.run(ApiGatewayApplication.class, args);
    }
}
