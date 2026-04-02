# フロントエンドモジュール

> **実装状況（現在）**: Step 1 完了時点。JS モジュールはすべてスタブ（実装予定コメントのみ）。CSS は基本スタイルが実装済み。

---

## HTML テンプレート

### `templates/index.html`

Flask の `render_template("index.html")` で返される単一ページのテンプレート。

**現在の構成:**

- `<link>` で `static/css/style.css` を読み込む
- `<main class="page-shell">` 内に `<section class="card">` が 1 つあり、Step 1 の骨格メッセージを表示する
- `<body>` 末尾で以下の順に JS を読み込む:
  1. `static/js/timer-engine.js`
  2. `static/js/pomodoro-state.js`
  3. `static/js/pomodoro-ui.js`
  4. `static/js/pomodoro-api.js`

---

## CSS

### `static/css/style.css`

| クラス / セレクタ | 説明 |
|------------------|------|
| `:root` | フォント（Noto Sans JP）、グラデーション背景（紫系）、基本文字色を定義 |
| `*` | `box-sizing: border-box` を全要素に適用 |
| `body` | `min-height: 100vh`、マージンなし |
| `.page-shell` | CSS Grid で画面中央にコンテンツを配置、`padding: 24px` |
| `.card` | 白背景・角丸・影つきのカードコンテナ、最大幅 480px |
| `.eyebrow` | 小文字大文字変換・太字・紫色のラベルテキスト |
| `h1` | `clamp` で可変フォントサイズ（2rem〜2.6rem） |
| `.lead` | 補足説明テキスト、`line-height: 1.7` |

---

## JavaScript モジュール（設計済み・未実装）

以下の 4 モジュールは `index.html` にリンクされているが、現時点では実装予定コメントのみ。

### `static/js/timer-engine.js`

- **役割**: タイマーのカウントダウン計算と状態遷移（`idle / running / paused / finished`）を担当
- **設計方針**: `Date.now()` の差分で残り秒数を算出し、単純減算によるドリフトを回避する
- **実装ステップ**: Step 3

### `static/js/pomodoro-state.js`

- **役割**: 現在モード・残り時間・完了回数・今日の集中時間などの画面状態を管理
- **設計方針**: `localStorage` と連携し、ページ再読み込み後の状態復元に対応する
- **実装ステップ**: Step 4

### `static/js/pomodoro-ui.js`

- **役割**: DOM 更新のみを担当する UI 描画モジュール
- **設計方針**: ロジックは持たず、State の内容を表示へ反映する。円形プログレス（SVG）、ボタン活性制御、今日の進捗カードを描画する
- **実装ステップ**: Step 2

### `static/js/pomodoro-api.js`

- **役割**: Flask API との HTTP 通信を担当
- **設計方針**: 初期状態取得・設定保存・セッション完了記録・集計更新を fetch API で処理する
- **実装ステップ**: Step 9
