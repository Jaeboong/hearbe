package com.ssafy.d108.backend.order.service;

import com.ssafy.d108.backend.auth.repository.UserRepository;
import com.ssafy.d108.backend.entity.Order;
import com.ssafy.d108.backend.entity.OrderItem;
import com.ssafy.d108.backend.entity.Platform;
import com.ssafy.d108.backend.entity.User;
import com.ssafy.d108.backend.global.exception.UserNotFoundException;
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

import java.util.Collections;
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
     * 주문 생성 (단일 상품 주문)
     */
    @Transactional
    public OrderResponse createOrder(Integer userId, OrderCreateRequest request) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException("사용자를 찾을 수 없습니다."));

        Platform platform = platformRepository.findById(request.getPlatformId().intValue())
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 플랫폼입니다."));

        // 1. Order 생성
        Order order = new Order();
        order.setUser(user);
        order.setOrderDetailUrl(request.getUrl()); // 상품 URL을 주문 상세 URL로 일단 사용 (기획에 따라 다름)
        // deliveryUrl은 현재 없음

        // Save Order
        Order savedOrder = orderRepository.save(order);

        // 2. OrderItem 생성
        OrderItem orderItem = new OrderItem();
        orderItem.setOrder(savedOrder);
        orderItem.setUser(user);
        orderItem.setPlatform(platform);
        orderItem.setName(request.getName());
        orderItem.setPrice(request.getPrice());
        orderItem.setQuantity(1); // 기본 1개
        orderItem.setUrl(request.getUrl());
        orderItem.setImgUrl(request.getImgUrl());

        OrderItem savedItem = orderItemRepository.save(orderItem);

        // 3. Response 생성
        List<OrderItemResponse> itemResponses = Collections.singletonList(OrderItemResponse.from(savedItem));
        return OrderResponse.of(savedOrder, itemResponses);
    }

    /**
     * 내 주문 내역 조회
     */
    public OrderListResponse getMyOrders(Integer userId) {
        List<Order> orders = orderRepository.findAllByUserIdOrderByCreatedAtDesc(userId);

        List<OrderListResponse.OrderDetailDto> orderDtos = orders.stream().map(order -> {
            List<OrderItem> items = orderItemRepository.findAllByOrderId(order.getId());
            List<OrderItemResponse> itemResponses = items.stream()
                    .map(OrderItemResponse::from)
                    .collect(Collectors.toList());

            // 플랫폼 ID 추출 (첫 번째 아이템 기준)
            Long platformId = items.isEmpty() ? null : Long.valueOf(items.get(0).getPlatform().getId());

            return OrderListResponse.OrderDetailDto.from(order, itemResponses, platformId);
        }).collect(Collectors.toList());

        return new OrderListResponse(orderDtos);
    }
}
