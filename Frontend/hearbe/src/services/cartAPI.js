// API Base URL Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

// Helper function to get auth token
const getAuthToken = () => {
    return localStorage.getItem('accessToken');
};

// Helper function to get username (login ID)
const getUsername = () => {
    return localStorage.getItem('username');
};

// API Service for Cart
export const cartAPI = {
    // 장바구니 목록 조회
    getCartItems: async () => {
        try {
            const token = getAuthToken();
            const username = getUsername();

            if (!token) {
                throw new Error('로그인이 필요합니다.');
            }
            if (!username) {
                throw new Error('사용자 정보를 찾을 수 없습니다.');
            }

            const response = await fetch(`${API_BASE_URL}/cart/${username}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || '장바구니 조회에 실패했습니다.');
            }

            return data;
        } catch (error) {
            console.error('Get Cart Items API Error:', error);
            throw error;
        }
    },

    // 장바구니에 상품 추가
    addToCart: async (itemData) => {
        try {
            const token = getAuthToken();
            if (!token) {
                throw new Error('로그인이 필요합니다.');
            }

            const username = getUsername();
            if (!username) {
                throw new Error('사용자 정보를 찾을 수 없습니다.');
            }

            const payload = {
                ...itemData,
                userId: username // username을 userId 필드로 전송 (백엔드 요구사항에 따라 필드명 조정)
            };

            const response = await fetch(`${API_BASE_URL}/cart`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || '장바구니 추가에 실패했습니다.');
            }

            return data;
        } catch (error) {
            console.error('Add to Cart API Error:', error);
            throw error;
        }
    },
};
