package com.ssafy.d108.backend.order.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * 주문 생성 시 개별 아이템 정보
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class OrderItemDto {

    @JsonProperty("name")
    @NotBlank(message = "상품명은 필수입니다.")
    private String name;

    @JsonProperty("price")
    @NotNull(message = "가격은 필수입니다.")
    @Min(value = 0, message = "가격은 0 이상이어야 합니다.")
    private Long price;

    @JsonProperty("quantity")
    @NotNull(message = "수량은 필수입니다.")
    @Min(value = 1, message = "수량은 1 이상이어야 합니다.")
    private Integer quantity;

    @JsonProperty("url")
    private String url;

    @JsonProperty("img_url")
    private String imgUrl;

    @JsonProperty("deliver_url")
    private String deliverUrl;
}
