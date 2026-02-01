import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Home, LogOut, Store } from 'lucide-react';
import BackButton from '../common/BackButtonA';
import { cartAPI } from '../../services/cartAPI';
import { authAPI } from '../../services/authAPI';
import './CartA.css';

const CartA = () => {
    const navigate = useNavigate();
    const location = useLocation();

    // Cart data grouped by mall
    const [cartData, setCartData] = useState({});
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    // Platform ID to name mapping
    const platformNames = {
        1: '쿠팡',
        2: '네이버',
        3: '11번가',
        4: 'SSG'
    };

    // Fetch cart items on component mount
    useEffect(() => {
        const fetchCartItems = async () => {
            try {
                setIsLoading(true);
                setError(null);
                const response = await cartAPI.getCart();

                // Transform API response to grouped format
                const groupedData = {};
                if (response.cart_items) {
                    response.cart_items.forEach(item => {
                        const platformName = platformNames[item.platform_id] || `Platform ${item.platform_id}`;
                        if (!groupedData[platformName]) {
                            groupedData[platformName] = [];
                        }
                        groupedData[platformName].push({
                            id: item.cart_item_id,
                            image: item.img_url || 'https://via.placeholder.com/80',
                            name: item.name,
                            price: item.price,
                            quantity: item.quantity || 1,
                            url: item.url
                        });
                    });
                }
                setCartData(groupedData);
            } catch (err) {
                console.error('Failed to fetch cart items:', err);
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        };

        fetchCartItems();
    }, []);

    const menuItems = [
        { id: 'profile', label: '회원정보', path: '/A/member-info' },
        { id: 'orders', label: '주문내역', path: '/A/order-history' },
        { id: 'cart', label: '장바구니', path: '/A/cart' },
        { id: 'wishlist', label: '찜한 상품', path: '/A/wishlist' },
        { id: 'card', label: '장애인 복지카드 변경', path: '/A/card-management' }
    ];

    const currentPath = location.pathname;

    const handleLogout = async () => {
        try {
            await authAPI.logout();
        } catch (err) {
            console.warn('Logout failed:', err);
        } finally {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('userData');
            localStorage.removeItem('user_id');
            localStorage.removeItem('username');
            window.location.href = 'http://localhost:5173/';
        }
    };

    const handleItemCheckout = item => {
        if (item.url) {
            window.open(item.url, '_blank', 'noopener,noreferrer');
            return;
        }
        alert('결제할 링크가 없습니다.');
    };

    return (
        <div className="cart-container">
            <BackButton onClick={() => navigate('/A/mall')} variant="arrow-only" />

            <div className="mypage-topbar">
                <h1 className="mypage-topbar-title">마이페이지</h1>
                <div className="mypage-topbar-actions">
                    <button className="topbar-action" onClick={() => navigate('/')}
                    >
                        <Home size={72} />
                        <span>홈</span>
                    </button>
                    <button className="topbar-action" onClick={() => navigate('/A/mall')}>
                        <Store size={72} />
                        <span>쇼핑몰</span>
                    </button>
                    <button className="topbar-action" onClick={handleLogout}>
                        <LogOut size={72} />
                        <span>로그아웃</span>
                    </button>
                </div>
            </div>

            <div className="cart-content">
                {/* Sidebar */}
                <aside className="cart-sidebar">
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
                <main className="cart-main">
                    <h2 className="content-title">장바구니</h2>

                    {isLoading && <div className="empty-cart">장바구니를 불러오는 중입니다.</div>}
                    {!isLoading && error && (
                        <div className="empty-cart">{error}</div>
                    )}

                    {/* Cart by Mall */}
                    {Object.entries(cartData).map(([mallName, items]) => (
                        items.length > 0 && (
                            <div key={mallName} className="cart-mall-section">
                                <div className="cart-mall-header">
                                    <h3 className="cart-mall-name">{mallName}</h3>
                                </div>

                                <div className="cart-items-list">
                                    {items.map(item => (
                                        <div key={item.id} className="cart-item">
                                            <img src={item.image} alt={item.name} className="cart-item-image" />
                                            <div className="cart-item-details">
                                                <div className="cart-item-name">{item.name}</div>
                                                <div className="cart-item-price">{item.price.toLocaleString()}원</div>
                                            </div>
                                            <div className="cart-item-actions">
                                                <button
                                                    className="cart-item-pay-btn"
                                                    onClick={() => handleItemCheckout(item)}
                                                >
                                                    결제하기
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )
                    ))}

                    {!isLoading && Object.values(cartData).every(items => items.length === 0) && (
                        <div className="empty-cart">
                            장바구니가 비어있습니다.
                        </div>
                    )}
                </main>
            </div>
        </div>
    );
};

export default CartA;


