import os
# from django.core.serializers import serialize
import plotly.graph_objs as go
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import DispatchStageComment, User, Dispatch, Comment, DispatchStageHistory
from datetime import timedelta
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from collections import defaultdict
from functools import wraps
from .utils import build_context, extract_dispatch_data, \
    save_dispatch, save_dispatch_image, create_ticket_and_pdf, \
    build_escalation_url, determine_email_recipients, \
    send_notification_email, handle_comment_update, \
    handle_dispatch_closing, handle_dispatch_reassignment
from django.db import transaction
from django.contrib import messages


def unauthenticated_user(view_func):
    @wraps(view_func)
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role == User.Role.ADMIN:
                return redirect('admin_dashboard')
            elif request.user.role == User.Role.MSP:
                return redirect('msp_dashboard')
            elif request.user.role == User.Role.FDP:
                return redirect('fdp_dashboard')
            elif request.user.role == User.Role.ENTERPRISE_CONNECTIVITY:
                return redirect('ec_dashboard')
            elif request.user.role == User.Role.ENTERPRISE_PROJECT:
                return redirect('ep_dashboard')
            elif request.user.role == User.Role.SUPPORT:
                return redirect('support_dashboard')
            else:
                return view_func(request, *args, **kwargs)
    return wrapper_func


def calculate_time_remaining(datetime_value):
    now = timezone.now()
    remaining_time = datetime_value - now

    if remaining_time < timedelta(0):
        time_since_expired = now - datetime_value
        hours = time_since_expired.seconds // 3600
        minutes = (time_since_expired.seconds % 3600) // 60
        return f"Expired {hours} hours {minutes} minutes ago"

    # Calculate hours and minutes remaining
    hours = remaining_time.seconds // 3600
    minutes = (remaining_time.seconds % 3600) // 60

    return f"{hours} hours {minutes} minutes remaining"


@csrf_exempt
def user_login(request):
    if request.user.is_authenticated:
        if request.user.role == User.Role.ADMIN:
            return redirect('admin_dashboard')
        elif request.user.role == User.Role.MSP:
            return redirect('msp_dashboard')
        elif request.user.role == User.Role.FDP:
            return redirect('fdp_dashboard')
        elif request.user.role == User.Role.ENTERPRISE_CONNECTIVITY:
            return redirect('ec_dashboard')
        elif request.user.role == User.Role.ENTERPRISE_PROJECT:
            return redirect('ep_dashboard')
        elif request.user.role == User.Role.SUPPORT:
            return redirect('support_dashboard')
        elif request.user.role == User.Role.ROLLOUT_PARTNER:
            return redirect('rp_dashboard')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if not username or not password:
            return JsonResponse(
                {'status': 'error',
                 'message': 'Username and password are required'}, status=400)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse(
                {'status': 'error',
                 'message': 'Invalid username or password'}, status=401)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session['userRole'] = request.user.role
                return JsonResponse(
                    {'status': 'success',
                     'role': request.user.role}, status=200)
            else:
                return JsonResponse(
                    {'status': 'error',
                     'message': 'User account is inactive'}, status=403)
        else:
            return JsonResponse(
                {'status': 'error',
                 'message': 'Invalid username or password'}, status=401)
    return render(request, 'mashauri/index.html', {})


@login_required
def msp_dashboard(request):
    user = request.user
    context = build_context(user, 'msp', user.msp_category, request)
    return render(request, 'mashauri/msp_dashboard.html', context)


@login_required
def fdp_dashboard(request):
    user = request.user
    context = build_context(user, 'fdp', user.fdp_category, request)
    return render(request, 'mashauri/fdp_dashboard.html', context)


@login_required
def ec_dashboard(request):
    user = request.user
    context = build_context(user, None, None, request)
    return render(request, 'mashauri/ec_dashboard.html', context)


@login_required
# @unauthenticated_user
def ep_dashboard(request):
    user = request.user
    context = build_context(user, None, None, request)
    return render(request, 'mashauri/ep_dashboard.html', context)


@login_required
# @unauthenticated_user
def support_dashboard(request):
    user = request.user
    context = build_context(user, None, None, request)
    return render(request, 'mashauri/support_dashboard.html', context)


@login_required
# @unauthenticated_user
def rp_dashboard(request):
    user = request.user
    context = build_context(user, 'rp', user.rp_category, request)
    return render(request, 'mashauri/rp_dashboard.html', context)


