"""Compound question decomposition for Ask.

A cheap rule-based heuristic gates an LLM call: genuinely single questions
(the common case - this is what Test 1 and Test 2 exercise) skip the LLM
call entirely and behave exactly as they did before this module existed.
Only questions that look compound trigger a decomposition call.

Fails safe throughout: if the heuristic misses something, or the LLM call
or its output can't be parsed, the original query is used unchanged as a
single "sub-question" - so this can never make a question harder to answer
than it already was, only better for genuinely compound ones.
"""

import json

from app.services.ollama_client import ollama_client

# Deliberately conservative - narrow signals only, not a bare split on "and",
# since "and" is often part of the content itself (e.g. "TCP and UDP") rather
# than a signal that two distinct questions are being asked.
_COMPOUND_SIGNALS = [
    " and which ",
    " and what ",
    " and where ",
    " and how ",
    " and why ",
]


def _looks_compound(query: str) -> bool:
    if query.count("?") > 1:
        return True
    lowered = query.lower()
    if any(signal in lowered for signal in _COMPOUND_SIGNALS):
        return True
    # Tamil "and" (மற்றும்) combined with a comma is a reasonably reliable
    # compound signal in this document domain - e.g. "X ஆகியவற்றுக்கு
    # இடையேயான வேறுபாடு என்ன, மற்றும் Y-ல் எந்த protocols பயன்படுத்தப்படுகின்றன?"
    return "மற்றும்" in query and query.count(",") >= 1


SYSTEM_PROMPT = """You split compound academic questions into standalone sub-questions.
Rules:
- If the question asks about more than one distinct topic, split it into separate, independently answerable questions.
- Preserve the original language and wording of each part as closely as possible.
- If it's actually a single question, return it unchanged as the only item.
- Do not answer the question. Only split it.
Output format:
- Respond with ONLY a JSON array of strings. No prose, no markdown fences, no explanation.
Example:
["What is the difference between LAN, MAN, and WAN?", "Which protocols are used at the Transport layer?"]"""


def _parse_sub_questions(raw_text: str, original_query: str) -> list[str]:
    text = raw_text.strip()

    if text.startswith("```"):
        text = text.strip("`").strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()

    if not text.startswith("["):
        start, end = text.find("["), text.rfind("]")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]

    try:
        data = json.loads(text)
        sub_questions = [str(item).strip() for item in data if str(item).strip()]
        if sub_questions:
            return sub_questions
    except (json.JSONDecodeError, TypeError):
        pass

    # Any failure here just falls back to treating it as one question -
    # same behavior as if decomposition didn't exist at all.
    return [original_query]


def decompose_query(query: str) -> list[str]:
    """Split a compound question into standalone sub-questions.

    Returns [query] unchanged for questions that don't look compound (fast
    path, no LLM call, no added latency), or if decomposition fails for any
    reason (fail-safe, no crash).
    """
    if not _looks_compound(query):
        return [query]

    try:
        raw_text = ollama_client.chat(SYSTEM_PROMPT, f"Question: {query}")
    except Exception:
        return [query]

    return _parse_sub_questions(raw_text, query)
