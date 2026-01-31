import React, { useState, useEffect } from 'react';
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

    const handleCheckboxChange = (mallName, itemId) => {
        setSelectedItems(prev => ({
            ...prev,
            [mallName]: {
                ...prev[mallName],
                [itemId]: !prev[mallName]?.[itemId]
            }
        }));
    };

    const handleDeleteItem = async (mallName, itemId) => {
        try {
            await cartAPI.deleteCart(itemId);
            // API 호출 성공 시 로컬 상태 업데이트
            setCartData(prev => ({
                ...prev,
                [mallName]: prev[mallName].filter(item => item.id !== itemId)
            }));
        } catch (err) {
            console.error('Failed to delete cart item:', err);
            alert(err.message || '상품 삭제에 실패했습니다.');
        }
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
        </div>
    );
};

export default CartA;
