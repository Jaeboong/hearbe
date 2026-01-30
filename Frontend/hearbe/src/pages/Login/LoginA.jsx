import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import logo from '../../assets/logoA.png';
import { authAPI } from '../../services/authAPI';
import './LoginA.css';

const Login = () => {
    const navigate = useNavigate();
    const [id, setId] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleLogin = async () => {
        if (!id || !password) {
            alert("아이디와 비밀번호를 입력해주세요.");
            return;
        }
        setIsLoading(true);
        try {
            const response = await authAPI.login({ username: id, password: password });

            if (response.code === 200) {
                if (response.data && response.data.accessToken) {
                    localStorage.setItem('accessToken', response.data.accessToken);
                }
                if (response.data && response.data.refreshToken) {
                    localStorage.setItem('refreshToken', response.data.refreshToken);
                }
                // 로그인 성공
                navigate('/A/mall');
            } else {
                alert(response.message || "로그인에 실패했습니다.");
            }
        } catch (error) {
            console.error('Login Error:', error);
            alert(error.message || "아이디 또는 비밀번호가 일치하지 않습니다.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-box">
                {/* Logo Section */}
                <div className="logo-area">
                    <img src={logo} alt="Logo" className="logo-image" />
                </div>

                {/* Input Section */}
                <div className="input-group">
                    <input
                        type="text"
                        placeholder="아이디"
                        className="login-input first-input"
                        value={id}
                        onChange={(e) => setId(e.target.value)}
                    />
                    <input
                        type="password"
                        placeholder="비밀번호"
                        className="login-input"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                </div>

                {/* Login Button */}
                <button className="login-button" onClick={handleLogin}>로그인</button>

                {/* Features (Save ID) */}
                <div className="login-options">
                    <label className="checkbox-container">
                        <input type="checkbox" defaultChecked />
                        <span className="checkmark"></span>
                        아이디 저장
                    </label>
                </div>

                {/* Footer Links */}
                <div className="login-footer">
                    <span>아이디 찾기</span>
                    <span className="login-separator">|</span>
                    <span>비밀번호 찾기</span>
                    <span className="login-separator">|</span>
                    <span className="signup-link" onClick={() => navigate('/A/signup')} style={{ cursor: 'pointer' }}>회원가입</span>
                </div>
            </div>
        </div>
    );
};

export default Login;
