# Dummy Services Usage Examples

## 1. Dummy Payment Processing

```python
from utils.payment_processor import process_payment, refund_payment, verify_card

# Process a payment
result = process_payment(
    amount=150.00,
    payment_method="credit_card",
    card_number="4111111111111111",  # Test card
    cvv="123",
    expiry="12/25"
)

print(result)
# Output:
# {
#     "success": True,
#     "transaction_id": "TXN-20260112143045-A1B2C3D4",
#     "amount": 150.0,
#     "payment_method": "credit_card",
#     "message": "Payment processed successfully (DEMO MODE)",
#     "timestamp": "2026-01-12T14:30:45.123456",
#     "card_last4": "1111"
# }

# Test declined payment (card ending in 0000)
declined = process_payment(
    amount=100.00,
    payment_method="credit_card",
    card_number="4111111111110000",  # Will be declined
    cvv="123",
    expiry="12/25"
)

# Process refund
refund = refund_payment(
    transaction_id="TXN-20260112143045-A1B2C3D4",
    amount=150.00
)
```

## 2. Dummy SMS Notifications

```python
from utils.sms_service import (
    send_sms,
    send_verification_code,
    send_appointment_reminder,
    send_medication_reminder
)

# Send generic SMS
result = send_sms(
    phone_number="+1234567890",
    message="Your appointment is confirmed!"
)

# Send verification code
result = send_verification_code(
    phone_number="+1234567890",
    code="123456"
)

# Send appointment reminder
result = send_appointment_reminder(
    phone_number="+1234567890",
    doctor_name="Smith",
    appointment_time="2026-01-15 10:00 AM"
)

# Send medication reminder
result = send_medication_reminder(
    phone_number="+1234567890",
    medication_name="Amoxicillin",
    dosage="500mg"
)

# All SMS will print to console like this:
# ============================================================
# 📱 DUMMY SMS NOTIFICATION
# ============================================================
# To: +1234567890
# Message: Your MediSecure verification code is: 123456
# Time: 2026-01-12T14:30:45.123456
# ============================================================
```

## 3. Integration in Services

### In BillingService:
```python
from utils.payment_processor import process_payment

# In the process_payment method
payment_result = process_payment(
    amount=payment_data.amount,
    payment_method=payment_data.payment_method,
    card_number=payment_data.card_number,  # Optional
    cvv=payment_data.cvv,  # Optional
    expiry=payment_data.expiry  # Optional
)

if payment_result["success"]:
    # Create payment record
    payment = Payment(
        invoice_id=invoice_id,
        patient_id=patient_id,
        transaction_id=payment_result["transaction_id"],
        amount=payment_data.amount,
        payment_method=payment_data.payment_method,
        is_successful=True
    )
```

### In NotificationService:
```python
from utils.sms_service import send_appointment_reminder

# Send reminder
sms_result = send_appointment_reminder(
    phone_number=patient.phone,
    doctor_name=doctor.full_name,
    appointment_time=appointment.appointment_date.strftime("%Y-%m-%d %I:%M %p")
)
```

## 4. Testing Tips

### Test Card Numbers (Dummy):
- `4111111111111111` - Successful payment
- `4111111111110000` - Declined payment (any card ending in 0000)

### Test Phone Numbers:
- Any valid phone format works (minimum 10 digits)
- Example: `+1234567890`, `1234567890`, etc.

### Console Output:
All SMS messages will print to console with clear formatting for easy testing.

### Payment Logging:
All payment transactions are logged with INFO level for easy debugging.

## 5. Replacing with Real Services (Production)

When ready for production, simply replace the implementations:

### For Real Payment Processing:
```python
# Replace utils/payment_processor.py with:
import stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def process_payment(amount, payment_method, **kwargs):
    charge = stripe.Charge.create(
        amount=int(amount * 100),  # Convert to cents
        currency="usd",
        source=kwargs.get("token"),
        description="MediSecure Payment"
    )
    return {
        "success": True,
        "transaction_id": charge.id,
        "amount": amount,
        ...
    }
```

### For Real SMS:
```python
# Replace utils/sms_service.py with:
from twilio.rest import Client

client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

def send_sms(phone_number, message):
    message = client.messages.create(
        body=message,
        from_=os.getenv("TWILIO_PHONE_NUMBER"),
        to=phone_number
    )
    return {"success": True, "message": "SMS sent"}
```

## Note:
These dummy services are perfect for:
- Development and testing
- Demo purposes
- MVP without payment processing costs
- Learning and prototyping

No paid services required! 🎉
