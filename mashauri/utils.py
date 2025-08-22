import io
import os
import ssl
import smtplib
import tempfile
from io import BytesIO
from django.conf import settings
from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A6
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, \
    Spacer, Image, Table, TableStyle
from reportlab.lib import colors
from .models import Dispatch, DispatchImage, Ticket, Comment
from django.utils.timezone import now
from datetime import timedelta
from django.core.serializers import serialize
from mashauri.documents import DispatchDocument
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from django.shortcuts import render
from reportlab.lib.pagesizes import letter, landscape


# Modify the role decorator to redirect to the appropriate dashboard
def role_required(required_role, redirect_url_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not (
                request.user.is_authenticated) or (
                    request.user.role != required_role):
                return redirect(reverse(redirect_url_name))
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# Admin users only
def admin_required(view_func):
    return role_required('ADMIN', 'admin_dashboard')(view_func)


# MSP users only
def msp_required(view_func):
    return role_required('MSP', 'msp_dashboard')(view_func)


# FDP users only
def fdp_required(view_func):
    return role_required('FDP', 'fdp_dashboard')(view_func)


# Enterprise Connectivity users only
def enterprise_connectivity_required(view_func):
    return role_required('ENTERPRISE_CONNECTIVITY', 'ec_dashboard')(view_func)


# Enterprise Project users only
def enterprise_project_required(view_func):
    return role_required(
        'ENTERPRISE_PROJECT', 'enterprise_project_dashboard')(view_func)


# Support users only
def support_required(view_func):
    return role_required(
        'SUPPORT', 'support_dashboard')(view_func)


# Rollout Partner users only
def rollout_partner_required(view_func):
    return role_required(
        'ROLLOUT_PARTNER', 'rollout_partner_dashboard')(view_func)


def send_mail(recipients, subject, message, attachment_path=None):
    # try:
    if settings.MAIL_SSL:
        server_type = smtplib.SMTP_SSL
    else:
        server_type = smtplib.SMTP

    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = ', '.join(
        recipients) if isinstance(
            recipients, list) else recipients
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    # If an attachment is provided, add it
    if attachment_path:
        for attachment_p in attachment_path:
            if isinstance(attachment_p, ContentFile):
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment_p.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={attachment_p.name}.pdf",
                )
                msg.attach(part)
            elif os.path.isfile(attachment_p):  # Check if it's a file
                with open(attachment_p, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={attachment_p.split('/')[-1]}",
                )
                msg.attach(part)
            else:
                pass

    # Connect to the email server and send the message
    with server_type(
        settings.MAIL_HOST_SERVER,
        settings.EMAIL_HOST_PORT,
            context=ssl.create_default_context()) as server:
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.sendmail(settings.EMAIL_HOST_USER, recipients, msg.as_string())

    print(f"Email successfully sent to {recipients}")


def generate_pdf(
        building_name,
        building_id,
        msp, fdp,
        escalation_type,
        comments, coordinates, CN, CID, tid):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A6,
                            topMargin=0,
                            bottomMargin=0.125 * inch,
                            leftMargin=0.125 * inch,
                            rightMargin=0.125 * inch)

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.darkblue,
        spaceAfter=10,
    )

    header_style = ParagraphStyle(
        'Header',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.darkgreen,
        spaceAfter=10,
    )
    darkred = colors.Color(0.5, 0, 0)
    normal_style = ParagraphStyle(
        'Body',
        parent=styles['BodyText'],
        textColor=darkred,
        spaceAfter=10,
    )
    # normal_style = styles['BodyText']

    # Document dimensions
    doc_width, doc_height = A6

    # Logo dimensions
    logo_width = doc_width - (doc.leftMargin + doc.rightMargin)
    logo_height = doc_height * 0.0625  # 25% of the document height

    image_width = 1600  # Example image width
    image_height = 399  # Example image height

    scale_factor = logo_height / image_height
    logo_width = image_width * scale_factor

    # Header Image
    logo_path = "https://mouseinc.net/wp-content/uploads/2024/07/logo.jpg"
    logo = Image(logo_path, width=logo_width, height=logo_height)

    # Content
    elements = []

    elements.append(logo)
    elements.append(Paragraph("Escalation/Dispatch Ticket", title_style))
    elements.append(Paragraph(f"MSH-{str(tid).zfill(7)}", header_style))

    # Table data
    data = [
        ['PROPERTY', 'VALUE'],
        ['Building Name', building_name],
        ['Building ID', building_id],
        ['Building Coordinates', coordinates],
        ['MSP', msp],
        ['FDP', fdp],
        ['Escalation Type', escalation_type],
        ['Client Name', CN],
        ['Client ID', CID]
    ]

    # Create table
    table = Table(
        data,
        colWidths=[
            (
                doc.width - doc.leftMargin - doc.rightMargin) / 2.0] * 2)

    # Style the table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 1),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1),
        ('WORDWRAP', (0, 0), (-1, -1), True)
    ]))

    elements.append(table)

    # Footer
    elements.append(Paragraph(f"Comments: {comments}", normal_style))
    elements.append(Spacer(1, 12))
    elements.append(
        Paragraph(f"Mashauri building dispatch ticket {str(tid).zfill(7)}",
                  styles['Italic']))

    doc.build(elements)
    buf.seek(0)
    return buf, str(tid).zfill(7)


