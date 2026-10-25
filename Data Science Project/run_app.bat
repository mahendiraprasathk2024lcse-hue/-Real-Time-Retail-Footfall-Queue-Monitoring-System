@echo off
title RTRFQM - Retail Footfall and Queue Monitor
echo =====================================================================
echo Starting Real-Time Retail Footfall & Checkout Queue Monitor (RTRFQM)
echo =====================================================================
python -m streamlit run app.py --server.port 8501 --server.headless false
pause
