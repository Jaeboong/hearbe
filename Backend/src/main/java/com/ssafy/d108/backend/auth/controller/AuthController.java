package com.ssafy.d108.backend.auth.controller;

import com.ssafy.d108.backend.auth.dto.FindIdRequest;
import com.ssafy.d108.backend.auth.dto.FindIdResponse;
import com.ssafy.d108.backend.auth.dto.LoginRequest;
import com.ssafy.d108.backend.auth.dto.LoginResponse;
import com.ssafy.d108.backend.auth.dto.SignupRequest;
import com.ssafy.d108.backend.auth.service.AuthService;
import com.ssafy.d108.backend.global.response.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 인증 컨트롤러 (B/C형)
 */
@Tag(name = "인증", description = "회원가입 및 로그인 API")
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    /**
     * 회원가입
     */
    @Operation(summary = "회원가입", description = "B/C형 사용자 회원가입 (복지카드 불필요)")
    @PostMapping("/signup")
    public ResponseEntity<ApiResponse<Integer>> signup(@Valid @RequestBody SignupRequest request) {
        Integer userId = authService.signup(request);
        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(ApiResponse.created(userId, "회원가입 완료"));
    }

    /**
     * 로그인
     */
    @Operation(summary = "로그인", description = "아이디/비밀번호로 로그인")
    @PostMapping("/login")
    public ResponseEntity<ApiResponse<LoginResponse>> login(@Valid @RequestBody LoginRequest request) {
        LoginResponse response = authService.login(request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    /**
     * 아이디 찾기 (A형 - 복지카드 인증)
     */
    @Operation(summary = "아이디 찾기", description = "복지카드 정보로 아이디 찾기 (A형 전용)")
    @PostMapping("/find-id")
    public ResponseEntity<ApiResponse<FindIdResponse>> findId(@Valid @RequestBody FindIdRequest request) {
        FindIdResponse response = authService.findId(request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    /**
     * 로그아웃
     */
    @Operation(summary = "로그아웃", description = "로그아웃 처리 (추후 토큰 만료 로직 포함)")
    @PostMapping("/logout")
    public ResponseEntity<ApiResponse<Void>> logout() {
        return ResponseEntity.ok(ApiResponse.success(null, "로그아웃 되었습니다."));
    }
}
