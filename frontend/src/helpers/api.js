const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

async function request(url, method, data, token = null) {
    const settings = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
    };

    if (data) {
        settings.body = JSON.stringify(data);
    }

    if (token !== null) {
        settings.headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, settings);

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Request failed: ${response.status} ${response.statusText}`);
    }

    return await response.json();
}

async function login(email, password) {
    const url = `${API_BASE_URL}/auth/login`;
    return await request(url, 'POST', { email, password });
}

async function register(email, password) {
    const url = `${API_BASE_URL}/auth/register`;
    return await request(url, 'POST', { email, password });
}

export { login, register, request, API_BASE_URL };
