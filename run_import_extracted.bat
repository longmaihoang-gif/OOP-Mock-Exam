@echo off
chcp 65001 > nul
title Chuyen Hoa 21 Ma Nguon OCR - C++ Exam Pipeline
cd /d "%~dp0"
echo ============================================================
echo   IMPORT EXTRACTED C++ EXAM PIPELINE
echo   Dang chay tien trinh nhan dien va nhap cau hoi...
echo ============================================================
python import_extracted_cpp.py
echo.
pause
