"""Audit logging for sensitive operations"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, String, DateTime, JSON, Integer
from sqlalchemy.orm import Session
from src.database.models import Base
from src.utils.logger import get_logger

logger = get_logger("audit")


class AuditLog(Base):
    """Audit log for sensitive operations"""
    __tablename__ = "audit_logs"
    
    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)  # e.g., "account", "trade", "strategy"
    resource_id = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False)  # "success", "failed", "pending"
    details = Column(JSON, default={})
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLogger:
    """Log sensitive operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_action(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        status: str = "success",
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """
        Log an action
        
        Args:
            action: e.g., "create", "update", "delete", "trade_executed"
            resource_type: e.g., "account", "trade", "strategy"
            resource_id: ID of the resource
            status: "success", "failed", "pending"
            details: Additional details
            user_id: User performing action
            ip_address: IP address of request
        """
        try:
            import uuid
            log_id = f"audit_{uuid.uuid4().hex[:8]}"
            
            audit_record = AuditLog(
                id=log_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                status=status,
                details=details or {},
                user_id=user_id,
                ip_address=ip_address
            )
            
            self.db.add(audit_record)
            self.db.commit()
            
            level = "info" if status == "success" else "warning"
            getattr(logger, level)(
                f"[AUDIT] {action} {resource_type} {resource_id}: {status}"
            )
        
        except Exception as e:
            logger.error(f"Failed to log audit: {e}")
    
    def get_account_audit_log(self, resource_id: str, limit: int = 100) -> list:
        """
        Get audit log for an account
        """
        return self.db.query(AuditLog).filter(
            AuditLog.resource_type == "account",
            AuditLog.resource_id == resource_id
        ).order_by(AuditLog.created_at.desc()).limit(limit).all()
    
    def get_trade_audit_log(self, resource_id: str) -> list:
        """
        Get audit log for a trade
        """
        return self.db.query(AuditLog).filter(
            AuditLog.resource_type == "trade",
            AuditLog.resource_id == resource_id
        ).order_by(AuditLog.created_at.desc()).all()
    
    def get_all_audit_logs(self, limit: int = 1000) -> list:
        """
        Get all recent audit logs
        """
        return self.db.query(AuditLog).order_by(
            AuditLog.created_at.desc()
        ).limit(limit).all()
