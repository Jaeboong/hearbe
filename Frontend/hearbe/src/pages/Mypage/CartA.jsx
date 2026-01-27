import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import BackButton from '../common/BackButtonA';
import './CartA.css';

const CartA = () => {
    const navigate = useNavigate();
    const location = useLocation();

    // Cart data grouped by mall
    const [cartData, setCartData] = useState({
        '쿠팡': [
            {
                id: 1,
                image: 'https://via.placeholder.com/80',
                name: '제주삼다수 2L 6개',
                price: 38000,
                quantity: 1
            },
            {
                id: 2,
                image: 'https://via.placeholder.com/80',
                name: 'KF94 마스크 50매',
                price: 24000,
                quantity: 1
            }
        ],
        '11번가': [
            {
                id: 3,
                image: 'https://via.placeholder.com/80',
                name: '농심 백산수 2L 12개',
                price: 12000,
                quantity: 1
            }
        ]
    });

    const menuItems = [
        { id: 'profile', label: '회원정보', path: '/mypage/profile' },
        { id: 'orders', label: '주문내역', path: '/mypage/orders' },
        { id: 'cart', label: '장바구니', path: '/cart' },
        { id: 'wishlist', label: '찜한 상품', path: '/mypage/wishlist' },
        { id: 'card', label: '장애인 복지카드 변경', path: '/mypage/card' }
    ];

    const currentPath = location.pathname;

    const handleQuantityChange = (mallName, itemId, delta) => {
        setCartData(prev => ({
            ...prev,
            [mallName]: prev[mallName].map(item =>
                item.id === itemId
                    ? { ...item, quantity: Math.max(1, item.quantity + delta) }
                    : item
            )
        }));
    };

    const handleDeleteItem = (mallName, itemId) => {
        setCartData(prev => ({
            ...prev,
            [mallName]: prev[mallName].filter(item => item.id !== itemId)
        }));
    };

    const calculateMallTotal = (items) => {
        return items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    };

    const handleCheckout = (mallName, total) => {
        alert(`${mallName}에서 ${total.toLocaleString()}원 결제를 진행합니다.`);
    };

    return (
        <div className="cart-container">
            <BackButton onClick={() => navigate(-1)} variant="arrow-only" />

            <div className="cart-content">
                {/* Sidebar */}
                <aside className="cart-sidebar">
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
                <main className="cart-main">
                    <h2 className="content-title">장바구니</h2>

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
                                            <div className="cart-item-controls">
                                                <div className="quantity-controls">
                                                    <button
                                                        className="quantity-btn"
                                                        onClick={() => handleQuantityChange(mallName, item.id, -1)}
                                                    >
                                                        -
                                                    </button>
                                                    <span className="quantity-value">{item.quantity}</span>
                                                    <button
                                                        className="quantity-btn"
                                                        onClick={() => handleQuantityChange(mallName, item.id, 1)}
                                                    >
                                                        +
                                                    </button>
                                                </div>
                                                <button
                                                    className="cart-delete-btn"
                                                    onClick={() => handleDeleteItem(mallName, item.id)}
                                                >
                                                    삭제
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                {/* Mall Total and Checkout */}
                                <div className="cart-mall-footer">
                                    <button
                                        className="checkout-btn"
                                        onClick={() => handleCheckout(mallName, calculateMallTotal(items))}
                                    >
                                        총 결제예정금액 {calculateMallTotal(items).toLocaleString()}원 결제하기
                                    </button>
                                </div>
                            </div>
                        )
                    ))}

                    {Object.values(cartData).every(items => items.length === 0) && (
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
