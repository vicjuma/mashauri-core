from datetime import timedelta

from django.utils.timezone import now

from mashauri.models import Dispatch
from emails.models import MSPEscalationMatrix, MSPEscalationEmail, HODEscalationEmail
from mashauri.utils import generate_pdf_mailed, save_contentfile_to_disk, send_mail


def get_optimization_sla_notifications_due():
    current_time = now()

    pm_cutoff = current_time - timedelta(days=7)
    coo_cutoff = current_time - timedelta(days=8)
    cto_cutoff = current_time - timedelta(days=9)
    ceo_cutoff = current_time - timedelta(days=9)
    hod_cutoff = current_time - timedelta(days=10)

    return {
        'pm': Dispatch.objects.filter(
            created_at__lte=pm_cutoff,
            status='Progress',
            escalation_type='Optimization',
            pm_sla_email_sent_optimization=False,
        ),

        'coo': Dispatch.objects.filter(
            created_at__lte=coo_cutoff,
            status='Progress',
            escalation_type='Optimization',
            coo_sla_email_sent_optimization=False,
        ),

        'cto': Dispatch.objects.filter(
            created_at__lte=cto_cutoff,
            status='Progress',
            escalation_type='Optimization',
            cto_sla_email_sent_optimization=False,
        ),

        'ceo': Dispatch.objects.filter(
            created_at__lte=ceo_cutoff,
            status='Progress',
            escalation_type='Optimization',
            ceo_sla_email_sent_optimization=False,
        ),

        'hod': Dispatch.objects.filter(
            created_at__lte=hod_cutoff,
            status='Progress',
            escalation_type='Optimization',
            hod_sla_email_sent_optimization=False,
        ),
    }


def get_otb_sla_notifications_due():
    current_time = now()

    pm_cutoff = current_time - timedelta(days=15)
    coo_cutoff = current_time - timedelta(days=18)
    cto_cutoff = current_time - timedelta(days=20)
    ceo_cutoff = current_time - timedelta(days=10)
    hod_cutoff = current_time - timedelta(days=21)

    return {
        'pm': Dispatch.objects.filter(
            created_at__lte=pm_cutoff,
            status='Progress',
            escalation_type='OTB',
            pm_sla_email_sent_otb=False,
        ),

        'coo': Dispatch.objects.filter(
            created_at__lte=coo_cutoff,
            status='Progress',
            escalation_type='OTB',
            coo_sla_email_sent_otb=False,
        ),

        'cto': Dispatch.objects.filter(
            created_at__lte=cto_cutoff,
            status='Progress',
            escalation_type='OTB',
            cto_sla_email_sent_otb=False,
        ),

        'ceo': Dispatch.objects.filter(
            created_at__lte=ceo_cutoff,
            status='Progress',
            escalation_type='OTB',
            ceo_sla_email_sent_otb=False,
        ),

        'hod': Dispatch.objects.filter(
            created_at__lte=hod_cutoff,
            status='Progress',
            escalation_type='OTB',
            hod_sla_email_sent_otb=False,
        ),
    }


def get_normal_sla_notifications_due():
    current_time = now()

    pm_cutoff = current_time - timedelta(hours=24)
    coo_cutoff = current_time - timedelta(hours=30)
    cto_cutoff = current_time - timedelta(hours=40)
    ceo_cutoff = current_time - timedelta(hours=40)
    hod_cutoff = current_time - timedelta(hours=48)

    return {
        'pm': Dispatch.objects.filter(
            created_at__lte=pm_cutoff,
            status='Progress',
            escalation_type__in=[
                'Proactive',
                'Reactive',
                'Interception',
                'Support',
            ],
            pm_sla_email_sent_normal=False,
        ),

        'coo': Dispatch.objects.filter(
            created_at__lte=coo_cutoff,
            status='Progress',
            escalation_type__in=[
                'Proactive',
                'Reactive',
                'Interception',
                'Support',
            ],
            coo_sla_email_sent_normal=False,
        ),

        'cto': Dispatch.objects.filter(
            created_at__lte=cto_cutoff,
            status='Progress',
            escalation_type__in=[
                'Proactive',
                'Reactive',
                'Interception',
                'Support',
            ],
            cto_sla_email_sent_normal=False,
        ),

        'ceo': Dispatch.objects.filter(
            created_at__lte=ceo_cutoff,
            status='Progress',
            escalation_type__in=[
                'Proactive',
                'Reactive',
                'Interception',
                'Support',
            ],
            ceo_sla_email_sent_normal=False,
        ),

        'hod': Dispatch.objects.filter(
            created_at__lte=hod_cutoff,
            status='Progress',
            escalation_type__in=[
                'Proactive',
                'Reactive',
                'Interception',
                'Support',
            ],
            hod_sla_email_sent_normal=False,
        ),
    }


