// API Base URL Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

// API Service for Authentication
export const authAPI = {
    // 회원가입 API
    register: async (userData) => {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/regist`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || '회원가입에 실패했습니다.');
            }

            return data;
        } catch (error) {
            console.error('Register API Error:', error);
            throw error;
        }
    },

    // ID 중복 확인 API (선택사항 - 해당 API가 있다면 사용)
    checkDuplicate: async (userId) => {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/check-duplicate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user_id: userId }),
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Check Duplicate API Error:', error);
            // API가 없으면 기본적으로 사용 가능으로 처리
            return { available: true };
        }
    },

    // 사용자 프로필 조회 API
    getUserProfile: async () => {
        const token = localStorage.getItem('accessToken');

        if (!token) {
            throw new Error('No access token found');
        }

        const response = await fetch(`${API_BASE_URL}/auth/mypage`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                throw new Error('401');
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }
};
