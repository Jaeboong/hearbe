import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import BackButton from '../BackButton/BackButtonA';
import { mallAPI } from '../../services/mallAPI';
import './OrderHistoryA.css';

const OrderHistoryA = () => {
    const navigate = useNavigate();
    const location = useLocation();

    // Order data state
    const [orderData, setOrderData] = useState({});
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    // Platform ID to name mapping
    const platformNames = {
        1: '쿠팡',
        2: '네이버',
        3: '11번가',
        4: 'SSG'
    };

    // Fetch orders on mount
    useEffect(() => {
        const fetchOrders = async () => {
            try {
                setIsLoading(true);
                setError(null);
                const response = await mallAPI.getMyOrders();

                // Transform API response to component format
                const groupedData = {};
                if (response.data && response.data.orders) {
                    response.data.orders.forEach(order => {
                        const platformName = platformNames[order.platform_id] || `Platform ${order.platform_id}`;
                        if (!groupedData[platformName]) {
                            groupedData[platformName] = [];
                        }

                        // Group by date
                        const orderDate = new Date(order.created_at);
                        const datetime = `${orderDate.getFullYear()}.${String(orderDate.getMonth() + 1).padStart(2, '0')}.${String(orderDate.getDate()).padStart(2, '0')} ${String(orderDate.getHours()).padStart(2, '0')}:${String(orderDate.getMinutes()).padStart(2, '0')}`;

                        groupedData[platformName].push({
                            datetime,
                            orders: [{
                                id: order.order_id,
                                image: order.img_url || 'https://via.placeholder.com/80',
                                name: order.product_name || order.name,
                                price: order.price,
                                quantity: order.quantity || 1
                            }]
                        });
                    });
                }
                setOrderData(groupedData);
            } catch (err) {
                console.error('Failed to fetch orders:', err);
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        };

        fetchOrders();
    }, []);

    // Collapsed state for each mall section
    const [collapsedMalls, setCollapsedMalls] = useState({});

    const menuItems = [
        { id: 'profile', label: '회원정보', path: '/A/member-info' },
        { id: 'orders', label: '주문내역', path: '/A/order-history' },
        { id: 'cart', label: '장바구니', path: '/A/cart' },
        { id: 'wishlist', label: '찜한 상품', path: '/A/wishlist' },
        { id: 'card', label: '장애인 복지카드 변경', path: '/A/card-management' }
    ];

    const currentPath = location.pathname;

    const toggleMallSection = (mallName) => {
        setCollapsedMalls(prev => ({
            ...prev,
            [mallName]: !prev[mallName]
        }));
    };

    const handleTrackDelivery = (mallName, datetime) => {
        alert(`${mallName} - ${datetime} 주문의 배송을 조회합니다.`);
    };

    return (
        <div className="orderhistory-container">
            <BackButton onClick={() => navigate(-1)} variant="arrow-only" />

            <div className="orderhistory-content">
                {/* Sidebar */}
                <aside className="orderhistory-sidebar">
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
                <main className="orderhistory-main">
                    <h2 className="content-title">주문내역</h2>

                    {isLoading ? (
                        <div className="empty-orders">
                            주문내역을 불러오는 중...
                        </div>
                    ) : error ? (
                        <div className="empty-orders" style={{ color: '#e53e3e' }}>
                            {error}
                        </div>
                    ) : Object.keys(orderData).length === 0 ? (
                        <div className="empty-orders">
                            주문내역이 없습니다.
                        </div>
                    ) : (
                        <>
                            {/* Orders by Mall */}
                            {Object.entries(orderData).map(([mallName, orderGroups]) => (
                                <div key={mallName} className="mall-section">
                                    <div
                                        className="mall-header"
                                        onClick={() => toggleMallSection(mallName)}
                                    >
                                        <h3 className="mall-name">{mallName}</h3>
                                        <span className="toggle-icon">
                                            {collapsedMalls[mallName] ? '▼' : '▲'}
                                        </span>
                                    </div>

                                    {!collapsedMalls[mallName] && (
                                        <div className="orders-list">
                                            {orderGroups.map((group, index) => (
                                                <div key={index} className="order-group">
                                                    <div className="order-date-header">
                                                        {group.datetime.split(' ')[0]}
                                                    </div>

                                                    <div className="order-details">
                                                        <div className="order-items">
                                                            {group.orders.map(order => (
                                                                <div key={order.id} className="order-item">
                                                                    <img
                                                                        src={order.image}
                                                                        alt={order.name}
                                                                        className="order-item-image"
                                                                    />
                                                                    <div className="order-item-info">
                                                                        <div className="order-item-name">{order.name}</div>
                                                                        <div className="order-item-meta">
                                                                            {order.price.toLocaleString()}원, {order.quantity}개
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            ))}
                                                        </div>
                                                        <button
                                                            className="track-delivery-btn"
                                                            onClick={() => handleTrackDelivery(mallName, group.datetime)}
                                                        >
                                                            배송 조회
                                                        </button>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </>
                    )}
                </main>
            </div>
        </div>
    );
};

export default OrderHistoryA;
