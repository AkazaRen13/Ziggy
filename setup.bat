@echo off
echo ============================================================
echo  RAG Assistant - Dev Setup
echo ============================================================

python -m venv venv
call venv\Scripts\activate.bat

echo.
echo [1/4] Upgrading pip...
venv\Scripts\python.exe -m pip install --upgrade pip

echo.
echo [2/4] Installing duckduckgo-search...
venv\Scripts\pip.exe install duckduckgo-search

echo.
echo [3/4] Installing llama-cpp-python (CPU build)...
venv\Scripts\pip.exe install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

echo.
echo [4/4] Installing pyinstaller...
venv\Scripts\pip.exe install pyinstaller

echo.
echo Downloading model (895 MB)...
venv\Scripts\python.exe -c "
import os, urllib.request, sys
url = 'https://huggingface.co/bartowski/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/Qwen2.5-1.5B-Instruct-IQ4_XS.gguf'
dest = os.path.join('src', 'models', 'Qwen2.5-1.5B-Instruct-IQ4_XS.gguf')
os.makedirs(os.path.dirname(dest), exist_ok=True)
if os.path.exists(dest):
    print('Model already downloaded.')
    sys.exit(0)
def progress(count, block, total):
    if total > 0:
        pct = min(100, count*block*100//total)
        mb = count*block//1024//1024
        tot = total//1024//1024
        sys.stdout.write(f'\r  {pct}%  ({mb} MB / {tot} MB)   ')
        sys.stdout.flush()
urllib.request.urlretrieve(url, dest, reporthook=progress)
print()
print('Done.')
"

echo.
echo ============================================================
echo  ALL DONE. You can now run:  run.bat
echo ============================================================
echo.
pause