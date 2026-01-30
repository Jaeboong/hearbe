import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Trash2, ShoppingCart, Home, User } from 'lucide-react';
import { cartAPI } from '../../services/cartAPI';
import './CartC.css';

export default function CartPage({ onBack, onClose, onHome, onCart, onMyPage, isEmbedded = false }) {
    const navigate = useNavigate();
    const [cartItems, setCartItems] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    // Platform ID to name mapping (A형과 동일)
    const platformNames = {
        1: '쿠팡',
        2: '네이버',
        3: '11번가',
        4: 'SSG'
    };

    // Fetch cart items on mount
    useEffect(() => {
        const fetchCartItems = async () => {
            try {
                setIsLoading(true);
                setError(null);
                const response = await cartAPI.getCart();

                console.log("-------------------------------");
                console.log("1. 서버 전체 응답:", response);
                console.log("2. 데이터 존재 여부:", !!response.data);
                if (response.data) {
                    console.log("3. items 배열 확인:", response.data.items);
                    console.log("4. items가 배열인가?:", Array.isArray(response.data.items));
                }

                // 1. 응답 구조 확인 (데이터가 어디에 들어있는지 찾기)
                let itemsList = [];
                if (Array.isArray(response)) {
                    itemsList = response;
                } else if (response.data && Array.isArray(response.data.items)) {
                    itemsList = response.data.items;
                } else if (response.data && Array.isArray(response.data)) {
                    itemsList = response.data;
                } else if (response.items && Array.isArray(response.items)) {
                    itemsList = response.items;
                }

                console.log("Found items list:", itemsList);

                // 2. 데이터 변환 (필드명이 달라도 최대한 매핑)
                if (itemsList.length > 0) {
                    const transformedItems = itemsList.map(item => ({
                        id: item.id || item.cart_item_id || item.cartId,
                        name: item.name || item.product_name || '상품명 없음',
                        price: item.price || 0,
                        quantity: item.quantity || 1,
                        image: item.img_url || item.image || item.thumbnail || '📦',
                        mallName: platformNames[item.platform_id] || item.platform_name || item.mall_name || '기타 쇼핑몰',
                    }));
                    setCartItems(transformedItems);
                } else {
                    setCartItems([]);
                }
            } catch (err) {
                console.error('Failed to fetch cart items:', err);
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        };

        fetchCartItems();
    }, []);

    // 쇼핑몰별 그룹화 로직
    const groupedItems = cartItems.reduce((acc, item) => {
        if (!acc[item.mallName]) acc[item.mallName] = [];
        acc[item.mallName].push(item);
        return acc;
    }, {});

    const handleRemoveItem = async (id) => {
        try {
            await cartAPI.deleteCart(id);
            // API 호출 성공 시 로컬 상태 업데이트
            setCartItems(items => items.filter(item => item.id !== id));
        } catch (err) {
            console.error('Failed to delete cart item:', err);
            alert(err.message || '상품 삭제에 실패했습니다.');
        }
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
                    {isLoading ? (
                        <div className="empty-cart">
                            <p>장바구니를 불러오는 중...</p>
                        </div>
                    ) : error ? (
                        <div className="empty-cart">
                            <p style={{ color: '#e53e3e' }}>{error}</p>
                        </div>
                    ) : cartItems.length === 0 ? (
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