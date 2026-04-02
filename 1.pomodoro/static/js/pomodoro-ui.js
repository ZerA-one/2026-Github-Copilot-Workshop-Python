(function () {
    const MODE_LABELS = {
        work: "作業中",
        shortBreak: "短い休憩",
        longBreak: "長い休憩",
    };

    const SESSION_STATUS_LABELS = {
        idle: "待機中",
        running: "進行中",
        paused: "一時停止中",
        finished: "完了",
    };

    let elements = null;

    function formatTime(totalSeconds) {
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;

        return String(minutes).padStart(2, "0") + ":" + String(seconds).padStart(2, "0");
    }

    function formatFocusedTime(totalSeconds) {
        const totalMinutes = Math.floor(totalSeconds / 60);
        const hours = Math.floor(totalMinutes / 60);
        const minutes = totalMinutes % 60;

        if (hours > 0) {
            return `${hours}時間${minutes}分`;
        }

        return `${totalMinutes}分`;
    }

    function calculateProgressOffset(state) {
        const radius = Number(elements.progressRing.getAttribute("r"));
        const circumference = 2 * Math.PI * radius;
        const duration = Math.max(state.durationSeconds, 1);
        const progressRatio = Math.max(0, Math.min(1, state.remainingSeconds / duration));

        elements.progressRing.style.strokeDasharray = String(circumference);
        return circumference * (1 - progressRatio);
    }

    function getStartButtonLabel(sessionStatus) {
        if (sessionStatus === "running") {
            return "一時停止";
        }

        if (sessionStatus === "paused") {
            return "再開";
        }

        return "開始";
    }

    function render(state) {
        if (!elements) {
            return;
        }

        elements.currentMode.textContent = MODE_LABELS[state.mode] || MODE_LABELS.work;
        elements.sessionStatus.textContent = SESSION_STATUS_LABELS[state.sessionStatus] || SESSION_STATUS_LABELS.idle;
        elements.remainingTime.textContent = formatTime(state.remainingSeconds);
        elements.completedCount.textContent = String(state.completedCount);
        elements.focusedTime.textContent = formatFocusedTime(state.focusedSeconds);
        elements.startButton.textContent = getStartButtonLabel(state.sessionStatus);
        elements.progressRing.style.strokeDashoffset = String(calculateProgressOffset(state));
    }

    function init() {
        elements = {
            currentMode: document.getElementById("current-mode"),
            sessionStatus: document.getElementById("session-status"),
            remainingTime: document.getElementById("remaining-time"),
            progressRing: document.getElementById("progress-ring"),
            completedCount: document.getElementById("completed-count"),
            focusedTime: document.getElementById("focused-time"),
            startButton: document.getElementById("start-button"),
            resetButton: document.getElementById("reset-button"),
        };

        if (!window.PomodoroState) {
            return;
        }

        window.PomodoroState.subscribe(render);
        render(window.PomodoroState.getState());
    }

    window.PomodoroUI = {
        init,
        render,
    };
})();
