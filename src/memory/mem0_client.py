import os

from dotenv import load_dotenv
from mem0 import Memory

load_dotenv()

MEM0_CONFIG = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": os.getenv("MEM0_LLM_MODEL", "gpt-4o-mini"),
            "temperature": 0.0,
            "api_key": os.getenv("OPENAI_API_KEY"),
        },
    }
}
# ✅ single shared memory instance
memory = Memory.from_config(MEM0_CONFIG)

# -------------------------------
# ✅ Add functions per memory type
# -------------------------------


def add_team_context(content: str):
    memory.add(content, user_id="team_context")


def add_worktype_glossary(content: str):
    memory.add(content, user_id="worktype_glossary")


def add_historical_cr(content: str):
    memory.add(content, user_id="historical_cr")


# -------------------------------
# ✅ Retrieval functions
# -------------------------------


def search_team_context(query: str, top_k: int = 5):
    query = (query or "").strip()
    if not query:
        return []
    return memory.search(query, filters={"user_id": "team_context"}, limit=top_k)


def search_worktype_glossary(query: str, top_k: int = 5):
    query = (query or "").strip()
    if not query:
        return []
    return memory.search(query, filters={"user_id": "worktype_glossary"}, limit=top_k)


def search_historical_cr(query: str, top_k: int = 5):
    query = (query or "").strip()
    if not query:
        return []
    return memory.search(
        query,
        filters={"user_id": "historical_cr"},
        limit=top_k,
    )
