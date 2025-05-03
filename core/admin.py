from django.contrib import admin
from .models import (
    Learner, Trainer, TrainingSession, Document, Evaluation, CustomField,
    Invoice, PedagogicalFinancialReport, ElearningModule, Quiz,
    Lead, Client, Quote, CallLog, CallScript, Reminder
)
from django.contrib.auth.models import Group, User
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def assign_group(sender, instance, created, **kwargs):
    if created:
        if 'commerciaux' in instance.groups.values_list('name', flat=True):
            commercial_group, _ = Group.objects.get_or_create(name='Commerciaux')
            instance.groups.add(commercial_group)
        if 'formateurs' in instance.groups.values_list('name', flat=True):
            trainer_group, _ = Group.objects.get_or_create(name='Formateurs')
            instance.groups.add(trainer_group)

class LearnerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('created_at',)

class TrainerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'specialty')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('specialty',)

class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'trainer')
    search_fields = ('title',)
    list_filter = ('start_date', 'trainer')
    filter_horizontal = ('learners',)

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('doc_type', 'session', 'created_at')
    search_fields = ('doc_type', 'session__title')
    list_filter = ('doc_type',)

class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('session', 'learner', 'satisfaction_score', 'created_at')
    search_fields = ('session__title', 'learner__last_name')
    list_filter = ('satisfaction_score',)

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('client', 'amount', 'issued_date', 'paid')
    search_fields = ('client__name',)
    list_filter = ('paid', 'issued_date')

class PedagogicalFinancialReportAdmin(admin.ModelAdmin):
    list_display = ('year', 'created_at')
    search_fields = ('year',)

class ElearningModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'session', 'created_at')
    search_fields = ('title', 'session__title')

class QuizAdmin(admin.ModelAdmin):
    list_display = ('question', 'module', 'created_at')
    search_fields = ('question', 'module__title')

class LeadAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'status', 'assigned_to')
    search_fields = ('first_name', 'last_name', 'email', 'company')
    list_filter = ('status', 'assigned_to')
    list_editable = ('status',)

class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'assigned_to')
    search_fields = ('name', 'email')
    list_filter = ('assigned_to',)

class QuoteAdmin(admin.ModelAdmin):
    list_display = ('lead', 'amount', 'status', 'created_at')
    search_fields = ('lead__first_name', 'lead__last_name')
    list_filter = ('status',)

class CallLogAdmin(admin.ModelAdmin):
    list_display = ('lead', 'date', 'outcome', 'created_by')
    search_fields = ('lead__first_name', 'lead__last_name', 'outcome')
    list_filter = ('date', 'created_by')

class CallScriptAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)

class ReminderAdmin(admin.ModelAdmin):
    list_display = ('lead', 'subject', 'scheduled_date', 'sent')
    search_fields = ('lead__first_name', 'lead__last_name', 'subject')
    list_filter = ('sent', 'scheduled_date')

admin.site.register(Learner, LearnerAdmin)
admin.site.register(Trainer, TrainerAdmin)
admin.site.register(TrainingSession, TrainingSessionAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Evaluation, EvaluationAdmin)
admin.site.register(CustomField)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(PedagogicalFinancialReport, PedagogicalFinancialReportAdmin)
admin.site.register(ElearningModule, ElearningModuleAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Lead, LeadAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Quote, QuoteAdmin)
admin.site.register(CallLog, CallLogAdmin)
admin.site.register(CallScript, CallScriptAdmin)
admin.site.register(Reminder, ReminderAdmin)
