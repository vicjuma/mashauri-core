from emails.models import MSPEscalationMatrix, MSPEscalationRole, RecipientCategory
from mashauri.models import Dispatch
from mashauri.utils import generate_pdf_mailed, save_contentfile_to_disk, send_mail
from django.utils.timezone import now, localtime
from datetime import timedelta


def send_normal_dispatch_age_reminder(
    reminder_hours,
    subject,
    recipient_group,
):
    current_time = now()
    current_date = localtime(current_time).date()

    reminder_fields = {
        15: "pm_sla_email_sent_normal",
        20: "coo_sla_email_sent_normal",
        25: "cto_sla_email_sent_normal",
        30: "ceo_sla_email_sent_normal",
        # cc
        36: "hod_sla_email_sent_normal_cc",
        40: "senior_manager_sla_email_sent_normal_cc",
    }

    reminder_field = reminder_fields.get(reminder_hours)

    if not reminder_field:
        raise ValueError("Reminder hours must be 15, 20, 25, 30, 36 or 40.")

    role_mapping = {
        1: [
            MSPEscalationRole.PROJECT_MANAGER,
            MSPEscalationRole.TECHNICAL_PROJECT_MANAGER,
        ],
        15: [
            MSPEscalationRole.PROJECT_MANAGER,
            MSPEscalationRole.TECHNICAL_PROJECT_MANAGER,
        ],
        20: [
            MSPEscalationRole.CHIEF_OPERATING_OFFICER,
        ],
        25: [
            MSPEscalationRole.CHIEF_TECHNICAL_OFFICER,
        ],
        30: [
            MSPEscalationRole.CHIEF_EXECUTIVE_OFFICER,
        ],
        36: [
            # Send to all escalation roles
                MSPEscalationRole.PROJECT_MANAGER,
                MSPEscalationRole.TECHNICAL_PROJECT_MANAGER,
                MSPEscalationRole.CHIEF_OPERATING_OFFICER,
                MSPEscalationRole.CHIEF_TECHNICAL_OFFICER,
                MSPEscalationRole.CHIEF_EXECUTIVE_OFFICER,
            ],
        40: [  # Send to all escalation roles
            MSPEscalationRole.PROJECT_MANAGER,
            MSPEscalationRole.TECHNICAL_PROJECT_MANAGER,
            MSPEscalationRole.CHIEF_OPERATING_OFFICER,
            MSPEscalationRole.CHIEF_TECHNICAL_OFFICER,
            MSPEscalationRole.CHIEF_EXECUTIVE_OFFICER,
        ],
    }

    # Collect active recipient-group email addresses.
    recipients = set(
        recipient_group.emails.filter(
            is_active=True,
        ).values_list("email", flat=True)
    )

    # Add the appropriate escalation contacts for MSP groups.
    if recipient_group.category == RecipientCategory.MSP:
        matrix = MSPEscalationMatrix.objects.filter(
            msp=recipient_group.name,
            is_active=True,
        ).first()

        if matrix:
            escalation_emails = matrix.emails.filter(
                is_active=True,
                role__in=role_mapping[reminder_hours],
            ).values_list("email", flat=True)

            recipients.update(escalation_emails)

    recipients = sorted(
        {email.strip() for email in recipients if email and email.strip()}
    )

    if not recipients:
        print(
            f"No active recipients for "
            f"{recipient_group.category} - "
            f"{recipient_group.name}."
        )
        return

    # Map the recipient category to the Dispatch field.
    category_field = {
        RecipientCategory.MSP: "msp",
        RecipientCategory.FDP: "fdp",
        RecipientCategory.RP: "rp",
    }.get(recipient_group.category)

    if not category_field:
        raise ValueError(
            f"Unsupported recipient category: " f"{recipient_group.category}"
        )

    # Select dispatches within the target one-hour age window.
    target_time = current_time - timedelta(hours=reminder_hours)
    next_time = target_time + timedelta(hours=1)

    dispatches = Dispatch.objects.filter(
        created_at__gte=target_time,
        created_at__lt=next_time,
        status="Progress",
        is_expired=False,
        sla_timer__gt=current_time,
        escalation_type__in=[
            "Proactive",
            "Reactive",
            "Interception",
            "Support",
        ],
        **{category_field: recipient_group.name},
    ).filter(**{reminder_field: False})

    if not dispatches.exists():
        print(
            f"No Core Provisioning dispatches found for "
            f"{recipient_group.category} - "
            f"{recipient_group.name}, "
            f"hour {reminder_hours}, on {current_date}."
        )
        return

    dispatch_count = dispatches.count()

    report_title = f"{reminder_hours}-Hour Core Provisioning " f"Dispatch SLA Reminder"

    report_pdf = generate_pdf_mailed(
        dispatches,
        report_title,
        report_title,
    )

    report_pdf_path = save_contentfile_to_disk(
        report_pdf,
        f"normal_dispatch_report_"
        f"{recipient_group.category}_"
        f"{recipient_group.name}_"
        f"hour_{reminder_hours}",
    )

    message = (
        f"Please find attached the Core Provisioning "
        f"dispatch report.\n\n"
        f"Recipient group: {recipient_group.category} - "
        f"{recipient_group.name}\n"
        f"Report date: {current_date}\n"
        f"Reminder age: {reminder_hours} hours\n"
        f"Dispatch count: {dispatch_count}\n"
    )

    email_sent = send_mail(
        recipients=recipients,
        subject=subject,
        message=message,
        attachment_path=[report_pdf_path],
    )

    if not email_sent:
        print(f"Email failed for {subject}. " "Notification flags were not updated.")
        return

    dispatches.update(**{reminder_field: True})

    print(
        f"Email sent to {len(recipients)} recipients for "
        f"{recipient_group.category} - "
        f"{recipient_group.name}, hour {reminder_hours}, "
        f"covering {dispatch_count} dispatches."
    )

