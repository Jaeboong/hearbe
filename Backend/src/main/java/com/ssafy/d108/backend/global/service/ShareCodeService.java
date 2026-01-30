package com.ssafy.d108.backend.global.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.Random;

@Slf4j
@Service
@RequiredArgsConstructor
public class ShareCodeService {

    private final StringRedisTemplate redisTemplate;
    private static final String CODE_PREFIX = "share:";
    private static final long CODE_EXPIRATION_MINUTES = 30;

    public String generateShareCode(String sessionId) {
        String code = generateRandomCode();
        // Ensure uniqueness (simple retry logic)
        while (Boolean.TRUE.equals(redisTemplate.hasKey(CODE_PREFIX + code))) {
            code = generateRandomCode();
        }

        // Save Code -> SessionId
        if (sessionId != null) {
            redisTemplate.opsForValue().set(CODE_PREFIX + code, sessionId, Duration.ofMinutes(CODE_EXPIRATION_MINUTES));
        }

        log.info("Generated Share Code: {} for Session: {}", code, sessionId);
        return code;
    }

    public String getSessionId(String code) {
        if (code == null)
            return null;
        return redisTemplate.opsForValue().get(CODE_PREFIX + code);
    }

    private String generateRandomCode() {
        Random random = new Random();
        int number = random.nextInt(999999);
        return String.format("%06d", number);
    }
}
