import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import BackButton from '../BackButton/BackButtonA';
import { mallAPI } from '../../services/mallAPI';
import './WishlistA.css';

const WishlistA = () => {
    const navigate = useNavigate();
    const location = useLocation();

    // Wishlist data state
    const [wishlistData, setWishlistData] = useState({});
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    // Platform ID to name mapping
    const platformNames = {
        1: '쿠팡',
        2: '네이버',
        3: '11번가',
        4: 'SSG'
    };

    // Fetch wishlist on mount
    useEffect(() => {
        const fetchWishlist = async () => {
            try {
                setIsLoading(true);
                setError(null);
                const response = await mallAPI.getWishlist();

                // Transform API response to component format
                const groupedData = {};
                if (response.data && response.data.items) {
                    response.data.items.forEach(item => {
                        const platformName = platformNames[item.platform_id] || `Platform ${item.platform_id}`;
                        if (!groupedData[platformName]) {
                            groupedData[platformName] = [];
                        }

                        const itemDate = item.created_at ? new Date(item.created_at) : new Date();
                        const formattedDate = `${itemDate.getFullYear()}.${String(itemDate.getMonth() + 1).padStart(2, '0')}.${String(itemDate.getDate()).padStart(2, '0')}`;

                        groupedData[platformName].push({
                            id: item.wishlist_item_id,
                            image: item.img_url || 'https://via.placeholder.com/150',
                            date: formattedDate,
                            name: item.name,
                            price: `${item.price.toLocaleString()}원`
                        });
                    });
                }
                setWishlistData(groupedData);
            } catch (err) {
                console.error('Failed to fetch wishlist:', err);
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        };

        fetchWishlist();
    }, []);

    const menuItems = [
        { id: 'profile', label: '회원정보', path: '/A/member-info' },
        { id: 'orders', label: '주문내역', path: '/A/order-history' },
        { id: 'cart', label: '장바구니', path: '/A/cart' },
        { id: 'wishlist', label: '찜한 상품', path: '/A/wishlist' },
        { id: 'card', label: '장애인 복지카드 변경', path: '/A/card-management' }
    ];

    const currentPath = location.pathname;

    const handleDeleteAll = async (mallName) => {
        if (!window.confirm(`${mallName}의 모든 찜한 상품을 삭제하시겠습니까?`)) return;

        try {
            const items = wishlistData[mallName] || [];
            await Promise.all(items.map(item => mallAPI.deleteWishlistItem(item.id)));
            setWishlistData(prev => ({
                ...prev,
                [mallName]: []
            }));
        } catch (err) {
            alert(err.message || '삭제에 실패했습니다.');
        }
    };

    const handleDeleteItem = async (mallName, itemId) => {
        try {
            await mallAPI.deleteWishlistItem(itemId);
            setWishlistData(prev => ({
                ...prev,
                [mallName]: prev[mallName].filter(item => item.id !== itemId)
            }));
        } catch (err) {
            alert(err.message || '삭제에 실패했습니다.');
        }
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

                    {isLoading ? (
                        <div className="empty-wishlist">
                            찜한 상품을 불러오는 중...
                        </div>
                    ) : error ? (
                        <div className="empty-wishlist" style={{ color: '#e53e3e' }}>
                            {error}
                        </div>
                    ) : Object.keys(wishlistData).length === 0 ? (
                        <div className="empty-wishlist">
                            찜한 상품이 없습니다.
                        </div>
                    ) : (
                        <>
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
                        </>
                    )}
                </main>
            </div>
        </div>
    );
};

export default WishlistA;
