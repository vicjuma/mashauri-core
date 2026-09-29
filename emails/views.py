from .models import RecipientEmail, RecipientCategory
from mashauri.utils import send_mail
from mashauri.models import Dispatch
from datetime import timedelta
from django.utils.timezone import now

# Create your views here.
def email_recipients_escalation_matrix(group_name):
    return list(
        RecipientEmail.objects.filter(
            group__category=RecipientCategory.ESCALATION_MATRIX,
            group__name=group_name,
            group__is_active=True,
            is_active=True,
        ).values_list("email", flat=True)
    )


def send_sla_escalation_email(dispatch, sla_stage, recipients):
    subject = (
        f"SLA Escalation: {sla_stage} — "
        f"{dispatch.building_name}"
    )

    message = (
        f"Please note that the dispatch for "
        f"\"{dispatch.client_name}\" located at "
        f"\"{dispatch.building_name}\" has reached the "
        f"{sla_stage} escalation stage.\n\n"
        f"Dispatch ID: MSH-{str(dispatch.id).zfill(7)}\n"
        f"Building ID: {dispatch.building_id}\n"
        f"MSP: {dispatch.msp or 'N/A'}\n"
        f"FDP: {dispatch.fdp or 'N/A'}\n"
        f"Escalation Type: {dispatch.escalation_type}\n\n"
        f"Please take the necessary action.\n\n"
        f"Mashauri | Core."
    )

    send_mail(
        recipients=recipients,
        subject=subject,
        message=message
    )


def send_project_manager_sla_emails():
    recipients = (
        email_recipients_escalation_matrix("Project Manager")
        + email_recipients_escalation_matrix("Technical Project Manager")
    )

    dispatches = Dispatch.objects.filter(
        is_expired=True,
        pm_sla_email_sent=False,
        expired_at__lte=now() - timedelta(hours=24),
    )

    for dispatch in dispatches:
        send_sla_escalation_email(
            dispatch,
            "Project Manager / Technical Project Manager — 24 Hours",
            recipients
        )

        dispatch.pm_sla_email_sent = True
        dispatch.save(update_fields=["pm_sla_email_sent"])


def send_chief_operating_officer_sla_emails():
    recipients = email_recipients_escalation_matrix("Chief Operating Officer")

    dispatches = Dispatch.objects.filter(
        is_expired=True,
        coo_sla_email_sent=False,
        expired_at__lte=now() - timedelta(hours=30),
    )

    for dispatch in dispatches:
        send_sla_escalation_email(
            dispatch,
            "Chief Operating Officer — 30 Hours",
            recipients
        )

        dispatch.coo_sla_email_sent = True
        dispatch.save(update_fields=["coo_sla_email_sent"])


def send_chief_technical_officer_sla_emails():
    recipients = email_recipients_escalation_matrix("Chief Technical Officer")

    dispatches = Dispatch.objects.filter(
        is_expired=True,
        cto_sla_email_sent=False,
        expired_at__lte=now() - timedelta(hours=40),
    )

    for dispatch in dispatches:
        send_sla_escalation_email(
            dispatch,
            "Chief Technical Officer — 40 Hours",
            recipients
        )

        dispatch.cto_sla_email_sent = True
        dispatch.save(update_fields=["cto_sla_email_sent"])


def send_chief_executive_officer_sla_emails():
    recipients = email_recipients_escalation_matrix("Chief Executive Officer")

    dispatches = Dispatch.objects.filter(
        is_expired=True,
        ceo_sla_email_sent=False,
        expired_at__lte=now() - timedelta(hours=48),
    )

    for dispatch in dispatches:
        send_sla_escalation_email(
            dispatch,
            "Chief Executive Officer — 48 Hours",
            recipients
        )

        dispatch.ceo_sla_email_sent = True
        dispatch.save(update_fields=["ceo_sla_email_sent"])


def send_chief_executive_officer_sla_emails():
    recipients = email_recipients_escalation_matrix("Chief Executive Officer")

    dispatches = Dispatch.objects.filter(
        is_expired=True,
        ceo_sla_email_sent=False,
        expired_at__lte=now() - timedelta(hours=48),
    )

    for dispatch in dispatches:
        send_sla_escalation_email(
            dispatch,
            "Chief Executive Officer — 48 Hours",
            recipients
        )

        dispatch.ceo_sla_email_sent = True
        dispatch.save(update_fields=["ceo_sla_email_sent"])