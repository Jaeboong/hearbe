import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Swal from 'sweetalert2';
import { Eye, EyeOff, User, Lock, CheckCircle2 } from 'lucide-react';
import logo from '../../assets/logoA.png';
import { authAPI } from '../../services/authAPI';
import './LoginA.css';

const Login = () => {
    const navigate = useNavigate();
    const [id, setId] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
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
            handleLogin(null, savedId, savedPassword, true);
        }
    }, [navigate]);

    const handleLogin = async (e, loginId = id, loginPassword = password, isAuto = false) => {
        if (e) e.preventDefault();

        if (!loginId || !loginPassword) {
            if (!isAuto) {
                Swal.fire({
                    icon: 'warning',
                    text: '아이디와 비밀번호를 입력해주세요.',
                    confirmButtonText: '확인'
                });
            }
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
                const message = response?.message || '로그인에 실패했습니다.';
                Swal.fire({
                    icon: 'error',
                    text: message.includes('존재') || message.includes('없') ? '회원가입이 필요합니다.' : message,
                    confirmButtonText: '확인'
                });
            }
        } catch (error) {
            console.error('Login Error:', error);
            if (!isAuto) {
                const errorMessage = error?.message || '아이디 또는 비밀번호가 일치하지 않습니다.';
                Swal.fire({
                    icon: 'error',
                    text: errorMessage.includes('존재') || errorMessage.includes('없') ? '회원가입이 필요합니다.' : errorMessage,
                    confirmButtonText: '확인'
                });
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="login-a-page-new">
            <main className="login-a-content-new">
                <div className="login-a-card-new">
                    <div className="logo-area-a-new">
                        <img
                            src={logo}
                            alt="Logo"
                            onClick={() => navigate('/main')}
                            className="logo-image-a-new cursor-pointer"
                        />
                    </div>

                    <form className="login-a-form-new" onSubmit={(e) => handleLogin(e)}>
                        <div className="input-with-icon-a-new">
                            <User className="input-icon-a-new" size={32} />
                            <input
                                type="text"
                                placeholder="아이디"
                                className="login-input-a-new"
                                value={id}
                                onChange={(e) => setId(e.target.value)}
                            />
                        </div>

                        <div className="password-wrapper-a-new">
                            <Lock className="input-icon-a-new" size={32} />
                            <input
                                type={showPassword ? "text" : "password"}
                                placeholder="비밀번호"
                                className="login-input-a-new"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                maxLength={6}
                            />
                            <button
                                type="button"
                                className="pw-toggle-a-new"
                                onClick={() => setShowPassword(!showPassword)}
                            >
                                {showPassword ? <EyeOff size={36} /> : <Eye size={36} />}
                            </button>
                        </div>

                        <div className="login-options-a-new">
                            <label className="checkbox-container-a-new">
                                <input
                                    type="checkbox"
                                    checked={rememberLogin}
                                    onChange={(e) => setRememberLogin(e.target.checked)}
                                />
                                <span className="checkmark-a-new">
                                    {rememberLogin && <CheckCircle2 size={24} className="checked-icon" />}
                                </span>
                                <span className="label-text-a-new">로그인 유지</span>
                            </label>
                        </div>

                        <button
                            type="submit"
                            className="login-submit-btn-a-new"
                            disabled={isLoading}
                        >
                            {isLoading ? '로그인 중...' : '로그인'}
                        </button>

                        <div className="login-footer-links-a-new">
                            <span onClick={() => navigate('/A/findId')} className="cursor-pointer">아이디 찾기</span>
                            <span className="separator-a-new">|</span>
                            <span onClick={() => navigate('/A/findPassword')} className="cursor-pointer">비밀번호 재설정</span>
                            <span className="separator-a-new">|</span>
                            <span onClick={() => navigate('/A/signup')} className="cursor-pointer">회원가입</span>
                        </div>
                    </form>
                </div>
            </main>
        </div>
    );
};

export default Login;

