package com.ssafy.d108.backend;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Health check endpoint for testing server availability.
 * TODO: Remove this file before production deployment.
 */
@RestController
public class HealthCheckController {

    @GetMapping("/health")
    public String health() {
        return "OK";
    }
}
