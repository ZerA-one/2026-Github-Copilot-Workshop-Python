(() => {
    class PomodoroApiClient {
        constructor(baseUrl = "") {
            this.baseUrl = baseUrl
        }

        async request(path, options = {}) {
            const requestOptions = {
                method: options.method || "GET",
                headers: {
                    Accept: "application/json",
                    ...(options.body ? { "Content-Type": "application/json" } : {}),
                    ...(options.headers || {}),
                },
                body: options.body ? JSON.stringify(options.body) : undefined,
            }

            let response
            try {
                response = await fetch(`${this.baseUrl}${path}`, requestOptions)
            } catch (error) {
                throw new Error("サーバーへ接続できませんでした。")
            }

            let payload
            try {
                payload = await response.json()
            } catch (error) {
                throw new Error("サーバー応答を解析できませんでした。")
            }

            if (!response.ok || payload.ok === false) {
                throw new Error(payload.error || "API 通信に失敗しました。")
            }

            return payload.data
        }

        fetchState() {
            return this.request("/api/state")
        }

        fetchTodayStats() {
            return this.request("/api/stats/today")
        }

        completeSession(payload) {
            return this.request("/api/session/complete", {
                method: "POST",
                body: payload,
            })
        }

        resetToday() {
            return this.request("/api/session/reset", {
                method: "POST",
            })
        }

        saveSettings(payload) {
            return this.request("/api/settings", {
                method: "POST",
                body: payload,
            })
        }
    }

    window.PomodoroApiClient = PomodoroApiClient
})()
