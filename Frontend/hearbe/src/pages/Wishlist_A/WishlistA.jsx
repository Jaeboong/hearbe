import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import BackButton from '../common/BackButtonA';
import { wishlistAPI } from '../../services/wishlistAPI';
import { cartAPI } from '../../services/cartAPI';
import './WishlistA.css';

const WishlistA = () => {
    const navigate = useNavigate();
    const location = useLocation();

    // 상태 관리
    const [wishlistData, setWishlistData] = useState({});
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    // platformName 매핑 (영문 -> 한글)
    const platformDisplayNames = {
        'coupang': '쿠팡',
        'naver': '네이버',
        '11st': '11번가',
        'ssg': 'SSG',
        'gmarket': 'G마켓'
    };

    const menuItems = [
        { id: 'profile', label: '회원정보', path: '/A/member-info' },
        { id: 'orders', label: '주문내역', path: '/A/order-history' },
        { id: 'cart', label: '장바구니', path: '/A/cart' },
        { id: 'wishlist', label: '찜한 상품', path: '/A/wishlist' },
        { id: 'card', label: '장애인 복지카드 변경', path: '/A/card-management' }
    ];

    const currentPath = location.pathname;

    // API 호출
    useEffect(() => {
        fetchWishlist();
    }, []);

    const fetchWishlist = async () => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await wishlistAPI.getWishlist();

            // 응답 데이터 변환: 플랫폼별로 그룹화
            const groupedData = {};

            if (response.items && response.items.length > 0) {
                response.items.forEach(item => {
                    const platform = platformDisplayNames[item.platformName] || item.platformName;

                    if (!groupedData[platform]) {
                        groupedData[platform] = [];
                    }

                    groupedData[platform].push({
                        id: item.wishlistItemId,
                        image: item.imgUrl || 'https://via.placeholder.com/150',
                        date: item.createdAt ? item.createdAt.split('T')[0].replace(/-/g, '.') : '',
                        name: item.productName,
                        url: item.productUrl,
                        liked: item.liked === 'true'
                    });
                });
            }

            setWishlistData(groupedData);
        } catch (err) {
            console.error('Failed to fetch wishlist:', err);
            setError(err.message);

            // 401 에러 시 로그인 페이지로 이동
            if (err.message === '로그인이 필요합니다.') {
                navigate('/A/login');
            }
        } finally {
            setIsLoading(false);
        }
    };

    const handleDeleteItem = async (mallName, itemId) => {
        try {
            await wishlistAPI.deleteWishlist(itemId);
            setWishlistData(prev => ({
                ...prev,
                [mallName]: prev[mallName].filter(item => item.id !== itemId)
            }));
        } catch (err) {
            console.error('Failed to delete wishlist item:', err);
            alert(err.message || '삭제에 실패했습니다.');
        }
    };

    const handleAddToCart = async (item) => {
        try {
            await cartAPI.addCart({
                productUrl: item.url,
                productName: item.name,
                imgUrl: item.image
            });
            alert(`${item.name}을(를) 장바구니에 담았습니다.`);
        } catch (err) {
            console.error('Failed to add to cart:', err);
            alert(err.message || '장바구니 담기에 실패했습니다.');
        }
    };

    const handleRetry = () => {
        fetchWishlist();
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

                    {/* 로딩 상태 */}
                    {isLoading && (
                        <div className="loading-state">
                            <div className="spinner"></div>
                            <p>찜한 상품을 불러오는 중...</p>
                        </div>
                    )}

                    {/* 에러 상태 */}
                    {!isLoading && error && (
                        <div className="error-state">
                            <p className="error-message">찜한 상품을 불러오지 못했습니다.</p>
                            <p className="error-detail">{error}</p>
                            <button className="retry-btn" onClick={handleRetry}>
                                다시 시도
                            </button>
                        </div>
                    )}

                    {/* 빈 상태 */}
                    {!isLoading && !error && Object.keys(wishlistData).length === 0 && (
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

                    {/* 찜 목록 데이터 */}
                    {!isLoading && !error && Object.keys(wishlistData).length > 0 && (
                        <>
                            {Object.entries(wishlistData).map(([mallName, items]) => (
                                items.length > 0 && (
                                    <div key={mallName} className="mall-section">
                                        <div className="mall-header">
                                            <h3 className="mall-name">{mallName}</h3>
                                        </div>

                                        <div className="items-list">
                                            {items.map(item => (
                                                <div key={item.id} className="wishlist-item">
                                                    <img
                                                        src={item.image}
                                                        alt={item.name}
                                                        className="item-image"
                                                        onError={(e) => {
                                                            e.target.src = 'https://via.placeholder.com/150';
                                                        }}
                                                    />
                                                    <div className="item-details">
                                                        <div className="item-date">{item.date}</div>
                                                        <div className="item-name">{item.name}</div>
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
