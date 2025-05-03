from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class CustomField(models.Model):
    name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=50)
    model_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.model_name})"

class Learner(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    custom_fields = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Trainer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    specialty = models.CharField(max_length=200, blank=True)
    custom_fields = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class TrainingSession(models.Model):
    title = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True)
    learners = models.ManyToManyField(Learner, related_name='sessions')
    custom_fields = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Document(models.Model):
    DOCUMENT_TYPES = [
        ('CONVENTION', 'Convention'),
        ('ATTESTATION', 'Attestation'),
        ('EMARGEMENT', 'Feuille d’émargement'),
    ]
    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE)
    doc_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='documents/', blank=True)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.doc_type} - {self.session.title}"

class Evaluation(models.Model):
    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE)
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE)
    satisfaction_score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Évaluation {self.session.title} - {self.learner}"

class Invoice(models.Model):
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='invoices')
    session = models.ForeignKey(TrainingSession, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    issued_date = models.DateField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    custom_fields = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Facture {self.id} - {self.client}"

class PedagogicalFinancialReport(models.Model):
    year = models.IntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"BPF {self.year}"

class ElearningModule(models.Model):
    title = models.CharField(max_length=200)
    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name='modules')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Quiz(models.Model):
    module = models.ForeignKey(ElearningModule, on_delete=models.CASCADE, related_name='quizzes')
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quiz {self.module.title}"

class Lead(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'Nouveau'),
        ('CONTACTED', 'Contacté'),
        ('QUALIFIED', 'Qualifié'),
        ('LOST', 'Perdu'),
    ]
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='leads')
    custom_fields = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.status})"

class Client(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='clients')
    custom_fields = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Quote(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('ACCEPTED', 'Accepté'),
        ('REJECTED', 'Refusé'),
    ]
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='quotes')
    session = models.ForeignKey(TrainingSession, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    content = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Devis {self.id} - {self.lead}"

class CallLog(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='call_logs')
    date = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True)
    outcome = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Appel {self.lead} - {self.date}"

class CallScript(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Reminder(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='reminders')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    scheduled_date = models.DateTimeField()
    sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Relance pour {self.lead} - {self.scheduled_date}"