@login_required
@csrf_exempt
def dispatch(request):
    if request.method == 'POST':
        data = extract_dispatch_data(request)
        dispatch_instance = save_dispatch(data, request.user)
        if data['dispatch_image']:
            save_dispatch_image(dispatch_instance, data['dispatch_image'])

        val, ticket = create_ticket_and_pdf(dispatch_instance, data)
        escalation_url = build_escalation_url(request, dispatch_instance.id)
        email_recipients = determine_email_recipients(
            data['msp'], data['fdp'], data['rp'])

        send_notification_email(
            escalation_type=data['escalation_type'],
            recipients=email_recipients,
            building_name=data['building_name'],
            client_name=data['client_name'],
            msp=data['msp'],
            rp=data['rp'],
            full_url=escalation_url,
            attachment_path=os.path.join(settings.MEDIA_ROOT, ticket.name)
        )

        return JsonResponse(
            {'status': 'success',
             'role': request.user.role}, status=200)

    context = {
        'msp_choices': Dispatch.MSP_CHOICES,
        'fdp_choices': Dispatch.FDP_CHOICES,
        'escalation_choices': Dispatch.ESCALATION_CHOICES,
        'rp_choices': Dispatch.RP_CHOICES
    }
    return render(request, 'mashauri/dispatch.html', context)


@login_required
@csrf_exempt
def dispatch_detail(request, pk):
    dispatch = get_object_or_404(Dispatch, pk=pk)
    current_user = request.user
    full_url = request.build_absolute_uri(
        reverse('dispatch_detail', kwargs={'pk': pk}))
    email_recipients = determine_email_recipients(
        dispatch.msp, dispatch.fdp, dispatch.rp)

    if request.method == 'POST':
        # Handle comment-only POST request
        if 'comment_only' in request.POST:
            return handle_comment_update(
                request, dispatch, current_user, email_recipients, full_url)

        # Handle dispatch closing POST request
        elif 'close' in request.POST:
            return handle_dispatch_closing(
                request, dispatch, email_recipients, full_url)

        # Handle reassignment POST request
        elif 'reassign' in request.POST:
            return handle_dispatch_reassignment(
                request, dispatch, email_recipients, full_url)

    # Fetch and render dispatch details
    comments = Comment.objects.filter(
        dispatch=dispatch).order_by('-created_at')
    filtered_image = dispatch.images.filter(image_type='creation').first()

    def is_pdf(image):
        if not image or not hasattr(image, "image") or not hasattr(image.image, "url"):
            return False  # Return False if image is None or missing attributes
        return image.image.url.lower().endswith('.pdf')
    
    is_img_pdf = is_pdf(filtered_image)
    return render(request, 'mashauri/dispatch_details.html', {
        'dispatch': dispatch,
        'is_msp': current_user.role == 'MSP',
        'is_ec': current_user.role == 'ENTERPRISE CONNECTIVITY',
        'comments': comments,
        'msp_choices': Dispatch.MSP_CHOICES,
        'rp_choices': Dispatch.RP_CHOICES,
        'user': current_user,
        'image': filtered_image,
        'is_img_pdf': is_img_pdf,
        'escalation_types': Dispatch.ESCALATION_CHOICES,
    })

