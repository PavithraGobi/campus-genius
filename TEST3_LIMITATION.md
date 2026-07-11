# Known Limitation: Compound Question Handling

## Summary

Campus Genius reliably handles single-fact queries (Tamil, English, and
Tanglish) and correctly triggers the insufficient-context fallback for
out-of-scope questions. On **compound questions where the source document
only partially covers the topic** — specifically, where a term is named
but never defined — the local LLM occasionally either fabricates a
plausible-sounding definition or over-refuses the entire question, rather
than cleanly separating the supported and unsupported parts.

## Example

**Test document:** `tamil_networks_notes.pdf` (defines LAN and WAN, but
only *names* MAN without defining it)

**Query:**
> LAN, MAN, WAN ஆகியவற்றுக்கு இடையேயான வேறுபாடு என்ன, மற்றும் Transport
> layer-ல் எந்த protocols பயன்படுத்தப்படுகின்றன?
> (*"What is the difference between LAN, MAN, WAN, and which protocols
> does the Transport layer use?"*)

**Expected behavior:** Correctly define LAN and WAN, explicitly state
that MAN is not defined in the source, and correctly name TCP/UDP for
the Transport layer.

**Observed behavior (across multiple test runs):** The model reliably
gets LAN, WAN, and the TCP/UDP protocol answer correct. For MAN
specifically, it has fabricated several different plausible-sounding but
incorrect definitions rather than stating the term is undefined, and in
some configurations over-refused the entire question instead.

## Root Cause Analysis

This was tested across multiple system prompt formulations (explicit
"do not guess" instructions, mandatory per-claim citations, multi-part
answer templates) and multiple sampling temperatures (default, 0.1, 0.3).
Retrieval itself remained accurate and well-ranked in every single test —
the correct source chunks were always retrieved with strong similarity
scores. The failure is isolated to the generation step.

This points to a **capacity limitation of the local 7B quantized model**
(`qwen2.5:7b-instruct`, running CPU-only) rather than a prompt engineering
or retrieval defect. Small instruction-tuned models are known to struggle
with the specific nuance of "answer part of a compound question while
explicitly flagging the unanswerable part" — a task that requires more
reliable instruction-following than pure factual recall.

## What Was Tried

- Multiple system prompt rewrites (explicit undefined-term handling,
  mandatory citations, partial-answer instructions)
- Temperature adjustment (default → 0.1 → 0.3)
- Output length capping (`num_predict`) to rule out truncation
- Query decomposition (`compound_handler.py`) — early-stage implementation
  exists but has a known bug: comma-splitting on the LAN/MAN/WAN list
  fragments it into isolated single-word sub-questions (e.g. "MAN" alone,
  with no surrounding context), which likely contributes to the
  hallucination on that specific term

## Recommended Path Forward (not implemented — out of scope for this phase)

1. Fix the comma-splitting logic in `compound_handler.py` to treat
   comma-separated acronym lists (e.g. "LAN, MAN, WAN") as a single unit
   rather than splitting on every comma
2. Add a similarity-threshold gate to per-sub-question retrieval,
   matching the safeguard already in place for single-question queries
3. Longer term: evaluate a larger or hosted model for the generation step,
   since the failure pattern is consistent with small-model capacity
   limits rather than a fixable prompt/retrieval issue

## Impact

This limitation affects a narrow category of queries: compound questions
where the source document names but does not define one of several
related terms. It does not affect single-fact queries, Tanglish queries,
or the out-of-scope refusal behavior, all of which were verified working
correctly and consistently.
