import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, ChevronDown, X, Users, Monitor, User } from 'lucide-react';
import hLogo from '../../assets/h-logo.png';

const StoreBrowserS = () => {
  const navigate = useNavigate();
  const mediaRecorderRef = useRef(null);
  
  const [isAiPanelOpen, setIsAiPanelOpen] = useState(true);
  const [isRecording, setIsRecording] = useState(false);
  const [voiceMemo, setVoiceMemo] = useState('');
  const [participants, setParticipants] = useState([]);
  const [recentKeywords, setRecentKeywords] = useState([]);

  // 초기 데이터 로드 (DB 연동 구조)
  useEffect(() => {
    const fetchData = async () => {
      // 가상 데이터 (실제 연동 시 API 호출로 대체)
      setParticipants([
        { id: 1, name: '서해령 (나)', role: 'host' },
        { id: 2, name: '김싸피', role: 'guest' }
      ]);
      setRecentKeywords(['노트북', '무선 마우스', 'USB-C 허브']);
    };
    fetchData();
  }, []);

  // 오디오 녹음 및 AI 서버 전송 함수
  const toggleRecording = async () => {
    if (!isRecording) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        const chunks = [];

        mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
        
        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(chunks, { type: 'audio/wav' });
          
          // AI 서버로 전송할 데이터 포장
          const formData = new FormData();
          formData.append('audio', audioBlob);

          try {
            // AI 서버 API 호출 (STT/TTS 처리 위임)
            const response = await fetch('http://AI_SERVER_URL/api/v1/ai/voice', {
              method: 'POST',
              body: formData,
            });
            const result = await response.json();
            
            setVoiceMemo(result.text); // 서버가 보낸 STT 결과 텍스트
            
            if (result.audioUrl) {
              const audio = new Audio(result.audioUrl); // 서버가 보낸 TTS 결과 음성
              audio.play();
            }
          } catch (err) {
            console.error("AI 서버 통신 실패:", err);
          }
        };

        mediaRecorder.start();
        setIsRecording(true);
      } catch (err) {
        console.error("마이크 접근 거부:", err);
      }
    } else {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-gray-100 overflow-hidden font-sans">
      {/* 상단바 및 참가자 UI (디자인 유지) */}
      <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 flex items-center bg-white/90 backdrop-blur-md px-6 py-2 rounded-full shadow-lg border border-[#78A196]">
        <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse mr-3" />
        <span className="text-[#78A196] font-bold text-sm flex items-center italic">
          <Monitor size={16} className="mr-2" /> 화면 공유 중 (코드: 5891)
        </span>
      </div>

      {/* 우측 상단 참가자 버튼 */}
      <div className="fixed top-4 right-4 z-50">
        <div className="flex items-center bg-white px-4 py-2 rounded-xl shadow-md border border-gray-100">
          <Users size={18} className="text-[#78A196] mr-2" />
          <span className="text-gray-700 font-bold text-sm">참가자 ({participants.length}명)</span>
        </div>
      </div>

      <iframe src="https://smartstore.naver.com" className="w-full h-screen border-none" title="Store" />

      {/* 좌측 하단 AI 도우미 섹션 */}
      <div className="fixed bottom-6 left-6 z-50 w-80">
        <AnimatePresence>
          {isAiPanelOpen && (
            <motion.div initial={{ y: 50, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="bg-white rounded-[24px] shadow-2xl overflow-hidden border border-gray-100">
              <div className="bg-[#78A196] p-4 flex items-center justify-between text-white font-bold">
                <div className="flex items-center space-x-2">
                  <img src={hLogo} alt="Logo" className="w-5 h-5 brightness-0 invert" />
                  <span>AI 도우미</span>
                </div>
                <button onClick={() => setIsAiPanelOpen(false)}><ChevronDown size={20} /></button>
              </div>

              <div className="p-6 space-y-6">
                <div>
                  <h3 className="text-gray-400 text-xs font-bold mb-3">지난 쇼핑 키워드</h3>
                  <div className="flex flex-wrap gap-2">
                    {recentKeywords.map((word, i) => (
                      <span key={i} className="bg-[#E8F3F1] text-[#78A196] px-3 py-1.5 rounded-full text-xs font-bold">{word}</span>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-gray-400 text-xs font-bold mb-3">AI 음성 대화</h3>
                  {voiceMemo && (
                    <div className="bg-blue-50 p-3 rounded-xl mb-3 text-blue-600 text-sm font-medium">
                      "{voiceMemo}"
                    </div>
                  )}
                  <button
                    onClick={toggleRecording}
                    className={`w-full py-4 rounded-2xl flex items-center justify-center space-x-2 font-bold transition-all shadow-md ${
                      isRecording ? 'bg-red-500 text-white animate-pulse' : 'bg-[#4A78FF] text-white'
                    }`}
                  >
                    <Mic size={20} />
                    <span>{isRecording ? '녹음 중지' : 'AI에게 말하기'}</span>
                  </button>
                  <p className="text-[10px] text-gray-300 mt-2 text-center">클릭하여 AI와 대화를 시작하세요</p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default StoreBrowserS;