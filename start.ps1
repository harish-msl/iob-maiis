# ============================================
# IOB MAIIS - Windows Startup Script
# Multimodal AI-Enabled Information System
# ============================================

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  IOB MAIIS - Starting Application" -ForegroundColor Cyan
Write-Host "  Multimodal AI-Enabled Information System" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if Docker is running
function Test-DockerRunning {
    try {
        $null = docker ps 2>&1
        return $true
    }
    catch {
        return $false
    }
}

# Function to wait for Docker
function Wait-ForDocker {
    param (
        [int]$TimeoutSeconds = 60
    )

    Write-Host "⏳ Waiting for Docker Desktop to start..." -ForegroundColor Yellow
    $elapsed = 0

    while (-not (Test-DockerRunning) -and $elapsed -lt $TimeoutSeconds) {
        Start-Sleep -Seconds 2
        $elapsed += 2
        Write-Host "." -NoNewline -ForegroundColor Yellow
    }

    Write-Host ""

    if (Test-DockerRunning) {
        Write-Host "✅ Docker Desktop is running" -ForegroundColor Green
        return $true
    }
    else {
        Write-Host "❌ Docker Desktop failed to start" -ForegroundColor Red
        return $false
    }
}

# Step 1: Check Docker Installation
Write-Host "📦 Checking Docker installation..." -ForegroundColor Cyan
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "✅ Docker installed: $dockerVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker is not installed!" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Step 2: Check if Docker is running
Write-Host ""
Write-Host "🐋 Checking Docker Desktop status..." -ForegroundColor Cyan

if (-not (Test-DockerRunning)) {
    Write-Host "⚠️  Docker Desktop is not running" -ForegroundColor Yellow
    Write-Host "🚀 Starting Docker Desktop..." -ForegroundColor Cyan

    # Try to start Docker Desktop
    try {
        Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe" -ErrorAction SilentlyContinue
    }
    catch {
        Write-Host "❌ Could not auto-start Docker Desktop" -ForegroundColor Red
        Write-Host "Please start Docker Desktop manually and run this script again" -ForegroundColor Yellow
        exit 1
    }

    # Wait for Docker to be ready
    if (-not (Wait-ForDocker -TimeoutSeconds 120)) {
        Write-Host "❌ Docker Desktop did not start in time" -ForegroundColor Red
        Write-Host "Please start Docker Desktop manually and run this script again" -ForegroundColor Yellow
        exit 1
    }
}
else {
    Write-Host "✅ Docker Desktop is already running" -ForegroundColor Green
}

# Step 3: Check for .env file
Write-Host ""
Write-Host "🔐 Checking environment configuration..." -ForegroundColor Cyan

if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found, creating from .env.example..." -ForegroundColor Yellow

    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Created .env file from template" -ForegroundColor Green
        Write-Host "⚠️  IMPORTANT: Review and update .env with your settings!" -ForegroundColor Yellow
    }
    else {
        Write-Host "❌ .env.example not found!" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "✅ .env file found" -ForegroundColor Green
}

# Step 4: Build and start services
Write-Host ""
Write-Host "🚀 Building and starting all services..." -ForegroundColor Cyan
Write-Host "   (This may take 5-10 minutes on first run)" -ForegroundColor Yellow
Write-Host ""

docker compose up -d --build

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "  ✅ IOB MAIIS Started Successfully!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""

    # Wait a bit for services to initialize
    Write-Host "⏳ Waiting for services to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5

    # Check service status
    Write-Host ""
    Write-Host "📊 Service Status:" -ForegroundColor Cyan
    docker compose ps

    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "  🌐 Access URLs:" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "  Frontend:      http://localhost:3000" -ForegroundColor White
    Write-Host "  API Docs:      http://localhost:8000/api/docs" -ForegroundColor White
    Write-Host "  Health Check:  http://localhost:8000/health" -ForegroundColor White
    Write-Host "  Grafana:       http://localhost:3001" -ForegroundColor White
    Write-Host "  Prometheus:    http://localhost:9090" -ForegroundColor White
    Write-Host "  MinIO Console: http://localhost:9001" -ForegroundColor White
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""

    # Check if Ollama models need to be downloaded
    Write-Host "🤖 Checking AI models..." -ForegroundColor Cyan
    $models = docker compose exec -T ollama ollama list 2>&1

    if ($models -notmatch "llama3.1") {
        Write-Host ""
        Write-Host "⚠️  AI models not found!" -ForegroundColor Yellow
        Write-Host "You need to download models for the first time." -ForegroundColor Yellow
        Write-Host ""
        $downloadModels = Read-Host "Download AI models now? (This takes 10-20 minutes) (y/N)"

        if ($downloadModels -eq 'y' -or $downloadModels -eq 'Y') {
            Write-Host ""
            Write-Host "⬇️  Downloading llama3.1:8b (~4.7GB)..." -ForegroundColor Cyan
            docker compose exec ollama ollama pull llama3.1:8b

            Write-Host "⬇️  Downloading nomic-embed-text (~274MB)..." -ForegroundColor Cyan
            docker compose exec ollama ollama pull nomic-embed-text

            Write-Host ""
            Write-Host "✅ AI models downloaded successfully!" -ForegroundColor Green
        }
        else {
            Write-Host ""
            Write-Host "⚠️  Models not downloaded. To download later, run:" -ForegroundColor Yellow
            Write-Host "   docker compose exec ollama ollama pull llama3.1:8b" -ForegroundColor White
            Write-Host "   docker compose exec ollama ollama pull nomic-embed-text" -ForegroundColor White
        }
    }
    else {
        Write-Host "✅ AI models are already downloaded" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "  📚 Useful Commands:" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "  View logs:     docker compose logs -f" -ForegroundColor White
    Write-Host "  Stop services: docker compose down" -ForegroundColor White
    Write-Host "  Restart:       docker compose restart" -ForegroundColor White
    Write-Host "  Status:        docker compose ps" -ForegroundColor White
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🎉 IOB MAIIS is ready to use!" -ForegroundColor Green
    Write-Host "   Open your browser and visit: http://localhost:3000" -ForegroundColor White
    Write-Host ""

    # Ask if user wants to view logs
    $viewLogs = Read-Host "View application logs? (y/N)"
    if ($viewLogs -eq 'y' -or $viewLogs -eq 'Y') {
        Write-Host ""
        Write-Host "📋 Showing logs (Press Ctrl+C to exit)..." -ForegroundColor Cyan
        docker compose logs -f
    }
}
else {
    Write-Host ""
    Write-Host "❌ Failed to start services!" -ForegroundColor Red
    Write-Host "Please check the error messages above" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "  1. Ports already in use - check with: netstat -ano | findstr :8000" -ForegroundColor White
    Write-Host "  2. Not enough memory - ensure Docker has at least 8GB RAM" -ForegroundColor White
    Write-Host "  3. Missing .env file - ensure it exists and has correct values" -ForegroundColor White
    Write-Host ""
    exit 1
}
