import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import logoA from '../../assets/logoA.png';
import iconCamera from '../../assets/icon-camera.png';
import { authAPI } from '../../services/authAPI';
import './FindIdA.css';

const FindIdA = () => {
    const navigate = useNavigate();
    const [showCamera, setShowCamera] = useState(false);
    const [modalStep, setModalStep] = useState('camera'); // camera | form
    const [resultModal, setResultModal] = useState(null); // success | fail | null
    const [cameraError, setCameraError] = useState('');
    const [foundId, setFoundId] = useState('');
    const [formError, setFormError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isOcrLoading, setIsOcrLoading] = useState(false);
    const [recognizedCardNumber, setRecognizedCardNumber] = useState('');
    const [welfareCard, setWelfareCard] = useState({
        card_company: '',
        card_number: '',
        expiration_date: '',
        cvc: ''
    });
    const videoRef = useRef(null);
    const [stream, setStream] = useState(null);

    const startCamera = async () => {
        try {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('이 브라우저에서 카메라를 사용할 수 없습니다.');
            }
            const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
            setStream(mediaStream);
            if (videoRef.current) {
                videoRef.current.srcObject = mediaStream;
            }
        } catch (err) {
            console.error('Error accessing camera:', err);
            setCameraError('카메라 접근이 차단되었습니다. 브라우저 권한을 확인해주세요.');
        }
    };

    const stopCamera = () => {
        if (stream) {
            stream.getTracks().forEach((track) => track.stop());
            setStream(null);
        }
    };

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

    useEffect(() => {
        if (stream && videoRef.current) {
            videoRef.current.muted = true;
            videoRef.current.srcObject = stream;
            videoRef.current.play().catch(() => {});
        }
    }, [stream]);

    const openCamera = () => {
        setCameraError('');
        setFormError('');
        setResultModal(null);
        setModalStep('camera');
        setShowCamera(true);
    };

    const handleSnap = () => {
        // 카드 인식 결과 임시 하드코딩
        setIsOcrLoading(true);
        setFormError('');
        setTimeout(() => {
            const recognized = {
                card_company: '신한카드',
                card_number: '1234-5678-9012-3456',
                expiration_date: '01/28',
                cvc: '123'
            };
            setRecognizedCardNumber(recognized.card_number.replace(/[^0-9]/g, ''));
            setWelfareCard(recognized);
            setIsOcrLoading(false);
            setShowCamera(false);
            setModalStep('camera');
            setResultModal(null);
            navigate('/A/changePassword');
        }, 1200);
    };

    const handleWelfareInputChange = (e) => {
        const { name, value } = e.target;
        if (name === 'card_number') {
            const digits = value.replace(/[^0-9]/g, '').slice(0, 16);
            setWelfareCard((prev) => ({ ...prev, [name]: digits }));
            return;
        }
        if (name === 'expiration_date') {
            const digits = value.replace(/[^0-9]/g, '').slice(0, 4);
            const formatted = digits.length <= 2 ? digits : `${digits.slice(0, 2)}/${digits.slice(2)}`;
            setWelfareCard((prev) => ({ ...prev, [name]: formatted }));
            return;
        }
        if (name === 'cvc') {
            const digits = value.replace(/[^0-9]/g, '').slice(0, 3);
            setWelfareCard((prev) => ({ ...prev, [name]: digits }));
            return;
        }
        setWelfareCard((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmitFindId = async () => {
        const { card_company, card_number, expiration_date, cvc } = welfareCard;
        if (!card_company || !card_number || !expiration_date || !cvc) {
            setFormError('복지카드 정보를 모두 입력해주세요.');
            return;
        }
        const expPattern = /^(0[1-9]|1[0-2])\/\d{2}$/;
        if (!expPattern.test(expiration_date)) {
            setFormError('유효기간은 MM/YY 형식으로 입력해주세요.');
            return;
        }
        const cardPattern = /^\d{16}$/;
        if (!cardPattern.test(card_number)) {
            setFormError('카드번호는 숫자 16자리로 입력해주세요.');
            return;
        }
        const cvcPattern = /^\d{3}$/;
        if (!cvcPattern.test(cvc)) {
            setFormError('CVC는 3자리 숫자여야 합니다.');
            return;
        }
        const normalizedCardNumber = card_number.replace(/\s+/g, '');
        const normalizedCardDigits = normalizedCardNumber.replace(/[^0-9]/g, '');
        if (recognizedCardNumber && normalizedCardDigits !== recognizedCardNumber) {
            setFormError('인식된 카드 번호와 일치하지 않습니다.');
            return;
        }
        const normalizedCompany = card_company.trim();
        const normalizedCvc = cvc.replace(/\s+/g, '');

        setIsSubmitting(true);
        setFormError('');
        try {
            const response = await authAPI.findIdByWelfareCard({
                card_company: normalizedCompany,
                card_number: normalizedCardDigits,
                expiration_date,
                cvc: normalizedCvc
            });
            const username =
                response?.data?.username ||
                response?.data?.userId ||
                response?.data?.id ||
                response?.username ||
                response?.id ||
                'hs123';
            setFoundId(username);
            setShowCamera(false);
            setModalStep('camera');
            setResultModal(username ? 'success' : 'fail');
        } catch {
            setFoundId('');
            setShowCamera(false);
            setModalStep('camera');
            setResultModal('fail');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleRetry = () => {
        setResultModal(null);
        setModalStep('camera');
        setShowCamera(true);
    };

    return (
        <div className="findid-container">
            <img
                src={logoA}
                alt="Logo"
                className="findid-logo"
                onClick={() => navigate('/')}
            />

            <div className="findid-box">
                <h1 className="findid-title">아이디 찾기</h1>
                <p className="findid-desc">
                    장애인 복지 카드를 촬영하여
                    <br />
                    아이디를 찾을 수 있습니다.
                </p>

                <div className="findid-card" onClick={openCamera}>
                    <div className="findid-card-title">장애인 복지카드 촬영하기</div>
                    <img src={iconCamera} alt="Camera" className="findid-camera-icon" />
                </div>
            </div>

            {showCamera && (
                <div className="findid-modal-overlay" onClick={() => setShowCamera(false)}>
                    <div className="findid-modal-box" onClick={(e) => e.stopPropagation()}>
                        <div className="findid-modal-close" onClick={() => setShowCamera(false)}>
                            X
                        </div>
                        <div className="findid-modal-scroll">
                            {modalStep === 'camera' ? (
                                <>
                                    <div className="findid-modal-title">카드 촬영</div>
                                    <div className="findid-modal-desc">장애인 복지카드를 촬영해주세요.</div>

                                    <div className="findid-modal-camera-area">
                                        {isOcrLoading ? (
                                            <div className="findid-ocr-loading">
                                                <div className="findid-spinner"></div>
                                                <div className="findid-ocr-text">카드 인식 중 ...</div>
                                                <div className="findid-ocr-subtext">잠시만 기다려주세요</div>
                                            </div>
                                        ) : stream ? (
                                            <video ref={videoRef} autoPlay playsInline muted className="findid-modal-video"></video>
                                        ) : (
                                            <>
                                                <div className="findid-modal-camera-text">{cameraError || '카메라 연결 중...'}</div>
                                                <img src={iconCamera} alt="Camera" className="findid-modal-camera-icon" />
                                            </>
                                        )}
                                    </div>

                                    {stream && !isOcrLoading && (
                                        <div className="findid-shutter-button" onClick={handleSnap}>
                                            <div className="findid-shutter-inner"></div>
                                        </div>
                                    )}
                                </>
                            ) : (
                                <>
                                    <div className="findid-card-form-box">
                                        <div className="findid-card-form-header">
                                            <span>장애인 복지카드 정보</span>
                                        </div>

                                        <div className="findid-modal-desc">
                                            {formError ? formError : '인식된 정보를 확인해주세요.'}
                                        </div>

                                        <div className="findid-form-field">
                                            <label>카드사</label>
                                            <input
                                                type="text"
                                                name="card_company"
                                                value={welfareCard.card_company}
                                                onChange={handleWelfareInputChange}
                                                className="findid-modal-input"
                                            />
                                        </div>
                                        <div className="findid-form-field">
                                            <label>복지카드 번호</label>
                                            <input
                                                type="text"
                                                name="card_number"
                                                value={welfareCard.card_number}
                                                onChange={handleWelfareInputChange}
                                                className="findid-modal-input"
                                            />
                                        </div>
                                        <div className="findid-form-row">
                                            <div className="findid-form-field half">
                                                <label>유효기간</label>
                                                <input
                                                    type="text"
                                                    name="expiration_date"
                                                    value={welfareCard.expiration_date}
                                                    onChange={handleWelfareInputChange}
                                                    className="findid-modal-input"
                                                    placeholder="MM/YY"
                                                />
                                            </div>
                                            <div className="findid-form-field half">
                                                <label>CVC</label>
                                                <input
                                                    type="text"
                                                    name="cvc"
                                                    value={welfareCard.cvc}
                                                    onChange={handleWelfareInputChange}
                                                    className="findid-modal-input"
                                                    placeholder="000"
                                                />
                                            </div>
                                        </div>
                                        <div className="findid-card-btns">
                                            <button className="findid-retake-btn" onClick={() => setModalStep('camera')}>
                                                다시 촬영
                                            </button>
                                            <button
                                                className="findid-confirm-btn"
                                                onClick={handleSubmitFindId}
                                                disabled={isSubmitting}
                                            >
                                                {isSubmitting ? '조회 중...' : '확인'}
                                            </button>
                                        </div>
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {resultModal === 'success' && (
                <div className="findid-modal-overlay" onClick={() => setResultModal(null)}>
                    <div className="findid-result-box" onClick={(e) => e.stopPropagation()}>
                        <div className="findid-result-title">카드 정보가 확인되었습니다</div>
                        <div className="findid-result-desc">아이디 : {foundId}</div>
                        <button className="findid-result-btn" onClick={() => setResultModal(null)}>확인</button>
                    </div>
                </div>
            )}

            {resultModal === 'fail' && (
                <div className="findid-modal-overlay" onClick={() => setResultModal(null)}>
                    <div className="findid-result-box" onClick={(e) => e.stopPropagation()}>
                        <div className="findid-result-title">카드 정보가 없습니다</div>
                        <div className="findid-result-desc">다시 촬영하시겠습니까?</div>
                        <div className="findid-result-actions">
                            <button className="findid-retake-btn" onClick={handleRetry}>다시 촬영</button>
                            <button className="findid-result-btn" onClick={() => setResultModal(null)}>취소</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default FindIdA;
