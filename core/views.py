from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import (
    TrainingSession, Lead, Client, Quote, CallLog, CallScript, ElearningModule, Learner,
    Trainer, Reminder, Document, Invoice
)
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import csv
from chartjs.views.lines import BaseLineChartView

def is_commercial(user):
    return user.groups.filter(name='Commerciaux').exists()

def is_trainer(user):
    return user.groups.filter(name='Formateurs').exists()

def is_admin(user):
    return user.is_staff or user.is_superuser

def home(request):
    sessions = TrainingSession.objects.all()
    return render(request, 'home.html', {'sessions': sessions})

@login_required
@user_passes_test(is_commercial)
def commercial_dashboard(request):
    leads = Lead.objects.filter(assigned_to=request.user)
    quotes = Quote.objects.filter(created_by=request.user)
    call_logs = CallLog.objects.filter(created_by=request.user).order_by('-date')[:5]
    scripts = CallScript.objects.all()
    reminders = Reminder.objects.filter(lead__assigned_to=request.user, sent=False)
    context = {
        'leads': leads,
        'quotes': quotes,
        'call_logs': call_logs,
        'scripts': scripts,
        'reminders': reminders,
    }
    return render(request, 'commercial/dashboard.html', context)

@login_required
@user_passes_test(is_commercial)
def add_lead(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        company = request.POST.get('company', '')
        status = request.POST.get('status', 'NEW')
        lead = Lead.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            company=company,
            status=status,
            assigned_to=request.user
        )
        if email:
            Reminder.objects.create(
                lead=lead,
                subject="Suivi de votre demande",
                message="Bonjour, nous vous contactons suite à votre intérêt pour nos formations...",
                scheduled_date=timezone.now() + timezone.timedelta(days=3)
            )
        messages.success(request, 'Prospect ajouté avec succès.')
        return redirect('commercial_dashboard')
    return render(request, 'commercial/add_lead.html')

@login_required
@user_passes_test(is_commercial)
def add_call_log(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    if request.method == 'POST':
        duration = request.POST.get('duration')
        notes = request.POST.get('notes')
        outcome = request.POST.get('outcome')
        CallLog.objects.create(
            lead=lead,
            duration=duration,
            notes=notes,
            outcome=outcome,
            created_by=request.user
        )
        messages.success(request, 'Appel enregistré.')
        return redirect('commercial_dashboard')
    return render(request, 'commercial/add_call_log.html', {'lead': lead})

@login_required
def learner_portal(request):
    if not request.user.is_authenticated:
        return redirect('login')
    learner = Learner.objects.filter(email=request.user.email).first()
    if not learner:
        return render(request, 'learner/portal.html', {'error': 'Aucun apprenant associé.'})
    sessions = learner.sessions.all()
    modules = ElearningModule.objects.filter(session__in=sessions)
    context = {
        'learner': learner,
        'sessions': sessions,
        'modules': modules,
    }
    return render(request, 'learner/portal.html', context)

@login_required
@user_passes_test(is_trainer)
def trainer_portal(request):
    trainer = Trainer.objects.filter(email=request.user.email).first()
    if not trainer:
        return render(request, 'trainer/portal.html', {'error': 'Aucun formateur associé.'})
    sessions = TrainingSession.objects.filter(trainer=trainer)
    context = {
        'trainer': trainer,
        'sessions': sessions,
    }
    return render(request, 'trainer/portal.html', context)

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_leads = Lead.objects.count()
    total_sessions = TrainingSession.objects.count()
    total_invoices = Invoice.objects.count()
    context = {
        'total_leads': total_leads,
        'total_sessions': total_sessions,
        'total_invoices': total_invoices,
    }
    return render(request, 'admin/dashboard.html', context)

class LeadStatusChart(BaseLineChartView):
    def get_labels(self):
        return ['Nouveau', 'Contacté', 'Qualifié', 'Perdu']

    def get_data(self):
        return [
            Lead.objects.filter(status='NEW').count(),
            Lead.objects.filter(status='CONTACTED').count(),
            Lead.objects.filter(status='QUALIFIED').count(),
            Lead.objects.filter(status='LOST').count(),
        ]

@login_required
@user_passes_test(is_admin)
def generate_qr_code(request, session_id):
    session = get_object_or_404(TrainingSession, id=session_id)
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"https://your-render-url.com/attendance/{session_id}/")
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    file_name = f"qr_{session.title}.png"
    file_content = ContentFile(buffer.getvalue())
    
    document = Document.objects.create(
        session=session,
        doc_type='EMARGEMENT',
        file=file_name
    )
    document.file.save(file_name, file_content)
    return redirect('admin_dashboard')

@login_required
def mark_attendance(request, session_id):
    session = get_object_or_404(TrainingSession, id=session_id)
    if request.method == 'POST':
        learner_id = request.POST.get('learner_id')
        learner = get_object_or_404(Learner, id=learner_id)
        document = Document.objects.get(session=session, doc_type='EMARGEMENT')
        document.content += f"{learner} présent le {timezone.now()}\n"
        document.save()
        messages.success(request, 'Présence enregistrée.')
    return render(request, 'attendance.html', {'session': session})

@login_required
@user_passes_test(is_admin)
def export_csv(request, model_name):
    if model_name == 'learners':
        queryset = Learner.objects.all()
        filename = 'learners.csv'
        fields = ['first_name', 'last_name', 'email', 'phone', 'created_at']
    elif model_name == 'leads':
        queryset = Lead.objects.all()
        filename = 'leads.csv'
        fields = ['first_name', 'last_name', 'email', 'phone', 'company', 'status', 'created_at']
    else:
        return HttpResponse(status=404)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(fields)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in fields])
    return response

@login_required
@user_passes_test(is_commercial)
def send_reminder(request, reminder_id):
    reminder = get_object_or_404(Reminder, id=reminder_id)
    if not reminder.sent:
        send_mail(
            reminder.subject,
            reminder.message,
            settings.DEFAULT_FROM_EMAIL,
            [reminder.lead.email],
            fail_silently=False,
        )
        reminder.sent = True
        reminder.save()
        messages.success(request, 'Relance envoyée.')
    return redirect('commercial_dashboard')
