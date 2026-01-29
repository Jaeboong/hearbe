import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, User, Lock, Eye, EyeOff, Mail, Calendar, Phone, CheckCircle2, UserPlus } from 'lucide-react';
import { validateUsername, validatePassword, validatePasswordConfirm, validateEmail } from '../../utils/validation';
import logoImage from '../../assets/HearBe_logo_.png';
import './SignUpC.css';

export default function SignUpC({ onBack }) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    email: '',
    name: '',
    birthdate: '',
    phone: '',
  });
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [agreements, setAgreements] = useState({
    all: false,
    age: false,
    terms: false,
    privacy: false
  });
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleChange = (field, value) => {
    setFormData({ ...formData, [field]: value });
    if (errors[field]) {
      setErrors({ ...errors, [field]: null });
    }
  };

  const handleConfirmPasswordChange = (value) => {
    setConfirmPassword(value);
    if (errors.confirmPassword) {
      setErrors({ ...errors, confirmPassword: null });
    }
  };

  const handleAgreementChange = (field, value) => {
    if (field === 'all') {
      setAgreements({ all: value, age: value, terms: value, privacy: value });
    } else {
      const newAgreements = { ...agreements, [field]: value };
      newAgreements.all = newAgreements.age && newAgreements.terms && newAgreements.privacy;
      setAgreements(newAgreements);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // 1. Validate Form
    const usernameError = validateUsername(formData.username);
    const passwordError = validatePassword(formData.password);
    const confirmPasswordError = validatePasswordConfirm(formData.password, confirmPassword);
    const emailError = validateEmail(formData.email);
    const nameError = !formData.name.trim() ? '이름을 입력해주세요.' : null;

    if (usernameError || passwordError || confirmPasswordError || emailError || nameError) {
      setErrors({
        username: usernameError,
        password: passwordError,
        confirmPassword: confirmPasswordError,
        email: emailError,
        name: nameError
      });
      return;
    }

    if (!agreements.terms) {
      alert('필수 이용약관에 동의해주세요.');
      return;
    }

    // --- Mock DB Logic Start ---
    try {
      const existingUsers = JSON.parse(localStorage.getItem('hearbe_mock_users') || '[]');
      const isDuplicate = existingUsers.some(user => user.username === formData.username);

      if (isDuplicate) {
        alert('이미 존재하는 아이디입니다.');
        return;
      }

      const newUser = {
        username: formData.username,
        password: formData.password,
        name: formData.name,
        email: formData.email,
        joinedAt: new Date().toISOString()
      };

      existingUsers.push(newUser);
      localStorage.setItem('hearbe_mock_users', JSON.stringify(existingUsers));

      setIsModalOpen(true);
    } catch (error) {
      console.error('Mock signup error:', error);
      alert('회원가입 중 오류가 발생했습니다.');
    }
  };

  return (
    <div className="signup-c-container">
      <main className="signup-c-main">
        <div className="signup-card-c">
          <div className="signup-header-c">
            <div className="header-title-group-c">
              <div className="title-icon-c">
                <UserPlus size={32} />
              </div>
              <h1>회원가입</h1>
            </div>
            <p className="signup-subtitle-c">HearBe 서비스 이용을 위한 회원가입을 진행합니다</p>
          </div>

          <form onSubmit={handleSubmit} className="signup-form-c">
            <div className="input-section-c">
              <div className={`input-c-group ${errors.username ? 'error' : ''}`}>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => handleChange('username', e.target.value)}
                  placeholder="아이디"
                  className="signup-input-c gray-bg-c"
                />
                {errors.username && <span className="error-text-c">{errors.username}</span>}
              </div>

              <div className={`input-c-group ${errors.password ? 'error' : ''}`}>
                <div className="password-wrapper-c">
                  <input
                    type={showPassword ? "text" : "password"}
                    value={formData.password}
                    onChange={(e) => handleChange('password', e.target.value)}
                    placeholder="비밀번호"
                    className="signup-input-c gray-bg-c"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="pw-toggle-c"
                  >
                    {showPassword ? <EyeOff size={20} color="#94A3B8" /> : <Eye size={20} color="#94A3B8" />}
                  </button>
                </div>
                {errors.password && <span className="error-text-c">{errors.password}</span>}
              </div>

              <div className={`input-c-group confirm-pw-group ${errors.confirmPassword ? 'error' : ''}`}>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => handleConfirmPasswordChange(e.target.value)}
                  placeholder="비밀번호 재확인"
                  className="signup-input-c gray-bg-c"
                />
                {errors.confirmPassword && <span className="error-text-c">{errors.confirmPassword}</span>}
              </div>
            </div>

            <hr className="form-divider-c" />

            <div className="input-section-c">
              <div className={`input-c-group ${errors.name ? 'error' : ''}`}>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleChange('name', e.target.value)}
                  placeholder="이름"
                  className="signup-input-c"
                />
                {errors.name && <span className="error-text-c">{errors.name}</span>}
              </div>
              <div className={`input-c-group ${errors.email ? 'error' : ''}`}>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleChange('email', e.target.value)}
                  placeholder="이메일 (example@gmail.com)"
                  className="signup-input-c"
                />
                {errors.email && <span className="error-text-c">{errors.email}</span>}
              </div>
            </div>

            <div className="terms-container-c">
              <div className="terms-item-c">
                <input
                  type="checkbox"
                  id="term1"
                  checked={agreements.terms}
                  onChange={(e) => setAgreements({ ...agreements, terms: e.target.checked })}
                />
                <label htmlFor="term1">[필수] 이용약관 동의</label>
              </div>
            </div>

            <button type="submit" className="signup-submit-btn-c">
              가입하기
            </button>
          </form>
        </div>
      </main>

      <AnimatePresence>
        {isModalOpen && (
          <div className="modal-overlay-c">
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="modal-content-c"
            >
              <div className="modal-icon-c">🎉</div>
              <h2 className="modal-title-c">가입 완료!</h2>
              <p className="modal-desc-c">
                HearBe의 회원이 되신 것을 축하드립니다.
              </p>
              <button onClick={() => { setIsModalOpen(false); if (onBack) onBack(); else navigate('/C/login'); }} className="modal-btn-c">
                확인
              </button>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      <footer className="landing-footer">
        <p>© 2026 HearBe. All rights reserved.</p>
      </footer>
    </div>
  );
}
