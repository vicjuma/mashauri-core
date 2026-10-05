from mashauri.utils import get_search_results, calculate_time_fields, calculate_status_counts
from mashauri.models import Dispatch
from django.conf import settings
from django.core.serializers import serialize
from django.utils.timezone import now

def get_filtered_dispatches(
        category_field,
        category_value,
        status=None,
        escalation_type=None):
    """
    Filter dispatches based on user category, status,
    and optionally escalation type.
    """

    filters = {}

    # Category filter
    if category_field and category_value:
        filters[category_field] = category_value

    # Status filter
    if status:
        filters['status'] = status

    # Escalation type filter
    if escalation_type:
        filters['escalation_type'] = escalation_type

    return Dispatch.objects.filter(
        **filters
    ).order_by('-sla_timer')


def build_context(user, category_field, category_value, request, escalation_type=None):
    """
    Build a context dictionary for the dashboard views.
    """
    all_dispatches = get_filtered_dispatches(
        category_field, category_value, escalation_type=escalation_type)
    closed_dispatches = get_filtered_dispatches(
        category_field, category_value, status='Closed', escalation_type=escalation_type)
    closed_dispatches_count = closed_dispatches.count()
    closed_dispatches_json = serialize('json', closed_dispatches)

    active_dispatches = get_filtered_dispatches(
        category_field, category_value, status='Progress', escalation_type=escalation_type).count()
    expired_dispatches = get_filtered_dispatches(
        category_field, category_value, status='Progress',
        escalation_type=escalation_type).filter(sla_timer__lte=now()).count()

    q = request.GET.get("q")
    search_dispatches, searched = get_search_results(
        q, ["msp", "client_name", "building_name", "escalation_type"])
    if search_dispatches:
        if escalation_type:
            search_dispatches = search_dispatches.filter(escalation_type=escalation_type)

        all_dispatches = search_dispatches
    # Calculate time fields and status counts
    all_dispatches = [
        calculate_time_fields(dispatch) for dispatch in all_dispatches]

    def get_closure_message(expired_at, closed_at):
        if not expired_at or not closed_at:
            return "Not enough data to determine closure time."
        
        duration = abs(closed_at - expired_at)
        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes = remainder // 60

        return f"Closed after {days} days, {hours} hours, and {minutes} minutes expiration."
    
    for dispatch in all_dispatches:
        dispatch.closure_message = get_closure_message(dispatch.expired_at, dispatch.closed_at)
    
    status_counts_user = calculate_status_counts(all_dispatches)
    status_counts_all = calculate_status_counts(all_dispatches)

    data = {
        'user': user,
        'status_counts': status_counts_user,
        'status_counts_all': status_counts_all,
        'dispatches': all_dispatches,
        'active_dispatches': active_dispatches,
        'total_dispatches_all': sum(status_counts_user.values()),
        'breached': expired_dispatches,
        'closed_dispatches_json': closed_dispatches_json,
        'closed_dispatches_count': closed_dispatches_count,
        'MEDIA_URL': settings.MEDIA_URL,
        'searched': searched,
        'dispatch_choices': {
            'escalation_type': Dispatch._meta.get_field('escalation_type').choices,
            'msp': Dispatch._meta.get_field('msp').choices,
            'fdp': Dispatch._meta.get_field('fdp').choices,
            'rp': Dispatch._meta.get_field('rp').choices,
        },
    }
    return data