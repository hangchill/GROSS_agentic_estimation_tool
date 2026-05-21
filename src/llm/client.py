from __future__ import annotations

import json
import os
import re
from typing import Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


class LLMClient:
    def __init__(self, model: str | None = None):
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        self.llm = ChatOpenAI(
            model=self.model,
            temperature=0,
        )

    def json_call(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = self.llm.invoke(messages)
        content = response.content or "{}"

        return self._parse_json(content)

    @staticmethod
    def _parse_json(content: str) -> dict:
        cleaned = content.strip()

        # ✅ extract from markdown ```json blocks
        match = re.search(r"```(?:json)?\s*(.*?)```", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1).strip()

        # ✅ remove any extra text
        cleaned = cleaned.replace("Here is the JSON:", "").strip()

        try:
            return json.loads(cleaned)

        except json.JSONDecodeError:
            print("\n❌ JSON PARSE ERROR")
            print("Raw content:\n", content)
            print("Cleaned content:\n", cleaned)
            raise
