package com.ssafy.d108.backend.cartItem.dto;

import jakarta.validation.constraints.Min;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class CartItemUpdateRequestDto {

    @Min(value = 1, message = "수량은 최소 1개 이상이어야 합니다.")
    private int quantity;

}