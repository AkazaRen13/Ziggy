@echo off
echo ============================================================
echo  Building standalone EXE...
echo ============================================================
call venv\Scripts\activate.bat

pyinstaller ^
  --onefile ^
  --windowed ^
  --name "SearchAssistant" ^
  --add-data "src\models;models" ^
  --hidden-import="llama_cpp" ^
  --hidden-import="duckduckgo_search" ^
  --hidden-import="duckduckgo_search.duckduckgo_search_async" ^
  --collect-all llama_cpp ^
  --collect-all duckduckgo_search ^
  src\app.py

echo.
echo ============================================================
echo  EXE built at: dist\SearchAssistant.exe
echo  Zipping...
echo ============================================================

:: Create release zip
powershell -Command "Compress-Archive -Path 'dist\SearchAssistant.exe' -DestinationPath 'SearchAssistant.zip' -Force"

echo.
echo  Done: SearchAssistant.zip
echo ============================================================
pause
