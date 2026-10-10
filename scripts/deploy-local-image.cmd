@echo off
setlocal

set IMAGE_NAME=ghcr.io/roshanefernando/deployflow-api
set IMAGE_TAG=latest

echo Pulling %IMAGE_NAME%:%IMAGE_TAG%...
docker pull %IMAGE_NAME%:%IMAGE_TAG%

if errorlevel 1 (
    echo Failed to pull image.
    exit /b 1
)

echo Image pulled successfully.
docker images %IMAGE_NAME%

endlocal