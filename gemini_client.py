"""Gemini API の薄いラッパー。"""

from __future__ import annotations

import os
from typing import Iterator

from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-3.8-flash"
MODEL_CHOICES = ["gemini-3.8-flash", "gemini-2.5-pro", "gemini-2.5-flash-lite"]


def get_api_key() -> str:
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""


def _strip_images(chunks: Iterator[str]) -> Iterator[str]:
    """Markdown画像記法 `![` の `!` を落とし、外部画像の自動読み込み(情報の持ち出し)を防ぐ。

    リンク `[alt](url)` になるだけで自動では読み込まれない。チャンク境界の `!` は次へ持ち越す。
    """
    carry = ""
    for chunk in chunks:
        text = (carry + chunk).replace("![", "[")
        carry = "!" if text.endswith("!") else ""
        if carry:
            text = text[:-1]
        if text:
            yield text
    if carry:
        yield carry


def stream_text(
    *,
    api_key: str,
    model: str,
    prompt: str,
    system_instruction: str,
    temperature: float,
) -> Iterator[str]:
    """テキストを逐次yieldする。"""
    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=temperature,
    )
    raw = (
        chunk.text
        for chunk in client.models.generate_content_stream(
            model=model, contents=prompt, config=config
        )
        if chunk.text
    )
    yield from _strip_images(raw)
