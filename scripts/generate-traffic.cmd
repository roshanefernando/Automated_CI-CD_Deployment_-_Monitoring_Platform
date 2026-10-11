@echo off
setlocal

set BASE_URL=http://127.0.0.1:8000

echo Sending health check traffic...
for /L %%i in (1,1,30) do (
    curl -s %BASE_URL%/health/ready > nul
)

echo Creating sample tasks...
for /L %%i in (1,1,10) do (
    curl -s -X POST %BASE_URL%/tasks ^
      -H "Content-Type: application/json" ^
      -d "{\"title\":\"Monitoring test task %%i\",\"description\":\"Generated sample traffic\",\"status\":\"TODO\"}" > nul
)

echo Listing tasks...
for /L %%i in (1,1,10) do (
    curl -s %BASE_URL%/tasks > nul
)

echo Sample traffic generated successfully.

endlocal