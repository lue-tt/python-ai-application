"""AIライティングツール (Streamlit + Gemini API)

起動: streamlit run app.py
"""

from __future__ import annotations

from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from gemini_client import DEFAULT_MODEL, MODEL_CHOICES, get_api_key, stream_text
from writing_tools import SYSTEM_INSTRUCTION, TOOLS, Field, Tool

load_dotenv()

st.set_page_config(page_title="AIライティングツール", page_icon="✍️", layout="wide")

MAX_HISTORY = 30


# ---------------------------------------------------------------- 部品
def render_field(tool: Tool, f: Field):
    key = f"{tool.name}:{f.key}"
    if f.kind == "textarea":
        return st.text_area(f.label, key=key, height=200, placeholder=f.placeholder, help=f.help or None)
    if f.kind == "select":
        idx = f.options.index(f.default) if f.default in f.options else 0
        return st.selectbox(f.label, f.options, index=idx, key=key, help=f.help or None)
    if f.kind == "slider":
        return st.slider(f.label, f.min_value, f.max_value, int(f.default), f.step, key=key)
    return st.text_input(f.label, key=key, placeholder=f.placeholder, help=f.help or None)


def show_result(text: str, tool_name: str, key: str) -> None:
    st.markdown(text)
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "💾 テキストで保存",
            data=text,
            file_name=f"{tool_name}_{datetime.now():%Y%m%d_%H%M%S}.txt",
            key=f"dl_{key}",
        )
    with st.expander("コピー用テキスト(右上のアイコンでコピー)"):
        st.code(text, language=None, wrap_lines=True)


def sidebar() -> tuple[str, str]:
    with st.sidebar:
        st.title("✍️ AIライティング")
        env_key = get_api_key()
        api_key = env_key
        if not env_key:
            api_key = st.text_input("Gemini APIキー", type="password", help="または .env に GEMINI_API_KEY を設定")
        else:
            st.caption("🔑 APIキー: 環境変数から読み込み済み")
        model = st.selectbox("モデル", MODEL_CHOICES, index=MODEL_CHOICES.index(DEFAULT_MODEL))

        st.divider()
        st.subheader("履歴(このセッション)")
        history = st.session_state.get("history", [])
        if not history:
            st.caption("まだ履歴はありません")
        for i, h in enumerate(history):
            with st.expander(f"{h['time']} {h['tool']}"):
                st.markdown(h["text"])
        if history and st.button("履歴を消去"):
            st.session_state.history = []
            st.rerun()
    return api_key, model


# ---------------------------------------------------------------- メイン
def main() -> None:
    api_key, model = sidebar()

    st.header("AIライティングツール")
    tabs = st.tabs([f"{t.icon} {t.name}" for t in TOOLS])

    for tool, tab in zip(TOOLS, tabs):
        with tab:
            st.caption(tool.description)
            values = {f.key: render_field(tool, f) for f in tool.fields}

            if st.button("生成する", type="primary", key=f"run:{tool.name}"):
                missing = [f.label for f in tool.fields if f.required and not str(values[f.key]).strip()]
                if missing:
                    st.warning(f"入力してください: {', '.join(missing)}")
                elif not api_key:
                    st.error("Gemini APIキーを設定してください(サイドバー、または .env)。")
                else:
                    try:
                        with st.spinner("生成中..."):
                            stream = stream_text(
                                api_key=api_key,
                                model=model,
                                prompt=tool.build_prompt(values),
                                system_instruction=SYSTEM_INSTRUCTION,
                                temperature=tool.temperature,
                            )
                            text = st.write_stream(stream)
                    except Exception as e:  # APIキー誤り・レート制限・ネットワーク等
                        st.error(f"生成に失敗しました: {e}")
                    else:
                        history = st.session_state.setdefault("history", [])
                        history.insert(0, {"time": f"{datetime.now():%H:%M}", "tool": tool.name, "text": text})
                        del history[MAX_HISTORY:]
                        st.session_state[f"last:{tool.name}"] = text
                        st.rerun()  # 履歴・コピー/保存ボタンを反映するため再描画

            last = st.session_state.get(f"last:{tool.name}")
            if last:
                st.divider()
                show_result(last, tool.name, tool.name)


main()
