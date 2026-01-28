package com.ssafy.d108.backend.auth.service;

import com.ssafy.d108.backend.auth.dto.FindIdRequest;
import com.ssafy.d108.backend.auth.dto.FindIdResponse;
import com.ssafy.d108.backend.auth.dto.LoginRequest;
import com.ssafy.d108.backend.auth.dto.LoginResponse;
import com.ssafy.d108.backend.auth.dto.SignupRequest;
import com.ssafy.d108.backend.auth.dto.WelfareCardRequest;
import com.ssafy.d108.backend.auth.repository.UserRepository;
import com.ssafy.d108.backend.auth.repository.WelfareCardRepository;
import com.ssafy.d108.backend.entity.User;
import com.ssafy.d108.backend.entity.enums.UserType;
import com.ssafy.d108.backend.entity.WelfareCard;
import com.ssafy.d108.backend.global.auth.JwtTokenProvider;
import com.ssafy.d108.backend.global.exception.DuplicateUserException;
import com.ssafy.d108.backend.global.exception.InvalidPasswordException;
import com.ssafy.d108.backend.global.exception.UserNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;

/**
 * 인증 서비스 (B/C형 - 보안 적용 버전)
 */
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class AuthService {

    private final UserRepository userRepository;
    private final WelfareCardRepository welfareCardRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;
    private final com.ssafy.d108.backend.global.util.AESUtil aesUtil;

    // AuthenticationManagerBuilder creates AuthenticationManager which checks
    // credentials
    // But here we are doing manual password check first?
    // Usually Spring Security uses loadUserByUsername.
    // Let's stick to the manual check we had, but use passwordEncoder.matches,
    // then generate token manually without AuthenticationManager for simplicity if
    // UserDetailService is not yet fully implemented.
    // However, JwtTokenProvider expects 'Authentication' object.

    /**
     * 회원가입
     */
    @Transactional
    public Integer signup(SignupRequest request) {
        // 비밀번호 정책 검증
        String rawPassword;

        if (request.getUserType() == UserType.BLIND) {
            // A형: 간편비밀번호(simplePassword)가 6자리 숫자인지 확인
            if (request.getSimplePassword() == null || !request.getSimplePassword().matches("^[0-9]{6}$")) {
                throw new IllegalArgumentException("A형 사용자의 간편 비밀번호는 6자리 숫자여야 합니다.");
            }
            // A형은 simplePassword를 메인 비밀번호로 사용
            rawPassword = request.getSimplePassword();
        } else {
            // B/C형: 비밀번호(password) 필수 및 유효성 검사
            if (request.getPassword() == null || request.getPassword().isBlank()) {
                throw new IllegalArgumentException("비밀번호는 필수입니다.");
            }
            if (request.getPassword().length() < 8 || request.getPassword().length() > 20) {
                throw new IllegalArgumentException("비밀번호는 8~20자 사이여야 합니다.");
            }
            if (request.getPasswordCheck() == null || !request.getPassword().equals(request.getPasswordCheck())) {
                throw new IllegalArgumentException("비밀번호가 일치하지 않습니다.");
            }
            rawPassword = request.getPassword();

            // B/C형은 이메일 필수
            if (request.getEmail() == null || request.getEmail().isBlank()) {
                throw new IllegalArgumentException("이메일은 필수입니다.");
            }
            if (!request.getEmail().matches("^[A-Za-z0-9+_.-]+@(.+)$")) {
                throw new IllegalArgumentException("올바른 이메일 형식이 아닙니다.");
            }
        }

        // BLIND 타입 복지카드 필수 검증
        if (request.getUserType() == UserType.BLIND) {
            if (request.getWelfareCard() == null) {
                throw new IllegalArgumentException("A형 사용자는 복지카드 등록이 필수입니다.");
            }

            // 복지카드 유효기간 검증
            if (request.getWelfareCard().getExpirationDate().isBefore(
                    request.getWelfareCard().getIssueDate())) {
                throw new IllegalArgumentException("복지카드 만료일은 발급일 이후여야 합니다.");
            }
        }

        // 중복 체크
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new DuplicateUserException("이미 사용 중인 아이디입니다.");
        }
        if (userRepository.existsByPhoneNumber(request.getPhoneNumber())) {
            throw new DuplicateUserException("이미 등록된 휴대폰 번호입니다.");
        }

        // User 생성 (비밀번호 암호화 저장)
        User user = new User();
        user.setUsername(request.getUsername());
        user.setPassword(passwordEncoder.encode(rawPassword)); // 선택된 패스워드 암호화
        user.setName(request.getName());
        user.setEmail(request.getEmail());
        user.setPhoneNumber(request.getPhoneNumber());
        user.setUserType(request.getUserType());
        if (request.getUserType() == UserType.BLIND) {
            user.setSimplePassword(request.getSimplePassword());
        } else {
            user.setSimplePassword(null);
        }

        User saved = userRepository.save(user);

        // 복지카드 저장 (BLIND 타입인 경우에만)
        if (request.getUserType() == UserType.BLIND && request.getWelfareCard() != null) {
            saveWelfareCard(request.getWelfareCard(), saved);
        }

        return saved.getId();
    }

    /**
     * 복지카드 저장
     */
    private void saveWelfareCard(WelfareCardRequest welfareCardRequest, User user) {
        WelfareCard welfareCard = new WelfareCard();
        welfareCard.setUser(user);
        welfareCard.setCardCompany(welfareCardRequest.getCardCompany());
        // 숫자만 저장 (하이픈 등 제거) -> 암호화
        String rawCardNumber = welfareCardRequest.getCardNumber().replaceAll("[^0-9]", "");
        welfareCard.setCardNumber(aesUtil.encrypt(rawCardNumber));
        welfareCard.setIssueDate(welfareCardRequest.getIssueDate());
        welfareCard.setExpirationDate(welfareCardRequest.getExpirationDate());
        welfareCard.setCvc(aesUtil.encrypt(welfareCardRequest.getCvc())); // 암호화 저장

        welfareCardRepository.save(welfareCard);
    }

    /**
     * 로그인
     */
    public LoginResponse login(LoginRequest request) {
        // 1. 사용자 조회
        User user = userRepository.findByUsername(request.getUsername())
                .orElseThrow(() -> new UserNotFoundException("존재하지 않는 아이디입니다."));

        // 2. 비밀번호 검증 (BCrypt Matches)
        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new InvalidPasswordException();
        }

        // 3. Authentication 객체 생성 (Custom)
        //
        Authentication authentication = new UsernamePasswordAuthenticationToken(
                user.getUsername(),
                null,
                Collections.singletonList(new SimpleGrantedAuthority("ROLE_USER")) // 임시 Role
        );

        // 4. JWT 토큰 생성
        String accessToken = jwtTokenProvider.createToken(authentication, user.getId());

        return new LoginResponse(
                user.getId(),
                user.getName(),
                user.getUserType(),
                accessToken,
                "로그인 성공");
    }

    /**
     * 아이디 찾기 (A형 - 복지카드 인증)
     */
    public FindIdResponse findId(FindIdRequest request) {
        // 복지카드 정보로 조회 (카드번호 포함 - 숫자만 비교)
        // 암호화된 값으로 검색 (AES Fixed IV 사용)
        String rawCardNumber = request.getWelfareCard().getCardNumber().replaceAll("[^0-9]", "");
        String encryptedCardNumber = aesUtil.encrypt(rawCardNumber);
        String encryptedCvc = aesUtil.encrypt(request.getWelfareCard().getCvc());

        WelfareCard welfareCard = welfareCardRepository
                .findByCardNumberAndCardCompanyAndIssueDateAndExpirationDateAndCvc(
                        encryptedCardNumber,
                        request.getWelfareCard().getCardCompany(),
                        request.getWelfareCard().getIssueDate(),
                        request.getWelfareCard().getExpirationDate(),
                        encryptedCvc)
                .orElseThrow(() -> new UserNotFoundException("일치하는 복지카드 정보가 없습니다."));

        return new FindIdResponse(welfareCard.getUser().getUsername(), "Found ID");
    }

    /**
     * 로그아웃
     */
    public void logout(Integer userId) {
        // TODO: 추후 JWT 토큰 무효화(Redis Blacklist) 등 구현
    }
}
