import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Eye, EyeOff } from 'lucide-react';
import logoC from '../../assets/logoC.png'; // C형 로고로 변경
import { authAPI } from '../../services/authAPI';
import './LoginC.css';

export default function LoginC() {
    const navigate = useNavigate();
    const [showPassword, setShowPassword] = useState(false);
    const [id, setId] = useState('');
    const [password, setPassword] = useState('');
    const [rememberId, setRememberId] = useState(false);

    useEffect(() => {
        const savedUsername = localStorage.getItem('rememberedUsername');
        if (savedUsername) {
            setId(savedUsername);
            setRememberId(true);
        }
    }, []);


    const handleLogin = async (e) => {
        e.preventDefault();
        if (!id || !password) {
            alert("아이디와 비밀번호를 입력해주세요.");
            return;
        }

        try {
            const response = await authAPI.login(id, password);

            // 토큰 저장
            if (response.data && response.data.accessToken) {
                localStorage.setItem('accessToken', response.data.accessToken);
            }
            if (response.data && response.data.refreshToken) {
                localStorage.setItem('refreshToken', response.data.refreshToken);
            }

            // 아이디 저장 여부에 따라 localStorage에 저장/삭제
            if (rememberId) {
                localStorage.setItem('rememberedUsername', id);
            } else {
                localStorage.removeItem('rememberedUsername');
            }

            // Save user info basics
            if (response.data) {
                localStorage.setItem('user', JSON.stringify(response.data));
            }

            navigate('/C/mall');
        } catch (error) {
            console.error("Login failed:", error);
            alert(error.message || "아이디 또는 비밀번호가 일치하지 않습니다.");
        }
    };

    return (
        <div className="login-c-page">


            <main className="login-c-content">
                <div className="login-c-card">
                    <div className="logo-area-c">
<<<<<<< HEAD
                        <img
                            src={logoC}
                            alt="HearBe Logo"
                            className="logo-image-c"
                            onClick={() => navigate('/')}
                            style={{ cursor: 'pointer' }}
                        />
=======
                        <img src={logoC} alt="HearBe Logo" className="logo-image-c" />
>>>>>>> 438f06fc602c619edbd98d1b7f7ce94b95068863
                    </div>

                    <form className="login-c-form" onSubmit={handleLogin}>
                        <input
                            type="text"
                            placeholder="아이디 입력"
                            className="login-input-c"
                            value={id}
                            onChange={(e) => setId(e.target.value)}
                        />

                        <div className="password-wrapper-c">
                            <input
                                type={showPassword ? "text" : "password"}
                                placeholder="비밀번호 입력"
                                className="login-input-c"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                            <button type="button" onClick={() => setShowPassword(!showPassword)}>
                                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                            </button>
                        </div>

                        <button type="submit" className="login-submit-btn-c">로그인</button>

                        <div className="login-keep-c">
                            <input
                                type="checkbox"
                                id="rememberId"
                                checked={rememberId}
                                onChange={(e) => setRememberId(e.target.checked)}
                            />
                            <label htmlFor="rememberId">아이디 저장</label>
                        </div>

                        <div className="login-links-c">
                            <span onClick={() => navigate('/C/findId')}>아이디 찾기</span> | <span onClick={() => navigate('/C/findPassword')}>비밀번호 재설정</span> | <span onClick={() => navigate('/signup-c')}>회원가입</span>
                        </div>
                    </form>
                </div>
            </main>

            <footer className="landing-footer">
                <p>© 2026 HearBe. All rights reserved.</p>
            </footer>


        </div>
    );
}
