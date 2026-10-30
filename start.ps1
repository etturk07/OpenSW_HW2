$ErrorActionPreference = 'Stop'
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { throw 'Python이 설치되어 있지 않습니다. Python 3.11+를 설치한 뒤 다시 실행하세요.' }
& $python.Source -m pip install -r requirements.txt
& $python.Source -m uvicorn app.main:app --host 127.0.0.1 --port 8000
