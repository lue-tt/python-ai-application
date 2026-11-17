# AIライティングツール

Python + Streamlit + Gemini API の個人用ライティングツール(DB・認証なし)。

## GitHub

- リポジトリ: https://github.com/lue-tt/python-ai-application (Private)
- ブランチ: `main`

```powershell
git clone https://github.com/lue-tt/python-ai-application.git
```

## セットアップ

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env   # GEMINI_API_KEY を記入(未設定ならサイドバーで入力可)
```

> Windows ARM64 + Python 3.14 では pandas/pyarrow のwheelが無く入らないため、Python 3.12 を使用。

## 起動

```powershell
.venv\Scripts\streamlit run app.py
```

## 機能

ブログ記事 / メール返信 / 要約 / 校正・推敲 / リライト・文体変換 / タイトル案 / SNS投稿 / 翻訳 / ネタ出し

## 構成

- `app.py` … UI(ツール定義からフォームを自動生成)
- `writing_tools.py` … 各ツールの入力項目とプロンプト。**ツール追加はここに `Tool` を足すだけ**
- `gemini_client.py` … Gemini API(ストリーミング)。モデル候補もここ
