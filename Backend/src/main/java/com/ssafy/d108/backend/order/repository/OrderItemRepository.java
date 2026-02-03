package com.ssafy.d108.backend.order.repository;

import com.ssafy.d108.backend.entity.OrderItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface OrderItemRepository extends JpaRepository<OrderItem, Integer> {
    List<OrderItem> findAllByOrderId(Integer orderId);

    @Modifying
    @Query("DELETE FROM OrderItem oi WHERE oi.user.id = :userId")
    void deleteAllByUserId(@Param("userId") Integer userId);
}
