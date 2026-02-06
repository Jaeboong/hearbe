import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    PartyPopper,
    User,
    Lock,
    Smartphone,
    Camera,
    CreditCard,
    CheckCircle2,
    ChevronRight,
    X,
    Eye,
    EyeOff
} from 'lucide-react';
import Swal from 'sweetalert2';
import logo from '../../assets/logoA.png';
import { authAPI } from '../../services/authAPI';
import { validateUsername } from '../../utils/validation';
import './SignUpA.css';

// Utility Functions
const formatPhoneNumber = (value) => {
    const numbers = value.replace(/[^\d]/g, '');
    const limited = numbers.slice(0, 11);
    if (limited.length <= 3) return limited;
    if (limited.length <= 7) return `${limited.slice(0, 3)}-${limited.slice(3)}`;
    return `${limited.slice(0, 3)}-${limited.slice(3, 7)}-
    ${limited.slice(7)}`;
};

const validatePassword = (password) => /^\d{6}$/.test(password);

const SignUp = () => {
    const navigate = useNavigate();

    // Form State
    const [formData, setFormData] = useState({
        id: '',
        password: '',
        name: '',
        phone: ''
    });

    const [showPassword, setShowPassword] = useState(false);
    const [isIdChecked, setIsIdChecked] = useState(false);
    const [isIdAvailable, setIsIdAvailable] = useState(false);

    // Terms State
    const [terms, setTerms] = useState({
        term1: false, // Essential 1
        term2: false, // Essential 2
    });

    // Card Recognition State
    const [showCamera, setShowCamera] = useState(false);
    const [modalStep, setModalStep] = useState('camera'); // 'camera' or 'form'
    const [cardData, setCardData] = useState(null);
    const [cardForm, setCardForm] = useState({
        company: '',
        number: '',
        expiry: '',
        cvc: ''
    });

    // Terms Modal State
    const [showTermsModal, setShowTermsModal] = useState(false);

    // Camera Logic
    const videoRef = useRef(null);
    const [stream, setStream] = useState(null);

    const startCamera = async () => {
        try {
            const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
            setStream(mediaStream);
            if (videoRef.current) {
                videoRef.current.srcObject = mediaStream;
            }
        } catch (err) {
            console.error("Error accessing camera:", err);
            Swal.fire({
                icon: 'error',
                text: '카메라에 접근할 수 없습니다. 권한을 확인해주세요.',
                confirmButtonText: '확인'
            });
        }
    };

    const stopCamera = () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            setStream(null);
        }
    };

    useEffect(() => {
        if (showCamera && modalStep === 'camera') {
            startCamera();
        } else {
            stopCamera();
        }
        return () => stopCamera();
    }, [showCamera, modalStep]);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        if (name === 'phone') {
            setFormData(prev => ({ ...prev, [name]: formatPhoneNumber(value) }));
        } else {
            setFormData(prev => ({ ...prev, [name]: value }));
        }

        if (name === 'id') {
            setIsIdChecked(false);
            setIsIdAvailable(false);
        }
    };

    const handleDuplicateCheck = async () => {
        const idError = validateUsername(formData.id);
        if (idError) {
            Swal.fire({
                icon: 'warning',
                text: idError,
                confirmButtonText: '확인'
            });
            return;
        }

        try {
            const result = await authAPI.checkDuplicate(formData.id);
            const isDuplicate = result.data;
            if (isDuplicate === false) {
                setIsIdChecked(true);
                setIsIdAvailable(true);
                Swal.fire({
                    icon: 'success',
                    text: '사용 가능한 아이디입니다.',
                    confirmButtonText: '확인'
                });
            } else {
                setIsIdAvailable(false);
                Swal.fire({
                    icon: 'error',
                    text: '이미 사용 중인 아이디입니다.',
                    confirmButtonText: '확인'
                });
                setIsIdChecked(true);
            }
        } catch (error) {
            Swal.fire({
                icon: 'error',
                text: error.message || "아이디 중복 확인에 실패했습니다.",
                confirmButtonText: '확인'
            });
        }
    };

    const handleSnap = () => {
        setCardForm({
            company: '신한카드',
            number: '0000-0000-0000-0000',
            expiry: '01/21',
            cvc: '123'
        });
        setModalStep('form');
    };

    const handleCardFormChange = (e) => {
        const { name, value } = e.target;
        setCardForm(prev => ({ ...prev, [name]: value }));
    };

    const handleCardRegister = () => {
        const today = new Date();
        const issueDate = today.toISOString().split('T')[0];
        setCardData({
            ...cardForm,
            issueDate
        });
        setShowCamera(false);
        setModalStep('camera');
        Swal.fire({
            icon: 'success',
            text: '복지카드가 등록되었습니다.',
            confirmButtonText: '확인'
        });
    };

    const handleSignUp = async () => {
        if (!isIdChecked || !isIdAvailable) {
            Swal.fire({
                icon: 'warning',
                text: '아이디 중복 확인이 필요합니다.',
                confirmButtonText: '확인'
            });
            return;
        }
        if (!validatePassword(formData.password)) {
            Swal.fire({
                icon: 'warning',
                text: '비밀번호는 숫자 6자리를 입력해주세요.',
                confirmButtonText: '확인'
            });
            return;
        }
        if (!formData.name) {
            Swal.fire({
                icon: 'warning',
                text: '이름을 입력해주세요.',
                confirmButtonText: '확인'
            });
            return;
        }
        if (!cardData) {
            Swal.fire({
                icon: 'warning',
                text: '장애인 복지카드를 등록해주세요.',
                confirmButtonText: '확인'
            });
            return;
        }
        if (!terms.term1 || !terms.term2) {
            Swal.fire({
                icon: 'warning',
                text: '필수 이용약관에 동의해주세요.',
                confirmButtonText: '확인'
            });
            return;
        }

        try {
            const userData = {
                username: formData.id,
                name: formData.name,
                email: `${formData.id}@hearbe.com`,
                phone_number: formData.phone,
                user_type: "BLIND",
                simple_password: formData.password,
                welfare_card: {
                    card_company: cardData.company,
                    card_number: cardData.number,
                    issue_date: cardData.issueDate,
                    expiration_date: cardData.expiry,
                    cvc: cardData.cvc
                }
            };

            const response = await authAPI.register(userData);
            if (response.success) {
                Swal.fire({
                    icon: 'success',
                    text: '가입 완료! HearBe 회원이 되신 것을 환영합니다.',
                    confirmButtonText: '확인'
                });
                navigate('/A/login');
            } else {
                throw new Error(response.message || '회원가입에 실패했습니다.');
            }
        } catch (error) {
            Swal.fire({
                icon: 'error',
                text: error.message || "회원가입 중 오류가 발생했습니다.",
                confirmButtonText: '확인'
            });
        }
    };

    return (
        <div className="signup-a-page-new">
            <main className="signup-a-content-new">
                <div className="signup-a-card-new">
                    <div className="signup-a-header-new">
                        <img
                            src={logo}
                            alt="Logo"
                            className="signup-logo-a-new cursor-pointer"
                            onClick={() => navigate('/main')}
                        />
                        <h1 className="signup-title-a-new">회원가입</h1>
                        <p className="signup-subtitle-a-new">나만을 위한 특별한 쇼핑 도우미, HearBe</p>
                    </div>

                    <div className="signup-a-form-new">
                        {/* ID Section */}
                        <div className="input-section-a-new">
                            <label className="input-label-a-new">아이디</label>
                            <div className="input-with-button-a-new">
                                <div className="input-icon-wrapper-a-new">
                                    <User size={32} />
                                    <input
                                        type="text"
                                        name="id"
                                        placeholder="영문, 숫자 포함 4자 이상"
                                        className="signup-input-a-new"
                                        value={formData.id}
                                        onChange={handleInputChange}
                                    />
                                </div>
                                <button
                                    className={`check-btn-a-new ${isIdChecked && isIdAvailable ? 'available' : ''}`}
                                    onClick={handleDuplicateCheck}
                                >
                                    {isIdChecked && isIdAvailable ? '확인됨' : '중복확인'}
                                </button>
                            </div>
                        </div>

                        {/* Password Section */}
                        <div className="input-section-a-new">
                            <label className="input-label-a-new">비밀번호 (숫자 6자리)</label>
                            <div className="input-icon-wrapper-a-new">
                                <Lock size={32} />
                                <input
                                    type={showPassword ? "text" : "password"}
                                    name="password"
                                    placeholder="간편 비밀번호 6자리"
                                    className="signup-input-a-new"
                                    value={formData.password}
                                    onChange={handleInputChange}
                                    maxLength={6}
                                />
                                <button
                                    type="button"
                                    className="pw-toggle-a-new"
                                    onClick={() => setShowPassword(!showPassword)}
                                >
                                    {showPassword ? <EyeOff size={44} /> : <Eye size={44} />}
                                </button>
                            </div>
                        </div>

                        {/* Name Section */}
                        <div className="input-section-a-new">
                            <label className="input-label-a-new">이름</label>
                            <div className="input-icon-wrapper-a-new">
                                <User size={32} />
                                <input
                                    type="text"
                                    name="name"
                                    placeholder="성함을 입력해주세요"
                                    className="signup-input-a-new"
                                    value={formData.name}
                                    onChange={handleInputChange}
                                />
                            </div>
                        </div>

                        {/* Phone Section */}
                        <div className="input-section-a-new">
                            <label className="input-label-a-new">휴대전화번호</label>
                            <div className="input-icon-wrapper-a-new">
                                <Smartphone size={32} />
                                <input
                                    type="tel"
                                    name="phone"
                                    placeholder="010-0000-0000"
                                    className="signup-input-a-new"
                                    value={formData.phone}
                                    onChange={handleInputChange}
                                    maxLength={13}
                                />
                            </div>
                        </div>

                        {/* Welfare Card Section */}
                        <div className="input-section-a-new">
                            <label className="input-label-a-new">장애인 복지카드 등록</label>
                            {cardData ? (
                                <div className="card-info-box-a-new" onClick={() => setShowCamera(true)}>
                                    <div className="card-icon-wrapper-a-new">
                                        <CreditCard size={48} color="#FFF064" />
                                    </div>
                                    <div className="card-details-a-new">
                                        <span className="card-company-a-new">{cardData.company}</span>
                                        <span className="card-number-a-new">{cardData.number.replace(/\d(?=\d{4})/g, "*")}</span>
                                    </div>
                                    <ChevronRight size={32} color="#FFF064" />
                                </div>
                            ) : (
                                <div className="camera-trigger-a-new" onClick={() => setShowCamera(true)}>
                                    <Camera size={64} />
                                    <span>복지카드 촬영하기</span>
                                </div>
                            )}
                        </div>

                        {/* Terms Section */}
                        <div className="terms-section-a-new">
                            <label className="terms-all-a-new">
                                <input
                                    type="checkbox"
                                    checked={terms.term1 && terms.term2}
                                    onChange={(e) => setTerms({ term1: e.target.checked, term2: e.target.checked })}
                                />
                                <span className="terms-checkmark-a-new">
                                    {(terms.term1 && terms.term2) && <CheckCircle2 size={44} />}
                                </span>
                                <span className="terms-label-text-a-new">[필수] 이용약관 및 개인정보 동의</span>
                            </label>
                            <button className="terms-view-btn-a-new" onClick={() => setShowTermsModal(true)}>보기</button>
                        </div>

                        <button className="signup-submit-btn-a-new" onClick={handleSignUp}>
                            회원가입
                        </button>
                    </div>
                </div>
            </main>

            {/* Camera Modal */}
            {showCamera && (
                <div className="signup-modal-overlay-a-new">
                    <div className="signup-modal-box-a-new">
                        <button className="modal-close-a-new" onClick={() => setShowCamera(false)}><X size={48} /></button>

                        {modalStep === 'camera' ? (
                            <div className="camera-modal-content-a-new">
                                <h2 className="modal-title-a-new">카드 촬영</h2>
                                <p className="modal-subtitle-a-new">복지카드 앞면이 가이드 안에 들어오게 해주세요.</p>
                                <div className="camera-view-a-new">
                                    <video ref={videoRef} autoPlay playsInline muted />
                                    <div className="camera-guide-a-new" />
                                </div>
                                <button className="shutter-btn-a-new" onClick={handleSnap}>
                                    <div className="shutter-inner-a-new" />
                                </button>
                            </div>
                        ) : (
                            <div className="form-modal-content-a-new">
                                <h2 className="modal-title-a-new">정보 확인</h2>
                                <p className="modal-subtitle-a-new">인식된 정보가 정확한지 확인해주세요.</p>
                                <div className="modal-form-a-new">
                                    <div className="modal-input-group-a-new">
                                        <label>카드사</label>
                                        <input type="text" name="company" value={cardForm.company} onChange={handleCardFormChange} />
                                    </div>
                                    <div className="modal-input-group-a-new">
                                        <label>카드번호</label>
                                        <input type="text" name="number" value={cardForm.number} onChange={handleCardFormChange} />
                                    </div>
                                    <div className="modal-input-row-a-new">
                                        <div className="modal-input-group-a-new half">
                                            <label>유효기간</label>
                                            <input type="text" name="expiry" value={cardForm.expiry} onChange={handleCardFormChange} placeholder="MM/YY" />
                                        </div>
                                        <div className="modal-input-group-a-new half">
                                            <label>CVC</label>
                                            <input type="text" name="cvc" value={cardForm.cvc} onChange={handleCardFormChange} maxLength={3} />
                                        </div>
                                    </div>
                                    <div className="modal-btn-group-a-new">
                                        <button className="modal-secondary-btn-a-new" onClick={() => setModalStep('camera')}>다시 촬영</button>
                                        <button className="modal-primary-btn-a-new" onClick={handleCardRegister}>등록하기</button>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Terms Modal */}
            {showTermsModal && (
                <div className="signup-modal-overlay-a-new" onClick={() => setShowTermsModal(false)}>
                    <div className="terms-modal-box-a-new" onClick={(e) => e.stopPropagation()}>
                        <h2 className="terms-modal-title-a-new">이용약관 및 개인정보 수집 동의</h2>
                        <div className="terms-modal-content-area-a-new">
                            <h3 style={{ fontSize: '32px', marginBottom: '15px' }}>환영합니다!</h3>
                            <p>
                                HearBe는 누구나 평등하게 쇼핑을 즐길 수 있도록 돕는 프로젝트입니다.<br /><br />
                                <strong>1. 함께 만드는 공간</strong><br />
                                HearBe는 여러분의 피드백으로 성장합니다. 서비스를 자유롭게 이용해보시고, 불편한 점이나 좋은 아이디어가 있다면 언제든 들려주세요.<br /><br />
                                <strong>2. 즐겁게 이용해주세요</strong><br />
                                이곳은 쇼핑의 장벽을 허물기 위해 노력하는 공간입니다. 서로 배려하는 마음으로 서비스를 이용해주시면 감사하겠습니다.
                            </p>
                            <div style={{ borderBottom: '2px solid #141C29', margin: '30px 0' }}></div>
                            <h3 style={{ fontSize: '32px', marginBottom: '15px' }}>&lt; 개인정보 수집 및 이용 안내 &gt;</h3>
                            <p>
                                여러분의 소중한 정보는 오직 '나만을 위한 쇼핑 도우미' 역할을 위해서만 사용됩니다.<br /><br />
                                <strong>1. 수집하는 약속</strong><br />
                                회원가입 시 입력하신 아이디, 이름, 이메일은 여러분이 누구인지 기억하고, 맞춤형 인사를 건네기 위해서만 활용됩니다.<br /><br />
                                <strong>2. 안전한 보관</strong><br />
                                여러분의 정보는 HearBe 프로젝트 내부에서만 안전하게 관리되며, 외부로 절대 공유되지 않습니다.
                            </p>
                        </div>
                        <button className="terms-modal-confirm-btn-a-new" onClick={() => {
                            setTerms({ term1: true, term2: true });
                            setShowTermsModal(false);
                        }}>
                            동의하고 확인했습니다
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SignUp;
