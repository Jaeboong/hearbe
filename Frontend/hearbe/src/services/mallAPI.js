import { API_BASE_URL } from '../config';

const getAuthHeader = () => {
    const token = localStorage.getItem('auth_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
};

export const mallAPI = {
    // --- 장바구니 (Cart) ---
    getCart: async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/cart`, {
                method: 'GET',
                headers: { ...getAuthHeader() },
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.message || '장바구니 조회 실패');
            return data;
        } catch (error) {
            console.error('getCart Error:', error);
            throw error;
        }
    },

    addCart: async (item) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/cart`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...getAuthHeader(),
                },
                body: JSON.stringify(item),
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.message || '장바구니 추가 실패');
            return data;
        } catch (error) {
            console.error('addCart Error:', error);
            throw error;
        }
    },

    updateCartQuantity: async (cartItemId, quantity) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/cart/${cartItemId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    ...getAuthHeader(),
                },
                body: JSON.stringify({ quantity }),
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.message || '장바구니 수정 실패');
            return data;
        } catch (error) {
            console.error('updateCartQuantity Error:', error);
            throw error;
        }
    },

    deleteCartItem: async (cartItemId) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/cart/${cartItemId}`, {
                method: 'DELETE',
                headers: { ...getAuthHeader() },
            });
            if (!response.ok) throw new Error('장바구니 삭제 실패');
            return true;
        } catch (error) {
            console.error('deleteCartItem Error:', error);
            throw error;
        }
    },

    // --- 찜 (Wishlist) ---
    getWishlist: async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/wishlist`, {
                method: 'GET',
                headers: { ...getAuthHeader() },
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.message || '찜 목록 조회 실패');
            return data;
        } catch (error) {
            console.error('getWishlist Error:', error);
            throw error;
        }
    },

    addWishlist: async (item) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/wishlist`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...getAuthHeader(),
                },
                body: JSON.stringify(item),
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.message || '찜 추가 실패');
            return data;
        } catch (error) {
            console.error('addWishlist Error:', error);
            throw error;
        }
    },

    deleteWishlistItem: async (wishlistItemId) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/wishlist/${wishlistItemId}`, {
                method: 'DELETE',
                headers: { ...getAuthHeader() },
            });
            if (!response.ok) throw new Error('찜 삭제 실패');
            return true;
        } catch (error) {
            console.error('deleteWishlistItem Error:', error);
            throw error;
        }
    },

    // --- 주문 (Orders) ---
    createOrder: async (orderData) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/orders`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...getAuthHeader(),
                },
                body: JSON.stringify(orderData),
            });
            const data = await response.json();
            if (response.status !== 201) throw new Error(data.message || '주문 실패');
            return data;
        } catch (error) {
            console.error('createOrder Error:', error);
            throw error;
        }
    },

    getMyOrders: async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/orders/me`, {
                method: 'GET',
                headers: { ...getAuthHeader() },
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.message || '주문 내역 조회 실패');
            return data;
        } catch (error) {
            console.error('getMyOrders Error:', error);
            throw error;
        }
    }
};
