package com.ssafy.d108.backend.auth.service;

import com.ssafy.d108.backend.auth.dto.LoginRequest;
import com.ssafy.d108.backend.auth.dto.LoginResponse;
import com.ssafy.d108.backend.auth.dto.SignupRequest;
import com.ssafy.d108.backend.auth.repository.UserRepository;
import com.ssafy.d108.backend.entity.User;
import com.ssafy.d108.backend.global.exception.DuplicateUserException;
import com.ssafy.d108.backend.global.exception.InvalidPasswordException;
import com.ssafy.d108.backend.global.exception.UserNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 인증 서비스 (B/C형 - 단순 버전)
 */
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class AuthService {

    private final UserRepository userRepository;

    /**
     * 회원가입
     */
    @Transactional
    public Integer signup(SignupRequest request) {
        // 비밀번호 일치 검증
        if (!request.getPassword().equals(request.getPasswordCheck())) {
            throw new IllegalArgumentException("비밀번호가 일치하지 않습니다.");
        }

        // 중복 체크
        if (userRepository.existsByLoginId(request.getLoginId())) {
            throw new DuplicateUserException("이미 사용 중인 아이디입니다.");
        }
        if (userRepository.existsByPhoneNumber(request.getPhoneNumber())) {
            throw new DuplicateUserException("이미 등록된 휴대폰 번호입니다.");
        }

        // User 생성 (비밀번호 평문 저장 - 추후 암호화 적용 예정)
        User user = new User();
        user.setLoginId(request.getLoginId());
        user.setPassword(request.getPassword());
        user.setUsername(request.getUsername());
        user.setEmail(request.getEmail());
        user.setPhoneNumber(request.getPhoneNumber());
        user.setUserType(request.getUserType());
        user.setSimplePassword(request.getSimplePassword());

        User saved = userRepository.save(user);
        return saved.getId();
    }

    /**
     * 로그인
     */
    public LoginResponse login(LoginRequest request) {
        // 사용자 조회
        User user = userRepository.findByLoginId(request.getLoginId())
                .orElseThrow(() -> new UserNotFoundException("존재하지 않는 아이디입니다."));

        // 비밀번호 검증 (평문 비교)
        if (!user.getPassword().equals(request.getPassword())) {
            throw new InvalidPasswordException();
        }

        return new LoginResponse(
                user.getId(),
                user.getUsername(),
                user.getUserType(),
                "로그인 성공");
    }
}
