@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated!
echo.
echo You can now run:
echo   python app.py
echo   python -m pytest
echo   python tests/run_tests.py
echo.
cmd /k
