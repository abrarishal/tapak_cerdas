@echo off
title TAPAK CERDAS - Aplikasi Web Geoteknik & Pondasi
echo =========================================================================
echo MEMULAI APLIKASI WEB TAPAK CERDAS...
echo Akses Komputer Sendiri : http://localhost:8501
echo Akses HP / Teman / Wi-Fi : http://192.168.1.7:8501
echo =========================================================================
cd /d "%~dp0"
"C:\Program Files\QGIS 3.40.7\apps\Python312\python.exe" -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
pause
