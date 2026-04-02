(() => {
    const elements = {};

    function setStatus(message, isError = false) {
        elements.settingsStatus.textContent = message;
        elements.settingsStatus.dataset.state = isError ? 'error' : 'success';
    }

    function fillForm(settings) {
        for (const [fieldName, value] of Object.entries(settings)) {
            if (elements.form.elements[fieldName]) {
                elements.form.elements[fieldName].value = value;
            }
        }
    }

    function toggleSettingsPanel(isOpen) {
        elements.settingsPanel.hidden = !isOpen;
    }

    function render() {
        const viewModel = window.pomodoroTimer.getViewModel();
        elements.currentModeText.textContent = viewModel.modeLabel;
        elements.timerDisplay.textContent = viewModel.timerDisplay;
        elements.cycleDisplay.textContent = `完了サイクル: ${viewModel.completedWorkSessions}`;
    }

    function collectSettingsPayload() {
        return {
            work_minutes: Number(elements.form.elements.work_minutes.value),
            short_break_minutes: Number(elements.form.elements.short_break_minutes.value),
            long_break_minutes: Number(elements.form.elements.long_break_minutes.value),
            cycles_before_long_break: Number(elements.form.elements.cycles_before_long_break.value),
        };
    }

    async function bootstrap() {
        const initialState = await window.pomodoroApi.getState();
        window.pomodoroTimer.initialize(initialState);
        fillForm(initialState.settings);
        render();
    }

    async function handleSubmit(event) {
        event.preventDefault();

        try {
            const response = await window.pomodoroApi.saveSettings(collectSettingsPayload());
            window.pomodoroTimer.applySettings(response.settings);
            fillForm(response.settings);
            render();
            toggleSettingsPanel(false);
            setStatus('設定を保存しました。');
        } catch (error) {
            const errors = error.response && error.response.errors ? Object.values(error.response.errors) : ['設定の保存に失敗しました。'];
            setStatus(errors.join(' '), true);
        }
    }

    function bindEvents() {
        elements.openSettingsButton.addEventListener('click', () => {
            toggleSettingsPanel(true);
            setStatus('');
        });

        elements.closeSettingsButton.addEventListener('click', () => {
            toggleSettingsPanel(false);
        });

        for (const button of elements.modeButtons) {
            button.addEventListener('click', () => {
                window.pomodoroTimer.setMode(button.dataset.modeButton);
                render();
            });
        }

        elements.completeSessionButton.addEventListener('click', () => {
            window.pomodoroTimer.completeCurrentSession();
            render();
        });

        elements.form.addEventListener('submit', handleSubmit);
    }

    document.addEventListener('DOMContentLoaded', async () => {
        elements.currentModeText = document.getElementById('current-mode-text');
        elements.timerDisplay = document.getElementById('timer-display');
        elements.cycleDisplay = document.getElementById('cycle-display');
        elements.settingsStatus = document.getElementById('settings-status');
        elements.settingsPanel = document.getElementById('settings-panel');
        elements.openSettingsButton = document.getElementById('open-settings-button');
        elements.closeSettingsButton = document.getElementById('close-settings-button');
        elements.completeSessionButton = document.getElementById('complete-session-button');
        elements.modeButtons = document.querySelectorAll('[data-mode-button]');
        elements.form = document.getElementById('settings-form');

        bindEvents();

        try {
            await bootstrap();
            setStatus('設定を読み込みました。');
        } catch (error) {
            setStatus('初期データの読み込みに失敗しました。', true);
        }
    });
})();
