(() => {
  const DEFAULT_STATE = {
    mode: "work",
    status: "loading",
    remainingSeconds: 0,
    totalSeconds: 0,
    stats: {
      completed_count: 0,
      focused_seconds: 0,
    },
    settings: {},
  };

  function clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function createPomodoroState(initialState = {}) {
    let state = {
      ...clone(DEFAULT_STATE),
      ...clone(initialState),
      stats: {
        ...clone(DEFAULT_STATE.stats),
        ...(initialState.stats || {}),
      },
      settings: {
        ...(initialState.settings || {}),
      },
    };
    const listeners = new Set();

    function notify() {
      const snapshot = clone(state);
      listeners.forEach((listener) => listener(snapshot));
    }

    return {
      getState() {
        return clone(state);
      },
      subscribe(listener) {
        listeners.add(listener);
        listener(this.getState());
        return () => listeners.delete(listener);
      },
      applyApiState(apiState) {
        state = {
          ...state,
          mode: apiState.mode || state.mode,
          status: apiState.status || "idle",
          remainingSeconds: apiState.remaining_seconds ?? state.remainingSeconds,
          totalSeconds: apiState.total_seconds ?? state.totalSeconds,
          stats: {
            ...state.stats,
            ...(apiState.stats || {}),
          },
          settings: {
            ...state.settings,
            ...(apiState.settings || {}),
          },
        };
        notify();
      },
      setStatus(status) {
        state.status = status;
        notify();
      },
      setRemainingSeconds(remainingSeconds) {
        state.remainingSeconds = Math.max(remainingSeconds, 0);
        notify();
      },
    };
  }

  window.PomodoroState = {
    createPomodoroState,
  };
})();
