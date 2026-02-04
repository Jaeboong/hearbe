import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PartyPopper } from 'lucide-react';
import iconCard from '../../assets/icon-card.png';
import iconCamera from '../../assets/icon-camera.png';
import logo from '../../assets/logoA.png';
import { authAPI } from '../../services/authAPI';
import './SignUpA.css';

// Utility Functions
const formatPhoneNumber = (value) => {
    // 숨자만 추출
    const numbers = value.replace(/[^\d]/g, '');

    // 11자리로 제한
    const limited = numbers.slice(0, 11);

    // 010-1234-5678 형식으로 변환
    if (limited.length <= 3) return limited;
    if (limited.length <= 7) return `${limited.slice(0, 3)}-${limited.slice(3)}`;
    return `${limited.slice(0, 3)}-${limited.slice(3, 7)}-${limited.slice(7)}`;
};

const validateUserId = (userId) => {
    // 영문자와 숫자 포함 필수, 4글자 이상 (서버 요구사항)
    if (userId.length < 4) return false;
    const hasLetter = /[a-zA-Z]/.test(userId);
    const hasNumber = /[0-9]/.test(userId);
    return hasLetter && hasNumber;
};

const SignUp = () => {
    const navigate = useNavigate();

    // Form State
    const [formData, setFormData] = useState({
        id: '',
        password: '',
        name: '',
        phone: ''
    });

    // Validation State
    const [isIdChecked, setIsIdChecked] = useState(false);

    // Terms State
    const [terms, setTerms] = useState({
        all: false,
        term1: false, // Essential 1
        term2: false, // Essential 2
    });

    // Modal States
    const [showCamera, setShowCamera] = useState(false);
    const [showError, setShowError] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [showSuccess, setShowSuccess] = useState(false);

    // Card Recognition State
    const [modalStep, setModalStep] = useState('camera'); // 'camera' or 'form'
    const [cardData, setCardData] = useState(null); // { company, number, expiry, cvc }
    const [cardForm, setCardForm] = useState({
        company: '',
        number: '',
        expiry: '',
        cvc: ''
    });

    // Camera Logic
    const videoRef = useRef(null);
    const [stream, setStream] = useState(null);

    const maskCardNumber = (value) => {
        if (!value) return '';
        const digits = value.replace(/[^0-9]/g, '');
        if (digits.length <= 4) return digits;
        return `${'*'.repeat(digits.length - 4)}${digits.slice(-4)}`;
    };

    const maskCvc = (value) => {
        if (!value) return '';
        return '*'.repeat(value.length);
    };

    const startCamera = async () => {
        try {
            const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
            setStream(mediaStream);
            if (videoRef.current) {
                videoRef.current.srcObject = mediaStream;
            }
        } catch (err) {
            console.error("Error accessing camera:", err);
        }
    };

    const stopCamera = () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            setStream(null);
        }
    };

    // 카메라 모달이 켜지고, 단계가 'camera'일 때만 카메라 실행
    useEffect(() => {
        if (showCamera && modalStep === 'camera') {
            startCamera();
        } else {
            stopCamera();
        }
        return () => {
            stopCamera();
        };
    }, [showCamera, modalStep]);

    // 스트림이 준비되면 비디오 태그에 연결
    useEffect(() => {
        if (stream && videoRef.current) {
            console.log("📹 스트림 연결 시도 중...");
            videoRef.current.muted = true;
            videoRef.current.srcObject = stream;
            videoRef.current.play()
                .then(() => console.log("video play success"))
                .catch(e => console.error("video play fail:", e));
        }
    }, [stream, modalStep]);

    // Input Handler
    const handleInputChange = (e) => {
        const { name, value } = e.target;

        // 전화번호 자동 포맷팅
        if (name === 'phone') {
            setFormData(prev => ({
                ...prev,
                [name]: formatPhoneNumber(value)
            }));
        } else {
            setFormData(prev => ({
                ...prev,
                [name]: value
            }));
        }

        if (name === 'id') {
            setIsIdChecked(false);
        }
    };

    // Duplicate Check Handler
    const handleDuplicateCheck = async () => {
        if (!formData.id) {
            setErrorMessage("아이디를 입력해주세요.");
            setShowError(true);
            return;
        }

        // 아이디 형식 검증 (영문+숫자 포함, 4글자 이상)
        if (!validateUserId(formData.id)) {
            setErrorMessage("아이디는 영문자와 숫자를 포함하여 4글자 이상이어야 합니다.");
            setShowError(true);
            return;
        }

        try {
            const result = await authAPI.checkDuplicate(formData.id);

            console.log("서버에서 온 진짜 값:", result);

            const isDuplicate = result.data; // 서버에서 중복 여부를 나타내는 필드명에 맞게 수정 필요

            if (isDuplicate === false) { // 중복이 아니라면 (사용 가능)
                setIsIdChecked(true);
                alert("사용 가능한 아이디입니다.");
            } else { // 중복이 맞다면 (true)
                setErrorMessage("이미 존재하는 아이디입니다.");
                setShowError(true);
                setIsIdChecked(false);
            }
        } catch (error) {
            // authAPI.checkDuplicate에서 던져진 에러를 여기서 처리
            // 에러 발생 시 아이디 중복 확인이 완료되지 않았으므로 isIdChecked는 false
            // 사용자에게는 실패 메시지를 보여줍니다.
            setErrorMessage(error.message || "아이디 중복 확인에 실패했습니다.");
            setShowError(true);
            setIsIdChecked(false); // 에러 발생 시 중복확인 상태 초기화
        }
    };

    // Terms Handlers
    const handleAllAgree = () => {
        const newState = !terms.all;
        setTerms({
            all: newState,
            term1: newState,
            term2: newState
        });
    };

    const handleTermToggle = (key) => {
        setTerms(prev => {
            const newTerms = { ...prev, [key]: !prev[key] };
            if (newTerms.term1 && newTerms.term2) {
                newTerms.all = true;
            } else {
                newTerms.all = false;
            }
            return newTerms;
        });
    };

    // --- Modal & Card Handlers ---

    // 1. 카메라 셔터 누름 -> 폼 확인 단계로 이동 (팝업 유지)
    const handleSnap = () => {
        setCardForm({
            company: '신한카드',
            number: '0000-0000-0000-0000',
            expiry: '01/21',
            cvc: '123'
        });
        setModalStep('form');
    };

    const formatCardNumber = (value) => {
        const digits = value.replace(/[^0-9]/g, '').slice(0, 16);
        if (digits.length <= 4) return digits;
        if (digits.length <= 8) return `${digits.slice(0, 4)}-${digits.slice(4)}`;
        if (digits.length <= 12) return `${digits.slice(0, 4)}-${digits.slice(4, 8)}-${digits.slice(8)}`;
        return `${digits.slice(0, 4)}-${digits.slice(4, 8)}-${digits.slice(8, 12)}-${digits.slice(12)}`;
    };

    const formatExpiry = (value) => {
        const digits = value.replace(/[^0-9]/g, '').slice(0, 4);
        if (digits.length <= 2) return digits;
        return `${digits.slice(0, 2)}/${digits.slice(2)}`;
    };

    const handleCardFormChange = (e) => {
        const { name, value } = e.target;
        if (name === 'number') {
            setCardForm((prev) => ({ ...prev, number: formatCardNumber(value) }));
            return;
        }
        if (name === 'expiry') {
            setCardForm((prev) => ({ ...prev, expiry: formatExpiry(value) }));
            return;
        }
        if (name === 'cvc') {
            const digits = value.replace(/[^0-9]/g, '').slice(0, 3);
            setCardForm((prev) => ({ ...prev, cvc: digits }));
            return;
        }
        setCardForm((prev) => ({ ...prev, [name]: value }));
    };

    // 2. 최종 카드 등록 -> 데이터 저장 후 팝업 닫기
    const handleCardRegister = () => {
        // 현재 날짜를 issue_date로, expiry를 백엔드 형식으로 변환
        const today = new Date();
        const issueDate = today.toISOString().split('T')[0]; // YYYY-MM-DD

        setCardData({
            company: cardForm.company,
            number: cardForm.number,
            issueDate: issueDate,
            expiry: cardForm.expiry,
            cvc: cardForm.cvc
        });
        setShowCamera(false);
        setModalStep('camera'); // 다음 번을 위해 초기화
    };

    const handleRetakeCard = () => {
        setCardData(null);
        setModalStep('camera');
        setShowCamera(true);
    };

    // 3. 모달 닫기
    const handleModalClose = () => {
        setShowCamera(false);
        setModalStep('camera');
    };

    // Sign Up Validation and API Handler
    const handleSignUp = async () => {
        // 1. 아이디 검증
        if (!formData.id) {
            setErrorMessage("아이디를 입력해주세요.");
            setShowError(true);
            return;
        }
        if (!validateUserId(formData.id)) {
            setErrorMessage("아이디는 영문자와 숫자를 포함하여 4글자 이상이어야 합니다.");
            setShowError(true);
            return;
        }
        if (!isIdChecked) {
            setErrorMessage("아이디 중복확인을 해주세요.");
            setShowError(true);
            return;
        }

        // 2. 비밀번호 검증 (숫자 6자리)
        if (!formData.password) {
            setErrorMessage("비밀번호를 입력해주세요.");
            setShowError(true);
            return;
        }
        const passwordRegex = /^\d{6}$/;
        if (!passwordRegex.test(formData.password)) {
            setErrorMessage("비밀번호는 숫자 6자리여야 합니다.");
            setShowError(true);
            return;
        }

        // 3. 이름 검증
        if (!formData.name) {
            setErrorMessage("이름을 입력해주세요.");
            setShowError(true);
            return;
        }

        // 4. 휴대전화번호 검증 (11자리)
        const phoneNumbers = formData.phone.replace(/[^0-9]/g, '');
        console.log("Debug Phone:", formData.phone);
        console.log("Debug Stripped:", phoneNumbers);
        console.log("Debug Length:", phoneNumbers.length);

        if (phoneNumbers.length !== 11) {
            setErrorMessage("휴대전화번호는 11자리 숫자여야 합니다.");
            setShowError(true);
            return;
        }

        // 5. 장애인 복지카드 등록 확인 (필수)
        if (!cardData) {
            setErrorMessage("장애인 복지카드를 등록해주세요.");
            setShowError(true);
            return;
        }

        // 6. 약관 동의 확인
        if (!terms.term1 || !terms.term2) {
            setErrorMessage("필수 약관에 동의해주세요.");
            setShowError(true);
            return;
        }

        // 7. API 호출
        try {
            const userData = {
                username: formData.id,
                name: formData.name,
                email: `${formData.id}@hearbe.com`, // 임시 이메일 생성
                phone_number: formData.phone,
                user_type: "BLIND",
                simple_password: formData.password, // 6자리 비밀번호
                welfare_card: {
                    card_company: cardData.company,
                    card_number: cardData.number,
                    issue_date: cardData.issueDate,
                    expiration_date: cardData.expiry,
                    cvc: cardData.cvc
                }
            };

            console.log('전송할 데이터:', JSON.stringify(userData, null, 2));

            const response = await authAPI.register(userData);

            if (response.success) {
                if (cardData?.number) {
                    localStorage.setItem('member_card_number', cardData.number);
                }
                if (formData.id) {
                    localStorage.setItem('member_username', formData.id);
                }
                setShowSuccess(true);
            } else {
                throw new Error(response.message || '회원가입에 실패했습니다.');
            }
        } catch (error) {
            console.error('SignUp Error:', error);
            if (error.message.includes('중복') || error.message.includes('존재')) {
                setErrorMessage("이미 존재하는 아이디입니다.");
            } else if (error.message === 'Failed to fetch') {
                setErrorMessage("서버 연결에 실패했습니다. 잠시 후 다시 시도해주세요.");
            } else {
                setErrorMessage(error.message || "회원가입에 실패했습니다.");
            }
            setShowError(true);
        }
    };

    return (
        <div className="signup-container">
            <div className="signup-box">
                {/* Logo Section */}
                <div className="signup-logo-area">
                    <img
                        src={logo}
                        alt="Logo"
                        className="signup-logo-image"
                        onClick={() => navigate('/main')}
                        style={{ cursor: 'pointer' }}
                    />
                </div>

                {/* ID Section */}
                <div className="form-group-outline">
                    <div className="input-row border-bottom">
                        <input
                            type="text"
                            name="id"
                            placeholder="아이디"
                            className="signup-input input-id"
                            value={formData.id}
                            onChange={handleInputChange}
                        />
                        <button className="check-btn" onClick={handleDuplicateCheck}>중복확인</button>
                    </div>
                    <div className="input-row">
                        <input
                            type="password"
                            name="password"
                            placeholder="비밀번호(숫자 6자리)"
                            className="signup-input input-password"
                            value={formData.password}
                            onChange={handleInputChange}
                            maxLength={6}
                        />
                    </div>
                </div>

                {/* Name/Phone Section */}
                <div className="form-group-outline">
                    <div className="input-row border-bottom">
                        <input
                            type="text"
                            name="name"
                            placeholder="이름"
                            className="signup-input input-name"
                            value={formData.name}
                            onChange={handleInputChange}
                        />
                    </div>
                    <div className="input-row">
                        <input
                            type="tel"
                            name="phone"
                            placeholder="휴대전화번호"
                            className="signup-input input-phone"
                            value={formData.phone}
                            onChange={handleInputChange}
                            maxLength={13}
                        />
                    </div>
                </div>

                {/* Disability Card Section (메인 화면) */}
                <div className="form-group-outline card-section">
                    <div className="input-row header-row">
                        <span className="label card-label">장애인 복지카드 등록</span>
                    </div>

                    {/* 카드가 등록되었으면 정보 표시, 아니면 카메라 아이콘 표시 */}
                    {cardData ? (
                        <>
                            <div className="card-info-display">
                                <div className="info-row">
                                    <span className="info-label-main">카드사</span>
                                    <span className="info-val-main">{cardData.company}</span>
                                </div>
                                <div className="info-row">
                                    <span className="info-label-main">복지카드 번호</span>
                                    <span className="info-val-main">{maskCardNumber(cardData.number)}</span>
                                </div>
                                <div className="info-row-flex">
                                    <div className="info-col">
                                        <span className="info-label-main">유효기간</span>
                                        <span className="info-val-main">{cardData.expiry}</span>
                                    </div>
                                    <div className="info-col">
                                        <span className="info-label-main">CVC</span>
                                        <span className="info-val-main">{maskCvc(cardData.cvc)}</span>
                                    </div>
                                </div>
                            </div>
                            <div className="card-retake-wrap">
                                <button type="button" className="card-retake-btn" onClick={handleRetakeCard}>
                                    다시 촬영하기
                                </button>
                            </div>
                        </>
                    ) : (
                        // 이 부분을 클릭하면 모달이 뜹니다!
                        <div className="camera-area" onClick={() => setShowCamera(true)} style={{ cursor: 'pointer' }}>
                            <div className="camera-text">장애인 복지카드 촬영하기</div>
                            <img src={iconCamera} alt="Camera" className="camera-icon-img" />
                        </div>
                    )}
                </div>

                {/* Terms Section */}
                <div className="form-group-outline terms-section">
                    <div className="term-row" onClick={handleAllAgree}>
                        <div className={`check-circle ${terms.all ? 'checked' : ''}`}>
                            {terms.all && '✓'}
                        </div>
                        <span className="term-text bold">전체 동의하기</span>
                    </div>
                    <div className="term-row" onClick={() => handleTermToggle('term1')}>
                        <div className={`check-circle ${terms.term1 ? 'checked' : ''}`}>
                            {terms.term1 && '✓'}
                        </div>
                        <span className="term-text">[필수] 이용약관 동의</span>
                    </div>
                    <div className="term-row" onClick={() => handleTermToggle('term2')}>
                        <div className={`check-circle ${terms.term2 ? 'checked' : ''}`}>
                            {terms.term2 && '✓'}
                        </div>
                        <span className="term-text">[필수] 개인정보 수집 및 이용 동의</span>
                    </div>
                </div>

                {/* Submit Button */}
                <button className="signup-submit-btn" onClick={handleSignUp}>회원가입하기</button>
            </div>


            {/* 📸 Camera/Card Modal (팝업 영역) */}
            {showCamera && (
                <div className="modal-overlay">
                    {/* 모달 박스 하나로 감싸서 디자인 유지! */}
                    <div className="modal-box" onClick={(e) => e.stopPropagation()}>

                        {/* 닫기 버튼 */}
                        <div className="modal-close-btn" onClick={handleModalClose}>
                            X
                        </div>

                        {modalStep === 'camera' ? (
                            // 1단계: 카메라 촬영 화면
                            <>
                                <div className="modal-title">카드 촬영</div>
                                <div className="modal-desc">장애인 복지카드를 촬영해주세요.</div>

                                <div className="modal-camera-area">
                                    {stream ? (
                                        <video ref={videoRef} autoPlay playsInline muted className="modal-video-stream"></video>
                                    ) : (
                                        <>
                                            <div className="modal-camera-text">카메라 연결 중...</div>
                                            <img src={iconCamera} alt="Camera" className="modal-camera-icon" />
                                        </>
                                    )}
                                </div>

                                {stream && (
                                    <div className="shutter-button" onClick={handleSnap}>
                                        <div className="shutter-inner"></div>
                                    </div>
                                )}
                            </>
                        ) : (
                            // 2단계: 카드 정보 확인 폼 (여기도 modal-box 안이라서 팝업처럼 보임)
                            <>

                                <div className="card-form-box" style={{ width: '100%', padding: '0', background: 'transparent', border: 'none', boxShadow: 'none' }}>
                                    <div className="card-form-header" style={{ justifyContent: 'center' }}>
                                        <img src={iconCard} alt="card" className="small-card-icon" />
                                        <span>장애인 복지카드 정보</span>
                                    </div>

                                    <div className="modal-desc" style={{ marginBottom: '10px' }}>인식된 정보를 확인해주세요.</div>


                                    <div className="form-field-group">
                                        <label>카드사</label>
                                        <input
                                            type="text"
                                            name="company"
                                            value={cardForm.company}
                                            onChange={handleCardFormChange}
                                            className="modal-input"
                                        />
                                    </div>

                                    <div className="form-field-group">
                                        <label>복지카드 번호</label>
                                        <input
                                            type="text"
                                            name="number"
                                            value={cardForm.number}
                                            onChange={handleCardFormChange}
                                            className="modal-input"
                                        />
                                    </div>

                                    <div className="form-row-group">
                                        <div className="form-field-group half">
                                            <label>유효기간</label>
                                            <input
                                                type="text"
                                                name="expiry"
                                                value={cardForm.expiry}
                                                onChange={handleCardFormChange}
                                                className="modal-input"
                                                placeholder="MM/YY"
                                            />
                                        </div>
                                        <div className="form-field-group half">
                                            <label>CVC</label>
                                            <input
                                                type="text"
                                                name="cvc"
                                                value={cardForm.cvc}
                                                onChange={handleCardFormChange}
                                                className="modal-input"
                                                placeholder="000"
                                            />
                                        </div>
                                    </div>


                                    <div className="card-button-group">
                                        <button className="card-retake-btn" onClick={() => setModalStep('camera')}>다시 촬영</button>
                                        <button className="card-register-btn" onClick={handleCardRegister}>카드 등록</button>
                                    </div>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            )
            }

            {/* Error Message Modal */}
            {
                showError && (
                    <div className="modal-overlay" onClick={() => setShowError(false)}>
                        <div className="error-modal-box" onClick={(e) => e.stopPropagation()}>
                            <div className="error-message">{errorMessage}</div>
                            <button className="error-confirm-btn" onClick={() => setShowError(false)}>확인</button>
                        </div>
                    </div>
                )
            }

            {/* Success Message Modal */}
            {
                showSuccess && (
                    <div className="modal-overlay" onClick={() => { }}>
                        <div className="error-modal-box" onClick={(e) => e.stopPropagation()} style={{ padding: '3rem', borderRadius: '1.5rem', textAlign: 'center' }}>
                            <div className="success-icon" style={{ display: 'flex', justifyContent: 'center', marginBottom: '1rem' }}>
                                <PartyPopper size={80} color="#FACC15" />
                            </div>
                            <div className="error-message" style={{ color: '#FACC15', fontSize: '2rem', fontWeight: '800', marginBottom: '1rem' }}>
                                가입완료!
                            </div>
                            <p style={{ color: '#cbd5e1', fontSize: '1.2rem', marginBottom: '2rem' }}>
                                HearBe 회원이 되신 것을 축하드립니다.
                            </p>
                            <button
                                className="error-confirm-btn"
                                onClick={() => navigate('/A/login')}
                                style={{
                                    backgroundColor: '#FACC15',
                                    color: '#1e293b',
                                    padding: '1rem 2rem',
                                    fontSize: '1.4rem',
                                    borderRadius: '1rem',
                                    border: 'none',
                                    fontWeight: '800',
                                    width: '100%'
                                }}
                            >
                                확인
                            </button>
                        </div>
                    </div>
                )
            }
        </div >
    );
};

export default SignUp;
