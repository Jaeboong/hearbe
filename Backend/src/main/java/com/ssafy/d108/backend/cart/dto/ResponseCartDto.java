package com.ssafy.d108.backend.cart.dto;

import java.time.OffsetDateTime;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;

@Getter

public class ResponseCartDto {

    @JsonProperty("cart_item_id")
    private Integer cartItemId;

    @JsonProperty("user_id")
    private Integer userId;

    @JsonProperty("product_id")
    private Long productId;

    @JsonProperty("platform_id")
    private Long platformId;

    private Integer quantity;

    private String message;

    @JsonProperty("action_type")
    private String actionType;

    @JsonProperty("created_at")
    private OffsetDateTime createdAt;

}
