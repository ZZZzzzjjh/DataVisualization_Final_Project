@echo off
set "PATH=C:\Windows\System32;C:\Windows;C:\Users\zjh\.cache\codex-runtimes\codex-primary-runtime\dependencies\python;C:\Users\zjh\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\Scripts"
set "APP_DIR=%~dp0"
set "APP=%~dp0app.py"
cd /d "%APP_DIR%"
start "" /min cmd /d /k ""C:\Users\zjh\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m streamlit run "%APP%" --server.address 127.0.0.1 --server.port 8501 --server.headless true > "%APP_DIR%streamlit.bat.log" 2>&1"
