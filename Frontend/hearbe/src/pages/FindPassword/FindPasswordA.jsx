import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import logoA from '../../assets/logoA.png';
import iconCamera from '../../assets/icon-camera.png';
import './FindPasswordA.css';
import { authAPI } from '../../services/authAPI';

const FindPasswordA = () => {
    const navigate = useNavigate();
    const [showModal, setShowModal] = useState(false);
    const [modalStep, setModalStep] = useState('camera'); // camera | form
    const [cardForm, setCardForm] = useState({
        card_company: '',
        card_number: '',
        expiration_date: '',
        cvc: ''
    });
    const videoRef = useRef(null);
    const [stream, setStream] = useState(null);
    const [cameraError, setCameraError] = useState('');

    const handleOpen = () => {
        setCardForm({
            card_company: '신한카드',
            card_number: '1234-5678-9012-3456',
            expiration_date: '01/28',
            cvc: '123'
        });
        setModalStep('camera');
        setShowModal(true);
    };

    const handleClose = () => {
        setShowModal(false);
    };

    const handleSnap = () => {
        setModalStep('form');
    };

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
            setCameraError('');
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
        if (showModal && modalStep === 'camera') {
            startCamera();
        } else {
            stopCamera();
        }
        return () => {
            stopCamera();
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [showModal, modalStep]);

    useEffect(() => {
        if (stream && videoRef.current) {
            videoRef.current.muted = true;
            videoRef.current.srcObject = stream;
            videoRef.current.play().catch(() => {});
        }
    }, [stream]);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        if (name === 'card_number') {
            const digits = value.replace(/[^0-9]/g, '').slice(0, 16);
            const formatted =
                digits.length <= 4
                    ? digits
                    : digits.length <= 8
                        ? `${digits.slice(0, 4)}-${digits.slice(4)}`
                        : digits.length <= 12
                            ? `${digits.slice(0, 4)}-${digits.slice(4, 8)}-${digits.slice(8)}`
                            : `${digits.slice(0, 4)}-${digits.slice(4, 8)}-${digits.slice(8, 12)}-${digits.slice(12)}`;
            setCardForm((prev) => ({ ...prev, [name]: formatted }));
            return;
        }
        if (name === 'expiration_date') {
            const digits = value.replace(/[^0-9]/g, '').slice(0, 4);
            const formatted = digits.length <= 2 ? digits : `${digits.slice(0, 2)}/${digits.slice(2)}`;
            setCardForm((prev) => ({ ...prev, [name]: formatted }));
            return;
        }
        if (name === 'cvc') {
            const digits = value.replace(/[^0-9]/g, '').slice(0, 3);
            setCardForm((prev) => ({ ...prev, [name]: digits }));
            return;
        }
        setCardForm((prev) => ({ ...prev, [name]: value }));
    };

    const handleVerify = async () => {
        if (!cardForm.card_company || !cardForm.card_number || !cardForm.expiration_date || !cardForm.cvc) {
            alert('복지카드 정보를 모두 입력해주세요.');
            return;
        }
        try {
            const verifyResponse = await authAPI.verifyWelfareCard({
                card_company: cardForm.card_company.trim(),
                card_number: cardForm.card_number.trim(),
                expiration_date: cardForm.expiration_date.trim(),
                cvc: cardForm.cvc.trim()
            });
            const isVerified = verifyResponse?.code === 200;
            if (!isVerified) {
                alert('해당 정보가 없습니다.');
                return;
            }
            alert('인증이 되었습니다.');
            localStorage.setItem('welfare_verified', 'true');
            localStorage.setItem('welfare_card', JSON.stringify({
                card_company: cardForm.card_company.trim(),
                card_number: cardForm.card_number.trim(),
                expiration_date: cardForm.expiration_date.trim(),
                cvc: cardForm.cvc.trim()
            }));
            setShowModal(false);
            navigate('/A/changePassword');
        } catch (error) {
            alert(error.message || '해당 정보가 없습니다.');
        }
    };

    return (
        <div className="findpw-container">
            <img
                src={logoA}
                alt="Logo"
                className="findpw-logo"
                onClick={() => navigate('/')}
            />

            <div className="findpw-box">
                <h1 className="findpw-title">비밀번호 변경</h1>
                <p className="findpw-desc">
                    장애인 복지 카드를 촬영하여
                    <br />
                    비밀번호를 변경할 수 있습니다.
                </p>

                <div className="findpw-card" onClick={handleOpen}>
                    <div className="findpw-card-title">장애인 복지카드 촬영하기</div>
                    <img src={iconCamera} alt="Camera" className="findpw-camera-icon" />
                </div>
            </div>

            {showModal && (
                <div className="findpw-modal-overlay" onClick={handleClose}>
                    <div className="findpw-modal-box" onClick={(e) => e.stopPropagation()}>
                        <div className="findpw-modal-close" onClick={handleClose}>X</div>
                        {modalStep === 'camera' ? (
                            <>
                                <div className="findpw-modal-title">카드 촬영</div>
                                <div className="findpw-modal-desc">장애인 복지카드를 촬영해주세요.</div>
                                <div className="findpw-modal-camera-area">
                                    {stream ? (
                                        <video ref={videoRef} autoPlay playsInline muted className="findpw-modal-video"></video>
                                    ) : (
                                        <>
                                            <div className="findpw-modal-camera-text">{cameraError || '카메라 연결 중...'}</div>
                                            <img src={iconCamera} alt="Camera" className="findpw-modal-camera-icon" />
                                        </>
                                    )}
                                </div>
                                {stream && (
                                    <div className="findpw-shutter-button" onClick={handleSnap}>
                                        <div className="findpw-shutter-inner"></div>
                                    </div>
                                )}
                            </>
                        ) : (
                            <>
                                <div className="findpw-modal-title">카드 정보 인증 확인</div>
                                <div className="findpw-modal-desc">복지카드 정보를 입력해주세요.</div>

                                <div className="findpw-form-field">
                                    <label>카드사</label>
                                    <input
                                        type="text"
                                        name="card_company"
                                        value={cardForm.card_company}
                                        onChange={handleInputChange}
                                        className="findpw-modal-input"
                                    />
                                </div>
                                <div className="findpw-form-field">
                                    <label>복지카드 번호</label>
                                    <input
                                        type="text"
                                        name="card_number"
                                        value={cardForm.card_number}
                                        onChange={handleInputChange}
                                        className="findpw-modal-input"
                                        placeholder="0000-0000-0000-0000"
                                    />
                                </div>
                                <div className="findpw-form-row">
                                    <div className="findpw-form-field half">
                                        <label>유효기간</label>
                                        <input
                                            type="text"
                                            name="expiration_date"
                                            value={cardForm.expiration_date}
                                            onChange={handleInputChange}
                                            className="findpw-modal-input"
                                            placeholder="MM/YY"
                                        />
                                    </div>
                                    <div className="findpw-form-field half">
                                        <label>CVC</label>
                                        <input
                                            type="text"
                                            name="cvc"
                                            value={cardForm.cvc}
                                            onChange={handleInputChange}
                                            className="findpw-modal-input"
                                            placeholder="000"
                                        />
                                    </div>
                                </div>
                                <button className="findpw-confirm-btn" onClick={handleVerify}>인증하기</button>
                            </>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default FindPasswordA;
