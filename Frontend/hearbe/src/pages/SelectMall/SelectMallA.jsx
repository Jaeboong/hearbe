import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, ShoppingCart, User } from 'lucide-react';
import './SelectMallA.css';
import iconNaver from '../../assets/naver.png';
import iconCoupang from '../../assets/coupang.png';
import icon11st from '../../assets/11.png';
import iconEmart from '../../assets/emartMall.png';
import BackButton from '../common/BackButtonA';

const SelectMall = () => {
    const navigate = useNavigate();

    const handleSelectMall = (mall) => {
        if (mall === 'naver') {
            window.open('https://shopping.naver.com/ns/home', '_blank');
        } else if (mall === 'coupang') {
            window.open('https://www.coupang.com', '_blank');
        } else if (mall === '11st') {
            window.open('https://m.11st.co.kr/', '_blank');
        } else if (mall === 'emart') {
            window.open('https://m.ssg.com/', '_blank');
        } else if (mall === 'cart') {
            navigate('/A/cart');
        }
    };

    return (
        <div className="mall-container">
            <BackButton onClick={() => navigate('/A/login')} variant="arrow-only" />
            {/* Header */}
            <div className="mypage-topbar">
                <div className="mypage-topbar-actions">
                    <button className="topbar-action" onClick={() => navigate('/')}>
                        <Home size={72} />
                        <span>홈</span>
                    </button>
                    <button className="topbar-action" onClick={() => handleSelectMall('cart')}>
                        <ShoppingCart size={72} />
                        <span>카트</span>
                    </button>
                    <button className="topbar-action" onClick={() => navigate('/A/mypage')}>
                        <User size={72} />
                        <span>마이</span>
                    </button>
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
                            <img src={icon11st} alt="11st" className="mall-logo-img" />
                        </div>
                    </div>

                    {/* Emart (4) */}
                    <div className="mall-card-wrapper" onClick={() => handleSelectMall('emart')}>
                        <div className="mall-square-box mall-emart-box">
                            <span className="mall-number">4</span>
                            <img src={iconEmart} alt="Emart" className="mall-logo-img" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SelectMall;
