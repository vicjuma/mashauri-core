from mashauri.models import Dispatch
from .models import (
    RecipientCategory,
    MSPEscalationMatrix,
    MSPEscalationRole,
)
from mashauri.utils import (
    generate_pdf_mailed,
    save_contentfile_to_disk,
    send_mail,
)
from django.utils.timezone import now, localtime
from datetime import timedelta


def send_test_dispatch_age_reminder(
    reminder_hours,
    subject,
    recipient_group,
):
    current_time = now()
    current_date = localtime(current_time).date()

    target_time = current_time - timedelta(hours=reminder_hours)
    next_time = target_time + timedelta(hours=1)

    reminder_fields = {
        1: "pm_sla_email_sent_test",
        2: "coo_sla_email_sent_test",
        3: "cto_sla_email_sent_test",
        4: "ceo_sla_email_sent_test",
        5: "hod_sla_email_sent_test",
    }

    if reminder_hours not in reminder_fields:
        raise ValueError("Reminder hours must be 1, 2, 3, 4, or 5.")

    reminder_field = reminder_fields[reminder_hours]

    # 1. Get active emails configured directly on RecipientGroup.
    recipients = set(
        recipient_group.emails.filter(
            is_active=True,
        ).values_list("email", flat=True)
    )

    # 2. Map the reminder stage to escalation matrix roles.
    role_mapping = {
        1: [
            MSPEscalationRole.PROJECT_MANAGER,
            MSPEscalationRole.TECHNICAL_PROJECT_MANAGER,
        ],
        2: [
            MSPEscalationRole.CHIEF_OPERATING_OFFICER,
        ],
        3: [
            MSPEscalationRole.CHIEF_TECHNICAL_OFFICER,
        ],
        4: [
            MSPEscalationRole.CHIEF_EXECUTIVE_OFFICER,
        ],
        # HOD is not currently defined in MSPEscalationRole.
        5: [],
    }

    # 3. For MSP groups, add the appropriate escalation contacts.
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

    recipients = sorted(recipients)

    if not recipients:
        print(
            f"No active recipients for "
            f"{recipient_group.category} - "
            f"{recipient_group.name}."
        )
        return

    # 4. Map the recipient category to the Dispatch field.
    category_field = {
        RecipientCategory.MSP: "msp",
        RecipientCategory.FDP: "fdp",
        RecipientCategory.RP: "rp",
    }.get(recipient_group.category)

    if not category_field:
        raise ValueError(
            f"Unsupported recipient category: " f"{recipient_group.category}"
        )

    # 5. Select only this company's matching dispatches.
    dispatch_filters = {
        category_field: recipient_group.name,
    }

    dispatches = Dispatch.objects.filter(
        created_at__gte=target_time,
        created_at__lt=next_time,
        status="Progress",
        is_expired=False,
        sla_timer__gt=current_time,
        escalation_type__in=[
            "Optimization",
            "Proactive",
            "Reactive",
            "Interception",
            "Support",
        ],
        **dispatch_filters,
    ).filter(**{reminder_field: False})

    if not dispatches.exists():
        print(
            f"No matching test dispatches found for "
            f"{recipient_group.category} - "
            f"{recipient_group.name}, "
            f"hour {reminder_hours}."
        )
        return

    dispatch_count = dispatches.count()

    report_title = f"{reminder_hours}-Hour Test Dispatch SLA Reminder"

    report_pdf = generate_pdf_mailed(
        dispatches,
        report_title,
        report_title,
    )

    report_pdf_path = save_contentfile_to_disk(
        report_pdf,
        f"test_dispatch_report_"
        f"{recipient_group.category}_{recipient_group.name}_"
        f"hour_{reminder_hours}",
    )

    message = (
        f"Please find attached the test dispatch report.\n\n"
        f"Recipient group: {recipient_group.category} - "
        f"{recipient_group.name}\n"
        f"Report date: {current_date}\n"
        f"Reminder age: {reminder_hours} hours\n"
        f"Dispatch count: {dispatch_count}\n"
    )

    send_mail(
        recipients=recipients,
        subject=subject,
        message=message,
        attachment_path=[report_pdf_path],
    )

    # Mark only the dispatches in this report after sending succeeds.
    dispatches.update(**{reminder_field: True})

    print(
        f"Email sent to {len(recipients)} recipients for "
        f"{recipient_group.category} - {recipient_group.name}, "
        f"hour {reminder_hours}, covering "
        f"{dispatch_count} dispatches."
    )
    
# ================================ SAFARICOM TEAM ======================================


def send_test_dispatch_age_reminder_safaricom(
    reminder_day,
    subject,
    recipients,
):
    current_time = now()
    current_date = localtime(current_time).date()

    # Sample test reminders for Safaricom.
    reminder_fields = {
        1: "team_manager_sla_email_sent_test",  # Team Manager
        2: "senior_manager_sla_email_sent_test",  # Senior Manager
        3: "hod_sla_email_sent_test",  # Safaricom HOD
    }

    reminder_field = reminder_fields.get(reminder_day)

    if not reminder_field:
        raise ValueError("Test reminder hour must be 1, 2, or 3.")

    # Find dispatches created within the target hour window.
    target_time = current_time - timedelta(hours=reminder_day)
    next_time = target_time + timedelta(hours=1)

    dispatches = Dispatch.objects.filter(
        created_at__gte=target_time,
        created_at__lt=next_time,
        status="Progress",
        is_expired=False,
        sla_timer__gt=current_time,
        escalation_type__in=[
            "Optimization",
            "Proactive",
            "Reactive",
            "Interception",
            "Support",
            "OTB",
        ],
    ).filter(**{reminder_field: False})

    if not dispatches.exists():
        print(
            f"No dispatches found for the "
            f"{reminder_day}-hour test reminder on {current_date}."
        )
        return

    dispatch_count = dispatches.count()

    report_title = f"Day {reminder_day} Sample Dispatch SLA Reminder"

    report_pdf = generate_pdf_mailed(
        dispatches,
        report_title,
        report_title,
    )

    report_pdf_path = save_contentfile_to_disk(
        report_pdf,
        f"sample_dispatch_report_hour_{reminder_day}",
    )

    message = (
        f"Please find attached the sample dispatch report "
        f"for dispatches reaching {reminder_day} hour(s) since creation.\n\n"
        f"Report date: {current_date}\n"
        f"Dispatch count: {dispatch_count}\n"
    )

    recipients = sorted(
        {email.strip() for email in recipients if email and email.strip()}
    )

    if not recipients:
        print(f"No valid recipients for the " f"{reminder_day}-hour test reminder.")
        return

    email_sent = send_mail(
        recipients=recipients,
        subject=subject,
        message=message,
        attachment_path=[report_pdf_path],
    )

    # Update flags only if send_mail returns True.
    if not email_sent:
        print(
            f"Email failed for {subject}. "
            "Dispatch notification flags were not updated."
        )
        return

    dispatches.update(**{reminder_field: True})

    print(f"Email sent for {subject}, covering " f"{dispatch_count} dispatches.")


