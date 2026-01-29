package com.ssafy.d108.backend.global.controller;

import com.ssafy.d108.backend.global.service.OpenViduService;
import com.ssafy.d108.backend.global.service.ShareCodeService;
import io.openvidu.java.client.OpenViduRole;
import io.openvidu.java.client.Session;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/sharing")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class WebRTCController {

    private final OpenViduService openViduService;
    private final ShareCodeService shareCodeService;

    @PostMapping("/create")
    public ResponseEntity<?> createSession(@RequestParam(required = false) String userId) {
        try {
            Session session = openViduService.createSession();
            String code = shareCodeService.generateShareCode(session.getSessionId());

            Map<String, Object> data = new HashMap<>();
            data.put("meetingCode", code);
            data.put("sessionId", session.getSessionId());

            return ResponseEntity.ok(Map.of("message", "Session created", "data", data));
        } catch (Exception e) {
            log.error("Error creating session", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("error", e.getMessage()));
        }
    }

    @PostMapping("/token")
    public ResponseEntity<?> createToken(@RequestParam String meetingCode,
            @RequestParam(defaultValue = "SUBSCRIBER") String role) {
        try {
            String sessionId = shareCodeService.getSessionId(meetingCode);
            if (sessionId == null) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("error", "Invalid meeting code"));
            }

            OpenViduRole openViduRole = OpenViduRole.valueOf(role.toUpperCase());
            String token = openViduService.createConnection(sessionId, openViduRole);

            if (token == null) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("error", "Session not active"));
            }

            Map<String, Object> data = new HashMap<>();
            data.put("token", token);
            data.put("sessionId", sessionId);

            return ResponseEntity.ok(Map.of("message", "Token created", "data", data));
        } catch (Exception e) {
            log.error("Error creating token", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("error", e.getMessage()));
        }
    }
}
