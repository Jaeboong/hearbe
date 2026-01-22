package com.ssafy.d108.backend.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;
import java.util.Map;

@Entity
@Table(name = "wishlist_items")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class WishlistItem {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "wishlist_item_id")
    private Integer wishlistItemId;

    @ManyToOne
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @ManyToOne
    @JoinColumn(name = "platform_id", nullable = false)
    private Platform platform;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "product_metadata", columnDefinition = "json")
    private Map<String, Object> productMetadata;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
}
