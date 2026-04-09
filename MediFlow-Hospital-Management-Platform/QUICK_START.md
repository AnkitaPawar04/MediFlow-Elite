# Payment Gateway Integration - Quick Start Checklist

## 🚀 Immediate Setup (Run These Commands)

### Step 1: Install Dependencies
```bash
cd hms
pip install -r requirements.txt
# This installs razorpay==1.4.1
```

### Step 2: Create .env File
Create `.env` file in `hms/` directory with:
```env
# Test Mode (Development)
RAZORPAY_KEY_ID=rzp_test_YOUR_TEST_KEY_ID
RAZORPAY_KEY_SECRET=your_test_key_secret

# Get test keys from: https://dashboard.razorpay.com/app/keys
```

### Step 3: Run Database Migration
```bash
python manage.py migrate
# Applies: 0002_booking_payment_fields.py
# This updates the Booking model with payment fields
```

### Step 4: Start Development Server
```bash
python manage.py runserver
```

## 🧪 Testing Payment Flow

### Test Step 1: Book an Appointment
1. Login as Patient
2. Go to "Doctors" tab
3. Click "View Availability" on a doctor
4. Book a slot → Should redirect to payment page

### Test Step 2: Complete Payment (Sandbox)
1. Payment page should show appointment details
2. Click "Pay with Razorpay"
3. Razorpay modal opens
4. Use test card: **4111 1111 1111 1111**
5. Any future date for expiry
6. Any 3-digit CVV
7. Enter OTP: **123456**
8. Payment should complete → Redirect to dashboard

### Test Step 3: Verify in Database
```bash
# Check booking payment status
python manage.py shell
>>> from bookings.models import Booking, Transaction
>>> b = Booking.objects.latest('id')
>>> print(b.payment_status)  # Should be 'completed'
>>> print(b.is_paid())       # Should be True
>>> t = Transaction.objects.filter(booking=b).first()
>>> print(t.amount)          # Should show payment amount
```

## 📋 Verification Checklist

### Payment Page Display
- [ ] Appointment details show correctly
- [ ] Consultation fee displays with amount
- [ ] Doctor name and time are correct
- [ ] "Pay Now" button is clickable

### Payment Processing
- [ ] Razorpay modal opens on button click
- [ ] Test card payment succeeds
- [ ] Loading overlay shows during verification
- [ ] Success message appears after payment

### Dashboard Updates
- [ ] Booking shows status as "Paid"
- [ ] Payment status badge is green
- [ ] "Pay" button disappears from bookings list
- [ ] "Complete Payment" button hidden from dashboard

### Database Records
- [ ] Booking.payment_status = 'completed'
- [ ] Booking.payment_id = razorpay payment ID
- [ ] Booking.consultation_fee set correctly
- [ ] Transaction record created with payment details

### Email Confirmation
- [ ] Confirmation email sent to patient
- [ ] Email includes appointment and payment details
- [ ] (Check settings if using real email or console backend)

## 🔧 Common Issues & Solutions

### Issue: "payment_status field does not exist"
**Solution:**
```bash
python manage.py migrate
# Make sure you're in hms/ directory
```

### Issue: "Razorpay module not found"
**Solution:**
```bash
pip install razorpay==1.4.1
```

### Issue: "RAZORPAY_KEY_ID is None"
**Solution:**
```bash
# Check .env file exists in hms/ directory
# Verify you have: RAZORPAY_KEY_ID=rzp_test_xxxxx
```

### Issue: Payment modal doesn't open
**Solution:**
- Open browser DevTools (F12)
- Check Console tab for JavaScript errors
- Verify Razorpay key ID is correct
- Clear browser cache and reload

### Issue: "Signature verification failed"
**Solution:**
- Ensure RAZORPAY_KEY_SECRET is correct
- Verify it's not truncated in .env
- Restart Django server after changing .env

## 📊 Production Deployment Steps

### Step 1: Get Production Keys
1. Login to Razorpay Dashboard
2. Change mode from "Test" to "Live"
3. Copy Live Key ID and Secret

### Step 2: Update Environment
```env
RAZORPAY_KEY_ID=rzp_live_YOUR_LIVE_KEY_ID
RAZORPAY_KEY_SECRET=your_live_key_secret
```

### Step 3: Test with Real Payment
- Use real credit/debit card
- Verify payment processes
- Check transaction in Razorpay dashboard

### Step 4: Monitor & Support
- Check Django logs for errors
- Monitor Razorpay dashboard for failed payments
- Setup email alerts for failures

## 📞 Testing with Real Razorpay Keys (After Development)

[See PAYMENT_SETUP.md for complete production documentation]

## 🎯 Key Routes Added

| URL | Method | Purpose |
|-----|--------|---------|
| `/bookings/payment/<booking_id>/` | GET | Display payment page |
| `/bookings/verify-payment/` | POST | Process payment verification |

## 💾 Files Changed Summary

### Backend
- ✅ hms/bookings/models.py - Added payment fields
- ✅ hms/bookings/views.py - Added payment endpoints
- ✅ hms/bookings/urls.py - Added payment routes
- ✅ hms/config/settings.py - Added Razorpay config

### Frontend
- ✅ hms/templates/bookings/payment.html - Payment page
- ✅ hms/templates/bookings/payment_modal_content.html - Payment modal
- ✅ hms/templates/patients/bookings_iframe.html - Updated with fee & status
- ✅ hms/templates/patients/dashboard_iframe.html - Updated with payment section

### Database
- ✅ hms/bookings/migrations/0002_booking_payment_fields.py - Schema migration

### Configuration
- ✅ hms/requirements.txt - Added razorpay package
- ✅ .env.example - Added Razorpay credentials

## 🔒 Security Checklist

- [ ] RAZORPAY_KEY_SECRET never hardcoded ✓
- [ ] All keys in .env (not in git)
- [ ] Signature verification enabled ✓
- [ ] CSRF protection on payment endpoints ✓
- [ ] Amount validation server-side ✓
- [ ] User authentication required ✓
- [ ] Payment IDs logged for audit ✓

## 📈 Next Phase Features (Optional)

After basic payment works, consider:
1. **Webhooks** - Real-time payment confirmation
2. **Payment History** - Transaction reports
3. **Failed Payment Recovery** - Retry mechanism
4. **Refunds** - Admin refund portal
5. **Invoices** - PDF invoice generation
6. **Multiple Payments** - Support for UPI, wallets

---

**Status**: ✅ Implementation Complete | ⏳ Awaiting Migration & Testing
