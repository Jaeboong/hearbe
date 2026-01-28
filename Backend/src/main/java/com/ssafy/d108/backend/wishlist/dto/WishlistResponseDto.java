package com.ssafy.d108.backend.wishlist.dto;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import java.util.List;

@Getter
@Setter
@NoArgsConstructor
public class WishlistResponseDto {


    private int totalCount;      // 전체 찜 개수 추가
    private long totalPrice;     // 전체 금액 합계 추가
    private List<WishlistItemDetail> items;

    @Getter
    @Setter
    @NoArgsConstructor
    public static class WishlistItemDetail {
        private Integer wishlistItemId;
        private String productName;
        private String productUrl;
        private String platformName;
        private String createdAt;
        private String imgUrl;
        private long price;      // 개별 가격 정보 (합산을 위해 추가 권장)
        private Boolean liked;
    }
}