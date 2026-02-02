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

    // TTS 기능 추가
    React.useEffect(() => {
        const message = "로그인 페이지입니다. 아이디와 비밀번호를 입력해주세요.";
        const utterance = new SpeechSynthesisUtterance(message);
        utterance.lang = 'ko-KR';
        window.speechSynthesis.speak(utterance);

        return () => {
            window.speechSynthesis.cancel();
        };
    }, []);

    const speak = (msg) => {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(msg);
        utterance.lang = 'ko-KR';
        window.speechSynthesis.speak(utterance);
    };

    const handleLogin = async () => {
        if (!id || !password) {
            speak("아이디와 비밀번호를 입력해주세요.");
            alert("아이디와 비밀번호를 입력해주세요.");
            return;
        }
        setIsLoading(true);
        try {
            const response = await authAPI.login(id, password);

            if (response.code === 200) {
                if (response.data && response.data.accessToken) {
                    localStorage.setItem('accessToken', response.data.accessToken);
                }
                if (response.data && response.data.refreshToken) {
                    localStorage.setItem('refreshToken', response.data.refreshToken);
                }
                // 로그인 성공
                speak("로그인되었습니다.");
                navigate('/A/mall');
            } else {
                speak("로그인에 실패했습니다.");
                alert(response.message || "로그인에 실패했습니다.");
            }
        } catch (error) {
            console.error('Login Error:', error);
            speak("아이디 또는 비밀번호가 일치하지 않습니다.");
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
                    <img src={logo} alt="Logo" className="logo-image" onClick={() => speak("히어비 로고입니다.")} />
                </div>

                {/* Input Section */}
                <div className="input-group">
                    <input
                        type="text"
                        placeholder="아이디"
                        className="login-input first-input"
                        value={id}
                        onChange={(e) => setId(e.target.value)}
                        onFocus={() => speak("아이디를 입력하세요")}
                    />
                    <input
                        type="password"
                        placeholder="비밀번호"
                        className="login-input"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        onFocus={() => speak("비밀번호를 입력하세요")}
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
