window.pomodoroState = (() => {
    let state = {
        settings: null,
        timer: {
            mode: 'work',
            remaining_seconds: 1500,
            completed_work_sessions: 0,
        },
    };

    const clone = (value) => JSON.parse(JSON.stringify(value));

    return {
        getState() {
            return clone(state);
        },
        setState(nextState) {
            state = {
                settings: nextState.settings,
                timer: nextState.timer,
            };
        },
    };
})();
