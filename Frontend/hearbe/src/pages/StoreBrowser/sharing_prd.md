# Sharing Session API Specification

## 1. 공유 세션 시작
**POST** `/api/sharing/sessions/`

### Request
```json
{
  "host_user_id": 1,
  "session_type": "SHOPPING_ASSIST"
}
```

### Response
```json
{
  "sharing_session_id": 201,
  "meeting_code": "XY72B9",
  "session_status": "active",
  "expires_at": "2026-01-19T15:30:00Z"
}
```

## 2. 공유 세션 참가
**POST** `/api/sharing/sessions/join`

### Request
```json
{
  "meeting_code": "XY72B9",
  "user_id": 1
}
```

### Response
```json
{
  "sharing_session_id": 201,
  "is_media_sharing": true,
  "is_audio_sharing": true,
  "host_sdp_offer": true,
  "status": "connected",
  "host_username": "홍길동",
  "webrtc_config": {
    "ice_servers": ["stun:stun.l.google.com:19302"]
  }
}
```

## 3. 공유 세션 종료
**PATCH** `/api/sharing/sessions/{id}/end`

### Response
```json
{
  "sharing_session_id": 201,
  "duration_seconds": 1200,
  "session_status": "completed",
  "ended_at": "2026-01-19T14:50:00Z",
  "session_closed": "host"
}
```
