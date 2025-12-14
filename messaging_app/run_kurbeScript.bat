@echo off
REM Windows Batch Script to run kurbeScript.ps1 without execution policy issues
echo ==========================================
echo Kubernetes Setup Script Launcher
echo ==========================================
echo.

REM Run PowerShell script with bypass execution policy
powershell.exe -ExecutionPolicy Bypass -File "%~dp0kurbeScript.ps1"

pause
