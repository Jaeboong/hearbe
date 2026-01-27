package com.ssafy.d108.backend.auth.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;

import java.time.LocalDate;

/**
 * 복지카드 등록 요청 DTO
 * AI 서버의 OCR 결과를 받아서 저장
 * - Lombok 없이 명시적 Getter/Setter 사용
 * - @JsonProperty 및 @JsonFormat 으로 필드 매핑 및 포맷 지정
 */
public class WelfareCardRequest {

    @JsonProperty("card_company")
    @NotNull(message = "카드사는 필수입니다.")
    private String cardCompany;

    @JsonProperty("card_number")
    @NotNull(message = "복지카드 번호는 필수입니다.")
    private String cardNumber;

    @JsonProperty("issue_date")
    @JsonFormat(pattern = "yyyy-MM-dd")
    @NotNull(message = "발급일은 필수입니다.")
    private LocalDate issueDate;

    @JsonProperty("expiration_date")
    @JsonFormat(pattern = "yyyy-MM-dd")
    @NotNull(message = "만료일은 필수입니다.")
    private LocalDate expirationDate;

    @JsonProperty("cvc")
    @NotNull(message = "CVC는 필수입니다.")
    @Pattern(regexp = "^[0-9]{3,5}$", message = "CVC는 3~5자리 숫자여야 합니다.")
    private String cvc;

    // 생성자 (기본 생성자 필수)
    public WelfareCardRequest() {
    }

    public WelfareCardRequest(String cardCompany, String cardNumber, LocalDate issueDate, LocalDate expirationDate,
            String cvc) {
        this.cardCompany = cardCompany;
        this.cardNumber = cardNumber;
        this.issueDate = issueDate;
        this.expirationDate = expirationDate;
        this.cvc = cvc;
    }

    // Getters and Setters
    public String getCardCompany() {
        return cardCompany;
    }

    public void setCardCompany(String cardCompany) {
        this.cardCompany = cardCompany;
    }

    public String getCardNumber() {
        return cardNumber;
    }

    public void setCardNumber(String cardNumber) {
        this.cardNumber = cardNumber;
    }

    public LocalDate getIssueDate() {
        return issueDate;
    }

    public void setIssueDate(LocalDate issueDate) {
        this.issueDate = issueDate;
    }

    public LocalDate getExpirationDate() {
        return expirationDate;
    }

    public void setExpirationDate(LocalDate expirationDate) {
        this.expirationDate = expirationDate;
    }

    public String getCvc() {
        return cvc;
    }

    public void setCvc(String cvc) {
        this.cvc = cvc;
    }
}
