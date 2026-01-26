package com.ssafy.d108.backend.cartItem.dto;


import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;

@Getter
@Setter
@NoArgsConstructor
@ToString
public class CartItemRequestDto {
    private Integer platformId;

    private String name;

    private String url;

    private String imgUrl;

    private Long price;
}
