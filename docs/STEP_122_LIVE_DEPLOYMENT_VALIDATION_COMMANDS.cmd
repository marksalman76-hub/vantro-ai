@echo off
REM Step 122 — Live Deployment Validation Commands
REM Replace these two values with your real deployed URLs before running.
REM Do not paste secrets into this file.

set BACKEND_URL=https://YOUR-BACKEND-URL-HERE
set FRONTEND_URL=https://YOUR-FRONTEND-URL-HERE

echo Checking backend health...
curl -i "%BACKEND_URL%/health"

echo.
echo Checking frontend homepage...
curl -i "%FRONTEND_URL%/"

echo.
echo Checking admin route...
curl -i "%FRONTEND_URL%/admin"

echo.
echo Checking client route...
curl -i "%FRONTEND_URL%/client"

echo.
echo Checking allowed CORS preflight...
curl -i -X OPTIONS "%BACKEND_URL%/health" -H "Origin: %FRONTEND_URL%" -H "Access-Control-Request-Method: GET"

echo.
echo Checking blocked origin CORS preflight...
curl -i -X OPTIONS "%BACKEND_URL%/health" -H "Origin: https://blocked-origin.example" -H "Access-Control-Request-Method: GET"

echo.
echo STEP_122_LIVE_VALIDATION_COMMANDS_COMPLETE
