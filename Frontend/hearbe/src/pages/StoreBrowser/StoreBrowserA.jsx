import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './StoreBrowserA.css';
import iconUser from '../../assets/icon-user.png';
import iconCart from '../../assets/icon-cart.png'; // Updated
import iconShare from '../../assets/icon-share.png'; // New Share Icon
import iconCard from '../../assets/icon-cart.png';
import logo from '../../assets/logoA.png';

import BackButton from '../common/BackButtonA';

const StoreBrowser = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const url = location.state?.url || 'https://m.naver.com';

    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [showShareModal, setShowShareModal] = useState(false);
    const [isSharing, setIsSharing] = useState(false);
    const [inviteCode, setInviteCode] = useState('0000');

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
        // Generate random 4-digit code
        const code = Math.floor(1000 + Math.random() * 9000).toString();
        setInviteCode(code);
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
                        <div className="sharing-pill">화면 공유 중 (코드: {inviteCode})</div>
                        <div className="participant-pill">
                            <img src={logo} alt="User" className="p-icon" />
                            <span>참가자 (1명)</span>
                        </div>
                    </div>

                    {/* Bottom Control Bar */}
                    <div className="sharing-bottom-bar">
                        <button className="sharing-btn" onClick={handleCart}>
                            <img src={iconCart} alt="Cart" className="s-icon" />
                            <span>장바구니</span>
                        </button>
                        <button className="sharing-btn primary">
                            <img src={iconCard} alt="Buy" className="s-icon" />
                            <span>바로구매</span>
                        </button>
                        <button className="sharing-btn highlight" onClick={handleEndShare}>
                            <img src={iconShare} alt="Share" className="s-icon" />
                            <span>공유 종료</span>
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
                                <img src={iconCart} alt="Cart" className="menu-icon" />
                                <span className="menu-text">장바구니</span>
                            </div>
                            <div className="menu-item" onClick={handleShareClick}>
                                <img src={iconShare} alt="Share" className="menu-icon" />
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

            {/* Share Modal (Popup) */}
            {showShareModal && (
                <div className="share-modal-overlay">
                    <div className="share-modal-content">
                        <div className="share-modal-title">초대 코드</div>
                        <div className="share-code-box">{inviteCode.split('').join(' ')}</div>
                        <div className="share-modal-desc">이 코드를 상대방에게 알려주세요</div>
                        <div className="share-modal-btns">
                            <button className="sm-btn cancel" onClick={() => setShowShareModal(false)}>취소</button>
                            <button className="sm-btn confirm" onClick={handleEnterShare}>입장</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default StoreBrowser;
