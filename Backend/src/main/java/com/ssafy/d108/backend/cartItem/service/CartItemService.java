package com.ssafy.d108.backend.cartItem.service;

import com.ssafy.d108.backend.cartItem.dto.CartItemRequestDto;
import com.ssafy.d108.backend.cartItem.dto.CartItemResponseDto;
import com.ssafy.d108.backend.cartItem.repository.CartItemRepository;
import com.ssafy.d108.backend.entity.CartItem;
import com.ssafy.d108.backend.entity.Platform;
import com.ssafy.d108.backend.entity.User;
import com.ssafy.d108.backend.platform.repository.PlatformRepository;
import com.ssafy.d108.backend.auth.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
public class CartItemService {

    private final CartItemRepository cartItemRepository;
    private final UserRepository userRepository;
    private final PlatformRepository platformRepository;

    /**
     * 장바구니 아이템 추가
     */
    public CartItemResponseDto addCartItem(Integer userId, CartItemRequestDto requestDto) {

        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 사용자입니다."));

        Platform platform = platformRepository.findById(requestDto.getPlatformId())
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 플랫폼입니다."));

        CartItem cartItem = new CartItem();
        cartItem.setUser(user);
        cartItem.setPlatform(platform);
        cartItem.setName(requestDto.getName());
        cartItem.setUrl(requestDto.getUrl());
        cartItem.setImgUrl(requestDto.getImgUrl());
        cartItem.setPrice(requestDto.getPrice());
        cartItem.setQuantity(1);

        CartItem savedItem = cartItemRepository.save(cartItem);

        return toResponseDto(savedItem);
    }

    /**
     * 장바구니 목록 조회
     */
    @Transactional(readOnly = true)
    public List<CartItemResponseDto> getCartItems(Integer userId) {

        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 사용자입니다."));

        return cartItemRepository.findAllByUser(user)
                .stream()
                .map(this::toResponseDto)
                .collect(Collectors.toList());
    }

    /**
     * 장바구니 아이템 수량 변경
     */
    public CartItemResponseDto updateQuantity(Integer cartItemId, Integer quantity) {

        if (quantity <= 0) {
            throw new IllegalArgumentException("수량은 1 이상이어야 합니다.");
        }

        CartItem cartItem = cartItemRepository.findById(cartItemId)
                .orElseThrow(() -> new IllegalArgumentException("장바구니 아이템을 찾을 수 없습니다."));

        cartItem.setQuantity(quantity);

        return toResponseDto(cartItem);
    }

    /**
     * 장바구니 아이템 삭제
     */
    public void deleteCartItem(Integer cartItemId) {

        CartItem cartItem = cartItemRepository.findById(cartItemId)
                .orElseThrow(() -> new IllegalArgumentException("장바구니 아이템을 찾을 수 없습니다."));

        cartItemRepository.delete(cartItem);
    }

    /**
     * 장바구니 비우기
     */
    public void clearCart(Integer userId) {

        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 사용자입니다."));

        cartItemRepository.deleteAllByUser(user);
    }

    /**
     * Entity → ResponseDto 변환
     */
    private CartItemResponseDto toResponseDto(CartItem cartItem) {

        return CartItemResponseDto.builder()
                .cartItemId(cartItem.getId())
                .userId(cartItem.getUser().getId())
                .platformId(cartItem.getPlatform().getId())
                .name(cartItem.getName())
                .quantity(cartItem.getQuantity())
                .url(cartItem.getUrl())
                .price(cartItem.getPrice())
                .createdAt(cartItem.getCreatedAt())
                .build();
    }
}
