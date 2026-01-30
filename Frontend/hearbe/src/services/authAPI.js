import { X } from "lucide-react";

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

    // 로그인 API
    login: async (credentials) => {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(credentials), // expect { username, password }
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || '로그인에 실패했습니다.');
            }
            return data;
        } catch (error) {
            console.error('Login API Error:', error);
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

            const result = await response.json();

            return {
                available: !result.data, // true(중복)면 false(사용불가) 반환
                message: result.message
            };
        } catch (error) {
            console.error('Check Duplicate API Error:', error);
            // API가 없으면 기본적으로 사용 가능으로 처리
            return { available: true };
        }
    },
};