def calculate_time_fields(dispatch):
    """
    Calculate time-related fields for a dispatch.
    """
    time_remaining = dispatch.sla_timer - now()
    dispatch.time_remaining = time_remaining

    if dispatch.status == 'Closed':
        time_since_closed = now() - dispatch.sla_timer
        if time_since_closed > timedelta(0):
            days = time_since_closed.days
            hours = time_since_closed.seconds // 3600
            minutes = (time_since_closed.seconds % 3600) // 60
            dispatch.closed_time_display = (
                f"Closed {days} days {hours} hours {minutes} minutes ago")
        else:
            dispatch.closed_time_display = "Closed just now"
    else:
        dispatch.closed_time_display = None

    if time_remaining < timedelta(0):
        time_after_expiration = abs(time_remaining)
        days = time_after_expiration.days
        hours = time_after_expiration.seconds // 3600
        minutes = (time_after_expiration.seconds % 3600) // 60
        dispatch.time_remaining_display = (
            f"Expired {days} days {hours} hours {minutes} minutes ago")
    else:
        days = time_remaining.days
        hours = time_remaining.seconds // 3600
        minutes = (time_remaining.seconds % 3600) // 60
        dispatch.time_remaining_display = (
            f"{days} days {hours} hours {minutes} minutes")

    return dispatch


def calculate_status_counts(dispatches):
    """
    Calculate status counts for dispatches.
    """
    status_counts = {'Hold': 0, 'Progress': 0, 'Closed': 0, 'breached': 0}

    for dispatch in dispatches:
        if dispatch.time_remaining < timedelta(0):
            status_counts['breached'] += 1
        status_counts[dispatch.status] += 1

    return status_counts


def get_filtered_dispatches(category_field, category_value, status=None):
    """
    Filter dispatches based on user category and status.
    """
    if not category_field and not category_value:
        if status == 'Closed':
            return Dispatch.objects.filter(
                status='Closed').order_by('-closed_at')
        elif status == 'Progress':
            return Dispatch.objects.filter(status='Progress')
        elif status == 'Hold':
            return Dispatch.objects.filter(status='Hold')
        else:
            return Dispatch.objects.all()
    filters = {category_field: category_value}
    if status:
        filters['status'] = status
    return Dispatch.objects.filter(**filters).order_by('-sla_timer')


def get_search_results(q, fields):
    """
    Perform search if a query is provided.
    """
    if q:
        search_query = DispatchDocument.search().query(
            "multi_match", query=q, fields=fields
        )
        dispatch_ids = [dispatch.id for dispatch in search_query.to_queryset()]
        return Dispatch.objects.filter(id__in=dispatch_ids), True
    return None, False


def build_context(user, category_field, category_value, request):
    """
    Build a context dictionary for the dashboard views.
    """
    all_dispatches = get_filtered_dispatches(category_field, category_value)
    closed_dispatches = get_filtered_dispatches(
        category_field, category_value, 'Closed')
    closed_dispatches_count = closed_dispatches.count()
    closed_dispatches_json = serialize('json', closed_dispatches)

    active_dispatches = get_filtered_dispatches(
        category_field, category_value, 'Progress').count()
    expired_dispatches = all_dispatches.filter(
        sla_timer__lte=now(), status='Progress').count()

    q = request.GET.get("q")
    search_dispatches, searched = get_search_results(
        q, ["msp", "client_name", "building_name", "escalation_type"])
    if search_dispatches:
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
        'searched': searched
    }
    return data


