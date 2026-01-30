import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import BackButton from '../common/BackButtonA';
import { memberAPI } from '../../services/memberAPI';
import './MemberInfoA.css';

const MemberInfoA = () => {
    const navigate = useNavigate();
    const location = useLocation();

    const [userData, setUserData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const menuItems = [
        { id: 'profile', label: '회원정보', path: '/A/member-info' },
        { id: 'orders', label: '주문내역', path: '/A/order-history' },
        { id: 'cart', label: '장바구니', path: '/A/cart' },
        { id: 'wishlist', label: '찜한 상품', path: '/A/wishlist' },
        { id: 'card', label: '장애인 복지카드 변경', path: '/A/card-management' }
    ];

    const currentPath = location.pathname;

    // Phone number formatting helper
    const formatPhoneNumber = (phone) => {
        if (!phone) return '';
        const cleaned = phone.replace(/\D/g, '');
        if (cleaned.length === 11) {
            return `${cleaned.slice(0, 3)}-${cleaned.slice(3, 7)}-${cleaned.slice(7)}`;
        }
        return phone;
    };

    // Fetch user profile on mount
    useEffect(() => {
        const fetchUserProfile = async () => {
            try {
                setLoading(true);
                setError(null);
                const response = await memberAPI.getProfile();

                // 백엔드 ProfileResponse 구조:
                // username: 실제 이름 (user.getName())
                // phoneNumber: 전화번호
                // userType: 사용자 유형 (BLIND, LOW_VISION, GENERAL)
                setUserData({
                    name: response.data?.username || '-',
                    phone: formatPhoneNumber(response.data?.phoneNumber) || '-',
                    password: '******',
                    userType: response.data?.userType || '-'
                });
            } catch (err) {
                console.error('Failed to fetch user profile:', err);
                setError(err.message);

                // Redirect to login on 401
                if (err.message === '로그인이 필요합니다.') {
                    navigate('/A/login');
                }
            } finally {
                setLoading(false);
            }
        };

        fetchUserProfile();
    }, [navigate]);

    const handleLogout = () => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('userData');
        navigate('/login');
    };

    const handleRetry = () => {
        setError(null);
        setLoading(true);
        // Re-trigger useEffect by navigating to same route
        navigate(location.pathname, { replace: true });
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

                    {loading ? (
                        <div className="loading-state">
                            <div className="spinner"></div>
                            <p>사용자 정보를 불러오는 중...</p>
                        </div>
                    ) : error ? (
                        <div className="error-state">
                            <p className="error-message">사용자 정보를 불러오지 못했습니다.</p>
                            <p className="error-detail">{error}</p>
                            <button className="retry-btn" onClick={handleRetry}>
                                다시 시도
                            </button>
                        </div>
                    ) : userData ? (
                        <>
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
                        </>
                    ) : null}
                </main>
            </div>
        </div>
    );
};

export default MemberInfoA;