@login_required
@csrf_exempt
def rp_dispatch_detail(request, pk):
    dispatch = get_object_or_404(Dispatch, pk=pk)
    current_user = request.user

    stages = [
        'Survey',
        'Design',
        'Design approval',
        'OSH',
        'Commercial approval',
        'Po issuance',
        'Materials',
        'Deployment',
        'Interception',
    ]

    current_stage = dispatch.stage
    
    stage_comments = DispatchStageComment.objects.filter(
        stage_history__dispatch=dispatch).select_related(
        'stage_history',
        'commented_by').order_by('-created_at')

    # ---------------------------------------------------------
    # POST - MOVE TO NEXT STAGE
    # ---------------------------------------------------------
    if request.method == "POST":

        action = request.POST.get("action")

        if action == "move_next":

            comment = request.POST.get("comment", "").strip()
            attachment = request.FILES.get("attachment")

            # -------------------------------------------------
            # Comment is mandatory
            # -------------------------------------------------
            if not comment:
                messages.error(
                    request,
                    "Please provide a comment before moving the dispatch."
                )

                return redirect(
                    'rp_dispatch_detail',
                    pk=dispatch.pk
                )

            # -------------------------------------------------
            # Make sure current stage is valid
            # -------------------------------------------------
            if current_stage not in stages:
                messages.error(
                    request,
                    "The current dispatch stage is invalid."
                )

                return redirect(
                    'rp_dispatch_detail',
                    pk=dispatch.pk
                )

            current_index = stages.index(current_stage)

            # -------------------------------------------------
            # Check if already at final stage
            # -------------------------------------------------
            if current_index >= len(stages) - 1:
                messages.warning(
                    request,
                    "This dispatch is already at the final stage."
                )

                return redirect(
                    'rp_dispatch_detail',
                    pk=dispatch.pk
                )

            next_stage = stages[current_index + 1]

            # -------------------------------------------------
            # Save stage + history together
            # -------------------------------------------------
            with transaction.atomic():

                # Update current dispatch stage
                dispatch.stage = next_stage
                dispatch.save(update_fields=["stage", "updated_at"])
               
                stage_completed_at = timezone.now()

                # Find when the current stage started
                previous_history = DispatchStageHistory.objects.filter(
                    dispatch=dispatch,
                    to_stage=current_stage
                ).order_by('-created_at').first()

                if previous_history and previous_history.completed_at:
                    stage_started_at = previous_history.completed_at
                else:
                    stage_started_at = dispatch.sla_timer
                    if stage_started_at:
                        if dispatch.escalation_type == 'Optimization':
                            stage_started_at -= timedelta(hours=720)
                        elif dispatch.escalation_type == 'OTB':
                            stage_started_at -= timedelta(hours=1512)
                        else:
                            stage_started_at = dispatch.created_at
                    else:
                        stage_started_at = dispatch.created_at

                stage_duration = stage_completed_at - stage_started_at

                dispatch_stage_history = DispatchStageHistory.objects.create(
                    dispatch=dispatch,
                    from_stage=current_stage,
                    to_stage=next_stage,
                    comment=comment,
                    moved_by=current_user,
                    started_at=stage_started_at,
                    completed_at=stage_completed_at,
                    duration_seconds=max(
                        0,
                        int(stage_duration.total_seconds())
                    ),
                )

                if attachment:
                    dispatch_stage_history.attachment = attachment
                    dispatch_stage_history.save(update_fields=['attachment'])

            messages.success(
                request,
                f"Dispatch moved from {current_stage} to {next_stage}."
            )

            return redirect(
                'rp_dispatch_detail',
                pk=dispatch.pk
            )
        elif action == "comment_only":

            stage_comment = request.POST.get("stage_comment", "").strip()
            selected_stage = request.POST.get("stage", "").strip()
            stage_attachment = request.FILES.get("attachment")

            # -------------------------------------------------
            # Stage comment is mandatory
            # -------------------------------------------------
            if not stage_comment:
                messages.error(
                    request,
                    "Please provide a comment."
                )

                return redirect(
                    'rp_dispatch_detail',
                    pk=dispatch.pk
                )

            # -------------------------------------------------
            # Make sure selected stage is valid
            # -------------------------------------------------
            if selected_stage not in stages:
                messages.error(
                    request,
                    "The selected dispatch stage is invalid."
                )

                return redirect(
                    'rp_dispatch_detail',
                    pk=dispatch.pk
                )

            # -------------------------------------------------
            # Create comment against the selected stage history
            # -------------------------------------------------
            stage_history = DispatchStageHistory.objects.filter(
                dispatch=dispatch,
                from_stage=selected_stage
            ).order_by('-created_at').first()
            print(stage_history)

            if not stage_history:
                messages.error(
                    request,
                    f"You cannot comment on {selected_stage}. The stage is not complete"
                )

                return redirect(
                    'rp_dispatch_detail',
                    pk=dispatch.pk
                )

            # -------------------------------------------------
            # Save stage comment
            # -------------------------------------------------
            with transaction.atomic():

                stage_comment_obj = DispatchStageComment.objects.create(
                    stage_history=stage_history,
                    comment=stage_comment,
                    commented_by=current_user,
                )

                if stage_attachment:
                    stage_comment_obj.attachment = stage_attachment
                    stage_comment_obj.save(update_fields=['attachment'])

            messages.success(
                request,
                f"Comment added to the {selected_stage} stage."
            )

            return redirect(
                'rp_dispatch_detail',
                pk=dispatch.pk
            )

    # ---------------------------------------------------------
    # CURRENT STAGE INFORMATION
    # ---------------------------------------------------------

    if current_stage in stages:

        current_stage_index = stages.index(current_stage)

        if current_stage_index < len(stages) - 1:
            next_stage = stages[current_stage_index + 1]
        else:
            next_stage = None

    else:
        current_stage_index = None
        next_stage = None

    # ---------------------------------------------------------
    # STAGE HISTORY
    # ---------------------------------------------------------

    stage_history = dispatch.stage_history.select_related(
        'moved_by'
    ).order_by('-created_at')

    # ---------------------------------------------------------
    # EXISTING DATA
    # ---------------------------------------------------------

    full_url = request.build_absolute_uri(
        reverse('dispatch_detail', kwargs={'pk': pk})
    )

    email_recipients = determine_email_recipients(
        dispatch.msp,
        dispatch.fdp,
        dispatch.rp
    )

    context = {
        'dispatch': dispatch,
        'user': current_user,

        # Workflow
        'stages': stages,
        'current_stage': current_stage,
        'current_stage_index': current_stage_index,
        'next_stage': next_stage,

        # Stage history
        'stage_history': stage_history,

        # Special states
        'is_on_hold': current_stage == 'On hold',
        'is_dropped': current_stage == 'Dropped',

        # Useful UI flag
        'can_move_next': (
            current_stage in stages
            and current_stage_index is not None
            and current_stage_index < len(stages) - 1
        ),

        # Existing data
        'full_url': full_url,
        'email_recipients': email_recipients,

        'stage_comments': stage_comments
    }

    return render(
        request,
        'mashauri/rp_dispatch_details.html',
        context
    )


