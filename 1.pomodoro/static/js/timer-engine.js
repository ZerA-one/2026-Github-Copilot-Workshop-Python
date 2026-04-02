window.pomodoroTimer = (() => {
    const MODE_LABELS = {
        work: '作業',
        short_break: '短休憩',
        long_break: '長休憩',
    };

    function getDurationSeconds(settings, mode) {
        if (mode === 'work') {
            return settings.work_minutes * 60;
        }
        if (mode === 'short_break') {
            return settings.short_break_minutes * 60;
        }
        return settings.long_break_minutes * 60;
    }

    function getNextMode(currentMode, completedWorkSessions, settings) {
        if (currentMode === 'work') {
            return completedWorkSessions % settings.cycles_before_long_break === 0
                ? 'long_break'
                : 'short_break';
        }
        return 'work';
    }

    function getState() {
        return window.pomodoroState.getState();
    }

    function setState(nextState) {
        window.pomodoroState.setState(nextState);
    }

    return {
        initialize(initialState) {
            setState(initialState);
        },
        setMode(mode) {
            const state = getState();
            const timer = {
                ...state.timer,
                mode,
                remaining_seconds: getDurationSeconds(state.settings, mode),
            };

            setState({ ...state, timer });
        },
        applySettings(settings) {
            const state = getState();
            const timer = {
                ...state.timer,
                remaining_seconds: getDurationSeconds(settings, state.timer.mode),
            };

            setState({ settings, timer });
        },
        completeCurrentSession() {
            const state = getState();
            const completedWorkSessions = state.timer.mode === 'work'
                ? state.timer.completed_work_sessions + 1
                : state.timer.completed_work_sessions;
            const nextMode = getNextMode(state.timer.mode, completedWorkSessions, state.settings);
            const timer = {
                mode: nextMode,
                remaining_seconds: getDurationSeconds(state.settings, nextMode),
                completed_work_sessions: completedWorkSessions,
            };

            setState({ ...state, timer });
        },
        getViewModel() {
            const state = getState();
            const minutes = String(Math.floor(state.timer.remaining_seconds / 60)).padStart(2, '0');
            const seconds = String(state.timer.remaining_seconds % 60).padStart(2, '0');

            return {
                timerDisplay: `${minutes}:${seconds}`,
                modeLabel: MODE_LABELS[state.timer.mode],
                completedWorkSessions: state.timer.completed_work_sessions,
                settings: state.settings,
            };
        },
    };
})();
