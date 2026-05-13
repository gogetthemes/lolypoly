"""2FA (Two-Factor Authentication) module"""

import secrets
import smtplib
from datetime import datetime, timedelta
from typing import Optional, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, DateTime, Integer
from src.database.models import Base
from src.utils.logger import get_logger
from src.config import settings

logger = get_logger("2fa")


class TwoFactorAuth(Base):
    """2FA verification codes storage"""
    __tablename__ = "two_factor_auth"
    
    id = Column(String(50), primary_key=True)
    account_id = Column(String(50), nullable=False)
    code = Column(String(6), nullable=False)
    operation = Column(String(100), nullable=False)  # e.g., "trade_execution", "credential_change"
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    verified = Column(Integer, default=0)  # 0=pending, 1=verified
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)


class TwoFactorAuthManager:
    """Manage 2FA codes and verification"""
    
    def __init__(self, db: Session, config: dict = None):
        self.db = db
        self.code_length = config.get("code_length", 6) if config else 6
        self.code_expiry = config.get("code_expiry_minutes", 10) if config else 10
        self.enable_email = config.get("enable_email_2fa", True) if config else True
        self.smtp_server = config.get("smtp_server") if config else "smtp.gmail.com"
        self.smtp_port = config.get("smtp_port", 587) if config else 587
        self.email_from = config.get("email_from") if config else None
        self.email_password = config.get("email_password") if config else None
    
    def generate_code(self, account_id: str, operation: str, email: str = None) -> Tuple[bool, str]:
        """
        Generate a 2FA code and send to user
        Returns: (success, message)
        """
        try:
            # Generate random code
            code = str(secrets.randbelow(10 ** self.code_length)).zfill(self.code_length)
            
            # Create verification record
            import uuid
            auth_id = f"2fa_{uuid.uuid4().hex[:8]}"
            
            expires_at = datetime.utcnow() + timedelta(minutes=self.code_expiry)
            
            auth_record = TwoFactorAuth(
                id=auth_id,
                account_id=account_id,
                code=code,
                operation=operation,
                expires_at=expires_at
            )
            
            self.db.add(auth_record)
            self.db.commit()
            
            # Send code if email provided
            if email and self.enable_email:
                success, msg = self._send_code_email(email, code, operation)
                if not success:
                    logger.warning(f"Failed to send 2FA code: {msg}")
                    return False, f"Generated code {code} but failed to send email. {msg}"
            
            logger.info(f"2FA code generated for account {account_id}, operation: {operation}")
            return True, f"2FA code sent to {email if email else 'your registered email'}. Code expires in {self.code_expiry} minutes"
        
        except Exception as e:
            logger.error(f"Error generating 2FA code: {e}")
            return False, f"Error generating 2FA code: {str(e)}"
    
    def verify_code(self, account_id: str, operation: str, code: str) -> Tuple[bool, str]:
        """
        Verify a 2FA code
        Returns: (is_valid, message)
        """
        try:
            # Find most recent code for this account and operation
            auth_record = self.db.query(TwoFactorAuth).filter(
                TwoFactorAuth.account_id == account_id,
                TwoFactorAuth.operation == operation,
                TwoFactorAuth.verified == 0,
                TwoFactorAuth.expires_at > datetime.utcnow()
            ).order_by(TwoFactorAuth.created_at.desc()).first()
            
            if not auth_record:
                logger.warning(f"No valid 2FA code found for {account_id}")
                return False, "No valid 2FA code found. Please request a new one."
            
            # Check attempts
            if auth_record.attempts >= auth_record.max_attempts:
                logger.warning(f"Max 2FA attempts exceeded for {account_id}")
                return False, "Maximum attempts exceeded. Please request a new code."
            
            # Check code
            auth_record.attempts += 1
            
            if code == auth_record.code:
                auth_record.verified = 1
                self.db.commit()
                logger.info(f"2FA code verified for account {account_id}")
                return True, "2FA verification successful"
            else:
                self.db.commit()
                remaining = auth_record.max_attempts - auth_record.attempts
                return False, f"Invalid code. {remaining} attempts remaining."
        
        except Exception as e:
            logger.error(f"Error verifying 2FA code: {e}")
            return False, f"Error verifying code: {str(e)}"
    
    def _send_code_email(self, email: str, code: str, operation: str) -> Tuple[bool, str]:
        """
        Send 2FA code via email
        Returns: (success, message)
        """
        try:
            if not self.email_from or not self.email_password:
                return False, "Email configuration not set up"
            
            subject = "Your 2FA Code for LolyPoly"
            body = f"""
            Your 2FA code for operation '{operation}': {code}
            
            This code expires in {self.code_expiry} minutes.
            
            If you did not request this code, please ignore this email.
            
            Do not share this code with anyone.
            """
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)
                server.send_message(msg)
            
            logger.info(f"2FA code sent to {email}")
            return True, "Code sent successfully"
        
        except Exception as e:
            logger.error(f"Error sending 2FA email: {e}")
            return False, f"Email sending failed: {str(e)}"
    
    def is_code_verified(self, account_id: str, operation: str) -> bool:
        """
        Check if 2FA code was verified for operation
        """
        auth_record = self.db.query(TwoFactorAuth).filter(
            TwoFactorAuth.account_id == account_id,
            TwoFactorAuth.operation == operation,
            TwoFactorAuth.verified == 1,
            TwoFactorAuth.expires_at > datetime.utcnow()
        ).order_by(TwoFactorAuth.created_at.desc()).first()
        
        return auth_record is not None
