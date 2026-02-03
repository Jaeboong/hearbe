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

            // 응답 상태 확인
            console.log('Response status:', response.status);
            console.log('Response ok:', response.ok);

            // 응답이 비어있거나 204 No Content인 경우
            if (response.status === 204) {
                return { success: true, message: '회원가입이 완료되었습니다' };
            }

            // JSON 파싱 전에 응답 텍스트를 확인
            const text = await response.text();
            console.log('Response text:', text);

            let data;
            try {
                data = text ? JSON.parse(text) : {};
            } catch (e) {
                console.error('JSON parse error:', e);
                throw new Error('서버 응답 형식이 올바르지 않습니다.');
            }

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
            const response = await fetch(`${API_BASE_URL}/auth/checkId`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username: userId }),
            });

            console.log('Check Duplicate Response status:', response.status);

            const data = await response.json();

            console.log('Check Duplicate Response data:', data);
            
            return data;
        } catch (error) {
            console.error('Check Duplicate API Error:', error);
            // API가 없으면 기본적으로 사용 가능으로 처리
            return { available: true };
        }
    },

    // 로그인 API
    login: async (id, password) => {
        try {
            if (typeof id !== 'string' || typeof password !== 'string') {
                throw new Error('로그인 값이 올바르지 않습니다.');
            }
            const username = id.trim();
            const resolvedPassword = password;

            if (!username || !resolvedPassword) {
                throw new Error('로그인 값이 올바르지 않습니다.');
            }

            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password: resolvedPassword }),
            });

            const text = await response.text();
            console.log('Login Response status:', response.status);
            console.log('Login Response text:', text);

            let data;
            try {
                data = text ? JSON.parse(text) : {};
            } catch (e) {
                console.error('JSON parse error:', e);
                throw new Error('서버 응답 형식이 올바르지 않습니다.');
            }

            if (!response.ok) {
                throw new Error(data.message || '로그인에 실패했습니다.');
            }

            // 토큰 받아 사용자 정보 저장 (새로운 응답 구조: accessToken이 data 바로 아래)
            if (data.data && data.data.accessToken) {
                localStorage.setItem('accessToken', data.data.accessToken);
            }
            // user_id 저장
            if (data.data && data.data.id) {
                localStorage.setItem('user_id', data.data.id);
                // 가입할때의 username도 저장(사람구분니 API 호출에서 사용)
                localStorage.setItem('username', username);
            }

            return data;
        } catch (error) {
            console.error('Login API Error:', error);
            throw error;
        }
    },

    // 사용자 프로필 조회 API
    getUserProfile: async () => {
        try {
            const token = localStorage.getItem('accessToken');

            if (!token) {
                throw new Error('로그인이 필요합니다');
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
                    throw new Error('로그인이 필요합니다');
                }
                if (response.status === 403) {
                    throw new Error('접근 권한이 없습니다.');
                }
                if (response.status === 404) {
                    throw new Error('회원정보를 찾을 수 없습니다.');
                }
                if (response.status >= 500) {
                    throw new Error('서버 오류가 발생했습니다.');
                }
                throw new Error('요청이 실패했습니다.');
            }

            return await response.json();
        } catch (error) {
            if (error.message === 'Failed to fetch') {
                throw new Error('네트워크 연결을 확인해주세요.');
            }
            console.error('getUserProfile API Error:', error);
            throw error;
        }
    },

    // 로그아웃 API
    logout: async () => {
        try {
            const token = localStorage.getItem('accessToken');

            if (!token) {
                return { success: true };
            }

            const response = await fetch(`${API_BASE_URL}/auth/logout`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                }
            });

            if (response.status === 204) {
                return { success: true };
            }

            const text = await response.text();
            let data;
            try {
                data = text ? JSON.parse(text) : {};
            } catch (e) {
                console.error('JSON parse error:', e);
                throw new Error('서버 응답 형식이 올바르지 않습니다.');
            }

            if (!response.ok) {
                throw new Error(data.message || '로그아웃에 실패했습니다.');
            }

            return data;
        } catch (error) {
            console.error('Logout API Error:', error);
            throw error;
        } finally {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('savedLoginId');
            localStorage.removeItem('savedLoginPassword');
            localStorage.removeItem('userData');
            localStorage.removeItem('user_id');
            localStorage.removeItem('username');
        }
    }
    ,
    // 아이디 찾기 (복지카드) API
    findIdByWelfareCard: async (welfareCard) => {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/findId`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ welfare_card: welfareCard }),
            });

            const text = await response.text();
            let data;
            try {
                data = text ? JSON.parse(text) : {};
            } catch (e) {
                console.error('JSON parse error:', e);
                throw new Error('서버 응답 형식이 올바르지 않습니다.');
            }

            if (!response.ok) {
                throw new Error(data.message || '아이디 찾기에 실패했습니다.');
            }

            return data;
        } catch (error) {
            console.error('Find ID By Welfare Card API Error:', error);
            throw error;
        }
    }
};
