from django.urls import path
from . import views
from management.views import (AppointmentDetailView, LeadDetailView, JobDetailView, PermitDetailView,
AccountDetailView, ArchiveDetailView, ServiceDetailView, InstallCalendarView, EditInstallCalendarView,
InstallerCalendarView, AppointmentCalendarView, EditAppointmentCalendarView, HomePageView)

urlpatterns = [
    path('enter', views.enter_view, name='enter'),
    path('', HomePageView.as_view(), name='index'),
    path('installer_home/', views.installer_home, name='installer-home'),
    path('user_list/', views.users, name='users'),
    path('new_user/', views.new_users, name='new-user'),
    path('user_list/<int:userpk>', views.edit_users, name='edit-user'),
    path('user_list/delete/<int:userpk>', views.delete_users, name='delete-user'),
    path('appointments/', views.appointments, name='appointments'),
    path('new_appointment/', views.new_appointment, name='new-appointment'),
    path('appointments/run/<int:leadpk>', views.send_to_leads_run, name='send-to-leads-run'),
    path('appointments/view/<int:pk>', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('appointments/edit<int:leadpk>', views.edit_appointment, name='edit-appointment'),
    path('appointments/delete/<int:leadpk>', views.delete_appointment, name='delete-appointment'),
    path('appointment_calendar/', AppointmentCalendarView.as_view(), name='appointment-calendar'),
    path('appointment_calendar/edit<int:pk>', EditAppointmentCalendarView.as_view(), name='edit-appointment-calendar'),
    path('install_schedule', InstallCalendarView.as_view(), name='install-schedule'),
    path('install_schedule/edit<int:pk>', EditInstallCalendarView.as_view(), name='edit-install-schedule'),
    path('installer_schedule/<int:pk>', InstallerCalendarView.as_view(), name='installer-schedule'),
    path('leads_run/', views.leads_run, name='leads-run'),
    path('new_lead/', views.new_lead, name='new-lead'),
    path('leads_run/jip/<int:leadpk>', views.send_to_jip, name='send-to-jip'),
    path('leads_run/standard/<int:leadpk>', views.send_to_standard, name='send-to-standard'),
    path('leads_run/view/<int:pk>', LeadDetailView.as_view(), name='lead-detail'),
    path('leads_run/edit<int:leadpk>', views.edit_lead, name='edit-lead'),
    path('confirm_delete_contract/<int:contpk>', views.confirm_delete_cont, name='confirm-delete-cont'),
    path('confirm_delete_cont/delete<int:contpk>', views.delete_contract, name='delete-contract'),
    path('confirm_delete_photo/<int:photopk>', views.confirm_delete_photo, name='confirm-delete-photo'),
    path('confirm_delete_photo/delete<int:photopk>', views.delete_photo, name='delete-photo'),
    path('leads_run/delete/<int:leadpk>', views.delete_lead, name='delete-lead'),
    path('jobs_in_progress/', views.jobs_in_progress, name='jobs-in-progress'),
    path('jobs_in_progress/view/<int:pk>', JobDetailView.as_view(), name='job-detail'),
    path('jobs_in_progress/receivable/<int:leadpk>', views.send_to_receivable, name='send-to-receivable'),
    path('jobs_in_progress/edit<int:leadpk>', views.edit_job, name='edit-job'),
    path('jobs_in_progress/delete/<int:leadpk>', views.delete_job, name='delete-job'),
    path('pending_permits/', views.pending_permits, name='pending-permits'),
    path('pending_permits/edit<int:leadpk>', views.edit_permit, name='edit-permit'),
    path('pending_permits/view/<int:pk>', PermitDetailView.as_view(), name='permit-detail'),
    path('pending_permits/archive/<int:permpk>', views.permit_to_archive, name='permit-to-archive'),
    path('permit_archives/', views.permit_archives, name='permit-archives'),
    path('permit_archives/pending/<int:permpk>', views.permit_to_pending, name='permit-to-pending'),
    path('accounts_receivable/', views.accounts_receivable, name='accounts-receivable'),
    path('accounts_receivable/archive/<int:leadpk>', views.send_to_archive, name='send-to-archive'),
    path('accounts_receivable/view/<int:pk>', AccountDetailView.as_view(), name='account-detail'),
    path('accounts_receivable/edit<int:leadpk>', views.edit_account, name='edit-account'),
    path('archives/', views.archives, name='archives'),
    path('archives/edit<int:leadpk>', views.edit_archive, name='edit-archive'),
    path('archives/view/<int:pk>', ArchiveDetailView.as_view(), name='archive-detail'),
    path('services/', views.services, name='services'),
    path('services/archive/<int:servpk>', views.send_to_service_archive, name='send-to-service-archive'),
    path('new_service/', views.new_service, name='new-service'),
    path('services/view/<int:pk>', ServiceDetailView.as_view(), name='service-detail'),
    path('services/edit<int:servpk>', views.edit_service, name='edit-service'),
    path('services/delete/<int:servpk>', views.delete_service, name='delete-service'),
    path('service_archive/', views.service_archive, name='service-archive'),
    path('service_archive/service/<int:servpk>', views.send_to_service, name='send-to-service'),
    path('project_type/', views.project_type, name='project-type'),
    path('new_project_type/', views.new_project_type, name='new-project-type'),
    path('project_type/<int:typepk>', views.edit_project_type, name='edit-project-type'),
    path('project_type/delete/<int:typepk>', views.delete_project_type, name='delete-project-type'),
    path('my_payroll/', views.my_payroll, name='my-payroll'),
    path('my_payroll/edit<int:paypk>', views.edit_payroll, name='payroll-detail'),
    path('submit_payroll/', views.submit_payroll, name='submit-payroll'),
    path('submit_payroll/installer<int:userid>', views.submit_installer, name='submit-installer'),
    path('submit_payroll/staff<int:userid>', views.submit_staff, name='submit-staff'),
    path('submit_payroll/sales<int:userid>', views.submit_sales, name='submit-sales'),
    path('payroll_to_process/', views.payroll_to_process, name='payroll-to-process'),
    path('confirm_submit_to_process/<int:paypk>', views.confirm_submit_to_process, name='confirm-submit-to-process'),
    path('payroll_to_process/edit<int:paypk>', views.edit_process_payroll, name='edit-process-payroll'),
    path('payroll_to_process/to_archive<int:paypk>', views.payroll_to_archive, name='payroll-to-archive'),
    path('delete_payroll<int:paypk>', views.delete_payroll, name='delete-payroll'),
    path('payroll_archive/', views.payroll_archive, name='payroll-archive')
]