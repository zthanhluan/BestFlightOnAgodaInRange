@echo off
:: Activate the Python environment
call webScrap\Scripts\activate

:: Run the Streamlit application on the desired port
call python main.py

:: Pause to view any error messages or output
pause