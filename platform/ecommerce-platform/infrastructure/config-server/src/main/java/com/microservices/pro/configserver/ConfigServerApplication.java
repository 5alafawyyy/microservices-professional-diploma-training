package com.microservices.pro.configserver;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.config.server.EnableConfigServer;

/**
 * Centralized configuration server for the platform.
 *
 * Runs with the "native" backend: configuration files are served from the
 * classpath (src/main/resources/configs) instead of a Git repository, so this
 * module is self-contained for the training environment.
 */
@EnableConfigServer
@SpringBootApplication
public class ConfigServerApplication {

    public static void main(String[] args) {
        SpringApplication.run(ConfigServerApplication.class, args);
    }
}