def get_msp_escalation_recipients(msp, role):
    if not msp:
        return []

    matrix = MSPEscalationMatrix.objects.filter(
        msp=msp,
        is_active=True
    ).first()

    if not matrix:
        return []

    return list(
        MSPEscalationEmail.objects.filter(
            matrix=matrix,
            role=role,
            is_active=True
        ).values_list(
            'email',
            flat=True
        )
    )


def send_sla_matrix_report(
    dispatches,
    msp,
    role,
    sla_type,
    sent_field,
    timeline
):
    if not msp:
        return

    dispatches = dispatches.filter(
        msp=msp,
        **{
            sent_field: False
        }
    )

    if not dispatches.exists():
        return

    recipients = get_msp_escalation_recipients(
        msp,
        role
    )

    if not recipients:
        print(
            f'No recipients configured for '
            f'{msp} - {role}'
        )
        return

    dispatch_list = list(
        dispatches.order_by('created_at')
    )

    filename = (
        f'{msp.lower()}_'
        f'{sla_type.lower()}_'
        f'{role.lower().replace(" ", "_")}_'
        f'sla_matrix'
    )

    title = (
        f'{msp} {sla_type} SLA Escalation Matrix - '
        f'{role}'
    )

    pdf = generate_pdf_mailed(
        dispatch_list,
        filename,
        title
    )

    pdf_path = save_contentfile_to_disk(
        pdf,
        filename
    )

    subject = (
        f'{msp} {sla_type} SLA Matrix - {role}'
    )

    message = (
        f'Please find attached the {sla_type} SLA '
        f'escalation matrix report for {msp}.\n\n'
        f'Escalation Role: {role}\n'
        f'SLA Timeline: {timeline}\n'
        f'Number of Dispatches: {len(dispatch_list)}\n\n'
        f'The attached report contains the dispatches '
        f'due for this SLA escalation.\n\n'
        f'Mashauri | Core.'
    )

    send_mail(
        recipients=recipients,
        subject=subject,
        message=message,
        attachment_path=[pdf_path]
    )

    dispatches.update(
        **{
            sent_field: True
        }
    )

    print(
        f'SLA email sent: '
        f'{sla_type} | {msp} | {role} | '
        f'{len(dispatch_list)} dispatches'
    )


def send_optimization_sla_matrix_emails():
    optimization_due = get_optimization_sla_notifications_due()

    permutations = [
        (
            'pm',
            'Project Manager',
            'pm_sla_email_sent_optimization',
            '7 days'
        ),
        (
            'coo',
            'Chief Operating Officer',
            'coo_sla_email_sent_optimization',
            '8 days'
        ),
        (
            'cto',
            'Chief Technical Officer',
            'cto_sla_email_sent_optimization',
            '9 days'
        ),
        (
            'ceo',
            'Chief Executive Officer',
            'ceo_sla_email_sent_optimization',
            '9 days'
        ),
        (
            'hod',
            'HOD',
            'hod_sla_email_sent_optimization',
            '10 days'
        ),
    ]

    for permutation, role, sent_field, timeline in permutations:
        dispatches = optimization_due[permutation]

        if role == 'HOD':
            send_hod_sla_matrix_report(
                dispatches=dispatches,
                sla_type='Optimization',
                sent_field=sent_field,
                timeline=timeline
            )
            continue

        msps = dispatches.values_list(
            'msp',
            flat=True
        ).distinct()

        for msp in msps:
            send_sla_matrix_report(
                dispatches=dispatches,
                msp=msp,
                role=role,
                sla_type='Optimization',
                sent_field=sent_field,
                timeline=timeline
            )


