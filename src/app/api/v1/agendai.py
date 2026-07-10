"""AgendAI API endpoints for yard-management operations."""

from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
)

from src.app.api.security.limiter import limiter
from src.app.api.v1.auth import get_current_session
from src.app.api.v1.dtos.agendai import (
    AppointmentCreate,
    AppointmentDetailResponse,
    AppointmentResponse,
    BusinessRuleDocumentResponse,
    CheckInCreate,
    CheckInResponse,
    DashboardSummaryResponse,
    DriverCreate,
    DriverResponse,
    IntegrationStatusResponse,
    LateAlertGenerationResponse,
    SupplierCreate,
    SupplierResponse,
    VehicleCreate,
    VehicleResponse,
    YardAlertResponse,
)
from src.app.core.agendai.agendai_model import AlertStatus, AppointmentStatus
from src.app.core.agendai.integrations import integration_status
from src.app.core.common.config import settings
from src.app.core.common.logging import logger
from src.app.core.session.session_model import Session
from src.app.init import agendai_repository

router = APIRouter()


@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["agendai"][0])
async def dashboard_summary(
    request: Request,
    session: Session = Depends(get_current_session),
) -> DashboardSummaryResponse:
    """Return dashboard counters for the receiving team."""
    try:
        summary = await agendai_repository.get_dashboard_summary()
        logger.info("agendai_dashboard_summary_loaded", session_id=session.id)
        return DashboardSummaryResponse(**summary)
    except Exception:
        logger.exception("agendai_dashboard_summary_failed", session_id=session.id)
        raise HTTPException(status_code=500, detail="Erro ao carregar resumo do AgendAI.")


@router.get("/appointments", response_model=list[AppointmentResponse])
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["agendai"][0])
async def list_appointments(
    request: Request,
    status: Optional[AppointmentStatus] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_current_session),
) -> list[AppointmentResponse]:
    """List receiving appointments."""
    try:
        appointments = await agendai_repository.list_appointments(status=status, limit=limit)
        logger.info("agendai_appointments_listed", session_id=session.id, count=len(appointments))
        return [AppointmentResponse(**appointment.model_dump()) for appointment in appointments]
    except Exception:
        logger.exception("agendai_appointments_list_failed", session_id=session.id)
        raise HTTPException(status_code=500, detail="Erro ao listar agendamentos.")


@router.get("/appointments/{appointment_id}", response_model=AppointmentDetailResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["agendai"][0])
async def get_appointment_detail(
    request: Request,
    appointment_id: int,
    session: Session = Depends(get_current_session),
) -> AppointmentDetailResponse:
    """Return an appointment detail."""
    try:
        detail = await agendai_repository.get_appointment_detail(appointment_id)
        logger.info("agendai_appointment_detail_loaded", session_id=session.id, appointment_id=appointment_id)
        return _appointment_detail_response(detail)
    except HTTPException:
        raise
    except Exception:
        logger.exception("agendai_appointment_detail_failed", session_id=session.id, appointment_id=appointment_id)
        raise HTTPException(status_code=500, detail="Erro ao carregar detalhe do agendamento.")


@router.post("/drivers", response_model=DriverResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["agendai"][0])
async def create_driver(
    request: Request,
    body: DriverCreate,
    session: Session = Depends(get_current_session),
) -> DriverResponse:
    """Create a driver."""
    try:
        driver = await agendai_repository.create_driver(**body.model_dump())
        logger.info("agendai_driver_created_from_api", session_id=session.id, driver_id=driver.id)
        return DriverResponse(**driver.model_dump())
    except Exception:
        logger.exception("agendai_driver_create_failed", session_id=session.id)
        raise HTTPException(status_code=500, detail="Erro ao cadastrar motorista.")


@router.post("/vehicles", response_model=VehicleResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["agendai"][0])
async def create_vehicle(
    request: Request,
    body: VehicleCreate,
    session: Session = Depends(get_current_session),
) -> VehicleResponse:
    """Create a vehicle."""
    try:
        vehicle = await agendai_repository.create_vehicle(**body.model_dump())
        logger.info("agendai_vehicle_created_from_api", session_id=session.id, vehicle_id=vehicle.id)
        return VehicleResponse(**vehicle.model_dump())
    except HTTPException:
        raise
    except Exception:
        logger.exception("agendai_vehicle_create_failed", session_id=session.id)
        raise HTTPException(status_code=500, detail="Erro ao cadastrar veículo.")


@router.post("/suppliers", response_model=SupplierResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["agendai"][0])
async def create_supplier(
    request: Request,
    body: SupplierCreate,
    session: Session = Depends(get_current_session),
) -> SupplierResponse:
    """Create a supplier."""
    try:
        supplier = await agendai_repository.create_supplier(**body.model_dump())
        logger.info("agendai_supplier_created_from_api", session_id=session.id, supplier_id=supplier.id)
        return SupplierResponse(**supplier.model_dump())
    except Exception:
        logger.exception("agendai_supplier_create_failed", session_id=session.id)
        raise HTTPException(status_code=500, detail="Erro ao cadastrar fornecedor.")


