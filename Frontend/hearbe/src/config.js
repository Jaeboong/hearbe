/**
 * Central configuration for HearBe Frontend
 */

const config = {
    API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080',
    SOCKET_SERVER_URL: import.meta.env.VITE_SOCKET_SERVER_URL || 'http://localhost:4000',
    DEFAULT_MALL_URL: 'https://m.shopping.naver.com/',
};

export default config;
export const { API_BASE_URL, SOCKET_SERVER_URL, DEFAULT_MALL_URL } = config;
