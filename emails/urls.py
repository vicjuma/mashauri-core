from . import views
from django.urls import path


urlpatterns = [
    # OPTIMIZATION
    path(
        'dashboard/msp/optimization',
        views.msp_optimization_dashboard,
        name='msp_optimization_dashboard'
    ),
    path(
        'dashboard/fdp/optimization',
        views.fdp_optimization_dashboard,
        name='fdp_optimization_dashboard'
    ),
    path(
        'dashboard/ec/optimization',
        views.ec_optimization_dashboard,
        name='ec_optimization_dashboard'
    ),
    path(
        'dashboard/ep/optimization',
        views.ep_optimization_dashboard,
        name='ep_optimization_dashboard'
    ),
    path(
        'dashboard/rp/optimization',
        views.rp_optimization_dashboard,
        name='rp_optimization_dashboard'
    ),
    path(
        'dashboard/support/optimization',
        views.support_optimization_dashboard,
        name='support_optimization_dashboard'
    ),

    # OTB
    path(
        'dashboard/msp/otb',
        views.msp_otb_dashboard,
        name='msp_otb_dashboard'
    ),
    path(
        'dashboard/fdp/otb',
        views.fdp_otb_dashboard,
        name='fdp_otb_dashboard'
    ),
    path(
        'dashboard/ec/otb',
        views.ec_otb_dashboard,
        name='ec_otb_dashboard'
    ),
    path(
        'dashboard/ep/otb',
        views.ep_otb_dashboard,
        name='ep_otb_dashboard'
    ),
    path(
        'dashboard/rp/otb',
        views.rp_otb_dashboard,
        name='rp_otb_dashboard'
    ),
    path(
        'dashboard/support/otb',
        views.support_otb_dashboard,
        name='support_otb_dashboard'
    ),

    # Redirection
    path(
        'dashboard/optimization-redirect',
        views.redirect_to_optimization_dashboard,
        name='redirect_to_optimization_dashboard'
    ),

    path(
        'dashboard/otb-redirect',
        views.redirect_to_otb_dashboard,
        name='redirect_to_otb_dashboard'
    ),

]
