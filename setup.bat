@echo off
echo ================================================
echo   Suhani's Daily Digest — Windows Setup
echo ================================================
echo.

:: Install Python dependencies
echo [1/3] Installing Python packages...
pip install feedparser requests groq
echo.

:: Check Python version
echo [2/3] Checking Python version...
python --version
echo.

echo [3/3] Setup complete!
echo.
echo ================================================
echo   NEXT STEPS:
echo ================================================
echo.
echo 1. Open config.py and fill in:
echo    - Your GROQ_API_KEY (get free at console.groq.com)
echo    - Your Gmail App Password
echo.
echo 2. Run once to test:
echo    python digest.py
echo.
echo 3. To schedule daily at 8 AM (Windows Task Scheduler):
echo    - Open Task Scheduler (search in Start menu)
echo    - Click "Create Basic Task"
echo    - Name: "Suhani Daily Digest"
echo    - Trigger: Daily, at 8:00 AM
echo    - Action: Start a program
echo    - Program: python
echo    - Arguments: C:\path\to\news_digest\digest.py
echo    - Start in: C:\path\to\news_digest\
echo    - Finish and enable.
echo.
echo ================================================
pause
