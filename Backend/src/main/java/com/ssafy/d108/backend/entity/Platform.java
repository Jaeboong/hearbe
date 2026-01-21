package com.ssafy.d108.backend.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@Getter
@NoArgsConstructor
@Table(name = "platforms")
public class Platform {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "platform_id")
    private Integer platformId;

    @Column(name = "shop_name", length = 100, nullable = false, unique = true)
    private String shopName;

    @Column(name = "base_url", length = 255)
    private String baseUrl;

    @Column(name = "api_endpoint_url", length = 255)
    private String apiEndpointUrl;
}
