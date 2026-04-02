import React, { useState, useRef } from 'react';
import { Share2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './StoreBrowserS.css';

const SharingJoinS = ({ onJoin, onCancel }) => {
    const [inputCode, setInputCode] = useState('');
    const inputRef = useRef(null);

    const handleInputChange = (e) => {
        const val = e.target.value.replace(/[^0-9]/g, '').slice(0, 4);
        setInputCode(val);
    };

    const focusInput = () => {
        if (inputRef.current) inputRef.current.focus();
    };

    const handleJoinClick = () => {
        if (inputCode.length === 4) {
            onJoin(inputCode);
        } else {
            alert("4자리 코드를 모두 입력해주세요.");
        }
    };

    return (
        <div className="sharing-join-container-overlay-s">
            <AnimatePresence>
                <motion.div
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0.9, opacity: 0 }}
                    className="join-modal-s"
                >
                    <div className="modal-icon-square-s">
                        <Share2 size={32} />
                    </div>
                    <h2 className="modal-title-s">공유 쇼핑 참여</h2>
                    <p className="modal-subtitle-s">상대방에게 받은 4자리 초대 코드를 입력하세요</p>

                    <div className="code-input-field-s cursor-pointer" onClick={focusInput}>
                        <div className="code-display-s">
                            {[0, 1, 2, 3].map((idx) => {
                                const char = inputCode[idx];
                                return (
                                    <span
                                        key={idx}
                                        className={`digit-s ${char ? 'entered' : 'placeholder'}`}
                                    >
                                        {char || '0'}
                                    </span>
                                );
                            })}
                        </div>
                        <input
                            ref={inputRef}
                            type="text"
                            pattern="\d*"
                            inputMode="numeric"
                            value={inputCode}
                            onChange={handleInputChange}
                            className="hidden-native-input-s"
                            autoFocus
                        />
                    </div>

                    <div className="modal-actions-s">
                        <button onClick={onCancel} className="btn-cancel-s cursor-pointer">취소</button>
                        <button
                            onClick={handleJoinClick}
                            className={`btn-join-s ${inputCode.length === 4 ? 'ready' : ''} cursor-pointer`}
                        >
                            참여하기
                        </button>
                    </div>
                </motion.div>
            </AnimatePresence>
        </div>
    );
};

export default SharingJoinS;
