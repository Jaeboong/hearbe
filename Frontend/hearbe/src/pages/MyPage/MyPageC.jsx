import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    ArrowLeft, User, Mail, Lock, ShoppingCart, Heart,
    ShieldCheck, Settings, Package, Home, CheckSquare, Trash2
} from 'lucide-react';
import { useLocation } from 'react-router-dom';
import CartPage from '../Cart/CartC';
import './MyPageC.css';

export default function MyPage({ onBack, onHome, onCart, onMyPage }) {
    const navigate = useNavigate();
    const location = useLocation();
    const [activeTab, setActiveTab] = useState('settings'); // Default to settings (dashboard)

    // Check for initial tab state
    React.useEffect(() => {
        if (location.state && location.state.activeTab) {
            setActiveTab(location.state.activeTab);
        }
    }, [location.state]);

    const [userData] = useState({
        name: '김싸피',
        email: 'kimssafy@ssafy.com',
    });

    const sidebarItems = [
        { id: 'settings', label: '계정 설정' },
        { id: 'orders', label: '주문내역' },
        { id: 'wishlist', label: '찜한 상품' },
        { id: 'cart', label: '장바구니', onClick: () => setActiveTab('cart') },
    ];

    const orders = [
        {
            mall: '쿠팡',
            items: [
                { id: 1, name: '노이몬 황사 방역용 마스크...', price: '18,650원', quantity: '1개', date: '2021. 12. 24', icon: '😷' },
            ]
        },
        {
            mall: '11번가',
            items: [
                { id: 2, name: '무로 바라나스 마사지 릴...', price: '18,980원', quantity: '1개', date: '2021. 12. 24', icon: '🥖' },
                { id: 3, name: '무로 바라나스 마사지 릴...', price: '18,980원', quantity: '1개', date: '2021. 09. 08', icon: '🥖' }
            ]
        }
    ];

    const wishlists = [
        {
            mall: '쿠팡',
            count: 2,
            items: [
                { id: 101, name: '몽베스트 위드어스 무라벨 생수, 500ml, 40개', price: 19900, tag: '와우 가입 쿠폰', icon: '💧' },
                { id: 102, name: '애니가드 미세먼지 마스크 KF94 100매', price: 34500, icon: '😷' }
            ]
        },
        {
            mall: '이마트몰',
            count: 2,
            items: [
                { id: 201, name: '노브랜드 유기농 아침 우유 900ml', price: 2180, icon: '🥛' },
                { id: 202, name: '피코크 등심 돈까스 600g', price: 8900, icon: '🥩' }
            ]
        }
    ];

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
                                onClick={() => item.onClick ? item.onClick() : setActiveTab(item.id)}
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
                                {orders.map((group, idx) => (
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
                                ))}
                            </div>
                        </section>
                    )}

                    {/* Wishlist Tab - Refactored Layout */}
                    {activeTab === 'wishlist' && (
                        <section className="dashboard-card full-height">
                            <h2 className="card-title-lg">찜한 상품</h2>
                            <div className="wishlist-content">
                                {wishlists.map((group, idx) => (
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
                                ))}
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