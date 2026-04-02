window.pomodoroApi = (() => {
    async function request(url, options = {}) {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...(options.headers || {}),
            },
            ...options,
        });
        const data = await response.json();

        if (!response.ok) {
            const error = new Error('API request failed');
            error.response = data;
            throw error;
        }

        return data;
    }

    return {
        getState() {
            return request('/api/state');
        },
        saveSettings(payload) {
            return request('/api/settings', {
                method: 'POST',
                body: JSON.stringify(payload),
            });
        },
    };
})();
