import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import logoA from '../../assets/logoA.png';
import { authAPI } from '../../services/authAPI';
import './ChangePasswordA.css';

const ChangePasswordA = () => {
    const navigate = useNavigate();
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');

    const handleSubmit = async () => {
        if (!password || !confirmPassword) {
            alert('비밀번호를 입력해주세요.');
            return;
        }
        if (password.length !== 6 || confirmPassword.length !== 6) {
            alert('비밀번호는 숫자 6자리여야 합니다.');
            return;
        }
        if (password !== confirmPassword) {
            alert('비밀번호가 일치하지 않습니다.');
            return;
        }
        try {
            const welfareVerified = localStorage.getItem('welfare_verified') === 'true';
            const storedCard = localStorage.getItem('welfare_card');
            if (!welfareVerified || !storedCard) {
                alert('복지카드 인증이 필요합니다.');
                return;
            }
            const welfareCard = JSON.parse(storedCard);
            const response = await authAPI.resetPasswordBlind(welfareCard, password);
            if (response?.result === 'success') {
                localStorage.removeItem('welfare_verified');
                localStorage.removeItem('welfare_card');
                alert('비밀번호가 변경되었습니다.');
                navigate('/A/login');
                return;
            }
            alert(response?.message || '비밀번호 변경에 실패했습니다.');
        } catch (error) {
            alert(error.message || '비밀번호 변경에 실패했습니다.');
        }
    };

    return (
        <div className="change-pw-container">
            <img
                src={logoA}
                alt="Logo"
                className="change-pw-logo"
                onClick={() => navigate('/')}
            />
            <div className="change-pw-card">
                <h1 className="change-pw-title">비밀번호 변경</h1>
                <p className="change-pw-desc">새 비밀번호를 설정하세요.</p>

                <div className="change-pw-field">
                    <label>새 비밀번호(숫자 6자리)</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value.replace(/[^0-9]/g, '').slice(0, 6))}
                        className="change-pw-input"
                    />
                </div>
                <div className="change-pw-field">
                    <label>비밀번호 확인</label>
                    <input
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value.replace(/[^0-9]/g, '').slice(0, 6))}
                        className="change-pw-input"
                    />
                </div>

                <button className="change-pw-btn" onClick={handleSubmit}>
                    비밀번호 변경하기
                </button>
            </div>
        </div>
    );
};

export default ChangePasswordA;
