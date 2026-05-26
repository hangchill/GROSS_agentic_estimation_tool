def mem_results_to_text(results) -> str:
    """
    Normalize Mem0 search results into a newline-joined text block.

    Mem0 may return:
    - list[str]
    - list[dict] with keys like 'memory' or 'text'
    - list[objects] with attributes like .memory or .text
    """
    if not results:
        return ""

    texts = []

    for r in results:
        if isinstance(r, str):
            texts.append(r.strip())
            continue

        if isinstance(r, dict):
            texts.append((r.get("memory") or r.get("text") or "").strip())
            continue

        # fallback for objects
        mem = getattr(r, "memory", None)
        txt = getattr(r, "text", None)
        if mem:
            texts.append(str(mem).strip())
        elif txt:
            texts.append(str(txt).strip())
        else:
            texts.append(str(r).strip())

    # remove empty lines
    texts = [t for t in texts if t]
    return "\n".join(texts)
