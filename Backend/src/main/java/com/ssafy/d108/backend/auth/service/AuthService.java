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
        if (request.getUserType() == UserType.BLIND) {
            // A형: 비밀번호(간편비밀번호)가 6자리 숫자인지 확인
            if (!request.getPassword().matches("^[0-9]{6}$")) {
                throw new IllegalArgumentException("A형 사용자의 비밀번호는 6자리 숫자여야 합니다.");
            }
            // A형은 password_check 확인 안 함 (또는 동일하다고 가정)
        } else {
            // B/C형: 비밀번호 8~20자 확인 및 password_check 일치 확인
            if (request.getPassword().length() < 8 || request.getPassword().length() > 20) {
                throw new IllegalArgumentException("비밀번호는 8~20자 사이여야 합니다.");
            }
            if (request.getPasswordCheck() == null || !request.getPassword().equals(request.getPasswordCheck())) {
                throw new IllegalArgumentException("비밀번호가 일치하지 않습니다.");
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
        if (userRepository.existsByLoginId(request.getLoginId())) {
            throw new DuplicateUserException("이미 사용 중인 아이디입니다.");
        }
        if (userRepository.existsByPhoneNumber(request.getPhoneNumber())) {
            throw new DuplicateUserException("이미 등록된 휴대폰 번호입니다.");
        }

        // User 생성 (비밀번호 암호화 저장)
        User user = new User();
        user.setLoginId(request.getLoginId());
        user.setPassword(passwordEncoder.encode(request.getPassword())); // BCrypt Encoding
        user.setUsername(request.getUsername());
        user.setEmail(request.getEmail());
        user.setPhoneNumber(request.getPhoneNumber());
        user.setUserType(request.getUserType());
        user.setSimplePassword(request.getSimplePassword());

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
        User user = userRepository.findByLoginId(request.getLoginId())
                .orElseThrow(() -> new UserNotFoundException("존재하지 않는 아이디입니다."));

        // 2. 비밀번호 검증 (BCrypt Matches)
        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new InvalidPasswordException();
        }

        // 3. Authentication 객체 생성 (Custom)
        //
        Authentication authentication = new UsernamePasswordAuthenticationToken(
                user.getLoginId(),
                null,
                Collections.singletonList(new SimpleGrantedAuthority("ROLE_USER")) // 임시 Role
        );

        // 4. JWT 토큰 생성
        String accessToken = jwtTokenProvider.createToken(authentication, user.getId());

        return new LoginResponse(
                user.getId(),
                user.getUsername(),
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
        String rawCardNumber = request.getCardNumber().replaceAll("[^0-9]", "");
        String encryptedCardNumber = aesUtil.encrypt(rawCardNumber);
        String encryptedCvc = aesUtil.encrypt(request.getCvc());

        WelfareCard welfareCard = welfareCardRepository
                .findByCardNumberAndCardCompanyAndIssueDateAndExpirationDateAndCvc(
                        encryptedCardNumber,
                        request.getCardCompany(),
                        request.getIssueDate(),
                        request.getExpirationDate(),
                        encryptedCvc)
                .orElseThrow(() -> new UserNotFoundException("일치하는 복지카드 정보가 없습니다."));

        // 연결된 사용자 정보 반환
        return new FindIdResponse(
                welfareCard.getUser().getLoginId(),
                "아이디 찾기 성공");
    }

    /**
     * 로그아웃
     */
    public void logout(Integer userId) {
        // TODO: 추후 JWT 토큰 무효화(Redis Blacklist) 등 구현
    }
}
