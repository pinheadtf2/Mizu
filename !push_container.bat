@echo off
setlocal enabledelayedexpansion

:: Configuration
set IMAGE_NAME=ghcr.io/pinheadtf2/mizu
set IMAGE_TAG=latest
set DOCKERFILE=Dockerfile
set BUILD_CONTEXT=.

:: Check if Dockerfile exists
if not exist "%DOCKERFILE%" (
    echo Dockerfile not found in current directory: %CD%!
    PAUSE
    exit /b 1
)

echo Building Docker image from %DOCKERFILE%...
docker build -f "%DOCKERFILE%" -t %IMAGE_NAME%:%IMAGE_TAG% %BUILD_CONTEXT%

if %ERRORLEVEL% NEQ 0 (
    echo Build failed!
    PAUSE
    exit /b %ERRORLEVEL%
)

echo Logging in...
docker login ghcr.io

if %ERRORLEVEL% NEQ 0 (
    echo Login failed!
    PAUSE
    exit /b %ERRORLEVEL%
)

echo Pushing image to %IMAGE_NAME%:%IMAGE_TAG% ...
docker push %IMAGE_NAME%:%IMAGE_TAG%

if %ERRORLEVEL% NEQ 0 (
    echo Push failed!
    PAUSE
    exit /b %ERRORLEVEL%
)

echo Successfully built and pushed!
PAUSE
