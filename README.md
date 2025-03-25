# Ecoffee - Sustainability Gamification Platform
Ecoffee is a web application designed to promote sustainability by incentivizing the use of reusable coffee cups. The platform gamifies environmentally friendly behavior by tracking coffee shop visits, rewarding users with badges, and maintaining user streaks. Key features include:

- QR code scanning for logging visits to partner coffee shops
- Badge system to reward sustainable behavior
- User dashboard to track progress and impact
- Leaderboards to encourage community participation
- GDPR compliant user data management
- Email verification for enhanced security
- Shop owner management interface
- Daily goals and progress tracking

The app aims to reduce single-use cup waste by creating a fun, engaging platform that motivates users to bring their own cups to participating coffee shops.
Ecoffee website link: https://ecm2434-group-project.onrender.com/home/

## Project Structure
```
Ecoffee/
├── Ecoffee/              # Main project configuration
├── EcoffeeBase/          # Core models and base functionality
├── login_system/         # User authentication and registration
├── qr_codes/             # QR code scanning and visit logging
├── add_to_database/      # Shop and badge management
├── templates/            # HTML templates
├── static/               # Static files (CSS, JS, images)
├── media/                # User-uploaded content
└── manage.py             # Django management script
```

## Setup

### Prerequisites
- Python 3.10 or higher
- Django 4.x
- SQLite (included in Django)
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/wentaohe1/ECM2434_Group_Project.git
cd ECM2434_Group_Project/Ecoffee
```

2. **Create and activate a virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
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

### Setting Up Test Data

1. To add test data to the database, including badges and shops:
   - Log in as a shop owner
   - Navigate to http://127.0.0.1:8000/add_data/add_new_data
   - Add shops with unique active codes
   - Create badges with different coffee cup thresholds

2. To simulate a shop visit using a QR code:
   - Visit http://127.0.0.1:8000/code/?code=YOUR_ACTIVE_CODE
   - Replace YOUR_ACTIVE_CODE with an active code you created for a shop
   - Note: User must be logged in and email verified to log visits

## Testing
The project includes comprehensive tests for all core functionalities:
- Functional testing of all features (login, challenge completion, rewards)
- Edge case testing (invalid inputs, error handling)
- User acceptance testing
- Automated tests for core functionality
- GDPR compliance testing

```bash
# Run all tests
python manage.py test

# Test specific apps
python manage.py test login_system
python manage.py test EcoffeeBase
python manage.py test qr_codes
python manage.py test add_to_database
```

## Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements
- Developed by Project Team A as part of ECM2434
- Thanks to all contributing developers
