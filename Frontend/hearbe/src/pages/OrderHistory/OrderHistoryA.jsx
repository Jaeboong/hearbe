import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Home, LogOut, Package } from 'lucide-react';
import logoA from '../../assets/logoA.png';
import { orderAPI } from '../../services/orderAPI';
import { authAPI } from '../../services/authAPI';
import './OrderHistoryA.css';

const OrderHistoryA = () => {
    const navigate = useNavigate();
    const location = useLocation();

    // 상태 관리
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

    const menuItems = [
        { id: 'profile', label: '회원 정보', path: '/A/member-info' },
        { id: 'orders', label: '주문 내역', path: '/A/order-history' },
        { id: 'wishlist', label: '찜한 상품', path: '/A/wishlist' },
        { id: 'cart', label: '장바구니', path: '/A/cart' },
        { id: 'card', label: <>장애인 복지<br />카드 변경</>, path: '/A/card-management' }
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
            navigate('/main');
        }
    };

    // API 호출
    useEffect(() => {
        const fetchOrders = async () => {
            try {
                setIsLoading(true);
                setError(null);
                const response = await orderAPI.getOrders();

                if (response.data && response.data.orders) {
                    const groupedByMall = {};

                    response.data.orders.forEach(order => {
                        const mallName = platformNames[order.platform_id] || `Platform ${order.platform_id}`;

                        if (!groupedByMall[mallName]) {
                            groupedByMall[mallName] = [];
                        }

                        // 날짜순 정렬을 위해 주문 데이터 구성
                        groupedByMall[mallName].push({
                            orderId: order.order_id,
                            datetime: order.ordered_at,
                            orderUrl: order.order_url,
                            items: order.items.map(item => ({
                                id: `${order.order_id}-${item.name}`,
                                image: item.img_url || 'https://via.placeholder.com/80',
                                name: item.name,
                                price: item.price,
                                quantity: item.quantity,
                                url: item.url,
                                deliverUrl: item.deliver_url
                            }))
                        });
                    });

                    // 각 몰 내부의 주문들을 최신순으로 정렬
                    Object.keys(groupedByMall).forEach(mall => {
                        groupedByMall[mall].sort((a, b) => new Date(b.datetime) - new Date(a.datetime));
                    });

                    setOrderData(groupedByMall);
                }
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

    const handleTrackDelivery = (deliverUrl) => {
        if (deliverUrl) {
            window.open(deliverUrl, '_blank', 'noopener,noreferrer');
        } else {
            Swal.fire({
                icon: 'info',
                text: '배송 조회 정보가 없습니다.',
                confirmButtonText: '확인'
            });
        }
    };

    const handleOrderDetail = (orderUrl) => {
        if (orderUrl) {
            window.open(orderUrl, '_blank', 'noopener,noreferrer');
        } else {
            Swal.fire({
                icon: 'info',
                text: '상세 조회 정보가 없습니다.',
                confirmButtonText: '확인'
            });
        }
    };

    const handleRetry = () => {
        setError(null);
        setIsLoading(true);
        // 다시 트리거
        window.location.reload();
    };

    // 날짜 포맷
    const formatDate = (dateString) => {
        if (!dateString) return '';
        // YYYY-MM-DD -> YYYY.MM.DD 변환
        return dateString.replace(/-/g, '.');
    };

    return (
        <div className="orderhistory-container">
            <img
                src={logoA}
                alt="Logo"
                className="orderhistory-logo-left cursor-pointer"
                onClick={() => navigate('/main')}
            />

            <div className="mypage-topbar">
                <h1 className="mypage-topbar-title">마이페이지</h1>
                <div className="mypage-topbar-actions">
                    <button className="topbar-action cursor-pointer" onClick={() => navigate('/A/mall')}>
                        <Home size={56} />
                        <span>홈</span>
                    </button>
                    <button className="topbar-action cursor-pointer" onClick={handleLogout}>
                        <LogOut size={56} />
                        <span>로그아웃</span>
                    </button>
                </div>
            </div>

            <div className="orderhistory-content">
                {/* Sidebar */}
                <aside className="orderhistory-sidebar">
                    <div className="sidebar-menu-card">
                        <nav className="sidebar-nav">
                            {menuItems.map(item => (
                                <button
                                    key={item.id}
                                    className={`sidebar-item cursor-pointer ${currentPath === item.path ? 'active' : ''}`}
                                    onClick={() => navigate(item.path)}
                                >
                                    {item.label}
                                </button>
                            ))}
                        </nav>
                    </div>
                </aside>

                {/* Main Content */}
                <main className="orderhistory-main">
                    <div className="content-card">
                        <h2 className="content-title">
                            <Package size={64} color="#FFF064" />
                            주문 내역
                        </h2>

                        {/* 로딩 상태 */}
                        {isLoading && (
                            <div className="loading-state">
                                <div className="spinner"></div>
                                <p>주문 내역을 불러오는 중...</p>
                            </div>
                        )}

                        {/* 에러 상태 */}
                        {!isLoading && error && (
                            <div className="error-state">
                                <p className="error-message">주문 내역을 불러오지 못했습니다.</p>
                                <p className="error-detail">{error}</p>
                                <button className="retry-btn cursor-pointer" onClick={handleRetry}>
                                    다시 시도
                                </button>
                            </div>
                        )}

                        {/* 빈 상태 */}
                        {!isLoading && !error && Object.keys(orderData).length === 0 && (
                            <div className="empty-orders">
                                주문 내역이 없습니다.
                            </div>
                        )}

                        {/* 주문 내역 데이터 (쇼핑몰별 그룹화 + 내부 건별 노출) */}
                        {!isLoading && !error && Object.keys(orderData).length > 0 && (
                            <div className="mall-sections-wrapper">
                                {Object.entries(orderData).map(([mallName, orders]) => (
                                    <div key={mallName} className="mall-section">
                                        <div className="mall-header">
                                            <h3 className="mall-name">{mallName}</h3>
                                        </div>

                                        <div className="orders-list">
                                            {orders.map((group, index) => (
                                                <div key={`${group.orderId}-${index}`} className="order-group">
                                                    <div className="order-date-header">
                                                        {formatDate(group.datetime)}
                                                    </div>

                                                    <div className="order-details">
                                                        <div className="order-items">
                                                            {group.items.map((item, itemIdx) => (
                                                                <div key={`${item.id}-${itemIdx}`} className="order-item">
                                                                    <img
                                                                        src={item.image}
                                                                        alt={item.name}
                                                                        className="order-item-image"
                                                                        onError={(e) => { e.target.src = 'https://via.placeholder.com/80'; }}
                                                                    />
                                                                    <div className="order-item-info">
                                                                        <div className="order-item-name">{item.name}</div>
                                                                        <div className="order-item-meta">
                                                                            {item.price.toLocaleString()}원, {item.quantity}개
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            ))}
                                                        </div>
                                                        <div className="order-actions">
                                                            <button
                                                                className={`track-delivery-btn cursor-pointer ${!group.orderUrl ? 'disabled' : ''}`}
                                                                onClick={() => handleOrderDetail(group.orderUrl)}
                                                                disabled={!group.orderUrl}
                                                            >
                                                                상세 조회
                                                            </button>
                                                            <button
                                                                className={`track-delivery-btn cursor-pointer ${!group.items.some(o => o.deliverUrl) ? 'disabled' : ''}`}
                                                                onClick={() => {
                                                                    const deliverUrl = group.items.find(o => o.deliver_url)?.deliver_url || group.items.find(o => o.deliverUrl)?.deliverUrl;
                                                                    handleTrackDelivery(deliverUrl);
                                                                }}
                                                                disabled={!group.items.some(o => o.deliverUrl || o.deliver_url)}
                                                            >
                                                                배송조회
                                                            </button>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </main>
            </div>

            <footer className="landing-footer-a">
                <p>© 2026 HearBe. All rights reserved.</p>
            </footer>
        </div>
    );
};

export default OrderHistoryA;
