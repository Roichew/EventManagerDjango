# EventManagerDjango

This is a Django Event Management Application with User Registration, Event Registration and Admin Controls.

##Features

-User Registration and Login
-JWT Auth
-Event Listing
-Users Can Register For Events

- Admins Can Perform CRUD Operations on Events

##Project Configurations

1. After Clonning the Repository

```bash
cd ../EventManagerDjango

```

2. Create Virtual Env

```bash
python -m venv venv

#or (for MacOS/Linux)

python3 -m venv venv

```

3. Activate Venv

```bash

# (Linux/Mac)
source venv/bin/activate

# Windows
venv\Scripts\activate

```

4. Install Dependencies

```bash
pip install -r requirements.txt
```

5. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create Superuser

```bash
python manage.py createsuperuser
```

7. Run Server

```bash
python manage.py runserver
```
