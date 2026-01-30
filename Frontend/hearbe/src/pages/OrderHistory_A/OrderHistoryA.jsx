import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import BackButton from '../common/BackButtonA';
import './OrderHistoryA.css';

const OrderHistoryA = () => {
    const navigate = useNavigate();
    const location = useLocation();

    // Order data grouped by mall, then by date+time
    const [orderData] = useState({
        '쿠팡': [
            {
                datetime: '2021.12.24 14:30',
                orders: [
                    {
                        id: 1,
                        image: 'https://via.placeholder.com/80',
                        name: '노비타 물티슈 방문판 마스크... 18,650원, 1개',
                        price: 18650,
                        quantity: 1
                    }
                ]
            },
            {
                datetime: '2021.09.08 11:20',
                orders: [
                    {
                        id: 2,
                        image: 'https://via.placeholder.com/80',
                        name: '무용 비비니스 머서 힐... 18,980원, 1개',
                        price: 18980,
                        quantity: 1
                    }
                ]
            }
        ],
        '네이버': [
            {
                datetime: '2021.11.15 09:45',
                orders: [
                    {
                        id: 3,
                        image: 'https://via.placeholder.com/80',
                        name: '스마트 블루투스 이어폰',
                        price: 45000,
                        quantity: 2
                    },
                    {
                        id: 4,
                        image: 'https://via.placeholder.com/80',
                        name: 'USB-C 충전 케이블',
                        price: 12000,
                        quantity: 1
                    }
                ]
            }
        ]
    });

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

                    {Object.keys(orderData).length === 0 && (
                        <div className="empty-orders">
                            주문내역이 없습니다.
                        </div>
                    )}
                </main>
            </div>
        </div>
    );
};

export default OrderHistoryA;
