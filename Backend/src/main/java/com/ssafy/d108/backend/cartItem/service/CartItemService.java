package com.ssafy.d108.backend.cartItem.service;

import com.ssafy.d108.backend.auth.repository.UserRepository;
import com.ssafy.d108.backend.cartItem.dto.*;
import com.ssafy.d108.backend.cartItem.repository.CartItemRepository;
import com.ssafy.d108.backend.global.exception.BusinessException;
import com.ssafy.d108.backend.global.response.ErrorCode;
import com.ssafy.d108.backend.platform.repository.PlatformRepository;
import com.ssafy.d108.backend.entity.CartItem;
import com.ssafy.d108.backend.entity.Platform;
import com.ssafy.d108.backend.entity.User;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class CartItemService {

    private final CartItemRepository cartItemRepository;
    private final PlatformRepository platformRepository;
    private final UserRepository userRepository;

    /**
     * 장바구니 아이템 추가
     */
    @Transactional
    public CartItemCreateResponseDto addCartItem(Integer userId, CartItemRequestDto requestDto) {
        // 1. 파라미터로 받은 userId로 유저 조회
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));

        // 2. 플랫폼 조회
        Platform platform = platformRepository.findById(requestDto.getPlatformId().intValue())
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 플랫폼입니다."));

        // 3. 엔티티 생성 및 저장
        CartItem cartItem = new CartItem();
        cartItem.setUser(user);
        cartItem.setPlatform(platform);
        cartItem.setName(requestDto.getName());
        cartItem.setPrice((long) requestDto.getPrice());
        cartItem.setImgUrl(requestDto.getImgUrl());
        cartItem.setUrl(requestDto.getUrl());
        cartItem.setQuantity(1);

        CartItem savedItem = cartItemRepository.save(cartItem);

        return new CartItemCreateResponseDto(savedItem.getId(), "장바구니 추가 완료");
    }

    /**
     * 내 장바구니 목록 조회
     */
    public CartItemListResponseDto getCartItems(Integer userId) {
        // 1. 유저 조회
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));

        // 2. 해당 유저의 아이템 리스트 조회
        List<CartItem> items = cartItemRepository.findAllByUser(user);

        // 3. Detail DTO 변환
        List<CartItemListResponseDto.CartItemDetail> itemDetails = items.stream()
                .map(this::convertToDetailDto)
                .collect(Collectors.toList());

        // 4. 합계 계산
        int totalPrice = (int) items.stream()
                .mapToLong(item -> item.getPrice() * item.getQuantity())
                .sum();

        // 5. 응답 DTO 조립
        CartItemListResponseDto response = new CartItemListResponseDto();
        response.setCartItems(itemDetails);
        response.setTotalCount(items.size());
        response.setTotalPrice(totalPrice);

        return response;
    }

    /**
     * 장바구니 아이템 수량 수정
     */
    @Transactional
    public CartItemUpdateResponseDto updateQuantity(Integer cartItemId, CartItemUpdateRequestDto requestDto) {
        CartItem cartItem = cartItemRepository.findById(cartItemId)
                .orElseThrow(() -> new IllegalArgumentException("해당 장바구니 아이템을 찾을 수 없습니다."));

        cartItem.setQuantity(requestDto.getQuantity());

        return new CartItemUpdateResponseDto(Long.valueOf(cartItem.getId()), "수량이 변경되었습니다.");
    }

    /**
     * 장바구니 아이템 개별 삭제
     */
    @Transactional
    public void deleteCartItem(Integer cartItemId) {
        if (!cartItemRepository.existsById(cartItemId)) {
            throw new IllegalArgumentException("삭제하려는 아이템이 존재하지 않습니다.");
        }
        cartItemRepository.deleteById(cartItemId);
    }

    /**
     * 장바구니 전체 비우기
     */
    @Transactional
    public void clearCart(Integer userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));
        cartItemRepository.deleteAllByUser(user);
    }

    /**
     * 내부 매핑 로직 (Entity -> Detail DTO)
     */
    private CartItemListResponseDto.CartItemDetail convertToDetailDto(CartItem item) {
        CartItemListResponseDto.CartItemDetail detail = new CartItemListResponseDto.CartItemDetail();
        detail.setCartItemId(Long.valueOf(item.getId()));
        detail.setPlatformId(Long.valueOf(item.getPlatform().getId()));
        detail.setName(item.getName());
        detail.setPrice(item.getPrice().intValue());
        detail.setImgUrl(item.getImgUrl());
        detail.setUrl(item.getUrl());
        detail.setQuantity(item.getQuantity());
        detail.setCreatedAt(item.getCreatedAt().toString());
        return detail;
    }
}