import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import BackButton from '../common/BackButtonA';
import iconCamera from '../../assets/icon-camera.png';
import iconCard from '../../assets/icon-card.png';
import './CardManagementA.css';

const CardManagementA = () => {
    const navigate = useNavigate();
    const location = useLocation();

    // Initial card data (would come from localStorage or API)
    const [cardData, setCardData] = useState({
        company: '신한카드',
        number: '0000-0000-0000-0000',
        expiry: '01/21',
        cvc: '123'
    });

    // Modal states
    const [showModal, setShowModal] = useState(false);
    const [modalStep, setModalStep] = useState('camera'); // 'camera' or 'form'

    // Camera logic
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
        }
    };

    const stopCamera = () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            setStream(null);
        }
    };

    // Camera modal management
    useEffect(() => {
        if (showModal && modalStep === 'camera') {
            startCamera();
        } else {
            stopCamera();
        }
        return () => {
            stopCamera();
        };
    }, [showModal, modalStep]);

    // Stream connection
    useEffect(() => {
        if (stream && videoRef.current) {
            videoRef.current.muted = true;
            videoRef.current.srcObject = stream;
            videoRef.current.play()
                .then(() => console.log("video play success"))
                .catch(e => console.error("video play fail:", e));
        }
    }, [stream, modalStep]);

    const handleChangeClick = () => {
        setShowModal(true);
        setModalStep('camera');
    };

    const handleSnap = () => {
        setModalStep('form');
    };

    const handleCardRegister = () => {
        // Update card data with new information
        setCardData({
            company: '신한카드',
            number: '0000-0000-0000-0000',
            expiry: '01/21',
            cvc: '123'
        });
        setShowModal(false);
        setModalStep('camera');
    };

    const handleModalClose = () => {
        setShowModal(false);
        setModalStep('camera');
    };

    const menuItems = [
        { id: 'profile', label: '회원정보', path: '/A/member-info' },
        { id: 'orders', label: '주문내역', path: '/A/order-history' },
        { id: 'cart', label: '장바구니', path: '/A/cart' },
        { id: 'wishlist', label: '찜한 상품', path: '/A/wishlist' },
        { id: 'card', label: '장애인 복지카드 변경', path: '/A/card-management' }
    ];

    const currentPath = location.pathname;

    return (
        <div className="cardmgmt-container">
            <BackButton onClick={() => navigate(-1)} variant="arrow-only" />

            <div className="cardmgmt-content">
                {/* Sidebar */}
                <aside className="cardmgmt-sidebar">
                    <h1 className="sidebar-title">마이페이지</h1>
                    <nav className="sidebar-nav">
                        {menuItems.map(item => (
                            <div
                                key={item.id}
                                className={`sidebar-item ${currentPath === item.path ? 'active' : ''}`}
                                onClick={() => navigate(item.path)}
                            >
                                {item.label}
                            </div>
                        ))}
                    </nav>
                </aside>

                {/* Main Content */}
                <main className="cardmgmt-main">
                    <h2 className="content-title">장애인 복지카드 변경하기</h2>

                    {/* Current Card Display */}
                    <div className="current-card-display">
                        <div className="card-info-row">
                            <span className="card-label">카드사</span>
                            <span className="card-value">{cardData.company}</span>
                        </div>
                        <div className="card-info-row">
                            <span className="card-label">복지카드 번호</span>
                            <span className="card-value">{cardData.number}</span>
                        </div>
                        <div className="card-info-row-flex">
                            <div className="card-info-col">
                                <span className="card-label">유효기간</span>
                                <span className="card-value">{cardData.expiry}</span>
                            </div>
                            <div className="card-info-col">
                                <span className="card-label">CVC</span>
                                <span className="card-value">{cardData.cvc}</span>
                            </div>
                        </div>
                    </div>

                    <button className="change-card-btn" onClick={handleChangeClick}>
                        변경하기
                    </button>
                </main>
            </div>

            {/* Camera Modal */}
            {showModal && (
                <div className="card-modal-overlay">
                    <div className="card-modal-box" onClick={(e) => e.stopPropagation()}>
                        {/* Close Button */}
                        <div className="card-modal-close" onClick={handleModalClose}>X</div>

                        {modalStep === 'camera' ? (
                            // Camera Step
                            <>
                                <div className="card-modal-title">카드 촬영</div>
                                <div className="card-modal-desc">장애인 복지카드를 촬영해주세요.</div>

                                <div className="card-camera-area">
                                    {stream ? (
                                        <video ref={videoRef} autoPlay playsInline muted className="card-video-stream"></video>
                                    ) : (
                                        <>
                                            <div className="card-camera-text">카메라 연결 중...</div>
                                            <img src={iconCamera} alt="Camera" className="card-camera-icon" />
                                        </>
                                    )}
                                </div>

                                {stream && (
                                    <div className="card-shutter-button" onClick={handleSnap}>
                                        <div className="card-shutter-inner"></div>
                                    </div>
                                )}
                            </>
                        ) : (
                            // Form Step
                            <>
                                <div className="card-form-content">
                                    <div className="card-form-header-area">
                                        <img src={iconCard} alt="card" className="small-card-icon" />
                                        <span>장애인 복지카드 정보</span>
                                    </div>

                                    <div className="card-modal-desc">인식된 정보를 확인해주세요.</div>

                                    <div className="form-field-group">
                                        <label>카드사</label>
                                        <input type="text" value="신한카드" readOnly className="card-modal-input" />
                                    </div>

                                    <div className="form-field-group">
                                        <label>복지카드 번호</label>
                                        <input type="text" value="0000-0000-0000-0000" readOnly className="card-modal-input" />
                                    </div>

                                    <div className="form-row-group">
                                        <div className="form-field-group half">
                                            <label>유효기간</label>
                                            <input type="text" value="01/21" readOnly className="card-modal-input" />
                                        </div>
                                        <div className="form-field-group half">
                                            <label>CVC</label>
                                            <input type="text" value="123" readOnly className="card-modal-input" />
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
            )}
        </div>
    );
};

export default CardManagementA;
