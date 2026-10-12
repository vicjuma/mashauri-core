from mashauri.models import Dispatch
from mashauri.utils import generate_pdf_mailed, save_contentfile_to_disk, send_mail
from django.utils.timezone import now, localtime
from datetime import timedelta


def send_test_dispatch_age_reminder(
    reminder_hours,
    subject,
    recipients,
):
    current_time = now()
    current_date = localtime(current_time).date()

    # Find dispatches by age in hours.
    target_time = current_time - timedelta(hours=reminder_hours)
    next_time = target_time + timedelta(hours=1)

    # Testing reminders: 1, 2, 3, 4, and 5 hours
    reminder_fields = {
        1: "pm_sla_email_sent_test",              # Project Manager and Technical Project Manager
        2: "coo_sla_email_sent_test",             # Chief Operating Officer
        3: "cto_sla_email_sent_test",             # Chief Technical Officer
        4: "ceo_sla_email_sent_test",             # Chief Executive Officer
        5: "hod_sla_email_sent_test",             # Safaricom HOD
    }

    reminder_field = reminder_fields.get(reminder_hours)

    if not reminder_field:
        raise ValueError(
            "Reminder hours must be 1, 2, 3, 4, or 5."
        )

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
    ).filter(**{reminder_field: False})

    if not dispatches.exists():
        print(
            f"No test dispatches found for the "
            f"{reminder_hours}-hour reminder on {current_date}."
        )
        return

    dispatch_count = dispatches.count()

    report_title = (
        f"{reminder_hours}-Hour Test Dispatch SLA Reminder"
    )

    report_pdf = generate_pdf_mailed(
        dispatches,
        report_title,
        report_title,
    )

    report_pdf_path = save_contentfile_to_disk(
        report_pdf,
        f"test_dispatch_report_hour_{reminder_hours}",
    )

    message = (
        f"Please find attached the test dispatch report "
        f"for dispatches reaching {reminder_hours} hours since creation.\n\n"
        f"Report date: {current_date}\n"
        f"Dispatch count: {dispatch_count}\n"
    )

    send_mail(
        recipients=recipients,
        subject=subject,
        message=message,
        attachment_path=[report_pdf_path],
    )

    # Mark dispatches as notified only after email sending succeeds.
    dispatches.update(**{reminder_field: True})

    print(
        f"Email sent for {subject}, covering "
        f"{dispatch_count} test dispatches."
    )