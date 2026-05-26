from pathlib import Path

from src.memory.mem0_client import (
    add_historical_cr,
    add_team_context,
    add_worktype_glossary,
)


def load_file(path):
    return Path(path).read_text(encoding="utf-8")


def main():
    print("🚀 Bootstrapping Mem0 memory...")

    team = load_file("data/memory_seed/team_context.md")
    glossary = load_file("data/memory_seed/worktype_glossary.md")
    historical = load_file("data/memory_seed/historical_crs.md")

    add_team_context(team)
    add_worktype_glossary(glossary)
    add_historical_cr(historical)

    print("✅ Memory loaded into Mem0")


if __name__ == "__main__":
    main()
