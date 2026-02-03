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

            console.log('Response status:', response.status);
            console.log('Response ok:', response.ok);

            const text = await response.text();
            console.log('Response text:', text);

            let data = {};
            if (text) { // 응답 본문이 있을 경우에만 JSON 파싱 시도
                try { // 백엔드는 201 Created와 함께 ApiResponse 객체를 반환합니다.
                    // data는 { code: 201, message: "회원가입 완료", data: userId } 형태
                    data = text ? JSON.parse(text) : {};
                } catch (e) {
                    console.error('JSON parse error for response text:', e);
                    throw new Error('서버 응답 형식이 올바르지 않습니다. 응답: ' + text);
                }
            }

            if (response.status === 201) { // 백엔드는 201 Created를 반환합니다.
                return { success: true, message: data.message || '회원가입이 완료되었습니다', data: data.data };
            } else { // 201이 아닌 모든 다른 상태 코드 (4xx, 5xx 또는 예상치 못한 2xx)는 실패로 처리
                throw new Error(data.message || `회원가입에 실패했습니다. (상태: ${response.status})`);
            }
        } catch (error) {
            console.error('Register API Error:', error);
            throw error;
        }
    },

    // ID 중복 확인 API
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
<<<<<<< HEAD

            console.log('Check Duplicate Response data:', data);
            
            return data;
=======
            // 백엔드 응답: { code: 200, message: "...", data: true/false }
            // 여기서 data: true는 중복, data: false는 사용 가능을 의미
            // 프론트엔드는 { available: true/false } 형태를 기대하며, available: true가 사용 가능
            // 따라서 백엔드의 data 값을 반전시켜 available로 반환
            // response.ok가 false인 경우 (4xx, 5xx)는 catch 블록에서 처리
            return { available: !data.data };
>>>>>>> 438f06fc602c619edbd98d1b7f7ce94b95068863
        } catch (error) {
            console.error('Check Duplicate API Error:', error);
            throw new Error(error.message || '아이디 중복 확인 중 네트워크 오류가 발생했습니다.'); // 에러를 다시 던짐
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
                // 가입할때의 username도 저장
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
<<<<<<< HEAD
=======
    // 이메일 인증번호 발송 API
    sendEmailVerification: async (email, username = null, name = null) => {
        try {
            const body = { email };
            if (username) body.username = username;
            if (name) body.name = name;

            const response = await fetch(`${API_BASE_URL}/auth/email/send`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.message || '인증번호 발송 실패');
            return data;
        } catch (error) {
            console.error('Send Email Verification Error:', error);
            throw error;
        }
    },

    // 비밀번호 재설정 API (C형 - 이메일 인증)
    resetPassword: async (email, newPassword) => {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/resetPassword`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, newPassword }),
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.message || '비밀번호 재설정 실패');
            return data;
        } catch (error) {
            console.error('Reset Password API Error:', error);
            throw error;
        }
    },

    // 이메일 인증번호 확인 API
    verifyEmailCode: async (email, code) => {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/email/verify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, code }),
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.message || '인증번호 확인 실패');
            return data;
        } catch (error) {
            console.error('Verify Email Code Error:', error);
            throw error;
        }
    },

    // 아이디 찾기 API (C형 - 이메일 인증)
    findId: async (name, email) => {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/findIdByEmail`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email }),
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.message || '아이디 찾기 실패');
            return data;
        } catch (error) {
            console.error('Find ID API Error:', error);
            throw error;
        }
    },
>>>>>>> 438f06fc602c619edbd98d1b7f7ce94b95068863

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
<<<<<<< HEAD
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
    ,
    // 비밀번호 변경(복지카드) API
    resetPasswordBlind: async (welfareCard, newPassword) => {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/resetPasswordBlind`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    welfare_card: welfareCard,
                    new_password: newPassword
                }),
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
                throw new Error(data.message || '비밀번호 변경에 실패했습니다.');
            }

            return data;
        } catch (error) {
            console.error('Reset Password Blind API Error:', error);
            throw error;
        }
    },
    // 복지카드 조회 API
    getWelfareCard: async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/welfare`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
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
                throw new Error(data.message || '복지카드 조회에 실패했습니다.');
            }

            return data;
        } catch (error) {
            console.error('Get Welfare Card API Error:', error);
            throw error;
        }
    },
    // 복지카드 등록/수정 API
    updateWelfareCard: async (welfareCard) => {
        try {
            const response = await fetch(`${API_BASE_URL}/welfare`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(welfareCard),
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
                throw new Error(data.message || '복지카드 저장에 실패했습니다.');
            }

            return data;
        } catch (error) {
            console.error('Update Welfare Card API Error:', error);
            throw error;
        }
    },
    // 복지카드 인증 확인 API
    verifyWelfareCard: async (welfareCard) => {
        try {
            const response = await fetch(`${API_BASE_URL}/welfare/verify`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(welfareCard),
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
                throw new Error(data.message || '복지카드 인증에 실패했습니다.');
            }

            return data;
        } catch (error) {
            console.error('Verify Welfare Card API Error:', error);
            throw error;
=======
>>>>>>> 438f06fc602c619edbd98d1b7f7ce94b95068863
        }
    }
};