def extract_dispatch_data(request):
    """Extract relevant data from the request."""
    return {
        'building_name': request.POST.get('building_name'),
        'building_id': request.POST.get('building_id'),
        'coordinates': request.POST.get('coordinates'),
        'msp': request.POST.get('msp'),
        'fdp': request.POST.get('fdp'),
        'rp': request.POST.get('rp'),
        'escalation_type': request.POST.get('escalation_type'),
        'client_name': request.POST.get('client_name'),
        'client_id': request.POST.get('client_id'),
        'comments': request.POST.get('comments'),
        'dispatch_image': request.FILES.get('dispatch_image')
    }


def save_dispatch(data, user):
    """Save the Dispatch instance."""
    dispatch = Dispatch(
        building_name=data['building_name'],
        building_id=data['building_id'],
        msp=data['msp'],
        fdp=data['fdp'],
        rp=data['rp'],
        escalation_type=data['escalation_type'],
        comments=data['comments'],
        coordinates=data['coordinates'],
        client_id=data['client_id'],
        client_name=data['client_name'],
        user=user
    )
    dispatch.save()
    return dispatch


def save_dispatch_image(dispatch, dispatch_image):
    """Save dispatch image to the database."""
    file_path = default_storage.save(
        dispatch_image.name, ContentFile(dispatch_image.read()))
    DispatchImage.objects.create(
        dispatch=dispatch,
        image=file_path,
        image_type='creation'
    )


def create_ticket_and_pdf(dispatch, data):
    """Create a ticket and its associated PDF."""
    ticket = Ticket.objects.create(dispatching=dispatch, status='Open')
    pdf_buffer, pdf_id = generate_pdf(
        data['building_name'], data['building_id'], data['msp'], data['fdp'],
        data['escalation_type'], data['comments'], data['coordinates'],
        data['client_name'], data['client_id'], ticket.id
    )
    filename = f"{pdf_id}.pdf"

    _ = default_storage.save(filename, ContentFile(pdf_buffer.getvalue()))
    ticket.name = filename
    ticket.save()
    return pdf_buffer, ticket


def build_escalation_url(request, dispatch_id):
    """Construct the escalation URL."""
    escalation_url = reverse('dispatch_detail', kwargs={'pk': dispatch_id})
    return request.build_absolute_uri(escalation_url)


def determine_email_recipients(msp, fdp, rp):
    """Determine the email recipients based on MSP, FDP, and user role."""
    msp_emails = {
        'Egypro': [
            "fnmc@egypro.com",
            "enterpriseconnectivity@safaricom.co.ke",
            "Tes-pms@safaricom.co.ke", "Fnmc_provisioning@egypro.com"],
        'Camusat': [
            "noc.kenya@camusat.com",
            "enterpriseconnectivity@safaricom.co.ke",
            "Tes-pms@safaricom.co.ke"],
        'Adrian': [
            "nmc-fiber@adriankenya.com",
            "enterpriseconnectivity@safaricom.co.ke",
            "Tes-pms@safaricom.co.ke"],
        'Kinde': [
            "noc@kinde.co.ke",
            "enterpriseconnectivity@safaricom.co.ke",
            "Tes-pms@safaricom.co.ke"],
        'Fireside': [
            "noc@fireside.africa",
            "enterpriseconnectivity@safaricom.co.ke",
            "Tes-pms@safaricom.co.ke"],
        'Soliton': [
            "noc@soliton.co.ke",
            "enterpriseconnectivity@safaricom.co.ke",
            "Tes-pms@safaricom.co.ke"]
    }
    fdp_emails = {
        'Fireside': ["fireside@safaricom.co.ke"],
        'Broadcom': ["broadcom@safaricom.co.ke"],
        'Optimax': ["optimax@safaricom.co.ke"],
        'BTN': ["btn@safaricom.co.ke", "noc@btn-solutions.co.ke"],
        'Com21': ["Com21@Safaricom.co.ke"],
        'Bens': ["bens.safaricom.co.ke"],
        'Geonet': ["geonettechnologies@safaricom.co.ke"]
    }

    rp_emails = {
        'Powergen': ["pmwangi@powergentechnologies.co.ke"],
        'Hatikvah': ["valary@hatikvah.co.ke"],
        'Fireside': ["linah@fireside.africa"],
        'Kinde': ["philip@kinde.co.ke"],
        'Camusat': ["cchenge@camusat.com, rkhamati@camusat.com"],
        'Techminds': ["nkarambu@techminds.co.ke"],

        'Egypro': ["Josephine_Kathure@egypro.com"],
        'Optimax': ["Mitchel.Ingato@optimaxgroup.co.ke"],
        'Pavicon': ["philip.omoiti@pavicon.co.ke"],

        'Adrian': ["Winnie.kamweti@adriankenya.com"],
        'Tetranet': ["joe.warutere@tetranet.co.ke"],
        'Acl': ["jane@aclkenya.co.ke"],
        'Quavatel': ["Florence.njoki@quavatel.com"],
    }

    recipients = msp_emails.get(msp, [])
    if fdp in fdp_emails:
        recipients += fdp_emails[fdp]
    if rp in rp_emails:
        recipients += rp_emails[rp]
    return recipients


