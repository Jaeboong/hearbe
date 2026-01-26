package com.ssafy.d108.backend.auth.service;

import com.ssafy.d108.backend.auth.dto.WelfareCardRequest;
import com.ssafy.d108.backend.auth.dto.WelfareCardResponse;
import com.ssafy.d108.backend.auth.repository.UserRepository;
import com.ssafy.d108.backend.auth.repository.WelfareCardRepository;
import com.ssafy.d108.backend.entity.User;
import com.ssafy.d108.backend.entity.WelfareCard;
import com.ssafy.d108.backend.global.exception.UserNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;

/**
 * 복지카드 관리 서비스
 */
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class WelfareCardService {

    private final UserRepository userRepository;
    private final WelfareCardRepository welfareCardRepository;

    /**
     * 복지카드 등록/수정 (OCR 결과 저장)
     * AI 서버에서 OCR 처리 후 결과를 받아서 저장
     */
    @Transactional
    public WelfareCardResponse registerWelfareCard(Integer userId, WelfareCardRequest request) {
        // 사용자 조회
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException("사용자를 찾을 수 없습니다."));

        // 복지카드 유효기간 검증
        if (request.getExpirationDate().isBefore(request.getIssueDate())) {
            throw new IllegalArgumentException("복지카드 만료일은 발급일 이후여야 합니다.");
        }

        // 기존 복지카드가 있는지 확인
        Optional<WelfareCard> existingCard = welfareCardRepository.findByUserId(userId);

        WelfareCard welfareCard;
        if (existingCard.isPresent()) {
            // 수정
            welfareCard = existingCard.get();
            welfareCard.setCardCompany(request.getCardCompany());
            welfareCard.setCardNumber(request.getCardNumber());
            welfareCard.setIssueDate(request.getIssueDate());
            welfareCard.setExpirationDate(request.getExpirationDate());
            welfareCard.setCvc(request.getCvc()); // TODO: 암호화 필요
        } else {
            // 신규 등록
            welfareCard = new WelfareCard();
            welfareCard.setUser(user);
            welfareCard.setCardCompany(request.getCardCompany());
            welfareCard.setCardNumber(request.getCardNumber());
            welfareCard.setIssueDate(request.getIssueDate());
            welfareCard.setExpirationDate(request.getExpirationDate());
            welfareCard.setCvc(request.getCvc()); // TODO: 암호화 필요
        }

        WelfareCard saved = welfareCardRepository.save(welfareCard);

        return new WelfareCardResponse(
                saved.getId(),
                userId,
                saved.getCardCompany(),
                saved.getCardNumber(),
                saved.getIssueDate(),
                saved.getExpirationDate(),
                saved.getCvc() != null, // CVC 존재 여부만 반환
                true,
                saved.getCreatedAt(),
                saved.getUpdatedAt());
    }

    /**
     * 복지카드 조회
     */
    public WelfareCardResponse getWelfareCard(Integer userId) {
        // 사용자 조회
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException("사용자를 찾을 수 없습니다."));

        Optional<WelfareCard> welfareCard = welfareCardRepository.findByUserId(userId);

        if (welfareCard.isPresent()) {
            WelfareCard card = welfareCard.get();
            return new WelfareCardResponse(
                    card.getId(),
                    userId,
                    card.getCardCompany(),
                    card.getCardNumber(),
                    card.getIssueDate(),
                    card.getExpirationDate(),
                    card.getCvc() != null, // CVC 존재 여부만 반환
                    true,
                    card.getCreatedAt(),
                    card.getUpdatedAt());
        } else {
            // 복지카드 없음
            return new WelfareCardResponse(
                    null,
                    userId,
                    null,
                    null,
                    null,
                    null,
                    false,
                    false,
                    null,
                    null);
        }
    }

}
