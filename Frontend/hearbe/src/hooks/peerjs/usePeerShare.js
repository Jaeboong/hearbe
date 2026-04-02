import { useState, useEffect, useRef } from 'react';
import Peer from 'peerjs';
import { PEER_CONFIG } from '../../config/peerConfig';

/**
 * A형 사용자용 PeerJS Hook - 화면 공유
 */
export const usePeerShare = () => {
    const [shareCode, setShareCode] = useState(null);
    const [isSharing, setIsSharing] = useState(false);
    const [error, setError] = useState(null);

    const peerRef = useRef(null);
    const localStreamRef = useRef(null);
    const currentCallRef = useRef(null);

    /**
     * 화면 공유 시작
     * @param {string} code - 백엔드에서 받은 4자리 코드
     */
    const startSharing = async (code) => {
        // Return if already sharing
        if (isSharing || peerRef.current) {
            console.warn('이미 화면 공유 중입니다.');
            return;
        }

        try {
            setError(null);

            // 1. 화면 공유 권한 요청
            const screenVideo = await navigator.mediaDevices.getDisplayMedia({
                video: { cursor: "always" },
                audio: false
            });

            // 2. 마이크 권한 (선택적)
            let audioTracks = [];
            try {
                const micAudio = await navigator.mediaDevices.getUserMedia({ audio: true });
                audioTracks = micAudio.getAudioTracks();
            } catch (e) {
                console.warn('마이크 권한 없음 (화면만 공유)');
            }

            // 3. 스트림 합치기
            localStreamRef.current = new MediaStream([
                ...screenVideo.getVideoTracks(),
                ...audioTracks
            ]);

            // 4. PeerJS Peer 생성
            const peerId = `share-${code}-user`;

            const newPeer = new Peer(peerId, PEER_CONFIG);
            peerRef.current = newPeer;

            newPeer.on("open", (id) => {
                setIsSharing(true);
                setShareCode(code);
            });

            // 5. Guardian 접속 대기 (DataConnection)
            newPeer.on("connection", (conn) => {

                // 0.5초 후 전화 걸기
                setTimeout(() => {
                    if (!localStreamRef.current) return;

                    const call = newPeer.call(conn.peer, localStreamRef.current);
                    currentCallRef.current = call;

                    call.on("stream", (remoteStream) => {
                        const audio = new Audio();
                        audio.srcObject = remoteStream;
                        audio.play().catch(e => console.warn('오디오 재생 실패'));
                    });

                    call.on("close", () => {
                    });

                    call.on("error", (e) => {
                        console.error('통화 에러:', e);
                    });
                }, 500);
            });

            newPeer.on("error", (err) => {
                console.error('Peer 에러:', err);
                setError(err.message);
                if (err.type === 'peer-unavailable' || err.type === 'network' || err.type === 'server-error') {
                    stopSharing();
                }
            });

            localStreamRef.current.getVideoTracks()[0].onended = () => {
                stopSharing();
            };

        } catch (err) {
            console.error('화면 공유 실패:', err);
            setError(err.message);
            stopSharing(); // 실패 시 정리
            throw err;
        }
    };

    /**
     * 화면 공유 종료
     */
    const stopSharing = () => {

        if (localStreamRef.current) {
            localStreamRef.current.getTracks().forEach(t => t.stop());
            localStreamRef.current = null;
        }
        if (currentCallRef.current) {
            currentCallRef.current.close();
            currentCallRef.current = null;
        }
        if (peerRef.current) {
            peerRef.current.destroy();
            peerRef.current = null;
        }
        setIsSharing(false);
        setShareCode(null);
    };

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            stopSharing();
        };
    }, []);

    return {
        shareCode,
        isSharing,
        error,
        startSharing,
        stopSharing
    };
};
