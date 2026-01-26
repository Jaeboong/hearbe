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
import com.ssafy.d108.backend.entity.UserType;
import com.ssafy.d108.backend.entity.WelfareCard;
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
    private final WelfareCardRepository welfareCardRepository;

    /**
     * 회원가입
     */
    @Transactional
    public Integer signup(SignupRequest request) {
        // 비밀번호 일치 검증
        if (!request.getPassword().equals(request.getPasswordCheck())) {
            throw new IllegalArgumentException("비밀번호가 일치하지 않습니다.");
        }

        // BLIND 타입 복지카드 필수 검증
        if (request.getUserType() == UserType.BLIND) {
            if (request.getWelfareCard() == null) {
                throw new IllegalArgumentException("전맹 사용자는 복지카드 등록이 필수입니다.");
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
        // 숫자만 저장 (하이픈 등 제거)
        welfareCard.setCardNumber(welfareCardRequest.getCardNumber().replaceAll("[^0-9]", ""));
        welfareCard.setIssueDate(welfareCardRequest.getIssueDate());
        welfareCard.setExpirationDate(welfareCardRequest.getExpirationDate());
        welfareCard.setCvc(welfareCardRequest.getCvc()); // TODO: 암호화 필요

        welfareCardRepository.save(welfareCard);
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

    /**
     * 아이디 찾기 (A형 - 복지카드 인증)
     */
    public FindIdResponse findId(FindIdRequest request) {
        // 복지카드 정보로 조회 (카드번호 포함 - 숫자만 비교)
        WelfareCard welfareCard = welfareCardRepository
                .findByCardNumberAndCardCompanyAndIssueDateAndExpirationDateAndCvc(
                        request.getCardNumber().replaceAll("[^0-9]", ""),
                        request.getCardCompany(),
                        request.getIssueDate(),
                        request.getExpirationDate(),
                        request.getCvc())
                .orElseThrow(() -> new UserNotFoundException("일치하는 복지카드 정보가 없습니다."));

        // 연결된 사용자 정보 반환
        return new FindIdResponse(
                welfareCard.getUser().getLoginId(),
                "아이디 찾기 성공");
    }

    /**
     * 로그아웃
     * 현재는 상태 비저장(Stateless)이라 별도 로직은 없지만, 추후 토큰 블랙리스팅/세션 무효화 등을 위해 API 마련
     */
    public void logout(Integer userId) {
        // TODO: 추후 JWT 토큰 무효화 로직 추가 예정
        // 현재는 클라이언트 측에서 토큰/세션 정보 삭제하면 됨
    }
}
