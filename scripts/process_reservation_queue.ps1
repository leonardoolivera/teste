param()

$ErrorActionPreference = 'Stop'
Push-Location backend
try {
  ..\.venv\Scripts\python manage.py process_reservation_queue
}
finally {
  Pop-Location
}
