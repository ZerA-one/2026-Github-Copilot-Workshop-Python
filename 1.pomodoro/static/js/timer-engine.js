(() => {
  function createTimerEngine({ onTick, onComplete, now = () => Date.now() }) {
    let intervalId = null;
    let deadline = 0;
    let status = "idle";

    function clearTimer() {
      if (intervalId !== null) {
        window.clearInterval(intervalId);
        intervalId = null;
      }
    }

    function tick() {
      const remainingSeconds = Math.max(0, Math.ceil((deadline - now()) / 1000));
      onTick(remainingSeconds);

      if (remainingSeconds === 0) {
        clearTimer();
        status = "finished";
        Promise.resolve(onComplete()).catch((error) => console.error(error));
      }
    }

    return {
      start(remainingSeconds) {
        clearTimer();
        if (remainingSeconds <= 0) {
          onTick(0);
          status = "finished";
          return Promise.resolve(onComplete());
        }

        deadline = now() + (remainingSeconds * 1000);
        status = "running";
        onTick(remainingSeconds);
        intervalId = window.setInterval(tick, 1000);
        return Promise.resolve();
      },
      pause() {
        if (status !== "running") {
          return;
        }

        clearTimer();
        status = "paused";
      },
      stop() {
        clearTimer();
        status = "idle";
      },
      getStatus() {
        return status;
      },
    };
  }

  window.PomodoroTimerEngine = {
    createTimerEngine,
  };
})();
