package com.ssafy.d108.backend.order.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.ssafy.d108.backend.entity.Order;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class OrderListResponse {

    @JsonProperty("orders")
    private List<OrderDetailDto> orders;

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class OrderDetailDto {
        @JsonProperty("order_id")
        private Integer orderId;

        @JsonProperty("ordered_at")
        private String orderedAt; // YYYY-MM-DD 형식

        @JsonProperty("order_url")
        private String orderUrl;

        // Platform ID is typically per Item, but if Order represents single platform
        // transaction:
        // However, entity Order doesn't have platformId. OrderItem does.
        // We will take platformId from the first item for now.
        @JsonProperty("platform_id")
        private Long platformId;

        @JsonProperty("items")
        private List<OrderItemResponse> items;

        public static OrderDetailDto from(Order order, List<OrderItemResponse> items, Long platformId) {
            // Format date as YYYY-MM-DD
            String formattedDate = order.getCreatedAt().toLocalDate().toString();

            return new OrderDetailDto(
                    order.getId(),
                    formattedDate,
                    order.getOrderDetailUrl(),
                    platformId,
                    items);
        }
    }
}
