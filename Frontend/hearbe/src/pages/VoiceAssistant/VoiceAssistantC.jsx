import React, { useState, useEffect } from 'react';
import { MessageCircle, Mic, X, Volume2, ChevronDown, CheckSquare } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './VoiceAssistant.css';

export function VoiceAssistant({ mode }) {
    const [isOpen, setIsOpen] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [memoText, setMemoText] = useState('');
    const [memos, setMemos] = useState([]);

    // Mock 데이터
    const lastShoppingKeywords = ['노트북', '무선 마우스', 'USB-C 허브'];

    useEffect(() => {
        if (isOpen) {
            const text = `지난 쇼핑 키워드는 ${lastShoppingKeywords.join(', ')} 입니다.`;
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'ko-KR';
            window.speechSynthesis.speak(utterance);
        }
    }, [isOpen]);

    const handleToggle = () => setIsOpen(!isOpen);

    const handleStartRecording = () => {
        setIsRecording(true);
        // 실제 구현 시 브라우저 Web Speech API의 Recognition 시작 로직이 들어갑니다.
        setTimeout(() => {
            setIsRecording(false);
            setMemoText('이 상품 괜찮아 보이는데 나중에 다시 확인해보자');
        }, 3000);
    };

    const handleSaveMemo = () => {
        if (memoText.trim()) {
            setMemos([...memos, memoText]);
            setMemoText('');
        }
    };

    const handleDeleteMemo = (index) => {
        setMemos(memos.filter((_, i) => i !== index));
    };

    return (
        <div className="voice-assistant-fixed">
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 20, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 20, scale: 0.95 }}
                        className="assistant-panel"
                    >
                        {/* Header: Premium Gradient */}
                        <div className="assistant-header">
                            <div className="header-title-group">
                                <div className="icon-badge">
                                    <Volume2 size={18} />
                                </div>
                                <h3>음성 도우미</h3>
                            </div>
                            <button onClick={handleToggle} className="close-circle-btn">
                                <ChevronDown size={24} />
                            </button>
                        </div>

                        <div className="assistant-body">
                            {/* 1. 쇼핑 키워드 섹션 */}
                            <section className="info-section">
                                <div className="section-label">
                                    <div className="dot purple" />
                                    <h4>최근 쇼핑 키워드</h4>
                                </div>
                                <div className="keyword-cloud">
                                    {lastShoppingKeywords.map((word, i) => (
                                        <span key={i} className="keyword-tag">{word}</span>
                                    ))}
                                </div>
                                <p className="helper-text">💡 이전 검색 기반 추천 키워드입니다.</p>
                            </section>

                            {/* 2. 음성 메모 섹션 */}
                            <section className="info-section">
                                <div className="section-label">
                                    <div className="dot orange" />
                                    <h4>스마트 음성 메모</h4>
                                </div>

                                <button
                                    onClick={handleStartRecording}
                                    className={`mic-action-btn ${isRecording ? 'recording' : ''}`}
                                >
                                    <Mic size={20} />
                                    {isRecording ? '듣고 있어요...' : '음성으로 메모하기'}
                                </button>

                                {memoText && (
                                    <div className="memo-edit-area animate-fade-in">
                                        <textarea
                                            value={memoText}
                                            onChange={(e) => setMemoText(e.target.value)}
                                            rows={3}
                                        />
                                        <button onClick={handleSaveMemo} className="save-btn">메모 저장</button>
                                    </div>
                                )}

                                {/* 메모 리스트 */}
                                <div className="memo-list">
                                    {memos.length > 0 ? (
                                        memos.map((memo, idx) => (
                                            <div key={idx} className="memo-item">
                                                <p>{memo}</p>
                                                <button onClick={() => handleDeleteMemo(idx)}><X size={14} /></button>
                                            </div>
                                        ))
                                    ) : !memoText && (
                                        <div className="empty-state">
                                            <MessageCircle size={32} />
                                            <p>음성 메모가 여기에 표시됩니다.</p>
                                        </div>
                                    )}
                                </div>
                            </section>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Main Toggle Button: Apple-style Floating Action Button */}
            <button
                onClick={handleToggle}
                className={`assistant-toggle-btn ${isOpen ? 'active' : ''}`}
            >
                {isOpen ? <ChevronDown size={32} /> : <MessageCircle size={32} />}
                {!isOpen && (
                    <div className="noti-badge">{lastShoppingKeywords.length}</div>
                )}
            </button>
        </div>
    );
}