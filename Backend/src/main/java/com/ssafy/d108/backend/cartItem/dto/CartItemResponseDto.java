package com.ssafy.d108.backend.cartItem.dto;

import java.time.LocalDateTime;

import lombok.*;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CartItemResponseDto {


    private Integer cartItemId;

    private Integer userId;

    private Integer platformId;

    private String name;
    private Integer quantity;
    private String url;
    private Long price;
    private LocalDateTime createdAt;

}