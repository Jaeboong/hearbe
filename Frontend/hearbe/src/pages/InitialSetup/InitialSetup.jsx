import { Volume2, Download } from 'lucide-react';
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const STEPS = {
    MCP_DOWNLOAD: 'mcp_download',
    MIC_PERMISSION: 'mic_permission',
    SPEAKER_TEST: 'speaker_test',
    COMPLETED: 'completed',
};

export default function InitialSetup({ onComplete }) {
    const [currentStep, setCurrentStep] = useState(STEPS.MCP_DOWNLOAD);

    const [micPermissionGranted, setMicPermissionGranted] = useState(false);

    useEffect(() => {
        if (currentStep === STEPS.COMPLETED) {
            onComplete(true);
        }
    }, [currentStep, onComplete]);

    const handleMcpDownload = () => {
        setCurrentStep(STEPS.MIC_PERMISSION);
    };

    const handleMicPermission = async (granted) => {
        if (granted) {
            try {
                await navigator.mediaDevices.getUserMedia({ audio: true });
                setMicPermissionGranted(true);
            } catch (error) {
                console.error('마이크 권한 거부됨', error);
                setMicPermissionGranted(false);
            }
        } else {
            setMicPermissionGranted(false);
        }
        setCurrentStep(STEPS.SPEAKER_TEST);
    };

    const handleSpeakerTest = () => {
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

    if (currentStep === STEPS.COMPLETED) {
        return null;
    }

    // --- 단계 1: MCP 다운로드 페이지 ---
    if (currentStep === STEPS.MCP_DOWNLOAD) {
        return (
            <div className="min-h-screen flex items-center justify-center p-8 bg-[#F8F8FA]">
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="relative rounded-3xl p-12 max-w-2xl w-full shadow-2xl bg-white border border-[#7C3AED]/15">
                    <div className="flex flex-col items-center text-center">
                        <div className="relative w-24 h-24 rounded-2xl flex items-center justify-center mb-6" style={{ background: 'linear-gradient(135deg, #A78BFA 0%, #7C3AED 100%)' }}>
                            <Download className="w-12 h-12 text-white" />
                        </div>
                        <h2 className="text-4xl font-bold mb-4 text-[#1A1A1A]">보조 프로그램 설치</h2>
                        <p className="text-xl mb-12 text-[#6B7280]">
                            음성 인식과 화면 공유 기능을 사용하려면<br />아래 프로그램을 설치해주세요.
                        </p>
                        <div className="flex gap-4 w-full">
                            <button onClick={handleMcpDownload} className="flex-1 py-5 text-xl rounded-xl font-bold bg-[#F3F4F6] border-2 border-[#E5E7EB] text-[#4B5563] cursor-pointer">나중에</button>
                            <a href="/downloads/MCPDesktop.zip" download onClick={handleMcpDownload}
                                className="flex-1 py-5 text-xl rounded-xl font-bold text-white shadow-lg no-underline flex items-center justify-center cursor-pointer" style={{ background: 'linear-gradient(135deg, #A78BFA 0%, #7C3AED 100%)' }}>다운로드</a>
                        </div>
                    </div>
                </motion.div>
            </div>
        );
    }

    // --- 단계 2: 마이크 권한 팝업 ---
    if (currentStep === STEPS.MIC_PERMISSION) {
        return (
            <div className="min-h-screen flex items-center justify-center p-8 bg-[#F8F8FA]">
                <div className="relative rounded-3xl p-12 max-w-2xl w-full shadow-2xl bg-white border border-[#7C3AED]/15">
                    <div className="flex flex-col items-center text-center">
                        <div className="relative w-24 h-24 rounded-2xl flex items-center justify-center mb-6" style={{ background: 'linear-gradient(135deg, #A78BFA 0%, #7C3AED 100%)' }}>
                            <Volume2 className="w-12 h-12 text-white" />
                        </div>
                        <h2 className="text-4xl font-bold mb-4 text-[#1A1A1A]">마이크 권한</h2>
                        <p className="text-xl mb-12 text-[#6B7280]">
                            HearBe는 음성 명령을 통해 쇼핑을 돕는 서비스입니다.<br />
                            마이크 사용 권한을 허용하여 음성 기능을 활성화하시겠습니까?
                        </p>
                        <div className="flex gap-4 w-full">
                            <button onClick={() => handleMicPermission(false)} className="flex-1 py-5 text-xl rounded-xl font-bold bg-[#F3F4F6] border-2 border-[#E5E7EB] text-[#4B5563] cursor-pointer">거부</button>
                            <button onClick={() => handleMicPermission(true)} className="flex-1 py-5 text-xl rounded-xl font-bold text-white shadow-lg cursor-pointer" style={{ background: 'linear-gradient(135deg, #A78BFA 0%, #7C3AED 100%)' }}>활성화</button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // --- 단계 3: 스피커 테스트 팝업 ---
    if (currentStep === STEPS.SPEAKER_TEST) {
        return (
            <div className="min-h-screen flex items-center justify-center p-8 bg-[#F8F8FA]">
                <div className="relative rounded-3xl p-12 max-w-2xl w-full shadow-2xl bg-white border border-[#7C3AED]/15">
                    <div className="flex flex-col items-center text-center">
                        <motion.div animate={{ scale: [1, 1.1, 1] }} transition={{ repeat: Infinity, duration: 2 }}
                            className="relative w-24 h-24 rounded-2xl flex items-center justify-center mb-6" style={{ background: 'linear-gradient(135deg, #A78BFA 0%, #7C3AED 100%)' }}>
                            <Volume2 className="w-12 h-12 text-white" />
                        </motion.div>
                        <h2 className="text-4xl font-bold mb-4 text-[#1A1A1A]">스피커 테스트</h2>
                        <p className="text-xl mb-6 text-[#6B7280]">
                            아래 버튼을 눌러 소리가 잘 들리는지 확인해주세요.
                        </p>
                        <button onClick={playTestSound} className="mb-12 px-8 py-4 rounded-xl text-xl font-bold bg-[#F3F4F6] border-2 border-[#E5E7EB] text-[#4B5563] cursor-pointer">소리 듣기</button>
                        <div className="flex gap-4 w-full">
                            <button onClick={handleSpeakerTest} className="flex-1 py-5 text-xl rounded-xl font-bold bg-[#F3F4F6] border-2 border-[#E5E7EB] text-[#4B5563] cursor-pointer">안 들림</button>
                            <button onClick={handleSpeakerTest} className="flex-1 py-5 text-xl rounded-xl font-bold text-white shadow-lg cursor-pointer" style={{ background: 'linear-gradient(135deg, #A78BFA 0%, #7C3AED 100%)' }}>잘 들림</button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}