def send_notification_email(
        escalation_type, recipients,
        building_name, client_name,
        msp, rp, full_url, attachment_path):
    subject = None
    message = None

    if escalation_type == 'Interception':
        subject = f"interception request: \"{building_name}\" "
        message = f"Please note that {building_name} Has been escalate to \"{msp}\" for interception."
    else:
        """Send an email notification."""
        subject = (
            f"Core Provisioning Request \"{client_name}\" Located at "
            f"\"{building_name}\"."
            if escalation_type == 'Reactive' else
            f"Core Provisioning Request: \"{building_name}\"."
        )
        message = (
            f"Please note that \"{client_name}\" Located at \"{building_name}\" "
            f"has been escalated to \"{msp}\" for core provisioning.\n\n"
            f"Click here for details: {full_url}.\n\nMashauri |Core."
        )
    print(subject, message, recipients)
    send_mail(recipients, subject, message, attachment_path)


def prepare_email_details(dispatch, comment_content, full_url, action):
    """Prepare the email subject and message based on the action type."""
    if action == "update":
        subject = (
            f"Core Provisioning Updates \"{dispatch.client_name}\" "
            f"Located at \"{dispatch.building_name}\"."
        )
        message = (
            f"Please note that Core Provisioning Request for "
            f"\"{dispatch.client_name}\" located at "
            f"\"{dispatch.building_name}\" "
            f"has been updated with the following comments:\n\n"
            f"\"{comment_content}\".\n\n"
            f"Click here for details: {full_url}.\n\nMashauri | Core."
        )
    elif action == "close":
        if dispatch.escalation_type == "Interception":
            subject = (
                f"Core Interception for \"{dispatch.client_name}\" "
                f"Located at \"{dispatch.building_name}\" has been closed."
            )
            
            message = (
                f"Please note that Interception Request for "
                f"\"{dispatch.building_name}\" "
                f"has been closed with the following comments:\n\n"
                f"\"{comment_content}\".\n\n"
                f"Click here for details: {full_url}.\n\nMashauri | Core."
            )
            return subject, message
        subject = (
            f"Core Provisioning for \"{dispatch.client_name}\" "
            f"Located at \"{dispatch.building_name}\" has been closed."
        )
        message = (
            f"Please note that Core Provisioning Request "
            f"\"{dispatch.client_name}\" located at "
            f"\"{dispatch.building_name}\" "
            f"has been closed with the following comments:\n\n"
            f"\"{comment_content}\".\n\n"
            f"Click here for details: {full_url}.\n\nMashauri | Core."
        )
        return subject, message
    elif action == "reassign":
        subject = (
            f"Core Provisioning: \"{dispatch.building_name}\" "
            f"has been reassigned."
        )
        message = (
            f"Please note that Core Provisioning for "
            f"\"{dispatch.client_name}\" located at "
            f" \"{dispatch.building_name}\" "
            f"has been reassigned.\n\n"
            f"Click here for details: {full_url}.\n\nMashauri | Core."
        )
    else:
        raise ValueError("Invalid action type provided for email preparation.")

    return subject, message


# Handler for adding comments
def handle_comment_update(request, dispatch, user, email_recipients, full_url):
    comment_content = request.POST['comment']
    dispatch_image = request.FILES.get('comment_image')
    if dispatch_image:
        save_dispatch_image(dispatch, dispatch_image)

    comment = Comment.objects.create(
        dispatch=dispatch,
        user=user,
        content=comment_content
    )
    comment.save()

    subject, message = prepare_email_details(
        dispatch, comment_content, full_url, "update")
    send_mail(email_recipients, subject, message)

    return redirect('dispatch_detail', pk=dispatch.pk)


