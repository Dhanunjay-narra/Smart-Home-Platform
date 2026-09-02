@echo off
echo =================================================================
echo  Smart Home Platform - Launching Web Application and Microservices
echo =================================================================
echo  Dashboard: http://localhost:8000
echo  API Docs:  http://localhost:8000/api/docs
echo =================================================================
start http://localhost:8000
python run_server.py
pause
