#!/bin/bash
BASE_URL="http://localhost:8000"
DOC_ID="7ebbc628-4158-4a0e-b854-38867417870e"
Q3="LAN, MAN, WAN ஆகியவற்றுக்கு இடையேயான வேறுபாடு என்ன, மற்றும் Transport layer-ல் எந்த protocols பயன்படுத்தப்படுகின்றன?"
START=$(date +%s)
curl -s --max-time 240 -X POST "$BASE_URL/answer/ask" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$Q3\", \"top_k\": 5, \"document_id\": \"$DOC_ID\"}"
END=$(date +%s)
echo
echo "(took $((END-START))s)"
