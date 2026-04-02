(() => {
    const RING_CIRCUMFERENCE = 2 * Math.PI * 92

    class PomodoroUI {
        constructor(doc = document) {
            this.doc = doc
            this.frameId = null
            this.pendingState = null
            this.renderedState = {}
            this.elements = {
                card: doc.getElementById("app-card"),
                modeLabel: doc.getElementById("mode-label"),
                timerDisplay: doc.getElementById("timer-display"),
                ringProgress: doc.getElementById("ring-progress"),
                primaryAction: doc.getElementById("primary-action"),
                resetAction: doc.getElementById("reset-action"),
                statusMessage: doc.getElementById("status-message"),
                errorMessage: doc.getElementById("error-message"),
                completedCount: doc.getElementById("completed-count"),
                focusedTime: doc.getElementById("focused-time"),
            }

            this.elements.ringProgress.style.strokeDasharray = `${RING_CIRCUMFERENCE}`
            this.elements.ringProgress.style.strokeDashoffset = `${RING_CIRCUMFERENCE}`
        }

        bind({ onPrimaryAction, onReset }) {
            this.elements.primaryAction.addEventListener("click", onPrimaryAction)
            this.elements.resetAction.addEventListener("click", onReset)
        }

        render(state) {
            this.pendingState = state
            if (this.frameId) {
                return
            }

            this.frameId = window.requestAnimationFrame(() => {
                this.frameId = null
                this._commit(this.pendingState)
            })
        }

        _commit(state) {
            const last = this.renderedState
            const modeLabel = window.PomodoroState.MODE_LABELS[state.mode] || "作業中"
            const timerText = formatTime(state.remaining_seconds)
            const statusText = state.loading ? "読み込み中..." : state.status_message
            const primaryLabel = getPrimaryLabel(state.timer_status)
            const focusedTimeText = formatFocusedTime(state.focused_seconds)
            const progressRatio = state.duration_seconds > 0
                ? 1 - state.remaining_seconds / state.duration_seconds
                : 0

            if (last.modeLabel !== modeLabel) {
                this.elements.modeLabel.textContent = modeLabel
            }
            if (last.timerText !== timerText) {
                this.elements.timerDisplay.textContent = timerText
            }
            if (last.statusText !== statusText) {
                this.elements.statusMessage.textContent = statusText
            }
            if (last.primaryLabel !== primaryLabel) {
                this.elements.primaryAction.textContent = primaryLabel
            }
            if (last.completedCount !== state.completed_count) {
                this.elements.completedCount.textContent = String(state.completed_count)
            }
            if (last.focusedTimeText !== focusedTimeText) {
                this.elements.focusedTime.textContent = focusedTimeText
            }

            this.elements.primaryAction.disabled = state.loading
            this.elements.resetAction.disabled = state.loading
            this.elements.card.classList.toggle("is-busy", state.loading)

            const offset = RING_CIRCUMFERENCE * (1 - Math.min(Math.max(progressRatio, 0), 1))
            if (last.ringOffset !== offset) {
                this.elements.ringProgress.style.strokeDashoffset = `${offset}`
            }

            const hasError = Boolean(state.error_message)
            this.elements.errorMessage.hidden = !hasError
            this.elements.errorMessage.textContent = state.error_message

            this.renderedState = {
                modeLabel,
                timerText,
                statusText,
                primaryLabel,
                completedCount: state.completed_count,
                focusedTimeText,
                ringOffset: offset,
            }
        }
    }

    function formatTime(totalSeconds) {
        const minutes = Math.floor(totalSeconds / 60)
        const seconds = totalSeconds % 60
        return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`
    }

    function formatFocusedTime(totalSeconds) {
        const hours = Math.floor(totalSeconds / 3600)
        const minutes = Math.floor((totalSeconds % 3600) / 60)
        if (hours === 0) {
            return `${minutes}分`
        }
        if (minutes === 0) {
            return `${hours}時間`
        }
        return `${hours}時間${minutes}分`
    }

    function getPrimaryLabel(status) {
        if (status === "running") {
            return "一時停止"
        }
        if (status === "paused") {
            return "再開"
        }
        if (status === "finished") {
            return "次へ"
        }
        return "開始"
    }

    function snapshotToState(state, snapshot) {
        return window.PomodoroState.sanitizeState({
            ...state,
            mode: snapshot.mode,
            timer_status: snapshot.status,
            duration_seconds: snapshot.durationSeconds,
            remaining_seconds: snapshot.remainingSeconds,
            end_timestamp: snapshot.endTimestamp,
        })
    }

    function createController() {
        if (!window.PomodoroTimer || !window.PomodoroState || !window.PomodoroApiClient) {
            return
        }

        const store = new window.PomodoroState.PomodoroStateStore()
        const ui = new PomodoroUI()
        const api = new window.PomodoroApiClient()
        const engine = new window.PomodoroTimer()
        let timerId = null
        let handlingCompletion = false

        function syncEngineFromState(state) {
            engine.restore({
                mode: state.mode,
                timer_status: state.timer_status,
                duration_seconds: state.duration_seconds,
                remaining_seconds: state.remaining_seconds,
                end_timestamp: state.end_timestamp,
                status: state.timer_status,
            })
        }

        function replaceState(nextState) {
            const state = store.replace(nextState)
            syncEngineFromState(state)
            return state
        }

        function updateFromSnapshot(snapshot) {
            return replaceState(snapshotToState(store.getState(), snapshot))
        }

        function stopTicker() {
            if (timerId) {
                window.clearInterval(timerId)
                timerId = null
            }
        }

        async function handleCompletion() {
            if (handlingCompletion) {
                return
            }

            handlingCompletion = true
            const state = store.getState()
            replaceState({
                ...state,
                loading: true,
                status_message: "セッションを保存中...",
            })

            try {
                const result = await api.completeSession({
                    mode: state.mode,
                    duration_seconds: state.duration_seconds,
                })

                replaceState({
                    ...store.getState(),
                    ...result.next_state,
                    completed_count: result.today_stats.completed_count,
                    focused_seconds: result.today_stats.focused_seconds,
                    loading: false,
                    error_message: "",
                    end_timestamp: null,
                    status_message: "次のセッションを準備しました",
                })
            } catch (error) {
                const latestState = store.getState()
                const fallbackStats = latestState.mode === "work"
                    ? {
                        completed_count: latestState.completed_count + 1,
                        focused_seconds: latestState.focused_seconds + latestState.duration_seconds,
                    }
                    : {
                        completed_count: latestState.completed_count,
                        focused_seconds: latestState.focused_seconds,
                    }
                const nextMode = window.PomodoroState.getNextMode(
                    latestState.mode,
                    fallbackStats.completed_count,
                    latestState.settings,
                )
                const nextDuration = window.PomodoroState.getDurationSeconds(
                    nextMode,
                    latestState.settings,
                )

                replaceState({
                    ...latestState,
                    mode: nextMode,
                    timer_status: "idle",
                    duration_seconds: nextDuration,
                    remaining_seconds: nextDuration,
                    end_timestamp: null,
                    completed_count: fallbackStats.completed_count,
                    focused_seconds: fallbackStats.focused_seconds,
                    loading: false,
                    error_message: "サーバーに接続できないため、端末内の状態で次のセッションへ進みました。",
                    status_message: "オフラインモード",
                })
            } finally {
                handlingCompletion = false
            }
        }

        function startTicker() {
            if (timerId) {
                return
            }

            timerId = window.setInterval(() => {
                const snapshot = engine.tick()
                updateFromSnapshot(snapshot)
                if (snapshot.status === "finished") {
                    stopTicker()
                    void handleCompletion()
                }
            }, 250)
        }

        store.subscribe((state) => {
            ui.render(state)
            if (state.timer_status === "running") {
                startTicker()
            } else {
                stopTicker()
            }
        })

        ui.bind({
            onPrimaryAction: async () => {
                const state = store.getState()
                if (state.loading) {
                    return
                }

                if (state.timer_status === "running") {
                    updateFromSnapshot(engine.pause())
                    replaceState({
                        ...store.getState(),
                        status_message: "一時停止中",
                    })
                    return
                }

                if (state.timer_status === "paused") {
                    updateFromSnapshot(engine.resume())
                    replaceState({
                        ...store.getState(),
                        error_message: "",
                        status_message: "タイマー進行中",
                    })
                    return
                }

                if (state.timer_status === "finished") {
                    await handleCompletion()
                    return
                }

                updateFromSnapshot(engine.start())
                replaceState({
                    ...store.getState(),
                    error_message: "",
                    status_message: "タイマー進行中",
                })
            },
            onReset: async () => {
                const state = store.getState()
                if (state.loading) {
                    return
                }

                const durationSeconds = window.PomodoroState.getDurationSeconds(
                    state.mode,
                    state.settings,
                )
                const localResetState = window.PomodoroState.sanitizeState({
                    ...state,
                    timer_status: "idle",
                    duration_seconds: durationSeconds,
                    remaining_seconds: durationSeconds,
                    end_timestamp: null,
                    completed_count: 0,
                    focused_seconds: 0,
                    loading: true,
                    error_message: "",
                    status_message: "リセット中...",
                })

                replaceState(localResetState)

                try {
                    const result = await api.resetToday()
                    replaceState({
                        ...localResetState,
                        ...result.state,
                        completed_count: result.today_stats.completed_count,
                        focused_seconds: result.today_stats.focused_seconds,
                        loading: false,
                        error_message: "",
                        status_message: "リセットしました",
                    })
                } catch (error) {
                    replaceState({
                        ...localResetState,
                        loading: false,
                        error_message: "サーバーに接続できないため、端末内の進捗だけをリセットしました。",
                        status_message: "オフラインでリセットしました",
                    })
                }
            },
        })

        const initialState = store.getState()
        syncEngineFromState(initialState)
        ui.render(initialState)
        if (initialState.timer_status === "running") {
            startTicker()
        }

        ;(async () => {
            const current = store.getState()
            replaceState({
                ...current,
                loading: true,
                status_message: "読み込み中...",
            })

            try {
                const remoteState = await api.fetchState()
                const latestState = store.getState()
                const mergedState = ["running", "paused"].includes(latestState.timer_status)
                    ? window.PomodoroState.sanitizeState({
                        ...latestState,
                        completed_count: remoteState.completed_count,
                        focused_seconds: remoteState.focused_seconds,
                        settings: remoteState.settings,
                        loading: false,
                        error_message: "",
                        status_message: "準備完了",
                    })
                    : window.PomodoroState.sanitizeState({
                        ...latestState,
                        ...remoteState,
                        loading: false,
                        error_message: "",
                        status_message: "準備完了",
                    })

                replaceState(mergedState)
            } catch (error) {
                replaceState({
                    ...current,
                    loading: false,
                    error_message: "サーバーに接続できないため、保存済みの状態で続行します。",
                    status_message: "オフラインモード",
                })
            }
        })()
    }

    document.addEventListener("DOMContentLoaded", createController)
    window.PomodoroUI = PomodoroUI
})()
