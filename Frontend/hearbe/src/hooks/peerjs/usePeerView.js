import { useState, useEffect, useRef } from 'react';
import Peer from 'peerjs';
import { PEER_CONFIG } from '../../config/peerConfig';

/**
 * S형 사용자용 PeerJS Hook - 화면 보기
 */
export const usePeerView = () => {
    const [remoteStream, setRemoteStream] = useState(null);
    const [isConnected, setIsConnected] = useState(false);
    const [error, setError] = useState(null);

    const peerRef = useRef(null);
    const myAudioStreamRef = useRef(null);
    const currentCallRef = useRef(null);
    const connRef = useRef(null);
    const isConnectingRef = useRef(false); // 중복 연결 방지 플래그

    /**
     * 세션 입장
     * @param {string} code - 사용자가 입력한 4자리 코드
     */
    const joinSession = async (code) => {
        // 이미 연결 중이거나 연결된 상태면 무시
        if (isConnectingRef.current || isConnected || peerRef.current) {
            console.log('이미 연결 중이거나 연결된 상태입니다.');
            return;
        }

        isConnectingRef.current = true;
        console.log(`🚀 세션 입장 시도: ${code}`);

        try {
            setError(null);

            // 1. 마이크 권한 요청
            try {
                const audioStream = await navigator.mediaDevices.getUserMedia({
                    video: false,
                    audio: true
                });
                myAudioStreamRef.current = audioStream;
            } catch (e) {
                console.warn('마이크 권한 거부됨 (듣기만 가능)');
            }

            // 2. PeerJS Peer 생성
            // 랜덤 ID 사용 (충돌 방지)
            // const peerId = `share-${code}-guardian-${Math.floor(Math.random() * 1000)}`;
            // 기존 규칙 유지 (테스트 편의성을 위해) -> 문제 시 랜덤 ID로 변경 고려
            const peerId = `share-${code}-guardian`;

            const newPeer = new Peer(peerId, PEER_CONFIG);
            peerRef.current = newPeer;

            newPeer.on("open", (id) => {
                console.log(`✅ Peer 연결: ${id}`);

                // 3. User에게 데이터 연결 (신호)
                const userId = `share-${code}-user`;
                console.log(`📡 사용자(${userId})에게 신호 전송...`);

                const conn = newPeer.connect(userId, { reliable: true });
                connRef.current = conn;

                conn.on('open', () => {
                    console.log('✅ 사용자에게 신호 전송 완료. 전화 대기 중...');
                });

                conn.on('error', (e) => {
                    console.error('접속 실패:', e);
                    setError('사용자를 찾을 수 없습니다.');
                    isConnectingRef.current = false;
                });

                // 10초 타임아웃
                setTimeout(() => {
                    if (!isConnected && isConnectingRef.current) {
                        // setError('사용자로부터 응답이 없습니다.');
                        // 연결 유지
                    }
                }, 10000);
            });

            // 4. User로부터 전화 받기
            newPeer.on("call", (call) => {
                console.log('📞 사용자로부터 영상 전화 수신');

                // 마이크 전송하며 응답
                call.answer(myAudioStreamRef.current);
                currentCallRef.current = call;

                // 화면 스트림 수신
                call.on("stream", (stream) => {
                    console.log('🎥 화면 수신 완료!');
                    setRemoteStream(stream);
                    setIsConnected(true);
                    isConnectingRef.current = false;
                });

                call.on("close", () => {
                    console.log('사용자 연결 종료');
                    leave();
                });

                call.on("error", (e) => {
                    console.error('통화 에러:', e);
                    setError(`통화 에러: ${e.message}`);
                });
            });

            newPeer.on("error", (err) => {
                console.error('Peer 에러:', err);
                setError(err.message);
                // 특정 에러는 연결 실패로 간주
                if (err.type === 'peer-unavailable') {
                    setError('사용자가 접속하지 않았거나 코드가 잘못되었습니다.');
                    leave();
                }
                isConnectingRef.current = false;
            });

        } catch (err) {
            console.error('세션 입장 실패:', err);
            setError(err.message);
            isConnectingRef.current = false;
            leave(); // 정리
            throw err;
        }
    };

    /**
     * 세션 나가기
     */
    const leave = () => {
        console.log('👋 세션 나가기');
        isConnectingRef.current = false;

        if (myAudioStreamRef.current) {
            myAudioStreamRef.current.getTracks().forEach(t => t.stop());
            myAudioStreamRef.current = null;
        }
        if (currentCallRef.current) {
            currentCallRef.current.close();
            currentCallRef.current = null;
        }
        if (connRef.current) {
            connRef.current.close();
            connRef.current = null;
        }
        if (peerRef.current) {
            peerRef.current.destroy();
            peerRef.current = null;
        }
        setRemoteStream(null);
        setIsConnected(false);
    };

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            leave();
        };
    }, []);

    return {
        remoteStream,
        isConnected,
        error,
        joinSession,
        leave
    };
};
