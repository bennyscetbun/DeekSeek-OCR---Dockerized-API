@echo off
REM DeepSeek-OCR Build and Run Script for Windows
REM This script enforces proper setup order before building

echo =========================================
echo DeepSeek-OCR Build and Run Script
echo =========================================
echo.

REM Step 1: Check prerequisites
echo Checking prerequisites...

REM Check Docker
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker is not installed
    pause
    exit /b 1
)
echo ✓ Docker found

REM Check Docker Compose
docker compose version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker Compose plugin not found
    echo Please install Docker Compose v2
    pause
    exit /b 1
)
echo ✓ Docker Compose found

REM Check NVIDIA GPU
nvidia-smi >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ nvidia-smi not found - NVIDIA GPU required
    pause
    exit /b 1
)
echo ✓ NVIDIA GPU found
echo.

REM Step 2: Build Docker image
echo.
echo =========================================
echo Building Docker image...
echo =========================================
echo.

docker compose build

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Docker build failed
    echo.
    echo Troubleshooting:
    echo   1. Ensure Docker Desktop is running
    echo   2. Check NVIDIA Container Toolkit: docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi
    echo   3. Free up disk space if needed: docker system prune
    echo.
    pause
    exit /b 1
)

echo.
echo =========================================
echo ✓ Build complete!
echo =========================================
echo.
echo 🔧 New OCR functionality available:
echo    - Enhanced PDF to OCR processor (pdf_to_ocr_enhanced.py)
echo    - OCR-specific prompt support: '<image>\nFree OCR.'
echo    - Test scripts: test_ocr_prompt.py, quick_test_ocr.py
echo.

REM Step 3: Ask if user wants to start the service
set /p START_SERVICE="Do you want to start the service now? (y/n): "

if /i "%START_SERVICE%"=="y" (
    echo.
    echo Starting DeepSeek-OCR service...
    docker compose up -d

    echo.
    echo ✓ Service started!
    echo.
    echo Checking service health...
    echo ^(This may take 1-2 minutes for model to load^)
    timeout /t 10 >nul

    echo.
    echo Testing health endpoint...
    curl -s http://localhost:8000/health

    echo.
    echo =========================================
    echo Service is running!
    echo =========================================
    echo.
    echo Useful commands:
    echo   View logs:      docker compose logs -f deepseek-ocr
    echo   Health check:   curl http://localhost:8000/health
    echo   Stop service:   docker compose down
    echo   Restart:        docker compose restart
    echo.
    echo 🧪 To test OCR functionality:
    echo   docker compose exec deepseek-ocr python quick_test_ocr.py
    echo.
) else (
    echo.
    echo Build complete!
    echo To start the service later, run:
    echo   docker compose up -d
    echo.
    echo 🧪 To test OCR functionality:
    echo   docker compose exec deepseek-ocr python quick_test_ocr.py
    echo.
)

pause