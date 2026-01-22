package com.ssafy.d108.backend.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "platforms")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Platform {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "platform_id")
    private Integer platformId;

    @Column(name = "platform_name", length = 100)
    private String platformName;

    @Column(name = "base_url", length = 500, nullable = false)
    private String baseUrl;
}
