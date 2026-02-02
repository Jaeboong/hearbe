import { useState } from 'react';
import PropTypes from 'prop-types';
import './GuardianJoinModal.css';

/**
 * 공유 쇼핑 입장 모달 (S형용)
 * 4자리 코드를 입력하여 사용자 화면에 접속합니다.
 */
const GuardianJoinModal = ({ isOpen, onClose, onJoin }) => {
    const [code, setCode] = useState('');
    const [error, setError] = useState('');

    if (!isOpen) return null;

    const handleCodeChange = (e) => {
        const value = e.target.value.replace(/[^0-9]/g, '').slice(0, 4);
        setCode(value);
        setError('');
    };

    const handleJoin = () => {
        if (code.length !== 4) {
            setError('4자리 코드를 입력해주세요');
            return;
        }
        onJoin(code);
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && code.length === 4) {
            handleJoin();
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content guardian-modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal-icon">🔗</div>
                <h2 className="modal-title">공유 쇼핑 입장</h2>
                <p className="modal-subtitle">조건으로 입장해주세요</p>

                <div className="code-input-container">
                    <input
                        type="text"
                        className={`code-input ${error ? 'error' : ''}`}
                        placeholder="초대코드 입력 (4자리)"
                        value={code}
                        onChange={handleCodeChange}
                        onKeyPress={handleKeyPress}
                        maxLength={4}
                        autoFocus
                    />
                    {error && <p className="error-message">{error}</p>}
                </div>

                <div className="modal-buttons">
                    <button className="btn-cancel" onClick={onClose}>
                        취소
                    </button>
                    <button
                        className="btn-join"
                        onClick={handleJoin}
                        disabled={code.length !== 4}
                    >
                        입장하기
                    </button>
                </div>
            </div>
        </div>
    );
};

GuardianJoinModal.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    onJoin: PropTypes.func.isRequired
};

export default GuardianJoinModal;
