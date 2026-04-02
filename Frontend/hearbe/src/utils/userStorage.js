
const STORAGE_KEY = 'hearbe_users';

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
