import React, { useState, useEffect } from 'react';
<<<<<<< HEAD
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
=======
import { useNavigate, useLocation } from 'react-router-dom';
import BackButton from '../common/BackButtonA';
import { cartAPI } from '../../services/cartAPI';
import './CartA.css';

const CartA = () => {
    const navigate = useNavigate();
    const location = useLocation();

    // Cart data grouped by mall
    const [cartData, setCartData] = useState({});
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    // Checkbox selection state
    const [selectedItems, setSelectedItems] = useState({});

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
                const response = await cartAPI.getCartItems();

                // Transform API response to grouped format
                const groupedData = {};
                if (response.data && response.data.items) {
                    response.data.items.forEach(item => {
                        const platformName = platformNames[item.platform_id] || `Platform ${item.platform_id}`;
                        if (!groupedData[platformName]) {
                            groupedData[platformName] = [];
                        }
                        groupedData[platformName].push({
                            id: item.cart_item_id,
                            image: item.img_url || 'https://via.placeholder.com/80',
                            name: item.name,
                            price: item.price
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
        { id: 'profile', label: '회원정보', path: '/mypage/profile' },
        { id: 'orders', label: '주문내역', path: '/mypage/orders' },
        { id: 'cart', label: '장바구니', path: '/cart' },
        { id: 'wishlist', label: '찜한 상품', path: '/mypage/wishlist' },
        { id: 'card', label: '장애인 복지카드 변경', path: '/mypage/card' }
    ];

    const currentPath = location.pathname;

    const handleCheckboxChange = (mallName, itemId) => {
        setSelectedItems(prev => ({
            ...prev,
            [mallName]: {
                ...prev[mallName],
                [itemId]: !prev[mallName]?.[itemId]
            }
        }));
    };

    const handleDeleteItem = (mallName, itemId) => {
        setCartData(prev => ({
            ...prev,
            [mallName]: prev[mallName].filter(item => item.id !== itemId)
        }));
    };

    const calculateSelectedTotal = (mallName, items) => {
        return items
            .filter(item => selectedItems[mallName]?.[item.id])
            .reduce((sum, item) => sum + item.price, 0);
    };

    const handleCheckout = (mallName, items) => {
        const selectedCount = items.filter(item => selectedItems[mallName]?.[item.id]).length;
        if (selectedCount === 0) {
            alert('결제할 상품을 선택해주세요.');
            return;
        }
        const total = calculateSelectedTotal(mallName, items);
        alert(`${mallName}에서 ${selectedCount}개 상품 ${total.toLocaleString()}원 결제를 진행합니다.`);
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
                                    <button
                                        className="checkout-btn"
                                        onClick={() => handleCheckout(mallName, items)}
                                    >
                                        선택상품 결제하기
                                    </button>
                                </div>

                                <div className="cart-items-list">
                                    {items.map(item => (
                                        <div key={item.id} className="cart-item">
                                            <input
                                                type="checkbox"
                                                className="cart-item-checkbox"
                                                checked={selectedItems[mallName]?.[item.id] || false}
                                                onChange={() => handleCheckboxChange(mallName, item.id)}
                                            />
                                            <img src={item.image} alt={item.name} className="cart-item-image" />
                                            <div className="cart-item-details">
                                                <div className="cart-item-name">{item.name}</div>
                                                <div className="cart-item-price">{item.price.toLocaleString()}원</div>
                                            </div>
                                            <div className="cart-item-controls">
                                                <button
                                                    className="cart-delete-btn"
                                                    onClick={() => handleDeleteItem(mallName, item.id)}
                                                >
                                                </button>
                                            </div>
                                        </div>
                                    ))}
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
>>>>>>> feat/front/login
        </div>
    );
};

<<<<<<< HEAD
export default Cart;
=======
export default CartA;
>>>>>>> feat/front/login
