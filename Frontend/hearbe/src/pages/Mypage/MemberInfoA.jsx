import React from 'react';
import { useNavigate } from 'react-router-dom';
import BackButton from '../common/BackButtonA';
import './MemberInfoA.css';

const MemberInfoA = () => {
    const navigate = useNavigate();

    // Get user data from localStorage (from signup/login)
    const userData = {
        name: '김싸피',
        phone: '010-1234-5678',
        password: '******'
    };

    const menuItems = [
        { id: 'profile', label: '회원정보', path: '/mypage/profile' },
        { id: 'orders', label: '주문내역', path: '/mypage/orders' },
        { id: 'cart', label: '장바구니', path: '/cart' },
        { id: 'wishlist', label: '찜한 상품', path: '/mypage/wishlist' },
        { id: 'card', label: '장애인 복지카드 변경', path: '/mypage/card' }
    ];

    const currentPath = '/mypage/profile';

    const handleLogout = () => {
        // Clear user data from localStorage
        localStorage.removeItem('userData');
        navigate('/login');
    };

    return (
        <div className="memberinfo-container">
            <BackButton onClick={() => navigate(-1)} variant="arrow-only" />

            <div className="memberinfo-content">
                {/* Sidebar Navigation */}
                <aside className="memberinfo-sidebar">
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
                <main className="memberinfo-main">
                    <h2 className="content-title">회원 정보</h2>

                    <div className="info-table">
                        <div className="table-row">
                            <div className="table-label">이름</div>
                            <div className="table-value">{userData.name}</div>
                        </div>
                        <div className="table-row">
                            <div className="table-label">휴대폰번호</div>
                            <div className="table-value">{userData.phone}</div>
                        </div>
                        <div className="table-row">
                            <div className="table-label">비밀번호</div>
                            <div className="table-value">{userData.password}</div>
                        </div>
                    </div>

                    <div className="logout-section">
                        <span className="logout-link" onClick={handleLogout}>
                            로그아웃
                        </span>
                    </div>
                </main>
            </div>
        </div>
    );
};

export default MemberInfoA;
