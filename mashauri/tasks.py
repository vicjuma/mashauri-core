from celery import shared_task
from .utils import schedule_nine_am_emails, schedule_twelve_noon_emails, \
    schedule_four_pm_emails
from .models import Dispatch
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
