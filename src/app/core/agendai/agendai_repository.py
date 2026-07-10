"""Repository for AgendAI yard-management operations."""

from datetime import UTC, datetime, timedelta
from typing import Optional

from fastapi import HTTPException
from sqlmodel import Session, select

from src.app.core.agendai.agendai_model import (
    AgendAIAppointment,
    AgendAIBusinessRuleDocument,
    AgendAICheckIn,
    AgendAIDriver,
    AgendAISupplier,
    AgendAIVehicle,
    AgendAIYardAlert,
    AlertSeverity,
    AlertStatus,
    AppointmentStatus,
    CheckInMethod,
)
from src.app.core.common.logging import logger


class AgendAIRepository:
    """Database operations for the AgendAI domain."""

    def __init__(self, session: Session):
        """Initialize repository with a SQLModel session."""
        self.session = session

    async def create_driver(
        self,
        name: str,
        cpf: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        company: Optional[str] = None,
        notes: str = "",
    ) -> AgendAIDriver:
        """Create a driver registration."""
        driver = AgendAIDriver(name=name, cpf=cpf, email=email, phone=phone, company=company, notes=notes)
        self.session.add(driver)
        self.session.commit()
        self.session.refresh(driver)
        logger.info("agendai_driver_created", driver_id=driver.id)
        return driver

    async def create_vehicle(
        self,
        driver_id: int,
        plate: str,
        model: Optional[str] = None,
        color: Optional[str] = None,
        year: Optional[int] = None,
    ) -> AgendAIVehicle:
        """Create a vehicle for an existing driver."""
        await self.get_driver(driver_id)
        vehicle = AgendAIVehicle(driver_id=driver_id, plate=plate, model=model, color=color, year=year)
        self.session.add(vehicle)
        self.session.commit()
        self.session.refresh(vehicle)
        logger.info("agendai_vehicle_created", vehicle_id=vehicle.id, driver_id=driver_id)
        return vehicle

    async def create_supplier(
        self,
        name: str,
        contact_email: Optional[str] = None,
        contact_phone: Optional[str] = None,
        authorized_email_domain: Optional[str] = None,
    ) -> AgendAISupplier:
        """Create a supplier."""
        supplier = AgendAISupplier(
            name=name,
            contact_email=contact_email,
            contact_phone=contact_phone,
            authorized_email_domain=authorized_email_domain,
        )
        self.session.add(supplier)
        self.session.commit()
        self.session.refresh(supplier)
        logger.info("agendai_supplier_created", supplier_id=supplier.id)
        return supplier

    async def create_appointment(
        self,
        driver_id: int,
        vehicle_id: int,
        supplier_id: int,
        scheduled_at: datetime,
        created_by_user_id: Optional[int],
        dock: Optional[str] = None,
        load_reference: Optional[str] = None,
        notes: str = "",
    ) -> AgendAIAppointment:
        """Create a receiving appointment."""
        await self.get_driver(driver_id)
        await self.get_vehicle(vehicle_id)
        await self.get_supplier(supplier_id)
        appointment = AgendAIAppointment(
            driver_id=driver_id,
            vehicle_id=vehicle_id,
            supplier_id=supplier_id,
            scheduled_at=_as_utc_naive(scheduled_at),
            dock=dock,
            load_reference=load_reference,
            notes=notes,
            created_by_user_id=created_by_user_id,
        )
        self.session.add(appointment)
        self.session.commit()
        self.session.refresh(appointment)
        logger.info("agendai_appointment_created", appointment_id=appointment.id)
        return appointment

    async def register_check_in(
        self,
        appointment_id: int,
        checked_in_at: Optional[datetime],
        method: CheckInMethod,
        confirmed_by_user_id: Optional[int],
        notes: str = "",
    ) -> AgendAICheckIn:
        """Register a check-in and update the appointment status."""
        appointment = await self.get_appointment(appointment_id)
        if appointment.status in {AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED}:
            raise HTTPException(status_code=409, detail="Agendamento não aceita novo check-in neste status.")

        check_in = AgendAICheckIn(
            appointment_id=appointment_id,
            checked_in_at=_as_utc_naive(checked_in_at or _utc_now_naive()),
            method=method,
            confirmed_by_user_id=confirmed_by_user_id,
            notes=notes,
        )
        appointment.status = AppointmentStatus.CHECKED_IN
        self.session.add(check_in)
        self.session.add(appointment)
        self.session.commit()
        self.session.refresh(check_in)
        logger.info("agendai_check_in_registered", appointment_id=appointment_id, check_in_id=check_in.id)
        return check_in

    async def create_late_alerts(self, now: Optional[datetime] = None) -> list[AgendAIYardAlert]:
        """Create alerts for appointments more than 10 minutes late without check-in."""
        reference_time = _as_utc_naive(now or _utc_now_naive())
        cutoff = reference_time - timedelta(minutes=10)
        statement = select(AgendAIAppointment).where(
            AgendAIAppointment.status == AppointmentStatus.PENDING,
            AgendAIAppointment.scheduled_at < cutoff,
        )
        appointments = self.session.exec(statement).all()
        created_alerts = []

        for appointment in appointments:
            check_in = self.session.exec(
                select(AgendAICheckIn).where(AgendAICheckIn.appointment_id == appointment.id)
            ).first()
            if check_in:
                continue

            existing_alert = self.session.exec(
                select(AgendAIYardAlert).where(
                    AgendAIYardAlert.appointment_id == appointment.id,
                    AgendAIYardAlert.alert_type == "late_check_in",
                    AgendAIYardAlert.status != AlertStatus.RESOLVED,
                )
            ).first()
            if existing_alert:
                continue

            alert = AgendAIYardAlert(
                appointment_id=appointment.id,
                alert_type="late_check_in",
                severity=AlertSeverity.WARNING,
                message="Motorista ultrapassou 10 minutos de atraso no check-in. Deseja chamar o próximo agendado?",
            )
            self.session.add(alert)
            created_alerts.append(alert)

        self.session.commit()
        for alert in created_alerts:
            self.session.refresh(alert)

        logger.info("agendai_late_alerts_created", count=len(created_alerts))
        return created_alerts

    async def resolve_alert(self, alert_id: int, user_id: Optional[int]) -> AgendAIYardAlert:
        """Resolve an open yard alert."""
        alert = await self.get_alert(alert_id)
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = _utc_now_naive()
        alert.resolved_by_user_id = user_id
        self.session.add(alert)
        self.session.commit()
        self.session.refresh(alert)
        logger.info("agendai_alert_resolved", alert_id=alert_id, user_id=user_id)
        return alert

    async def list_appointments(
        self,
        status: Optional[AppointmentStatus] = None,
        limit: int = 100,
    ) -> list[AgendAIAppointment]:
        """List receiving appointments."""
        statement = select(AgendAIAppointment).order_by(AgendAIAppointment.scheduled_at).limit(limit)
        if status is not None:
            statement = (
                select(AgendAIAppointment)
                .where(AgendAIAppointment.status == status)
                .order_by(AgendAIAppointment.scheduled_at)
                .limit(limit)
            )
        return self.session.exec(statement).all()

    async def list_alerts(self, status: Optional[AlertStatus] = None) -> list[AgendAIYardAlert]:
        """List yard alerts."""
        statement = select(AgendAIYardAlert).order_by(AgendAIYardAlert.created_at)
        if status is not None:
            statement = (
                select(AgendAIYardAlert)
                .where(AgendAIYardAlert.status == status)
                .order_by(AgendAIYardAlert.created_at)
            )
        return self.session.exec(statement).all()

    async def get_dashboard_summary(self) -> dict[str, int]:
        """Return operational counters for the top dashboard."""
        appointments = self.session.exec(select(AgendAIAppointment)).all()
        check_ins = self.session.exec(select(AgendAICheckIn)).all()
        cutoff = _utc_now_naive() - timedelta(minutes=10)
        late_count = 0

        for appointment in appointments:
            scheduled_at = _as_utc_naive(appointment.scheduled_at)
            if appointment.status != AppointmentStatus.PENDING or scheduled_at >= cutoff:
                continue
            has_check_in = any(check_in.appointment_id == appointment.id for check_in in check_ins)
            if not has_check_in:
                late_count += 1

        return {
            "pending_appointments": sum(1 for item in appointments if item.status == AppointmentStatus.PENDING),
            "completed_appointments": sum(1 for item in appointments if item.status == AppointmentStatus.COMPLETED),
            "check_ins": len(check_ins),
            "late_loads": late_count,
        }

    async def get_driver(self, driver_id: int) -> AgendAIDriver:
        """Get a driver by ID."""
        driver = self.session.get(AgendAIDriver, driver_id)
        if driver is None:
            raise HTTPException(status_code=404, detail="Motorista não encontrado.")
        return driver

    async def get_vehicle(self, vehicle_id: int) -> AgendAIVehicle:
        """Get a vehicle by ID."""
        vehicle = self.session.get(AgendAIVehicle, vehicle_id)
        if vehicle is None:
            raise HTTPException(status_code=404, detail="Veículo não encontrado.")
        return vehicle

    async def get_supplier(self, supplier_id: int) -> AgendAISupplier:
        """Get a supplier by ID."""
        supplier = self.session.get(AgendAISupplier, supplier_id)
        if supplier is None:
            raise HTTPException(status_code=404, detail="Fornecedor não encontrado.")
        return supplier

    async def get_appointment(self, appointment_id: int) -> AgendAIAppointment:
        """Get an appointment by ID."""
        appointment = self.session.get(AgendAIAppointment, appointment_id)
        if appointment is None:
            raise HTTPException(status_code=404, detail="Agendamento não encontrado.")
        return appointment

    async def get_alert(self, alert_id: int) -> AgendAIYardAlert:
        """Get a yard alert by ID."""
        alert = self.session.get(AgendAIYardAlert, alert_id)
        if alert is None:
            raise HTTPException(status_code=404, detail="Alerta não encontrado.")
        return alert

    async def get_appointment_detail(self, appointment_id: int) -> dict[str, object]:
        """Return an appointment with its related operational data."""
        appointment = await self.get_appointment(appointment_id)
        driver = await self.get_driver(appointment.driver_id)
        vehicle = await self.get_vehicle(appointment.vehicle_id)
        supplier = await self.get_supplier(appointment.supplier_id)
        check_ins = self.session.exec(
            select(AgendAICheckIn).where(AgendAICheckIn.appointment_id == appointment_id)
        ).all()
        alerts = self.session.exec(
            select(AgendAIYardAlert).where(AgendAIYardAlert.appointment_id == appointment_id)
        ).all()
        return {
            "appointment": appointment,
            "driver": driver,
            "vehicle": vehicle,
            "supplier": supplier,
            "check_ins": check_ins,
            "alerts": alerts,
        }

    async def list_business_rule_documents(self) -> list[AgendAIBusinessRuleDocument]:
        """List business-rule document metadata."""
        return self.session.exec(select(AgendAIBusinessRuleDocument).order_by(AgendAIBusinessRuleDocument.created_at)).all()


def _utc_now_naive() -> datetime:
    """Return a UTC timestamp without tzinfo for SQLModel DateTime columns."""
    return datetime.now(UTC).replace(tzinfo=None)


def _as_utc_naive(value: datetime) -> datetime:
    """Normalize aware or naive datetimes to UTC without tzinfo."""
    if value.tzinfo is None:
        return value
    return value.astimezone(UTC).replace(tzinfo=None)
