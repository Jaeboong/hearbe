import { API_BASE_URL } from '../config';

const getAuthHeader = () => {
    const token = localStorage.getItem('accessToken');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
};

export const memberAPI = {
    // 1. 프로필 조회
    getProfile: async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/members/profile`, {
                method: 'GET',
                headers: {
                    ...getAuthHeader(),
                },
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.message || '프로필 조회 실패');
            return data;
        } catch (error) {
            console.error('getProfile Error:', error);
            throw error;
        }
    },

    // 2. 프로필 수정
    updateProfile: async (profileData) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/members/profile`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    ...getAuthHeader(),
                },
                body: JSON.stringify(profileData),
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.message || '프로필 수정 실패');
            return data;
        } catch (error) {
            console.error('updateProfile Error:', error);
            throw error;
        }
    }
};
