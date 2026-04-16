param()

$ErrorActionPreference = 'Stop'
Push-Location backend
try {
  ..\.venv\Scripts\python manage.py test apps.core apps.catalog apps.users apps.circulation apps.inventory apps.notifications
}
finally {
  Pop-Location
}
