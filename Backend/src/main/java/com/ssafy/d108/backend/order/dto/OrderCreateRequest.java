package com.ssafy.d108.backend.order.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class OrderCreateRequest {

    @JsonProperty("platformId")
    @NotNull(message = "플랫폼 ID는 필수입니다.")
    private Long platformId;

    @NotNull(message = "상품명은 필수입니다.")
    private String name;

    private String url;

    @NotNull(message = "가격은 필수입니다.")
    private Long price;

    @JsonProperty("quantity")
    @NotNull(message = "수량은 필수입니다.")
    private Integer quantity;

    @JsonProperty("img_url")
    private String imgUrl;
}
