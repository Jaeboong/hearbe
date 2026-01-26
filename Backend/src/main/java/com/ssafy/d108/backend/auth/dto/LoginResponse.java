package com.ssafy.d108.backend.auth.dto;

import com.ssafy.d108.backend.entity.UserType;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * 로그인 응답 DTO
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class LoginResponse {

    private Integer userId;
    private String username;
    private UserType userType;
    private String message;
}
