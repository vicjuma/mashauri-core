from celery import shared_task

from emails.email_utils import schedule_normal_dispatch_age_reminders, schedule_normal_dispatch_age_reminders_safaricom, schedule_optimization_dispatch_age_reminders, schedule_optimization_dispatch_age_reminders_safaricom, schedule_otb_dispatch_age_reminders, schedule_otb_dispatch_age_reminders_safaricom, schedule_test_dispatch_age_reminders, schedule_test_dispatch_age_reminders_safaricom
from .utils import schedule_nine_am_emails, schedule_twelve_noon_emails, \
    schedule_four_pm_emails
from mashauri.models import Dispatch
from django.utils.timezone import now


@shared_task
def nine_am():
    # Import and call your Django function here
    schedule_nine_am_emails()
    print("Running my scheduled function!")


@shared_task
def twelve_noon():
    # Import and call your Django function here
    schedule_twelve_noon_emails()
    print("Running my scheduled function!")


@shared_task
def four_pm():
    # Import and call your Django function here
    schedule_four_pm_emails()
    print("Running my scheduled function!")


@shared_task
def update_expired_dispatches():
    expired_dispatches = Dispatch.objects.filter(
        is_expired=False,
        sla_timer__lte=now())
    count = expired_dispatches.update(
        is_expired=True,
        expired_at=now())
    return f'{count} dispatches marked as expired.'

# ======================== OPTIMIZATION TASKS ========================


@shared_task
def dispatch_optimization_age_reminders():
    schedule_optimization_dispatch_age_reminders()
    print("Running Optimization dispatch reminders: days 5, 6, 7, 8.")


@shared_task
def dispatch_optimization_age_reminders_safaricom():
    schedule_optimization_dispatch_age_reminders_safaricom()
    print("Running Safaricom Optimization reminders: days 8, 9, 10.")


# ======================== OTB TASKS ========================


@shared_task
def dispatch_otb_age_reminders():
    schedule_otb_dispatch_age_reminders()
    print("Running OTB dispatch reminders: days 9, 11, 12, 15.")


@shared_task
def dispatch_otb_age_reminders_safaricom():
    schedule_otb_dispatch_age_reminders_safaricom()
    print("Running Safaricom OTB reminders: days 15, 18, 21.")


# ======================== NORMAL / CORE PROVISIONING TASKS ========================


@shared_task
def dispatch_normal_age_reminders():
    schedule_normal_dispatch_age_reminders()
    print("Running Core Provisioning reminders: hours 15, 20, 25, 30.")


@shared_task
def dispatch_normal_age_reminders_safaricom():
    schedule_normal_dispatch_age_reminders_safaricom()
    print("Running Safaricom Core Provisioning reminders: hours 30, 36, 40.")


# ======================== TEST REMINDER TASKS ========================


@shared_task
def dispatch_test_age_reminders():
    schedule_test_dispatch_age_reminders()
    print("Running test dispatch reminders: hours 1, 2, 3, 4, 5.")


@shared_task
def dispatch_test_age_reminders_safaricom():
    schedule_test_dispatch_age_reminders_safaricom()
    print("Running Safaricom test dispatch reminders: hours 1, 2, 3.")