def plots_visualization(request):
    all_dispatches = Dispatch.objects.all().order_by('created_at')
    dispatch_numbers = list(range(1, len(all_dispatches) + 1))
    dispatch_counts = [idx + 1 for idx in range(len(all_dispatches))]

    # Plot: Dispatch Growth Over Time
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dispatch_numbers,
        y=dispatch_counts,
        mode='lines+markers', name='Dispatch Growth'))
    fig.update_layout(
        title='Dispatch Growth Over Time',
        xaxis_title='Number of Dispatches',
        yaxis_title='Cumulative Count',
        width=800,
        height=600
    )

    # Convert the Plotly figure to JSON
    plot_div = fig.to_html(full_html=False, config={'staticPlot': True})

    # Total escalations and aggregations for MSP and FDP
    total_escalations = 0
    msp_escalations = defaultdict(int)
    fdp_escalations = defaultdict(int)

    for dispatch in all_dispatches:
        if dispatch.escalation_type:
            total_escalations += 1
            msp_escalations[dispatch.msp] += 1
            fdp_escalations[dispatch.fdp] += 1

    msp_escalations = dict(msp_escalations)
    fdp_escalations = dict(fdp_escalations)

    # MSP Bar Chart
    fig_msp = go.Figure()
    fig_msp.add_trace(go.Bar(
        name='Escalations to MSP',
        x=list(msp_escalations.keys()), y=list(msp_escalations.values()),
        marker_color='skyblue'))
    fig_msp.update_layout(
        title='Escalations to Each MSP',
        xaxis_title='MSP',
        yaxis_title='Count',
        width=800,
        height=600
    )
    plot_div_msp = fig_msp.to_html(
        full_html=False, config={'staticPlot': True})

    # FDP Bar Chart
    fig_fdp = go.Figure()
    fig_fdp.add_trace(go.Bar(
        name='Escalations from FDP',
        x=list(fdp_escalations.keys()), y=list(fdp_escalations.values()),
        marker_color='orange'))
    fig_fdp.update_layout(
        title='Escalations from Each FDP',
        xaxis_title='FDP',
        yaxis_title='Count',
        width=800,
        height=600
    )
    plot_div_fdp = fig_fdp.to_html(
        full_html=False, config={'staticPlot': True})

    # Escalation Types Bar Chart
    escalation_type_counts = defaultdict(int)
    for dispatch in all_dispatches:
        escalation_type_counts[dispatch.escalation_type] += 1
    escalation_type_counts = dict(escalation_type_counts)

    fig_esc = go.Figure()
    fig_esc.add_trace(go.Bar(
        x=list(escalation_type_counts.keys()),
        y=list(escalation_type_counts.values()),
        marker_color='royalblue'))
    fig_esc.update_layout(
        title='Number of Escalations by Escalation Type',
        xaxis_title='Escalation Type',
        yaxis_title='Count',
        width=800,
        height=600
    )
    plot_div_esc = fig_esc.to_html(
        full_html=False, config={'staticPlot': True})

    # --- Average SLA per Escalation Type ---
    sla_durations = defaultdict(float)  # Total SLA durations
    sla_counts = defaultdict(int)  # Escalation counts

    for dispatch in all_dispatches:
        if dispatch.escalation_type and dispatch.sla_timer:
            # Calculate SLA duration in hours
            duration = (
                dispatch.sla_timer - dispatch.created_at
                ).total_seconds() / 3600
            sla_durations[dispatch.escalation_type] += duration
            sla_counts[dispatch.escalation_type] += 1

    # Calculate average SLA
    average_sla = {etype: sla_durations[etype] / sla_counts[etype]
                   for etype in sla_durations if sla_counts[etype] > 0}

    # SLA Bar Chart
    fig_sla = go.Figure()
    fig_sla.add_trace(go.Bar(
        x=list(average_sla.keys()),
        y=list(average_sla.values()),
        marker_color='green'))
    fig_sla.update_layout(
        title='Average SLA Hours by Escalation Type',
        xaxis_title='Escalation Type',
        yaxis_title='Average SLA (Hours)',
        width=800,
        height=600
    )
    plot_div_sla = fig_sla.to_html(
        full_html=False, config={'staticPlot': True})

    # Context
    context = {
        'plot_div': plot_div,
        'plot_div_msp': plot_div_msp,
        'plot_div_fdp': plot_div_fdp,
        'total_escalations': total_escalations,
        'plot_div_esc': plot_div_esc,
        'plot_div_sla': plot_div_sla  # New SLA Chart
    }
    return render(request, 'mashauri/presentation.html', context)


