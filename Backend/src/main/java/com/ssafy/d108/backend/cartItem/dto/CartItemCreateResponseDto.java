package com.ssafy.d108.backend.cartItem.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class CartItemCreateResponseDto {

    private Integer cartItemId;
    private String message;
}
