package com.ssafy.d108.backend.cartItem.dto;


import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@AllArgsConstructor
public class CartItemUpdateResponseDto {

    private Long cartItemId;
    private String message;
}
