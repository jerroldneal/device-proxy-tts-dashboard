Write-Host "Starting TTS Kokoro Processor..."
Set-Location "$PSScriptRoot\..\tts-kokoro-processor"
docker-compose up -d

Write-Host "Starting TTS Dashboard..."
Set-Location "$PSScriptRoot\..\tts-dashboard"
docker-compose up -d

Write-Host "All services started."
Write-Host "Dashboard available at http://localhost:7860"
Set-Location "$PSScriptRoot"
