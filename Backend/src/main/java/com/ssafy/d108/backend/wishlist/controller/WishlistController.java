package com.ssafy.d108.backend.wishlist.controller;

import com.ssafy.d108.backend.global.util.SecurityUtil;
import com.ssafy.d108.backend.wishlist.dto.*;
import com.ssafy.d108.backend.wishlist.service.WishlistService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/wishlist")
@RequiredArgsConstructor
public class WishlistController {

    private final WishlistService wishlistService;

    /**
     * 찜 추가 (POST /wishlist)
     * Request Header: Authorization (Bearer token)
     * Request Body: WishlistCreateRequestDto
     */
    @PostMapping
    public ResponseEntity<WishlistCreateResponseDto> addWishlistItem(
            @Valid @RequestBody WishlistCreateRequestDto requestDto) {

        // SecurityUtil을 사용하여 현재 로그인한 유저 ID 추출
        Integer userId = SecurityUtil.getCurrentUserId();

        WishlistCreateResponseDto response = wishlistService.addWishlistItem(userId, requestDto);
        return ResponseEntity.ok(response);
    }

    /**
     * 찜 목록 조회 (GET /wishlist)
     * Request Header: Authorization (Bearer token)
     */
    @GetMapping("/{userId}") // 경로상의 {userId}를
    public ResponseEntity<WishlistResponseDto> getWishlistItems(
            @PathVariable("userId") Integer userId) { // 여기서 낚아챕니다.

        // 이 경우 SecurityUtil을 쓰지 않고 경로에 들어온 userId를 바로 사용하게 됩니다.
        WishlistResponseDto response = wishlistService.getWishlistItems(userId);
        return ResponseEntity.ok(response);
    }

    /**
     * 찜 삭제 (DELETE /wishlist/{wishlistItemId})
     * Request Header: Authorization (Bearer token)
     */
    @DeleteMapping("/{wishlistItemId}")
    public ResponseEntity<Void> deleteWishlistItem(
            @PathVariable("wishlistItemId") Integer wishlistItemId) {

        // 서비스에서 존재 여부 확인 후 삭제 수행
        wishlistService.deleteWishlistItem(wishlistItemId);

        // 삭제 성공 시 204 No Content 반환
        return ResponseEntity.noContent().build();
    }
}