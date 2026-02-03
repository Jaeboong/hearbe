import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import hLogo from '../../assets/h-logo.png';
import GuardianJoinModal from '../../components/ShareCode/GuardianJoinModal';
import './LoginS.css';

const LoginS = () => {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(true);

  const handleJoin = (code) => {
    // 코드 검증은 GuardianViewS 내부에서 하거나 여기서 API 호출
    // 일단 바로 이동
    navigate('/S/guardian-view', { state: { code } });
  };

  const handleClose = () => {
    setIsModalOpen(false);
    navigate('/main'); // 메인으로 돌아가기
  };

  // 모달이 닫히면 다시 메인으로 돌아가는 것이 자연스러움
  if (!isModalOpen) return null;

  return (
    <div className="login-s-container">
      {/* 배경용 (기존 디자인 유지) */}
      <div className="login-s-card" style={{ opacity: 0.5 }}>
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
      </div>

      {/* 실제 기능 모달 */}
      <GuardianJoinModal
        isOpen={isModalOpen}
        onClose={handleClose}
        onJoin={handleJoin}
      />
    </div>
  );
};

export default LoginS;
