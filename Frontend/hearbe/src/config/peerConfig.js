// PeerJS 서버 설정
export const PEER_CONFIG = {
    host: import.meta.env.VITE_PEER_HOST || "i14d108.p.ssafy.io",
    port: import.meta.env.VITE_PEER_PORT ? parseInt(import.meta.env.VITE_PEER_PORT) : 443,
    path: "/hearbe-peer",
    secure: import.meta.env.VITE_PEER_SECURE !== "false",
    config: {
        iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
    }
};

// API 엔드포인트
export const API_BASE_URL = import.meta.env.VITE_API_URL || "https://i14d108.p.ssafy.io/api";
