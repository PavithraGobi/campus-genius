# Query Decomposition for Compound Questions — backend patch (v2)

## v2 update: fixed real truncation bug found during your live test
Your screenshot showed the answer cutting off mid-word ("இணைக") right before
ever reaching part 2 (Transport layer protocols) - not a scroll/UI issue.
Root cause: app/services/ollama_client.py has always capped every response
to num_predict: 250 tokens. That was fine for short single-topic answers,
but a genuine multi-part answer needs more room. Raised to 600.

Estimated cost using your own measured Ollama speed (189ms/token from your
earlier direct test): ~113s generation at 600 tokens vs ~47s at 250 - plus
prompt processing and the decomposition call, still comfortably under your
300s timeout.

## Files in this patch
- app/services/query_decomposition.py -> NEW file
- app/services/answer_service.py      -> REPLACE existing file
- app/services/ollama_client.py       -> REPLACE existing file (only the
  num_predict value changed, 250 -> 600, nothing else touched)

## Why this exists (query decomposition)
Test 3 ("difference between LAN/MAN/WAN, and which Transport-layer protocols")
was marked passing, but the saved result only answered half the question -
it worked only because the small test document let top_k=5 pull nearly the
whole doc by accident. On a larger document, the two topics might not both
land in one top_k window - silently dropping half the answer.

## How it works
1. Cheap rule-based check gates an LLM call - simple questions (Test 1/2
   style) get zero added latency, exactly as before.
2. Compound-looking questions trigger one small LLM call to split into
   standalone sub-questions.
3. Each sub-question is retrieved SEPARATELY and merged/de-duplicated - the
   actual fix for missed-topic risk on larger documents.
4. Final prompt explicitly numbers each part, instructing the model not to
   skip any of them.

## What was actually tested
- _looks_compound tested against 5 cases including "TCP and UDP" (correctly
  NOT flagged) and the real Test 3 question (correctly flagged)
- Full generate_answer() tested with mocked retrieval simulating a larger
  document (top_k=1) where single-pass retrieval would miss one topic -
  confirmed both topics now merge into context correctly
- Single-question fast path verified BYTE-IDENTICAL prompt to the
  pre-decomposition version, exactly 1 Ollama call (no added latency)
- Confirmed via live user testing: the LAN/MAN/WAN part of the real Test 3
  question now genuinely explains the differences (not just names them) -
  first real proof this fix works, not just mocked tests
- Full app boot-tested after all three file changes - still registers all
  6 routes correctly

## Known limitation
Whether part 2 (Transport layer protocols) is now included in the FULL
answer after the num_predict fix - not yet confirmed, since the previous
test was cut off before reaching it. That's the next thing to check.

## Test after applying
1. Restart backend
2. Re-run the exact Test 3 question again
3. Check: does the FULL answer now cover BOTH parts (LAN/MAN/WAN
   difference AND Transport layer protocols) without cutting off?
4. Re-check Test 1/Test 2 style simple questions still work normally
5. Re-check "what is TCP and UDP" still stays single-pass (not split)
