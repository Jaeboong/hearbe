import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './StoreBrowserA.css';
import iconUser from '../../assets/icon-user.png';
import iconCard from '../../assets/icon-card.png';
import iconPhone from '../../assets/icon-phone.png';
import hLogoOrigin from '../../assets/h-logo-origin.jpg'; // Using the origin logo

import BackButton from '../common/BackButtonA';

const StoreBrowser = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const url = location.state?.url || 'https://m.naver.com';

    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [showShareModal, setShowShareModal] = useState(false);
    const [isSharing, setIsSharing] = useState(false);

    // Naver Add Simulation
    const isNaver = url.includes('naver');

    const handleSimulateAddCart = () => {
        const newItem = {
            id: Date.now(),
            mall: '네이버',
            name: `네이버 스토어 상품 ${Math.floor(Math.random() * 100)}`,
            price: Math.floor(Math.random() * 50000) + 10000,
            quantity: 1,
            image: null,
            date: new Date().toLocaleDateString()
        };

        const currentCart = JSON.parse(localStorage.getItem('naverCart') || '[]');
        localStorage.setItem('naverCart', JSON.stringify([...currentCart, newItem]));
        alert("장바구니에 상품을 담았습니다!");
    };

    const handleToggleMenu = () => {
        if (!isSharing) {
            setIsMenuOpen(!isMenuOpen);
        }
    };

    const handleShareClick = () => {
        setIsMenuOpen(false); // Close menu
        setShowShareModal(true);
    };

    const handleEnterShare = () => {
        setShowShareModal(false);
        setIsSharing(true);
    };

    const handleEndShare = () => {
        setIsSharing(false);
    };

    const handleCart = () => {
        setIsMenuOpen(false);
        navigate('/cart');
    };

    return (
        <div className="store-container">
            <BackButton onClick={() => navigate('/mall')} variant="navy" />

            {/* Iframe */}
            <iframe
                src={url}
                title="Store"
                className="store-iframe"
            />

            {/* --- Sharing Mode UI --- */}
            {isSharing && (
                <>
                    {/* Top Sharing Banner */}
                    <div className="sharing-header">
                        <div className="sharing-pill">화면 공유 중 (코드: 4572)</div>
                        <div className="participant-pill">
                            <img src={hLogoOrigin} alt="User" className="p-icon" />
                            <span>참가자 (1명)</span>
                        </div>
                    </div>

                    {/* Bottom Control Bar */}
                    <div className="sharing-bottom-bar">
                        <button className="sharing-btn" onClick={handleCart}>
                            <img src={iconCard} alt="Cart" className="s-icon" />
                            <span>장바구니</span>
                        </button>
                        <button className="sharing-btn primary">
                            <img src={iconCard} alt="Buy" className="s-icon" />
                            <span>바로구매</span>
                        </button>
                        <button className="sharing-btn highlight" onClick={handleEndShare}>
                            <span>X 공유 종료</span>
                        </button>
                    </div>
                </>
            )}


            {/* --- Normal Mode UI (Hidden when sharing) --- */}
            {!isSharing && (
                <>
                    {/* Menu Bubble */}
                    {isMenuOpen && (
                        <div className="menu-bubble">
                            <div className="menu-item">
                                <img src={iconUser} alt="My Page" className="menu-icon" />
                                <span className="menu-text">마이페이지</span>
                            </div>
                            <div className="menu-item" onClick={handleCart}>
                                <img src={iconCard} alt="Cart" className="menu-icon" />
                                <span className="menu-text">장바구니</span>
                            </div>
                            <div className="menu-item" onClick={handleShareClick}>
                                <img src={iconPhone} alt="Share" className="menu-icon" />
                                <span className="menu-text">공유</span>
                            </div>
                        </div>
                    )}

                    {/* Hamburger Button */}
                    <div className={`hamburger-overlay ${isMenuOpen ? 'open' : ''}`} onClick={handleToggleMenu}>
                        {isMenuOpen ? (
                            <div className="close-x">X</div>
                        ) : (
                            <>
                                <div className="hamburger-line"></div>
                                <div className="hamburger-line"></div>
                                <div className="hamburger-line"></div>
                            </>
                        )}
                    </div>
                </>
            )}

            {/* --- Share Code Modal --- */}
            {showShareModal && (
                <div className="modal-overlay-dark">
                    <div className="share-modal-box">
                        <div className="share-title">회의 코드</div>
                        <div className="share-code-box">4 5 7 2</div>
                        <div className="share-desc">이 코드를 상대방에게 알려주세요</div>
                        <div className="share-btn-row">
                            <button className="share-btn-cancel" onClick={() => setShowShareModal(false)}>취소</button>
                            <button className="share-btn-enter" onClick={handleEnterShare}>입장</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default StoreBrowser;
