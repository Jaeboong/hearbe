import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ArrowLeft, User, X } from 'lucide-react';
import { motion } from 'framer-motion';
import { io } from 'socket.io-client';
import { SOCKET_SERVER_URL, DEFAULT_MALL_URL } from '../../config';
import './StoreBrowserS.css';

const SharingViewerS = () => {
    const navigate = useNavigate();
    const location = useLocation();

    // --- UI States ---
    const [mallUrl, setMallUrl] = useState(DEFAULT_MALL_URL);
    const [meetingCode, setMeetingCode] = useState('');

    // --- WebRTC & Socket States ---
    const [participants, setParticipants] = useState([]);
    const [remoteStream, setRemoteStream] = useState(null);
    const socketRef = useRef();
    const pcsRef = useRef({});
    const videoRef = useRef();

    useEffect(() => {
        if (remoteStream && videoRef.current) {
            videoRef.current.srcObject = remoteStream;
        }
    }, [remoteStream]);

    useEffect(() => {
        const code = location.state?.code;
        if (!code) {
            navigate('/S/join');
            return;
        }
        setMeetingCode(code);
        connectToStore(code);

        return () => {
            if (socketRef.current) socketRef.current.disconnect();
        };
    }, [location.state, navigate]);

    // 1. 방 참여 로직 (수신자 모드)
    const connectToStore = (code) => {
        socketRef.current = io(SOCKET_SERVER_URL);
        socketRef.current.emit("join_room", { roomCode: code, name: "나 (참가자)" });

        setParticipants([
            { id: 'host', name: '방장', isMe: false },
            { id: 'me', name: '나 (참가자)', isMe: true }
        ]);

        // WebRTC 시그널링 (수신자 모드: 오퍼를 받아서 응답)
        socketRef.current.on("get_offer", async ({ offer, from }) => {
            const pc = new RTCPeerConnection({
                iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
            });
            pcsRef.current[from] = pc;

            pc.onicecandidate = (e) => {
                if (e.candidate) {
                    socketRef.current.emit("candidate", { candidate: e.candidate, to: from });
                }
            };

            pc.ontrack = (event) => {
                setRemoteStream(event.streams[0]);
            };

            await pc.setRemoteDescription(new RTCSessionDescription(offer));
            const answer = await pc.createAnswer();
            await pc.setLocalDescription(answer);
            socketRef.current.emit("answer", { answer, to: from });
        });

        socketRef.current.on("get_candidate", ({ candidate, from }) => {
            if (pcsRef.current[from]) {
                pcsRef.current[from].addIceCandidate(new RTCIceCandidate(candidate));
            }
        });

        socketRef.current.on("url_update", (newUrl) => {
            setMallUrl(newUrl);
        });
    };

    const handleLeave = () => {
        if (socketRef.current) socketRef.current.disconnect();
        navigate('/main');
    };

    return (
        <div className="store-browser-container-s">
            {/* 브라우저 영역 */}
            <div className="iframe-wrapper-s">
                {remoteStream ? (
                    <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        className="sharing-screen-video"
                    />
                ) : (
                    <div className="waiting-screen-s">
                        <p className="waiting-text-s">방장님이 화면 공유를 시작하기를 기다리고 있습니다...</p>
                    </div>
                )}
            </div>

            {/* 고정 뒤로가기 */}
            <button onClick={handleLeave} className="back-button-circle-s cursor-pointer">
                <ArrowLeft size={24} />
            </button>

            {/* 상단 정보 바 */}
            <motion.div
                initial={{ y: -50, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                className="top-sharing-info-s"
            >
                <div className="status-dot-s" />
                <span className="info-text-s">
                    실시간 공유 시청 중 <span className="divider-s">|</span> 초대 코드: <strong>{meetingCode}</strong>
                </span>
            </motion.div>

            {/* 우측 참가자 패널 */}
            <motion.div
                initial={{ x: 100, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                className="participants-panel-s"
            >
                <div className="panel-header-s">참가자 ({participants.length}명)</div>
                <div className="participant-list-s">
                    {participants.map((person) => (
                        <div key={person.id} className="participant-item-s">
                            <div className="user-avatar-s">
                                <User size={18} />
                            </div>
                            <span className="user-name-s">{person.name}</span>
                        </div>
                    ))}
                    {participants.length === 1 && (
                        <div className="participant-item-s waiting">
                            <div className="user-avatar-s"><User size={18} /></div>
                            <span className="user-name-s">대기 중...</span>
                        </div>
                    )}
                </div>
            </motion.div>

            {/* 하단 액션바 */}
            <motion.div
                initial={{ y: 100, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                className="bottom-sharing-actions-s"
            >
                <button onClick={handleLeave} className="share-action-btn-s purple-btn cursor-pointer">
                    <X size={20} /> 공유 종료
                </button>
            </motion.div>
        </div>
    );
};

export default SharingViewerS;
