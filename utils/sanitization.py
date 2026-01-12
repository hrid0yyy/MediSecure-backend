import bleach
import re
from typing import Any, Dict, List, Union

class InputSanitizer:
    """
    Utility class for sanitizing user input to prevent XSS, SQL injection,
    and other injection attacks.
    """
    
    # Allowed HTML tags for rich text (if needed)
    ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li']
    ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """
        Sanitize HTML input to prevent XSS attacks.
        Removes all HTML tags except whitelisted ones.
        """
        if not text:
            return text
        
        return bleach.clean(
            text,
            tags=InputSanitizer.ALLOWED_TAGS,
            attributes=InputSanitizer.ALLOWED_ATTRIBUTES,
            strip=True
        )
    
    @staticmethod
    def strip_html(text: str) -> str:
        """
        Completely strip all HTML tags from input.
        Use this for plain text fields.
        """
        if not text:
            return text
        
        return bleach.clean(text, tags=[], strip=True)
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """
        Sanitize email input.
        Converts to lowercase and removes dangerous characters.
        """
        if not email:
            return email
        
        email = email.lower().strip()
        # Remove any HTML tags
        email = InputSanitizer.strip_html(email)
        # Basic email validation pattern
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError("Invalid email format")
        
        return email
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = None) -> str:
        """
        General string sanitization.
        Removes HTML, trims whitespace, and limits length.
        """
        if not text:
            return text
        
        # Strip HTML
        text = InputSanitizer.strip_html(text)
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove control characters except newlines and tabs
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        
        # Trim whitespace
        text = text.strip()
        
        # Limit length
        if max_length and len(text) > max_length:
            text = text[:max_length]
        
        return text
    
    @staticmethod
    def sanitize_phone(phone: str) -> str:
        """
        Sanitize phone number input.
        Keeps only digits, plus, and hyphens.
        """
        if not phone:
            return phone
        
        # Remove all characters except digits, +, -, (, ), and spaces
        phone = re.sub(r'[^\d+\-() ]', '', phone)
        return phone.strip()
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any], string_fields: List[str] = None, 
                     max_length: int = 1000) -> Dict[str, Any]:
        """
        Sanitize dictionary data.
        
        Args:
            data: Dictionary to sanitize
            string_fields: List of field names to sanitize as strings
            max_length: Maximum length for string fields
        
        Returns:
            Sanitized dictionary
        """
        if not data:
            return data
        
        sanitized = {}
        
        for key, value in data.items():
            # Sanitize the key itself
            clean_key = InputSanitizer.sanitize_string(str(key), 100)
            
            # Sanitize the value based on type
            if isinstance(value, str):
                if string_fields and key in string_fields:
                    sanitized[clean_key] = InputSanitizer.sanitize_string(value, max_length)
                else:
                    sanitized[clean_key] = InputSanitizer.strip_html(value)
            elif isinstance(value, dict):
                sanitized[clean_key] = InputSanitizer.sanitize_dict(value, string_fields, max_length)
            elif isinstance(value, list):
                sanitized[clean_key] = [
                    InputSanitizer.sanitize_string(item, max_length) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                sanitized[clean_key] = value
        
        return sanitized
    
    @staticmethod
    def validate_no_sql_injection(text: str) -> bool:
        """
        Check for common SQL injection patterns.
        This is a basic check - parameterized queries are the main defense.
        """
        if not text:
            return True
        
        # Common SQL injection patterns
        sql_patterns = [
            r"(\bOR\b|\bAND\b).*=.*",
            r"(\'|\")(\s)*(or|OR|and|AND)(\s)*(\d+)(\s)*=(\s)*(\d+)",
            r"(\bUNION\b|\bSELECT\b|\bDROP\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b)",
            r"(--|#|\/\*)",
            r"(\bEXEC\b|\bEXECUTE\b)",
            r"xp_cmdshell"
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        return True
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal attacks.
        """
        if not filename:
            return filename
        
        # Remove path separators
        filename = filename.replace('/', '').replace('\\', '')
        
        # Remove null bytes
        filename = filename.replace('\x00', '')
        
        # Allow only alphanumeric, dots, underscores, and hyphens
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Prevent hidden files
        if filename.startswith('.'):
            filename = '_' + filename[1:]
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:200] + ('.' + ext if ext else '')
        
        return filename


# Convenience functions for common use cases
def sanitize_user_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize user input data for general use.
    """
    return InputSanitizer.sanitize_dict(
        data,
        string_fields=['name', 'description', 'notes', 'message'],
        max_length=5000
    )


def validate_input_safety(text: str) -> bool:
    """
    Check if input is safe (no SQL injection patterns).
    """
    return InputSanitizer.validate_no_sql_injection(text)
