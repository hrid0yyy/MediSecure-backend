"""
Dummy SMS notification service for development/demo purposes.
Replace with real SMS gateway (Twilio, AWS SNS, etc.) in production.
"""
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class DummySMSService:
    """Simulates SMS sending without actual SMS delivery"""
    
    def __init__(self):
        self.sent_messages = []  # Store for testing/debugging
    
    def send_sms(self, phone_number: str, message: str) -> dict:
        """
        Simulate sending SMS
        
        Args:
            phone_number: Recipient phone number
            message: SMS message content
            
        Returns:
            dict with sending status
        """
        # Validate phone number format (basic)
        if not phone_number or len(phone_number) < 10:
            logger.error(f"[DUMMY SMS] Invalid phone number: {phone_number}")
            return {
                "success": False,
                "message": "Invalid phone number",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Simulate SMS sending
        logger.info(f"[DUMMY SMS] Sending to {phone_number}")
        logger.info(f"[DUMMY SMS] Message: {message}")
        
        # Store message for debugging
        sms_record = {
            "phone_number": phone_number,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "sent"
        }
        self.sent_messages.append(sms_record)
        
        # Print to console for visibility during development
        print("\n" + "="*60)
        print("📱 DUMMY SMS NOTIFICATION")
        print("="*60)
        print(f"To: {phone_number}")
        print(f"Message: {message}")
        print(f"Time: {sms_record['timestamp']}")
        print("="*60 + "\n")
        
        return {
            "success": True,
            "phone_number": phone_number,
            "message": "SMS sent successfully (DEMO MODE)",
            "timestamp": sms_record['timestamp']
        }
    
    def send_verification_code(self, phone_number: str, code: str) -> dict:
        """Send verification code via SMS"""
        message = f"Your MediSecure verification code is: {code}. Valid for 10 minutes."
        return self.send_sms(phone_number, message)
    
    def send_appointment_reminder(
        self,
        phone_number: str,
        doctor_name: str,
        appointment_time: str
    ) -> dict:
        """Send appointment reminder"""
        message = (
            f"Reminder: You have an appointment with Dr. {doctor_name} "
            f"on {appointment_time}. - MediSecure"
        )
        return self.send_sms(phone_number, message)
    
    def send_medication_reminder(
        self,
        phone_number: str,
        medication_name: str,
        dosage: str
    ) -> dict:
        """Send medication reminder"""
        message = (
            f"Reminder: Take {medication_name} ({dosage}). - MediSecure"
        )
        return self.send_sms(phone_number, message)
    
    def send_prescription_ready(
        self,
        phone_number: str,
        pharmacy_name: str
    ) -> dict:
        """Send prescription ready notification"""
        message = (
            f"Your prescription is ready for pickup at {pharmacy_name}. - MediSecure"
        )
        return self.send_sms(phone_number, message)
    
    def get_sent_messages(self, phone_number: Optional[str] = None) -> list:
        """Get sent messages (for testing/debugging)"""
        if phone_number:
            return [msg for msg in self.sent_messages if msg["phone_number"] == phone_number]
        return self.sent_messages
    
    def clear_history(self):
        """Clear message history (for testing)"""
        self.sent_messages = []


# Global instance
sms_service = DummySMSService()


def send_sms(phone_number: str, message: str) -> dict:
    """
    Send SMS notification
    
    Usage:
        result = send_sms(
            phone_number="+1234567890",
            message="Your appointment is confirmed."
        )
    """
    return sms_service.send_sms(phone_number, message)


def send_verification_code(phone_number: str, code: str) -> dict:
    """Send verification code"""
    return sms_service.send_verification_code(phone_number, code)


def send_appointment_reminder(
    phone_number: str,
    doctor_name: str,
    appointment_time: str
) -> dict:
    """Send appointment reminder"""
    return sms_service.send_appointment_reminder(phone_number, doctor_name, appointment_time)


def send_medication_reminder(
    phone_number: str,
    medication_name: str,
    dosage: str
) -> dict:
    """Send medication reminder"""
    return sms_service.send_medication_reminder(phone_number, medication_name, dosage)


def send_prescription_ready(phone_number: str, pharmacy_name: str) -> dict:
    """Send prescription ready notification"""
    return sms_service.send_prescription_ready(phone_number, pharmacy_name)
