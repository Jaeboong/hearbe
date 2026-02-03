import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { ArrowLeft, User, Lock, Eye, EyeOff, Mail, Calendar, Phone, CheckCircle2, UserPlus } from 'lucide-react';
import { validateUsername, validatePassword, validatePasswordConfirm, validateEmail, validateName } from '../../utils/validation';
import { authAPI } from '../../services/authAPI';
<<<<<<< HEAD
import logoC from '../../assets/logoC.png';
=======
import logoC from '../../assets/logoC.png'; // C형 로고로 변경
>>>>>>> 438f06fc602c619edbd98d1b7f7ce94b95068863
import './SignUpC.css';

export default function SignUpC({ onBack }) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    email: '',
    name: '',
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
  const [isUsernameChecked, setIsUsernameChecked] = useState(false);
  const [isUsernameAvailable, setIsUsernameAvailable] = useState(false);

  const handleChange = (field, value) => {
    setFormData({ ...formData, [field]: value });
    if (errors[field]) {
      setErrors({ ...errors, [field]: null });
    }
    // 아이디 입력이 변경되면 중복확인 상태 초기화
    if (field === 'username') {
      setIsUsernameChecked(false);
      setIsUsernameAvailable(false);
    }
  };

  const handleConfirmPasswordChange = (value) => {
    setConfirmPassword(value);
    if (errors.confirmPassword) {
      setErrors({ ...errors, confirmPassword: null });
    }
  };

  const handleCheckUsername = async () => {
    const usernameError = validateUsername(formData.username);
    if (usernameError) {
      alert(usernameError);
      return;
    }

    try {
      const apiResponse = await authAPI.checkDuplicate(formData.username);
<<<<<<< HEAD
      //const isDuplicate = apiResponse && apiResponse.success === true ? apiResponse.data === true : false;
      const isDuplicate = apiResponse.data;

      if (isDuplicate==false) {
=======
      if (apiResponse.available) {
>>>>>>> 438f06fc602c619edbd98d1b7f7ce94b95068863
        setIsUsernameChecked(true);
        setIsUsernameAvailable(true);
        alert('사용 가능한 아이디입니다.');
      } else {
        setIsUsernameChecked(true);
        setIsUsernameAvailable(false);
        alert('이미 사용 중인 아이디입니다.');
      }
    } catch (error) {
      console.error('Username check error:', error);
      alert('아이디 중복 확인에 실패했습니다.');
<<<<<<< HEAD
      setIsUsernameChecked(false);
=======
      setIsUsernameChecked(false); // 에러 발생 시 중복확인 상태 초기화
    }
  };

  const handleAgreementChange = (field, value) => {
    if (field === 'all') {
      setAgreements({ all: value, age: value, terms: value, privacy: value });
    } else {
      const newAgreements = { ...agreements, [field]: value };
      newAgreements.all = newAgreements.age && newAgreements.terms && newAgreements.privacy;
      setAgreements(newAgreements);
>>>>>>> 438f06fc602c619edbd98d1b7f7ce94b95068863
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const usernameError = validateUsername(formData.username);
    const passwordError = validatePassword(formData.password);
    const confirmPasswordError = validatePasswordConfirm(formData.password, confirmPassword);
    const emailError = validateEmail(formData.email);
    const nameError = validateName(formData.name);

    if (!isUsernameChecked || !isUsernameAvailable) {
      alert('아이디 중복확인을 해주세요.');
      return;
    }

    if (usernameError || passwordError || confirmPasswordError || emailError || nameError) {
      const errorMsg = [usernameError, passwordError, confirmPasswordError, emailError, nameError].filter(Boolean).join('\n');
      alert('필수 입력 정보를 확인해주세요.\n\n' + errorMsg);

      setErrors({
        username: usernameError,
        password: passwordError,
        confirmPassword: confirmPasswordError,
        email: emailError,
        name: nameError,
      });
      return;
    }

    if (!agreements.terms) {
      alert('필수 약관에 동의해주세요.');
      return;
    }

    try {
      const payload = {
        username: formData.username,
        password: formData.password,
        password_check: confirmPassword,
        name: formData.name,
        email: formData.email,
        phone_number: null,
<<<<<<< HEAD
        user_type: 'GENERAL',
=======
        user_type: "GENERAL", // C형 사용자
>>>>>>> 438f06fc602c619edbd98d1b7f7ce94b95068863
        simple_password: null,
        welfare_card: null
      };

      const apiResponse = await authAPI.register(payload);
      if (apiResponse.success) {
        setIsModalOpen(true);
      } else {
        alert(apiResponse.message || '회원가입에 실패했습니다.');
      }
    } catch (error) {
      console.error('Signup error:', error);
      alert(error.message || '회원가입 중 오류가 발생했습니다.');
    }
  };

  return (
    <div className="signup-c-container">
      <main className="signup-c-main">
        <div className="signup-card-c">
<<<<<<< HEAD
          <div className="signup-header-c">
            <img
              src={logoC}
              alt="HearBe Logo"
              className="signup-logo-c"
              style={{ marginBottom: '20px', cursor: 'pointer' }}
              onClick={() => window.location.assign('/')}
            />
=======
          <div className="signup-header-c"> {/* 로고 이미지 사용 */}
            <img src={logoC} alt="HearBe Logo" className="signup-logo-c" style={{ marginBottom: '20px' }} />
>>>>>>> 438f06fc602c619edbd98d1b7f7ce94b95068863
            <div className="header-title-group-c" style={{ display: 'none' }}>
              <div className="title-icon-c">
                <UserPlus size={32} />
              </div>
              <h1>회원가입</h1>
            </div>
            <p className="signup-subtitle-c" style={{ display: 'none' }}>
              HearBe 서비스 이용을 위한 회원가입을 진행합니다.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="signup-form-c">
            <div className="input-section-c">
              <div className={`input-c-group ${errors.username ? 'error' : ''}`}>
                <div className="input-with-button-c">
                  <input
                    type="text"
                    value={formData.username}
                    onChange={(e) => handleChange('username', e.target.value)}
                    placeholder="아이디"
                    className="signup-input-c"
                  />
                  <button
                    type="button"
                    onClick={handleCheckUsername}
                    className={`check-duplicate-btn-c ${isUsernameChecked && isUsernameAvailable ? 'checked' : ''}`}
                  >
                    {isUsernameChecked && isUsernameAvailable ? '확인완료' : '중복확인'}
                  </button>
                </div>
                {errors.username && <span className="error-text-c">{errors.username}</span>}
                {isUsernameChecked && !isUsernameAvailable && (
                  <span className="error-text-c">이미 사용 중인 아이디입니다.</span>
                )}
              </div>

              <div className={`input-c-group ${errors.password ? 'error' : ''}`}>
                <div className="password-wrapper-c">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={(e) => handleChange('password', e.target.value)}
                    placeholder="비밀번호(숫자 6자리)"
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
                  placeholder="비밀번호 확인"
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
                  placeholder="이메일(example@gmail.com)"
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
              회원가입하기
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
              <div className="modal-icon-c">✔</div>
              <h2 className="modal-title-c">가입완료!</h2>
              <p className="modal-desc-c">
                HearBe 회원이 되신 것을 축하드립니다.
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
