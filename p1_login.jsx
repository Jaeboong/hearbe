import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import hLogo from '../../assets/HearBe_A_logo.png';
import { findUser } from '../../utils/userStorage';
import './LoginA.css';

const Login = () => {
    const navigate = useNavigate();
    const [id, setId] = useState('');
    const [password, setPassword] = useState('');

    const handleLogin = () => {
        if (!id || !password) {
            alert("아이디와 비밀번호를 입력해주세요.");
            return;
        }

        const user = findUser(id, password);
        if (user) {
            // Success
            navigate('/A/mall');
        } else {
            alert("아이디 또는 비밀번호가 일치하지 않습니다.");
        }
    };

    return (
        <div className="login-container-a">
            <div className="login-box-a">
                {/* Logo Section */}
                <div className="logo-area-a">
                    <img src={hLogo} alt="Logo" className="logo-image-a" />
                </div>

                {/* Input Section */}
                <div className="input-group-a">
                    <input
                        type="text"
                        placeholder="아이디"
                        className="login-input-a first-input-a"
                        value={id}
                        onChange={(e) => setId(e.target.value)}
                    />
                    <input
                        type="password"
                        placeholder="비밀번호"
                        className="login-input-a"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                </div>

                {/* Login Button */}
                <button className="login-button-a" onClick={handleLogin}>로그인</button>

                {/* Features (Save ID) */}
                <div className="login-options-a">
                    <label className="checkbox-container-a">
                        <input type="checkbox" defaultChecked />
                        <span className="checkmark-a"></span>
                        아이디 저장
                    </label>
                </div>

                {/* Footer Links */}
                <div className="login-footer-a">
                    <span>아이디 찾기</span>
                    <span className="login-separator-a">|</span>
                    <span>비밀번호 찾기</span>
                    <span className="login-separator-a">|</span>
                    <span className="signup-link-a" onClick={() => navigate('/A/signup')} style={{ cursor: 'pointer' }}>회원가입</span>
                </div>
            </div>
        </div>
    );
};

export default Login;