# ================ SAFARICOM TEAM ======================
def send_normal_dispatch_age_reminder_safaricom(
    reminder_hours,
    subject,
    recipients,
):
    current_time = now()
    current_date = localtime(current_time).date()

    reminder_fields = {
        30: "team_manager_sla_email_sent_normal",
        36: "hod_sla_email_sent_normal",
        40: "senior_manager_sla_email_sent_normal",
    }

    reminder_field = reminder_fields.get(reminder_hours)

    if not reminder_field:
        raise ValueError("Safaricom reminder hours must be 30, 36, or 40.")

    # Find dispatches within the target one-hour age window.
    target_time = current_time - timedelta(hours=reminder_hours)
    next_time = target_time + timedelta(hours=1)

    dispatch_filters = {
        "created_at__gte": target_time,
        "created_at__lt": next_time,
        "status": "Progress",
        "is_expired": False,
        "escalation_type__in": [
            "Proactive",
            "Reactive",
            "Interception",
            "Support",
        ],
    }

    # Team Manager: before SLA breach.
    # HOD and Senior Manager: after the 36-hour SLA deadline.
    if reminder_hours == 30:
        dispatch_filters["sla_timer__gt"] = current_time
    else:
        dispatch_filters["sla_timer__lte"] = current_time

    dispatches = Dispatch.objects.filter(
        **dispatch_filters,
    ).filter(**{reminder_field: False})

    if not dispatches.exists():
        print(
            f"No Core Provisioning dispatches found for "
            f"the Safaricom {reminder_hours}-hour reminder "
            f"on {current_date}."
        )
        return

    recipients = sorted(
        {email.strip() for email in recipients if email and email.strip()}
    )

    if not recipients:
        print(
            f"No valid recipients for the Safaricom " f"{reminder_hours}-hour reminder."
        )
        return

    dispatch_count = dispatches.count()

    report_title = (
        f"{reminder_hours}-Hour Safaricom " f"Core Provisioning Dispatch SLA Reminder"
    )

    report_pdf = generate_pdf_mailed(
        dispatches,
        report_title,
        report_title,
    )

    report_pdf_path = save_contentfile_to_disk(
        report_pdf,
        f"safaricom_normal_dispatch_report_" f"hour_{reminder_hours}",
    )

    message = (
        f"Please find attached the Safaricom "
        f"Core Provisioning dispatch report.\n\n"
        f"Team: Safaricom\n"
        f"Report date: {current_date}\n"
        f"Reminder age: {reminder_hours} hours\n"
        f"Dispatch count: {dispatch_count}\n"
    )

    email_sent = send_mail(
        recipients=recipients,
        subject=subject,
        message=message,
        attachment_path=[report_pdf_path],
    )

    if not email_sent:
        print(f"Email failed for {subject}. " "Notification flags were not updated.")
        return

    dispatches.update(**{reminder_field: True})

    print(
        f"Safaricom email sent for {subject}, " f"covering {dispatch_count} dispatches."
    )
