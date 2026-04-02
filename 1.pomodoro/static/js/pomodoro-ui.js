(function () {
    function formatTime(remainingMs) {
        const totalSeconds = Math.max(0, Math.ceil(remainingMs / 1000))
        const minutes = Math.floor(totalSeconds / 60)
        const seconds = totalSeconds % 60

        return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`
    }

    function getStatusMessage(status) {
        if (status === "running") {
            return "集中中です"
        }

        if (status === "paused") {
            return "一時停止中です"
        }

        if (status === "finished") {
            return "作業セッションが完了しました"
        }

        return "開始するとタイマーが進行します"
    }

    function getToggleButtonLabel(status) {
        if (status === "running") {
            return "一時停止"
        }

        if (status === "paused") {
            return "再開"
        }

        if (status === "finished") {
            return "完了"
        }

        return "開始"
    }

    function createPomodoroUI(rootElement) {
        if (!rootElement) {
            return null
        }

        const currentModeElement = rootElement.querySelector("#current-mode")
        const timerDisplayElement = rootElement.querySelector("#timer-display")
        const timerStatusElement = rootElement.querySelector("#timer-status")
        const toggleButtonElement = rootElement.querySelector("#toggle-timer-button")
        const resetButtonElement = rootElement.querySelector("#reset-timer-button")
        const progressIndicatorElement = rootElement.querySelector("#progress-indicator")
        const radius = Number(progressIndicatorElement.getAttribute("r"))
        const circumference = 2 * Math.PI * radius

        progressIndicatorElement.style.strokeDasharray = `${circumference}`
        progressIndicatorElement.style.strokeDashoffset = `${circumference}`

        function render(snapshot) {
            rootElement.dataset.timerStatus = snapshot.status
            currentModeElement.textContent = snapshot.mode === "work" ? "作業" : snapshot.mode
            timerDisplayElement.textContent = formatTime(snapshot.remainingMs)
            timerStatusElement.textContent = getStatusMessage(snapshot.status)
            toggleButtonElement.textContent = getToggleButtonLabel(snapshot.status)
            toggleButtonElement.disabled = snapshot.status === "finished"
            resetButtonElement.disabled = snapshot.status === "idle"

            const dashOffset = circumference * (1 - snapshot.progress)
            progressIndicatorElement.style.strokeDashoffset = `${dashOffset}`
        }

        function bind(engine) {
            toggleButtonElement.addEventListener("click", () => {
                engine.toggle()
            })

            resetButtonElement.addEventListener("click", () => {
                engine.reset()
            })
        }

        return {
            bind,
            render,
        }
    }

    function initializePomodoroApp() {
        const rootElement = document.getElementById("pomodoro-app")

        if (!rootElement || !window.PomodoroTimerEngine) {
            return
        }

        const durationSeconds = Number(rootElement.dataset.workDurationSeconds) || window.PomodoroTimerEngine.DEFAULT_DURATION_SECONDS
        const ui = createPomodoroUI(rootElement)

        if (!ui) {
            return
        }

        const engine = window.PomodoroTimerEngine.createTimerEngine({
            durationSeconds,
            onUpdate: (snapshot) => ui.render(snapshot),
        })

        ui.bind(engine)
        ui.render(engine.getState())

        window.pomodoroApp = {
            engine,
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initializePomodoroApp)
    } else {
        initializePomodoroApp()
    }
})()
