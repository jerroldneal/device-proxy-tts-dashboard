# TTS Dashboard

A Gradio-based web UI for managing the TTS workflow.

## Features

- **Todo Tab**: Create new text files to be spoken. View queued files.
- **Working Tab**: Automatically switches to this tab when a file is being processed. Shows the currently speaking file.
- **Done Tab**: View history of spoken files. Replay files (moves them back to Todo).

## Architecture

- **Frontend/Backend**: Python (Gradio)
- **Data**: Watches the shared volume `C:/.tts` (mounted at `/app/data`).

## Usage

### Build & Run

```bash
docker-compose up -d --build
```

Access the dashboard at `http://localhost:7860`.
