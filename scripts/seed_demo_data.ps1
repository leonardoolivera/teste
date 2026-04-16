Push-Location backend
try {
    ..\.venv\Scripts\python manage.py seed_demo_data
} finally {
    Pop-Location
}