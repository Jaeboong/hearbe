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
            navigate('/A/store', { state: { url: 'https://www.coupang.com' } });
        } else if (mall === '11st') {
            navigate('/A/store', { state: { url: 'https://m.11st.co.kr/' } });
        } else if (mall === 'emart') {
            navigate('/A/store', { state: { url: 'https://m.ssg.com/' } });
        } else if (mall === 'cart') {
            navigate('/A/cart');
        }
    };

    return (
        <div className="mall-container">
            <BackButton onClick={() => navigate('/login')} variant="arrow-only" />
            {/* Header */}
            <div className="mall-header">
                <div className="header-title">쇼핑몰 선택</div>
                <div className="header-nav">
                    <div className="nav-item" onClick={() => navigate('/')}>
                        <img src={iconHome} alt="Home" className="nav-icon" />
                        <span>홈</span>
                    </div>
                    <div className="nav-item" onClick={() => handleSelectMall('cart')}>
                        <img src={iconCart} alt="Cart" className="nav-icon" />
                        <span>카트</span>
                    </div>
                    <div className="nav-item" onClick={() => navigate('/A/mypage')}>
                        <img src={iconUser} alt="My" className="nav-icon" />
                        <span>마이</span>
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="mall-content">
                <div className="mall-scroll-container">
                    {/* Coupang (1) */}
                    <div className="mall-card-wrapper" onClick={() => handleSelectMall('coupang')}>
                        <div className="mall-square-box coupang-box">
                            <span className="mall-number">1</span>
                            <img src={iconCoupang} alt="Coupang" className="mall-logo-img" />
                        </div>
                    </div>

                    {/* Naver (2) */}
                    <div className="mall-card-wrapper" onClick={() => handleSelectMall('naver')}>
                        <div className="mall-square-box naver-box">
                            <span className="mall-number">2</span>
                            <img src={iconNaver} alt="Naver" className="mall-logo-img" />
                        </div>
                    </div>

                    {/* 11st (3) */}
                    <div className="mall-card-wrapper" onClick={() => handleSelectMall('11st')}>
                        <div className="mall-square-box mall-11st-box">
                            <span className="mall-number">3</span>
                            <div className="mall-logo-placeholder">11st</div>
                        </div>
                    </div>

                    {/* Emart (4) */}
                    <div className="mall-card-wrapper" onClick={() => handleSelectMall('emart')}>
                        <div className="mall-square-box mall-emart-box">
                            <span className="mall-number">4</span>
                            <div className="mall-logo-placeholder">SSG</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SelectMall;
