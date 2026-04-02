# Pomodoro Timer Web App Architecture

## 概要

このプロジェクトでは、Pomodoro タイマー Web アプリを Flask と HTML/CSS/JavaScript で構築する。
画面は単一ページ構成とし、Flask は画面配信と API、フロントエンドはタイマー進行と UI 制御を担当する。

Pomodoro 関連の実装ファイルは、リポジトリ内の `1.pomodoro/` 配下に配置する。

## 設計方針

- 単一画面アプリとして構成し、過剰なフレームワークは導入しない
- タイマーのカウントダウンはブラウザ側で処理し、操作感を優先する
- Flask は設定、進捗、履歴などの永続化と API 提供に集中する
- 時刻依存、保存処理、DOM 操作を分離し、単体テストしやすい構成にする
- 将来的な通知、履歴、統計画面の追加に耐えられる責務分離を保つ

## 全体構成

```text
Browser
  ├─ HTML/CSS
  ├─ JavaScript Timer Engine
  ├─ UI Rendering
  └─ API Client
       ↓ HTTP/JSON
Flask
  ├─ Routes
  ├─ Services
  ├─ Domain Logic
  └─ Repositories
       ↓
SQLite or JSON Storage
```

## バックエンド構成

Flask 側は次の 4 層で構成する。

### 1. Routes

- `/` で画面を配信する
- `/api/*` で JSON API を提供する
- リクエストとレスポンスの変換だけを担当し、業務ロジックを持たない

### 2. Services

- 進捗更新、設定保存、セッション完了記録を担当する
- Repository を通じて永続化を実行する
- Domain Logic を呼び出して、必要な計算結果を組み立てる

### 3. Domain Logic

- Pomodoro の状態遷移やルール判定を担当する
- 例: 作業終了後に短休憩へ進むか、長休憩へ進むかの判定
- 副作用を持たない純粋関数を中心に実装する

### 4. Repositories

- 設定、日次集計、セッション履歴の保存と取得を担当する
- 実装は SQLite を推奨する
- テスト用に In-memory 実装へ差し替え可能な構成にする

## フロントエンド構成

フロントエンドは Vanilla JavaScript をベースに、責務ごとに分割する。

### 1. Timer Engine

- 残り時間計算を担当する
- `Date.now()` の差分で残り秒数を算出し、単純減算によるドリフトを避ける
- `idle / running / paused / finished` の状態遷移を管理する

### 2. State Module

- 現在モード、残り時間、完了回数、集計値などの画面状態を管理する
- localStorage と連携して再読み込み後の復元に対応する

### 3. UI Module

- DOM 更新のみを担当する
- モード表示、ボタン状態、円形プログレス、今日の進捗カードを描画する
- ロジックは持たず、State の内容を表示へ反映する

### 4. API Module

- Flask API との通信を担当する
- 初期状態取得、設定保存、セッション完了記録、集計更新を扱う

## 推奨 API

- `GET /` : メイン画面表示
- `GET /api/state` : 初期表示用の状態と設定を取得
- `POST /api/settings` : 作業時間、休憩時間などの設定を更新
- `POST /api/session/complete` : 1 セッション完了を記録
- `POST /api/session/reset` : 当日の進捗をリセット
- `GET /api/stats/today` : 今日の完了回数と集中時間を取得

`POST /api/session/complete` のレスポンスでは、保存結果だけでなく最新の集計値も返し、フロントエンド側で集計ロジックを重複させない。

## データモデル

### settings

- work_minutes
- short_break_minutes
- long_break_minutes
- cycles_before_long_break

### daily_stats

- date
- completed_count
- focused_seconds

### session_log

- started_at
- ended_at
- session_type
- completed

## テストしやすさのための設計追加

単体テスト容易性の観点で、次の追加ルールを採用する。

### Clock の抽象化

- Python 側で `datetime.now()` を直接呼ばず、Clock インターフェース経由で時刻を取得する
- JavaScript 側でも `Date.now()` をラップし、テスト時に差し替え可能にする

### Repository の差し替え

- `StatsRepository` や `SettingsRepository` は interface ベースで扱う
- 本番では SQLite、テストでは In-memory 実装を利用する

### DOM とロジックの分離

- タイマー計算と状態遷移は DOM 非依存にする
- UI テストは最小限に抑え、ロジックは単体テストで検証する

### 純粋関数の活用

- モード遷移
- 長休憩判定
- 日次集計更新
- 初期表示データ生成

これらは副作用なしで実装し、入力と出力だけを検証できるようにする。

## 推奨ディレクトリ構成

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

## UI 実装メモ

- 円形プログレスは SVG の `circle` を使って実装する
- 色、余白、角丸、シャドウは CSS 変数化する
- モックの主要要素は、ヘッダー、モード表示、円形タイマー、操作ボタン、今日の進捗カードの 5 ブロックで構成する

## 将来拡張

この構成で次の拡張に対応しやすい。

- 通知音とブラウザ通知
- 設定画面
- セッション履歴表示
- 週次、月次の統計表示

複数端末同期やユーザー認証が必要になった場合は、その段階でサーバー側がアクティブタイマーの状態を持つ構成へ拡張する。