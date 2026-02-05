import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Swal from 'sweetalert2';
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
    const [alertState, setAlertState] = useState({
        isOpen: false,
        message: '',
        type: 'success', // 'success' or 'error'
        onConfirm: null
    });

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
                    userId: localStorage.getItem('username') || '',
                    userName: profileData.username || profileData.name || '',
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
                    localStorage.removeItem('username');
                    navigate('/C/login');
                    return;
                }

                // Fallback logic
                const storedUsername = localStorage.getItem('username');
                const storedUser = localStorage.getItem('user');

                let fallbackData = {
                    userId: storedUsername || '',
                    userName: '',
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

                setUserData(fallbackData);
            } finally {
                setIsLoading(false);
            }
        };

        fetchUserProfile();
    }, [navigate]);

    const handlePasswordReset = () => {
        navigate('/C/findPassword');
    };

    // Alert Helper
    const showAlert = (message, type = 'success', onConfirm = null) => {
        setAlertState({
            isOpen: true,
            message,
            type,
            onConfirm
        });
    };

    const handleAlertClose = () => {
        const callback = alertState.onConfirm;
        setAlertState(prev => ({ ...prev, isOpen: false }));
        if (callback) callback();
    };

    // 회원탈퇴 모달 열기
    const handleWithdraw = () => {
        setShowWithdrawModal(true);
        setWithdrawPassword('');
    };

    // 회원탈퇴 모달 닫기
    const handleCloseWithdrawModal = () => {
        setShowWithdrawModal(false);
    };

    // 회원탈퇴 실행
    const handleConfirmWithdraw = async () => {
        if (!withdrawPassword) {
            showAlert("비밀번호를 입력해주세요.", "error");
            return;
        }

        try {
            // Updated to use the post method with password as body
            await authAPI.deleteAccount(withdrawPassword);

            setShowWithdrawModal(false);

            showAlert("회원탈퇴가 완료되었습니다.", "success", () => {
                // Local Storage 정리
                localStorage.removeItem('accessToken');
                localStorage.removeItem('refreshToken');
                localStorage.removeItem('user');
                localStorage.removeItem('username');
                localStorage.removeItem('user_id');
                localStorage.removeItem('user_name');
                localStorage.removeItem('savedLoginId_C');
                localStorage.removeItem('savedLoginPassword_C');

                navigate('/');
            });

        } catch (error) {
            console.error('Delete account failed:', error);
            if (error.message && (error.message.includes('비밀번호') || error.message.includes('password') || error.message.includes('mismatch'))) {
                showAlert("비밀번호가 일치하지 않습니다.", "error");
            } else {
                showAlert("예상치못한 오류가 발생했습니다.", "error");
            }
        } finally {
            setIsWithdrawing(false);
        }
    };

    // DEBUG: Mount log
    useEffect(() => {
        console.log('MemberInfoC Mounted');
    }, []);

    const handleLogout = async () => {
        try {
            await authAPI.logout();
        } catch (error) {
            console.error('Logout failed:', error);
        } finally {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('user');
            localStorage.removeItem('user_id');
            localStorage.removeItem('username');
            navigate('/main');
        }
    };

    return (
        <div className="mypage-container">
            {/* Header - MyPageC와 동일한 구조 */}
            <header className="mall-header-c">
                <div className="header-left-c">
                    <div className="title-area-c" style={{ marginLeft: 0, cursor: 'pointer' }} onClick={() => navigate('/main')}>
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
                            <h2 className="sidebar-name">{userData.userName || userData.userId}님</h2>
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
                    zIndex: 1000,
                    backdropFilter: 'blur(5px)'
                }}>
                    <div style={{
                        backgroundColor: 'white',
                        borderRadius: '1.5rem',
                        padding: '2.5rem',
                        width: '90%',
                        maxWidth: '450px',
                        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.15)',
                        border: '1px solid #f3e8ff',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: '1.5rem'
                    }}>
                        <h3 style={{ fontSize: '1.8rem', fontWeight: '800', color: '#dc2626', margin: 0 }}>회원 탈퇴</h3>

                        <p style={{ fontSize: '1.15rem', color: '#4b5563', lineHeight: '1.6', textAlign: 'center', margin: 0 }}>
                            정말로 탈퇴하시겠습니까?<br />
                            <span style={{ fontSize: '0.95rem', color: '#6b7280' }}>
                                탈퇴 시 모든 정보가 삭제되며 복구할 수 없습니다.<br />
                                본인 확인을 위해 비밀번호를 입력해주세요.
                            </span>
                        </p>

                        <input
                            type="password"
                            value={withdrawPassword}
                            onChange={(e) => setWithdrawPassword(e.target.value)}
                            placeholder="비밀번호 입력"
                            style={{
                                width: '100%',
                                padding: '1rem 1.25rem',
                                borderRadius: '0.75rem',
                                border: '2px solid #e5e7eb',
                                fontSize: '1.1rem',
                                outline: 'none',
                                transition: 'all 0.2s'
                            }}
                            onFocus={(e) => e.target.style.borderColor = '#7c3aed'}
                            onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                        />

                        <div style={{ display: 'flex', gap: '0.75rem', width: '100%' }}>
                            <button
                                onClick={handleCloseWithdrawModal}
                                style={{
                                    flex: 1,
                                    padding: '1rem',
                                    fontSize: '1.1rem',
                                    fontWeight: '700',
                                    border: '2px solid #e5e7eb',
                                    borderRadius: '0.75rem',
                                    backgroundColor: 'white',
                                    color: '#6b7280',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s'
                                }}
                                onMouseOver={(e) => e.target.style.backgroundColor = '#f9fafb'}
                                onMouseOut={(e) => e.target.style.backgroundColor = 'white'}
                            >
                                취소
                            </button>
                            <button
                                onClick={handleConfirmWithdraw}
                                style={{
                                    flex: 1,
                                    padding: '1rem',
                                    fontSize: '1.1rem',
                                    fontWeight: '700',
                                    border: 'none',
                                    borderRadius: '0.75rem',
                                    backgroundColor: '#e53e3e',
                                    color: 'white',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s',
                                    boxShadow: '0 4px 12px rgba(229, 62, 62, 0.3)'
                                }}
                                onMouseOver={(e) => e.target.style.backgroundColor = '#dc2626'}
                                onMouseOut={(e) => e.target.style.backgroundColor = '#e53e3e'}
                            >
                                탈퇴하기
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Custom Alert Modal for C Type */}
            {alertState.isOpen && (
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
                    zIndex: 1100,
                    backdropFilter: 'blur(5px)'
                }}>
                    <div style={{
                        backgroundColor: 'white',
                        borderRadius: '1.5rem',
                        padding: '2.5rem',
                        width: '90%',
                        maxWidth: '400px',
                        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.15)',
                        border: '1px solid #f3e8ff',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: '1.5rem'
                    }}>
                        <h3 style={{
                            fontSize: '1.5rem',
                            fontWeight: '800',
                            color: alertState.type === 'error' ? '#e53e3e' : '#7c3aed',
                            margin: 0
                        }}>
                            {alertState.type === 'error' ? '오류' : '알림'}
                        </h3>

                        <p style={{
                            fontSize: '1.1rem',
                            color: '#4b5563',
                            lineHeight: '1.6',
                            textAlign: 'center',
                            margin: 0,
                            whiteSpace: 'pre-line'
                        }}>
                            {alertState.message}
                        </p>

                        <button
                            onClick={handleAlertClose}
                            style={{
                                width: '100%',
                                padding: '1rem',
                                fontSize: '1.1rem',
                                fontWeight: '700',
                                border: 'none',
                                borderRadius: '0.75rem',
                                backgroundColor: '#7c3aed',
                                color: 'white',
                                cursor: 'pointer',
                                transition: 'all 0.2s',
                                boxShadow: '0 4px 12px rgba(124, 58, 237, 0.3)'
                            }}
                            onMouseOver={(e) => e.target.style.backgroundColor = '#6d28d9'}
                            onMouseOut={(e) => e.target.style.backgroundColor = '#7c3aed'}
                        >
                            확인
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}