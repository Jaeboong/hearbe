import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion as _motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, User, Lock, Eye, EyeOff, Mail, Calendar, Phone, CheckCircle2, PartyPopper } from 'lucide-react';
import { validateUsername, validatePassword, validatePasswordConfirm, validateEmail, validateName } from '../../utils/validation';
import { authAPI } from '../../services/authAPI';
import Swal from 'sweetalert2';
import logoC from '../../assets/logoC.png'; // C형 로고로 변경
import './SignUpC.css';

export default function SignUpC() {
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

  const [matchMessage, setMatchMessage] = useState('');
  const [matchValid, setMatchValid] = useState(false);

  const handlePasswordCheck = () => {
    if (!confirmPassword) {
      setMatchMessage('');
      setMatchValid(false);
      return;
    }

    if (formData.password === confirmPassword) {
      setMatchMessage('비밀번호가 일치합니다.');
      setMatchValid(true);
    } else {
      setMatchMessage('비밀번호가 일치하지 않습니다.');
      setMatchValid(false);
    }
  };

  const handleConfirmPasswordChange = (value) => {
    setConfirmPassword(value);
    if (errors.confirmPassword) {
      setErrors({ ...errors, confirmPassword: null });
    }
    // 입력 중에도 메시지 초기화 혹은 실시간 체크를 원한다면 여기서 호출 가능
    // 하지만 LoginC와 동일하게 onBlur/onMouseLeave에서만 메시지 뜨게 하려면 여기서는 메시지 초기화만
    if (matchMessage) {
      setMatchMessage('');
    }
  };

  const handleCheckUsername = async () => {
    // 1. 길이 검사 (4자 이상)
    if (!formData.username || formData.username.length < 4) {
      Swal.fire({
        icon: 'warning',
        text: '아이디는 4자 이상 입력해주세요.',
        confirmButtonColor: '#7c3aed',
        confirmButtonText: '확인'
      });
      return;
    }

    // 2. 영문 + 숫자 포함 검사
    const hasLetter = /[a-zA-Z]/.test(formData.username);
    const hasNumber = /[0-9]/.test(formData.username);

    if (!hasLetter || !hasNumber) {
      Swal.fire({
        icon: 'warning',
        text: '아이디는 영문과 숫자를 모두 포함해야 합니다.',
        confirmButtonColor: '#7c3aed',
        confirmButtonText: '확인'
      });
      return;
    }

    // 기존 usernameError check는 위 로직으로 대체되었으므로 제거하거나 기본적인 것만 유지할 수 있지만,
    // 여기서는 사용자가 요청한 규칙이 우선이므로 위 로직 통과 후 다른 검증(예: 공백 등)은 validateUsername에 맡기되
    // 위 에러들과 중복되지 않게 처리하거나 바로 중복확인으로 넘어감.
    // 하지만 validateUsername에는 길이 체크등이 있어서 그냥 여기 로직만 통과하면 중복체크로 넘어가도 무방하지만
    // validateUsername이 '아이디를 입력해주세요' 등을 리턴하므로 안전하게 호출하되, 위 조건들에 걸리지 않는 에러만 처리.

    // 단순화: 위 조건 통과하면 바로 API 호출 시도 (validateUsername은 submit시에 한번 더 체크됨)


    try {
      const apiResponse = await authAPI.checkDuplicate(formData.username);
      const isDuplicate = apiResponse.data;

      if (!isDuplicate) {
        setIsUsernameChecked(true);
        setIsUsernameAvailable(true);
        Swal.fire({
          icon: 'success',
          text: '사용 가능한 아이디입니다.',
          confirmButtonColor: '#7c3aed',
          confirmButtonText: '확인'
        });
      } else {
        setIsUsernameChecked(true);
        setIsUsernameAvailable(false);
        Swal.fire({
          icon: 'error',
          text: '이미 사용 중인 아이디입니다.',
          confirmButtonColor: '#7c3aed',
          confirmButtonText: '확인'
        });
      }
    } catch (error) {
      console.error('Username check error:', error);
      Swal.fire({
        icon: 'error',
        text: '아이디 중복 확인에 실패했습니다.',
        confirmButtonColor: '#7c3aed',
        confirmButtonText: '확인'
      });
      setIsUsernameChecked(false); // 에러 발생 시 중복확인 상태 초기화
    }
  };


  // handleAgreementChange는 더이상 필요하지 않고 setter 직접 사용
  // 하지만 호환성을 위해 남겨두거나 삭제하고 JSX에서 setAgreements 직접 호출


  const handleEmailBlur = () => {
    if (!formData.email) return; // 빈 값일 때는 에러 표시 안 함 (선택 사항)

    if (!formData.email.includes('@')) {
      setErrors((prev) => ({ ...prev, email: '@포함한 유효한 이메일을 입력해주세요' }));
      return;
    }

    // 간단한 도메인 체크를 포함한 정규식 (최소한 . 뒤에 2글자 이상)
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
    if (!emailRegex.test(formData.email)) {
      setErrors((prev) => ({ ...prev, email: '유효한 이메일을 입력해주세요' }));
      return;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const usernameError = validateUsername(formData.username);
    const passwordError = validatePassword(formData.password);
    const confirmPasswordError = validatePasswordConfirm(formData.password, confirmPassword);
    // emailError는 아래에서 별도로 처리하거나 validateEmail 결과 사용
    const nameError = validateName(formData.name);

    // 이메일 정밀 검사
    if (!formData.email.includes('@')) {
      Swal.fire({
        icon: 'warning',
        text: '@를 포함하여 이메일을 작성해주세요.',
        confirmButtonColor: '#7c3aed',
        confirmButtonText: '확인'
      });
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      Swal.fire({
        icon: 'warning',
        text: '올바른 이메일 주소를 입력해주세요.', // 도메인 포함 여부 등 포괄적 메시지
        confirmButtonColor: '#7c3aed',
        confirmButtonText: '확인'
      });
      return;
    }

    // validateEmail 결과도 확인 (혹시 모를 다른 케이스)
    const emailError = validateEmail(formData.email);


    if (!isUsernameChecked || !isUsernameAvailable) {
      Swal.fire({
        icon: 'warning',
        text: '아이디 중복확인을 해주세요.',
        confirmButtonColor: '#7c3aed',
        confirmButtonText: '확인'
      });
      return;
    }

    if (usernameError || passwordError || confirmPasswordError || emailError || nameError) {
      const errorMsg = [usernameError, passwordError, confirmPasswordError, emailError, nameError].filter(Boolean).join('\n');

      Swal.fire({
        icon: 'warning',
        title: '입력 정보 확인',
        html: errorMsg.replace(/\n/g, '<br/>'), // 줄바꿈 처리를 위해 html 사용
        confirmButtonColor: '#7c3aed',
        confirmButtonText: '확인'
      });

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
      Swal.fire({
        icon: 'warning',
        text: '필수 이용약관 및 개인정보 수집에 동의해주세요.',
        confirmButtonColor: '#7c3aed',
        confirmButtonText: '확인'
      });
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
        Swal.fire({
          icon: 'error',
          text: apiResponse.message || '회원가입에 실패했습니다.',
          confirmButtonColor: '#7c3aed',
          confirmButtonText: '확인'
        });
      }
    } catch (error) {
      console.error('Signup error:', error);
      Swal.fire({
        icon: 'error',
        text: error.message || '회원가입 중 오류가 발생했습니다.',
        confirmButtonColor: '#7c3aed',
        confirmButtonText: '확인'
      });
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
            <img
              src={logoC}
              alt="HearBe Logo"
              className="signup-logo-c"
              style={{ marginBottom: '20px', cursor: 'pointer' }}
              onClick={() => navigate('/main')}
            />
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
                    onMouseLeave={handlePasswordCheck}
                    onBlur={handlePasswordCheck}
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
                {matchMessage && (
                  <div style={{ textAlign: 'left', marginTop: '8px', paddingLeft: '5px' }}>
                    <p
                      className={`pw-condition-text ${matchValid ? 'satisfied' : 'unsatisfied'}`}
                      style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '6px' }}
                    >
                      <span style={{ fontSize: matchValid ? '14px' : '8px', lineHeight: '1' }}>
                        {matchValid ? '✓' : '●'}
                      </span>
                      {matchMessage}
                    </p>
                  </div>
                )}
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
                  onBlur={handleEmailBlur}
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
            <_motion.div
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
            </_motion.div>
          </div>
        )}

        {termModalState.isOpen && (
          <div className="modal-overlay-c" onClick={() => closeTermModal(false)}>
            <_motion.div
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
            </_motion.div>
          </div>
        )}
      </AnimatePresence>

      <footer className="landing-footer">
        <p>© 2026 HearBe. All rights reserved.</p>
      </footer>
    </div>
  );
}

