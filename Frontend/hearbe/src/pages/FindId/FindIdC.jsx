import { ArrowLeft, User, Mail, Check } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './FindIdC.css';
import logoC from '../../assets/logoC.png';

import { authAPI } from '../../services/authAPI';

export default function FindIdPage({ onBack, micPermissionGranted }) {
    const navigate = useNavigate();
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [verificationCode, setVerificationCode] = useState('');
    const [isSent, setIsSent] = useState(false);
    const [isVerified, setIsVerified] = useState(false);
    const [showIdPopup, setShowIdPopup] = useState(false);
    const [foundUserId, setFoundUserId] = useState('');

    useEffect(() => {
        if (micPermissionGranted) {
            const text = '아이디 찾기 페이지입니다. 이름과 이메일을 입력하여 인증을 진행해 주세요.';
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'ko-KR';
            window.speechSynthesis.speak(utterance);
        }
    }, [micPermissionGranted]);

    const handleSendVerification = async () => {
        if (!name || !email) {
            alert('이름과 이메일 주소를 입력해주세요.');
            return;
        }
        try {
            await authAPI.sendEmailVerification(email);
            setIsSent(true);
            alert('인증번호가 이메일로 전송되었습니다.');
        } catch (error) {
            alert(error.message || '인증번호 전송에 실패했습니다.');
        }
    };

    const handleVerifyCode = async () => {
        if (!verificationCode) {
            alert('인증번호를 입력해주세요.');
            return;
        }
        try {
            await authAPI.verifyEmailCode(email, verificationCode);
            setIsVerified(true);
            alert('인증이 완료되었습니다.');
        } catch (error) {
            alert(error.message || '인증번호가 일치하지 않습니다.');
        }
    };

    const handleFindId = async () => {
        if (!isVerified) {
            alert('먼저 이메일 인증을 완료해주세요.');
            return;
        }
        try {
            const response = await authAPI.findId(name, email);
            if (response.data) {
                setFoundUserId(response.data);
                setShowIdPopup(true);
            } else {
                alert('해당 정보로 가입된 아이디를 찾을 수 없습니다.');
            }
        } catch (error) {
            alert(error.message || '아이디 찾기에 실패했습니다.');
        }
    };

    return (
        <div className="find-id-container">


            <main className="find-id-main">
                <div className="find-id-card">
                    <div className="card-header">
                        <img src={logoC} alt="HearBe" className="mini-logo" />
                        <h1>아이디 찾기</h1>
                        <p>가입 시 등록한 정보로 아이디를 찾을 수 있습니다.</p>
                    </div>

                    <div className="form-section">
                        <div className="input-field">
                            <label>이름</label>
                            <div className="input-wrapper">
                                <User className="input-icon" />
                                <input
                                    type="text"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    placeholder="성함을 입력하세요"
                                />
                            </div>
                        </div>

                        <div className="input-field">
                            <label>이메일</label>
                            <div className="flex-row gap-2">
                                <div className="input-wrapper grow">
                                    <Mail className="input-icon" />
                                    <input
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        placeholder="example@mail.com"
                                    />
                                </div>
                                <button onClick={handleSendVerification} className="secondary-btn">
                                    {isSent ? '재발송' : '인증요청'}
                                </button>
                            </div>
                        </div>

                        {isSent && (
                            <div className="input-field animate-slide-down">
                                <label>인증번호</label>
                                <div className="flex-row gap-2">
                                    <input
                                        type="text"
                                        value={verificationCode}
                                        onChange={(e) => setVerificationCode(e.target.value)}
                                        placeholder="6자리 숫자 입력"
                                        className="grow code-input"
                                    />
                                    <button onClick={handleVerifyCode} className="black-btn">
                                        확인
                                    </button>
                                </div>
                            </div>
                        )}

                        <button
                            onClick={handleFindId}
                            className="submit-full-btn active"
                        >
                            아이디 확인하기
                        </button>
                    </div>
                </div>
            </main>

            <footer className="landing-footer">
                <p>© 2026 HearBe. All rights reserved.</p>
            </footer>

            {showIdPopup && (
                <div className="modal-overlay-c">
                    <div className="id-result-modal-c">
                        <div className="check-icon-wrapper-c">
                            <Check className="check-icon-c" />
                        </div>
                        <h2 className="modal-title-c">아이디 조회 결과</h2>
                        <div className="result-box-c">
                            <span className="result-label-c">회원님의 아이디는</span>
                            <strong className="result-value-c">{foundUserId}</strong>
                        </div>
                        <button onClick={() => navigate('/C/login')} className="modal-confirm-btn-c"> {/* 로그인 페이지로 이동 */}
                            확인 및 로그인하기
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}