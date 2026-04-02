(function () {
    const DEFAULT_DURATION_SECONDS = 25 * 60
    const TICK_INTERVAL_MS = 100

    function createTimerEngine(options = {}) {
        const now = options.now || (() => Date.now())
        const durationMs = Math.max(0, Number(options.durationSeconds || DEFAULT_DURATION_SECONDS) * 1000)
        const onUpdate = typeof options.onUpdate === "function" ? options.onUpdate : () => {}
        const onFinish = typeof options.onFinish === "function" ? options.onFinish : () => {}
        const scheduleTick = options.scheduleTick || ((callback) => window.setInterval(callback, TICK_INTERVAL_MS))
        const cancelTick = options.cancelTick || ((tickId) => window.clearInterval(tickId))

        let status = "idle"
        let remainingMs = durationMs
        let startedAt = null
        let tickId = null

        function stopTicker() {
            if (tickId !== null) {
                cancelTick(tickId)
                tickId = null
            }
        }

        function calculateRemainingMs() {
            if (status !== "running" || startedAt === null) {
                return remainingMs
            }

            return Math.max(0, durationMs - (now() - startedAt))
        }

        function getState() {
            const currentRemainingMs = calculateRemainingMs()
            const progress = durationMs === 0 ? 1 : 1 - currentRemainingMs / durationMs

            return {
                status,
                mode: "work",
                durationMs,
                remainingMs: currentRemainingMs,
                progress: Math.min(Math.max(progress, 0), 1),
            }
        }

        function emitUpdate() {
            const snapshot = getState()
            onUpdate(snapshot)
            return snapshot
        }

        function finish() {
            stopTicker()
            remainingMs = 0
            startedAt = null
            status = "finished"
            const snapshot = emitUpdate()
            onFinish(snapshot)
            return snapshot
        }

        function tick() {
            if (status !== "running") {
                return getState()
            }

            const currentRemainingMs = calculateRemainingMs()

            if (currentRemainingMs <= 0) {
                return finish()
            }

            remainingMs = currentRemainingMs
            return emitUpdate()
        }

        function startTicker() {
            stopTicker()
            tickId = scheduleTick(tick)
        }

        function start() {
            if (status !== "idle") {
                return getState()
            }

            remainingMs = durationMs
            startedAt = now()
            status = "running"
            startTicker()
            return emitUpdate()
        }

        function pause() {
            if (status !== "running") {
                return getState()
            }

            remainingMs = calculateRemainingMs()
            startedAt = null
            status = "paused"
            stopTicker()
            return emitUpdate()
        }

        function resume() {
            if (status !== "paused") {
                return getState()
            }

            startedAt = now() - (durationMs - remainingMs)
            status = "running"
            startTicker()
            return emitUpdate()
        }

        function reset() {
            stopTicker()
            startedAt = null
            remainingMs = durationMs
            status = "idle"
            return emitUpdate()
        }

        function toggle() {
            if (status === "idle") {
                return start()
            }

            if (status === "running") {
                return pause()
            }

            if (status === "paused") {
                return resume()
            }

            return getState()
        }

        return {
            getState,
            start,
            pause,
            resume,
            reset,
            toggle,
        }
    }

    window.PomodoroTimerEngine = {
        DEFAULT_DURATION_SECONDS,
        createTimerEngine,
    }
})()
