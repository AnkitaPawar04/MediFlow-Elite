
# 🏥 MediFlow – Hospital Management Platform 

MediFlow is a full-stack Hospital Management Platform built with Django that streamlines appointment booking, doctor availability, patient management, email notifications, and calendar integrations.

---

## 🚀 Features

### 👤 Authentication & Roles
- Custom user model with **Doctor** and **Patient** roles
- Secure login, signup, and logout
- Role-based dashboard redirection

### 🩺 Doctor Dashboard
- Create and manage availability slots
- View booked appointments
- Google Calendar integration
- Appointment statistics

### 🧑‍⚕️ Patient Dashboard
- Browse doctors
- Book and cancel appointments
- View upcoming appointments
- Google Calendar integration

### 📅 Appointment Management
- Slot-based booking system
- Transaction-safe booking (prevents double booking)
- Cancellation support

### ✉️ Email Notifications
- Signup welcome email
- Booking confirmation (patient & doctor)
- Cancellation email
- Appointment reminder (1 hour before)
- Powered by a **Serverless email microservice**

### 🔗 Integrations
- Google Calendar (OAuth 2.0)
- Serverless email service (AWS Lambda style)

---

## 🛠️ Tech Stack

**Backend**
- Django
- Python
- SQLite (dev) / PostgreSQL (production-ready)

**Frontend**
- HTML
- CSS
- JavaScript
- Django Templates

**Services**
- Google Calendar API
- Serverless Framework
- REST-based Email Service

---

## ⚙️ Setup Instructions

### 1️⃣ Clone Repository
```bash
git clone https://github.com/MuktaRedij/MediFlow-Hospital-Management-Platform.git
cd MediFlow-Hospital-Management-Platform/hms
```
### 2️⃣ Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate   # Windows
```
### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
### 4️⃣ Environment Variables
Create a .env file based on .env.example and add:

- Google OAuth credentials
- Email service URL
### 5️⃣ Run Migrations
```bash
python manage.py migrate
```
### 6️⃣ Start Server
```bash
python manage.py runserver
```
---
### Demo Email Reminders

Run manually:
```bash
python manage.py send_reminders
```
---
🔐 Security Notes

Secrets are never committed

.env, tokens, and credentials are git-ignored

Google OAuth handled securely
---
👩‍💻 Author

Ankita Pawar
