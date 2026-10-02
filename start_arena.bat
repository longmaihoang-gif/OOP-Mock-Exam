@echo off
title He Thong Thi Thu Trac Nghiem C++ OOP - Local Server
cd /d "%~dp0"
echo ============================================================
echo   HE THONG THI THU TRAC NGHIEM C++ OOP
echo   Dang khoi dong may chu noi bo tai cong 8000...
echo ============================================================
start http://localhost:8000/MockExam.html
python arena_server.py
if %errorlevel% neq 0 (
    echo [LOI]: Khong the khoi chay bang arena_server.py. Dang thu lai bang http.server...
    python -m http.server 8000
)
pause
