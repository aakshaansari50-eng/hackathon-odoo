# AssetFlow database in XAMPP (MySQL)

## 1. Start XAMPP

Open the XAMPP Control Panel and start **Apache** and **MySQL**.

## 2. Create the database

1. Go to `http://localhost/phpmyadmin`.
2. Click **Import**.
3. Select `database/assetflow_xampp.sql` from this project and click **Import**.

It creates the database named `assetflow` and the `assetflow_user` database account.

## 3. Configure AssetFlow

In PowerShell, open the `AssetFlow` folder and set these values for the current session:

```powershell
$env:DB_ENGINE='mysql'
$env:DB_NAME='assetflow'
$env:DB_USER='assetflow_user'
$env:DB_PASSWORD='ChangeThisStrongPassword!'
$env:DB_HOST='127.0.0.1'
$env:DB_PORT='3306'
```

For a real deployment, change the password in both the SQL file and these settings before importing.

## 4. Create Django tables and demo data

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py runserver
```

Open `http://127.0.0.1:8000/login/`.

Demo login: `admin` / `Admin@123`

After migration, all Django login/authentication tables and AssetFlow tables will be visible in phpMyAdmin under the `assetflow` database.
