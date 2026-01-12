"""
Dummy payment processing service for development/demo purposes.
Replace with real payment gateway (Stripe, PayPal, etc.) in production.
"""
import secrets
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DummyPaymentProcessor:
    """Simulates payment processing without actual transactions"""
    
    @staticmethod
    def process_payment(
        amount: float,
        payment_method: str,
        card_number: Optional[str] = None,
        cvv: Optional[str] = None,
        expiry: Optional[str] = None
    ) -> dict:
        """
        Simulate payment processing
        
        Args:
            amount: Payment amount
            payment_method: Payment method (credit_card, debit_card, etc.)
            card_number: Card number (dummy)
            cvv: CVV (dummy)
            expiry: Expiry date (dummy)
            
        Returns:
            dict with transaction details
        """
        # Generate fake transaction ID
        transaction_id = f"TXN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(4).upper()}"
        
        # Simulate processing delay
        logger.info(f"[DUMMY PAYMENT] Processing ${amount:.2f} via {payment_method}")
        
        # Simulate success (you can add failure simulation for testing)
        if card_number and card_number.endswith("0000"):
            # Simulate declined card
            logger.warning(f"[DUMMY PAYMENT] Payment declined for amount ${amount:.2f}")
            return {
                "success": False,
                "transaction_id": None,
                "message": "Payment declined - card ending in 0000",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        logger.info(f"[DUMMY PAYMENT] Payment successful! Transaction ID: {transaction_id}")
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "amount": amount,
            "payment_method": payment_method,
            "message": "Payment processed successfully (DEMO MODE)",
            "timestamp": datetime.utcnow().isoformat(),
            "card_last4": card_number[-4:] if card_number else "XXXX"
        }
    
    @staticmethod
    def refund_payment(transaction_id: str, amount: float) -> dict:
        """
        Simulate payment refund
        
        Args:
            transaction_id: Original transaction ID
            amount: Refund amount
            
        Returns:
            dict with refund details
        """
        refund_id = f"RFD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(4).upper()}"
        
        logger.info(f"[DUMMY PAYMENT] Processing refund of ${amount:.2f} for transaction {transaction_id}")
        
        return {
            "success": True,
            "refund_id": refund_id,
            "transaction_id": transaction_id,
            "amount": amount,
            "message": "Refund processed successfully (DEMO MODE)",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def verify_card(card_number: str, cvv: str, expiry: str) -> dict:
        """
        Simulate card verification
        
        Args:
            card_number: Card number
            cvv: CVV
            expiry: Expiry date (MM/YY)
            
        Returns:
            dict with verification result
        """
        logger.info(f"[DUMMY PAYMENT] Verifying card ending in {card_number[-4:]}")
        
        # Simple validation
        if len(card_number) < 13 or len(card_number) > 19:
            return {"valid": False, "message": "Invalid card number length"}
        
        if len(cvv) < 3 or len(cvv) > 4:
            return {"valid": False, "message": "Invalid CVV"}
        
        return {
            "valid": True,
            "card_type": "DEMO",
            "card_last4": card_number[-4:],
            "message": "Card verified (DEMO MODE)"
        }


# Global instance
payment_processor = DummyPaymentProcessor()


def process_payment(
    amount: float,
    payment_method: str = "credit_card",
    **kwargs
) -> dict:
    """
    Process a payment
    
    Usage:
        result = process_payment(
            amount=100.50,
            payment_method="credit_card",
            card_number="4111111111111111",
            cvv="123",
            expiry="12/25"
        )
    """
    return payment_processor.process_payment(amount, payment_method, **kwargs)


def refund_payment(transaction_id: str, amount: float) -> dict:
    """Process a refund"""
    return payment_processor.refund_payment(transaction_id, amount)


def verify_card(card_number: str, cvv: str, expiry: str) -> dict:
    """Verify a card"""
    return payment_processor.verify_card(card_number, cvv, expiry)
