(() => {
  const MODE_LABELS = {
    work: "作業",
    short_break: "短い休憩",
    long_break: "長い休憩",
  };

  const STATUS_MESSAGES = {
    loading: "読み込み中です…",
    idle: "開始を押すとセッションが始まります。",
    running: "集中中です。",
    paused: "一時停止中です。",
    syncing: "最新の統計を反映しています…",
    error: "API との通信に失敗しました。",
  };

  function formatSeconds(totalSeconds) {
    const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
    const seconds = String(totalSeconds % 60).padStart(2, "0");
    return `${minutes}:${seconds}`;
  }

  function formatFocusedDuration(focusedSeconds) {
    const minutes = Math.floor(focusedSeconds / 60);
    const seconds = focusedSeconds % 60;

    if (seconds === 0) {
      return `${minutes} 分`;
    }

    return `${minutes} 分 ${seconds} 秒`;
  }

  function render(state) {
    const modeLabel = document.querySelector("[data-role='mode-label']");
    const timerValue = document.querySelector("[data-role='timer-value']");
    const statusMessage = document.querySelector("[data-role='status-message']");
    const completedCount = document.querySelector("[data-role='completed-count']");
    const focusedMinutes = document.querySelector("[data-role='focused-minutes']");
    const startButton = document.getElementById("start-button");
    const resetButton = document.getElementById("reset-button");

    modeLabel.textContent = MODE_LABELS[state.mode] || "作業";
    timerValue.textContent = formatSeconds(state.remainingSeconds);
    statusMessage.textContent = STATUS_MESSAGES[state.status] || STATUS_MESSAGES.idle;
    completedCount.textContent = String(state.stats.completed_count || 0);
    focusedMinutes.textContent = formatFocusedDuration(state.stats.focused_seconds || 0);

    let startButtonLabel = "開始";
    if (state.status === "running") {
      startButtonLabel = "一時停止";
    } else if (state.status === "paused") {
      startButtonLabel = "再開";
    }

    startButton.textContent = startButtonLabel;
    startButton.disabled = state.status === "loading" || state.status === "syncing";
    resetButton.disabled = state.status === "loading" || state.status === "syncing";
  }

  window.PomodoroUI = {
    render,
  };
})();
