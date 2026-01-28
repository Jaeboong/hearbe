import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './CartA.css';
import BackButton from '../common/BackButtonA';
import iconCard from '../../assets/icon-card.png'; // Generic Icon

const Cart = () => {
    const navigate = useNavigate();
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);

    // Mock API Fetch for Coupang
    useEffect(() => {
        const fetchCoupangData = async () => {
            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 500));

            // Mock Data
            return [
                {
                    id: 'c1',
                    mall: '쿠팡',
                    date: '2025.01.24',
                    name: '아메리칸이글 더블린RC 브리스톨GT 로드 2종 자전거',
                    price: 72620,
                    quantity: 1,
                    image: null
                },
                {
                    id: 'c2',
                    mall: '쿠팡',
                    date: '2025.01.25',
                    name: 'USB-C 고속 충전 케이블 2m 3개입',
                    price: 15900,
                    quantity: 2,
                    image: null
                }
            ];
        };

        const loadCart = async () => {
            // 1. Fetch Coupang
            const coupangItems = await fetchCoupangData();

            // 2. Load Naver from LocalStorage (Simulated)
            const naverItems = JSON.parse(localStorage.getItem('naverCart') || '[]');

            setItems([...coupangItems, ...naverItems]);
            setLoading(false);
        };

        loadCart();
    }, []);

    const handleDelete = (id) => {
        const updatedItems = items.filter(item => item.id !== id);
        setItems(updatedItems);

        // If it was a Naver item, update localStorage too
        const naverItems = updatedItems.filter(item => item.mall === '네이버');
        localStorage.setItem('naverCart', JSON.stringify(naverItems));
    };

    // Calculate Total
    const totalCount = items.length; // Or sum of quantities? User said 'Cart(0)' so items count usually.
    const totalPrice = items.reduce((acc, item) => acc + (item.price * item.quantity), 0);
    const formattedPrice = totalPrice.toLocaleString();

    // Group by Mall
    const groupedItems = items.reduce((groups, item) => {
        if (!groups[item.mall]) groups[item.mall] = [];
        groups[item.mall].push(item);
        return groups;
    }, {});

    return (
        <div className="cart-container">
            <BackButton onClick={() => navigate(-1)} />

            {/* Header */}
            <div className="cart-header">
                <div className="cart-title">장바구니({totalCount})</div>
            </div>

            {/* Empty State */}
            {!loading && items.length === 0 ? (
                <div className="cart-empty-message">
                    장바구니에 담은 상품이 없습니다.
                </div>
            ) : (
                /* List Area */
                <div className="cart-list-area">
                    {Object.keys(groupedItems).map(mallName => (
                        <div key={mallName} className="mall-group">
                            {/* Mall Header */}
                            <div className="mall-header-bar">
                                <div className="mall-name">
                                    <label className="checkbox-container">
                                        <input type="checkbox" defaultChecked />
                                        <span className="cart-checkmark"></span>
                                    </label>
                                    <span style={{ marginLeft: '15px' }}>{mallName}</span>
                                </div>
                                <div className="mall-select-btn">선택 상품 결제하기</div>
                            </div>

                            {/* Items */}
                            {groupedItems[mallName].map(item => (
                                <div key={item.id} className="cart-item-row">
                                    <label className="checkbox-container">
                                        <input type="checkbox" defaultChecked />
                                        <span className="cart-checkmark"></span>
                                    </label>
                                    <div className="item-img-box">
                                        <img src={iconCard} alt="prod" className="item-img" style={{ opacity: 0.3 }} />
                                    </div>
                                    <div className="item-details">
                                        <div className="item-date">{item.date || '2025.01.25'}</div>
                                        <div className="item-name">{item.name}</div>
                                        <div className="item-price-row">
                                            <span>{item.price.toLocaleString()}원</span>
                                            {item.quantity > 1 && (
                                                <span className="item-qty-badge">({item.quantity}개)</span>
                                            )}
                                        </div>
                                    </div>
                                    <button className="row-delete-btn" onClick={() => handleDelete(item.id)}>
                                        X
                                    </button>
                                </div>
                            ))}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Cart;
