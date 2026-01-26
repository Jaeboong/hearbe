package com.ssafy.d108.backend.auth.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDate;

/**
 * 아이디 찾기 요청 DTO (A형 - 복지카드 인증)
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class FindIdRequest {

    @JsonProperty("card_company")
    @NotNull(message = "카드사는 필수입니다.")
    private String cardCompany;

    @JsonProperty("card_number")
    @NotNull(message = "복지카드 번호는 필수입니다.")
    private String cardNumber;

    @JsonProperty("issue_date")
    @NotNull(message = "발급일은 필수입니다.")
    private LocalDate issueDate;

    @JsonProperty("expiration_date")
    @NotNull(message = "만료일은 필수입니다.")
    private LocalDate expirationDate;

    @NotNull(message = "CVC는 필수입니다.")
    private String cvc;
}
