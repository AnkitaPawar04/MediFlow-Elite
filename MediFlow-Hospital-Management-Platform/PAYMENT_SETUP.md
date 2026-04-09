# Payment Gateway Integration - Razorpay Setup Guide

## Overview
MediFlow now includes integrated payment processing for consultation fees using Razorpay. Patients must complete payment after booking an appointment.

## Features Implemented

### 1. **Payment Flow**
- Patient books appointment → redirected to payment page
- Razorpay payment modal with appointment details
- Secure payment processing with signature verification
- Automatic transaction logging
- Confirmation email after successful payment

### 2. **Payment Management**
- Show payment status in bookings list (Paid/Pending/Failed)
- Pay button for pending payments
- Refund tracking when cancelling paid appointments
- Payment history in Transaction model

### 3. **Doctor Fee Configuration**
- Doctors set consultation fees via DoctorApproval model
- Default fee: ₹500 (if not configured)
- Fee displayed on payment page

## Setup Instructions

### Step 1: Install Razorpay Package
```bash
pip install razorpay
# Or if using requirements.txt
pip install -r requirements.txt
```

### Step 2: Configure Razorpay API Keys
Create/Update `.env` file with Razorpay credentials:

```env
RAZORPAY_KEY_ID=rzp_live_***your_key_here***
RAZORPAY_KEY_SECRET=***your_secret_here***
```

Get keys from: https://dashboard.razorpay.com/app/keys

### Step 3: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

This will:
- Convert Booking.patient from OneToOneField to ForeignKey (allows multiple bookings)
- Add consultation_fee field
- Add payment_status field
- Add payment_id field

### Step 4: Test in Development

Use Razorpay test keys:
- Key ID: `rzp_test_***`
- Key Secret: `***`

Test credentials:
- Card: 4111 1111 1111 1111
- Expiry: 12/25
- CVV: 123
- OTP: 123456

### Step 5: Production Deployment

1. Get live Razorpay keys
2. Update .env with production keys
3. Test payment flow thoroughly
4. Monitor transactions in Razorpay dashboard

## API Integration Details

### Models Updated

**Booking Model Changes:**
```python
patient = ForeignKey(CustomUser, ...)  # Changed from OneToOne
consultation_fee = DecimalField()       # New
payment_status = CharField()            # New: pending/completed/failed
payment_id = CharField()                # New: Razorpay payment ID
```

**Transaction Model:**
- Records all payment transactions
- Links to booking and patient
- Tracks refunds

### Views

**initiate_payment(request, booking_id)**
- Creates Razorpay order
- Returns payment page/modal with order details
- AJAX support: returns payment_modal_content.html if ajax=1

**verify_payment(request)** - POST
- Verifies Razorpay signature
- Updates booking payment_status
- Creates transaction record
- Sends confirmation email
- Returns JSON response

**book_appointment(request, slot_id)**
- Modified to redirect to payment instead of confirming immediately
- Sets consultation fee before creating booking

**cancel_booking(request)**
- Updated to handle multiple bookings
- Creates refund transaction if payment was completed

### Payment Page Features

**Full Page (payment.html)**
- Complete appointment details
- Fee breakdown
- Secure Razorpay checkout
- Professional styling
- Loading overlay during payment verification

**AJAX Modal (payment_modal_content.html)**
- Compact version for in-dashboard loading
- Same functionality
- Optimized for modal display

## Security Measures

1. **Signature Verification**: All payments verified using Razorpay signature
2. **CSRF Protection**: All payment endpoints protected with @csrf_protect
3. **Amount Verification**: Server-side validation of payment amount
4. **Transaction Logging**: All transactions recorded with timestamp
5. **Secure API Keys**: Keys stored in environment variables

## Payment Status Workflow

```
Booking Created (payment_status='pending')
         ↓
    initiate_payment()
         ↓
 Razorpay Checkout Modal
         ↓
   Payment Completed
         ↓
   verify_payment()
         ↓
   Signature Valid? 
    ↙         ↘
  YES          NO
   ↓            ↓
payment_status='completed'  payment_status='failed'
Send Email               Show Error
         ↓
  Redirect Dashboard
```

## Booking Status Display

### Payment Status Badges
- **Paid** (Green): `<i class="fas fa-check-circle"></i> Paid`
- **Pending** (Orange): `<i class="fas fa-clock"></i> Pending`
- **Failed** (Red): `<i class="fas fa-times-circle"></i> Failed`

### Actions Available
- **Paid**: Cancel appointment (generates refund transaction)
- **Pending**: Pay button + Cancel button
- **Failed**: Pay button + Cancel button + Error message

## Transaction Tracking

All transactions are logged in the Transaction model:
- Payment ID (Razorpay)
- Booking reference
- Amount
- Payment method (razorpay/refund)
- Timestamp
- Status

## Testing Checklist

- [ ] Razorpay API keys configured
- [ ] Book appointment → redirects to payment
- [ ] Payment page displays correctly
- [ ] Razorpay modal opens on "Pay Now" click
- [ ] Test payment with Razorpay test card
- [ ] Payment signature verification works
- [ ] Booking status updates to 'completed'
- [ ] Confirmation email sent
- [ ] Transaction record created
- [ ] Cancel booking creates refund transaction
- [ ] Pending payment button works
- [ ] AJAX payment modal loads correctly
- [ ] Payment page responsive (mobile/desktop)

## Error Handling

### Common Errors & Solutions

**"Razorpay API key not configured"**
- Check .env file has RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET
- Restart Django server after updating .env

**"Payment verification failed"**
- Check Razorpay keys are correct
- Ensure signature verification is enabled
- Check payment amount matches

**"Booking not found"**
- Verify booking exists and belongs to current user
- Check booking ID in URL is correct

**"Payment request blocked"**
- Check CSRF token in payment form
- Verify X-CSRFToken header in AJAX request
- Check CORS settings if cross-domain

## Future Enhancements

- [ ] Support multiple payment methods (Apple Pay, Google Pay)
- [ ] Partial refunds for cancellations
- [ ] Payment plans/installments
- [ ] Invoice generation
- [ ] Payment reminder emails
- [ ] Subscription-based appointments
- [ ] Wallet integration

## Support & Monitoring

### Monitor Payments
- Razorpay Dashboard: https://dashboard.razorpay.com
- Django Admin: Admin > Transactions
- Django Admin: Admin > Bookings (view payment_status)

### Webhook Handling (Future)
Currently using synchronous verification. Consider implementing webhooks for:
- Automatic reconciliation
- Refund notifications
- Payment failure alerts

## References
- [Razorpay Documentation](https://razorpay.com/docs/)
- [Razorpay Python SDK](https://github.com/razorpay/razorpay-python)
- [Payment Integration Best Practices](https://razorpay.com/docs/payments/payments-api/integration-guide/)
