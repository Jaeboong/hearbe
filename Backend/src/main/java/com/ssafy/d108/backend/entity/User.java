package com.ssafy.d108.backend.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "users")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {

    @Id
    @Column(name = "user_id", length = 30, nullable = false)
    private String userId;

    @Column(name = "username", length = 15)
    private String username;

    @Column(name = "password", length = 255)
    private String password;

    @Column(name = "phone_number", length = 20, nullable = false, unique = true)
    private String phoneNumber;

    @Column(name = "simple_password", length = 6)
    private String simplePassword;

    @Enumerated(EnumType.STRING)
    @Column(name = "user_type", nullable = false, columnDefinition = "enum('BLIND', 'LOW_VISION', 'GUARDIAN', 'GENERAL') default 'BLIND'")
    private UserType userType = UserType.BLIND;

    @Column(name = "last_login_at")
    private LocalDateTime lastLoginAt;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    public enum UserType {
        BLIND, LOW_VISION, GUARDIAN, GENERAL
    }
}
