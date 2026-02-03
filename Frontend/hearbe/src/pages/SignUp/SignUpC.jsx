import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, User, Lock, Eye, EyeOff, Mail, Calendar, Phone, CheckCircle2 } from 'lucide-react';
import { validateUsername, validatePassword, validatePasswordConfirm, validateEmail, validateName } from '../../utils/validation';
import { authAPI } from '../../services/authAPI';
import logoC from '../../assets/logoC.png'; // C형 로고로 변경
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
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [agreements, setAgreements] = useState(false); // 단일 약관 동의 상태 (Boolean)
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isUsernameChecked, setIsUsernameChecked] = useState(false);
  const [isUsernameAvailable, setIsUsernameAvailable] = useState(false);

  // 약관 모달 상태
  const [termModalState, setTermModalState] = useState({
    isOpen: false,
    title: '',
    content: ''
  });

  const termContents = {
    terms: `환영합니다!
HearBe는 누구나 평등하게 쇼핑을 즐길 수 있도록 돕는 프로젝트입니다.

1. 함께 만드는 공간
HearBe는 여러분의 피드백으로 성장합니다. 서비스를 자유롭게 이용해보시고, 불편한 점이나 좋은 아이디어가 있다면 언제든 들려주세요.

2. 즐겁게 이용해주세요
이곳은 쇼핑의 장벽을 허물기 위해 노력하는 공간입니다. 서로 배려하는 마음으로 서비스를 이용해주시면 감사하겠습니다.`,
    privacy: `여러분의 소중한 정보는 오직 '나만을 위한 쇼핑 도우미' 역할을 위해서만 사용됩니다.

1. 수집하는 약속
회원가입 시 입력하신 아이디, 이름, 이메일은 여러분이 누구인지 기억하고, 맞춤형 인사를 건네기 위해서만 활용됩니다.

2. 안전한 보관
여러분의 정보는 HearBe 프로젝트 내부에서만 안전하게 관리되며, 외부로 절대 공유되지 않습니다.`
  };

  const openTermModal = () => {
    const title = '이용약관 및 개인정보 수집 동의';
    const content = `${termContents.terms}

---------------------------------------------

< 개인정보 수집 및 이용 안내 >

${termContents.privacy}`;

    setTermModalState({ isOpen: true, title, content });
  };

  const closeTermModal = (agree = false) => {
    setTermModalState({ ...termModalState, isOpen: false });
    if (agree) {
      setAgreements(true);
    }
  };

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
      const isDuplicate = apiResponse.data;

      if (!isDuplicate) {
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
      setIsUsernameChecked(false); // 에러 발생 시 중복확인 상태 초기화
    }
  };


  // handleAgreementChange는 더이상 필요하지 않고 setter 직접 사용
  // 하지만 호환성을 위해 남겨두거나 삭제하고 JSX에서 setAgreements 직접 호출


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

    if (!agreements) {
      alert('필수 이용약관 및 개인정보 수집에 동의해주세요.');
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
        user_type: "GENERAL", // C형 사용자
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

  // 실시간 유효성 검사 (버튼 활성화용)
  const isFormValid =
    isUsernameChecked &&
    isUsernameAvailable &&
    !validatePassword(formData.password) &&
    !validatePasswordConfirm(formData.password, confirmPassword) &&
    !validateName(formData.name) &&
    !validateEmail(formData.email) &&
    agreements;

  return (
    <div className="signup-c-container">
      <main className="signup-c-main">
        <div className="signup-card-c">
          <div className="signup-header-c"> {/* 로고 이미지 사용 */}
            <img src={logoC} alt="HearBe Logo" className="signup-logo-c" style={{ marginBottom: '20px' }} />
            <div className="header-title-group-c" style={{ display: 'none' }}>
              <div className="title-icon-c">
                <User size={32} />
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
                    placeholder="비밀번호 (8~20자, 영문+숫자)"
                    className={`signup-input-c gray-bg-c ${errors.password ? 'input-error' : ''}`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="pw-toggle-c"
                  >
                    {showPassword ? <EyeOff size={32} color="#94A3B8" /> : <Eye size={32} color="#94A3B8" />}
                  </button>
                </div>

                {/* 비밀번호 실시간 유효성 검사 표시 */}
                {formData.password.length > 0 && (
                  <div className="password-conditions-text-group">
                    {formData.password.length >= 8 && formData.password.length <= 20 && /[a-zA-Z]/.test(formData.password) && /[0-9]/.test(formData.password) ? (
                      <p className="pw-condition-text satisfied">✓ 사용 가능한 비밀번호입니다</p>
                    ) : (
                      <>
                        {!(formData.password.length >= 8 && formData.password.length <= 20) && (
                          <p className="pw-condition-text unsatisfied">• 8~20자 이내여야 합니다</p>
                        )}
                        {!/[a-zA-Z]/.test(formData.password) && (
                          <p className="pw-condition-text unsatisfied">• 영문이 포함되어야 합니다</p>
                        )}
                        {!/[0-9]/.test(formData.password) && (
                          <p className="pw-condition-text unsatisfied">• 숫자가 포함되어야 합니다</p>
                        )}
                      </>
                    )}
                  </div>
                )}

                {errors.password && <span className="error-text-c">{errors.password}</span>}
              </div>

              <div className={`input-c-group confirm-pw-group ${errors.confirmPassword ? 'error' : ''}`}>
                <div className="password-wrapper-c">
                  <input
                    type={showConfirmPassword ? "text" : "password"}
                    value={confirmPassword}
                    onChange={(e) => handleConfirmPasswordChange(e.target.value)}
                    placeholder="비밀번호 재확인"
                    className="signup-input-c gray-bg-c"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="pw-toggle-c"
                  >
                    {showConfirmPassword ? <EyeOff size={32} color="#94A3B8" /> : <Eye size={32} color="#94A3B8" />}
                  </button>
                </div>
                {errors.confirmPassword && <span className="error-text-c">{errors.confirmPassword}</span>}
              </div >
            </div >

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
              <div className="terms-item-c" style={{ justifyContent: 'space-between' }}>
                <div className="checkbox-row">
                  <input
                    type="checkbox"
                    id="all"
                    checked={agreements}
                    onChange={(e) => setAgreements(e.target.checked)}
                  />
                  <label htmlFor="all" style={{ fontWeight: 'bold' }}>[필수] 이용약관 및 개인정보 수집 동의</label>
                </div>
                <button type="button" className="terms-view-btn-c" onClick={() => openTermModal('terms')}>보기 &gt;</button>
              </div>
            </div>

            <button
              type="submit"
              className={`signup-submit-btn-c ${isFormValid ? '' : 'disabled'}`}
              disabled={!isFormValid}
            >
              회원 가입
            </button>
          </form >
        </div >
      </main >

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
              <button onClick={() => { setIsModalOpen(false); navigate('/C/login'); }} className="modal-btn-c">
                확인
              </button>
            </motion.div>
          </div>
        )}

        {termModalState.isOpen && (
          <div className="modal-overlay-c" onClick={() => closeTermModal(false)}>
            <motion.div
              initial={{ y: 50, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: 50, opacity: 0 }}
              className="modal-content-c term-modal-c"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="term-modal-header">
                <h3 className="term-title">{termModalState.title}</h3>
                <button onClick={() => closeTermModal(false)} className="close-btn-c">✕</button>
              </div>
              <div className="term-scroll-box">
                <p className="term-text whitespace-pre-line">{termModalState.content}</p>
              </div>
              <button onClick={() => closeTermModal(true)} className="modal-btn-c term-confirm-btn">
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

