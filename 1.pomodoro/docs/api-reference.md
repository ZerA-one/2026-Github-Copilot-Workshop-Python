# API リファレンス

> **実装状況（現在）**: Step 1 完了時点。`GET /` のみ実装済み。`/api/*` エンドポイントは未実装。

## 実装済みエンドポイント

### `GET /`

メイン画面（`index.html`）を返す。

- **レスポンスコード**: `200 OK`
- **Content-Type**: `text/html`
- **説明**: Flask の `render_template("index.html")` で HTML ページを返す。

---

## 未実装エンドポイント（設計済み）

以下のエンドポイントは `architecture.md` に設計として記載されているが、現時点ではコードが存在しない。

| メソッド | パス | 説明 |
|---------|------|------|
| `GET` | `/api/state` | 初期表示用の状態と設定を取得 |
| `POST` | `/api/settings` | 作業時間・休憩時間などの設定を更新 |
| `POST` | `/api/session/complete` | 1 セッション完了を記録 |
| `POST` | `/api/session/reset` | 当日の進捗をリセット |
| `GET` | `/api/stats/today` | 今日の完了回数と集中時間を取得 |
