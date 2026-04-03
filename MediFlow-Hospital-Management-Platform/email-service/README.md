# HMS Email Service

Mini Hospital Management System Email Service using Serverless Framework.

## Setup

```bash
npm install -g serverless
npm install --save-dev serverless-offline serverless-python-requirements
```

## Local Development

```bash
serverless offline start
```

The service will run at `http://localhost:3000/dev/send-email`

## Deployment

```bash
serverless deploy
```

## API

### Endpoint
`POST /send-email`

### Supported Actions

#### SIGNUP_WELCOME
```json
{
    "action": "SIGNUP_WELCOME",
    "user_email": "user@example.com",
    "user_name": "John Doe",
    "role": "Doctor"
}
```

#### BOOKING_CONFIRMATION
```json
{
    "action": "BOOKING_CONFIRMATION",
    "patient_email": "patient@example.com",
    "patient_name": "Jane Doe",
    "doctor_name": "Dr. Smith",
    "date": "2025-12-20",
    "time": "14:00:00"
}
```
