import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Home, LogOut } from 'lucide-react';
import logoA from '../../assets/logoA.png';
import { memberAPI } from '../../services/memberAPI';
import { authAPI } from '../../services/authAPI';
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
        { id: 'card', label: <>장애인 복지카드<br />변경</>, path: '/A/card-management' }
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
            localStorage.removeItem('user_name');
            navigate('/');
        }
    };

    const handleWithdraw = async () => {
        const password = window.prompt("회원탈퇴를 위해 비밀번호를 입력해주세요.");
        if (!password) return;

        if (!window.confirm("정말로 탈퇴하시겠습니까? 탈퇴 시 모든 정보가 삭제됩니다.")) {
            return;
        }

        try {
            await authAPI.deleteAccount(password);
            alert("회원탈퇴가 완료되었습니다.");

            // 로그아웃과 동일한 정리 작업
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('savedLoginId');
            localStorage.removeItem('savedLoginPassword');
            localStorage.removeItem('userData');
            localStorage.removeItem('user_id');
            localStorage.removeItem('username');
            localStorage.removeItem('user_name');
            navigate('/');
        } catch (err) {
            console.error('Withdrawal failed:', err);
            alert(`회원탈퇴 실패: ${err.message}`);
        }
    };

    const handleRetry = () => {
        setError(null);
        setLoading(true);
        // Re-trigger useEffect by navigating to same route
        navigate(location.pathname, { replace: true });
    };

    return (
        <div className="memberinfo-container">
            <img
                src={logoA}
                alt="Logo"
                className="memberinfo-logo-left"
                onClick={() => window.location.assign('/')}
            />

            <div className="mypage-topbar">
                <h1 className="mypage-topbar-title">마이페이지</h1>
                <div className="mypage-topbar-actions">
                    <button className="topbar-action" onClick={() => navigate('/A/mall')}>
                        <Home size={72} />
                        <span>홈</span>
                    </button>
                    <button className="topbar-action" onClick={handleLogout}>
                        <LogOut size={72} />
                        <span>로그아웃</span>
                    </button>
                </div>
            </div>

            <div className="memberinfo-content">
                {/* Sidebar Navigation */}
                <aside className="memberinfo-sidebar">
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
                                    <div className="table-value password-value">
                                        {userData.password}
                                        <button className="password-change-btn">변경하기</button>
                                    </div>
                                </div>
                            </div>

                            <div className="logout-section">
                                <span className="logout-link" onClick={handleWithdraw}>
                                    회원탈퇴
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