def send_otb_sla_matrix_emails():
    otb_due = get_otb_sla_notifications_due()

    permutations = [
        (
            'pm',
            'Project Manager',
            'pm_sla_email_sent_otb',
            '15 days'
        ),
        (
            'coo',
            'Chief Operating Officer',
            'coo_sla_email_sent_otb',
            '18 days'
        ),
        (
            'cto',
            'Chief Technical Officer',
            'cto_sla_email_sent_otb',
            '20 days'
        ),
        (
            'ceo',
            'Chief Executive Officer',
            'ceo_sla_email_sent_otb',
            '10 days'
        ),
        (
            'hod',
            'HOD',
            'hod_sla_email_sent_otb',
            '21 days'
        ),
    ]

    for permutation, role, sent_field, timeline in permutations:
        dispatches = otb_due[permutation]

        if role == 'HOD':
            send_hod_sla_matrix_report(
                dispatches=dispatches,
                sla_type='OTB',
                sent_field=sent_field,
                timeline=timeline
            )
            continue

        msps = dispatches.values_list(
            'msp',
            flat=True
        ).distinct()

        for msp in msps:
            send_sla_matrix_report(
                dispatches=dispatches,
                msp=msp,
                role=role,
                sla_type='OTB',
                sent_field=sent_field,
                timeline=timeline
            )


def send_normal_sla_matrix_emails():
    normal_due = get_normal_sla_notifications_due()

    permutations = [
        (
            'pm',
            'Project Manager',
            'pm_sla_email_sent_normal',
            '24 hours'
        ),
        (
            'coo',
            'Chief Operating Officer',
            'coo_sla_email_sent_normal',
            '30 hours'
        ),
        (
            'cto',
            'Chief Technical Officer',
            'cto_sla_email_sent_normal',
            '40 hours'
        ),
        (
            'ceo',
            'Chief Executive Officer',
            'ceo_sla_email_sent_normal',
            '40 hours'
        ),
        (
            'hod',
            'HOD',
            'hod_sla_email_sent_normal',
            '48 hours'
        ),
    ]

    for permutation, role, sent_field, timeline in permutations:
        dispatches = normal_due[permutation]

        if role == 'HOD':
            send_hod_sla_matrix_report(
                dispatches=dispatches,
                sla_type='Normal',
                sent_field=sent_field,
                timeline=timeline
            )
            continue

        msps = dispatches.values_list(
            'msp',
            flat=True
        ).distinct()

        for msp in msps:
            send_sla_matrix_report(
                dispatches=dispatches,
                msp=msp,
                role=role,
                sla_type='Normal',
                sent_field=sent_field,
                timeline=timeline
            )

def send_hod_sla_matrix_report(
    dispatches,
    sla_type,
    sent_field,
    timeline
):
    dispatches = dispatches.filter(
        **{
            sent_field: False
        }
    )

    if not dispatches.exists():
        return

    recipients = list(
        HODEscalationEmail.objects.filter(
            is_active=True
        ).values_list(
            'email',
            flat=True
        )
    )

    if not recipients:
        print(
            f'No HOD recipients configured for '
            f'{sla_type}'
        )
        return

    dispatch_list = list(
        dispatches.order_by('created_at')
    )

    filename = (
        f'hod_{sla_type.lower()}_sla_matrix'
    )

    title = (
        f'HOD {sla_type} SLA Escalation Matrix'
    )

    pdf = generate_pdf_mailed(
        dispatch_list,
        filename,
        title
    )

    pdf_path = save_contentfile_to_disk(
        pdf,
        filename
    )

    subject = (
        f'HOD {sla_type} SLA Matrix'
    )

    message = (
        f'Please find attached the {sla_type} SLA '
        f'escalation matrix report for HOD.\n\n'
        f'Escalation Role: HOD\n'
        f'SLA Timeline: {timeline}\n'
        f'Number of Dispatches: {len(dispatch_list)}\n\n'
        f'The attached report contains the dispatches '
        f'due for this SLA escalation across all partners.\n\n'
        f'Mashauri | Core.'
    )

    send_mail(
        recipients=recipients,
        subject=subject,
        message=message,
        attachment_path=[pdf_path]
    )

    dispatches.update(
        **{
            sent_field: True
        }
    )


def send_all_sla_matrix_emails():
    send_optimization_sla_matrix_emails()
    send_otb_sla_matrix_emails()
    send_normal_sla_matrix_emails()