# Handler for closing dispatch
def handle_dispatch_closing(request, dispatch, email_recipients, full_url):
    comment_content = request.POST.get('comment')
    dispatch_image = request.FILES.get('close_image')
    if dispatch_image:
        save_dispatch_image(dispatch, dispatch_image)

    dispatch.status = "Closed"
    dispatch.closed_at = now()
    dispatch.save()

    comment = Comment.objects.create(
        dispatch=dispatch,
        user=request.user,
        content=comment_content
    )
    comment.save()

    messages.success(
        request,
        f"Dispatch for {dispatch.building_name} "
        f"(ID: {dispatch.building_id}) has been closed.")

    subject, message = prepare_email_details(
        dispatch, comment_content,
        full_url, "close")
    print(email_recipients)
    send_mail(email_recipients, subject, message)

    return render(request, 'mashauri/success_deletion.html', {})


# Handler for reassigning dispatch
def handle_dispatch_reassignment(
        request, dispatch, email_recipients, full_url):
    selected_value = request.POST.get('assignment')
    if selected_value != 'ENTERPRISE CONNECTIVITY':
        dispatch.msp = selected_value
    else:
        dispatch.msp = None
    dispatch.reassign_to = selected_value
    dispatch.save()

    subject, message = prepare_email_details(
        dispatch, None, full_url, "reassign")
    send_mail(email_recipients, subject, message)

    return render(request, 'mashauri/success_reassignment.html', {})


'''SENDING SCHEDULES EMAILS'''


def generate_pdf_mailed(dispatches, filename, title):
    buffer = BytesIO()

    # Create the PDF document in landscape mode
    doc = SimpleDocTemplate(
        buffer, pagesize=landscape(letter), rightMargin=36,
        leftMargin=36, topMargin=36, bottomMargin=36)

    # Create a custom stylesheet for text formatting
    styles = getSampleStyleSheet()
    header_style = styles['Heading1']
    header_style.fontName = "Times-Roman"  # Use a serif font
    header_style.fontSize = 16  # Larger font for title
    header_style.alignment = 1  # Center align the heading
    header_style.spaceAfter = 12  # Add some spacing after the title

    # Normal text style
    normal_style = styles['Normal']
    normal_style.fontName = "Times-Roman"  # Use a serif font
    normal_style.fontSize = 8  # Set body font size to 8

    # Prepare table data with headers
    data = [
        ["Client Name", "CI", "Building Name", "Escalation Type", "MSP"]
    ]

    # Alternate colors for stripes
    stripe_colors = [colors.lightgrey, colors.whitesmoke]

    # Add rows for the dispatches
    for dispatch in dispatches:
        row = [
            Paragraph(dispatch.client_name or "N/A", normal_style),
            Paragraph(dispatch.client_id or "N/A", normal_style),
            Paragraph(dispatch.building_name or "N/A", normal_style),
            Paragraph(dispatch.escalation_type or "N/A", normal_style),
            Paragraph(dispatch.msp or "N/A", normal_style),
        ]
        data.append(row)

    # Define column widths
    column_widths = [
        1.8 * inch,
        1.2 * inch,
        1.8 * inch, 1.8 * inch, 1.2 * inch]

    # Create the table
    table = Table(data, colWidths=column_widths)

    # Apply styling to the table
    style = TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # White text for header
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),  # Dark blue header
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center-align all cells
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),  # Grid lines
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),  # Serif font
        ('FONTSIZE', (0, 0), (-1, 0), 10),  # Larger font for header
        ('FONTSIZE', (0, 1), (-1, -1), 8),  # Smaller font for body
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding for header
        ('TOPPADDING', (0, 1), (-1, -1), 8),  # Padding for body rows
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('WORDWRAP', (0, 0), (-1, -1), True),  # Enable word wrapping
    ])

    # Apply striping colors for each row
    for i in range(1, len(data)):
        style.add('BACKGROUND', (0, i), (-1, i), stripe_colors[i % 2])

    # Apply the style to the table
    table.setStyle(style)

    # Add a title at the top of the page
    elements = [Paragraph(title, header_style)]  # Title at the top

    # Build the PDF document with the title and table
    doc.build(elements + [table])

    # Move to the beginning of the buffer to read the generated content
    buffer.seek(0)

    # Return as a ContentFile, including the dynamic filename
    return ContentFile(buffer.read(), name=filename)


