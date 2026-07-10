"""Safe integration stubs for AgendAI external services."""

from dataclasses import dataclass

from src.app.core.common.config import settings
from src.app.core.common.logging import logger


@dataclass(frozen=True)
class StubResult:
    """Result returned by a disabled external integration."""

    executed: bool
    provider: str
    message: str


class EmailConfirmationStub:
    """Gmail/MCP confirmation adapter disabled by default in the MVP."""

    async def send_confirmation(self, recipient: str, subject: str, body: str) -> StubResult:
        """Return a safe result without sending an e-mail."""
        logger.info(
            "agendai_email_confirmation_stubbed",
            recipient_domain=recipient.split("@")[-1] if "@" in recipient else "",
            subject_length=len(subject),
            body_length=len(body),
        )
        return StubResult(
            executed=False,
            provider="gmail",
            message="Envio de e-mail desabilitado no MVP.",
        )


class WhatsAppReminderStub:
    """WhatsApp reminder adapter disabled by default in the MVP."""

    async def send_arrival_reminder(self, phone: str, message: str) -> StubResult:
        """Return a safe result without sending a WhatsApp message."""
        logger.info(
            "agendai_whatsapp_reminder_stubbed",
            phone_last_digits=phone[-4:] if len(phone) >= 4 else "",
            message_length=len(message),
        )
        return StubResult(
            executed=False,
            provider="whatsapp",
            message="Envio de WhatsApp desabilitado no MVP.",
        )


class BusinessRuleStorageStub:
    """MinIO business-rule document adapter disabled by default in the MVP."""

    async def list_documents(self) -> StubResult:
        """Return a safe result without reading a bucket."""
        logger.info("agendai_minio_storage_stubbed")
        return StubResult(
            executed=False,
            provider="minio",
            message="Leitura de documentos MinIO desabilitada no MVP.",
        )


def integration_status() -> dict[str, bool]:
    """Return whether real integrations are enabled by configuration."""
    return {
        "gmail_enabled": settings.AGENDAI_ENABLE_REAL_EMAIL,
        "whatsapp_enabled": settings.AGENDAI_ENABLE_REAL_WHATSAPP,
        "minio_enabled": settings.AGENDAI_ENABLE_REAL_MINIO,
    }
