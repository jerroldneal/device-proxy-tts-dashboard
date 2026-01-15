#!/bin/bash

# Start both the Gradio dashboard and the API server

echo "Starting API Server on port 3021..."
python /app/src/api_server.py &
API_PID=$!

echo "Waiting for API server to be ready..."
sleep 2

echo "Starting Gradio Dashboard on port 7860..."
python /app/src/main.py &
GRADIO_PID=$!

echo "Both services started"
echo "API Server PID: $API_PID"
echo "Gradio Dashboard PID: $GRADIO_PID"

# Wait for both processes
wait $API_PID $GRADIO_PID
