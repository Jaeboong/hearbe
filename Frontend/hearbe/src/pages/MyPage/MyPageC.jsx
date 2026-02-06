import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    ArrowLeft, User, Mail, Lock, ShoppingCart, Heart,
    ShieldCheck, Settings, Package, Home, CheckSquare, Trash2
} from 'lucide-react';
import { useLocation } from 'react-router-dom';
import CartPage from '../Cart/CartC';
import { orderAPI } from '../../services/orderAPI';
import { wishlistAPI } from '../../services/wishlistAPI';
import { memberAPI } from '../../services/memberAPI';
import './MyPageC.css';
import logoC from '../../assets/logoC.png';


export default function MyPage({ onBack, onHome, onCart, onMyPage }) {
    const navigate = useNavigate();
    const location = useLocation();
    // Determine active tab from URL (A형과 동일한 URL 구조)
    const getActiveTabFromPath = () => {
        const path = location.pathname;
        if (path === '/C/order-history') return 'order-history';
        if (path === '/C/wishlist') return 'wishlist';
        if (path === '/C/cart') return 'cart';
        return 'order-history'; // 기본 탭
    };

    const [activeTab, setActiveTab] = useState(getActiveTabFromPath());

    // Update active tab when URL changes
    React.useEffect(() => {
        setActiveTab(getActiveTabFromPath());
    }, [location.pathname]);

    const [userData, setUserData] = useState({
        name: '',
        email: '',
    });

    useEffect(() => {
        const fetchUserInfo = async () => {
            try {
                const response = await memberAPI.getProfile();
                if (response && response.data) {
                    setUserData({
                        name: response.data.name || '사용자',
                        email: response.data.email || '',
                    });
                }
            } catch (err) {
                console.error('Failed to fetch user info:', err);
                // navigate('/C/login'); // 옵션: 로그인 실패시 이동
            }
        };
        fetchUserInfo();
    }, []);

    const sidebarItems = [
        { id: 'member-info', label: '회원 정보', path: '/C/member-info' },
        { id: 'order-history', label: '주문 내역', path: '/C/order-history' },
        { id: 'wishlist', label: '찜한 상품', path: '/C/wishlist' },
        { id: 'cart', label: '장바구니', path: '/C/cart' },
    ];

    // Orders and wishlist state
    const [orders, setOrders] = useState([]);
    const [wishlists, setWishlists] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    // Platform ID to name mapping
    const platformNames = {
        1: '쿠팡',
        2: '네이버',
        3: '11번가',
        4: 'SSG',
        5: 'G마켓',
        6: '컬리'
    };

    // Fetch data when switching tabs
    useEffect(() => {
        if (activeTab === 'order-history') {
            fetchOrders();
        } else if (activeTab === 'wishlist') {
            fetchWishlist();
        }
    }, [activeTab]);

    const fetchOrders = async () => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await orderAPI.getOrders();

            // Transform API response to component format
            if (response.data && response.data.orders) {
                const ordersByMall = {};
                response.data.orders.forEach(order => {
                    const mallName = platformNames[order.platform_id] || `Platform ${order.platform_id}`;
                    if (!ordersByMall[mallName]) {
                        ordersByMall[mallName] = { mall: mallName, items: [] };
                    }
                    // 새 API는 order 안에 items 배열이 있음
                    if (order.items && order.items.length > 0) {
                        order.items.forEach(item => {
                            ordersByMall[mallName].items.push({
                                id: `${order.order_id}-${item.name}`,
                                name: item.name,
                                price: `${item.price.toLocaleString()}원`,
                                quantity: `${item.quantity || 1}개`,
                                date: order.ordered_at || '',
                                icon: '📦'
                            });
                        });
                    }
                });
                setOrders(Object.values(ordersByMall));
            }
        } catch (err) {
            console.error('Failed to fetch orders:', err);
            setError(err.message);
            // 401 에러 시 로그인 페이지로 이동
            if (err.message === '로그인이 필요합니다.') {
                navigate('/C/login');
            }
        } finally {
            setIsLoading(false);
        }
    };

    const fetchWishlist = async () => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await wishlistAPI.getWishlist();

            // Transform API response
            // Assuming response.data or response is the list of wishlist items
            const items = response.data || response || [];

            if (Array.isArray(items)) {
                const wishlistsByMall = {};
                items.forEach(item => {
                    const mallName = item.mallName || platformNames[item.platformId] || '기타 쇼핑몰';
                    if (!wishlistsByMall[mallName]) {
                        wishlistsByMall[mallName] = {
                            mall: mallName,
                            count: 0,
                            items: []
                        };
                    }
                    wishlistsByMall[mallName].items.push({
                        id: item.wishlistId || item.id,
                        name: item.productName || item.name,
                        price: item.price || 0,
                        imgUrl: item.imageUrl || item.imgUrl,
                        icon: '🎁'
                    });
                    wishlistsByMall[mallName].count++;
                });
                setWishlists(Object.values(wishlistsByMall));
            } else {
                setWishlists([]);
            }

        } catch (err) {
            console.error('Failed to fetch wishlist:', err);
            setError(err.message);
            if (err.message === '로그인이 필요합니다.') {
                navigate('/C/login');
            }
        } finally {
            setIsLoading(false);
        }
    };

    // platformName 매핑 (영문 -> 한글)
    const platformDisplayNames = {
        'coupang': '쿠팡',
        'naver': '네이버',
        '11st': '11번가',
        'ssg': 'SSG',
        'gmarket': 'G마켓'
    };

    return (
        <div className="mypage-container">
            {/* Header 섹션 (디자인 통일) */}
            <header className="mall-header-c">
                <div className="header-left-c">
                    <div className="title-area-c" style={{ marginLeft: 0, cursor: 'pointer' }} onClick={() => navigate('/main')}>
                        <img src={logoC} alt="HearBe Logo" style={{ height: '70px', objectFit: 'contain' }} />
                    </div>
                </div>

                <div className="header-right-c">

                    <button className="nav-item-c cursor-pointer" onClick={onHome || (() => navigate('/C/mall'))}>
                        <div className="nav-icon-c"><Home size={24} /></div>
                        <span>홈</span>
                    </button>
                    <button className="nav-item-c cursor-pointer" onClick={() => setActiveTab('cart')} style={activeTab === 'cart' ? { background: '#f5f3ff', color: '#7c3aed', fontWeight: '800' } : {}}>
                        <div className="nav-icon-c"><ShoppingCart size={24} /></div>
                        <span>장바구니</span>
                    </button>
                    <button className="nav-item-c active cursor-pointer" onClick={onMyPage || (() => navigate('/C/member-info'))}> {/* 마이페이지 링크를 /C/member-info로 변경 */}
                        <div className="nav-icon-c"><User size={24} /></div>
                        <span>마이페이지</span>
                    </button>
                </div>
            </header>

            <div className="mypage-layout">
                {/* Sidebar */}
                <aside className="mypage-sidebar">
                    {/* Profile Card in Sidebar */}
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
                                onClick={() => navigate(item.path)} // MyPageC 내부 탭 이동
                                className={`mp-sidebar-item ${activeTab === item.id ? 'active' : ''}`}
                                style={{
                                    display: 'flex',
                                    flexDirection: 'row',
                                    alignItems: 'center',
                                    fontSize: '1.25rem', // 1.85rem -> 1.25rem Adjusted
                                    width: '100%',
                                    padding: '1rem 1.2rem',
                                    color: activeTab === item.id ? '#7c3aed' : '#9ca3af',
                                    background: activeTab === item.id ? 'white' : 'transparent',
                                    border: 'none',
                                    fontWeight: activeTab === item.id ? '800' : '600',
                                    boxShadow: activeTab === item.id ? '0 4px 15px rgba(0, 0, 0, 0.03)' : 'none',
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
                    {/* Dashboard View (Settings Tab) */}
                    {activeTab === 'settings' && (
                        <div className="content-stack">
                            {/* Profile Card Removed from here */}

                            {/* Shopping Management Card */}
                            <section className="dashboard-card">
                                <h3 className="card-title">쇼핑 관리</h3>
                                <div className="quick-links-grid">
                                    <button
                                        className="quick-link-item"
                                        onClick={() => setActiveTab('orders')}
                                        style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem', background: 'transparent', border: 'none', cursor: 'pointer', padding: '1rem' }}
                                    >
                                        <div className="quick-icon-box"><Package size={32} /></div>
                                        <span style={{ fontSize: '1.1rem', fontWeight: '700', color: '#4b5563' }}>주문 내역</span>
                                    </button>
                                    <button
                                        className="quick-link-item"
                                        onClick={() => setActiveTab('wishlist')}
                                        style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem', background: 'transparent', border: 'none', cursor: 'pointer', padding: '1rem' }}
                                    >
                                        <div className="quick-icon-box"><Heart size={32} /></div>
                                        <span style={{ fontSize: '1.1rem', fontWeight: '700', color: '#4b5563' }}>찜한 상품</span>
                                    </button>
                                    <button
                                        className="quick-link-item"
                                        onClick={onCart || (() => navigate('/C/cart'))}
                                        style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem', background: 'transparent', border: 'none', cursor: 'pointer', padding: '1rem' }}
                                    >
                                        <div className="quick-icon-box"><ShoppingCart size={32} /></div>
                                        <span style={{ fontSize: '1.1rem', fontWeight: '700', color: '#4b5563' }}>장바구니</span>
                                    </button>
                                </div>
                            </section>

                            {/* Account Settings Card */}
                            <section className="dashboard-card">
                                <div className="card-header-row">
                                    <ShieldCheck size={24} className="purple-text" />
                                    <h3 className="card-title">회원 정보</h3>
                                </div>
                                <div className="info-list-full">
                                    <div className="info-row-full">
                                        <div className="row-icon-circle"><User size={20} /></div>
                                        <div className="row-content">
                                            <span className="row-label">이름</span>
                                            <span className="row-value">{userData.name}</span>
                                        </div>
                                    </div>
                                    <div className="info-row-full">
                                        <div className="row-icon-circle"><Lock size={20} /></div>
                                        <div className="row-content">
                                            <span className="row-label">비밀번호</span>
                                            <span className="row-value">********</span>
                                        </div>
                                        <button className="small-action-btn cursor-pointer">재설정하기</button>
                                    </div>
                                    <div className="info-row-full">
                                        <div className="row-icon-circle"><Mail size={20} /></div>
                                        <div className="row-content">
                                            <span className="row-label">이메일</span>
                                            <span className="row-value">{userData.email}</span>
                                        </div>
                                    </div>
                                </div>
                            </section>
                            <button className="withdraw-link cursor-pointer">회원탈퇴</button>
                        </div>
                    )}

                    {/* Orders Tab - Refactored Layout */}
                    {activeTab === 'order-history' && (
                        <section className="dashboard-card full-height">
                            <h2 className="card-title-lg">주문내역</h2>
                            <div className="orders-list">
                                {isLoading ? (
                                    <div style={{ textAlign: 'center', padding: '3rem', color: '#888' }}>
                                        주문내역을 불러오는 중...
                                    </div>
                                ) : error ? (
                                    <div style={{ textAlign: 'center', padding: '3rem', color: '#e53e3e' }}>
                                        {error}
                                    </div>
                                ) : orders.length === 0 ? (
                                    <div style={{ textAlign: 'center', padding: '3rem', color: '#888', fontSize: '2rem', fontWeight: 'bold' }}>
                                        주문내역이 없습니다.
                                    </div>
                                ) : (
                                    orders.map((group, idx) => (
                                        <div key={idx} className="mall-order-group">
                                            <div className="mall-order-header">
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                                    <div className="mall-order-indicator"></div>
                                                    <h2 style={{ fontSize: '2rem', fontWeight: '900', margin: 0, color: '#111827' }}>{group.mall}</h2>
                                                </div>
                                                <div className="order-group-actions">
                                                    <button className="btn-outline-sm cursor-pointer">상세 조회</button>
                                                    <button className="btn-fill-sm cursor-pointer">배송 조회</button>
                                                </div>
                                            </div>
                                            <div className="group-items">
                                                {group.items.map((item) => (
                                                    <div key={item.id} className="item-row-card">
                                                        <div className="item-row-left">
                                                            <div className="item-thumb">{item.icon}</div>
                                                            <div className="item-info-text">
                                                                <div className="item-name-lg">{item.name}</div>
                                                            </div>
                                                        </div>
                                                        <div style={{
                                                            fontSize: '1.4rem',
                                                            fontWeight: 'bold',
                                                            color: '#374151',
                                                            whiteSpace: 'nowrap',
                                                            marginRight: '0.5rem'
                                                        }}>
                                                            {item.quantity}
                                                        </div>
                                                        <div className="item-row-actions order-item-actions-container">
                                                            <button className="btn-outline-sm order-item-action-btn cursor-pointer">상품 조회</button>
                                                            <button className="btn-fill-sm order-item-deliver-btn cursor-pointer">배송 조회</button>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </section>
                    )}

                    {/* Wishlist Tab - Refactored Layout */}
                    {activeTab === 'wishlist' && (
                        <section className="dashboard-card full-height">
                            <h2 className="card-title-lg">찜한 상품</h2>
                            <div className="wishlist-content">
                                {isLoading ? (
                                    <div style={{ textAlign: 'center', padding: '3rem', color: '#888' }}>
                                        찜한 상품을 불러오는 중...
                                    </div>
                                ) : error ? (
                                    <div style={{ textAlign: 'center', padding: '3rem', color: '#e53e3e' }}>
                                        {error}
                                    </div>
                                ) : wishlists.length === 0 ? (
                                    <div style={{ width: '100%', display: 'flex', justifyContent: 'center', padding: '3rem', color: '#888', fontSize: '2rem', fontWeight: 'bold' }}>
                                        찜한 상품이 없습니다.
                                    </div>
                                ) : (
                                    wishlists.map((group, idx) => (
                                        <div key={idx} className="mall-wish-group">
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
                                                <div className="mall-order-indicator"></div>
                                                <h3 className="mall-header-text" style={{ marginBottom: 0 }}>{group.mall} <span className="count-badge">{group.count}개</span></h3>
                                            </div>

                                            {/* Selection Toolbar */}
                                            <div className="selection-toolbar">
                                                <button className="check-all-btn cursor-pointer">
                                                    <CheckSquare size={40} /> 전체선택
                                                </button>
                                                <button className="delete-selected-btn cursor-pointer">선택삭제</button>
                                            </div>

                                            <div className="group-items">
                                                {group.items.map((item) => (
                                                    <div key={item.id} className="item-row-card">
                                                        <div className="item-row-left">
                                                            <button className="check-item-btn cursor-pointer"><CheckSquare size={40} color="#ddd" /></button>
                                                            <div className="item-thumb">
                                                                {item.imgUrl ? (
                                                                    <img src={item.imgUrl} alt={item.name} style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '1rem' }} />
                                                                ) : (
                                                                    item.icon
                                                                )}
                                                            </div>
                                                            <div className="item-info-text">
                                                                <div className="item-name-lg">{item.name}</div>
                                                                <div className="item-price-lg">{item.price.toLocaleString()}원</div>
                                                            </div>
                                                        </div>
                                                        <div className="item-row-actions vertical">
                                                            <button className="btn-outline-rounded cursor-pointer">장바구니 담기</button>
                                                            <button className="btn-text-grey cursor-pointer">삭제</button>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </section>
                    )}

                    {/* Cart Tab - Integrated CartPage */}
                    {activeTab === 'cart' && (
                        <section className="dashboard-card full-height" style={{ background: 'transparent', padding: 0, boxShadow: 'none', border: 'none' }}>
                            <CartPage
                                isEmbedded={true}
                                onHome={onHome}
                                onMyPage={() => setActiveTab('settings')}
                            />
                        </section>
                    )}
                </main>
            </div>

            <footer className="landing-footer">
                <p>© 2026 HearBe. All rights reserved.</p>
            </footer>
        </div >
    );
}