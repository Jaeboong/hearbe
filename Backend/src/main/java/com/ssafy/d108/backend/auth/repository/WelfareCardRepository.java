package com.ssafy.d108.backend.auth.repository;

import com.ssafy.d108.backend.entity.WelfareCard;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.Optional;

/**
 * WelfareCard Repository
 */
@Repository
public interface WelfareCardRepository extends JpaRepository<WelfareCard, Integer> {

    Optional<WelfareCard> findByUserId(Integer userId);

    boolean existsByUserId(Integer userId);

    Optional<WelfareCard> findByCardNumberAndCardCompanyAndIssueDateAndExpirationDateAndCvc(
            String cardNumber, String cardCompany, LocalDate issueDate, LocalDate expirationDate, String cvc);
}
