package com.ssafy.d108.backend.global.exception;

import com.ssafy.d108.backend.global.response.ErrorCode;

/**
 * 사용자를 찾을 수 없을 때 발생하는 예외
 */
public class UserNotFoundException extends BusinessException {

    public UserNotFoundException() {
        super(ErrorCode.USER_NOT_FOUND);
    }

    public UserNotFoundException(Integer userId) {
        super(ErrorCode.USER_NOT_FOUND, "사용자를 찾을 수 없습니다. ID: " + userId);
    }

    public UserNotFoundException(String loginId) {
        super(ErrorCode.USER_NOT_FOUND, "사용자를 찾을 수 없습니다. 로그인 ID: " + loginId);
    }
}
