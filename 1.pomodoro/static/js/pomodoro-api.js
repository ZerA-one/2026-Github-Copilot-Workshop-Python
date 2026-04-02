(() => {
  async function requestJson(url, options = {}) {
    const headers = {
      ...(options.headers || {}),
    };

    if (options.body && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }

    const response = await fetch(url, {
      headers,
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }

    return response.json();
  }

  function createPomodoroApi() {
    return {
      fetchState() {
        return requestJson("/api/state");
      },
      completeSession(payload) {
        return requestJson("/api/session/complete", {
          method: "POST",
          body: JSON.stringify(payload),
        });
      },
      resetSession() {
        return requestJson("/api/session/reset", {
          method: "POST",
        });
      },
    };
  }

  function showError(message) {
    const errorMessage = document.getElementById("app-error");
    errorMessage.textContent = message;
    errorMessage.hidden = false;
  }

  function clearError() {
    const errorMessage = document.getElementById("app-error");
    errorMessage.hidden = true;
    errorMessage.textContent = "";
  }

  async function bootstrap() {
    const api = createPomodoroApi();
    const state = window.PomodoroState.createPomodoroState();
    const engine = window.PomodoroTimerEngine.createTimerEngine({
      onTick(remainingSeconds) {
        state.setRemainingSeconds(remainingSeconds);
      },
      async onComplete() {
        state.setStatus("syncing");
        try {
          const currentState = state.getState();
          const apiState = await api.completeSession({
            session_type: currentState.mode,
            focused_seconds: currentState.totalSeconds,
          });
          clearError();
          state.applyApiState(apiState);
        } catch (error) {
          console.error(error);
          showError("セッション完了の保存に失敗しました。");
          state.setStatus("error");
        }
      },
    });

    state.subscribe(window.PomodoroUI.render);

    document.getElementById("start-button").addEventListener("click", async () => {
      clearError();
      const currentState = state.getState();

      if (currentState.status === "running") {
        engine.pause();
        state.setStatus("paused");
        return;
      }

      state.setStatus("running");
      await engine.start(currentState.remainingSeconds);
    });

    document.getElementById("reset-button").addEventListener("click", async () => {
      clearError();
      engine.stop();
      state.setStatus("syncing");

      try {
        const apiState = await api.resetSession();
        state.applyApiState(apiState);
      } catch (error) {
        console.error(error);
        showError("リセットに失敗しました。");
        state.setStatus("error");
      }
    });

    try {
      const apiState = await api.fetchState();
      state.applyApiState(apiState);
      clearError();
    } catch (error) {
      console.error(error);
      showError("初期状態の取得に失敗しました。");
      state.applyApiState({
        mode: "work",
        status: "error",
        remaining_seconds: 25 * 60,
        total_seconds: 25 * 60,
        stats: {
          completed_count: 0,
          focused_seconds: 0,
        },
      });
    }

    window.pomodoroApp = {
      api,
      state,
      engine,
    };
  }

  document.addEventListener("DOMContentLoaded", bootstrap);
  window.PomodoroApi = {
    createPomodoroApi,
  };
})();
