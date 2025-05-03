from django.urls import path
from . import views
from .views import LeadStatusChart

urlpatterns = [
    path('', views.home, name='home'),
    path('commercial/', views.commercial_dashboard, name='commercial_dashboard'),
    path('commercial/add-lead/', views.add_lead, name='add_lead'),
    path('commercial/add-call-log/<int:lead_id>/', views.add_call_log, name='add_call_log'),
    path('commercial/send-reminder/<int:reminder_id>/', views.send_reminder, name='send_reminder'),
    path('learner/', views.learner_portal, name='learner_portal'),
    path('trainer/', views.trainer_portal, name='trainer_portal'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/chart/lead-status/', LeadStatusChart.as_view(), name='lead_status_chart'),
    path('admin/generate-qr/<int:session_id>/', views.generate_qr_code, name='generate_qr_code'),
    path('attendance/<int:session_id>/', views.mark_attendance, name='mark_attendance'),
    path('admin/export/<str:model_name>/', views.export_csv, name='export_csv'),
]
