package com.ssafy.d108.backend.auth.controller;

import com.ssafy.d108.backend.auth.dto.WelfareCardRequest;
import com.ssafy.d108.backend.auth.dto.WelfareCardResponse;
import com.ssafy.d108.backend.auth.service.WelfareCardService;
import com.ssafy.d108.backend.global.response.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * 복지카드 관리 API
 */
@Tag(name = "복지카드", description = "복지카드 등록/조회/삭제 API (OCR 결과 처리)")
@RestController
@RequestMapping("/api/users/{userId}/welfare-card")
@RequiredArgsConstructor
public class WelfareCardController {

    private final WelfareCardService welfareCardService;

    /**
     * 복지카드 등록/수정
     * AI 서버에서 OCR 처리 후 결과를 여기로 전송
     */
    @Operation(summary = "복지카드 등록/수정", description = "AI 서버의 OCR 결과를 받아서 복지카드 정보를 저장합니다. 이미 등록된 경우 수정됩니다.")
    @PostMapping
    public ResponseEntity<ApiResponse<WelfareCardResponse>> registerWelfareCard(
            @PathVariable Integer userId,
            @Valid @RequestBody WelfareCardRequest request) {

        WelfareCardResponse response = welfareCardService.registerWelfareCard(userId, request);

        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(ApiResponse.created(response, "복지카드가 등록되었습니다."));
    }

    /**
     * 복지카드 조회
     */
    @Operation(summary = "복지카드 조회", description = "사용자의 복지카드 정보를 조회합니다.")
    @GetMapping
    public ResponseEntity<ApiResponse<WelfareCardResponse>> getWelfareCard(
            @PathVariable Integer userId) {

        WelfareCardResponse response = welfareCardService.getWelfareCard(userId);

        return ResponseEntity.ok(ApiResponse.success(response));
    }

}
