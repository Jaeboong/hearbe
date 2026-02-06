import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Store, Package, LogOut } from 'lucide-react';
import { orderAPI } from '../../services/orderAPI';
import { authAPI } from '../../services/authAPI';
import '../MyPage/MyPageC.css';
import './OrderHistoryC.css';
import logoC from '../../assets/logoC.png';

export default function OrderHistoryC({ onHome }) {
    const navigate = useNavigate();

    const [userData, setUserData] = useState({
        name: '',
        email: '',
    });

    // localStorage에서 사용자 정보 로드
    useEffect(() => {
        const userName = localStorage.getItem('user_name');
        setUserData({
            name: userName || '회원',
            email: '',
        });
    }, []);

    // 사이드바 아이템
    const sidebarItems = [
        { id: 'member-info', label: '회원 정보', path: '/C/member-info' },
        { id: 'order-history', label: '주문 내역', path: '/C/order-history' },
        { id: 'wishlist', label: '찜한 상품', path: '/C/wishlist' },
        { id: 'cart', label: '장바구니', path: '/C/cart' },
    ];

    // Orders state
    const [orders, setOrders] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    // Platform ID to name mapping
    const platformNames = {
        1: '쿠팡',
        2: '네이버',
        3: '11번가',
        4: 'SSG',
        5: 'G마켓',
        6: '컬리'
    };

    const resolvePlatformName = (order) => {
        return (
            platformNames[order.platform_id] ||
            order.platform_name ||
            order.platformName ||
            order.mall_name ||
            order.mallName ||
            (order.platform_id ? `플랫폼 ${order.platform_id}` : '기타 쇼핑몰')
        );
    };

    const formatOrderDate = (orderedAt) => {
        if (!orderedAt) return '날짜 미상';
        if (orderedAt.includes('T')) return orderedAt.split('T')[0];
        if (orderedAt.includes(' ')) return orderedAt.split(' ')[0];
        return orderedAt;
    };

    const getOrderDetailUrl = (group) => {
        if (!group.orderUrls || group.orderUrls.length === 0) return '';
        return group.orderUrls[0];
    };

    useEffect(() => {
        fetchOrders();
    }, []);

    const handleLogout = async () => {
        try {
            await authAPI.logout();
            navigate('/main');
        } catch (error) {
            console.error('Logout failed:', error);
            localStorage.removeItem('accessToken');
            localStorage.removeItem('user_id');
            localStorage.removeItem('username');
            navigate('/main');
        }
    };

    async function fetchOrders() {
        try {
            setIsLoading(true);
            setError(null);
            const response = await orderAPI.getOrders();

            if (response.data && response.data.orders) {
                const ordersByDate = {};
                response.data.orders.forEach(order => {
                    const dateKey = formatOrderDate(order.ordered_at);
                    const mallName = resolvePlatformName(order);

                    if (!ordersByDate[dateKey]) {
                        ordersByDate[dateKey] = {
                            date: dateKey,
                            platforms: {}
                        };
                    }

                    if (!ordersByDate[dateKey].platforms[mallName]) {
                        ordersByDate[dateKey].platforms[mallName] = {
                            mall: mallName,
                            orderUrls: [],
                            items: []
                        };
                    }

                    if (order.order_url) {
                        ordersByDate[dateKey].platforms[mallName].orderUrls.push(order.order_url);
                    }

                    if (order.items && order.items.length > 0) {
                        order.items.forEach(item => {
                            ordersByDate[dateKey].platforms[mallName].items.push({
                                id: `${order.order_id}-${item.name}-${item.url || ''}`,
                                name: item.name,
                                price: `${item.price.toLocaleString()}원`,
                                quantity: `${(item.quantity || 1)}개`,
                                date: order.ordered_at || '',
                                mall: mallName,
                                icon: '📦',
                                imgUrl: item.img_url,
                                productUrl: item.url,
                                deliverUrl: item.deliver_url
                            });
                        });
                    }
                });

                const sortedGroups = Object.values(ordersByDate).map(dateGroup => ({
                    date: dateGroup.date,
                    platformGroups: Object.values(dateGroup.platforms)
                })).sort((a, b) => {
                    if (a.date === '날짜 미상') return 1;
                    if (b.date === '날짜 미상') return -1;
                    return new Date(b.date) - new Date(a.date);
                });

                setOrders(sortedGroups);
            }
        } catch (err) {
            console.error('Failed to fetch orders:', err);
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="mypage-container">
            {/* Header */}
            <header className="mall-header-c">
                <div className="header-left-c">
                    <div className="title-area-c" style={{ marginLeft: 0, cursor: 'pointer' }} onClick={() => navigate('/main')}>
                        <img src={logoC} alt="HearBe Logo" style={{ height: '70px', objectFit: 'contain' }} />
                    </div>
                </div>

                <div className="header-right-c">
                    <button className="nav-item-c cursor-pointer" onClick={onHome || (() => navigate('/C/mall'))}>
                        <div className="nav-icon-c"><Store size={24} /></div>
                        <span>쇼핑몰</span>
                    </button>
                    <button className="nav-item-c cursor-pointer" onClick={handleLogout}>
                        <div className="nav-icon-c"><LogOut size={24} /></div>
                        <span>로그아웃</span>
                    </button>
                </div>
            </header>

            <div className="mypage-layout">
                {/* Sidebar */}
                <aside className="mypage-sidebar">
                    <div className="sidebar-profile-card">
                        <div className="sidebar-avatar">
                            <User size={40} color="#7c3aed" />
                        </div>
                        <div className="sidebar-profile-info">
                            <h2 className="sidebar-name">{userData.name}님</h2>
                            <span className="sidebar-badge">hearbe 회원</span>
                        </div>
                        <p className="sidebar-welcome">오늘도 즐거운 쇼핑 되세요!</p>
                    </div>

                    <div className="sidebar-menu-list">
                        {sidebarItems.map((item) => (
                            <button
                                key={item.id}
                                onClick={() => navigate(item.path)}
                                className={`mp-sidebar-item cursor-pointer ${item.id === 'order-history' ? 'active' : ''}`}
                            >
                                <span className="label">{item.label}</span>
                            </button>
                        ))}
                    </div>
                </aside>

                {/* Main Content */}
                <main className="mypage-content">
                    <section className="dashboard-card full-height">
                        <div className="oh-content-title-row">
                            <div className="oh-content-title-icon">
                                <Package size={28} />
                            </div>
                            <h2 className="card-title-lg" style={{ marginBottom: 0 }}>주문 내역</h2>
                        </div>
                        <div className="oh-content-body">
                            {isLoading ? (
                                <div className="oh-status-message">
                                    주문 내역을 불러오는 중...
                                </div>
                            ) : error ? (
                                <div className="oh-status-message oh-error">
                                    {error}
                                </div>
                            ) : orders.length === 0 ? (
                                <div className="oh-status-message">
                                    주문 내역이 없습니다.
                                </div>
                            ) : (
                                <div className="orders-list-c">
                                    {orders.map((dateGroup, dateIdx) => (
                                        <div key={dateIdx} className="date-group-c">
                                            {/* Date Header */}
                                            <div className="date-header-c">
                                                <div className="date-indicator-c"></div>
                                                <h3 className="date-title-c">{dateGroup.date} 주문</h3>
                                            </div>

                                            {/* Platform Sections */}
                                            {dateGroup.platformGroups.map((platformGroup, platformIdx) => {
                                                const detailUrl = platformGroup.orderUrls && platformGroup.orderUrls.length > 0 ? platformGroup.orderUrls[0] : '';
                                                return (
                                                    <div key={platformIdx} className="platform-section-c">
                                                        <div className="platform-header-c">
                                                            <div className="platform-name-c">{platformGroup.mall}</div>
                                                            <button
                                                                className="btn-outline-sm cursor-pointer"
                                                                onClick={() => detailUrl && window.open(detailUrl, '_blank')}
                                                                disabled={!detailUrl}
                                                            >
                                                                주문 상세 조회
                                                            </button>
                                                        </div>
                                                        <div className="group-items">
                                                            {platformGroup.items.map((item) => (
                                                                <div key={item.id} className="item-row-card">
                                                                    <div className="item-row-left">
                                                                        <div className="item-thumb">
                                                                            {item.imgUrl ? (
                                                                                <img src={item.imgUrl} alt={item.name} className="order-item-image" />
                                                                            ) : (
                                                                                item.icon
                                                                            )}
                                                                        </div>
                                                                        <div className="oh-item-info">
                                                                            <div className="oh-item-name">{item.name}</div>
                                                                            <div className="oh-item-price">{item.price}</div>
                                                                        </div>
                                                                    </div>
                                                                    <span className="oh-item-qty">{item.quantity}</span>
                                                                    <div className="order-item-actions-container">
                                                                        <button
                                                                            className="btn-outline-sm order-item-action-btn cursor-pointer"
                                                                            onClick={() => item.productUrl && window.open(item.productUrl, '_blank')}
                                                                        >
                                                                            상품 조회
                                                                        </button>
                                                                        <button
                                                                            className="btn-fill-sm order-item-deliver-btn cursor-pointer"
                                                                            onClick={() => item.deliverUrl && window.open(item.deliverUrl, '_blank')}
                                                                            disabled={!item.deliverUrl}
                                                                        >
                                                                            배송 조회
                                                                        </button>
                                                                    </div>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </section>
                </main>
            </div>

            <footer className="landing-footer">
                <p>© 2026 HearBe. All rights reserved.</p>
            </footer>
        </div>
    );
}
