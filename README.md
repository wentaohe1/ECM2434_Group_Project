# ECM2434_Group_Project

## Setup
Basic instructions for setting up the app locally. 

1. **Clone the repository**
```bash
git clone https://github.com/wentaohe1/ECM2434_Group_Project.git
cd ECM2434_Group_Project
```

2. **Create and activate a virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies (if needed)**
```bash
pip install django psycopg2-binary
```

4. **Apply database migrations**
```bash
# make migrations
python manage.py makemigrations

# apply migrations
python manage.py migrate
```

5. **Create a superuser (admin)**
```bash
python manage.py createsuperuser
```

6. **Run the development server**
```bash
python manage.py runserver
```

7. **The application should now be running at http://127.0.0.1:8000/**


8. To add data to the database, including your own badges and shops, follow the link
 http://127.0.0.1:8000/add_data/add_new_data

9. To register a visit to the shop, follow the link
   127.0.0.1:8000/code/?code=(active_code you submitted above)

   
## Requirement
- Python 3.10
- PostgreSQL
- pip (Python package manager)

## Testing
To test the basic functionalities (login, registration, basic gamification), you can use:

~~~
# test all
python manage.py test

# test specific app
python manage.py test login_system
python manage.py test EcoffeeBase
python manage.py test qr_codes
~~~
