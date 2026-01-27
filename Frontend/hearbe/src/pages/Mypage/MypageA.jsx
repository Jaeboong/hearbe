import React from 'react';
import { useNavigate } from 'react-router-dom';
import './MypageA.css';
import BackButton from '../common/BackButtonA';
import iconHome from '../../assets/home.png';
import iconCart from '../../assets/icon-cart.png';
import iconUser from '../../assets/icon-user.png';

const Mypage = () => {
    const navigate = useNavigate();

    const requestedMenuItems = [
        { id: 1, label: '회원정보', action: () => { } },
        { id: 2, label: '주문내역', action: () => { } },
        { id: 3, label: '장바구니', action: () => navigate('/cart') },
        { id: 4, label: '찜한 상품', action: () => { } },
        { id: 5, label: '장애인 복지카드 변경', action: () => { } },
    ];

    return (
        <div className="mypage-container">
            {/* 1. 상단 네비게이션 (홈/카트/마이) - 가장 위로 뺐어! */}
            <div className="top-nav-area">
                <div className="header-nav">
                    <div className="nav-item" onClick={() => navigate('/mall')}>
                        <img src={iconHome} alt="Home" className="nav-icon" />
                        <span>홈</span>
                    </div>
                    <div className="nav-item" onClick={() => navigate('/cart')}>
                        <img src={iconCart} alt="Cart" className="nav-icon" />
                        <span>카트</span>
                    </div>
                    <div className="nav-item" onClick={() => navigate('/mypage')}>
                        <img src={iconUser} alt="My" className="nav-icon" />
                        <span>마이</span>
                    </div>
                </div>
            </div>

            {/* 2. 유저 정보 영역 (뒤로가기 화살표 + 김싸피님) */}
            <div className="user-info-area">
                {/* 화살표 */}
                <BackButton onClick={() => navigate(-1)} variant="arrow-only" />

                {/* 인사말 (화살표 오른쪽에 붙을 거야) */}
                <div className="user-greeting">
                    <div className="user-icon-circle">
                        <img src={iconUser} alt="User" className="user-profile-icon" />
                    </div>
                    <span className="greeting-text">김싸피님, 환영합니다!</span>
                </div>
            </div>

            {/* 3. 페이지 제목 */}
            <div className="page-title">마이페이지</div>

            {/* 4. 메뉴 리스트 */}
            <div className="menu-list">
                {requestedMenuItems.map((item) => (
                    <div key={item.id} className="menu-item" onClick={item.action}>
                        <div className="menu-number">{item.id}</div>
                        <div className="menu-label">{item.label}</div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Mypage;