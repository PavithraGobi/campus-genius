#!/bin/bash
BASE_URL="http://localhost:8000"
DOC_ID="7ebbc628-4158-4a0e-b854-38867417870e"
Q4="இந்த ஆவணத்தில் database normalization பற்றி என்ன சொல்லப்பட்டுள்ளது?"
curl -s --max-time 30 -X POST "$BASE_URL/answer/ask" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$Q4\", \"top_k\": 5, \"document_id\": \"$DOC_ID\"}"
echo
