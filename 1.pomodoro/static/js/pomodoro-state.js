(() => {
    const STORAGE_KEY = "pomodoro-state-v1"
    const VALID_MODES = new Set(["work", "short_break", "long_break"])
    const VALID_STATUSES = new Set(["idle", "running", "paused", "finished"])

    const DEFAULT_SETTINGS = Object.freeze({
        work_minutes: 25,
        short_break_minutes: 5,
        long_break_minutes: 15,
        cycles_before_long_break: 4,
    })

    const MODE_LABELS = Object.freeze({
        work: "作業中",
        short_break: "短い休憩",
        long_break: "長い休憩",
    })

    function normalizeInteger(value, fallback, min = 0) {
        const parsed = Number.parseInt(value, 10)
        if (Number.isNaN(parsed)) {
            return fallback
        }
        return Math.max(min, parsed)
    }

    function sanitizeSettings(settings = {}) {
        return {
            work_minutes: normalizeInteger(settings.work_minutes, DEFAULT_SETTINGS.work_minutes, 1),
            short_break_minutes: normalizeInteger(settings.short_break_minutes, DEFAULT_SETTINGS.short_break_minutes, 1),
            long_break_minutes: normalizeInteger(settings.long_break_minutes, DEFAULT_SETTINGS.long_break_minutes, 1),
            cycles_before_long_break: normalizeInteger(
                settings.cycles_before_long_break,
                DEFAULT_SETTINGS.cycles_before_long_break,
                1,
            ),
        }
    }

    function getDurationSeconds(mode, settings = DEFAULT_SETTINGS) {
        const normalizedSettings = sanitizeSettings(settings)
        if (mode === "short_break") {
            return normalizedSettings.short_break_minutes * 60
        }
        if (mode === "long_break") {
            return normalizedSettings.long_break_minutes * 60
        }
        return normalizedSettings.work_minutes * 60
    }

    function getNextMode(mode, completedCount, settings = DEFAULT_SETTINGS) {
        const normalizedSettings = sanitizeSettings(settings)
        if (mode === "work") {
            return completedCount > 0 && completedCount % normalizedSettings.cycles_before_long_break === 0
                ? "long_break"
                : "short_break"
        }
        return "work"
    }

    function sanitizeState(candidate = {}) {
        const settings = sanitizeSettings(candidate.settings || {})
        const mode = VALID_MODES.has(candidate.mode) ? candidate.mode : "work"
        const durationSeconds = normalizeInteger(
            candidate.duration_seconds,
            getDurationSeconds(mode, settings),
            1,
        )
        let remainingSeconds = normalizeInteger(
            candidate.remaining_seconds,
            durationSeconds,
            0,
        )
        let timerStatus = VALID_STATUSES.has(candidate.timer_status)
            ? candidate.timer_status
            : "idle"
        let endTimestamp = Number.isFinite(Number(candidate.end_timestamp))
            ? Number(candidate.end_timestamp)
            : null

        if (timerStatus === "running" && endTimestamp) {
            remainingSeconds = Math.max(0, Math.ceil((endTimestamp - Date.now()) / 1000))
            if (remainingSeconds === 0) {
                timerStatus = "finished"
                endTimestamp = null
            }
        }

        if (timerStatus === "idle" && remainingSeconds === 0) {
            remainingSeconds = durationSeconds
        }

        if (timerStatus !== "running") {
            endTimestamp = null
        }

        return {
            mode,
            timer_status: timerStatus,
            duration_seconds: durationSeconds,
            remaining_seconds: remainingSeconds,
            end_timestamp: endTimestamp,
            completed_count: normalizeInteger(candidate.completed_count, 0, 0),
            focused_seconds: normalizeInteger(candidate.focused_seconds, 0, 0),
            settings,
            loading: Boolean(candidate.loading),
            status_message: candidate.status_message || "準備完了",
            error_message: candidate.error_message || "",
        }
    }

    class PomodoroStateStore {
        constructor(storage = window.localStorage) {
            this.storage = storage
            this.listeners = new Set()
            this.state = sanitizeState(this._loadFromStorage())
        }

        _loadFromStorage() {
            try {
                const raw = this.storage.getItem(STORAGE_KEY)
                return raw ? JSON.parse(raw) : {}
            } catch (error) {
                return {}
            }
        }

        _saveToStorage() {
            try {
                this.storage.setItem(STORAGE_KEY, JSON.stringify(this.state))
            } catch (error) {
                return
            }
        }

        getState() {
            return JSON.parse(JSON.stringify(this.state))
        }

        replace(nextState) {
            this.state = sanitizeState(nextState)
            this._saveToStorage()
            this.listeners.forEach((listener) => listener(this.getState()))
            return this.getState()
        }

        merge(partialState) {
            return this.replace({
                ...this.state,
                ...partialState,
                settings: {
                    ...this.state.settings,
                    ...(partialState.settings || {}),
                },
            })
        }

        subscribe(listener) {
            this.listeners.add(listener)
            return () => this.listeners.delete(listener)
        }
    }

    window.PomodoroState = {
        DEFAULT_SETTINGS,
        MODE_LABELS,
        PomodoroStateStore,
        sanitizeState,
        getDurationSeconds,
        getNextMode,
    }
})()
