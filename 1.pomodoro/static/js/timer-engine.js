(function () {
    const TICK_INTERVAL_MS = 250;
    let timerId = null;

    function now() {
        return Date.now();
    }

    function clearTimer() {
        if (timerId !== null) {
            window.clearInterval(timerId);
            timerId = null;
        }
    }

    function calculateRemainingSeconds(endTimestamp) {
        return Math.max(0, Math.ceil((endTimestamp - now()) / 1000));
    }

    function completeSession() {
        clearTimer();

        const currentState = window.PomodoroState.getState();
        const nextState = {
            sessionStatus: "finished",
            remainingSeconds: 0,
            endTimestamp: null,
        };

        if (currentState.mode === "work" && !currentState.completedForCurrentRun) {
            nextState.completedCount = currentState.completedCount + 1;
            nextState.focusedSeconds = currentState.focusedSeconds + currentState.durationSeconds;
            nextState.completedForCurrentRun = true;
        }

        window.PomodoroState.updateState(nextState);
    }

    function syncRunningTimer() {
        const currentState = window.PomodoroState.getState();

        if (currentState.sessionStatus !== "running" || !currentState.endTimestamp) {
            clearTimer();
            return;
        }

        const nextRemainingSeconds = calculateRemainingSeconds(currentState.endTimestamp);

        if (nextRemainingSeconds <= 0) {
            completeSession();
            return;
        }

        if (nextRemainingSeconds !== currentState.remainingSeconds) {
            window.PomodoroState.updateState({ remainingSeconds: nextRemainingSeconds });
        }
    }

    function startTicking() {
        clearTimer();
        timerId = window.setInterval(syncRunningTimer, TICK_INTERVAL_MS);
        syncRunningTimer();
    }

    function startOrResumeTimer() {
        const currentState = window.PomodoroState.getState();
        const durationSeconds = currentState.durationSeconds || window.PomodoroState.getDefaultDuration(currentState.mode);
        const remainingSeconds = currentState.sessionStatus === "finished"
            ? durationSeconds
            : Math.max(currentState.remainingSeconds, 1);

        window.PomodoroState.updateState({
            remainingSeconds,
            durationSeconds,
            sessionStatus: "running",
            endTimestamp: now() + remainingSeconds * 1000,
            completedForCurrentRun: false,
        });

        startTicking();
    }

    function pauseTimer() {
        const currentState = window.PomodoroState.getState();

        if (currentState.sessionStatus !== "running" || !currentState.endTimestamp) {
            return;
        }

        clearTimer();
        window.PomodoroState.updateState({
            sessionStatus: "paused",
            remainingSeconds: calculateRemainingSeconds(currentState.endTimestamp),
            endTimestamp: null,
        });
    }

    function resetTimer() {
        clearTimer();

        const currentState = window.PomodoroState.getState();
        const durationSeconds = window.PomodoroState.getDefaultDuration(currentState.mode);

        window.PomodoroState.updateState({
            remainingSeconds: durationSeconds,
            durationSeconds,
            sessionStatus: "idle",
            endTimestamp: null,
            completedForCurrentRun: false,
        });
    }

    function bindEvents() {
        const startButton = document.getElementById("start-button");
        const resetButton = document.getElementById("reset-button");

        if (startButton) {
            startButton.addEventListener("click", function () {
                const currentState = window.PomodoroState.getState();

                if (currentState.sessionStatus === "running") {
                    pauseTimer();
                    return;
                }

                startOrResumeTimer();
            });
        }

        if (resetButton) {
            resetButton.addEventListener("click", resetTimer);
        }
    }

    function restoreRunningSessionIfNeeded() {
        const currentState = window.PomodoroState.getState();

        if (currentState.sessionStatus !== "running" || !currentState.endTimestamp) {
            return;
        }

        const remainingSeconds = calculateRemainingSeconds(currentState.endTimestamp);

        if (remainingSeconds <= 0) {
            completeSession();
            return;
        }

        window.PomodoroState.updateState({ remainingSeconds });
        startTicking();
    }

    function init() {
        if (!window.PomodoroState || !window.PomodoroUI) {
            return;
        }

        window.PomodoroState.loadState();
        window.PomodoroUI.init();
        bindEvents();
        restoreRunningSessionIfNeeded();
    }

    document.addEventListener("DOMContentLoaded", init);
})();
