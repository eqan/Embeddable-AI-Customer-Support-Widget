#!/bin/bash

echo "Container Started"
source ~/.bashrc
ulimit -n 50000 &

cd /workspace/app


uvicorn app:app --host 0.0.0.0 --port 8000 --workers 16 --timeout-keep-alive 120 &

echo "Server Started"

sleep infinity
