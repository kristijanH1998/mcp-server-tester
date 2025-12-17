curl -X POST http://127.0.0.1:8000/call \
  -H "Content-Type: application/json" \
  -d '{"tool":"echo","arguments":{"message":"Hello World!"}}'

