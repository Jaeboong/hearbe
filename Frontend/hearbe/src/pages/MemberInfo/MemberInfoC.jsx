import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Mail, Lock, Home, ShoppingCart, ShieldCheck } from 'lucide-react';
import { memberAPI } from '../../services/memberAPI';
import '../MyPage/MyPageC.css';

export default function MemberInfoC({ onHome }) {
    const navigate = useNavigate();

    const [userData, setUserData] = useState({
        name: '',
        email: '',
        phone: '',
    });
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    // 사이드바 아이템 (A형과 동일한 URL 구조)
    const sidebarItems = [
        { id: 'member-info', label: '회원 정보', path: '/C/member-info' },
        { id: 'order-history', label: '주문 내역', path: '/C/order-history' },
        { id: 'wishlist', label: '찜한 상품', path: '/C/wishlist' },
        { id: 'cart', label: '장바구니', path: '/C/cart' },
    ];

    useEffect(() => {
        const fetchUserProfile = async () => {
            try {
                setIsLoading(true);
                setError(null);
                const response = await memberAPI.getProfile();

                // 데이터 매핑
                const profileData = response.data || response;
                setUserData({
                    name: profileData.username || profileData.name || '',
                    email: profileData.email || '',
                    phone: profileData.phoneNumber || profileData.phone || '',
                });
            } catch (err) {
                console.error('Failed to fetch user profile:', err);
                setError(err.message);

                if (err.message === '로그인이 필요합니다.' || err.message === '접근 권한이 없습니다.') {
                    localStorage.removeItem('accessToken');
                    localStorage.removeItem('refreshToken');
                    localStorage.removeItem('user');
                    navigate('/C/login');
                    return;
                }

                // API 실패 시 localStorage에서 백업 데이터 로드
                const storedUser = localStorage.getItem('user');
                if (storedUser) {
                    try {
                        const parsed = JSON.parse(storedUser);
                        setUserData({
                            name: parsed.name || '',
                            email: parsed.email || '',
                            phone: parsed.phone || '',
                        });
                    } catch (e) {
                        console.error('Failed to parse stored user data:', e);
                    }
                }
            } finally {
                setIsLoading(false);
            }
        };

        fetchUserProfile();
    }, [navigate]);

    const handlePasswordReset = () => {
        navigate('/C/findPassword');
    };

    const handleWithdraw = () => {
        if (window.confirm('정말로 회원탈퇴 하시겠습니까?')) {
            alert('회원탈퇴가 완료되었습니다.');
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('user');
            navigate('/');
        }
    };

    const handleLogout = () => {
        if (window.confirm('로그아웃 하시겠습니까?')) {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('user');
            navigate('/C/login');
        }
    };

    return (
        <div className="mypage-container">
            {/* Header - MyPageC와 동일한 구조 */}
            <header className="mall-header-c">
                <div className="header-left-c">
                    <div className="title-area-c" style={{ marginLeft: 0 }}>
                        <div className="title-icon-box-c">
                            <User size={24} />
                        </div>
                        <div className="title-text-c">
                            <h1>마이페이지</h1>
                            <span className="subtitle-c">My Page</span>
                        </div>
                    </div>
                </div>

                <div className="header-right-c">
                    <button className="nav-item-c" onClick={onHome || (() => navigate('/'))}>
                        <div className="nav-icon-c"><Home size={24} /></div>
                        <span>홈</span>
                    </button>
                    <button className="nav-item-c" onClick={() => navigate('/C/cart')}>
                        <div className="nav-icon-c"><ShoppingCart size={24} /></div>
                        <span>장바구니</span>
                    </button>
                    <button className="nav-item-c active">
                        <div className="nav-icon-c"><User size={24} /></div>
                        <span>마이페이지</span>
                    </button>
                </div>
            </header>

            <div className="mypage-layout">
                {/* Sidebar - MyPageC와 동일한 구조 */}
                <aside className="mypage-sidebar">
                    <div className="sidebar-profile-card">
                        <div className="sidebar-avatar">
                            <User size={40} color="#7c3aed" />
                        </div>
                        <div className="sidebar-profile-info">
                            <h2 className="sidebar-name">{userData.name}님</h2>
                            <span className="sidebar-badge">hearbe 회원</span>
                        </div>
                        <p className="sidebar-welcome">오늘도 즐거운 쇼핑 되세요!</p>
                    </div>

                    <div className="sidebar-menu-list">
                        {sidebarItems.map((item) => (
                            <button
                                key={item.id}
                                onClick={() => navigate(item.path)}
                                className={`mp-sidebar-item ${item.id === 'member-info' ? 'active' : ''}`}
                                style={{
                                    display: 'flex',
                                    flexDirection: 'row',
                                    alignItems: 'center',
                                    fontSize: '1.85rem',
                                    width: '100%',
                                    padding: '1.4rem 2rem',
                                    color: item.id === 'member-info' ? '#7c3aed' : '#9ca3af',
                                    background: item.id === 'member-info' ? 'white' : 'transparent',
                                    border: 'none',
                                    fontWeight: item.id === 'member-info' ? '800' : '600',
                                    boxShadow: item.id === 'member-info' ? '0 4px 15px rgba(0, 0, 0, 0.03)' : 'none',
                                    borderRadius: '1rem',
                                    cursor: 'pointer'
                                }}
                            >
                                <span className="label" style={{ fontSize: 'inherit' }}>{item.label}</span>
                            </button>
                        ))}
                    </div>
                </aside>

                {/* Main Content */}
                <main className="mypage-content">
                    <div className="content-stack">
                        {/* Profile Section */}
                        <section className="dashboard-card">
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                                <div className="card-header-row" style={{ marginBottom: 0 }}>
                                    <ShieldCheck size={24} className="purple-text" />
                                    <h3 className="card-title" style={{ margin: 0 }}>회원 정보</h3>
                                </div>
                                <button className="withdraw-link" onClick={handleLogout} style={{ marginTop: 0 }}>
                                    로그아웃
                                </button>
                            </div>
                            {isLoading ? (
                                <div style={{ textAlign: 'center', padding: '3rem', color: '#888' }}>
                                    회원정보를 불러오는 중...
                                </div>
                            ) : error ? (
                                <div style={{ textAlign: 'center', padding: '3rem', color: '#e53e3e' }}>
                                    {error}
                                </div>
                            ) : (
                                <div className="info-list-full">
                                    <div className="info-row-full">
                                        <div className="row-icon-circle"><User size={20} /></div>
                                        <div className="row-content">
                                            <span className="row-label">이름</span>
                                            <span className="row-value">{userData.name || '-'}</span>
                                        </div>
                                    </div>
                                    <div className="info-row-full">
                                        <div className="row-icon-circle"><Mail size={20} /></div>
                                        <div className="row-content">
                                            <span className="row-label">이메일</span>
                                            <span className="row-value">{userData.email || '-'}</span>
                                        </div>
                                    </div>
                                    <div className="info-row-full">
                                        <div className="row-icon-circle"><Lock size={20} /></div>
                                        <div className="row-content">
                                            <span className="row-label">비밀번호</span>
                                            <span className="row-value">********</span>
                                        </div>
                                        <button className="small-action-btn" onClick={handlePasswordReset}>재설정하기</button>
                                    </div>
                                </div>
                            )}
                        </section>
                        <button className="withdraw-link" onClick={handleWithdraw}>회원탈퇴</button>
                    </div>
                </main>
            </div>

            <footer className="landing-footer">
                <p>© 2026 HearBe. All rights reserved.</p>
            </footer>
        </div>
    );
}
