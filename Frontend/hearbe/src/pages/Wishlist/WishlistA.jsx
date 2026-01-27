import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import BackButton from '../common/BackButtonA';
import './WishlistA.css';

const WishlistA = () => {
    const navigate = useNavigate();
    const location = useLocation();

    // Sample wishlist data grouped by mall
    const [wishlistData, setWishlistData] = useState({
        '쿠팡': [
            {
                id: 1,
                image: 'https://via.placeholder.com/150',
                date: '2019.05.19',
                name: '아메리칸이글 더블린캔RC 브리스틀GT 로드 2종 자전거',
                price: '72,620원'
            },
            {
                id: 2,
                image: 'https://via.placeholder.com/150',
                date: '2019.05.19',
                name: '아메리칸이글 더블린캔RC 브리스틀GT 로드 2종 자전거',
                price: '72,620원'
            }
        ],
        '11번가': [
            {
                id: 3,
                image: 'https://via.placeholder.com/150',
                date: '2019.05.19',
                name: '미스 코모도 도심형 알루미늄 하이브리드 10.6kg',
                price: '99,000원'
            }
        ],
        'G마켓': [
            {
                id: 4,
                image: 'https://via.placeholder.com/150',
                date: '2019.05.19',
                name: '스티커투스 스티커투 하이브리드/자전거 타우리 700C 21단',
                price: '69,000원'
            }
        ]
    });

    const menuItems = [
        { id: 'profile', label: '회원정보', path: '/mypage/profile' },
        { id: 'orders', label: '주문내역', path: '/mypage/orders' },
        { id: 'cart', label: '장바구니', path: '/cart' },
        { id: 'wishlist', label: '찜한 상품', path: '/mypage/wishlist' },
        { id: 'card', label: '장애인 복지카드 변경', path: '/mypage/card' }
    ];

    const currentPath = location.pathname;

    const handleDeleteAll = (mallName) => {
        setWishlistData(prev => ({
            ...prev,
            [mallName]: []
        }));
    };

    const handleDeleteItem = (mallName, itemId) => {
        setWishlistData(prev => ({
            ...prev,
            [mallName]: prev[mallName].filter(item => item.id !== itemId)
        }));
    };

    const handleAddToCart = (item) => {
        alert(`${item.name}을(를) 장바구니에 담았습니다.`);
    };

    return (
        <div className="wishlist-container">
            <BackButton onClick={() => navigate(-1)} variant="arrow-only" />

            <div className="wishlist-content">
                {/* Sidebar */}
                <aside className="wishlist-sidebar">
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
                <main className="wishlist-main">
                    <h2 className="content-title">찜한 상품</h2>

                    {/* Wishlist by Mall */}
                    {Object.entries(wishlistData).map(([mallName, items]) => (
                        items.length > 0 && (
                            <div key={mallName} className="mall-section">
                                <div className="mall-header">
                                    <h3 className="mall-name">{mallName}</h3>
                                    <button
                                        className="delete-all-btn"
                                        onClick={() => handleDeleteAll(mallName)}
                                    >
                                        선택 상품 관리/삭제
                                    </button>
                                </div>

                                <div className="items-list">
                                    {items.map(item => (
                                        <div key={item.id} className="wishlist-item">
                                            <div className="item-checkbox">
                                                <input type="checkbox" />
                                            </div>
                                            <img src={item.image} alt={item.name} className="item-image" />
                                            <div className="item-details">
                                                <div className="item-date">{item.date}</div>
                                                <div className="item-name">{item.name}</div>
                                                <div className="item-price">{item.price}</div>
                                            </div>
                                            <div className="item-actions">
                                                <button
                                                    className="add-cart-btn"
                                                    onClick={() => handleAddToCart(item)}
                                                >
                                                    장바구니 담기
                                                </button>
                                                <button
                                                    className="delete-btn"
                                                    onClick={() => handleDeleteItem(mallName, item.id)}
                                                >
                                                    삭제
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )
                    ))}

                    {Object.values(wishlistData).every(items => items.length === 0) && (
                        <div className="empty-wishlist">
                            찜한 상품이 없습니다.
                        </div>
                    )}
                </main>
            </div>
        </div>
    );
};

export default WishlistA;
