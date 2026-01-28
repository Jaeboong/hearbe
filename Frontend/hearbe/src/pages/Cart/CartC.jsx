import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Trash2, ShoppingCart, Home, User } from 'lucide-react';
import './CartC.css';

export default function CartPage({ onBack, onClose, onHome, onCart, onMyPage, isEmbedded = false }) {
    const navigate = useNavigate();
    const [cartItems, setCartItems] = useState([
        {
            id: 1,
            name: '무선 블루투스 이어폰',
            price: 45000,
            quantity: 1,
            image: '🎧',
            mallName: '이마트몰',
        },
        {
            id: 2,
            name: '스마트워치',
            price: 89000,
            quantity: 2,
            image: '⌚',
            mallName: '쿠팡',
        },
        {
            id: 3,
            name: 'USB-C 충전 케이블',
            price: 12000,
            quantity: 3,
            image: '🔌',
            mallName: '이마트몰',
        },
    ]);

    // 쇼핑몰별 그룹화 로직
    const groupedItems = cartItems.reduce((acc, item) => {
        if (!acc[item.mallName]) acc[item.mallName] = [];
        acc[item.mallName].push(item);
        return acc;
    }, {});

    const handleRemoveItem = (id) => {
        setCartItems(items => items.filter(item => item.id !== id));
    };

    const totalPrice = cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
    const totalItems = cartItems.reduce((sum, item) => sum + item.quantity, 0);

    return (
        <div className="cart-page-container" style={isEmbedded ? {
            position: 'static',
            width: '100%',
            minHeight: 'auto',
            background: 'transparent',
            padding: 0,
            margin: 0
        } : {
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'flex-start',
            alignItems: 'stretch',
            margin: 0,
            padding: 0,
            background: '#fafafa'
        }}>
            {/* Header 섹션 (디자인 통일) - Embedded 모드에서는 숨김 */}
            {!isEmbedded && (
                <header className="mall-header-c">
                    <div className="header-left-c">
                        <div className="title-area-c" style={{ marginLeft: 0 }}>
                            <div className="title-icon-box-c">
                                <ShoppingCart size={24} />
                            </div>
                            <div className="title-text-c">
                                <h1>장바구니</h1>
                                <span className="subtitle-c">Shopping Cart</span>
                            </div>
                        </div>
                    </div>

                    <div className="header-right-c">
                        <button className="nav-item-c" onClick={onHome || (() => navigate('/'))}>
                            <div className="nav-icon-c"><Home size={24} /></div>
                            <span>홈</span>
                        </button>
                        <button className="nav-item-c active">
                            <div className="nav-icon-c"><ShoppingCart size={24} /></div>
                            <span>장바구니</span>
                        </button>
                        <button className="nav-item-c" onClick={onMyPage || (() => navigate('/C/mypage'))}>
                            <div className="nav-icon-c"><User size={24} /></div>
                            <span>마이페이지</span>
                        </button>
                    </div>
                </header>
            )}

            {/* Main Content */}
            <main className="cart-content" style={isEmbedded ? { padding: 0 } : {}}>
                <div className="cart-list-wrapper" style={isEmbedded ? { marginBottom: 0 } : {}}>
                    {cartItems.length === 0 ? (
                        <div className="empty-cart">
                            <ShoppingCart className="empty-icon" />
                            <p>장바구니가 비어있습니다</p>
                        </div>
                    ) : (
                        Object.entries(groupedItems).map(([mallName, items]) => {
                            const mallTotalPrice = items.reduce((sum, item) => sum + item.price * item.quantity, 0);
                            const mallTotalItems = items.reduce((sum, item) => sum + item.quantity, 0);

                            return (
                                <section key={mallName} className="mall-group">
                                    <div className="mall-header">
                                        <div className="mall-indicator" />
                                        <h2>{mallName}</h2>
                                    </div>

                                    <div className="item-grid">
                                        {items.map(item => (
                                            <div key={item.id} className="cart-item-card">
                                                <div className="item-image-box">
                                                    {item.image}
                                                </div>
                                                <div className="item-info">
                                                    <h3>{item.name}</h3>
                                                    <p className="item-price">{item.price.toLocaleString()}원</p>
                                                </div>
                                                <div className="item-quantity-badge">
                                                    <span className="label">주문 수량</span>
                                                    <span className="count">{item.quantity}개</span>
                                                </div>
                                                <button onClick={() => handleRemoveItem(item.id)} className="delete-button">
                                                    <Trash2 size={18} /> 삭제하기
                                                </button>
                                            </div>
                                        ))}
                                    </div>

                                    <div className="mall-footer">
                                        <div className="mall-summary-detail">
                                            <div className="summary-row">
                                                <span className="summary-label">총 주문 수량 :</span>
                                                <span className="summary-value">{mallTotalItems}개</span>
                                            </div>
                                            <div className="summary-row highlight">
                                                <span className="summary-label">총 결제금액 :</span>
                                                <span className="summary-value price">{mallTotalPrice.toLocaleString()} 원</span>
                                            </div>
                                        </div>
                                        <button className="mall-pay-button" onClick={() => alert(`${mallName} 결제 페이지로 이동합니다.`)}>
                                            <span>{mallName}에서 결제하기</span>
                                            <ArrowLeft className="rotate-180" />
                                        </button>
                                    </div>
                                </section>
                            );
                        })
                    )}
                </div>

                {/* Total Summary Footer Removed */}
            </main>

            {!isEmbedded && (
                <footer className="landing-footer">
                    <p>© 2026 HearBe. All rights reserved.</p>
                </footer>
            )}
        </div>
    );
}