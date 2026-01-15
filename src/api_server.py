"""
Simple API server for TTS Dashboard control interface.
Provides endpoints for controlling the Kokoro processor and playback.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sock import Sock
import subprocess
import os
import time
import json
import threading

app = Flask(__name__)
CORS(app)
sock = Sock(app)

# Configuration
DATA_DIR = "/app/data"
TODO_DIR = os.path.join(DATA_DIR, "todo")
WORKING_DIR = os.path.join(DATA_DIR, "working")
DONE_DIR = os.path.join(DATA_DIR, "done")

# State
current_status = {
    "connected": True,
    "processing": False,
    "current_file": None,
    "queue_count": 0
}

websocket_clients = []

def broadcast_status():
    """Broadcast current status to all connected WebSocket clients"""
    message = json.dumps(current_status)
    for ws in websocket_clients[:]:
        try:
            ws.send(message)
        except:
            websocket_clients.remove(ws)

def update_status():
    """Update the current status based on file system"""
    try:
        working_files = [f for f in os.listdir(WORKING_DIR) if os.path.isfile(os.path.join(WORKING_DIR, f))]
        todo_files = [f for f in os.listdir(TODO_DIR) if os.path.isfile(os.path.join(TODO_DIR, f))]

        current_status["processing"] = len(working_files) > 0
        current_status["current_file"] = working_files[0] if working_files else None
        current_status["queue_count"] = len(todo_files)

        broadcast_status()
    except Exception as e:
        print(f"Error updating status: {e}")

def status_monitor_loop():
    """Background thread to monitor status"""
    while True:
        update_status()
        time.sleep(1)

# Start background monitor
monitor_thread = threading.Thread(target=status_monitor_loop, daemon=True)
monitor_thread.start()

@sock.route('/ws')
def websocket(ws):
    """WebSocket endpoint for real-time updates"""
    websocket_clients.append(ws)
    try:
        # Send initial status
        ws.send(json.dumps(current_status))

        # Keep connection alive
        while True:
            data = ws.receive()
            if data is None:
                break
    except:
        pass
    finally:
        if ws in websocket_clients:
            websocket_clients.remove(ws)

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current status"""
    update_status()
    return jsonify(current_status)

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get list of completed files"""
    try:
        files = []
        for f in os.listdir(DONE_DIR):
            if os.path.isfile(os.path.join(DONE_DIR, f)):
                path = os.path.join(DONE_DIR, f)
                mtime = os.path.getmtime(path)
                files.append({
                    "filename": f,
                    "timestamp": int(mtime * 1000),  # milliseconds
                    "size": os.path.getsize(path)
                })

        # Sort by timestamp descending
        files.sort(key=lambda x: x["timestamp"], reverse=True)
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/control', methods=['POST'])
def control():
    """Control playback (pause, resume, stop)"""
    try:
        data = request.json
        command = data.get('command')

        if command == 'pause':
            # For now, pause is not implemented in the processor
            # We could implement this by stopping file monitoring temporarily
            return jsonify({"status": "success", "message": "Pause not yet implemented"})

        elif command == 'resume':
            # Resume is also not implemented
            return jsonify({"status": "success", "message": "Resume not yet implemented"})

        elif command == 'stop':
            # Emergency stop: move all working files to done
            try:
                working_files = [f for f in os.listdir(WORKING_DIR) if os.path.isfile(os.path.join(WORKING_DIR, f))]
                for f in working_files:
                    src = os.path.join(WORKING_DIR, f)
                    dst = os.path.join(DONE_DIR, f)
                    os.rename(src, dst)

                update_status()
                return jsonify({"status": "success", "message": f"Stopped {len(working_files)} files"})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500

        else:
            return jsonify({"status": "error", "message": "Unknown command"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/defaults', methods=['POST'])
def set_defaults():
    """Set default voice and speed"""
    try:
        data = request.json
        voice = data.get('voice')
        speed = data.get('speed')

        # For now, we just acknowledge the request
        # To actually implement this, we'd need to modify the processor
        # to read default settings from a config file

        return jsonify({
            "status": "success",
            "message": "Defaults updated (not yet applied to processor)",
            "voice": voice,
            "speed": speed
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/server', methods=['POST'])
def server_control():
    """Start or stop the Kokoro server"""
    try:
        data = request.json
        command = data.get('command')

        if command == 'start':
            # Check if processor is already running
            # For now, we'll just return success
            # In a real implementation, we'd need to manage the processor process
            return jsonify({
                "status": "success",
                "message": "Kokoro server start requested (manual start required)"
            })

        elif command == 'stop':
            # Stop the processor
            # This is tricky because the processor might be running in another container
            return jsonify({
                "status": "success",
                "message": "Kokoro server stop requested (manual stop required)"
            })

        else:
            return jsonify({"status": "error", "message": "Unknown command"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs(TODO_DIR, exist_ok=True)
    os.makedirs(WORKING_DIR, exist_ok=True)
    os.makedirs(DONE_DIR, exist_ok=True)

    print("Starting API Server on port 3021...")
    app.run(host='0.0.0.0', port=3021, debug=False)
