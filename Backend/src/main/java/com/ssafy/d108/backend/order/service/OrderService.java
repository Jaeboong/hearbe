package com.ssafy.d108.backend.order.service;

import com.ssafy.d108.backend.auth.repository.UserRepository;
import com.ssafy.d108.backend.entity.Order;
import com.ssafy.d108.backend.entity.OrderItem;
import com.ssafy.d108.backend.entity.Platform;
import com.ssafy.d108.backend.entity.User;
import com.ssafy.d108.backend.global.exception.BusinessException;
import com.ssafy.d108.backend.global.response.ErrorCode;
import com.ssafy.d108.backend.order.dto.OrderCreateRequest;
import com.ssafy.d108.backend.order.dto.OrderItemResponse;
import com.ssafy.d108.backend.order.dto.OrderListResponse;
import com.ssafy.d108.backend.order.dto.OrderResponse;
import com.ssafy.d108.backend.order.repository.OrderItemRepository;
import com.ssafy.d108.backend.order.repository.OrderRepository;
import com.ssafy.d108.backend.platform.repository.PlatformRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class OrderService {

    private final OrderRepository orderRepository;
    private final OrderItemRepository orderItemRepository;
    private final UserRepository userRepository;
    private final PlatformRepository platformRepository;

    /**
     * 주문 생성 (다중 상품 주문)
     */
    @Transactional
    public OrderResponse createOrder(Integer userId, OrderCreateRequest request) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));

        Platform platform = platformRepository.findById(request.getPlatformId().intValue())
                .orElseThrow(() -> new BusinessException(ErrorCode.PLATFORM_NOT_FOUND));

        // 1. Order 생성
        Order order = new Order();
        order.setUser(user);
        // orderDetailUrl은 첫 번째 아이템의 URL 사용 (또는 null)
        if (!request.getItems().isEmpty() && request.getItems().get(0).getUrl() != null) {
            order.setOrderDetailUrl(request.getItems().get(0).getUrl());
        }

        // Save Order
        Order savedOrder = orderRepository.save(order);

        // 2. 여러 OrderItem 생성
        List<OrderItem> savedItems = new ArrayList<>();
        for (com.ssafy.d108.backend.order.dto.OrderItemDto itemDto : request.getItems()) {
            OrderItem orderItem = new OrderItem();
            orderItem.setOrder(savedOrder);
            orderItem.setUser(user);
            orderItem.setPlatform(platform);
            orderItem.setName(itemDto.getName());
            orderItem.setPrice(itemDto.getPrice());
            orderItem.setQuantity(itemDto.getQuantity());
            orderItem.setUrl(itemDto.getUrl());
            orderItem.setImgUrl(itemDto.getImgUrl());
            orderItem.setDeliverUrl(itemDto.getDeliverUrl());

            savedItems.add(orderItemRepository.save(orderItem));
        }

        // 3. Response 생성
        List<OrderItemResponse> itemResponses = savedItems.stream()
                .map(OrderItemResponse::from)
                .collect(Collectors.toList());

        return OrderResponse.of(savedOrder, itemResponses);
    }

    /**
     * 내 주문 내역 조회
     * 
     * @param userId 사용자 ID
     * @return 주문 내역 리스트
     */
    public OrderListResponse getMyOrders(Integer userId) {
        List<Order> orders = orderRepository.findAllByUserIdOrderByCreatedAtDesc(userId);

        List<OrderListResponse.OrderDetailDto> orderDtos = orders.stream()
                .map(order -> {
                    List<OrderItem> items = orderItemRepository.findAllByOrderId(order.getId());

                    // 아이템이 없으면 null 반환 (나중에 제거됨)
                    if (items.isEmpty()) {
                        return null;
                    }

                    List<OrderItemResponse> itemResponses = items.stream()
                            .map(OrderItemResponse::from)
                            .collect(Collectors.toList());

                    // 플랫폼 ID 추출 (첫 번째 아이템 기준)
                    Long extractedPlatformId = Long.valueOf(items.get(0).getPlatform().getId());

                    return OrderListResponse.OrderDetailDto.from(order, itemResponses, extractedPlatformId);
                })
                .filter(dto -> dto != null) // null 제거
                .collect(Collectors.toList());

        return new OrderListResponse(orderDtos);
    }
}
