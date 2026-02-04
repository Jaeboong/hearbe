import React, { useState, useEffect } from 'react';
import { User, Mail, Lock, ShieldCheck, Smile } from 'lucide-react';
import logoC from '../../assets/logoC.png';
import './FindPasswordC.css';

import { authAPI } from '../../services/authAPI';
import { emailService } from '../../services/emailService';

export default function FindPasswordPage({ onBack, micPermissionGranted }) {
    const [step, setStep] = useState(1);
    const [name, setName] = useState('');
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [verificationCode, setVerificationCode] = useState('');
    const [isSent, setIsSent] = useState(false);
    const [isVerified, setIsVerified] = useState(false);

    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');

    useEffect(() => {
        if (micPermissionGranted) {
            const text = '비밀번호 재설정 페이지입니다. 가입 정보를 입력하여 본인 인증을 진행해 주세요.';
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'ko-KR';
            window.speechSynthesis.speak(utterance);
        }
    }, [micPermissionGranted]);

    const handleSendVerification = async () => {
        if (!name || !username || !email) {
            alert('이름, 아이디, 그리고 이메일 주소를 모두 입력해주세요.');
            return;
        }
        try {
            // EmailJS로 인증번호 발송 (클라이언트 사이드)
            await emailService.sendVerificationCode(email, name);
            setIsSent(true);
            alert('인증번호가 이메일로 전송되었습니다. (3분 내 입력)');
        } catch (error) {
            alert(error.message || '인증번호 전송에 실패했습니다.');
        }
    };

    const handleVerifyCode = () => {
        if (!verificationCode) {
            alert('인증번호를 입력해주세요.');
            return;
        }
        try {
            // EmailJS 인증번호 확인 (클라이언트 사이드)
            emailService.verifyCode(email, verificationCode);
            setIsVerified(true);
            alert('본인 인증이 완료되었습니다. 하단의 버튼을 눌러 비밀번호를 재설정해주세요.');
        } catch (error) {
            alert(error.message || '인증번호가 일치하지 않습니다.');
        }
    };

    const handleNextStep = () => {
        if (!isVerified) {
            alert('먼저 이메일 인증을 완료해주세요.');
            return;
        }
        setStep(2);
    };

    const handleResetPassword = async (e) => {
        e.preventDefault();
        if (newPassword !== confirmPassword) {
            alert('비밀번호가 일치하지 않습니다.');
            return;
        }
        try {
            await authAPI.resetPassword(email, newPassword);
            alert('비밀번호가 성공적으로 재설정되었습니다.');
            onBack();
        } catch (error) {
            alert(error.message || '비밀번호 재설정에 실패했습니다.');
        }
    };

    return (
        <div className="find-pw-container-c">


            <main className="find-pw-main-c">
                <div className="pw-form-card-c">
                    <div className="pw-card-header-c">
                        <img src={logoC} alt="HearBe" className="pw-logo-c" />
                        <h1>비밀번호 재설정</h1>
                        <p className="pw-desc-c">안전한 서비스 이용을 위해 본인 확인이 필요합니다.</p>
                    </div>

                    {step === 1 ? (
                        /* 1단계: 본인 인증 폼 */
                        <div className="pw-step-form-c">
                            <div className="pw-input-group-c">
                                <label>이름</label>
                                <div className="pw-input-wrapper-c">
                                    <Smile className="pw-icon-c" size={32} />
                                    <input
                                        type="text"
                                        value={name}
                                        onChange={(e) => setName(e.target.value)}
                                        placeholder="성함 입력"
                                    />
                                </div>
                            </div>

                            <div className="pw-input-group-c">
                                <label>아이디</label>
                                <div className="pw-input-wrapper-c">
                                    <User className="pw-icon-c" size={32} />
                                    <input
                                        type="text"
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                        placeholder="아이디 입력"
                                    />
                                </div>
                            </div>

                            <div className="pw-input-group-c">
                                <label>이메일</label>
                                <div className="pw-input-flex-c">
                                    <div className="pw-input-wrapper-c flex-1-c">
                                        <Mail className="pw-icon-c" size={32} />
                                        <input
                                            type="email"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            placeholder="mail@example.com"
                                        />
                                    </div>
                                    <button onClick={handleSendVerification} className="pw-action-btn-c">
                                        {isSent ? '재발송' : '인증요청'}
                                    </button>
                                </div>
                            </div>

                            {isSent && (
                                <div className="pw-verify-section-c animate-fade-in-c">
                                    <div className="pw-input-group-c">
                                        <label>인증번호</label>
                                        <div className="pw-input-flex-c">
                                            <input
                                                type="text"
                                                value={verificationCode}
                                                onChange={(e) => setVerificationCode(e.target.value)}
                                                placeholder="6자리 숫자 입력"
                                                className="pw-code-input-c flex-1-c"
                                            />
                                            <button onClick={handleVerifyCode} className="pw-confirm-btn-c">
                                                확인
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            )}

                            <button
                                onClick={handleNextStep}
                                className={`pw-submit-btn-c active`}
                            >
                                비밀번호 재설정
                            </button>
                        </div>
                    ) : (
                        /* 2단계: 비밀번호 변경 폼 */
                        <form onSubmit={handleResetPassword} className="pw-step-form-c animate-fade-in-c">
                            <div className="pw-status-badge-c">
                                <ShieldCheck size={20} />
                                <span>본인 인증 완료</span>
                            </div>

                            <div className="pw-input-group-c">
                                <label>새 비밀번호</label>
                                <div className="pw-input-wrapper-c">
                                    <Lock className="pw-icon-c" size={20} />
                                    <input
                                        type="password"
                                        value={newPassword}
                                        onChange={(e) => setNewPassword(e.target.value)}
                                        placeholder="새 비밀번호 입력"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="pw-input-group-c">
                                <label>비밀번호 확인</label>
                                <div className="pw-input-wrapper-c">
                                    <Lock className="pw-icon-c" size={20} />
                                    <input
                                        type="password"
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                        placeholder="다시 한번 입력"
                                        required
                                    />
                                </div>
                            </div>

                            <button type="submit" className="pw-submit-btn-c active">
                                비밀번호 변경하기
                            </button>
                        </form>
                    )}
                </div>
            </main>

            <footer className="landing-footer">
                <p>© 2026 HearBe. All rights reserved.</p>
            </footer>
        </div>
    );
}
