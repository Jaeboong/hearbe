const STORAGE_KEY = 'hearbe_users';

// 기본 테스트 계정 초기화 함수
const initializeDefaultUser = () => {
    try {
        const users = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
        if (!users.find(u => u.id === 'ssafy')) {
            users.push({ id: 'ssafy', password: '1234', name: '싸피' });
            localStorage.setItem(STORAGE_KEY, JSON.stringify(users));
        }
    } catch (e) {
        console.error("Error initializing default user:", e);
    }
};

// 모듈 로드 시 실행
initializeDefaultUser();

export const saveUser = (user) => {
    try {
        const users = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
        if (users.find(u => u.id === user.id)) {
            return false; // User exists
        }
        users.push(user);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(users));
        return true;
    } catch (e) {
        console.error("Error saving user:", e);
        return false;
    }
};

export const findUser = (id, password) => {
    try {
        const users = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
        return users.find(u => u.id === id && u.password === password);
    } catch (e) {
        console.error("Error finding user:", e);
        return null;
    }
};
