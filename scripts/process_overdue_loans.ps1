param()

$ErrorActionPreference = 'Stop'
Push-Location backend
try {
  ..\.venv\Scripts\python manage.py process_overdue_loans
}
finally {
  Pop-Location
}
