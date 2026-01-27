package com.ssafy.d108.backend.cartItem.controller;

import com.ssafy.d108.backend.cartItem.dto.*;
import com.ssafy.d108.backend.cartItem.service.CartItemService;
import com.ssafy.d108.backend.global.util.SecurityUtil; // 활용
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/cart")
@RequiredArgsConstructor
public class CartItemController {

    private final CartItemService cartItemService;

    /**
     * 장바구니 담기
     */
    @PostMapping
    public ResponseEntity<CartItemCreateResponseDto> addCartItem(
            @Valid @RequestBody CartItemRequestDto requestDto) {

        return ResponseEntity.ok(cartItemService.addCartItem(SecurityUtil.getCurrentUserId(), requestDto));
    }

    /**
     * 장바구니 목록 조회
     */
    @GetMapping
    public ResponseEntity<CartItemListResponseDto> getCartItems() {

        return ResponseEntity.ok(cartItemService.getCartItems(SecurityUtil.getCurrentUserId()));
    }

    /**
     * 장바구니 수량 수정
     */
    @PatchMapping("/{cart_item_id}")
    public ResponseEntity<CartItemUpdateResponseDto> updateQuantity(
            @PathVariable("cart_item_id") Integer cartItemId,
            @Valid @RequestBody CartItemUpdateRequestDto requestDto) {

        return ResponseEntity.ok(cartItemService.updateQuantity(cartItemId, requestDto));
    }

    /**
     * 장바구니 삭제
     */
    @DeleteMapping("/{cart_item_id}")
    public ResponseEntity<Void> deleteCartItem(
            @PathVariable("cart_item_id") Integer cartItemId) {

        cartItemService.deleteCartItem(cartItemId);
        return ResponseEntity.noContent().build();
    }
}