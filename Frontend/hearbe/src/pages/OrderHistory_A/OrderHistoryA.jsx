import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import BackButton from '../common/BackButtonA';
import { orderAPI } from '../../services/orderAPI';
import './OrderHistoryA.css';

const OrderHistoryA = () => {
    const navigate = useNavigate();
    const location = useLocation();

    // 상태 관리
    const [orderData, setOrderData] = useState({});
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    // Collapsed state for each mall section
    const [collapsedMalls, setCollapsedMalls] = useState({});

    // Platform ID to name mapping
    const platformNames = {
        1: '쿠팡',
        2: '네이버',
        3: '11번가',
        4: 'SSG'
    };

    const menuItems = [
        { id: 'profile', label: '회원정보', path: '/A/member-info' },
        { id: 'orders', label: '주문내역', path: '/A/order-history' },
        { id: 'cart', label: '장바구니', path: '/A/cart' },
        { id: 'wishlist', label: '찜한 상품', path: '/A/wishlist' },
        { id: 'card', label: '결제카드 변경', path: '/A/card-management' }
    ];

    const currentPath = location.pathname;

    // API 호출
    useEffect(() => {
        const fetchOrders = async () => {
            try {
                setIsLoading(true);
                setError(null);
                const response = await orderAPI.getOrders();

                // 응답 데이터 변환: 플랫폼별로 그룹화
                const groupedData = {};

                if (response.data && response.data.orders) {
                    response.data.orders.forEach(order => {
                        const platformName = platformNames[order.platform_id] || `Platform ${order.platform_id}`;

                        if (!groupedData[platformName]) {
                            groupedData[platformName] = [];
                        }

                        // 같은 날짜의 주문이 있는지 확인
                        const existingGroup = groupedData[platformName].find(
                            g => g.datetime === order.ordered_at
                        );

                        const orderItems = order.items.map(item => ({
                            id: `${order.order_id}-${item.name}`,
                            image: item.img_url || 'https://via.placeholder.com/80',
                            name: item.name,
                            price: item.price,
                            quantity: item.quantity,
                            url: item.url,
                            deliverUrl: item.deliver_url
                        }));

                        if (existingGroup) {
                            // 기존 그룹에 추가
                            existingGroup.orders.push(...orderItems);
                        } else {
                            // 새 그룹 생성
                            groupedData[platformName].push({
                                datetime: order.ordered_at,
                                orderUrl: order.order_url,
                                orderId: order.order_id,
                                orders: orderItems
                            });
                        }
                    });
                }

                setOrderData(groupedData);
            } catch (err) {
                console.error('Failed to fetch orders:', err);
                setError(err.message);

                // 401 에러 시 로그인 페이지로 이동
                if (err.message === '로그인이 필요합니다.') {
                    navigate('/A/login');
                }
            } finally {
                setIsLoading(false);
            }
        };

        fetchOrders();
    }, [navigate]);

    const toggleMallSection = (mallName) => {
        setCollapsedMalls(prev => ({
            ...prev,
            [mallName]: !prev[mallName]
        }));
    };

    const handleTrackDelivery = (deliverUrl) => {
        if (deliverUrl) {
            window.open(deliverUrl, '_blank', 'noopener,noreferrer');
        } else {
            alert('배송 조회 정보가 없습니다.');
        }
    };

    const handleRetry = () => {
        setError(null);
        setIsLoading(true);
        // 재시도 트리거
        window.location.reload();
    };

    // 날짜 포맷팅
    const formatDate = (dateString) => {
        if (!dateString) return '';
        // YYYY-MM-DD 형식을 YYYY.MM.DD 형식으로 변환
        return dateString.replace(/-/g, '.');
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

                    {/* 로딩 상태 */}
                    {isLoading && (
                        <div className="loading-state">
                            <div className="spinner"></div>
                            <p>주문내역을 불러오는 중...</p>
                        </div>
                    )}

                    {/* 에러 상태 */}
                    {!isLoading && error && (
                        <div className="error-state">
                            <p className="error-message">주문내역을 불러오지 못했습니다.</p>
                            <p className="error-detail">{error}</p>
                            <button className="retry-btn" onClick={handleRetry}>
                                다시 시도
                            </button>
                        </div>
                    )}

                    {/* 빈 상태 */}
                    {!isLoading && !error && Object.keys(orderData).length === 0 && (
                        <div className="empty-orders">
                            주문내역이 없습니다.
                        </div>
                    )}

                    {/* 주문내역 데이터 */}
                    {!isLoading && !error && Object.keys(orderData).length > 0 && (
                        <>
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
                                                <div key={`${group.orderId}-${index}`} className="order-group">
                                                    <div className="order-date-header">
                                                        {formatDate(group.datetime)}
                                                    </div>

                                                    <div className="order-details">
                                                        <div className="order-items">
                                                            {group.orders.map((order, orderIndex) => (
                                                                <div key={`${order.id}-${orderIndex}`} className="order-item">
                                                                    <img
                                                                        src={order.image}
                                                                        alt={order.name}
                                                                        className="order-item-image"
                                                                        onError={(e) => {
                                                                            e.target.src = 'https://via.placeholder.com/80';
                                                                        }}
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
                                                            className={`track-delivery-btn ${!group.orders.some(o => o.deliverUrl) ? 'disabled' : ''}`}
                                                            onClick={() => {
                                                                const deliverUrl = group.orders.find(o => o.deliverUrl)?.deliverUrl;
                                                                handleTrackDelivery(deliverUrl);
                                                            }}
                                                            disabled={!group.orders.some(o => o.deliverUrl)}
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
