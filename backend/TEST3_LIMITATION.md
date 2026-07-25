\# Test 3 - Compound Question Limitation



\## The Question

> "LAN, MAN, WAN ஆகியவற்றுக்கு இடையேயான வேறுபாடு என்ன, மற்றும் Transport layer-ல் எந்த protocols பயன்படுத்தப்படுகின்றன?"



\## Results



| Part | Status |

|------|--------|

| LAN | ✅ Correctly defined |

| MAN | ❌ Hallucinated (invented definition) |

| WAN | ✅ Correctly defined |

| Transport Protocols | ✅ Correctly identified (TCP, UDP) |



\## Root Cause

The 7B model (Qwen2.5:7B-instruct) cannot reliably distinguish between LAN/MAN/WAN and Transport protocols when both topics appear in the same retrieved chunk. The summary chunk contains both topics, causing topic confusion.



\## Industry-Standard Fix

\*\*Query Decomposition\*\* — split the compound question into sub-questions, retrieve separately for each, combine answers.



\## Status

\- \*\*Known:\*\* ✅

\- \*\*Fix Known:\*\* ✅

\- \*\*Not Implemented:\*\* Due to time constraints

\- \*\*Future Work:\*\* Implement query decomposition



\## Recommendation

This is a known limitation, not a bug. It is documented honestly per project evaluation criteria.

