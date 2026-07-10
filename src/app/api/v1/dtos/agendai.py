"""Request and response models for AgendAI domain endpoints."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from src.app.core.agendai.agendai_model import (
    AlertSeverity,
    AlertStatus,
    AppointmentStatus,
    BusinessRuleDocumentStatus,
    CheckInMethod,
)


class DriverCreate(BaseModel):
    """Create a driver registration."""

    name: str = Field(..., min_length=1, max_length=160)
    cpf: str = Field(..., min_length=1, max_length=32)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=40)
    company: Optional[str] = Field(default=None, max_length=160)
    notes: str = Field(default="", max_length=1000)


class DriverResponse(DriverCreate):
    """Driver returned by the API."""

    id: int
    created_at: datetime


class VehicleCreate(BaseModel):
    """Create a vehicle registration."""

    driver_id: int = Field(..., ge=1)
    plate: str = Field(..., min_length=1, max_length=20)
    model: Optional[str] = Field(default=None, max_length=120)
    color: Optional[str] = Field(default=None, max_length=60)
    year: Optional[int] = Field(default=None, ge=1900, le=2100)


class VehicleResponse(VehicleCreate):
    """Vehicle returned by the API."""

    id: int
    created_at: datetime


class SupplierCreate(BaseModel):
    """Create a supplier."""

    name: str = Field(..., min_length=1, max_length=180)
    contact_email: Optional[str] = Field(default=None, max_length=255)
    contact_phone: Optional[str] = Field(default=None, max_length=40)
    authorized_email_domain: Optional[str] = Field(default=None, max_length=180)


class SupplierResponse(SupplierCreate):
    """Supplier returned by the API."""

    id: int
    created_at: datetime


class AppointmentCreate(BaseModel):
    """Create a receiving appointment."""

    driver_id: int = Field(..., ge=1)
    vehicle_id: int = Field(..., ge=1)
    supplier_id: int = Field(..., ge=1)
    scheduled_at: datetime
    dock: Optional[str] = Field(default=None, max_length=80)
    load_reference: Optional[str] = Field(default=None, max_length=120)
    notes: str = Field(default="", max_length=1000)


class AppointmentResponse(AppointmentCreate):
    """Appointment returned by the API."""

    id: int
    status: AppointmentStatus
    created_by_user_id: Optional[int] = None
    created_at: datetime


class CheckInCreate(BaseModel):
    """Register a check-in for an appointment."""

    checked_in_at: Optional[datetime] = None
    method: CheckInMethod = CheckInMethod.QR_CODE
    notes: str = Field(default="", max_length=1000)


class CheckInResponse(CheckInCreate):
    """Check-in returned by the API."""

    id: int
    appointment_id: int
    confirmed_by_user_id: Optional[int] = None
    created_at: datetime


class YardAlertResponse(BaseModel):
    """Operational yard alert."""

    id: int
    appointment_id: int
    alert_type: str
    severity: AlertSeverity
    message: str
    status: AlertStatus
    resolved_at: Optional[datetime] = None
    resolved_by_user_id: Optional[int] = None
    created_at: datetime


class DashboardSummaryResponse(BaseModel):
    """Counters for the AgendAI dashboard."""

    pending_appointments: int
    completed_appointments: int
    check_ins: int
    late_loads: int


class AppointmentDetailResponse(BaseModel):
    """Appointment detail with related receiving information."""

    appointment: AppointmentResponse
    driver: DriverResponse
    vehicle: VehicleResponse
    supplier: SupplierResponse
    check_ins: List[CheckInResponse]
    alerts: List[YardAlertResponse]


class BusinessRuleDocumentResponse(BaseModel):
    """Metadata for future MinIO business-rule documents."""

    id: int
    file_name: str
    source: str
    bucket: Optional[str] = None
    object_key: Optional[str] = None
    status: BusinessRuleDocumentStatus
    created_at: datetime


class LateAlertGenerationResponse(BaseModel):
    """Result of late-alert generation."""

    created_alerts: List[YardAlertResponse]


class IntegrationStatusResponse(BaseModel):
    """Status of external integrations in the AgendAI MVP."""

    gmail_enabled: bool
    whatsapp_enabled: bool
    minio_enabled: bool
