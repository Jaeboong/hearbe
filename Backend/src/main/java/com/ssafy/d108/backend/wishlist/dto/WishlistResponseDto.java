package com.ssafy.d108.backend.wishlist.dto;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import java.util.List;

@Getter
@Setter
@NoArgsConstructor
public class WishlistResponseDto {

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
        private Boolean liked;
    }
}