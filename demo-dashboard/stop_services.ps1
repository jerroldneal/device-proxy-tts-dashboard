Write-Host "Stopping TTS Dashboard..."
Set-Location "$PSScriptRoot\..\tts-dashboard"
docker-compose down

Write-Host "Stopping TTS Kokoro Processor..."
Set-Location "$PSScriptRoot\..\tts-kokoro-processor"
docker-compose down

Write-Host "All services stopped."
Set-Location "$PSScriptRoot"
