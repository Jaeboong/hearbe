package com.ssafy.d108.backend.cartItem.controller;

import com.ssafy.d108.backend.cartItem.dto.*;
import com.ssafy.d108.backend.cartItem.service.CartItemService;
import com.ssafy.d108.backend.global.util.SecurityUtil; // 활용
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

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
    @GetMapping("/{userId}")
    public ResponseEntity<CartItemListResponseDto> getCartItems(@PathVariable("userId") Integer userId) {

        // 경로 변수로 받은 userId를 서비스로 전달
        CartItemListResponseDto response = cartItemService.getCartItems(userId);

        return ResponseEntity.ok(response);
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
    public ResponseEntity<Map<String, String>> deleteCartItem(
            @PathVariable("cart_item_id") Integer cartItemId) {

        cartItemService.deleteCartItem(cartItemId);

        Map<String, String> response = new HashMap<>();
        response.put("message", "상품이 성공적으로 삭제되었습니다.");

        return ResponseEntity.ok(response);
    }
}