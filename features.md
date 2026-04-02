# Pomodoro Timer 実装機能一覧

## 概要

このファイルは、`architecture.md` に基づいて Pomodoro タイマーアプリの実装対象機能を整理したものである。

Pomodoro 関連の実装ファイルは `1.pomodoro/` 配下に配置する。

## MVP で実装する機能

### 1. 画面表示

- 単一ページのメイン画面表示
- ヘッダー表示
- 現在モード表示
- 残り時間表示
- 円形プログレス表示
- 操作ボタン表示
- 今日の進捗カード表示

### 2. タイマー操作

- 作業セッション開始
- 短休憩開始
- 長休憩開始
- タイマー一時停止
- タイマー再開
- タイマー終了時の状態更新
- セッション完了後の次モード自動判定

### 3. タイマー状態管理

- `idle / running / paused / finished` の状態遷移管理
- 現在モードの管理
- 残り時間の管理
- 完了回数の管理
- 今日の集中時間の管理
- 画面再読み込み後の状態復元
- localStorage を使ったクライアント状態保存

### 4. タイマー計算ロジック

- `Date.now()` の差分を利用した残り時間計算
- 単純減算によるドリフト回避
- 作業終了後に短休憩へ進む判定
- 一定回数ごとに長休憩へ進む判定

### 5. UI 更新

- モード表示の切り替え
- タイマー数字表示の更新
- 円形プログレスの更新
- ボタン活性・非活性の切り替え
- 今日の進捗カードの更新
- API 応答に応じた画面反映

### 6. Flask ルートと API

- `GET /` でメイン画面を返す
- `GET /api/state` で初期表示用の状態と設定を返す
- `POST /api/settings` で設定を更新する
- `POST /api/session/complete` で 1 セッション完了を記録する
- `POST /api/session/reset` で当日の進捗をリセットする
- `GET /api/stats/today` で今日の統計を返す

### 7. バックエンドサービス

- 初期表示データの組み立て
- 設定保存処理
- セッション完了記録処理
- 日次集計更新処理
- 当日統計取得処理
- 当日進捗リセット処理

### 8. ドメインロジック

- Pomodoro のモード遷移ルール
- 長休憩判定ルール
- 日次集計更新ルール
- 初期表示データ生成ロジック

### 9. 永続化

- 設定データの保存と取得
- 日次統計データの保存と取得
- セッション履歴の保存と取得
- `settings` データモデルの実装
- `daily_stats` データモデルの実装
- `session_log` データモデルの実装

### 10. 設定項目

- `work_minutes`
- `short_break_minutes`
- `long_break_minutes`
- `cycles_before_long_break`

### 11. テスト容易性のための設計機能

- Python 側 Clock 抽象化
- JavaScript 側 Clock 抽象化
- Repository の差し替え可能な構成
- DOM とロジックの分離
- 副作用を持たない純粋関数中心の実装

### 12. テスト

- ドメインロジックの単体テスト
- サービス層の単体テスト
- API のテスト
- In-memory Repository を使ったテスト

## 将来拡張として想定する機能

- 通知音
- ブラウザ通知
- 設定画面
- セッション履歴画面
- 週次統計表示
- 月次統計表示
- 複数端末同期
- ユーザー認証

## 推奨実装ファイル

```text
1.pomodoro/
├── app.py
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── timer-engine.js
│       ├── pomodoro-state.js
│       ├── pomodoro-ui.js
│       └── pomodoro-api.js
├── domain/
│   └── pomodoro_rules.py
├── services/
│   ├── stats_service.py
│   └── settings_service.py
├── repositories/
│   ├── stats_repository.py
│   └── settings_repository.py
└── tests/
    ├── test_pomodoro_rules.py
    ├── test_stats_service.py
    └── test_api.py
```