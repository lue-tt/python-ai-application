# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 概要

Python + Streamlit + Gemini API(`google-genai`)の個人用AIライティングツール。DB・認証なし。テスト・リンタ・ビルド設定はない。

## 作業方針

- 回答は日本語で行う。
- 依存パッケージを勝手に増やさない(`requirements.txt` への追加は事前に確認する)。
- コミットする前に必ずユーザーに確認する。

## コマンド

```powershell
py -3.12 -m venv .venv                              # Python 3.12 を使う(Windows ARM64 + 3.14 では pandas/pyarrow の wheel が無く入らない)
.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env                              # GEMINI_API_KEY を記入(未設定ならサイドバーで入力可)
.venv\Scripts\streamlit run app.py                  # 起動(http://localhost:8501)
```

非対話環境(バックグラウンド実行など)では、初回のメール入力プロンプトで終了するため、`~\.streamlit\credentials.toml` に `[general]` / `email = ""` を置き、`--server.headless true` を付けて起動する。

## アーキテクチャ

3ファイル構成で、ツール定義とUIが分離されている。

- `writing_tools.py` … 各ツールを `Tool` dataclass(`name` / `icon` / `fields: list[Field]` / `build_prompt` / `temperature`)として宣言し、`TOOLS` リストに並べる。`SYSTEM_INSTRUCTION`(前置き禁止・不明点は【要確認】)も全ツール共通でここにある。
- `app.py` … `TOOLS` を走査してタブとフォームを自動生成する。ツール固有のUIコードは持たない。`Field.kind` は `text` / `textarea` / `select` / `slider` で、`render_field` が対応する。
- `gemini_client.py` … `stream_text()` が Gemini のストリーミング応答を yield する。モデル候補(`MODEL_CHOICES` / `DEFAULT_MODEL`)もここ。APIキーは `GEMINI_API_KEY` または `GOOGLE_API_KEY` を参照する。

**ツール追加は `writing_tools.py` に `_xxx(v: dict) -> str` のプロンプト関数と `Tool(...)` を足すだけ。`app.py` は変更不要。** 新しい入力種別が必要な場合のみ `app.py` の `render_field` に `kind` を追加する。

### 実装上の注意点

- ウィジェットのキーは `"{tool.name}:{field.key}"`、実行ボタンは `run:{tool.name}`、直近結果は `session_state["last:{tool.name}"]`。ツール名を変えるとこれらも変わる。
- 生成成功後に `st.rerun()` で再描画し、履歴(`session_state["history"]`、最大 `MAX_HISTORY`=30件)と保存/コピー表示を反映する。結果の表示は `last:` キー経由なので、rerun 前後で表示が二重にならないようにしている。
- 必須入力(`Field.required`)の検証は `app.py` 側で行う。`build_prompt` は `values[key]` が必ず存在する前提で書かれている。
- `_opt(label, value)` は空値の行を出力しないヘルパー。任意項目のプロンプト組み立てに使う。
- プロンプトと UI の文言は日本語。
