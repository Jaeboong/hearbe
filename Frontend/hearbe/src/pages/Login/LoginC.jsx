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
            // LoginRequest DTO requires 'username' and 'password'
            const response = await authAPI.login(id, password);

            // Assuming response.data contains tokens or user info
            // API Response format: ApiResponse<LoginResponse> -> data: LoginResponse
            // LoginResponse fields needs to be checked. Usually it has accessToken/refreshToken/user info.
            console.log("Login Success:", response);

            // Save token if available (adjust based on actual response structure)
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
                        <img src={logoC} alt="HearBe Logo" className="logo-image-c" />
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
                                id="rememberId" // ID를 'rememberId'로 변경
                                checked={rememberId} // rememberId 상태에 연결
                                onChange={(e) => setRememberId(e.target.checked)} // 상태 변경 핸들러 연결
                            />
                            <label htmlFor="rememberId">아이디 저장</label> {/* 라벨 텍스트 변경 */}
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
