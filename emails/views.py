from django.contrib.auth.decorators import login_required
from .optimization_otb_utils import build_context
from django.shortcuts import render, redirect
from mashauri.models import User
from django.http import HttpResponseForbidden

@login_required
def redirect_to_optimization_dashboard(request):
    if request.user.role == User.Role.ADMIN:
        return redirect('admin_optimization_dashboard')
    elif request.user.role == User.Role.MSP:
        return redirect('msp_optimization_dashboard')
    elif request.user.role == User.Role.FDP:
        return redirect('fdp_optimization_dashboard')
    elif request.user.role == User.Role.ENTERPRISE_CONNECTIVITY:
        return redirect('ec_optimization_dashboard')
    elif request.user.role == User.Role.ENTERPRISE_PROJECT:
        return redirect('ep_optimization_dashboard')
    elif request.user.role == User.Role.SUPPORT:
        return redirect('support_optimization_dashboard')
    elif request.user.role == User.Role.ROLLOUT_PARTNER:
        return redirect('rp_optimization_dashboard')
    else:
        return HttpResponseForbidden(
            "You don't have access to the Optimization dashboard."
        )


@login_required
def redirect_to_otb_dashboard(request):
    if request.user.role == User.Role.ADMIN:
        return redirect('admin_otb_dashboard')
    elif request.user.role == User.Role.MSP:
        return redirect('msp_otb_dashboard')
    elif request.user.role == User.Role.FDP:
        return redirect('fdp_otb_dashboard')
    elif request.user.role == User.Role.ENTERPRISE_CONNECTIVITY:
        return redirect('ec_otb_dashboard')
    elif request.user.role == User.Role.ENTERPRISE_PROJECT:
        return redirect('ep_otb_dashboard')
    elif request.user.role == User.Role.SUPPORT:
        return redirect('support_otb_dashboard')
    elif request.user.role == User.Role.ROLLOUT_PARTNER:
        return redirect('rp_otb_dashboard')
    else:
        return HttpResponseForbidden(
            "You don't have access to the OTB dashboard."
        )

################################ OPTIMIZATION ####################################
@login_required
def msp_optimization_dashboard(request):
    user = request.user

    context = build_context(
        user,
        'msp',
        user.msp_category,
        request,
        escalation_type='Optimization'
    )

    return render(
        request,
        'optimization/msp_optimization_dashboard.html',
        context
    )


@login_required
def fdp_optimization_dashboard(request):
    user = request.user

    context = build_context(
        user,
        'fdp',
        user.fdp_category,
        request,
        escalation_type='Optimization'
    )

    return render(
        request,
        'optimization/fdp_optimization_dashboard.html',
        context
    )


@login_required
def rp_optimization_dashboard(request):
    user = request.user

    context = build_context(
        user,
        'rp',
        user.rp_category,
        request,
        escalation_type='Optimization'
    )

    return render(
        request,
        'optimization/rp_optimization_dashboard.html',
        context
    )


@login_required
def ec_optimization_dashboard(request):
    user = request.user

    context = build_context(
        user,
        None,
        None,
        request,
        escalation_type='Optimization'
    )

    return render(
        request,
        'optimization/ec_optimization_dashboard.html',
        context
    )


@login_required
def ep_optimization_dashboard(request):
    user = request.user

    context = build_context(
        user,
        None,
        None,
        request,
        escalation_type='Optimization'
    )

    return render(
        request,
        'optimization/ep_optimization_dashboard.html',
        context
    )


@login_required
def support_optimization_dashboard(request):
    user = request.user

    context = build_context(
        user,
        None,
        None,
        request,
        escalation_type='Optimization'
    )

    return render(
        request,
        'optimization/support_optimization_dashboard.html',
        context
    )


################################ OTB ####################################
@login_required
def msp_otb_dashboard(request):
    user = request.user

    context = build_context(
        user,
        'msp',
        user.msp_category,
        request,
        escalation_type='OTB'
    )

    return render(
        request,
        'otb/msp_otb_dashboard.html',
        context
    )


@login_required
def fdp_otb_dashboard(request):
    user = request.user

    context = build_context(
        user,
        'fdp',
        user.fdp_category,
        request,
        escalation_type='OTB'
    )

    return render(
        request,
        'otb/fdp_otb_dashboard.html',
        context
    )


@login_required
def rp_otb_dashboard(request):
    user = request.user

    context = build_context(
        user,
        'rp',
        user.rp_category,
        request,
        escalation_type='OTB'
    )

    return render(
        request,
        'otb/rp_otb_dashboard.html',
        context
    )


@login_required
def ec_otb_dashboard(request):
    user = request.user

    context = build_context(
        user,
        None,
        None,
        request,
        escalation_type='OTB'
    )

    return render(
        request,
        'otb/ec_otb_dashboard.html',
        context
    )


@login_required
def ep_otb_dashboard(request):
    user = request.user

    context = build_context(
        user,
        None,
        None,
        request,
        escalation_type='OTB'
    )

    return render(
        request,
        'otb/ep_otb_dashboard.html',
        context
    )


@login_required
def support_otb_dashboard(request):
    user = request.user

    context = build_context(
        user,
        None,
        None,
        request,
        escalation_type='OTB'
    )

    return render(
        request,
        'otb/support_otb_dashboard.html',
        context
    )