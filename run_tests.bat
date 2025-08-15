@echo off
echo Running Media Management Tool Tests...
call venv\Scripts\activate.bat
python -m pytest --cov=media_processor --cov=app --cov-report=term-missing -v
pause
