package com.ssafy.d108.backend.cartItem.dto;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

@Getter
@Setter
@NoArgsConstructor
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class CartItemListResponseDto {

    private List<CartItemDetail> cartItems;
    private int totalCount;
    private int totalPrice;

    @Getter
    @Setter
    @NoArgsConstructor
    @JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
    public static class CartItemDetail {
        private Long cartItemId;
        private Long platformId;
        private String name;
        private int price;
        private String imgUrl;
        private String url;      // JSON에 없으면 null로 들어감
        private int quantity;
        private String createdAt; // 날짜 포맷팅 필요 시 LocalDateTime 권장
    }
}