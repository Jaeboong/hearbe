import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    ArrowLeft, User, Mail, Lock, ShoppingCart, Heart,
    ShieldCheck, Settings, Package, Home, CheckSquare, Trash2
} from 'lucide-react';
import { useLocation } from 'react-router-dom';
import CartPage from '../Cart/CartC';
import { mallAPI } from '../../services/mallAPI';
import './MyPageC.css';

export default function MyPage({ onBack, onHome, onCart, onMyPage }) {
    const navigate = useNavigate();
    const location = useLocation();
    // Determine active tab from URL
    const getActiveTabFromPath = () => {
        const path = location.pathname;
        if (path === '/C/orders') return 'orders';
        if (path === '/C/wishlist') return 'wishlist';
        if (path === '/C/cart') return 'cart';
        return 'settings'; // default for /C/mypage
    };

    const [activeTab, setActiveTab] = useState(getActiveTabFromPath());

    // Update active tab when URL changes
    React.useEffect(() => {
        setActiveTab(getActiveTabFromPath());
    }, [location.pathname]);

    const [userData] = useState({
        name: '김싸피',
        email: 'kimssafy@ssafy.com',
    });

    const sidebarItems = [
        { id: 'settings', label: '계정 설정', path: '/C/mypage' },
        { id: 'orders', label: '주문내역', path: '/C/orders' },
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
        if (activeTab === 'orders') {
            fetchOrders();
        } else if (activeTab === 'wishlist') {
            fetchWishlist();
        }
    }, [activeTab]);

    const fetchOrders = async () => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await mallAPI.getMyOrders();

            // Transform API response to component format
            const groupedOrders = [];
            if (response.data && response.data.orders) {
                const ordersByMall = {};
                response.data.orders.forEach(order => {
                    const mallName = platformNames[order.platform_id] || `Platform ${order.platform_id}`;
                    if (!ordersByMall[mallName]) {
                        ordersByMall[mallName] = { mall: mallName, items: [] };
                    }
                    ordersByMall[mallName].items.push({
                        id: order.order_id,
                        name: order.product_name || order.name,
                        price: `${order.price.toLocaleString()}원`,
                        quantity: `${order.quantity || 1}개`,
                        date: new Date(order.created_at).toLocaleDateString('ko-KR'),
                        icon: '📦'
                    });
                });
                setOrders(Object.values(ordersByMall));
            }
        } catch (err) {
            console.error('Failed to fetch orders:', err);
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    const fetchWishlist = async () => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await mallAPI.getWishlist();

            // Transform API response to component format
            const groupedWishlist = [];
            if (response.data && response.data.items) {
                const wishlistByMall = {};
                response.data.items.forEach(item => {
                    const mallName = platformNames[item.platform_id] || `Platform ${item.platform_id}`;
                    if (!wishlistByMall[mallName]) {
                        wishlistByMall[mallName] = { mall: mallName, count: 0, items: [] };
                    }
                    wishlistByMall[mallName].items.push({
                        id: item.wishlist_item_id,
                        name: item.name,
                        price: item.price,
                        tag: '',
                        icon: '❤️'
                    });
                    wishlistByMall[mallName].count++;
                });
                setWishlists(Object.values(wishlistByMall));
            }
        } catch (err) {
            console.error('Failed to fetch wishlist:', err);
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="mypage-container">
            {/* Header 섹션 (디자인 통일) */}
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
                    <button className="nav-item-c" onClick={() => setActiveTab('cart')} style={activeTab === 'cart' ? { background: '#f5f3ff', color: '#7c3aed', fontWeight: '800' } : {}}>
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
                                onClick={() => navigate(item.path)}
                                className={`mp-sidebar-item ${activeTab === item.id ? 'active' : ''}`}
                                style={{
                                    display: 'flex',
                                    flexDirection: 'row',
                                    alignItems: 'center',
                                    fontSize: '1.85rem', // User requested EVEN larger size
                                    width: '100%',
                                    padding: '1.4rem 2rem', /* 패딩 추가 확대 */
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
                                        <span style={{ fontSize: '1.1rem', fontWeight: '700', color: '#4b5563' }}>주문내역</span>
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
                                    <h3 className="card-title">계정 설정</h3>
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
                                        <button className="small-action-btn">재설정하기</button>
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
                            <button className="withdraw-link">회원탈퇴</button>
                        </div>
                    )}

                    {/* Orders Tab - Refactored Layout */}
                    {activeTab === 'orders' && (
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
                                    <div style={{ textAlign: 'center', padding: '3rem', color: '#888' }}>
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
                                                    <button className="btn-outline-sm">상세 조회</button>
                                                    <button className="btn-fill-sm">배송 조회</button>
                                                </div>
                                            </div>
                                            <div className="group-items">
                                                {group.items.map((item) => (
                                                    <div key={item.id} className="item-row-card">
                                                        <div className="item-row-left">
                                                            <div className="item-thumb">{item.icon}</div>
                                                            <div className="item-info-text">
                                                                <div className="item-name-lg">{item.name}</div>
                                                                <div className="item-meta-text">{item.date} · {item.quantity}</div>
                                                            </div>
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
                                    <div style={{ textAlign: 'center', padding: '3rem', color: '#888' }}>
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
                                                <button className="check-all-btn">
                                                    <CheckSquare size={40} /> 전체선택
                                                </button>
                                                <button className="delete-selected-btn">선택삭제</button>
                                            </div>

                                            <div className="group-items">
                                                {group.items.map((item) => (
                                                    <div key={item.id} className="item-row-card">
                                                        <div className="item-row-left">
                                                            <button className="check-item-btn"><CheckSquare size={40} color="#ddd" /></button>
                                                            <div className="item-thumb">{item.icon}</div>
                                                            <div className="item-info-text">
                                                                <div className="item-name-lg">{item.name}</div>
                                                                <div className="item-price-lg">{item.price.toLocaleString()}원</div>
                                                            </div>
                                                        </div>
                                                        <div className="item-row-actions vertical">
                                                            <button className="btn-outline-rounded">장바구니 담기</button>
                                                            <button className="btn-text-grey">삭제</button>
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