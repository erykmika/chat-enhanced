function getApiBaseUrl() {
    // 1) Runtime-injected config (Docker/nginx)
    if (typeof window !== 'undefined' && window.__ENV__ && window.__ENV__.VITE_API_BASE_URL) {
        return window.__ENV__.VITE_API_BASE_URL;
    }

    // 2) Vite dev/build-time env
    if (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_BASE_URL) {
        return import.meta.env.VITE_API_BASE_URL;
    }

    // 3) Fallback for local dev
    return 'http://localhost:5000';
}

const API_BASE_URL = getApiBaseUrl();

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
        throw new Error(
            errorData.error ||
                `Request failed: ${response.status} ${response.statusText}`,
        );
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
