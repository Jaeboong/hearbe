import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import hLogo from '../../assets/logoA.png';
import './LoginS.css';

const LoginS = () => {
  const navigate = useNavigate();
  const [inviteCode, setInviteCode] = useState('');

  const handleEntry = (e) => {
    e.preventDefault();
    if (inviteCode.length === 4) {
      navigate('/store-c');
    } else {
      alert('초대코드 4자리를 입력해주세요.');
    }
  };

  return (
    <div className="login-s-container">
      <div className="login-s-card">
        <div className="logo-wrapper">
          <img
            src={hLogo}
            alt="HearBe 로고"
            className="s-logo"
            onClick={() => window.location.assign('/')}
            style={{ cursor: 'pointer' }}
          />
        </div>

        <h1 className="login-s-title">공유 쇼핑 입장</h1>
        <p className="login-s-desc">초대코드를 입력해주세요</p>

        <form onSubmit={handleEntry} className="login-s-form">
          <input
            type="text"
            maxLength={4}
            value={inviteCode}
            onChange={(e) => setInviteCode(e.target.value.replace(/[^0-9]/g, ''))}
            placeholder="초대코드 입력 (4자리)"
            className="invite-input"
          />

          <div className="login-s-btns">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="btn-cancel"
            >
              취소
            </button>
            <button
              type="submit"
              className="btn-submit"
            >
              입장하기
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LoginS;
