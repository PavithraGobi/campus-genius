#!/bin/bash
BASE_URL="http://localhost:8000"
DOC_ID="7ebbc628-4158-4a0e-b854-38867417870e"

ask() {
  echo "=== ASK: $1 ==="
  START=$(date +%s)
  curl -s --max-time 180 -X POST "$BASE_URL/answer/ask" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"$1\", \"top_k\": 5, \"document_id\": \"$DOC_ID\"}"
  END=$(date +%s)
  echo
  echo "(took $((END-START))s)"
  echo
}

Q1="IPv4 முகவரி எத்தனை பிட்கள் கொண்டது?"
ask "$Q1"

Q2="இந்த document-ல OSI model-ல எத்தனை layers இருக்கு?"
ask "$Q2"

Q3="LAN, MAN, WAN ஆகியவற்றுக்கு இடையேயான வேறுபாடு என்ன, மற்றும் Transport layer-ல் எந்த protocols பயன்படுத்தப்படுகின்றன?"
ask "$Q3"
