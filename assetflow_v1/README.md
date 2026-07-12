# AssetFlow — Enterprise Asset & Resource Management

AssetFlow is a Django ERP application for registering, allocating, maintaining, auditing and reporting on company assets and shared resources. It contains no AI features or external AI services.

## Features

- Secure Django login, logout and employee-only signup; admin promotion is managed in Django Admin.
- Role-ready employee profiles: Admin, Asset Manager, Department Head and Employee.
- Departments, categories, asset lifecycle status, allocations, resource booking, maintenance, transfers, audits and notifications.
- Booking conflict detection based on overlapping time ranges.
- Premium responsive Bootstrap interface with dashboard KPIs, Chart.js utilization chart, tables and forms.
- MySQL production configuration plus SQLite local-development fallback.

## Run locally

1. Create and activate a Python virtual environment.
2. Run `pip install -r requirements.txt`.
3. For MySQL, create a database and copy `.env.example` values into environment variables. The MySQL user needs rights on that database. For a quick local preview leave `DB_ENGINE` unset (SQLite).
4. Run `python manage.py makemigrations core`, then `python manage.py migrate`.
5. Run `python manage.py createsuperuser`.
6. Run `python manage.py runserver` and open `http://127.0.0.1:8000`.

Use `/admin/` to add departments, categories, resources and to promote Employee profiles to Admin, Asset Manager or Department Head.

For XAMPP MySQL, follow [XAMPP_SETUP.md](XAMPP_SETUP.md). The phpMyAdmin import file is in `database/assetflow_xampp.sql`.

## Production checklist

- Set a unique `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False` and trusted `DJANGO_ALLOWED_HOSTS`.
- Use MySQL with backups and a restricted database user.
- Run `collectstatic`, deploy behind HTTPS, and use a production WSGI server such as Gunicorn or Waitress.
