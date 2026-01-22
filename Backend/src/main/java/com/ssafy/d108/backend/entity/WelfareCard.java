package com.ssafy.d108.backend.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "welfare_cards")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class WelfareCard {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "welfare_card_id")
    private Integer welfareCardId;

    @OneToOne
    @JoinColumn(name = "user_id", nullable = false, unique = true)
    private User user;

    @Column(name = "cvc", length = 5, columnDefinition = "varchar(5) COMMENT 'CVC 번호 (AES-256 암호화 필수)'")
    private String cvc;

    @Column(name = "issue_date", nullable = false)
    private LocalDate issueDate;

    @Column(name = "expiration_date", nullable = false)
    private LocalDate expirationDate;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;
}
