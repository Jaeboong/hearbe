import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import logo from '../../assets/logoA.png';
import { authAPI } from '../../services/authAPI';
import './LoginA.css'; // Importing empty file for safety, can be removed later

const Login = () => {
    const navigate = useNavigate();
    const [id, setId] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [rememberLogin, setRememberLogin] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('accessToken');
        if (token) {
            navigate('/A/mall');
            return;
        }
        const savedId = localStorage.getItem('savedLoginId');
        const savedPassword = localStorage.getItem('savedLoginPassword');
        if (savedId) {
            setId(savedId);
            setRememberLogin(true);
        }
        if (savedPassword) {
            setPassword(savedPassword);
            setRememberLogin(true);
        }
        if (savedId && savedPassword) {
            handleLogin(savedId, savedPassword, true);
        }
    }, [navigate]);

    const handleLogin = async (loginId = id, loginPassword = password, isAuto = false) => {
        if (!loginId || !loginPassword) {
            alert('아이디와 비밀번호를 입력해주세요.');
            return;
        }
        setIsLoading(true);
        try {
            const response = await authAPI.login(loginId, loginPassword);

            const accessToken =
                response?.data?.accessToken ||
                response?.data?.access_token ||
                response?.accessToken ||
                response?.access_token;
            const refreshToken =
                response?.data?.refreshToken ||
                response?.data?.refresh_token ||
                response?.refreshToken ||
                response?.refresh_token;

            if (accessToken) {
                localStorage.setItem('accessToken', accessToken);
            }
            if (refreshToken) {
                localStorage.setItem('refreshToken', refreshToken);
            }

            const isSuccess = response?.code === 200 || !!accessToken;

            if (isSuccess) {
                if (rememberLogin) {
                    localStorage.setItem('savedLoginId', loginId);
                    localStorage.setItem('savedLoginPassword', loginPassword);
                } else {
                    localStorage.removeItem('savedLoginId');
                    localStorage.removeItem('savedLoginPassword');
                }
                // 로그인 성공
                navigate('/A/mall');
            } else if (!isAuto) {
                const message = response?.message || '';
                if (message.includes('존재') || message.includes('없')) {
                    alert('회원가입이 필요합니다.');
                } else {
                    alert(message || '로그인에 실패했습니다.');
                }
            }
        } catch (error) {
            console.error('Login Error:', error);
            if (!isAuto) {
                const errorMessage = error?.message || '';
                if (errorMessage.includes('존재') || errorMessage.includes('없')) {
                    alert('회원가입이 필요합니다.');
                } else {
                    alert(errorMessage || '아이디 또는 비밀번호가 일치하지 않습니다.');
                }
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-box">
                {/* Logo Section */}
                <div className="logo-area">
                    <img
                        src={logo}
                        alt="Logo"
                        className="logo-image cursor-pointer"
                        onClick={() => navigate('/')}
                    />
                </div>

                <form
                    className="login-form"
                    onSubmit={(e) => {
                        e.preventDefault();
                        handleLogin();
                    }}
                >
                    {/* Input Section */}
                    <div className="input-box">
                        <input
                            type="text"
                            placeholder="아이디"
                            className="login-input"
                            value={id}
                            onChange={(e) => setId(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter') {
                                    handleLogin();
                                }
                            }}
                        />
                    </div>
                    <div className="input-box">
                        <input
                            type="password"
                            placeholder="비밀번호"
                            className="login-input"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            maxLength={6}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter') {
                                    handleLogin();
                                }
                            }}
                        />
                    </div>

                    {/* Login Button */}
                    <button className="login-button" type="submit" disabled={isLoading}>
                        로그인
                    </button>
                </form>

                {/* Features (Save ID) */}
                <div className="login-options">
                    <label className="checkbox-container">
                        <input
                            type="checkbox"
                            className="checkbox-input"
                            checked={rememberLogin}
                            onChange={(e) => setRememberLogin(e.target.checked)}
                        />
                        <span className="checkmark">
                            <span className="checkmark-icon"></span>
                        </span>
                        자동 로그인
                    </label>
                </div>

                {/* Footer Links */}
                <div className="login-footer">
                    <span onClick={() => navigate('/A/findId')} className="cursor-pointer">아이디 찾기</span>
                    <span className="login-separator">|</span>
                    <span onClick={() => navigate('/A/findPassword')} className="cursor-pointer">비밀번호 변경</span>
                    <span className="login-separator">|</span>
                    <span onClick={() => navigate('/A/signup')} className="cursor-pointer">
                        회원가입
                    </span>
                </div>
            </div>
        </div>
    );
};

export default Login;
