(() => {
    class PomodoroTimer {
        constructor({ now = () => Date.now() } = {}) {
            this.now = now
            this.reset(25 * 60, "work")
        }

        restore(snapshot = {}) {
            this.mode = snapshot.mode || this.mode || "work"
            this.status = snapshot.status || "idle"
            const durationSeconds = snapshot.durationSeconds ?? snapshot.duration_seconds ?? this.durationSeconds ?? 1500
            const remainingSeconds = snapshot.remainingSeconds ?? snapshot.remaining_seconds ?? durationSeconds

            this.durationSeconds = Math.max(1, Number(durationSeconds))
            this.remainingSeconds = Math.max(0, Number(remainingSeconds))
            this.endTimestamp = snapshot.endTimestamp ?? snapshot.end_timestamp ?? null
            return this.getSnapshot()
        }

        start() {
            if (this.status === "running") {
                return this.getSnapshot()
            }
            if (this.status === "paused") {
                return this.resume()
            }
            if (this.remainingSeconds <= 0) {
                this.remainingSeconds = this.durationSeconds
            }
            this.status = "running"
            this.endTimestamp = this.now() + this.remainingSeconds * 1000
            return this.getSnapshot()
        }

        pause() {
            if (this.status !== "running") {
                return this.getSnapshot()
            }
            this.remainingSeconds = this._calculateRemainingSeconds()
            this.endTimestamp = null
            this.status = "paused"
            return this.getSnapshot()
        }

        resume() {
            if (this.status === "idle") {
                return this.start()
            }
            if (this.status !== "paused") {
                return this.getSnapshot()
            }
            this.status = "running"
            this.endTimestamp = this.now() + this.remainingSeconds * 1000
            return this.getSnapshot()
        }

        reset(durationSeconds = this.durationSeconds, mode = this.mode) {
            this.mode = mode || "work"
            this.status = "idle"
            this.durationSeconds = Math.max(1, Number(durationSeconds || 1500))
            this.remainingSeconds = this.durationSeconds
            this.endTimestamp = null
            return this.getSnapshot()
        }

        tick() {
            if (this.status !== "running") {
                return this.getSnapshot()
            }

            this.remainingSeconds = this._calculateRemainingSeconds()
            if (this.remainingSeconds <= 0) {
                this.remainingSeconds = 0
                this.endTimestamp = null
                this.status = "finished"
            }

            return this.getSnapshot()
        }

        _calculateRemainingSeconds() {
            if (!this.endTimestamp) {
                return this.remainingSeconds
            }
            return Math.max(0, Math.ceil((this.endTimestamp - this.now()) / 1000))
        }

        getSnapshot() {
            if (this.status === "running") {
                this.remainingSeconds = this._calculateRemainingSeconds()
                if (this.remainingSeconds <= 0) {
                    this.remainingSeconds = 0
                    this.endTimestamp = null
                    this.status = "finished"
                }
            }

            return {
                mode: this.mode,
                status: this.status,
                durationSeconds: this.durationSeconds,
                remainingSeconds: this.remainingSeconds,
                endTimestamp: this.endTimestamp,
            }
        }
    }

    window.PomodoroTimer = PomodoroTimer
})()
