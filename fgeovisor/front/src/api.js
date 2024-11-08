import axios from 'axios';

// Получение статуса авторизации
export const getAuthStatus = async () => {
    return await axios.get('/api/auth-status/');
};

// Логин пользователя
export const login = async (username, password) => {
    return await axios.post('/api/login/', { username, password });
};