# データモデル仕様

> **実装状況（現在）**: Step 1 完了時点。データモデルの実装はなく、`repositories/` は未実装のスタブのみ。

---

## 未実装モデル（設計済み）

以下のモデルは `architecture.md` に設計として記載されているが、現時点でコードは存在しない。

### `settings`

アプリ全体の設定を保持する。

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `work_minutes` | integer | 作業セッションの長さ（分） |
| `short_break_minutes` | integer | 短休憩の長さ（分） |
| `long_break_minutes` | integer | 長休憩の長さ（分） |
| `cycles_before_long_break` | integer | 長休憩に入るまでの作業セッション回数 |

---

### `daily_stats`

日別の集計データを保持する。

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `date` | date | 集計対象の日付 |
| `completed_count` | integer | その日に完了した作業セッション数 |
| `focused_seconds` | integer | その日の合計集中時間（秒） |

---

### `session_log`

各セッションの実績ログを保持する。

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `started_at` | datetime | セッション開始日時 |
| `ended_at` | datetime | セッション終了日時 |
| `session_type` | string | セッション種別（`work` / `short_break` / `long_break`） |
| `completed` | boolean | セッションが完了したか否か |