@router.post("/appointments", response_model=AppointmentResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["agendai"][0])
async def create_appointment(
    request: Request,
    body: AppointmentCreate,
    session: Session = Depends(get_current_session),
) -> AppointmentResponse:
    """Create a receiving appointment."""
    try:
        appointment = await agendai_repository.create_appointment(
            **body.model_dump(),
            created_by_user_id=session.user_id,
        )
        logger.info("agendai_appointment_created_from_api", session_id=session.id, appointment_id=appointment.id)
        return AppointmentResponse(**appointment.model_dump())
    except HTTPException:
        raise
    except Exception:
        logger.exception("agendai_appointment_create_failed", session_id=session.id)
        raise HTTPException(status_code=500, detail="Erro ao criar agendamento.")


@router.post("/appointments/{appointment_id}/check-ins", response_model=CheckInResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["agendai"][0])
async def register_check_in(
    request: Request,
    appointment_id: int,
    body: CheckInCreate,
    session: Session = Depends(get_current_session),
) -> CheckInResponse:
    """Register a check-in for an appointment."""
    try:
        check_in = await agendai_repository.register_check_in(
            appointment_id=appointment_id,
            checked_in_at=body.checked_in_at,
            method=body.method,
            confirmed_by_user_id=session.user_id,
            notes=body.notes,
        )
        logger.info("agendai_check_in_created_from_api", session_id=session.id, check_in_id=check_in.id)
        return CheckInResponse(**check_in.model_dump())
    except HTTPException:
        raise
    except Exception:
        logger.exception("agendai_check_in_create_failed", session_id=session.id, appointment_id=appointment_id)
        raise HTTPException(status_code=500, detail="Erro ao registrar check-in.")


@router.post("/alerts/generate-late", response_model=LateAlertGenerationResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["agendai"][0])
async def generate_late_alerts(
    request: Request,
    session: Session = Depends(get_current_session),
) -> LateAlertGenerationResponse:
    """Generate alerts for appointments more than 10 minutes late."""
    try:
        alerts = await agendai_repository.create_late_alerts()
        logger.info("agendai_late_alerts_generated_from_api", session_id=session.id, count=len(alerts))
        return LateAlertGenerationResponse(created_alerts=[YardAlertResponse(**alert.model_dump()) for alert in alerts])
    except Exception:
        logger.exception("agendai_late_alert_generation_failed", session_id=session.id)
        raise HTTPException(status_code=500, detail="Erro ao gerar alertas de atraso.")


@router.get("/alerts", response_model=list[YardAlertResponse])
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["agendai"][0])
async def list_alerts(
    request: Request,
    status: Optional[AlertStatus] = Query(default=None),
    session: Session = Depends(get_current_session),
) -> list[YardAlertResponse]:
    """List yard alerts."""
    try:
        alerts = await agendai_repository.list_alerts(status=status)
        logger.info("agendai_alerts_listed", session_id=session.id, count=len(alerts))
        return [YardAlertResponse(**alert.model_dump()) for alert in alerts]
    except Exception:
        logger.exception("agendai_alerts_list_failed", session_id=session.id)
        raise HTTPException(status_code=500, detail="Erro ao listar alertas.")


@router.post("/alerts/{alert_id}/resolve", response_model=YardAlertResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["agendai"][0])
async def resolve_alert(
    request: Request,
    alert_id: int,
    session: Session = Depends(get_current_session),
) -> YardAlertResponse:
    """Resolve a yard alert."""
    try:
        alert = await agendai_repository.resolve_alert(alert_id=alert_id, user_id=session.user_id)
        logger.info("agendai_alert_resolved_from_api", session_id=session.id, alert_id=alert_id)
        return YardAlertResponse(**alert.model_dump())
    except HTTPException:
        raise
    except Exception:
        logger.exception("agendai_alert_resolve_failed", session_id=session.id, alert_id=alert_id)
        raise HTTPException(status_code=500, detail="Erro ao resolver alerta.")


@router.get("/business-rule-documents", response_model=list[BusinessRuleDocumentResponse])
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["agendai"][0])
async def list_business_rule_documents(
    request: Request,
    session: Session = Depends(get_current_session),
) -> list[BusinessRuleDocumentResponse]:
    """List business-rule document metadata. MinIO is stubbed in the MVP."""
    try:
        documents = await agendai_repository.list_business_rule_documents()
        logger.info("agendai_business_rule_documents_listed", session_id=session.id, count=len(documents))
        return [BusinessRuleDocumentResponse(**document.model_dump()) for document in documents]
    except Exception:
        logger.exception("agendai_business_rule_documents_list_failed", session_id=session.id)
        raise HTTPException(status_code=500, detail="Erro ao listar documentos de regras.")


def _appointment_detail_response(detail: dict[str, object]) -> AppointmentDetailResponse:
    """Convert repository detail payload into an API response."""
    return AppointmentDetailResponse(
        appointment=AppointmentResponse(**detail["appointment"].model_dump()),
        driver=DriverResponse(**detail["driver"].model_dump()),
        vehicle=VehicleResponse(**detail["vehicle"].model_dump()),
        supplier=SupplierResponse(**detail["supplier"].model_dump()),
        check_ins=[CheckInResponse(**check_in.model_dump()) for check_in in detail["check_ins"]],
        alerts=[YardAlertResponse(**alert.model_dump()) for alert in detail["alerts"]],
    )


@router.get("/integrations/status", response_model=IntegrationStatusResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["agendai"][0])
async def get_integration_status(
    request: Request,
    session: Session = Depends(get_current_session),
) -> IntegrationStatusResponse:
    """Return whether real external integrations are enabled."""
    logger.info("agendai_integration_status_loaded", session_id=session.id)
    return IntegrationStatusResponse(**integration_status())