def save_contentfile_to_disk(contentfile, filename):
    temp_file = tempfile.NamedTemporaryFile(
        delete=False, suffix=".pdf", mode='wb')
    with open(temp_file.name, 'wb') as f:
        f.write(contentfile.read())
    final_filename = f"{filename}.pdf"
    temp_file.close()
    os.rename(temp_file.name, final_filename)
    return final_filename


def send_escalation_email(start_time, end_time, subject, recipients):
    closed_dispatches = Dispatch.objects.filter(
        closed_at__range=(start_time, end_time))
    expired_dispatches = Dispatch.objects.filter(
        sla_timer__lte=now(), status="Progress")

    if not closed_dispatches.exists() and not expired_dispatches.exists():
        print(
            f"No dispatches to notify for the time window: "
            f"{start_time} - {end_time}.")
        return

    # Generate PDFs for closed and expired dispatches
    closed_pdf = generate_pdf_mailed(
        closed_dispatches, "Closed Mashauri Escalations Report",
        "Closed Mashauri Escalations Report")
    expired_pdf = generate_pdf_mailed(
        expired_dispatches, "Out of SLA Core Provisioning Escalations",
        "Out of SLA Core Provisioning Escalations")

    closed_pdf_path = save_contentfile_to_disk(
        closed_pdf, "dispatch_report_closed")
    expired_pdf_path = save_contentfile_to_disk(
        expired_pdf, "dispatch_report_expired")

    # Send email with both PDFs as attachments
    if not closed_dispatches.exists() and not expired_dispatches.exists():
        print(
            f"No dispatches to notify for the time window: "
            f"{start_time} - {end_time}.")
        return

    # Format the times as per the requested format
    start_time_str = start_time.strftime("%B %d, %Y at %I:%M %p")
    end_time_str = end_time.strftime("%B %d, %Y at %I:%M %p")

    # Construct the message with formatted start and end times
    message = (
        f"The following escalations were updated between "
        f"{start_time_str} and {end_time_str}:\n\n"
    )

    send_mail(
        recipients=recipients,
        subject=subject,
        message=message,
        attachment_path=[closed_pdf_path, expired_pdf_path]
    )
    print(f"Email sent for {subject} covering {start_time} to {end_time}.")


def email_recipients_report():
    return [
        'Com21@Safaricom.co.ke',
        'Tes-pms@safaricom.co.ke', 'bens.safaricom.co.ke',
        'broadcom@safaricom.co.ke',
        'enterpriseconnectivity@safaricom.co.ke',
        'fnmc@egypro.com', 'Fnmc_provisioning@egypro.com',
        'noc@btn-solutions.co.ke',
        'noc@fireside.africa', 'noc@kinde.co.ke', 'noc@soliton.co.ke',
        'noc.kenya@camusat.com',
        'nmc-fiber@adriankenya.com', 'optimax@safaricom.co.ke']


# 9 AM Escalation Email
def schedule_nine_am_emails():
    now_time = now()
    start_time = now_time.replace(
        hour=16,
        minute=1, second=0, microsecond=0) - timedelta(days=1)
    end_time = now_time.replace(
        hour=8, minute=59, second=59, microsecond=0)

    recipients = email_recipients_report()
    send_escalation_email(
        start_time, end_time, "9 AM Escalation Update", recipients)


# 12 Noon Escalation Email
def schedule_twelve_noon_emails():
    now_time = now()
    start_time = now_time.replace(hour=9, minute=0, second=0, microsecond=0)
    end_time = now_time.replace(hour=11, minute=59, second=59, microsecond=0)

    recipients = email_recipients_report()
    send_escalation_email(
        start_time, end_time, "12 Noon Escalation Update", recipients)


# 4 PM Escalation Email
def schedule_four_pm_emails():
    now_time = now()
    start_time = now_time.replace(hour=12, minute=0, second=0, microsecond=0)
    end_time = now_time.replace(hour=15, minute=59, second=59, microsecond=0)

    recipients = email_recipients_report()
    send_escalation_email(
        start_time, end_time, "4 PM Escalation Update", recipients)
