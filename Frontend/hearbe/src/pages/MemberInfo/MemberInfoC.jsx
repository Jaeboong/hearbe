import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Mail, Lock, Home, ShieldCheck, LogOut, X } from 'lucide-react';
import { memberAPI } from '../../services/memberAPI';
import { authAPI } from '../../services/authAPI';
import '../MyPage/MyPageC.css';
import logoC from '../../assets/logoC.png';

export default function MemberInfoC({ onHome }) {
    const navigate = useNavigate();

    const [userData, setUserData] = useState({
        userId: '',   // 아이디 (username)
        userName: '', // 이름 (name)
        email: '',
        phone: '',
    });
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    // 회원탈퇴 모달 상태
    const [showWithdrawModal, setShowWithdrawModal] = useState(false);
    const [withdrawPassword, setWithdrawPassword] = useState('');
    const [withdrawError, setWithdrawError] = useState('');
    const [isWithdrawing, setIsWithdrawing] = useState(false);

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
                    userId: localStorage.getItem('username') || '', // ID from storage (backend does not send it)
                    userName: profileData.username || localStorage.getItem('user_name') || '',   // 백엔드는 username 필드에 이름을 보냄
                    email: profileData.email || '',
                    phone: profileData.phoneNumber || profileData.phone || '',
                });
            } catch (err) {
                console.error('Failed to fetch user profile:', err);
                setError(err.message);

                if (err.message === '로그인이 필요합니다.' || err.message === '접근 권한이 없습니다.') {
                    // 무한 리다이렉트 방지를 위해 자동 이동 제거, 대신 에러 표시
                    // localStorage.removeItem('accessToken'); ...
                    // navigate('/C/login');
                    console.warn('Authentication error:', err.message);
                }

                // API 실패 시 localStorage에서 백업 데이터 로드
                // authAPI stores 'username' directly in localStorage
                const storedUsername = localStorage.getItem('username');
                const storedUser = localStorage.getItem('user'); // Legacy or other source

                let fallbackData = {
                    userId: storedUsername || '',
                    userName: localStorage.getItem('user_name') || '',
                    email: '',
                    phone: ''
                };

                if (storedUser) {
                    try {
                        const parsed = JSON.parse(storedUser);
                        fallbackData.userId = fallbackData.userId || parsed.username || parsed.id || '';
                        fallbackData.userName = parsed.name || parsed.realName || '';
                        fallbackData.email = parsed.email || '';
                        fallbackData.phone = parsed.phone || '';
                    } catch (e) {
                        console.error('Failed to parse stored user data:', e);
                    }
                }

                // 폴백 데이터가 있으면 그것을 보여주고 에러는 콘솔에만
                if (fallbackData.userId) {
                    setUserData(fallbackData);
                    setError(null); // 폴백으로 표시하므로 에러 UI 숨김
                } else {
                    // 폴백도 없으면 에러 표시
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

    // 회원탈퇴 모달 열기
    const handleWithdraw = () => {
        setShowWithdrawModal(true);
        setWithdrawPassword('');
        setWithdrawError('');
    };

    // 회원탈퇴 모달 닫기
    const handleCloseWithdrawModal = () => {
        setShowWithdrawModal(false);
        setWithdrawPassword('');
        setWithdrawError('');
    };

    // 회원탈퇴 실행
    const handleConfirmWithdraw = async () => {
        if (!withdrawPassword) {
            setWithdrawError('비밀번호를 입력해주세요.');
            return;
        }

        setIsWithdrawing(true);
        setWithdrawError('');

        try {
            await authAPI.deleteAccount(withdrawPassword);
            alert('회원탈퇴가 완료되었습니다.');
            navigate('/');
        } catch (error) {
            console.error('Delete account failed:', error);
            setWithdrawError(error.message || '회원탈퇴에 실패했습니다.');
        } finally {
            setIsWithdrawing(false);
        }
    };

    // DEBUG: Mount log
    useEffect(() => {
        console.log('MemberInfoC Mounted');
    }, []);

    const handleLogout = async () => {
        // 1. 선제적 토큰 삭제 (API 에러 여부와 상관없이 즉시 로그아웃 처리)
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        localStorage.removeItem('user_id');
        localStorage.removeItem('username');
        localStorage.removeItem('user_name');

        sessionStorage.removeItem('accessToken');
        sessionStorage.removeItem('refreshToken');
        sessionStorage.removeItem('user');
        sessionStorage.removeItem('user_id');
        sessionStorage.removeItem('username');
        sessionStorage.removeItem('user_name');

        try {
            await authAPI.logout();
        } catch (error) {
            console.error('Logout failed:', error);
        } finally {
            // 한 번 더 확인 사살
            localStorage.clear(); // Auth 관련 외에 다른게 없다면 clear도 방법, 하지만 안전하게 개별 삭제 유지하거나 removeItem 반복
            sessionStorage.clear();

            // 로그인 화면으로 이동
            navigate('/C/login');
        }
    };

    return (
        <div className="mypage-container">
            {/* Header - MyPageC와 동일한 구조 */}
            <header className="mall-header-c">
                <div className="header-left-c">
                    <div className="title-area-c" style={{ marginLeft: 0, cursor: 'pointer' }} onClick={() => navigate('/')}>
                        <img src={logoC} alt="HearBe Logo" style={{ height: '60px', objectFit: 'contain' }} />
                    </div>
                </div>

                <div className="header-right-c">
                    <button className="nav-item-c" onClick={onHome || (() => navigate('/C/mall'))}>
                        <div className="nav-icon-c"><Home size={24} /></div>
                        <span>홈</span>
                    </button>
                    <button className="nav-item-c" onClick={handleLogout}>
                        <div className="nav-icon-c"><LogOut size={24} /></div>
                        <span>로그아웃</span>
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
                            <h2 className="sidebar-name">{userData.userName || '회원'}님</h2>
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
                                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                    <div style={{
                                        width: '50px', height: '50px', borderRadius: '1rem',
                                        backgroundColor: '#f3e8ff', color: '#7c3aed',
                                        display: 'flex', alignItems: 'center', justifyContent: 'center'
                                    }}>
                                        <ShieldCheck size={28} />
                                    </div>
                                    <h2 className="card-title-lg" style={{ marginBottom: 0 }}>회원 정보</h2>
                                </div>
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
                                    <div className="info-row-full" style={{ padding: '0.8rem 0' }}>
                                        <div className="row-icon-circle"><User size={20} /></div>
                                        <div className="row-content">
                                            <span className="row-label" style={{ fontSize: '1.6rem' }}>아이디</span>
                                            <span className="row-value" style={{ fontSize: '1.6rem' }}>{userData.userId || '-'}</span>
                                        </div>
                                    </div>
                                    <div className="info-row-full" style={{ padding: '0.8rem 0' }}>
                                        <div className="row-icon-circle"><Lock size={20} /></div>
                                        <div className="row-content">
                                            <span className="row-label" style={{ fontSize: '1.6rem' }}>비밀번호</span>
                                            <span className="row-value" style={{ fontSize: '1.6rem' }}>********</span>
                                        </div>
                                        <button className="small-action-btn" onClick={handlePasswordReset}>재설정하기</button>
                                    </div>
                                    <div className="info-row-full" style={{ padding: '0.8rem 0' }}>
                                        <div className="row-icon-circle"><User size={20} /></div>
                                        <div className="row-content">
                                            <span className="row-label" style={{ fontSize: '1.6rem' }}>이름</span>
                                            <span className="row-value" style={{ fontSize: '1.6rem' }}>{userData.userName || '-'}</span>
                                        </div>
                                    </div>
                                    <div className="info-row-full" style={{ padding: '0.8rem 0' }}>
                                        <div className="row-icon-circle"><Mail size={20} /></div>
                                        <div className="row-content">
                                            <span className="row-label" style={{ fontSize: '1.6rem' }}>이메일</span>
                                            <span className="row-value" style={{ fontSize: '1.6rem' }}>{userData.email || '-'}</span>
                                        </div>
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

            {/* 회원탈퇴 모달 */}
            {showWithdrawModal && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: 'rgba(0, 0, 0, 0.5)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1000
                }}>
                    <div style={{
                        backgroundColor: 'white',
                        borderRadius: '1.5rem',
                        padding: '2.5rem',
                        width: '90%',
                        maxWidth: '400px',
                        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.15)'
                    }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                            <h3 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#1f2937', margin: 0 }}>회원탈퇴</h3>
                            <button
                                onClick={handleCloseWithdrawModal}
                                style={{
                                    background: 'none',
                                    border: 'none',
                                    cursor: 'pointer',
                                    padding: '0.5rem',
                                    color: '#9ca3af'
                                }}
                            >
                                <X size={24} />
                            </button>
                        </div>

                        <p style={{ fontSize: '1.1rem', color: '#6b7280', marginBottom: '1.5rem', lineHeight: '1.6' }}>
                            회원탈퇴를 진행하시려면 비밀번호를 입력해주세요.
                        </p>

                        <div style={{ marginBottom: '1rem' }}>
                            <input
                                type="password"
                                placeholder="비밀번호 입력"
                                value={withdrawPassword}
                                onChange={(e) => setWithdrawPassword(e.target.value)}
                                style={{
                                    width: '100%',
                                    padding: '1rem 1.2rem',
                                    fontSize: '1.1rem',
                                    border: '2px solid #e5e7eb',
                                    borderRadius: '0.75rem',
                                    outline: 'none',
                                    boxSizing: 'border-box'
                                }}
                                onFocus={(e) => e.target.style.borderColor = '#7c3aed'}
                                onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                            />
                        </div>

                        {withdrawError && (
                            <p style={{ color: '#e53e3e', fontSize: '0.95rem', marginBottom: '1rem' }}>
                                {withdrawError}
                            </p>
                        )}

                        <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1.5rem' }}>
                            <button
                                onClick={handleCloseWithdrawModal}
                                style={{
                                    flex: 1,
                                    padding: '1rem',
                                    fontSize: '1.1rem',
                                    fontWeight: '600',
                                    border: '2px solid #e5e7eb',
                                    borderRadius: '0.75rem',
                                    backgroundColor: 'white',
                                    color: '#6b7280',
                                    cursor: 'pointer'
                                }}
                            >
                                취소
                            </button>
                            <button
                                onClick={handleConfirmWithdraw}
                                disabled={isWithdrawing}
                                style={{
                                    flex: 1,
                                    padding: '1rem',
                                    fontSize: '1.1rem',
                                    fontWeight: '600',
                                    border: 'none',
                                    borderRadius: '0.75rem',
                                    backgroundColor: isWithdrawing ? '#d1d5db' : '#e53e3e',
                                    color: 'white',
                                    cursor: isWithdrawing ? 'not-allowed' : 'pointer'
                                }}
                            >
                                {isWithdrawing ? '처리 중...' : '탈퇴하기'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}