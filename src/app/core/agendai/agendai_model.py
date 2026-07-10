"""SQLModel entities for the AgendAI yard-management domain."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field

from src.app.core.common.model.base import BaseModel


class AppointmentStatus(str, Enum):
    """Operational status for a receiving appointment."""

    PENDING = "pending"
    CHECKED_IN = "checked_in"
    RECEIVING = "receiving"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class CheckInMethod(str, Enum):
    """How a driver check-in was recorded."""

    QR_CODE = "qr_code"
    MANUAL = "manual"


class AlertSeverity(str, Enum):
    """Severity for operational yard alerts."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Lifecycle status for yard alerts."""

    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class BusinessRuleDocumentStatus(str, Enum):
    """Lifecycle status for business-rule documents."""

    STUB = "stub"
    UPLOADED = "uploaded"
    INDEXED = "indexed"
    DISABLED = "disabled"


class AgendAIDriver(BaseModel, table=True):
    """Driver registered to interact with the yard receiving flow."""

    __tablename__ = "agendai_driver"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=1)
    cpf: str = Field(index=True, unique=True, min_length=1)
    email: Optional[str] = Field(default=None, index=True)
    phone: Optional[str] = Field(default=None, index=True)
    company: Optional[str] = Field(default=None, index=True)
    notes: str = Field(default="")


class AgendAIVehicle(BaseModel, table=True):
    """Vehicle used by a driver for receiving appointments."""

    __tablename__ = "agendai_vehicle"

    id: Optional[int] = Field(default=None, primary_key=True)
    driver_id: int = Field(foreign_key="agendai_driver.id", index=True)
    plate: str = Field(index=True, unique=True, min_length=1)
    model: Optional[str] = Field(default=None)
    color: Optional[str] = Field(default=None)
    year: Optional[int] = Field(default=None, ge=1900, le=2100)


class AgendAISupplier(BaseModel, table=True):
    """Supplier or origin related to a receiving appointment."""

    __tablename__ = "agendai_supplier"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=1)
    contact_email: Optional[str] = Field(default=None, index=True)
    contact_phone: Optional[str] = Field(default=None)
    authorized_email_domain: Optional[str] = Field(default=None)


class AgendAIAppointment(BaseModel, table=True):
    """Receiving appointment scheduled for a driver, vehicle and supplier."""

    __tablename__ = "agendai_appointment"

    id: Optional[int] = Field(default=None, primary_key=True)
    driver_id: int = Field(foreign_key="agendai_driver.id", index=True)
    vehicle_id: int = Field(foreign_key="agendai_vehicle.id", index=True)
    supplier_id: int = Field(foreign_key="agendai_supplier.id", index=True)
    scheduled_at: datetime = Field(index=True)
    dock: Optional[str] = Field(default=None, index=True)
    load_reference: Optional[str] = Field(default=None, index=True)
    status: AppointmentStatus = Field(default=AppointmentStatus.PENDING, index=True)
    notes: str = Field(default="")
    created_by_user_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)


class AgendAICheckIn(BaseModel, table=True):
    """Check-in event for a receiving appointment."""

    __tablename__ = "agendai_check_in"

    id: Optional[int] = Field(default=None, primary_key=True)
    appointment_id: int = Field(foreign_key="agendai_appointment.id", index=True)
    checked_in_at: datetime = Field(index=True)
    method: CheckInMethod = Field(default=CheckInMethod.QR_CODE, index=True)
    confirmed_by_user_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)
    notes: str = Field(default="")


class AgendAIYardAlert(BaseModel, table=True):
    """Operational alert shown to the receiving team."""

    __tablename__ = "agendai_yard_alert"

    id: Optional[int] = Field(default=None, primary_key=True)
    appointment_id: int = Field(foreign_key="agendai_appointment.id", index=True)
    alert_type: str = Field(index=True, min_length=1)
    severity: AlertSeverity = Field(default=AlertSeverity.WARNING, index=True)
    message: str = Field(min_length=1)
    status: AlertStatus = Field(default=AlertStatus.OPEN, index=True)
    resolved_at: Optional[datetime] = Field(default=None)
    resolved_by_user_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)


class AgendAIBusinessRuleDocument(BaseModel, table=True):
    """Metadata for future MinIO business-rule documents."""

    __tablename__ = "agendai_business_rule_document"

    id: Optional[int] = Field(default=None, primary_key=True)
    file_name: str = Field(index=True, min_length=1)
    source: str = Field(default="stub", index=True)
    bucket: Optional[str] = Field(default=None)
    object_key: Optional[str] = Field(default=None, index=True)
    status: BusinessRuleDocumentStatus = Field(default=BusinessRuleDocumentStatus.STUB, index=True)
