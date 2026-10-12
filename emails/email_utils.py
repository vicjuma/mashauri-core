
from emails.email_normal import send_normal_dispatch_age_reminder
from emails.email_otb import send_otb_dispatch_age_reminder
from emails.email_test import send_test_dispatch_age_reminder
from .email_optimization import send_optimization_dispatch_age_reminder


def schedule_optimization_dispatch_age_reminders():
    recipient_groups = {
        5: ["vicjuma945@gmail.com"],  # Project Manager and Technical Project Manager
        6: ["vicjuma945@gmail.com"],  # Chief Operating Officer
        7: ["vicjuma945@gmail.com"],  # Chief Technical Officer
        8: ["vicjuma945@gmail.com"],  # Chief Executive Officer & Team Manager
        9: ["vicjuma945@gmail.com"],  # Senior Manager
        10: ["vicjuma945@gmail.com"], # HOD (SLA breached)
    }

    for reminder_day, recipients in recipient_groups.items():
        send_optimization_dispatch_age_reminder(
            reminder_day=reminder_day,
            subject=(
                f"Day {reminder_day} Optimization Dispatch SLA Reminder"
            ),
            recipients=recipients,
        )

def schedule_otb_dispatch_age_reminders():
    recipient_groups = {
        9: ["vicjuma945@gmail.com"],   # Project Manager and Technical Project Manager
        11: ["vicjuma945@gmail.com"],  # Chief Operating Officer
        12: ["vicjuma945@gmail.com"],  # Chief Technical Officer
        15: ["vicjuma945@gmail.com"],  # Chief Executive Officer and Team Manager
        18: ["vicjuma945@gmail.com"],  # Senior Manager
        21: ["vicjuma945@gmail.com"],  # Safaricom HOD (SLA breached)
    }

    for reminder_day, recipients in recipient_groups.items():
        send_otb_dispatch_age_reminder(
            reminder_day=reminder_day,
            subject=f"Day {reminder_day} OTB Dispatch SLA Reminder",
            recipients=recipients,
        )

def schedule_normal_dispatch_age_reminders():
    recipient_groups = {
        15: ["vicjuma945@gmail.com"],  # Project Manager and Technical Project Manager
        20: ["vicjuma945@gmail.com"],  # Chief Operating Officer
        25: ["vicjuma945@gmail.com"],  # Chief Technical Officer
        30: ["vicjuma945@gmail.com"],  # CEO and Team Manager
        36: ["vicjuma945@gmail.com"],  # Safaricom HOD (SLA breached)
        40: ["vicjuma945@gmail.com"],  # Senior Manager
    }

    for reminder_hours, recipients in recipient_groups.items():
        send_normal_dispatch_age_reminder(
            reminder_hours=reminder_hours,
            subject=(
                f"{reminder_hours}-Hour Core Provisioning "
                f"Dispatch SLA Reminder"
            ),
            recipients=recipients,
        )



def schedule_test_dispatch_age_reminders():
    recipient_groups = {
        1: ["vicjuma945@gmail.com"],  # Project Manager and Technical Project Manager
        2: ["vicjuma945@gmail.com"],  # Chief Operating Officer
        3: ["vicjuma945@gmail.com"],  # Chief Technical Officer
        4: ["vicjuma945@gmail.com"],  # Chief Executive Officer
        5: ["vicjuma945@gmail.com"],  # Safaricom HOD
    }

    for reminder_hours, recipients in recipient_groups.items():
        send_test_dispatch_age_reminder(
            reminder_hours=reminder_hours,
            subject=(
                f"{reminder_hours}-Hour Test Dispatch SLA Reminder"
            ),
            recipients=recipients,
        )