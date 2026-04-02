# アーキテクチャ概要

> **実装状況（現在）**: Step 1 完了時点。Flask アプリの骨組みが完成した状態。

## 現在の構成

```text
Browser
  └─ HTML/CSS (templates/index.html, static/css/style.css)
       ↕ HTTP
Flask (app.py)
  └─ GET / → render_template("index.html")
```

JavaScript モジュール（`static/js/`）は HTML にリンクされているが、中身はすべてスタブ（実装予定コメントのみ）。

バックエンドの Service・Domain・Repository 各層もスタブ状態のみ。

---

## ファイル構成（現在）

```text
1.pomodoro/
├── app.py                        # Flask アプリファクトリ（create_app）
├── templates/
│   └── index.html                # メイン画面テンプレート（Step 1 骨格）
├── static/
│   ├── css/
│   │   └── style.css             # 基本スタイル（背景・カード・タイポグラフィ）
│   └── js/
│       ├── timer-engine.js       # タイマーエンジン（未実装）
│       ├── pomodoro-state.js     # 状態管理（未実装）
│       ├── pomodoro-ui.js        # UI 描画（未実装）
│       └── pomodoro-api.js       # Flask API 連携（未実装）
├── domain/
│   └── pomodoro_rules.py         # ドメインルール（未実装）
├── services/
│   ├── stats_service.py          # 統計サービス（未実装）
│   └── settings_service.py      # 設定サービス（未実装）
├── repositories/
│   ├── stats_repository.py      # 統計リポジトリ（未実装）
│   └── settings_repository.py  # 設定リポジトリ（未実装）
└── tests/
    ├── conftest.py              # テスト設定（sys.path 調整）
    ├── test_api.py              # API テスト（Flask インスタンス・ルート検証）
    ├── test_pomodoro_rules.py   # ドメインルールテスト（未実装）
    └── test_stats_service.py    # 統計サービステスト（未実装）
```

---

## `app.py` の構成

```python
from pathlib import Path
from flask import Flask, render_template

BASE_DIR = Path(__file__).resolve().parent

def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    return app

app = create_app()
```

- `create_app()` はアプリファクトリパターンで Flask インスタンスを生成する。
- `template_folder` と `static_folder` は `BASE_DIR` を基準にした絶対パスで設定する。
- `app = create_app()` によりモジュールレベルのインスタンスも公開しており、`flask run` から起動できる。

---

## 設計上の方針（`architecture.md` より）

将来実装される全体像は以下の 4 層構成を想定している。

| 層 | 役割 |
|----|------|
| Routes | リクエスト/レスポンスの変換のみ担当、業務ロジックを持たない |
| Services | 進捗更新・設定保存・セッション完了記録を担当 |
| Domain Logic | 副作用のない純粋関数でモード遷移・ルール判定を実装 |
| Repositories | SQLite を使った設定・統計・セッション履歴の永続化 |

フロントエンドは Vanilla JavaScript で 4 モジュール（Timer Engine / State / UI / API）に分割する設計。
