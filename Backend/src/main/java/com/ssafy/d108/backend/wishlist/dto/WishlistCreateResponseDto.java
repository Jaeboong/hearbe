package com.ssafy.d108.backend.wishlist.dto;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@AllArgsConstructor // 생성자를 통해 필드를 채울 수 있도록 추가
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class WishlistCreateResponseDto {

    private Integer wishlistItemId;
    private String createdAt;

}