
from emails.email_normal import send_normal_dispatch_age_reminder, send_normal_dispatch_age_reminder_safaricom
from emails.email_otb import send_otb_dispatch_age_reminder, send_otb_dispatch_age_reminder_safaricom
from emails.email_test import send_test_dispatch_age_reminder, send_test_dispatch_age_reminder_safaricom
from .email_optimization import send_optimization_dispatch_age_reminder, send_optimization_dispatch_age_reminder_safaricom
from .models import (
    RecipientGroup,
    RecipientCategory,
    SafaricomEscalationEmail,
)

''' Optimization category '''
def schedule_optimization_dispatch_age_reminders():
    recipient_groups = RecipientGroup.objects.filter(
        category__in=[
            RecipientCategory.MSP,
            RecipientCategory.FDP,
            RecipientCategory.RP,
        ],
        is_active=True,
        emails__is_active=True,
    ).distinct()

    for reminder_day in (5, 6, 7, 8, 9, 10):
        for recipient_group in recipient_groups:
            send_optimization_dispatch_age_reminder(
                reminder_day=reminder_day,
                subject=(
                    f"Day {reminder_day} Optimization "
                    f"Dispatch SLA Reminder - "
                    f"{recipient_group.category} "
                    f"{recipient_group.name}"
                ),
                recipient_group=recipient_group,
            )

# ================= SAFARICOM TEAM =====================
def schedule_optimization_dispatch_age_reminders_safaricom():
    reminder_recipients = {
        8: list(
            SafaricomEscalationEmail.objects.filter(
                role="Team Manager",
                is_active=True,
            ).values_list("email", flat=True)
        ),
        9: list(
            SafaricomEscalationEmail.objects.filter(
                role="Senior Manager",
                is_active=True,
            ).values_list("email", flat=True)
        ),
        10: list(
            SafaricomEscalationEmail.objects.filter(
                role="HOD",
                is_active=True,
            ).values_list("email", flat=True)
        ),
    }

    for reminder_day, recipients in reminder_recipients.items():
        send_optimization_dispatch_age_reminder_safaricom(
            reminder_day=reminder_day,
            subject=(
                f"Day {reminder_day} Safaricom " f"Optimization Dispatch SLA Reminder"
            ),
            recipients=recipients,
        )
   
''' OTB category '''
def schedule_otb_dispatch_age_reminders():
    recipient_groups = RecipientGroup.objects.filter(
        category__in=[
            RecipientCategory.MSP,
            RecipientCategory.FDP,
            RecipientCategory.RP,
        ],
        is_active=True,
        emails__is_active=True,
    ).distinct()

    for reminder_day in (9, 11, 12, 15, 18, 21):
        for recipient_group in recipient_groups:
            send_otb_dispatch_age_reminder(
                reminder_day=reminder_day,
                subject=(
                    f"Day {reminder_day} OTB "
                    f"Dispatch SLA Reminder - "
                    f"{recipient_group.category} "
                    f"{recipient_group.name}"
                ),
                recipient_group=recipient_group,
            )

# ================= SAFARICOM TEAM =====================
def schedule_otb_dispatch_age_reminders_safaricom():
    reminder_recipients = {
        15: list(
            SafaricomEscalationEmail.objects.filter(
                role="Team Manager",
                is_active=True,
            ).values_list("email", flat=True)
        ),
        18: list(
            SafaricomEscalationEmail.objects.filter(
                role="Senior Manager",
                is_active=True,
            ).values_list("email", flat=True)
        ),
        21: list(
            SafaricomEscalationEmail.objects.filter(
                role="HOD",
                is_active=True,
            ).values_list("email", flat=True)
        ),
    }

    for reminder_day, recipients in reminder_recipients.items():
        send_otb_dispatch_age_reminder_safaricom(
            reminder_day=reminder_day,
            subject=(f"Day {reminder_day} Safaricom " f"OTB Dispatch SLA Reminder"),
            recipients=recipients,
        )

''' Other categories '''
def schedule_normal_dispatch_age_reminders():
    recipient_groups = RecipientGroup.objects.filter(
        category__in=[
            RecipientCategory.MSP,
            RecipientCategory.FDP,
            RecipientCategory.RP,
        ],
        is_active=True,
        emails__is_active=True,
    ).distinct()

    for reminder_hours in (15, 20, 25, 30, 36, 40):
        for recipient_group in recipient_groups:
            send_normal_dispatch_age_reminder(
                reminder_hours=reminder_hours,
                subject=(
                    f"{reminder_hours}-Hour Core Provisioning "
                    f"Dispatch SLA Reminder - "
                    f"{recipient_group.category} "
                    f"{recipient_group.name}"
                ),
                recipient_group=recipient_group,
            )

# ======================== SAFARICOM TEAM ======================
def schedule_normal_dispatch_age_reminders_safaricom():
    reminder_recipients = {
        30: list(
            SafaricomEscalationEmail.objects.filter(
                role="Team Manager",
                is_active=True,
            ).values_list("email", flat=True)
        ),
        36: list(
            SafaricomEscalationEmail.objects.filter(
                role="HOD",
                is_active=True,
            ).values_list("email", flat=True)
        ),
        40: list(
            SafaricomEscalationEmail.objects.filter(
                role="Senior Manager",
                is_active=True,
            ).values_list("email", flat=True)
        ),
    }

    for reminder_hours, recipients in reminder_recipients.items():
        send_normal_dispatch_age_reminder_safaricom(
            reminder_hours=reminder_hours,
            subject=(
                f"{reminder_hours}-Hour Safaricom "
                f"Core Provisioning Dispatch SLA Reminder"
            ),
            recipients=recipients,
        )


def schedule_test_dispatch_age_reminders():
    recipient_groups = RecipientGroup.objects.filter(
        category__in=[
            RecipientCategory.MSP,
            RecipientCategory.FDP,
            RecipientCategory.RP,
        ],
        is_active=True,
        emails__is_active=True,
    ).distinct()

    for reminder_hours in (1, 2, 3, 4, 5):
        for recipient_group in recipient_groups:
            send_test_dispatch_age_reminder(
                reminder_hours=reminder_hours,
                subject=(
                    f"{reminder_hours}-Hour Test Dispatch "
                    f"SLA Reminder - "
                    f"{recipient_group.category} "
                    f"{recipient_group.name}"
                ),
                recipient_group=recipient_group,
            )


# ======================== SAFARICOM TEAM ======================


def schedule_test_dispatch_age_reminders_safaricom():
    recipient_groups = {
        1: list(
            SafaricomEscalationEmail.objects.filter(
                role="Team Manager",
                is_active=True,
            ).values_list("email", flat=True)
        ),
        2: list(
            SafaricomEscalationEmail.objects.filter(
                role="Senior Manager",
                is_active=True,
            ).values_list("email", flat=True)
        ),
        3: list(
            SafaricomEscalationEmail.objects.filter(
                role="HOD",
                is_active=True,
            ).values_list("email", flat=True)
        ),
    }

    for reminder_hours, recipients in recipient_groups.items():
        send_test_dispatch_age_reminder_safaricom(
            reminder_day=reminder_hours,
            subject=(f"{reminder_hours}-Hour Sample Dispatch " f"SLA Reminder"),
            recipients=recipients,
        )



