
from emails.models import MSPEscalationMatrix, MSPEscalationRole, RecipientCategory
from mashauri.models import Dispatch
from mashauri.utils import generate_pdf_mailed, save_contentfile_to_disk, send_mail
from django.utils.timezone import now, localtime
from datetime import timedelta


def send_optimization_dispatch_age_reminder(
    reminder_day,
    subject,
    recipient_group,
):
    current_time = now()
    current_date = localtime(current_time).date()

    reminder_fields = {
        5: "pm_sla_email_sent_optimization",
        6: "coo_sla_email_sent_optimization",
        7: "cto_sla_email_sent_optimization",
        8: "ceo_sla_email_sent_optimization",
        # cc
        9: "senior_manager_sla_email_sent_optimization_cc",
        10: "hod_sla_email_sent_optimization_cc",
    }

    reminder_field = reminder_fields.get(reminder_day)

    if not reminder_field:
        raise ValueError("Reminder day must be 5, 6, 7, 8, 9, or 10")

    # Map each reminder day to its escalation roles.
    role_mapping = {
        5: [
            MSPEscalationRole.PROJECT_MANAGER,
            MSPEscalationRole.TECHNICAL_PROJECT_MANAGER,
        ],
        6: [
            MSPEscalationRole.CHIEF_OPERATING_OFFICER,
        ],
        7: [
            MSPEscalationRole.CHIEF_TECHNICAL_OFFICER,
        ],
        8: [
            MSPEscalationRole.CHIEF_EXECUTIVE_OFFICER,
        ],
        9: [  
            # Send to all escalation roles
            MSPEscalationRole.PROJECT_MANAGER,
            MSPEscalationRole.TECHNICAL_PROJECT_MANAGER,
            MSPEscalationRole.CHIEF_OPERATING_OFFICER,
            MSPEscalationRole.CHIEF_TECHNICAL_OFFICER,
            MSPEscalationRole.CHIEF_EXECUTIVE_OFFICER,
        ],
        10: [ 
            # Send to all escalation roles
            MSPEscalationRole.PROJECT_MANAGER,
            MSPEscalationRole.TECHNICAL_PROJECT_MANAGER,
            MSPEscalationRole.CHIEF_OPERATING_OFFICER,
            MSPEscalationRole.CHIEF_TECHNICAL_OFFICER,
            MSPEscalationRole.CHIEF_EXECUTIVE_OFFICER,
        ],
    }

    # Collect active recipients configured on the group.
    recipients = set(
        recipient_group.emails.filter(
            is_active=True,
        ).values_list("email", flat=True)
    )

    # Add the relevant escalation contacts for MSP groups.
    if recipient_group.category == RecipientCategory.MSP:
        matrix = MSPEscalationMatrix.objects.filter(
            msp=recipient_group.name,
            is_active=True,
        ).first()

        if matrix:
            escalation_emails = matrix.emails.filter(
                is_active=True,
                role__in=role_mapping[reminder_day],
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

    # Map the recipient category to its Dispatch field.
    category_field = {
        RecipientCategory.MSP: "msp",
        RecipientCategory.FDP: "fdp",
        RecipientCategory.RP: "rp",
    }.get(recipient_group.category)

    if not category_field:
        raise ValueError(
            f"Unsupported recipient category: " f"{recipient_group.category}"
        )

    # Select dispatches created on the target calendar date.
    target_date = current_date - timedelta(days=reminder_day)

    dispatches = Dispatch.objects.filter(
        created_at__date=target_date,
        status="Progress",
        is_expired=False,
        sla_timer__gt=current_time,
        escalation_type="Optimization",
        **{category_field: recipient_group.name},
    ).filter(**{reminder_field: False})

    if not dispatches.exists():
        print(
            f"No Optimization dispatches found for "
            f"{recipient_group.category} - "
            f"{recipient_group.name}, "
            f"day {reminder_day}."
        )
        return

    dispatch_count = dispatches.count()

    report_title = f"Day {reminder_day} Optimization " f"Dispatch SLA Reminder"

    report_pdf = generate_pdf_mailed(
        dispatches,
        report_title,
        report_title,
    )

    report_pdf_path = save_contentfile_to_disk(
        report_pdf,
        f"optimization_dispatch_report_"
        f"{recipient_group.category}_"
        f"{recipient_group.name}_"
        f"day_{reminder_day}",
    )

    message = (
        f"Please find attached the Optimization dispatch report.\n\n"
        f"Recipient group: {recipient_group.category} - "
        f"{recipient_group.name}\n"
        f"Report date: {current_date}\n"
        f"Reminder age: {reminder_day} days\n"
        f"Dispatch count: {dispatch_count}\n"
    )

    email_sent = send_mail(
        recipients=recipients,
        subject=subject,
        message=message,
        attachment_path=[report_pdf_path],
    )

    # Update notification flags only after successful delivery.
    if not email_sent:
        print(f"Email failed for {subject}. " "Notification flags were not updated.")
        return

    dispatches.update(**{reminder_field: True})

    print(
        f"Email sent to {len(recipients)} recipients for "
        f"{recipient_group.category} - "
        f"{recipient_group.name}, day {reminder_day}, "
        f"covering {dispatch_count} dispatches."
    )


# ================ SAFARICOM TEAM ======================
def send_optimization_dispatch_age_reminder_safaricom(
    reminder_day,
    subject,
    recipients,
):
    current_time = now()
    current_date = localtime(current_time).date()

    reminder_fields = {
        8: "team_manager_sla_email_sent_optimization",
        9: "senior_manager_sla_email_sent_optimization",
        10: "hod_sla_email_sent_optimization",
    }

    reminder_field = reminder_fields.get(reminder_day)

    if not reminder_field:
        raise ValueError("Safaricom reminder day must be 8, 9, or 10.")

    target_date = current_date - timedelta(days=reminder_day)

    dispatch_filters = {
        "created_at__date": target_date,
        "status": "Progress",
        "is_expired": False,
        "escalation_type": "Optimization",
    }

    # Days 8 and 9: SLA is still running.
    # Day 10: SLA has been breached.
    if reminder_day == 10:
        dispatch_filters["sla_timer__lte"] = current_time
    else:
        dispatch_filters["sla_timer__gt"] = current_time

    dispatches = Dispatch.objects.filter(
        **dispatch_filters,
    ).filter(**{reminder_field: False})

    if not dispatches.exists():
        print(
            f"No Optimization dispatches found for "
            f"the Safaricom day-{reminder_day} reminder "
            f"on {current_date}."
        )
        return

    recipients = sorted(
        {email.strip() for email in recipients if email and email.strip()}
    )

    if not recipients:
        print(f"No valid recipients for the Safaricom " f"day-{reminder_day} reminder.")
        return

    dispatch_count = dispatches.count()

    report_title = (
        f"Day {reminder_day} Safaricom Optimization " f"Dispatch SLA Reminder"
    )

    report_pdf = generate_pdf_mailed(
        dispatches,
        report_title,
        report_title,
    )

    report_pdf_path = save_contentfile_to_disk(
        report_pdf,
        f"safaricom_optimization_dispatch_report_" f"day_{reminder_day}",
    )

    message = (
        f"Please find attached the Safaricom Optimization "
        f"dispatch report.\n\n"
        f"Team: Safaricom\n"
        f"Report date: {current_date}\n"
        f"Reminder age: {reminder_day} days\n"
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