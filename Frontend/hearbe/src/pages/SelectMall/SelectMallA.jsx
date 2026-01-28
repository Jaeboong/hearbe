import React from 'react';
import { useNavigate } from 'react-router-dom';
import './SelectMallA.css';
import iconUser from '../../assets/icon-user.png';
import iconMic from '../../assets/mike.png';
import iconHome from '../../assets/home.png';
import iconCart from '../../assets/icon-cart.png'; // Use cart.png
import iconNaver from '../../assets/naver.png';
import iconCoupang from '../../assets/coupang.png';
import BackButton from '../common/BackButtonA';

const SelectMall = () => {
    const navigate = useNavigate();

    const handleSelectMall = (mall) => {
        if (mall === 'naver') {
            navigate('/A/store', { state: { url: 'https://m.shopping.naver.com/' } });
        } else if (mall === 'coupang') {
            navigate('/A/store', { state: { url: 'https://m.coupang.com/' } });
        } else if (mall === 'cart') {
            navigate('/A/cart');
        }
    };

    return (
        <div className="mall-container">
            <BackButton onClick={() => navigate('/A/login')} variant="arrow-only" />
            {/* Header */}
            <div className="mall-header">
                <div className="header-title">쇼핑몰 선택</div>
                <div className="header-nav">
                    <div className="nav-item">
                        <img src={iconHome} alt="Home" className="nav-icon" />
                        <span>홈</span>
                    </div>
                    <div className="nav-item" onClick={() => handleSelectMall('cart')}>
                        <img src={iconCart} alt="Cart" className="nav-icon" />
                        <span>카트</span>
                    </div>
                    <div className="nav-item">
                        <img src={iconUser} alt="My" className="nav-icon" />
                        <span>마이</span>
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="mall-content">
                {/* Naver */}
                <div className="mall-card naver-card" onClick={() => handleSelectMall('naver')}>
                    <div className="mall-icon-box naver-box">
                        <img src={iconNaver} alt="Naver" className="mall-logo-img" />
                    </div>
                    <div className="mall-text">1 네이버</div>
                </div>

                {/* Mic Center */}
                <div className="mic-center">
                    <img src={iconMic} alt="Mic" className="mic-icon" />
                </div>

                {/* Coupang */}
                <div className="mall-card coupang-card" onClick={() => handleSelectMall('coupang')}>
                    <div className="mall-icon-box coupang-box">
                        <img src={iconCoupang} alt="Coupang" className="mall-logo-img" />
                    </div>
                    <div className="mall-text">2 쿠팡</div>
                </div>
            </div>
        </div>
    );
};

export default SelectMall;
