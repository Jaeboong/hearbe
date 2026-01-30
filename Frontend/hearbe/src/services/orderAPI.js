// 주문내역 API
// A형과 C형에서 공통으로 사용

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

// Helper function to get auth token
const getAuthToken = () => {
    return localStorage.getItem('accessToken');
};

// Helper function to get auth header
const getAuthHeader = () => {
    const token = getAuthToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
};

// 공통 에러 핸들링
const handleResponse = async (response) => {
    if (!response.ok) {
        if (response.status === 401) {
            throw new Error('로그인이 필요합니다.');
        }
        if (response.status === 403) {
            throw new Error('접근 권한이 없습니다.');
        }
        if (response.status === 404) {
            throw new Error('주문내역을 찾을 수 없습니다.');
        }
        if (response.status >= 500) {
            throw new Error('서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
        }
        const data = await response.json().catch(() => ({}));
        throw new Error(data.message || '요청이 실패했습니다.');
    }
    return await response.json();
};

// Order API Service
export const orderAPI = {
    /**
     * 주문내역 조회
     * GET /orders/me
     * @returns {Promise<Object>} 주문내역 데이터
     */
    getOrders: async () => {
        const token = getAuthToken();
        if (!token) {
            throw new Error('로그인이 필요합니다.');
        }

        try {
            const response = await fetch(`${API_BASE_URL}/orders/me`, {
                method: 'GET',
                headers: {
                    ...getAuthHeader(),
                },
            });

            return await handleResponse(response);
        } catch (error) {
            // 네트워크 에러 처리
            if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
                throw new Error('네트워크 연결을 확인해주세요.');
            }
            console.error('getOrders API Error:', error);
            throw error;
        }
    },
};
