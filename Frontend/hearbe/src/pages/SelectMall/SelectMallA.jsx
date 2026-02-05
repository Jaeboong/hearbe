import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShoppingCart, User, LogOut } from 'lucide-react';
import './SelectMallA.css';
import iconNaver from '../../assets/naver.png';
import iconCoupang from '../../assets/coupang.png';
import icon11st from '../../assets/11st_logo.png';
import iconEmart from '../../assets/SSG_logo.png';
import logoA from '../../assets/logoA.png';
import { authAPI } from '../../services/authAPI';

const SelectMall = () => {
    const navigate = useNavigate();

    const mallUrlMap = {
        naver: 'https://shopping.naver.com/ns/home',
        coupang: 'https://www.coupang.com',
        '11st': 'https://m.11st.co.kr/',
        emart: 'https://m.ssg.com/'
    };

    const handleSelectMall = (mall) => {
        if (mall === 'cart') {
            navigate('/A/cart');
            return;
        }

        const targetUrl = mallUrlMap[mall];
        if (targetUrl) {
            window.open(targetUrl, '_blank', 'noopener,noreferrer');
        }
    };

    const handleLogout = async () => {
        try {
            await authAPI.logout();
        } catch (err) {
            console.warn('Logout failed:', err);
        } finally {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('savedLoginId');
            localStorage.removeItem('savedLoginPassword');
            localStorage.removeItem('userData');
            localStorage.removeItem('user_id');
            localStorage.removeItem('username');
            navigate('/main');
        }
    };

    return (
        <div className="mall-container">
            <img
                src={logoA}
                alt="Logo"
                className="mall-logo-left"
                onClick={() => navigate('/main')}
            />
            {/* Header */}
            <div className="mypage-topbar">
                <div className="mypage-topbar-actions">
                    <button className="topbar-action" onClick={() => handleSelectMall('cart')}>
                        <ShoppingCart size={72} />
                        <span>카트</span>
                    </button>
                    <button className="topbar-action" onClick={() => navigate('/A/member-info')}>
                        <User size={72} />
                        <span>마이</span>
                    </button>
                    <button className="topbar-action" onClick={handleLogout}>
                        <LogOut size={72} />
                        <span>로그아웃</span>
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

            <footer className="landing-footer-a">
                <p>© 2026 HearBe. All rights reserved.</p>
            </footer>
        </div>
    );
};

export default SelectMall;

