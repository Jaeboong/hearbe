import { Volume2, Download } from 'lucide-react';
import { useState } from 'react';
import { motion } from 'framer-motion';

export default function InitialSetup({ onComplete }) {
    const [showMicPermission, setShowMicPermission] = useState(true);
    const [micPermissionGranted, setMicPermissionGranted] = useState(false);
    const [showSpeakerTest, setShowSpeakerTest] = useState(false);
    const [showMcpDownloadPage, setShowMcpDownloadPage] = useState(false);

    // 1. 마이크 권한 요청 및 단계 전환
    const handleMicPermission = async (granted) => {
        if (granted) {
            try {
                await navigator.mediaDevices.getUserMedia({ audio: true });
                setMicPermissionGranted(true);
            } catch (error) {
                console.log('마이크 권한 거부됨');
                setMicPermissionGranted(false);
            }
        } else {
            setMicPermissionGranted(false);
        }
        setShowMicPermission(false);
        setShowSpeakerTest(true);
    };

    // 2. 스피커 테스트 완료 후 MCP 다운로드 페이지로 이동
    const handleSpeakerTest = () => {
        setShowSpeakerTest(false);
        setShowMcpDownloadPage(true);
    };

    // 3. MCP 설정 완료 처리 및 메인 이동
    const handleMcpDownload = () => {
        // 다시 뜨지 않도록 로컬스토리지에 저장
        localStorage.setItem('hearbe_mcp_setup_completed', 'true');
        onComplete(micPermissionGranted);
    };

    // 브라우저 TTS 기능을 활용한 테스트 음성 재생
    const playTestSound = () => {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance('안녕하세요. 이 소리가 선명하게 들리나요?');
        utterance.lang = 'ko-KR';
        window.speechSynthesis.speak(utterance);
    };

    // --- 단계 1: 마이크 권한 팝업 ---
    if (showMicPermission) {
        return (
            <div className="min-h-screen flex items-center justify-center p-8 bg-[#F8F8FA]">
                <div className="relative rounded-3xl p-12 max-w-2xl w-full shadow-2xl bg-white border border-[#7C3AED]/15">
                    <div className="flex flex-col items-center text-center">
                        <div className="relative w-24 h-24 rounded-2xl flex items-center justify-center bg-[#7C3AED] mb-6">
                            <Volume2 className="w-12 h-12 text-white" />
                        </div>
                        <h2 className="text-4xl font-bold mb-4 text-[#1A1A1A]">음성 안내 권한</h2>
                        <p className="text-xl mb-12 text-[#6B7280]">
                            시각장애인을 위한 음성 안내 서비스를 제공합니다.<br />
                            더 나은 쇼핑 경험을 위해 기능을 활성화하시겠습니까?
                        </p>
                        <div className="flex gap-4 w-full">
                            <button onClick={() => handleMicPermission(false)} className="flex-1 py-5 text-xl rounded-xl font-bold bg-[#F3F4F6] border-2 border-[#E5E7EB] text-[#4B5563]">나중에</button>
                            <button onClick={() => handleMicPermission(true)} className="flex-1 py-5 text-xl rounded-xl font-bold bg-[#7C3AED] text-white shadow-lg">활성화</button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // --- 단계 2: 스피커 테스트 팝업 ---
    if (showSpeakerTest) {
        return (
            <div className="min-h-screen flex items-center justify-center p-8 bg-[#F8F8FA]">
                <div className="relative max-w-4xl w-full rounded-[48px] p-20 shadow-2xl text-white"
                    style={{ background: 'linear-gradient(135deg, #A78BFA 0%, #7C3AED 100%)' }}>
                    <div className="flex flex-col items-center">
                        <motion.div animate={{ scale: [1, 1.1, 1] }} transition={{ repeat: Infinity, duration: 2 }}
                            className="w-40 h-40 rounded-full flex items-center justify-center bg-white/20 border-2 border-white/40 mb-10 shadow-2xl">
                            <Volume2 className="w-20 h-20 text-white" />
                        </motion.div>
                        <h2 className="text-6xl font-bold mb-5">스피커 테스트</h2>
                        <button onClick={playTestSound} className="mb-16 px-12 py-6 rounded-2xl text-xl font-bold bg-white/25 border-2 border-white/40">소리 듣기</button>
                        <div className="flex gap-6 w-full max-w-2xl">
                            <button onClick={() => handleSpeakerTest()} className="flex-1 py-6 text-xl rounded-2xl font-semibold bg-white/15 border-2 border-white/25 text-white">안 들림</button>
                            <button onClick={() => handleSpeakerTest()} className="flex-1 py-6 text-xl rounded-2xl font-bold bg-white text-[#7C3AED] shadow-xl">잘 들림 ✓</button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // --- 단계 3: MCP 다운로드 페이지 ---
    if (showMcpDownloadPage) {
        return (
            <div className="min-h-screen flex items-center justify-center p-8 bg-[#F8F8FA]">
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                    className="relative max-w-4xl w-full rounded-[48px] p-16 shadow-2xl text-white"
                    style={{ background: 'linear-gradient(135deg, #A78BFA 0%, #7C3AED 100%)' }}>
                    <div className="flex flex-col items-center text-center">
                        <div className="w-28 h-28 rounded-full bg-white/25 border-2 border-white/40 flex items-center justify-center mb-8 shadow-xl">
                            <Download className="w-14 h-14 text-white" />
                        </div>
                        <h2 className="text-6xl font-bold mb-8">MCP 프로그램 설치</h2>
                        <p className="text-2xl mb-16 opacity-90 leading-relaxed">음성 인식과 화면 공유 기능을 사용하려면<br />MCP 프로그램 설치가 필요합니다.</p>
                        <div className="flex gap-6 w-full max-w-2xl">
                            <button onClick={() => handleMcpDownload()} className="flex-1 py-6 text-xl rounded-2xl font-semibold bg-white/15 border-2 border-white/25 text-white">나중에</button>
                            <a href="/hearbe-mcp-server.exe" download onClick={() => handleMcpDownload()}
                                className="flex-1 py-6 text-xl rounded-2xl font-bold bg-white text-[#7C3AED] no-underline flex items-center justify-center gap-2 shadow-xl">다운로드</a>
                        </div>
                    </div>
                </motion.div>
            </div>
        );
    }

    return null;
}