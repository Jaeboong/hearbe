package com.ssafy.d108.backend.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "sharing_session_logs")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SharingSessionLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "sharing_session_id")
    private Integer sharingSessionId;

    @ManyToOne
    @JoinColumn(name = "host_user_id", nullable = false)
    private User hostUser;

    @CreationTimestamp
    @Column(name = "started_at", nullable = false, updatable = false)
    private LocalDateTime startedAt;

    @Column(name = "ended_at")
    private LocalDateTime endedAt;

    @Enumerated(EnumType.STRING)
    @Column(name = "session_status", nullable = false, columnDefinition = "enum('active', 'completed', 'cancelled') default 'active'")
    private SessionStatus sessionStatus = SessionStatus.ACTIVE;

    public enum SessionStatus {
        ACTIVE, COMPLETED, CANCELLED
    }
}
