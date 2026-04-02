(function () {
    const STORAGE_KEY = "pomodoro.timer.state.v1";
    const VALID_MODES = new Set(["work", "shortBreak", "longBreak"]);
    const VALID_SESSION_STATUSES = new Set(["idle", "running", "paused", "finished"]);
    const DEFAULT_DURATIONS = {
        work: 25 * 60,
        shortBreak: 5 * 60,
        longBreak: 15 * 60,
    };

    const subscribers = new Set();
    let state = createDefaultState();

    function createDefaultState() {
        return {
            mode: "work",
            remainingSeconds: DEFAULT_DURATIONS.work,
            durationSeconds: DEFAULT_DURATIONS.work,
            sessionStatus: "idle",
            completedCount: 0,
            focusedSeconds: 0,
            endTimestamp: null,
            completedForCurrentRun: false,
        };
    }

    function getStorage() {
        try {
            return window.localStorage;
        } catch (error) {
            return null;
        }
    }

    function getDefaultDuration(mode) {
        return DEFAULT_DURATIONS[mode] || DEFAULT_DURATIONS.work;
    }

    function toNonNegativeInteger(value, fallback) {
        if (!Number.isFinite(value)) {
            return fallback;
        }

        return Math.max(0, Math.floor(value));
    }

    function sanitizeState(candidate) {
        if (!candidate || typeof candidate !== "object" || Array.isArray(candidate)) {
            return createDefaultState();
        }

        const mode = VALID_MODES.has(candidate.mode) ? candidate.mode : "work";
        const durationSeconds = toNonNegativeInteger(candidate.durationSeconds, getDefaultDuration(mode)) || getDefaultDuration(mode);
        const remainingSeconds = Math.min(
            toNonNegativeInteger(candidate.remainingSeconds, durationSeconds),
            durationSeconds
        );
        const sessionStatus = VALID_SESSION_STATUSES.has(candidate.sessionStatus)
            ? candidate.sessionStatus
            : "idle";
        const completedCount = toNonNegativeInteger(candidate.completedCount, 0);
        const focusedSeconds = toNonNegativeInteger(candidate.focusedSeconds, 0);
        const endTimestamp = Number.isFinite(candidate.endTimestamp)
            ? Math.floor(candidate.endTimestamp)
            : null;

        return {
            mode,
            remainingSeconds,
            durationSeconds,
            sessionStatus,
            completedCount,
            focusedSeconds,
            endTimestamp,
            completedForCurrentRun: Boolean(candidate.completedForCurrentRun),
        };
    }

    function persistState() {
        const storage = getStorage();

        if (!storage) {
            return;
        }

        try {
            storage.setItem(STORAGE_KEY, JSON.stringify(state));
        } catch (error) {
            // localStorage が利用できない場合はメモリ上だけで継続する。
        }
    }

    function emitChange() {
        const snapshot = getState();
        subscribers.forEach((listener) => listener(snapshot));
    }

    function getState() {
        return { ...state };
    }

    function replaceState(nextState) {
        state = sanitizeState(nextState);
        persistState();
        emitChange();
        return getState();
    }

    function updateState(partialState) {
        return replaceState({ ...state, ...partialState });
    }

    function loadState() {
        const storage = getStorage();

        if (!storage) {
            state = createDefaultState();
            return getState();
        }

        try {
            const storedValue = storage.getItem(STORAGE_KEY);

            if (!storedValue) {
                state = createDefaultState();
                persistState();
                return getState();
            }

            state = sanitizeState(JSON.parse(storedValue));
        } catch (error) {
            state = createDefaultState();

            try {
                storage.removeItem(STORAGE_KEY);
            } catch (storageError) {
                // 破損データ削除ができなくてもデフォルト状態で継続する。
            }

            persistState();
        }

        return getState();
    }

    function subscribe(listener) {
        subscribers.add(listener);

        return function unsubscribe() {
            subscribers.delete(listener);
        };
    }

    window.PomodoroState = {
        DEFAULT_DURATIONS,
        createDefaultState,
        getDefaultDuration,
        getState,
        loadState,
        replaceState,
        subscribe,
        updateState,
    };
})();
