param()

$ErrorActionPreference = 'Stop'

if (-not (Test-Path '.venv')) {
  python -m venv .venv
}

.\.venv\Scripts\python -m pip install -r backend\requirements.txt
.\.venv\Scripts\python backend\manage.py migrate
Write-Host 'Backend pronto. Execute:' -ForegroundColor Green
Write-Host '.\.venv\Scripts\python backend\manage.py runserver' -ForegroundColor Cyan
