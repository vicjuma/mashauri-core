from emails.models import MSPEscalationMatrix, MSPEscalationRole, RecipientCategory
from mashauri.models import Dispatch
from mashauri.utils import generate_pdf_mailed, save_contentfile_to_disk, send_mail
from django.utils.timezone import now, localtime
from datetime import timedelta


def send_otb_dispatch_age_reminder(
    reminder_day,
    subject,
    recipient_group,
):
    current_time = now()
    current_date = localtime(current_time).date()

    reminder_fields = {
        9: "pm_sla_email_sent_otb",
        11: "coo_sla_email_sent_otb",
        12: "cto_sla_email_sent_otb",
        15: "ceo_sla_email_sent_otb",
        # cc
        18: "senior_manager_sla_email_sent_otb_cc",
        21: "hod_sla_email_sent_otb_cc",
    }

    reminder_field = reminder_fields.get(reminder_day)

    if not reminder_field:
        raise ValueError("Reminder day must be 9, 11, 12, 15, 18, or 21")

    role_mapping = {
        9: [
            MSPEscalationRole.PROJECT_MANAGER,
            MSPEscalationRole.TECHNICAL_PROJECT_MANAGER,
        ],
        11: [
            MSPEscalationRole.CHIEF_OPERATING_OFFICER,
        ],
        12: [
            MSPEscalationRole.CHIEF_TECHNICAL_OFFICER,
        ],
        15: [
            MSPEscalationRole.CHIEF_EXECUTIVE_OFFICER,
        ],
        18: [  
            # Send to all escalation roles
            MSPEscalationRole.PROJECT_MANAGER,
            MSPEscalationRole.TECHNICAL_PROJECT_MANAGER,
            MSPEscalationRole.CHIEF_OPERATING_OFFICER,
            MSPEscalationRole.CHIEF_TECHNICAL_OFFICER,
            MSPEscalationRole.CHIEF_EXECUTIVE_OFFICER,
        ],
        21: [ 
            # Send to all escalation roles
            MSPEscalationRole.PROJECT_MANAGER,
            MSPEscalationRole.TECHNICAL_PROJECT_MANAGER,
            MSPEscalationRole.CHIEF_OPERATING_OFFICER,
            MSPEscalationRole.CHIEF_TECHNICAL_OFFICER,
            MSPEscalationRole.CHIEF_EXECUTIVE_OFFICER,
        ],
    }

    # Get active recipients configured on the recipient group.
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

    # Map recipient category to the Dispatch model field.
    category_field = {
        RecipientCategory.MSP: "msp",
        RecipientCategory.FDP: "fdp",
        RecipientCategory.RP: "rp",
    }.get(recipient_group.category)

    if not category_field:
        raise ValueError(
            f"Unsupported recipient category: " f"{recipient_group.category}"
        )

    
    next_time = current_time - timedelta(days=reminder_day)
    target_time = next_time - timedelta(days=1)

    dispatches = Dispatch.objects.filter(
        created_at__gte=target_time,
        created_at__lt=next_time,
        status="Progress",
        escalation_type="OTB",
        **{category_field: recipient_group.name},
    ).filter(**{reminder_field: False})


    if not dispatches.exists():
        print(
            f"No OTB dispatches found for "
            f"{recipient_group.category} - "
            f"{recipient_group.name}, "
            f"day {reminder_day}."
        )
        return

    dispatch_count = dispatches.count()

    report_title = f"Day {reminder_day} OTB Dispatch SLA Reminder"

    report_pdf = generate_pdf_mailed(
        dispatches,
        report_title,
        report_title,
    )

    report_pdf_path = save_contentfile_to_disk(
        report_pdf,
        f"otb_dispatch_report_"
        f"{recipient_group.category}_"
        f"{recipient_group.name}_"
        f"day_{reminder_day}",
    )

    message = (
        f"Please find attached the OTB dispatch report.\n\n"
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

    if not email_sent:
        print(f"Email failed for {subject}. " "Notification flags were not updated.")
        return

    dispatches.update(**{reminder_field: True})

    print(
        f"OTB email sent to {len(recipients)} recipients for "
        f"{recipient_group.category} - "
        f"{recipient_group.name}, day {reminder_day}, "
        f"covering {dispatch_count} dispatches."
    )
    
# ================ SAFARICOM TEAM ======================
def send_otb_dispatch_age_reminder_safaricom(
    reminder_day,
    subject,
    recipients,
):
    current_time = now()
    current_date = localtime(current_time).date()

    reminder_fields = {
        15: "team_manager_sla_email_sent_otb",
        18: "senior_manager_sla_email_sent_otb",
        21: "hod_sla_email_sent_otb",
    }

    reminder_field = reminder_fields.get(reminder_day)

    if not reminder_field:
        raise ValueError("Safaricom OTB reminder day must be 15, 18, or 21.")

    
    next_time = current_time - timedelta(days=reminder_day)
    target_time = next_time - timedelta(days=1)

    dispatches = Dispatch.objects.filter(
        created_at__gte=target_time,
        created_at__lt=next_time,
        status="Progress",
        escalation_type="OTB",
    ).filter(**{reminder_field: False})


    if not dispatches.exists():
        print(
            f"No OTB dispatches found for the Safaricom "
            f"day-{reminder_day} reminder on {current_date}."
        )
        return

    recipients = sorted(
        {email.strip() for email in recipients if email and email.strip()}
    )

    if not recipients:
        print(
            f"No valid recipients for the Safaricom "
            f"day-{reminder_day} OTB reminder."
        )
        return

    dispatch_count = dispatches.count()

    report_title = f"Day {reminder_day} Safaricom OTB " f"Dispatch SLA Reminder"

    report_pdf = generate_pdf_mailed(
        dispatches,
        report_title,
        report_title,
    )

    report_pdf_path = save_contentfile_to_disk(
        report_pdf,
        f"safaricom_otb_dispatch_report_day_{reminder_day}",
    )

    message = (
        f"Please find attached the Safaricom OTB dispatch report.\n\n"
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
        f"Safaricom OTB email sent for {subject}, "
        f"covering {dispatch_count} dispatches."
    )