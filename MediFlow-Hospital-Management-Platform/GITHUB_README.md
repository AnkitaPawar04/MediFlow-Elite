# MediFlow - Hospital Management System

A comprehensive Django-based Hospital Management Platform with appointment booking, payment integration, and doctor/patient portals.

## Features

✅ **Multi-role Authentication** - Admin, Doctor, Patient accounts  
✅ **Appointment Booking System** - Real-time slot management  
✅ **Razorpay Payment Integration** - Secure online payments  
✅ **Doctor Dashboard** - Manage availability and bookings  
✅ **Patient Portal** - Book appointments, view medical history  
✅ **Google Calendar Integration** - Auto-sync appointments  
✅ **Email Notifications** - Booking confirmations  

## Tech Stack

- **Backend**: Django 4.2.7
- **Database**: SQLite3 (development)
- **Frontend**: Bootstrap 5.3, Font Awesome 6.4
- **Payment**: Razorpay API
- **Email**: Background email service
- **Calendar**: Google Calendar API

## Installation

### Prerequisites

- Python 3.9+
- pip (Python package manager)
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/MediFlow.git
   cd MediFlow
   ```

2. **Create and activate virtual environment**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   cd hms
   pip install -r requirements.txt
   ```

4. **Create .env file for local configuration**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your actual credentials (never commit this file)

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (admin)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

Server runs at: `http://127.0.0.1:8000/`

## Configuration

### Environment Variables

Create a `.env` file in the `hms/` directory (copy from `.env.example`):

```
DEBUG=True
SECRET_KEY=your-django-secret-key
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret
GOOGLE_CLIENT_ID=your-google-oauth-id
GOOGLE_CLIENT_SECRET=your-google-oauth-secret
```

### Razorpay Setup

1. Create account at https://razorpay.com
2. Get test credentials from dashboard
3. Add to `.env` (test mode by default)

## Project Structure

```
MediFlow/
├── hms/                    # Django project root
│   ├── accounts/          # User authentication app
│   ├── admin_management/  # Admin portal
│   ├── doctors/           # Doctor app & API
│   ├── patients/          # Patient app & API
│   ├── bookings/          # Appointment & payment handling
│   ├── config/            # Django settings
│   ├── templates/         # HTML templates
│   ├── static/            # CSS, JS, assets
│   └── manage.py
├── email-service/         # Lambda email service
├── .env.example          # Environment template
└── README.md
```

## Test Accounts

After creating a super user, access the admin panel:
- URL: `http://127.0.0.1:8000/admin`

Create test accounts for:
- Doctor: `/admin_management/doctor/`
- Patient: via signup page

## Database

Development uses SQLite3. To reset database:

```bash
# Delete existing database
rm db.sqlite3

# Re-run migrations
python manage.py migrate

# Create new super user
python manage.py createsuperuser
```

## API Endpoints

### Authentication
- `POST /accounts/login/` - User login
- `POST /accounts/register/` - Patient signup
- `POST /accounts/logout/` - Logout

### Bookings
- `POST /bookings/book/<slot_id>/` - Create booking
- `POST /bookings/initiate-payment/<booking_id>/` - Start payment
- `POST /bookings/verify-payment/` - Verify Razorpay payment

### Doctors
- `GET /doctors/` - List doctors
- `POST /doctors/availability/` - Create availability slot
- `GET /doctors/dashboard/` - Doctor dashboard

### Patients
- `GET /patients/dashboard/` - Patient dashboard
- `GET /patients/bookings/` - View patient bookings

## Troubleshooting

### ImportError: No module named 'razorpay'
```bash
pip install razorpay==1.4.1
```

### Database is locked
Stop the development server and restart it.

### Port 8000 in use
```bash
python manage.py runserver 8001
```

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/YourFeature`
3. Commit changes: `git commit -m 'Add feature'`
4. Push to branch: `git push origin feature/YourFeature`
5. Open Pull Request

## License

MIT License - See LICENSE file for details

## Support

For issues and feature requests, please create a GitHub issue.

## Author

Created with ❤️ for healthcare management

---

**Note**: This is a development version. For production use, implement:
- Environment-based configuration
- Proper database setup (PostgreSQL recommended)
- HTTPS/SSL certificates
- Security headers
- Rate limiting
- Proper logging system