def logout_user(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logging out


@login_required
def redirect_to_dashboard(request):
    if request.user.role == User.Role.ADMIN:
        return redirect('admin_dashboard')
    elif request.user.role == User.Role.MSP:
        return redirect('msp_dashboard')
    elif request.user.role == User.Role.FDP:
        return redirect('fdp_dashboard')
    elif request.user.role == User.Role.ENTERPRISE_CONNECTIVITY:
        return redirect('ec_dashboard')
    elif request.user.role == User.Role.ENTERPRISE_PROJECT:
        return redirect('ep_dashboard')
    elif request.user.role == User.Role.SUPPORT:
        return redirect('support_dashboard')
    elif request.user.role == 'ROLLOUT_PARTNER':
        return redirect('rp_dashboard')
    else:
        return HttpResponseForbidden("You don't have access to any dashboard.")


@login_required
def average_sla(request):
    from collections import defaultdict

    # Fetch all dispatches
    all_dispatches = Dispatch.objects.all()

    # Initialize dictionaries to store SLA durations and counts
    sla_durations = defaultdict(float)  # Total SLA durations in hours
    sla_counts = defaultdict(int)  # Counts of escalation types

    # Calculate SLA durations
    for dispatch in all_dispatches:
        if dispatch.sla_timer and dispatch.created_at:
            duration = (
                dispatch.sla_timer - dispatch.created_at
                ).total_seconds() / 3600  # Convert seconds to hours
            sla_durations[dispatch.escalation_type] += duration
            sla_counts[dispatch.escalation_type] += 1

    # Helper function to format hours into hours and minutes
    def format_duration(hours):
        total_minutes = int(hours * 60)
        h, m = divmod(total_minutes, 60)
        return f"{h}h {m}m"

    # Calculate average SLA for each escalation type (raw hours, not formatted)
    raw_average_sla = {
        etype: sla_durations[
            etype] / sla_counts[etype]
        for etype in sla_durations if sla_counts[etype] > 0}

    # Combine Reactive and Interception categories before formatting
    reactive_interception_avg = None
    if 'Reactive' in raw_average_sla and 'Interception' in raw_average_sla:
        reactive_interception_avg = (
            raw_average_sla['Reactive'
                            ] + raw_average_sla['Interception']) / 2

    # Prepare formatted SLA data
    sla_data = {
        'Reactive_Interception': format_duration(
            reactive_interception_avg
            ) if reactive_interception_avg is not None else "No Data",
        'Optimization': format_duration(
            raw_average_sla.get('Optimization', 0)
            ) if 'Optimization' in raw_average_sla else "No Data",
        'Proactive': format_duration(
            raw_average_sla.get('Proactive', 0)
            ) if 'Proactive' in raw_average_sla else "No Data",
        'Support': format_duration(
            raw_average_sla.get('Support', 0)
            ) if 'Support' in raw_average_sla else "No Data",
    }

    # Pass the calculated SLA data to the template
    context = {
        'Reactive_Interception': sla_data['Reactive_Interception'],
        'Optimization': sla_data['Optimization'],
        'Proactive': sla_data['Proactive'],
        'Support': sla_data['Support'],
    }
    return render(request, 'mashauri/average_sla.html', context)
