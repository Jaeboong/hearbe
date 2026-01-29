package com.ssafy.d108.backend.cartItem.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class CartItemCreateResponseDto {

    @JsonProperty("cart_item_id")
    private Integer cartItemId;

    @JsonProperty("message")
    private String message;
}