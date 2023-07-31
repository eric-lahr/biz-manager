from django.shortcuts import render, redirect, get_object_or_404
from apps.core.models import (ProjectType, Customer, Lead, SourceGroup, ProjectGroup,
Pictures, Contracts, JobStatus, Permit, Installation, Payment, Message, EntryLog, Services,
Installer_Payroll, Payroll, Staff_Payroll, Sales_Payroll, Employee_Documents, Employee_Files)
from apps.core.forms import (DashboardForm, NewUserForm, NewProjectTypeForm, NewAppointmentForm,
SortLeadsRunForm, NewLeadForm, SortJIPForm, SortAccountsForm, EditJobForm, EditPermitForm,
SortArchivesForm, EditAccountForm, ServiceForm, InstallerForm, StaffForm, SalesForm, InstallAppointmentForm,
SelectInstallerForm, EditAppointmentCalendarForm, SortPayrollForm, SortPayProcessForm, SalesFormSet,
JobSearchForm, SalespersonPayEditForm, SalesPayEditForm, SalesEditFormSet)
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.views.generic.list import ListView
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.template import RequestContext
from datetime import datetime, date, time, timedelta
from django.views.generic.detail import DetailView
from django.contrib import messages
from django.contrib.messages import get_messages
from django.utils.http import is_safe_url
from django.db.models import Q
from django.utils.safestring import mark_safe
from .utils import (Calendar, EditCalendar, InstallerCalendar, AppointmentCalendar,
EditAppointmentCalendar)
import calendar
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.handlers import exception

# Create your views here.

@login_required
def enter_view(request):
    if request.user.groups.filter(name='installer'):
        return redirect('installer-home')
    else:
        return redirect('index')

class HomePageView(LoginRequiredMixin, generic.View):
    template_name = 'home.html'

    def get_dashboard_messages(self):
        dash = Message.objects.all().order_by('-datetime')
        return dash

    def get_entry_logs(self):
        events = EntryLog.objects.all()
        return events

    def get_context_data(self, **kwargs):
        dash = self.get_dashboard_messages()
        if dash.count() != 0:
            kwargs['dash'] = dash
        if 'dash_form' not in kwargs:
            kwargs['dash_form'] = DashboardForm()
        if 'search_form' not in kwargs:
            kwargs['search_form'] = JobSearchForm()
        events = self.get_entry_logs()
        kwargs['events'] = events

        return kwargs

    def get(self, request, *args, **kwargs):
        dash = self.get_dashboard_messages()
        if dash.count() != 0:
            kwargs['dash'] = dash
        if 'dash_form' not in kwargs:
            kwargs['dash_form'] = DashboardForm()
        if 'search_form' not in kwargs:
            kwargs['search_form'] = JobSearchForm()
        events = self.get_entry_logs()
        kwargs['events'] = events

        context = kwargs
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        ctxt = {}
        if 'dash' in request.POST:
            dash_form = DashboardForm(request.POST)
            postuser = User.objects.get(username=request.user.username)
            if dash_form.is_valid():
                model_instance = dash_form.save(commit=False)
                model_instance.datetime = timezone.now()
                model_instance.user_id = postuser
                model_instance.save()
                return redirect('index')
            else:
                ctxt['dash_form'] = dash_form

        elif 'search' in request.POST:
            search_form = JobSearchForm(request.POST)
            if search_form.is_valid():
                first_name = search_form.cleaned_data['first_name']               
                last_name = search_form.cleaned_data['last_name']               
                address = search_form.cleaned_data['address']               
                city = search_form.cleaned_data['city']
                state = search_form.cleaned_data['state']               
                phone_number = search_form.cleaned_data['phone_number']               
                cross_streets = search_form.cleaned_data['cross_streets']               
                project_notes = search_form.cleaned_data['project_notes']               
                pro_t = search_form.cleaned_data['project_type']               
                seller = search_form.cleaned_data['salesperson']

                if pro_t:
                    pt = ProjectType.objects.get(pk=pro_t)
                    customer_list = Lead.objects.filter(project_type__proj_type__contains=pt)
                else:
                    customer_list = Lead.objects.all()

                if first_name:
                    customer_list = customer_list.filter(client_id__name__icontains=first_name)
                if last_name:
                    customer_list = customer_list.filter(client_id__last_name__icontains=last_name)
                if address:
                    customer_list = customer_list.filter(Q(client_id__address__icontains=address) |
                                                         Q(client_id__address1__icontains=address))
                if city:
                    customer_list = customer_list.filter(client_id__city__icontains=city)
                if state:
                    customer_list = customer_list.filter(client_id__state__icontains=state)
                if phone_number:
                    customer_list = customer_list.filter(Q(client_id__home_phone__icontains=phone_number) |
                                                         Q(client_id__cell_phone__icontains=phone_number) |
                                                         Q(client_id__fax_number__icontains=phone_number))
                if cross_streets:
                    customer_list = customer_list.filter(client_id__nmc_street__icontains=cross_streets)
                if project_notes:
                    customer_list = customer_list.filter(project_notes__icontains=project_notes)
                if seller:
                    customer_list = customer_list.filter(salesperson=seller)

                context = {
                    'customer_list': customer_list
                }

                return render(request, 'results.html', context)

            else:
                ctxt['search_form'] = search_form

        return render(request, self.template_name, self.get_context_data(**ctxt))

@login_required
def installer_home(request):
    inst_jobs = Installation.objects.filter(
        Q(job__lead_status='4') | Q(job__lead_status='5'),
        installer=request.user.id
    ).order_by('-install_schedule')

    paginator = Paginator(inst_jobs, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        job = paginator.page(page)
    except(EmptyPage, InvalidPage):
        job = paginator.page(paginator.num_pages)

    context = {
        'job': job
    }

    return render(request, 'installer_home.html', context=context)

@login_required
def users(request):
    user_list = User.objects.filter(is_staff=False).order_by('last_name')

    paginator = Paginator(user_list, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        usr = paginator.page(page)
    except(EmptyPage, InvalidPage):
        usr = paginator.page(paginator.num_pages)

    context = {
        'usr': usr
    }

    return render(request, 'user_list.html', context=context)

@login_required
def new_users(request):
    if request.method == 'POST':

        form = NewUserForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            user_type = form.cleaned_data['user_type']

            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.save() 

            user.groups.set([user_type])

            current_user = User.objects.get(username=request.user.username)
            new_entry_log = EntryLog(user_id=current_user,
                                     action="{} created a user account for {}".format(
                                         current_user.username,
                                         user.first_name+' '+user.last_name
                                     ),
                                     entry_date=timezone.now())
            new_entry_log.save()

            return redirect('users')

    else:
        form = NewUserForm()

    context = {
        'form': form
    }

    return render(request, 'new_user.html', context)

@login_required
def edit_users(request, userpk):
    user = User.objects.get(pk = userpk)
    if request.method == 'POST':
        pd = user.password
        form = NewUserForm(request.POST)
        if 'activebox' in request.POST:
            user.is_active=True
        else:
            user.is_active=False
        form.fields['password'].required = False
        form.fields['confirm'].required = False
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            user_type = form.cleaned_data['user_type']
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            if password != '':
                user.set_password(password)
            user.email = email
            user.save()

            user.groups.set([user_type])

            current_user = User.objects.get(username=request.user.username)
            new_entry_log = EntryLog(user_id=current_user,
                                     action="{} edited the user account for {}".format(
                                         current_user.username,
                                         user.first_name+' '+user.last_name
                                     ),
                                     entry_date=timezone.now())
            new_entry_log.save()


            return redirect('users')

    else:
        all_groups = user.groups.values_list('name', flat=False)
        groupchoice = '1'
        for gr in all_groups:
            if gr[0] == 'installer':
                groupchoice = '2'
            if gr[0] == 'admin':
                groupchoice = '1'
            if gr[0] == 'salesperson':
                groupchoice = '3'
            if gr[0] == 'staff':
                groupchoice = '4'

        form = NewUserForm(initial={ 'first_name':user.first_name,
                                     'last_name':user.last_name,
                                     'username':user.username,
                                     'password':user.password,
                                     'confirm':user.password,
                                     'email':user.email,
                                     'user_type':groupchoice})
        form.fields['password'].required = False
        form.fields['confirm'].required = False

    context = {
        'form': form,
        'user': user
    }

    return render(request, 'edit_user.html', context)

@login_required
def delete_users(request, userpk):  
    user = User.objects.get(pk = userpk)

    if request.method == "POST":
        g = user.groups.all()
        for gr in g:
            gr.user_set.remove(user)

        current_user = User.objects.get(username=request.user.username)
        new_entry_log = EntryLog(user_id=current_user,
                                    action="{} deleted {}'s user account.".format(
                                        current_user.username,
                                        user.first_name+' '+user.last_name
                                    ),
                                    entry_date=timezone.now())
        new_entry_log.save()
        user.delete()

        return redirect('users')

    context = {
        'user': user
    }

    return render(request, 'user_confirm.html', context)

@login_required
def appointments(request):
    appointment_list = Lead.objects.filter(lead_status='6').order_by('appointment_date', 'appointment_time')

    paginator = Paginator(appointment_list, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        apt = paginator.page(page)
    except(EmptyPage, InvalidPage):
        apt = paginator.page(paginator.num_pages)

    context = {
        'apt': apt
    }

    return render(request, 'appointments.html', context)

@login_required
def send_to_leads_run(request, leadpk):
    ran = Lead.objects.get(pk=leadpk)
    back = False
    returnURL = '../'

    if ran.lead_status == '6':
        returnURL = 'appointments'
    elif ran.lead_status == '4':
        returnURL = 'accounts-receivable'
        back = True
    elif ran.lead_status == '5':
        returnURL = 'jobs-in-progress'
        back = True

    if request.method == "POST":

        ran.lead_status = 2
        if not ran.lead_cur_status:
            ran.lead_cur_status = None
        ran.save()

        current_user = User.objects.get(username=request.user.username)
        new_entry_log = EntryLog(user_id=current_user,
                                    action="{} sent the appointment with {} to leads run.".format(
                                        current_user.username,
                                        ran.client_id
                                    ),
                                    lead=ran,
                                    entry_date=timezone.now())
        new_entry_log.save()

        return redirect(returnURL)

    context = {
        'back': back,
        'ran': ran
    }

    return render(request, 'send_to_leads_run.html', context)

class AppointmentDetailView(LoginRequiredMixin, DetailView):
    model = Lead
    template_name = 'appointment_detail.html'

    def get_context_data(self, **kwargs):
        context = super(AppointmentDetailView, self).get_context_data(**kwargs)
        return context

@login_required
def new_appointment(request):
    if request.method == 'POST':

        form = NewAppointmentForm(request.POST, request.FILES)

        form.fields['address1'].required = False
        form.fields['state'].required = False
        form.fields['gate_code'].required = False
        form.fields['nmc_street'].required = False
        form.fields['home_phone'].required = False
        form.fields['cell_phone'].required = False
        form.fields['email'].required = False
        form.fields['detailed_instr'].required = False
        form.fields['found_us'].required = False
        form.fields['salesperson'].required = False
        form.fields['contracts'].required = False
        form.fields['images'].required = False
        form.fields['date'].required = False

        if form.is_valid():
            name = form.cleaned_data['name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            address1 = form.cleaned_data['address1']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zip_code = form.cleaned_data['zip_code']
            gate_code = form.cleaned_data['gate_code']
            nmc_street = form.cleaned_data['nmc_street']
            home_phone = form.cleaned_data['home_phone']
            cell_phone = form.cleaned_data['cell_phone']
            email = form.cleaned_data['email']
            project_notes = form.cleaned_data['detailed_instr']
            salesperson = form.cleaned_data['salesperson']
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']
            time_ap = form.cleaned_data['time_ap']
            found_us = form.cleaned_data['found_us']

            new_customer = Customer(name=name, last_name=last_name,
                                    address=address, address1=address1,
                                    city=city, state=state, 
                                    zip_code=zip_code, gate_code=gate_code,
                                    nmc_street=nmc_street, home_phone=home_phone,
                                    cell_phone=cell_phone, email_address=email,
                                    entry_date=timezone.now())
            new_customer.save()
            a_or_p = 'AM' if time_ap=="1" else 'PM'
            t = str(time)+a_or_p
            if t == 'NoneAM' or t == 'NonePM':
                appoint_sched = time
            else:
                appoint_sched = datetime.strptime(t, '%I:%M:%S%p')
            new_lead = Lead(client_id=new_customer, project_notes=project_notes,
                            appointment_date=date, appointment_time=appoint_sched,
                            salesperson=salesperson, lead_status=6, source=found_us,
                            entry_date=timezone.now())
            new_lead.save()
            current_user = User.objects.get(username=request.user.username)
            new_entry_log = EntryLog(user_id=current_user,
                                     action="{} created a new appointment with {}".format(
                                         current_user.username,
                                         new_lead.client_id
                                     ),
                                     lead=new_lead,
                                     customer=new_customer,
                                     entry_date=timezone.now())
            new_entry_log.save()

            files_lead = Lead.objects.get(pk=new_lead.id)
            for contract in request.FILES.getlist('contracts'):
                add_files = Contracts(job=files_lead, document=contract)
                add_files.save()
            for photo in request.FILES.getlist('images'):
                add_photos = Pictures(job=files_lead, photos=photo)
                add_photos.save()

            return redirect('appointments')

    else:
        form = NewAppointmentForm()
        form.fields['address1'].required = False
        form.fields['state'].required = False
        form.fields['gate_code'].required = False
        form.fields['nmc_street'].required = False
        form.fields['home_phone'].required = False
        form.fields['cell_phone'].required = False
        form.fields['email'].required = False
        form.fields['detailed_instr'].required = False
        form.fields['found_us'].required = False
        form.fields['salesperson'].required = False
        form.fields['contracts'].required = False
        form.fields['images'].required = False
        form.fields['date'].required = False

    context = {
        'form': form
    }

    return render(request, 'new_appointment.html', context)

@login_required
def edit_appointment(request, leadpk):
    appt = Lead.objects.get(pk=leadpk)
    cust = Customer.objects.get(pk=appt.client_id.id)

    if request.method == "POST":
        form = NewAppointmentForm(request.POST)

        form.fields['address1'].required = False
        form.fields['state'].required = False
        form.fields['gate_code'].required = False
        form.fields['nmc_street'].required = False
        form.fields['home_phone'].required = False
        form.fields['cell_phone'].required = False
        form.fields['email'].required = False
        form.fields['detailed_instr'].required = False
        form.fields['found_us'].required = False
        form.fields['salesperson'].required = False
        form.fields['contracts'].required = False
        form.fields['images'].required = False
        form.fields['date'].required = False

        if form.is_valid():
            name = form.cleaned_data['name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            address1 = form.cleaned_data['address1']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zip_code = form.cleaned_data['zip_code']
            gate_code = form.cleaned_data['gate_code']
            nmc_street = form.cleaned_data['nmc_street']
            home_phone = form.cleaned_data['home_phone']
            cell_phone = form.cleaned_data['cell_phone']
            email = form.cleaned_data['email']
            project_notes = form.cleaned_data['detailed_instr']
            salesperson = form.cleaned_data['salesperson']
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']
            time_ap = form.cleaned_data['time_ap']
            found_us = form.cleaned_data['found_us']

            # a_or_p = 'AM' if time_ap=="1" else 'PM'
            # t = str(time)+a_or_p
            # appoint_sched = datetime.strptime(t, '%I:%M:%S%p')

            a_or_p = 'AM' if time_ap=="1" else 'PM'
            t = str(time)+a_or_p
            if t == 'NoneAM' or t == 'NonePM':
                appoint_sched = time
            else:
                appoint_sched = datetime.strptime(t, '%I:%M:%S%p')

            cust.name = name
            cust.last_name = last_name
            cust.address = address
            cust.address1 = address1
            cust.city = city
            cust.state = state
            cust.zip_code = zip_code
            cust.gate_code = gate_code
            cust.nmc_street = nmc_street
            cust.home_phone = home_phone
            cust.cell_phone = cell_phone
            cust.email_address = email
            cust.save()
            appt.project_notes = project_notes
            appt.salesperson = salesperson
            appt.appointment_date = date
            appt.appointment_time = appoint_sched
            appt.source = found_us
            appt.save()

            current_user = User.objects.get(username=request.user.username)
            new_entry_log = EntryLog(user_id=current_user,
                                     action="{} changed the {} appointment with {}".format(
                                         current_user.username,
                                         appt.appointment_date,
                                         name+' '+last_name
                                     ),
                                     customer=appt.client_id,
                                     lead=appt,
                                     entry_date=timezone.now())
            new_entry_log.save()

            return redirect('appointments')

        else:
            print(form.errors)

    else:
        if appt.appointment_time:
            if appt.appointment_time.hour <= 12:
                ap_init = "1"
            else:
                ap_init = "2"
            appoint_time = appt.appointment_time.strftime("%I:%M")
            if appoint_time[0] == "0":
                appoint_time = appoint_time[1:]
        else:
            appoint_time = ''
            ap_init = "1"

        form = NewAppointmentForm(initial = {
            'name': cust.name,
            'last_name': cust.last_name,
            'address': cust.address,
            'address1': cust.address1,
            'city': cust.city,
            'state': cust.state,
            'zip_code': cust.zip_code,
            'gate_code': cust.gate_code,
            'nmc_street': cust.nmc_street,
            'home_phone': cust.home_phone,
            'cell_phone': cust.cell_phone,
            'email': cust.email_address,
            'detailed_instr': appt.project_notes,
            'salesperson': appt.salesperson,
            'date': appt.appointment_date,
            'time': appoint_time,
            'time_ap': ap_init,
            'found_us': appt.source
        })

    form.fields['address1'].required = False
    form.fields['state'].required = False
    form.fields['gate_code'].required = False
    form.fields['nmc_street'].required = False
    form.fields['home_phone'].required = False
    form.fields['cell_phone'].required = False
    form.fields['email'].required = False
    form.fields['detailed_instr'].required = False
    form.fields['found_us'].required = False
    form.fields['salesperson'].required = False
    form.fields['contracts'].required = False
    form.fields['images'].required = False
    form.fields['date'].required = False

    context = {
        'form': form
    }

    return render(request, 'edit_appointment.html', context)

@login_required
def delete_appointment(request, leadpk):
    appt_del = Lead.objects.get(pk=leadpk)
    cust = Customer.objects.get(pk=appt_del.client_id.id)

    if request.method == "POST":

        current_user = User.objects.get(username=request.user.username)
        new_entry_log = EntryLog(user_id=current_user,
                                action="{} deleteded the {} appointment with {}".format(
                                        current_user.username,
                                        appt_del.appointment_date,
                                        cust
                                    ),
                                customer=appt_del.client_id,
                                entry_date=timezone.now())
        new_entry_log.save()

        appt_del.delete()
        cust.delete()

        # messages.add_message(request, messages.INFO, 'appointments')

        # return redirect(reverse('delete-customer', kwargs={'custpk': cust.id}))
        return redirect('appointments')

    context = {
        'cust': cust,
        'appt_del': appt_del
    }

    return render(request, 'delete_appointment.html', context)

# @login_required
# def delete_customer(request, custpk):
#     del_cust = Customer.objects.get(pk=custpk)
#     urlList = []

#     if request.method == "POST":

#         storage = get_messages(request)

#         for message in storage:
#             urlList.append(message.message)
#         storage.used = True

#         returnURL = urlList.pop()

#         current_user = User.objects.get(username=request.user.username)
#         new_entry_log = EntryLog(user_id=current_user,
#                                 action="{} deleted the customer {}.".format(
#                                             current_user.username,
#                                             del_cust
#                                         ),
#                                 entry_date=timezone.now())
#         new_entry_log.save()

#         del_cust.delete()
        
#         return redirect(returnURL)

#     context = {
#         'del_cust': del_cust
#     }

#     return render(request, 'delete_customer.html', context)

@login_required
def leads_run(request):
    leadsrun = Lead.objects.filter(lead_status='2').order_by('-appointment_date', '-appointment_time')
    if request.method == "POST":
        form = SortLeadsRunForm(request.POST)

        form.fields['sort_by'].required = False
        form.fields['order'].required = False

        if form.is_valid():
            sort_by = form.cleaned_data['sort_by']
            order = form.cleaned_data['order']

            if sort_by == "1": # customer name
                sortstring = 'client_id__last_name'
            if sort_by == "2": # Address
                sortstring = 'client_id__address'
            if sort_by == "3": # City
                sortstring = 'client_id__city'
            if sort_by == "4": # Date Appointment Run
                sortstring = 'appointment_date'
            if sort_by == "5": # Nearest Cross Street
                sortstring = 'client_id__nmc_street'
            if order == "1":
                sortstring = '-'+sortstring

            leadsrun = Lead.objects.filter(lead_status='2').order_by(sortstring)

    else:
        form = SortLeadsRunForm()

    paginator = Paginator(leadsrun, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        lead = paginator.page(page)
    except(EmptyPage, InvalidPage):
        lead = paginator.page(paginator.num_pages)

    context = {
        'lead': lead,
        'form': form
    }

    return render(request, 'leads_run.html', context)

@login_required
def new_lead(request):
    if request.method == 'POST':
        form = NewLeadForm(request.POST, request.FILES)

        if form.is_valid():
            name = form.cleaned_data['name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            address1 = form.cleaned_data['address1']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zip_code = form.cleaned_data['zip_code']
            nmc_street = form.cleaned_data['nmc_street']
            home_phone = form.cleaned_data['home_phone']
            cell_phone = form.cleaned_data['cell_phone']
            fax_number = form.cleaned_data['fax_number']
            email_address = form.cleaned_data['email']
            project_notes = form.cleaned_data['detailed_instr']
            if 'priority-choice' in request.POST:
                priority = True
            else:
                priority = False
            priority_notes = form.cleaned_data['priority_notes']
            salesperson = form.cleaned_data['salesperson']
            sales_date = form.cleaned_data['sales_date']
            date_appointment_run = form.cleaned_data['date_appointment_run']
            time = form.cleaned_data['time']
            time_ap = form.cleaned_data['time_ap']
            project_type = form.cleaned_data['project_type']
            association_approval = form.cleaned_data['association_approval']
            permits = form.cleaned_data['permits']
            materials_ordered = form.cleaned_data['materials_ordered']
            concrete_existing = form.cleaned_data['concrete_existing']
            footer_needed = form.cleaned_data['footer_needed']
            footer_dig_date = form.cleaned_data['footer_dig_date']
            footer_pour_date = form.cleaned_data['footer_pour_date']
            footer_inspection_date = form.cleaned_data['footer_inspection_date']
            safety_stakes = form.cleaned_data['safety_stakes']
            contract_amount = form.cleaned_data['total_contract_amount']
            payments = form.cleaned_data['payments']
            downpayment = form.cleaned_data['downpayment']
            lead_cur_status = form.cleaned_data['lead_status']

            new_customer = Customer(name=name, last_name=last_name,
                                    address=address, address1=address1,
                                    city=city, state=state, 
                                    zip_code=zip_code, nmc_street=nmc_street,
                                    home_phone=home_phone, cell_phone=cell_phone,
                                    fax_number=fax_number, email_address=email_address,
                                    entry_date=timezone.now())
            new_customer.save()
            current_user = User.objects.get(username=request.user.username)
            new_entry_log = EntryLog(user_id=current_user,
                                     action="{} created a new customer, {}".format(
                                         current_user.username,
                                         name+' '+last_name
                                     ),
                                     customer=new_customer,
                                     entry_date=timezone.now())
            new_entry_log.save()

            # if date != '' and time != '':
            a_or_p = 'AM' if time_ap=="1" else 'PM'
            t = str(time)+a_or_p
            if t == 'NoneAM' or t == 'NonePM':
                appoint_sched = time
            else:
                appoint_sched = datetime.strptime(t, '%I:%M:%S%p')

            # a_or_p = 'AM' if time_ap=="1" else 'PM'
            # t = str(time)+a_or_p
            # appoint_sched = datetime.strptime(t, '%I:%M:%S%p')
            new_lead = Lead(client_id=new_customer, project_notes=project_notes,
                            appointment_date=date_appointment_run, appointment_time=appoint_sched,
                            salesperson=salesperson, lead_status=2,
                            priority=priority, priority_msg=priority_notes,
                            contract_amount=contract_amount,lead_cur_status=lead_cur_status,
                            entry_date=timezone.now())
            new_lead.save()

            files_lead = Lead.objects.get(pk=new_lead.id)
            for contract in request.FILES.getlist('contracts'):
                add_files = Contracts(job=files_lead, document=contract)
                add_files.save()
            for photo in request.FILES.getlist('images'):
                add_photos = Pictures(job=files_lead, photos=photo)
                add_photos.save()

            add_proj = Lead.objects.get(pk=new_lead.id)
            for p in project_type:
                pt = ProjectType.objects.get(pk=int(p))
                add_proj.project_type.add(pt)
                add_proj.save()

            log_entry2 = EntryLog(user_id=current_user,
                                    action="{} created a new lead with {} ".format(
                                        current_user.username,
                                        name+' '+last_name
                                    ),
                                    lead=new_lead,
                                    customer=new_customer,
                                    entry_date=timezone.now())
            log_entry2.save()

            job = JobStatus(lead=new_lead, sale_date=sales_date, association_approval=association_approval,
                            materials_ordered=materials_ordered, concrete_existing=concrete_existing,
                            footer_needed=footer_needed, safety_stakes=safety_stakes,)
            job.save()

            if footer_dig_date or footer_inspection_date or footer_pour_date:
                inst = Installation(footer_dig_date=footer_dig_date,
                                    footer_inspection_date=footer_inspection_date,
                                    footer_pour_date=footer_pour_date,
                                    job=new_lead)
                inst.save()

            pay = Payment(job=new_lead, status=payments, amount=downpayment)
            pay.save()

            permit = Permit(job=new_lead, status=permits)
            permit.save()
            
            return redirect('leads-run')

    else:
        form = NewLeadForm()

        context = {
            'form': form
        }

        return render(request, 'new_lead.html', context)

@login_required
def send_to_standard(request, leadpk):
    stand = Lead.objects.get(pk=leadpk)

    if request.method == "POST":
        stand.lead_status = 6
        stand.save()

        current_user = User.objects.get(username=request.user.username)
        log_entry2 = EntryLog(user_id=current_user,
                                action="{} sent the lead with {} to standard view.".format(
                                    current_user.username,
                                    stand.client_id
                                ),
                                lead=stand,
                                entry_date=timezone.now())
        log_entry2.save()

        return redirect('leads-run')

    context = {
        'stand': stand
    }

    return render(request, 'send_to_standard.html', context)

@login_required
def send_to_jip(request, leadpk):
    jip = Lead.objects.get(pk=leadpk)
    returnURL = '../'

    if request.method == "POST":
        if jip.lead_status == '4':
            returnURL = 'accounts-receivable'
        if jip.lead_status == '2':
            returnURL = 'leads-run'

        jip.lead_status = 5
        jip.save()

        current_user = User.objects.get(username=request.user.username)
        log_entry2 = EntryLog(user_id=current_user,
                                action="{} sent the lead with {} to jobs in progress.".format(
                                    current_user.username,
                                    jip.client_id
                                ),
                                lead=jip,
                                entry_date=timezone.now())
        log_entry2.save()


        return redirect(returnURL)

    context = {
        'job': jip
    }

    return render(request, 'send_to_jip.html', context)

class LeadDetailView(LoginRequiredMixin, DetailView):
    model = Lead
    template_name = 'lead_detail.html'

    def get_context_data(self, **kwargs):
        context = super(LeadDetailView, self).get_context_data(**kwargs)
        context['lead_files'] = Contracts.objects.filter(job=self.kwargs['pk'])
        context['lead_photos'] = Pictures.objects.filter(job=self.kwargs['pk'])
        return context

@login_required
def edit_lead(request, leadpk):
    change_lead = Lead.objects.get(pk=leadpk)
    change_cust = Customer.objects.get(pk=change_lead.client_id.id)
    try:
        change_job = JobStatus.objects.get(lead=leadpk)
    except Exception as exception:
        change_job = False

    try:
        change_install = Installation.objects.get(job=leadpk)
    except Exception as exception:
        change_install = False

    try:
        change_payment = Payment.objects.get(job=leadpk)
    except Exception as exception:
        change_payment = False

    try:
        change_permit = Permit.objects.get(job=leadpk)
    except Exception as exception:
        change_permit = False

    if request.method == 'POST':
        form = NewLeadForm(request.POST, request.FILES)
        if form.is_valid():
      
            for contract in request.FILES.getlist('contracts'):
                new_file = Contracts(job=change_lead, document=contract)
                new_file.save()
            for photo in request.FILES.getlist('images'):
                add_photos = Pictures(job=change_lead, photos=photo)
                add_photos.save()

            name = form.cleaned_data['name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            address1 = form.cleaned_data['address1']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zip_code = form.cleaned_data['zip_code']
            nmc_street = form.cleaned_data['nmc_street']
            home_phone = form.cleaned_data['home_phone']
            cell_phone = form.cleaned_data['cell_phone']
            fax_number = form.cleaned_data['fax_number']
            email_address = form.cleaned_data['email']
            project_notes = form.cleaned_data['detailed_instr']
            if 'priority-choice' in request.POST:
                priority = True
            else:
                priority = False
            priority_notes = form.cleaned_data['priority_notes']
            salesperson = form.cleaned_data['salesperson']
            sales_date = form.cleaned_data['sales_date']
            date_appointment_run = form.cleaned_data['date_appointment_run']
            time = form.cleaned_data['time']
            time_ap = form.cleaned_data['time_ap']
            project_type = form.cleaned_data['project_type']
            association_approval = form.cleaned_data['association_approval']
            permits = form.cleaned_data['permits']
            materials_ordered = form.cleaned_data['materials_ordered']
            concrete_existing = form.cleaned_data['concrete_existing']
            footer_needed = form.cleaned_data['footer_needed']
            footer_dig_date = form.cleaned_data['footer_dig_date']
            footer_pour_date = form.cleaned_data['footer_pour_date']
            footer_inspection_date = form.cleaned_data['footer_inspection_date']
            safety_stakes = form.cleaned_data['safety_stakes']
            contract_amount = form.cleaned_data['total_contract_amount']
            payments = form.cleaned_data['payments']
            downpayment = form.cleaned_data['downpayment']
            lead_cur_status = form.cleaned_data['lead_status']

            # a_or_p = 'AM' if time_ap=="1" else 'PM'
            # t = str(time)+a_or_p
            # appoint_sched = datetime.strptime(t, '%I:%M:%S%p')

            a_or_p = 'AM' if time_ap=="1" else 'PM'
            t = str(time)+a_or_p
            if t == 'NoneAM' or t == 'NonePM':
                appoint_sched = time
            else:
                appoint_sched = datetime.strptime(t, '%I:%M:%S%p')

            change_cust.name = name
            change_cust.last_name = last_name
            change_cust.address = address
            change_cust.address1 = address1
            change_cust.city = city
            change_cust.state = state
            change_cust.zip_code = zip_code
            change_cust.nmc_street = nmc_street
            change_cust.home_phone = home_phone
            change_cust.cell_phone = cell_phone
            change_cust.fax_number = fax_number
            change_cust.email_address = email_address
            change_lead.project_notes = project_notes
            change_lead.salesperson = salesperson
            change_lead.appointment_date = date_appointment_run
            change_lead.appointment_time = appoint_sched
            change_lead.project_type.set(project_type)
            change_lead.contract_amount = contract_amount
            change_lead.lead_cur_status = lead_cur_status
            change_lead.priority = priority
            change_lead.priority_msg = priority_notes
            change_lead.save()
            change_cust.save()

            if change_permit:
                change_permit.status = permits
                change_permit.save()
            else:
                change_permit = Permit(job=change_lead, status=permits)
                change_permit.save()

            if change_job:
                change_job.sale_date = sales_date
                change_job.association_approval = association_approval
                change_job.materials_ordered = materials_ordered
                change_job.concrete_existing = concrete_existing
                change_job.footer_needed = footer_needed
                change_job.safety_stakes = safety_stakes
                change_job.save()
            else:
                change_job = JobStatus(lead=change_lead, sale_date=sales_date,
                                    association_approval=association_approval,
                                    materials_ordered=materials_ordered,
                                    concrete_existing=concrete_existing,
                                    footer_needed=footer_needed,
                                    safety_stakes=safety_stakes)
                change_job.save()

            if change_install:
                change_install.footer_dig_date = footer_dig_date
                change_install.footer_dig_date = footer_pour_date
                change_install.footer_dig_date = footer_inspection_date
                change_install.save()
            else:
                change_install = Installation(job=change_lead, footer_dig_date=footer_dig_date,
                                            footer_inspection_date=footer_inspection_date,
                                            footer_pour_date=footer_pour_date)
                change_install.save()

            if change_payment:
                change_payment.status = payments
                change_payment.amount = downpayment
                change_payment.save()
            else:
                change_payment = Payment(job=change_lead, status=payments, amount=downpayment)
                change_payment.save()

            current_user = User.objects.get(username=request.user.username)
            new_entry_log = EntryLog(user_id=current_user,
                                        action="{} edited a lead".format(
                                            current_user.username
                                        ),
                                        lead=change_lead,
                                        customer=change_cust,
                                        entry_date=timezone.now())
            new_entry_log.save()

            add_proj = Lead.objects.get(pk=change_lead.id)
            for p in project_type:
                pt = ProjectType.objects.get(pk=int(p))
                change_lead.project_type.add(pt)
                add_proj.save()

            return redirect('leads-run')
        else:
            print(form.errors)

    else:
        if change_lead.appointment_time:
            if change_lead.appointment_time.hour <= 12:
                ap_init = "1"
            else:
                ap_init = "2"
            appoint_time = change_lead.appointment_time.strftime("%I:%M")
            if appoint_time[0] == "0":
                appoint_time = appoint_time[1:]
        else:
            appoint_time = ''
            ap_init = "1"

        form = NewLeadForm(initial = {
            'name': change_cust.name,
            'last_name': change_cust.last_name,
            'address': change_cust.address,
            'address1': change_cust.address1,
            'city': change_cust.city,
            'state': change_cust.state,
            'zip_code': change_cust.zip_code,
            'nmc_street': change_cust.nmc_street,
            'home_phone': change_cust.home_phone,
            'cell_phone': change_cust.cell_phone,
            'fax_number': change_cust.fax_number,
            'email': change_cust.email_address,
            'detailed_instr': change_lead.project_notes,
            'priority': change_lead.priority,
            'priority_notes': change_lead.priority_msg,
            'salesperson': change_lead.salesperson,
            'date_appointment_run': change_lead.appointment_date,
            'time': appoint_time,        #change_lead.appointment_time,
            'time_ap': ap_init,
            'project_type': Lead.objects.filter(pk=leadpk).values('project_type'),
            'contract_amount': change_lead.contract_amount,
            'lead_status': change_lead.lead_cur_status,
        })

        if change_job:
            form.initial['sales_date'] = change_job.sale_date
            form.initial['association_approval'] = change_job.association_approval
            form.initial['materials_ordered'] = change_job.materials_ordered
            form.initial['concrete_existing'] = change_job.concrete_existing
            form.initial['footer_needed'] = change_job.footer_needed
            form.initial['safety_stakes'] = change_job.safety_stakes
        if change_install:
            form.initial['footer_dig_date'] = change_install.footer_dig_date
            form.initial['footer_inspection_date'] = change_install.footer_inspection_date
            form.initial['footer_pour_date'] = change_install.footer_pour_date
        if change_payment:
            form.initial['payments'] = change_payment.status
            form.initial['downpayment'] = change_payment.amount
        lead_types = Lead.objects.filter(pk=leadpk).values('project_type',
                                                           'project_type__proj_type',
                                                           'project_type__group')
        initial_types = []
        for pt in lead_types:
            num = pt['project_type']
            initial_types.append(str(num))
            form.initial['project_type'] = initial_types

    context = {
        'form': form
    }

    context['lead_files'] = Contracts.objects.filter(job=leadpk)
    context['lead_photos'] = Pictures.objects.filter(job=leadpk)

    return render(request, 'edit_lead.html', context)

@login_required
def confirm_delete_cont(request, contpk):
    remove = Contracts.objects.get(pk=contpk)
    lead = Lead.objects.get(pk=remove.job.id)

    context = {
        'remove': remove,
        'lead': lead
    }

    return render(request, 'confirm_delete_contract.html', context)

@login_required
def delete_contract(request, contpk):
    remove = Contracts.objects.get(pk=contpk)
    lead = Lead.objects.get(pk=remove.job.id)

    current_user = User.objects.get(username=request.user.username)
    log_entry2 = EntryLog(user_id=current_user,
                          action="{} deleted a contract from the {} lead.".format(
                                current_user.username,
                                lead.client_id
                            ),
                            lead=lead,
                            entry_date=timezone.now())
    log_entry2.save()

    remove.delete()

    return redirect('edit-lead', leadpk=lead.id)

@login_required
def confirm_delete_photo(request, photopk):
    remove = Pictures.objects.get(pk=photopk)
    lead = Lead.objects.get(pk=remove.job.id)

    context = {
        'remove': remove,
        'lead': lead
    }

    return render(request, 'confirm_delete_photo.html', context)

@login_required
def delete_photo(request, photopk):
    remove = Pictures.objects.get(pk=photopk)
    lead = Lead.objects.get(pk=remove.job.id)
    remove.delete()

    current_user = User.objects.get(username=request.user.username)
    log_entry2 = EntryLog(user_id=current_user,
                            action="{} deleted a photo from the {} lead.".format(
                                current_user.username,
                                lead.client_id
                            ),
                            lead=lead,
                            entry_date=timezone.now())
    log_entry2.save()

    return redirect('edit-lead', leadpk=lead.id)

@login_required
def delete_lead(request, leadpk):
    ex_lead = Lead.objects.get(pk=leadpk)
    cust = Customer.objects.get(pk=ex_lead.client_id.id)
    # messages.add_message(request, messages.INFO, 'leads-run')

    if request.method == "POST":

        current_user = User.objects.get(username=request.user.username)
        log_entry2 = EntryLog(user_id=current_user,
                                action="{} deleted a lead with {}.".format(
                                    current_user.username,
                                    ex_lead.client_id
                                ),
                                entry_date=timezone.now())
        log_entry2.save()
        ex_lead.delete()
        cust.delete()

        # return redirect(reverse('delete-customer', kwargs={'custpk':cust.id}))
        return redirect('leads-run')

    context = {
            'cust': cust,
            'ex_lead': ex_lead
        }

    return render(request, 'delete_lead.html', context)

@login_required
def jobs_in_progress(request):
    jip = Lead.objects.filter(lead_status='5').order_by('appointment_date', 'appointment_time')
    if request.method == "POST":
        form = SortJIPForm(request.POST)

        form.fields['sort_by'].required = False
        form.fields['order'].required = False

        if form.is_valid():
            sort_by = form.cleaned_data['sort_by']
            order = form.cleaned_data['order']

            if sort_by == "1": # customer name
                sortstring = 'client_id__last_name'
            if sort_by == "2": # Address
                sortstring = 'client_id__address'
            if sort_by == "3": # City
                sortstring = 'client_id__city'
            if sort_by == "4": # Installation Date
                sortstring = 'installation__install_schedule'
            if sort_by == "5": # Project Type
                sortstring = 'project_type'
            if sort_by == "6": # Installer
                sortstring = 'installation__installer'

            if order == "1":
                sortstring = '-'+sortstring

            jip = Lead.objects.filter(lead_status='5').order_by(sortstring)

    else:
        form = SortJIPForm()

    paginator = Paginator(jip, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        job_in_prog = paginator.page(page)
    except(EmptyPage, InvalidPage):
        job_in_prog = paginator.page(paginator.num_pages)

    context = {
#        'install': install,
        'job_in_prog': job_in_prog,
        'form': form
    }

    return render(request, 'jobs_in_progress.html', context)

@login_required
def send_to_receivable(request, leadpk):
    receivable = Lead.objects.get(pk=leadpk)

    if request.method == "POST":
        returnURL = '../'
        if receivable.lead_status == '3':
            returnURL = 'archives'
        else:
            returnURL = 'jobs-in-progress'
        receivable.lead_status = 4
        receivable.save()

        current_user = User.objects.get(username=request.user.username)
        log_entry2 = EntryLog(user_id=current_user,
                                action="{} sent the job for {} to accounts receivable.".format(
                                    current_user.username,
                                    receivable.client_id
                                ),
                                lead=receivable,
                                entry_date=timezone.now())
        log_entry2.save()

        try:
            job = JobStatus.objects.get(pk=receivable.id)
        except Exception as exception:
            job = False

        if job:
            job.completion_date = timezone.now()
            job.save()
        else:
            newjob = JobStatus(lead=receivable, materials_ordered=False, 
            safety_stakes=False, completion_date=timezone.now())
            newjob.save()

        return redirect(returnURL)

    context = {
        'receivable': receivable
    }

    return render(request, 'send_to_receivable.html', context)

class JobDetailView(LoginRequiredMixin, DetailView):
    model = Lead
    template_name = 'job_detail.html'

    def get_context_data(self, **kwargs):
        context = super(JobDetailView, self).get_context_data(**kwargs)
        context['job_files'] = Contracts.objects.filter(job=self.kwargs['pk'])
        context['job_photos'] = Pictures.objects.filter(job=self.kwargs['pk'])
        return context

@login_required
def edit_job(request, leadpk):
    change_lead = Lead.objects.get(pk=leadpk)
    change_cust = Customer.objects.get(pk=change_lead.client_id.id)
    try:
        change_job = JobStatus.objects.get(lead=leadpk)
    except Exception as exception:
        change_job = False

    try:
        change_install = Installation.objects.get(job=leadpk)
    except Exception as exception:
        change_install = False

    try:
        change_payment = Payment.objects.get(job=leadpk)
    except Exception as exception:
        change_payment = False

    try:
        change_permit = Permit.objects.get(job=leadpk)
    except Exception as exception:
        change_permit = False

    if request.method == 'POST':
        form = EditJobForm(request.POST, request.FILES)
        if form.is_valid():
      
            for contract in request.FILES.getlist('contracts'):
                new_file = Contracts(job=change_lead, document=contract)
                new_file.save()
            for photo in request.FILES.getlist('images'):
                add_photos = Pictures(job=change_lead, photos=photo)
                add_photos.save()

            name = form.cleaned_data['name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            address1 = form.cleaned_data['address1']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zip_code = form.cleaned_data['zip_code']
            gate_code = form.cleaned_data['gate_code']
            nmc_street = form.cleaned_data['nmc_street']
            home_phone = form.cleaned_data['home_phone']
            cell_phone = form.cleaned_data['cell_phone']
            email_address = form.cleaned_data['email']
            project_notes = form.cleaned_data['detailed_instr']
            if 'priority-choice' in request.POST:
                priority = True
            else:
                priority = False
            priority_notes = form.cleaned_data['priority_notes']
            salesperson = form.cleaned_data['salesperson']
            sales_date = form.cleaned_data['sales_date']
            installation_schedule = form.cleaned_data['install_schedule']
            project_type = form.cleaned_data['project_type']
            association_approval = form.cleaned_data['association_approval']
            permits = form.cleaned_data['permits']
            materials_ordered = form.cleaned_data['materials_ordered']
            concrete_existing = form.cleaned_data['concrete_existing']
            footer_needed = form.cleaned_data['footer_needed']
            footer_dig_date = form.cleaned_data['footer_dig_date']
            footer_pour_date = form.cleaned_data['footer_pour_date']
            footer_inspection_date = form.cleaned_data['footer_inspection_date']
            safety_stakes = form.cleaned_data['safety_stakes']
            contract_amount = form.cleaned_data['contract_amount']
            price_breakdown = form.cleaned_data['price_breakdown']
            payments = form.cleaned_data['payments']
            downpayment = form.cleaned_data['downpayment']
            installer = form.cleaned_data['installer']

            change_cust.name = name
            change_cust.last_name = last_name
            change_cust.address = address
            change_cust.address1 = address1
            change_cust.city = city
            change_cust.state = state
            change_cust.zip_code = zip_code
            change_cust.gate_code = gate_code
            change_cust.nmc_street = nmc_street
            change_cust.home_phone = home_phone
            change_cust.cell_phone = cell_phone
            change_cust.email_address = email_address
            change_lead.project_notes = project_notes
            change_lead.salesperson = salesperson
            change_lead.project_type.set(project_type)
            change_lead.contract_amount = contract_amount
            change_lead.priority = priority
            change_lead.priority_msg = priority_notes
            change_lead.save()
            change_cust.save()

            if change_permit:
                change_permit.status = permits
                change_permit.save()
            else:
                change_permit = Permit(job=change_lead, status=permits)
                change_permit.save()

            if change_job:
                change_job.sale_date = sales_date
                change_job.association_approval = association_approval
                change_job.materials_ordered = materials_ordered
                change_job.concrete_existing = concrete_existing
                change_job.footer_needed = footer_needed
                change_job.safety_stakes = safety_stakes
                change_job.save()
            else:
                change_job = JobStatus(lead=change_lead, sale_date=sales_date,
                                    association_approval=association_approval,
                                    materials_ordered=materials_ordered,
                                    concrete_existing=concrete_existing,
                                    footer_needed=footer_needed,
                                    safety_stakes=safety_stakes)
                change_job.save()

            if change_install:
                change_install.footer_dig_date = footer_dig_date
                change_install.footer_pour_date = footer_pour_date
                change_install.footer_inspection_date = footer_inspection_date
                change_install.install_schedule = installation_schedule
                change_install.installer = installer
                change_install.save()
            else:
                change_install = Installation(job=change_lead, footer_dig_date=footer_dig_date,
                                            footer_inspection_date=footer_inspection_date,
                                            footer_pour_date=footer_pour_date, installer=installer,
                                            install_schedule=installation_schedule)
                change_install.save()

            if change_payment:
                change_payment.status = payments
                change_payment.amount = downpayment
                change_payment.breakdown = price_breakdown
                change_payment.save()
            else:
                change_payment = Payment(job=change_lead, status=payments, amount=downpayment,
                                         breakdown=price_breakdown)
                change_payment.save()

            current_user = User.objects.get(username=request.user.username)
            new_entry_log = EntryLog(user_id=current_user,
                                        action="{} edited the lead for {}.".format(
                                            current_user.username,
                                            change_lead.client_id
                                        ),
                                        lead=change_lead,
                                        customer=change_cust,
                                        entry_date=timezone.now())
            new_entry_log.save()

            add_proj = Lead.objects.get(pk=change_lead.id)
            for p in project_type:
                pt = ProjectType.objects.get(pk=int(p))
                change_lead.project_type.add(pt)
                add_proj.save()

            return redirect('jobs-in-progress')
        else:
            print(form.errors)

    else:

        form = EditJobForm(initial = {
            'name': change_cust.name,
            'last_name': change_cust.last_name,
            'address': change_cust.address,
            'address1': change_cust.address1,
            'city': change_cust.city,
            'state': change_cust.state,
            'zip_code': change_cust.zip_code,
            'gate_code': change_cust.gate_code,
            'nmc_street': change_cust.nmc_street,
            'home_phone': change_cust.home_phone,
            'cell_phone': change_cust.cell_phone,
            'email': change_cust.email_address,
            'detailed_instr': change_lead.project_notes,
            'priority': change_lead.priority,
            'priority_notes': change_lead.priority_msg,
            'salesperson': change_lead.salesperson,
            'project_type': Lead.objects.filter(pk=leadpk).values('project_type'),
            'contract_amount': change_lead.contract_amount
        })

        if change_job:
            form.initial['sales_date'] = change_job.sale_date
            form.initial['association_approval'] = change_job.association_approval
            form.initial['materials_ordered'] = change_job.materials_ordered
            form.initial['concrete_existing'] = change_job.concrete_existing
            form.initial['footer_needed'] = change_job.footer_needed
            form.initial['safety_stakes'] = change_job.safety_stakes
        if change_install:
            form.initial['footer_dig_date'] = change_install.footer_dig_date
            form.initial['footer_inspection_date'] = change_install.footer_inspection_date
            form.initial['footer_pour_date'] = change_install.footer_pour_date
            form.initial['install_schedule'] = change_install.install_schedule
            form.initial['installer'] = change_install.installer
        if change_payment:
            form.initial['payments'] = change_payment.status
            form.initial['downpayment'] = change_payment.amount
            form.initial['price_breakdown'] = change_payment.breakdown
        lead_types = Lead.objects.filter(pk=leadpk).values('project_type',
                                                           'project_type__proj_type',
                                                           'project_type__group')
        initial_types = []
        for pt in lead_types:
            num = pt['project_type']
            initial_types.append(str(num))
            form.initial['project_type'] = initial_types

    context = {
        'form': form
    }

    context['job_files'] = Contracts.objects.filter(job=leadpk)
    context['job_photos'] = Pictures.objects.filter(job=leadpk)

    return render(request, 'edit_job.html', context)

@login_required
def delete_job(request, leadpk):
    returnURL = ''
    ex_lead = Lead.objects.get(pk=leadpk)
    cust = Customer.objects.get(pk=ex_lead.client_id.id)
    if ex_lead.lead_status == '5':
        returnURL = 'jobs-in-progress'
    elif ex_lead.lead_status == '4':
        returnURL = 'accounts-receivable'
    else:
        returnURL = 'archives'

    if request.method == "POST":
        current_user = User.objects.get(username=request.user.username)
        log_entry2 = EntryLog(user_id=current_user,
                                action="{} deleted the job with {}.".format(
                                    current_user.username,
                                    ex_lead.client_id
                                ),
                                entry_date=timezone.now())
        log_entry2.save()

        ex_lead.delete()
        cust.delete()

        # return redirect(reverse('delete-customer', kwargs={'custpk':cust.id}))
        return redirect(returnURL)

    context = {
            'cust': cust,
            'ex_lead': ex_lead
        }

    return render(request, 'delete_job.html', context)

@login_required
def pending_permits(request):
    pp = Permit.objects.filter(
        Q(job__lead_status = '5') | Q(job__lead_status = '4') | Q(job__lead_status = '3')
        ).exclude(
            status = 'NO'
            ).exclude(
                status = ''
                ).exclude(
                    archive = True
                    ).order_by(
                        '-job__appointment_date'
                    )

    paginator = Paginator(pp, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        perm = paginator.page(page)
    except(EmptyPage, InvalidPage):
        perm = paginator.page(paginator.num_pages)

    context = {
        'perm': perm
    }

    return render(request, 'pending_permits.html', context)

@login_required
def edit_permit(request, leadpk):
    pp = Permit.objects.get(pk=leadpk)
    cust = pp.job.client_id

    if request.method == "POST":
        form = EditPermitForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            last_name = form.cleaned_data['last_name']
            status = form.cleaned_data['status']
            jurisdiction = form.cleaned_data['jurisdiction']
            permit_number = form.cleaned_data['permit_number']
            description = form.cleaned_data['description']

            cust.name = name
            cust.last_name = last_name
            cust.save()
            pp.status = status
            pp.jurisdiction = jurisdiction
            pp.permit = permit_number
            pp.description = description
            pp.save()

            current_user = User.objects.get(username=request.user.username)
            log_entry2 = EntryLog(user_id=current_user,
                                    action="{} edited the permit for the {} job.".format(
                                        current_user.username,
                                        cust
                                    ),
                                    lead=pp.job,
                                    entry_date=timezone.now())
            log_entry2.save()

            return redirect('pending-permits')

    else:
        form = EditPermitForm(initial = {
            'name': pp.job.client_id.name,
            'last_name': pp.job.client_id.last_name,
            'status': pp.status,
            'jurisdiction': pp.jurisdiction,
            'permit_number': pp.permit,
            'description': pp.description
        })

        context = {
            'form': form
        }

    return render(request, 'edit_permit.html', context)

class PermitDetailView(LoginRequiredMixin, DetailView):
    model = Permit
    template_name = 'permit_detail.html'

    def get_context_data(self, **kwargs):
        context = super(PermitDetailView, self).get_context_data(**kwargs)
        return context

@login_required
def permit_to_archive(request, permpk):
    perm = Permit.objects.get(pk=permpk)

    if request.method == "POST":
        perm.archive = True
        perm.archive_date = datetime.now()
        perm.save()

        current_user = User.objects.get(username=request.user.username)
        log_entry2 = EntryLog(user_id=current_user,
                                action="{} sent the permit for the {} job to archive.".format(
                                    current_user.username,
                                    perm.job.client_id
                                ),
                                lead=perm.job,
                                entry_date=timezone.now())
        log_entry2.save()

        return redirect('pending-permits')

    context = {
        'perm': perm
    }

    return render(request, 'permit_to_archive.html', context)

@login_required
def permit_archives(request):
    archives = Permit.objects.filter(archive=True).order_by('-archive_date')

    paginator = Paginator(archives, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        arch = paginator.page(page)
    except(EmptyPage, InvalidPage):
        arch = paginator.page(paginator.num_pages)

    context = {
        'arch': arch
    }

    return render(request, 'permit_archives.html', context)

@login_required
def permit_to_pending(request, permpk):
    perm = Permit.objects.get(pk=permpk)

    if request.method == "POST":
        perm.archive = False
        perm.save()

        return redirect('permit-archives')

    context = {
        'perm': perm
    }

    return render(request, 'permit_to_pending.html', context)

@login_required
def accounts_receivable(request):
    acc = Lead.objects.filter(lead_status = '4')

    if request.method == "POST":
        form = SortAccountsForm(request.POST)

        form.fields['sort_by'].required = False
        form.fields['order'].required = False

        if form.is_valid():
            sort_by = form.cleaned_data['sort_by']
            order = form.cleaned_data['order']

            if sort_by == "1": # customer name
                sortstring = 'client_id__last_name'
            if sort_by == "2": # Address
                sortstring = 'client_id__address'
            if sort_by == "3": # City
                sortstring = 'client_id__city'

            if order == "1":
                sortstring = '-'+sortstring

            acc = Lead.objects.filter(lead_status='4').order_by(sortstring)
    else:
        form = SortAccountsForm

    paginator = Paginator(acc, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        accounts_receivable = paginator.page(page)
    except(EmptyPage, InvalidPage):
        accounts_receivable = paginator.page(paginator.num_pages)

    context = {
        'accounts_receivable': accounts_receivable,
        'form': form
    }

    return render(request, 'accounts_receivable.html', context)

@login_required
def send_to_archive(request, leadpk):
    arch = Lead.objects.get(pk=leadpk)
    try:
        job = JobStatus.objects.get(lead=leadpk)
    except Exception as exception:
        job = False

    if request.method == "POST":
        arch.lead_status = '3'
        arch.save()

        current_user = User.objects.get(username=request.user.username)
        log_entry2 = EntryLog(user_id=current_user,
                                action="{} sent the job with {} to archives.".format(
                                    current_user.username,
                                    arch.client_id
                                ),
                                lead=arch,
                                entry_date=timezone.now())
        log_entry2.save()

        if job:
            job.completion_date = datetime.now()
            job.save()

            current_user = User.objects.get(username=request.user.username)
            log_entry2 = EntryLog(user_id=current_user,
                                    action="{} deleted a contract from the {} lead.".format(
                                        current_user.username,
                                        arch.client_id
                                    ),
                                    lead=arch,
                                    entry_date=timezone.now())
            log_entry2.save()

        return redirect('accounts-receivable')

    context = {
        'arch': arch
    }

    return render(request, 'send_to_archive.html', context)

class AccountDetailView(LoginRequiredMixin, DetailView):
    model = Lead
    template_name = 'account_detail.html'

    def get_context_data(self, **kwargs):
        context = super(AccountDetailView, self).get_context_data(**kwargs)
        context['job_files'] = Contracts.objects.filter(job=self.kwargs['pk'])
        context['job_photos'] = Pictures.objects.filter(job=self.kwargs['pk'])
        return context

@login_required
def edit_account(request, leadpk):
    change_lead = Lead.objects.get(pk=leadpk)
    change_cust = Customer.objects.get(pk=change_lead.client_id.id)
    try:
        change_job = JobStatus.objects.get(lead=leadpk)
    except Exception as exception:
        change_job = False

    try:
        change_install = Installation.objects.get(job=leadpk)
    except Exception as exception:
        change_install = False

    try:
        change_payment = Payment.objects.get(job=leadpk)
    except Exception as exception:
        change_payment = False

    try:
        change_permit = Permit.objects.get(job=leadpk)
    except Exception as exception:
        change_permit = False

    if request.method == 'POST':
        form = EditAccountForm(request.POST, request.FILES)
        if form.is_valid():
      
            for contract in request.FILES.getlist('contracts'):
                new_file = Contracts(job=change_lead, document=contract)
                new_file.save()
            for photo in request.FILES.getlist('images'):
                add_photos = Pictures(job=change_lead, photos=photo)
                add_photos.save()

            name = form.cleaned_data['name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            address1 = form.cleaned_data['address1']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zip_code = form.cleaned_data['zip_code']
            nmc_street = form.cleaned_data['nmc_street']
            home_phone = form.cleaned_data['home_phone']
            cell_phone = form.cleaned_data['cell_phone']
            fax_number = form.cleaned_data['fax_number']
            email_address = form.cleaned_data['email']
            project_notes = form.cleaned_data['detailed_instr']
            if 'priority-choice' in request.POST:
                priority = True
            else:
                priority = False
            priority_notes = form.cleaned_data['priority_notes']
            salesperson = form.cleaned_data['salesperson']
            schedule_date = form.cleaned_data['schedule_date']
            project_type = form.cleaned_data['project_type']
            alumalattice = form.cleaned_data['alumalattice']
            association_approval = form.cleaned_data['association_approval']
            permits = form.cleaned_data['permits']
            materials_ordered = form.cleaned_data['materials_ordered']
            concrete_existing = form.cleaned_data['concrete_existing']
            footer_needed = form.cleaned_data['footer_needed']
            footer_dig_date = form.cleaned_data['footer_dig_date']
            footer_pour_date = form.cleaned_data['footer_pour_date']
            footer_inspection_date = form.cleaned_data['footer_inspection_date']
            safety_stakes = form.cleaned_data['safety_stakes']
            contract_amount = form.cleaned_data['contract_amount']
            price_breakdown = form.cleaned_data['price_breakdown']
            payments = form.cleaned_data['payments']
            downpayment = form.cleaned_data['downpayment']
            installer = form.cleaned_data['installer']

            change_cust.name = name
            change_cust.last_name = last_name
            change_cust.address = address
            change_cust.address1 = address1
            change_cust.city = city
            change_cust.state = state
            change_cust.zip_code = zip_code
            change_cust.nmc_street = nmc_street
            change_cust.home_phone = home_phone
            change_cust.cell_phone = cell_phone
            change_cust.email_address = email_address
            change_lead.project_notes = project_notes
            change_lead.salesperson = salesperson
            change_lead.project_type.set(project_type)
            change_lead.contract_amount = contract_amount
            change_lead.priority = priority
            change_lead.priority_msg = priority_notes
            change_lead.appointment_date = schedule_date
            change_lead.save()
            change_cust.save()

            if change_permit:
                change_permit.status = permits
                change_permit.save()
            else:
                change_permit = Permit(job=change_lead, status=permits)
                change_permit.save()

            if change_job:
                change_job.association_approval = association_approval
                change_job.materials_ordered = materials_ordered
                change_job.concrete_existing = concrete_existing
                change_job.footer_needed = footer_needed
                change_job.safety_stakes = safety_stakes
                change_job.alumalattice = alumalattice
                change_job.save()
            else:
                change_job = JobStatus(lead=change_lead,
                                    association_approval=association_approval,
                                    materials_ordered=materials_ordered,
                                    concrete_existing=concrete_existing,
                                    footer_needed=footer_needed,
                                    safety_stakes=safety_stakes,
                                    alumalattice=alumalattice)
                change_job.save()

            if change_install:
                change_install.footer_dig_date = footer_dig_date
                change_install.footer_pour_date = footer_pour_date
                change_install.footer_inspection_date = footer_inspection_date
                change_install.installer = installer
                change_install.save()
            else:
                change_install = Installation(job=change_lead, footer_dig_date=footer_dig_date,
                                            footer_inspection_date=footer_inspection_date,
                                            footer_pour_date=footer_pour_date, installer=installer)
                change_install.save()

            if change_payment:
                change_payment.status = payments
                change_payment.amount = downpayment
                change_payment.breakdown = price_breakdown
                change_payment.save()
            else:
                change_payment = Payment(job=change_lead, status=payments, amount=downpayment,
                                         breakdown=price_breakdown)
                change_payment.save()

            current_user = User.objects.get(username=request.user.username)
            new_entry_log = EntryLog(user_id=current_user,
                                        action="{} edited the account for the {} job.".format(
                                            current_user.username,
                                            change_cust
                                        ),
                                        lead=change_lead,
                                        entry_date=timezone.now())
            new_entry_log.save()

            add_proj = Lead.objects.get(pk=change_lead.id)
            for p in project_type:
                pt = ProjectType.objects.get(pk=int(p))
                change_lead.project_type.add(pt)
                add_proj.save()

            return redirect('accounts-receivable')
        else:
            print(form.errors)

    else:

        form = EditAccountForm(initial = {
            'name': change_cust.name,
            'last_name': change_cust.last_name,
            'address': change_cust.address,
            'address1': change_cust.address1,
            'city': change_cust.city,
            'state': change_cust.state,
            'zip_code': change_cust.zip_code,
            'nmc_street': change_cust.nmc_street,
            'home_phone': change_cust.home_phone,
            'cell_phone': change_cust.cell_phone,
            'email': change_cust.email_address,
            'detailed_instr': change_lead.project_notes,
            'priority': change_lead.priority,
            'priority_notes': change_lead.priority_msg,
            'salesperson': change_lead.salesperson,
            'project_type': Lead.objects.filter(pk=leadpk).values('project_type'),
            'contract_amount': change_lead.contract_amount,
            'schedule_date': change_lead.appointment_date
        })

        if change_job:
            form.initial['association_approval'] = change_job.association_approval
            form.initial['materials_ordered'] = change_job.materials_ordered
            form.initial['concrete_existing'] = change_job.concrete_existing
            form.initial['footer_needed'] = change_job.footer_needed
            form.initial['safety_stakes'] = change_job.safety_stakes
        if change_install:
            form.initial['footer_dig_date'] = change_install.footer_dig_date
            form.initial['footer_inspection_date'] = change_install.footer_inspection_date
            form.initial['footer_pour_date'] = change_install.footer_pour_date
            form.initial['installer'] = change_install.installer
        if change_payment:
            form.initial['payments'] = change_payment.status
            form.initial['downpayment'] = change_payment.amount
            form.initial['price_breakdown'] = change_payment.breakdown
        lead_types = Lead.objects.filter(pk=leadpk).values('project_type',
                                                           'project_type__proj_type',
                                                           'project_type__group')
        initial_types = []
        for pt in lead_types:
            num = pt['project_type']
            initial_types.append(str(num))
            form.initial['project_type'] = initial_types

    context = {
        'form': form
    }

    context['job_files'] = Contracts.objects.filter(job=leadpk)
    context['job_photos'] = Pictures.objects.filter(job=leadpk)

    return render(request, 'edit_account.html', context)

@login_required
def archives(request):
    archives = Lead.objects.filter(lead_status = '3')

    if request.method == "POST":
        form = SortArchivesForm(request.POST)

        form.fields['sort_by'].required = False
        form.fields['order'].required = False

        if form.is_valid():
            sort_by = form.cleaned_data['sort_by']
            order = form.cleaned_data['order']

            if sort_by == "1": # customer name
                sortstring = 'client_id__last_name'
            if sort_by == "2": # date order complete
                sortstring = 'payment__archive_date'

            if order == "1":
                sortstring = '-'+sortstring

            archives = Lead.objects.filter(lead_status='3').order_by(sortstring)
    else:
        form = SortArchivesForm

    paginator = Paginator(archives, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        job_archive = paginator.page(page)
    except(EmptyPage, InvalidPage):
        job_archive = paginator.page(paginator.num_pages)

    context = {
        'job_archive': job_archive,
        'form': form
    }

    return render(request, 'archive.html', context)

class ArchiveDetailView(LoginRequiredMixin, DetailView):
    model = Lead
    template_name = 'archive_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ArchiveDetailView, self).get_context_data(**kwargs)
        context['job_files'] = Contracts.objects.filter(job=self.kwargs['pk'])
        context['job_photos'] = Pictures.objects.filter(job=self.kwargs['pk'])
        return context

@login_required
def edit_archive(request, leadpk):
    change_lead = Lead.objects.get(pk=leadpk)
    change_cust = Customer.objects.get(pk=change_lead.client_id.id)
    try:
        change_job = JobStatus.objects.get(lead=leadpk)
    except Exception as exception:
        change_job = False

    try:
        change_install = Installation.objects.get(job=leadpk)
    except Exception as exception:
        change_install = False

    try:
        change_payment = Payment.objects.get(job=leadpk)
    except Exception as exception:
        change_payment = False

    try:
        change_permit = Permit.objects.get(job=leadpk)
    except Exception as exception:
        change_permit = False

    if request.method == 'POST':
        form = EditAccountForm(request.POST, request.FILES)
        if form.is_valid():
      
            for contract in request.FILES.getlist('contracts'):
                new_file = Contracts(job=change_lead, document=contract)
                new_file.save()
            for photo in request.FILES.getlist('images'):
                add_photos = Pictures(job=change_lead, photos=photo)
                add_photos.save()

            name = form.cleaned_data['name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            address1 = form.cleaned_data['address1']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zip_code = form.cleaned_data['zip_code']
            nmc_street = form.cleaned_data['nmc_street']
            home_phone = form.cleaned_data['home_phone']
            cell_phone = form.cleaned_data['cell_phone']
            fax_number = form.cleaned_data['fax_number']
            email_address = form.cleaned_data['email']
            project_notes = form.cleaned_data['detailed_instr']
            if 'priority-choice' in request.POST:
                priority = True
            else:
                priority = False
            priority_notes = form.cleaned_data['priority_notes']
            salesperson = form.cleaned_data['salesperson']
            schedule_date = form.cleaned_data['schedule_date']
            project_type = form.cleaned_data['project_type']
            alumalattice = form.cleaned_data['alumalattice']
            association_approval = form.cleaned_data['association_approval']
            permits = form.cleaned_data['permits']
            materials_ordered = form.cleaned_data['materials_ordered']
            concrete_existing = form.cleaned_data['concrete_existing']
            footer_needed = form.cleaned_data['footer_needed']
            footer_dig_date = form.cleaned_data['footer_dig_date']
            footer_pour_date = form.cleaned_data['footer_pour_date']
            footer_inspection_date = form.cleaned_data['footer_inspection_date']
            safety_stakes = form.cleaned_data['safety_stakes']
            contract_amount = form.cleaned_data['contract_amount']
            price_breakdown = form.cleaned_data['price_breakdown']
            payments = form.cleaned_data['payments']
            downpayment = form.cleaned_data['downpayment']
            installer = form.cleaned_data['installer']

            change_cust.name = name
            change_cust.last_name = last_name
            change_cust.address = address
            change_cust.address1 = address1
            change_cust.city = city
            change_cust.state = state
            change_cust.zip_code = zip_code
            change_cust.nmc_street = nmc_street
            change_cust.home_phone = home_phone
            change_cust.cell_phone = cell_phone
            change_cust.email_address = email_address
            change_lead.project_notes = project_notes
            change_lead.salesperson = salesperson
            change_lead.project_type.set(project_type)
            change_lead.contract_amount = contract_amount
            change_lead.priority = priority
            change_lead.priority_msg = priority_notes
            change_lead.appointment_date = schedule_date
            change_lead.save()
            change_cust.save()

            if change_permit:
                change_permit.status = permits
                change_permit.save()
            else:
                change_permit = Permit(job=change_lead, status=permits)
                change_permit.save()

            if change_job:
                change_job.association_approval = association_approval
                change_job.materials_ordered = materials_ordered
                change_job.concrete_existing = concrete_existing
                change_job.footer_needed = footer_needed
                change_job.safety_stakes = safety_stakes
                change_job.alumalattice = alumalattice
                change_job.save()
            else:
                change_job = JobStatus(lead=change_lead,
                                    association_approval=association_approval,
                                    materials_ordered=materials_ordered,
                                    concrete_existing=concrete_existing,
                                    footer_needed=footer_needed,
                                    safety_stakes=safety_stakes,
                                    alumalattice=alumalattice)
                change_job.save()

            if change_install:
                change_install.footer_dig_date = footer_dig_date
                change_install.footer_pour_date = footer_pour_date
                change_install.footer_inspection_date = footer_inspection_date
                change_install.installer = installer
                change_install.save()
            else:
                change_install = Installation(job=change_lead, footer_dig_date=footer_dig_date,
                                            footer_inspection_date=footer_inspection_date,
                                            footer_pour_date=footer_pour_date, installer=installer)
                change_install.save()

            if change_payment:
                change_payment.status = payments
                change_payment.amount = downpayment
                change_payment.breakdown = price_breakdown
                change_payment.save()
            else:
                change_payment = Payment(job=change_lead, status=payments, amount=downpayment,
                                         breakdown=price_breakdown)
                change_payment.save()

            current_user = User.objects.get(username=request.user.username)
            new_entry_log = EntryLog(user_id=current_user,
                                        action="{} edited the lead with {}.".format(
                                            current_user.username,
                                            change_cust
                                        ),
                                        lead=change_lead,
                                        entry_date=timezone.now())
            new_entry_log.save()

            add_proj = Lead.objects.get(pk=change_lead.id)
            for p in project_type:
                pt = ProjectType.objects.get(pk=int(p))
                change_lead.project_type.add(pt)
                add_proj.save()

            return redirect('archives')
        else:
            print(form.errors)

    else:

        form = EditAccountForm(initial = {
            'name': change_cust.name,
            'last_name': change_cust.last_name,
            'address': change_cust.address,
            'address1': change_cust.address1,
            'city': change_cust.city,
            'state': change_cust.state,
            'zip_code': change_cust.zip_code,
            'nmc_street': change_cust.nmc_street,
            'home_phone': change_cust.home_phone,
            'cell_phone': change_cust.cell_phone,
            'email': change_cust.email_address,
            'detailed_instr': change_lead.project_notes,
            'priority': change_lead.priority,
            'priority_notes': change_lead.priority_msg,
            'salesperson': change_lead.salesperson,
            'project_type': Lead.objects.filter(pk=leadpk).values('project_type'),
            'contract_amount': change_lead.contract_amount,
            'schedule_date': change_lead.appointment_date
        })

        if change_job:
            form.initial['association_approval'] = change_job.association_approval
            form.initial['materials_ordered'] = change_job.materials_ordered
            form.initial['concrete_existing'] = change_job.concrete_existing
            form.initial['footer_needed'] = change_job.footer_needed
            form.initial['safety_stakes'] = change_job.safety_stakes
        if change_install:
            form.initial['footer_dig_date'] = change_install.footer_dig_date
            form.initial['footer_inspection_date'] = change_install.footer_inspection_date
            form.initial['footer_pour_date'] = change_install.footer_pour_date
            form.initial['installer'] = change_install.installer
        if change_payment:
            form.initial['payments'] = change_payment.status
            form.initial['downpayment'] = change_payment.amount
            form.initial['price_breakdown'] = change_payment.breakdown
        lead_types = Lead.objects.filter(pk=leadpk).values('project_type',
                                                           'project_type__proj_type',
                                                           'project_type__group')
        initial_types = []
        for pt in lead_types:
            num = pt['project_type']
            initial_types.append(str(num))
            form.initial['project_type'] = initial_types

    context = {
        'form': form
    }

    context['job_files'] = Contracts.objects.filter(job=leadpk)
    context['job_photos'] = Pictures.objects.filter(job=leadpk)

    return render(request, 'edit_archive.html', context)

@login_required
def services(request):
    service_list = Services.objects.filter(archive=False).order_by('-cust_called')

    paginator = Paginator(service_list, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        srv = paginator.page(page)
    except(EmptyPage, InvalidPage):
        srv = paginator.page(paginator.num_pages)

    context = {
        'srv': srv
    }

    return render(request, 'services.html', context)

@login_required
def new_service(request):
    if request.method == 'POST':

        form = ServiceForm(request.POST, request.FILES)

        form.fields['address'].required = False
        form.fields['name'].required = False
        form.fields['cust_called'].required = False
        form.fields['service_sched'].required = False
        form.fields['description'].required = False
        form.fields['phone_number'].required = False
        form.fields['installer'].required = False

        if form.is_valid():
            name = form.cleaned_data['name']
            address = form.cleaned_data['address']
            cust_called = form.cleaned_data['cust_called']
            service_sched = form.cleaned_data['service_sched']
            description = form.cleaned_data['description']
            phone_number = form.cleaned_data['phone_number']
            installer = form.cleaned_data['installer']

            service_call = Services(customer_name=name, customer_address=address,
                                    cust_called=cust_called, service_schedule=service_sched,
                                    description=description, phone_number=phone_number,
                                    installer=installer, archive=False)
            service_call.save()

            current_user = User.objects.get(username=request.user.username)
            new_entry_log = EntryLog(user_id=current_user,
                                     action="{} created a new service call, {}".format(
                                         current_user.username,
                                         name
                                     ),
                                     service=service_call,
                                     entry_date=timezone.now())
            new_entry_log.save()

            return redirect('services')

    else:
        form = ServiceForm()
        form.fields['address'].required = False
        form.fields['name'].required = False
        form.fields['cust_called'].required = False
        form.fields['service_sched'].required = False
        form.fields['description'].required = False
        form.fields['phone_number'].required = False
        form.fields['installer'].required = False

    context = {
        'form': form
    }

    return render(request, 'new_service.html', context)

@login_required
def send_to_service_archive(request, servpk):
    completed = Services.objects.get(pk=servpk)

    if request.method == "POST":
        completed.archive = True
        completed.save()

        current_user = User.objects.get(username=request.user.username)
        log_entry2 = EntryLog(user_id=current_user,
                                action="{} sent the service call with {} to archives.".format(
                                    current_user.username,
                                    completed.customer_name
                                ),
                                service=completed,
                                entry_date=timezone.now())
        log_entry2.save()

        return redirect('services')

    context = {
        'completed': completed
    }

    return render(request, 'send_to_service_archive.html', context)

class ServiceDetailView(LoginRequiredMixin, DetailView):
    model = Services
    template_name = 'service_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ServiceDetailView, self).get_context_data(**kwargs)
        return context

@login_required
def edit_service(request, servpk):
    srv = Services.objects.get(pk=servpk)

    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            address = form.cleaned_data['address']
            cust_called = form.cleaned_data['cust_called']
            service_sched = form.cleaned_data['service_sched']
            phone_number = form.cleaned_data['phone_number']
            description = form.cleaned_data['description']
            installer = form.cleaned_data['installer']

            if srv.archive == True:
                returnURL = 'service-archive'
            else:
                returnURL = 'services'

            srv.customer_name = name
            srv.customer_address = address
            srv.cust_called = cust_called
            srv.service_schedule = service_sched
            srv.phone_number = phone_number
            srv.description = description
            srv.installer = installer
            srv.save()

            current_user = User.objects.get(username=request.user.username)
            log_entry2 = EntryLog(user_id=current_user,
                                  action="{} edited the service call for {}.".format(
                                        current_user.username,
                                        srv.customer_name
                                    ),
                                  service=srv,
                                  entry_date=timezone.now())
            log_entry2.save()

            return redirect(returnURL)

    else:
        form = ServiceForm(initial = {
            'name': srv.customer_name,
            'address': srv.customer_address,
            'cust_called': srv.cust_called,
            'service_sched': srv.service_schedule,
            'phone_number': srv.phone_number,
            'description': srv.description,
            'installer': srv.installer
        })

        context = {
            'form': form
        }

    return render(request, 'edit_service.html', context)

@login_required
def delete_service(request, servpk):
    ex_serv = Services.objects.get(pk=servpk)

    if request.method == "POST":
        if ex_serv.archive == True:
            returnUrl = 'service-archive'
        else:
            returnUrl = 'services'

        current_user = User.objects.get(username=request.user.username)
        log_entry2 = EntryLog(user_id=current_user,
                              action="{} deleted the service call for {}.".format(
                                    current_user.username,
                                    ex_serv.customer_name
                                ),
                                entry_date=timezone.now())
        log_entry2.save()

        ex_serv.delete()

        return redirect(returnUrl)

    context = {
            'ex_serv': ex_serv
        }

    return render(request, 'delete_service.html', context)

@login_required
def service_archive(request):
    history = Services.objects.filter(archive=True)

    paginator = Paginator(history, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        hist = paginator.page(page)
    except:
        hist = paginator.page(paginator.num_pages)

    context = {
        'hist': hist
    }

    return render(request, 'service_archive.html', context)

@login_required
def send_to_service(request, servpk):
    not_done = Services.objects.get(pk=servpk)

    if request.method == "POST":
        not_done.archive = False
        not_done.save()

        current_user = User.objects.get(username=request.user.username)
        log_entry2 = EntryLog(user_id=current_user,
                                action="{} sent the service call with {} from archives back to active.".format(
                                    current_user.username,
                                    not_done.customer_name
                                ),
                                service=not_done,
                                entry_date=timezone.now())
        log_entry2.save()

        return redirect('service-archive')

    context = {
        'not_done': not_done
    }

    return render(request, 'send_to_service.html', context)

@login_required
def project_type(request):
    proj_list = ProjectType.objects.all()

    paginator = Paginator(proj_list, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        prj = paginator.page(page)
    except(EmptyPage, InvalidPage):
        prj = paginator.page(paginator.num_pages)

    context = {
        'prj': prj
    }
    return render(request, 'project_type.html', context)

@login_required
def new_project_type(request):
    if request.method == 'POST':

        form = NewProjectTypeForm(request.POST)
        if form.is_valid():
            project_type = form.cleaned_data['project_type']
            project_category = form.cleaned_data['project_category']

            pt = ProjectType(proj_type=project_type,
                             group=project_category)
            pt.save()

            current_user = User.objects.get(username=request.user.username)
            log_entry2 = EntryLog(user_id=current_user,
                                  action="{} created a new project type: {}.".format(
                                        current_user.username,
                                        pt
                                    ),
                                  entry_date=timezone.now())
            log_entry2.save()

            return redirect('project-type')

    else:
        form = NewProjectTypeForm()

    context = {
        'form': form
    }

    return render(request, 'new_project_type.html', context=context)

@login_required
def edit_project_type(request, typepk):
    current_type = ProjectType.objects.get(pk=typepk)

    if request.method == "POST":
        form = NewProjectTypeForm(request.POST)
        if form.is_valid():
            if 'activebox' in request.POST:
                current_type.active=True
            else:
                current_type.active=False

            project_type = form.cleaned_data['project_type']
            project_category = form.cleaned_data['project_category']

            current_type.proj_type = project_type
            current_type.group = project_category
            current_type.save()

            current_user = User.objects.get(username=request.user.username)
            log_entry2 = EntryLog(user_id=current_user,
                                  action="{} edited the {} project type.".format(
                                        current_user.username,
                                        current_type
                                    ),
                                  entry_date=timezone.now())
            log_entry2.save()

            return redirect('project-type')

    else:
        form = NewProjectTypeForm(initial = {'project_type': current_type.proj_type,
                                             'project_category': current_type.group})

    context = {
        'current_type': current_type,
        'form': form
    }

    return render(request, 'edit_project_type.html', context=context)

@login_required
def delete_project_type(request, typepk):
    pro_t = ProjectType.objects.get(pk=typepk)

    if request.method == "POST":
        current_user = User.objects.get(username=request.user.username)
        log_entry2 = EntryLog(user_id=current_user,
                                action="{} deleted the {} project type.".format(
                                    current_user.username,
                                    pro_t
                                ),
                                entry_date=timezone.now())
        log_entry2.save()

        pro_t.delete()

        return redirect('project-type')

    context = {
        'pro_t': pro_t
    }

    return render(request, 'confirm_delete_project_type.html', context)

@login_required
def my_payroll(request):
    storage = messages.get_messages(request)
    storage.used = True
    if User.objects.filter(pk=request.user.id, groups__name="admin").exists():
        payItems = Payroll.objects.all().order_by('-payroll_id')
    else:
        payItems = Payroll.objects.filter(user=request.user.id).order_by('-payroll_id')

    try:
        documents = Employee_Documents.objects.first()
    except:
        documents = False
    if documents:
        try:
            employee_files = Employee_Files.objects.filter(record=documents.id)
        except:
            employee_files = False
    else:
        employee_files = False
    if request.method == "POST":
        form = SortPayrollForm(request.POST)

        form.fields['order'].required = False

        if form.is_valid():
            order = form.cleaned_data['order']

            if order == "1":
                payItems = payItems.order_by('-payroll_id')
            if order == "2":
                payItems = payItems.order_by('payroll_id')

    else:
        form = SortPayrollForm

    paginator = Paginator(payItems, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        payroll_item = paginator.page(page)
    except(EmptyPage, InvalidPage):
        payroll_item = paginator.page(paginator.num_pages)
    context = {
        'payroll_item': payroll_item,
        'form': form,
        'documents': documents,
        'employee_files': employee_files
    }

    return render(request, 'my_payroll.html', context)

@login_required
def edit_payroll(request, paypk):
    payChange = Payroll.objects.get(pk=paypk)
    staff_mem = ''
    form = ''
    formset = ''
    context = {}

    if request.method == "POST":
        if payChange.user.groups.filter(name="installer").exists():
            form = InstallerForm(request.POST, request.FILES)
            installerPay = Installer_Payroll.objects.get(job=payChange.id)
            if form.is_valid():
                job_name = form.cleaned_data['job_name']
                date_completed = form.cleaned_data['date_completed']
                job_address = form.cleaned_data['job_address']
                description = form.cleaned_data['description']
                helper = form.cleaned_data['helper']
                helper_name = form.cleaned_data['helper_name']
                work_performed = form.cleaned_data['work_performed']
                amount_owed = form.cleaned_data['amount_owed']

                installerPay.job_name = job_name
                installerPay.job_address = job_address
                installerPay.description = description
                installerPay.date_completed = date_completed
                installerPay.helper = helper
                installerPay.helper_name = helper_name
                installerPay.work_performed = work_performed
                installerPay.amount_owed = amount_owed
                installerPay.save()

                files_pay = Installer_Payroll.objects.get(pk=installerPay.job)
                for contract in request.FILES.getlist('job_files'):
                    add_files = Installer_Payroll(job=files_pay, job_file=contract)
                    add_files.save()
                
        if payChange.user.groups.filter(name="salesperson").exists():
            formset = SalesEditFormSet(request.POST)
            form = SalespersonPayEditForm(request.POST)
            if form.is_valid():
                sales_text = request.POST.get('salesperson')
                date_added = request.POST.get('date_added')

                if formset.is_valid():
                    for f in formset:
                        f.save(commit=False)
                        sales_job_id = f.cleaned_data['id']
                        # sales_text = form.cleaned_data['salesperson']
                        job_name = f.cleaned_data['job_name']
                        # date_added = form.cleaned_data['date_added']
                        status = f.cleaned_data['status']
                        contract_amount = f.cleaned_data['contract_amount']
                        commission = f.cleaned_data['commission']
                        if sales_job_id == None:
                            new_payroll = Sales_Payroll(job=payChange, job_name=job_name,
                                salesperson=sales_text,
                                date_added=date_added,
                                status=status,
                                contract_amount=contract_amount,
                                commission=commission)
                            new_payroll.save()
                        else:
                            sales_pay = Sales_Payroll.objects.get(id=sales_job_id.id)

                            sales_pay.job_name=job_name
                            sales_pay.salesperson=sales_text
                            sales_pay.date_added=date_added
                            sales_pay.status=status
                            sales_pay.contract_amount=contract_amount
                            sales_pay.commission=commission
                            sales_pay.save()

            #     else:
            #         print(formset.errors)
            #         return redirect(reverse('payroll-detail', kwargs={'paypk': payChange.id}))
            # else:
            # return redirect(reverse('payroll-detail', kwargs={'paypk': payChange.id}))


            # if formset.is_valid():
            #     job_name = form.cleaned_data['job_name']
            #     date_added = form.cleaned_data['date_added']
            #     status = form.cleaned_data['status']
            #     contract_amount = form.cleaned_data['contract_amount']
            #     commission = form.cleaned_data['commission']

            #     payChange.job_name = job_name
            #     payChange.date_added = date_added
            #     payChange.status = status
            #     payChange.contract_amount = contract_amount
            #     payChange.commission = commission
            #     payChange.save()

        if payChange.user.groups.filter(name="staff").exists():
            form = StaffForm(request.POST, request.FILES)
            staffPay = Staff_Payroll.objects.get(job=payChange.id)
            if form.is_valid():
                monday_date = form.cleaned_data['monday_date']
                monday_in_hr = form.cleaned_data['monday_in_hr']
                monday_in_min = form.cleaned_data['monday_in_min']
                monday_out_hr = form.cleaned_data['monday_out_hr']
                monday_out_min = form.cleaned_data['monday_out_min']
                monday_tot = form.cleaned_data['monday_tot']
                tuesday_date = form.cleaned_data['tuesday_date']
                tuesday_in_hr = form.cleaned_data['tuesday_in_hr']
                tuesday_in_min = form.cleaned_data['tuesday_in_min']
                tuesday_out_hr = form.cleaned_data['tuesday_out_hr']
                tuesday_out_min = form.cleaned_data['tuesday_out_min']
                tuesday_tot = form.cleaned_data['tuesday_tot']
                wednesday_date = form.cleaned_data['wednesday_date']
                wednesday_in_hr = form.cleaned_data['wednesday_in_hr']
                wednesday_in_min = form.cleaned_data['wednesday_in_min']
                wednesday_out_hr = form.cleaned_data['wednesday_out_hr']
                wednesday_out_min = form.cleaned_data['wednesday_out_min']
                wednesday_tot = form.cleaned_data['wednesday_tot']
                thursday_date = form.cleaned_data['thursday_date']
                thursday_in_hr = form.cleaned_data['thursday_in_hr']
                thursday_in_min = form.cleaned_data['thursday_in_min']
                thursday_out_hr = form.cleaned_data['thursday_out_hr']
                thursday_out_min = form.cleaned_data['thursday_out_min']
                thursday_tot = form.cleaned_data['thursday_tot']
                friday_date = form.cleaned_data['friday_date']
                friday_in_hr = form.cleaned_data['friday_in_hr']
                friday_in_min = form.cleaned_data['friday_in_min']
                friday_out_hr = form.cleaned_data['friday_out_hr']
                friday_out_min = form.cleaned_data['friday_out_min']
                friday_tot = form.cleaned_data['friday_tot']
                saturday_date = form.cleaned_data['saturday_date']
                saturday_in_hr = form.cleaned_data['saturday_in_hr']
                saturday_in_min = form.cleaned_data['saturday_in_min']
                saturday_out_hr = form.cleaned_data['saturday_out_hr']
                saturday_out_min = form.cleaned_data['saturday_out_min']
                saturday_tot = form.cleaned_data['saturday_tot']
                sunday_date = form.cleaned_data['sunday_date']
                sunday_in_hr = form.cleaned_data['sunday_in_hr']
                sunday_in_min = form.cleaned_data['sunday_in_min']
                sunday_out_hr = form.cleaned_data['sunday_out_hr']
                sunday_out_min = form.cleaned_data['sunday_out_min']
                sunday_tot = form.cleaned_data['sunday_tot']
                weekly_hours = form.cleaned_data['weekly_hours']
                hourly_rate = form.cleaned_data['hourly_rate']
                week_start_date = form.cleaned_data['week_start_date']
                payroll_notes = form.cleaned_data['payroll_notes']
                upload_file = form.cleaned_data['upload_file']

                staffPay.monday_date = monday_date
                staffPay.monday_in_hr = monday_in_hr
                staffPay.monday_in_min = monday_in_min
                staffPay.monday_out_hr = monday_out_hr
                staffPay.monday_out_min = monday_out_min
                staffPay.monday_tot = monday_tot
                staffPay.tuesday_date = tuesday_date
                staffPay.tuesday_in_hr = tuesday_in_hr
                staffPay.tuesday_in_min = tuesday_in_min
                staffPay.tuesday_out_hr = tuesday_out_hr
                staffPay.tuesday_out_min = tuesday_out_min
                staffPay.tuesday_tot = tuesday_tot
                staffPay.wednesday_date = wednesday_date
                staffPay.wednesday_in_hr = wednesday_in_hr
                staffPay.wednesday_in_min = wednesday_in_min
                staffPay.wednesday_out_hr = wednesday_out_hr
                staffPay.wednesday_out_min = wednesday_out_min
                staffPay.wednesday_tot = wednesday_tot
                staffPay.thursday_date = thursday_date
                staffPay.thursday_in_hr = thursday_in_hr
                staffPay.thursday_in_min = thursday_in_min
                staffPay.thursday_out_hr = thursday_out_hr
                staffPay.thursday_out_min = thursday_out_min
                staffPay.thursday_tot = thursday_tot
                staffPay.friday_date = friday_date
                staffPay.friday_in_hr = friday_in_hr
                staffPay.friday_in_min = friday_in_min
                staffPay.friday_out_hr = friday_out_hr
                staffPay.friday_out_min = friday_out_min
                staffPay.friday_tot = friday_tot
                staffPay.saturday_date = saturday_date
                staffPay.saturday_in_hr = saturday_in_hr
                staffPay.saturday_in_min = saturday_in_min
                staffPay.saturday_out_hr = saturday_out_hr
                staffPay.saturday_out_min = saturday_out_min
                staffPay.saturday_tot = saturday_tot
                staffPay.sunday_date = sunday_date
                staffPay.sunday_in_hr = sunday_in_hr
                staffPay.sunday_in_min = sunday_in_min
                staffPay.sunday_out_hr = sunday_out_hr
                staffPay.sunday_out_min = sunday_out_min
                staffPay.sunday_tot = sunday_tot
                staffPay.weekly_hours = weekly_hours
                staffPay.hourly_rate = hourly_rate
                staffPay.week_start_date = week_start_date
                staffPay.payroll_notes = payroll_notes
                staffPay.upload_file = upload_file
                staffPay.save()

        current_user = User.objects.get(username=request.user.username)
        log_entry2 = EntryLog(user_id=current_user,
                              action="{} edited payroll item {} for {}.".format(
                                    current_user.username,
                                    payChange.payroll_id,
                                    payChange.user.first_name+" "+payChange.user.last_name
                                ),
                              payroll=payChange,
                              entry_date=timezone.now())
        log_entry2.save()

        if 'submit' in request.POST:
            return redirect('confirm-submit-to-process', paypk=payChange.id)
        else:
            messages.success(request, 'successfully inserted')
            return redirect(reverse('payroll-detail', kwargs={'paypk': payChange.id}))

    else:
        if payChange.user.groups.filter(name="installer").exists():
            form = InstallerForm(initial = {'job_file': payChange.installer_payroll.job_file,
                                            'job_name': payChange.installer_payroll.job_name,
                                            'date_completed': payChange.installer_payroll.date_completed,
                                            'job_address': payChange.installer_payroll.job_address,
                                            'description': payChange.installer_payroll.description,
                                            'helper': payChange.installer_payroll.helper,
                                            'helper_name': payChange.installer_payroll.helper_name,
                                            'work_performed': payChange.installer_payroll.work_performed,
                                            'amount_owed': payChange.installer_payroll.amount_owed})
            html = 'submit_installer.html'
            context['installer'] = payChange.user
        if payChange.user.groups.filter(name="salesperson").exists():
            sales_jobs = Sales_Payroll.objects.filter(job=payChange.id)
            sales_jobs_ex = sales_jobs.first()
            formset = SalesEditFormSet(queryset = Sales_Payroll.objects.filter(job=payChange.id))
            print(formset.forms[0])
            print('------')
            print(formset.forms[0].hidden_fields())
            form = SalespersonPayEditForm(initial = {
                'salesperson': sales_jobs_ex.salesperson,
                'date_added': sales_jobs_ex.date_added
            })
            html = 'submit_sales.html'
            context['salesperson'] = payChange.user
        if payChange.user.groups.filter(name="staff").exists():
            edit_staffpay = Staff_Payroll.objects.get(job=payChange.id)
            form = StaffForm(initial = {
                'monday_date': edit_staffpay.monday_date,
                'monday_in_hr': edit_staffpay.monday_in_hr,
                'monday_in_min': edit_staffpay.monday_in_min,
                'monday_out_hr': edit_staffpay.monday_out_hr,
                'monday_out_min': edit_staffpay.monday_out_min,
                'monday_tot': edit_staffpay.monday_tot,
                'tuesday_date': edit_staffpay.tuesday_date,
                'tuesday_in_hr': edit_staffpay.tuesday_in_hr,
                'tuesday_in_min': edit_staffpay.tuesday_in_min,
                'tuesday_out_hr': edit_staffpay.tuesday_out_hr,
                'tuesday_out_min': edit_staffpay.tuesday_out_min,
                'tuesday_tot': edit_staffpay.tuesday_tot,
                'wednesday_date': edit_staffpay.wednesday_date,
                'wednesday_in_hr': edit_staffpay.wednesday_in_hr,
                'wednesday_in_min': edit_staffpay.wednesday_in_min,
                'wednesday_out_hr': edit_staffpay.wednesday_out_hr,
                'wednesday_out_min': edit_staffpay.wednesday_out_min,
                'wednesday_tot': edit_staffpay.wednesday_tot,
                'thursday_date': edit_staffpay.thursday_date,
                'thursday_in_hr': edit_staffpay.thursday_in_hr,
                'thursday_in_min': edit_staffpay.thursday_in_min,
                'thursday_out_hr': edit_staffpay.thursday_out_hr,
                'thursday_out_min': edit_staffpay.thursday_out_min,
                'thursday_tot': edit_staffpay.thursday_tot,
                'friday_date': edit_staffpay.friday_date,
                'friday_in_hr': edit_staffpay.friday_in_hr,
                'friday_in_min': edit_staffpay.friday_in_min,
                'friday_out_hr': edit_staffpay.friday_out_hr,
                'friday_out_min': edit_staffpay.friday_out_min,
                'friday_tot': edit_staffpay.friday_tot,
                'saturday_date': edit_staffpay.saturday_date,
                'saturday_in_hr': edit_staffpay.saturday_in_hr,
                'saturday_in_min': edit_staffpay.saturday_in_min,
                'saturday_out_hr': edit_staffpay.saturday_out_hr,
                'saturday_out_min': edit_staffpay.saturday_out_min,
                'saturday_tot': edit_staffpay.saturday_tot,
                'sunday_date': edit_staffpay.sunday_date,
                'sunday_in_hr': edit_staffpay.sunday_in_hr,
                'sunday_in_min': edit_staffpay.sunday_in_min,
                'sunday_out_hr': edit_staffpay.sunday_out_hr,
                'sunday_out_min': edit_staffpay.sunday_out_min,
                'sunday_tot': edit_staffpay.sunday_tot,
                'weekly_hours': edit_staffpay.weekly_hours,
                'hourly_rate': edit_staffpay.hourly_rate,
                'week_start_date': edit_staffpay.week_start_date,
                'payroll_notes': edit_staffpay.payroll_notes,
                'upload_file': edit_staffpay.upload_file
            })
            html = 'submit_staff.html'
            context['staff_mem'] = payChange.user

    context['form'] = form
    context['formset'] = formset
    context['pay_change'] = payChange

    return render(request, html, context=context)

@login_required
def submit_payroll(request):
    installers = User.objects.filter(groups__name='installer')
    salesperson = User.objects.filter(groups__name='salesperson')
    staff = User.objects.filter(groups__name='staff')

    context = {
        'installers': installers,
        'salespeople': salesperson,
        'staff': staff
    }

    return render(request, 'submit_payroll.html', context)

@login_required
def submit_installer(request, userid):
    installer = User.objects.get(pk=userid)

    if request.method == "POST":
        form = InstallerForm(request.POST, request.FILES)
        if form.is_valid():
            job_name = form.cleaned_data['job_name']
            date_completed = form.cleaned_data['date_completed']
            job_address = form.cleaned_data['job_address']
            description = form.cleaned_data['description']
            helper = form.cleaned_data['helper']
            helper_name = form.cleaned_data['helper_name']
            work_performed = form.cleaned_data['work_performed']
            amount_owed = form.cleaned_data['amount_owed']

            new_job = Payroll(archived=False, processed=False, user=installer,
                              date_entered=datetime.now(), submitted=False)
            new_job.save()
            new_job.payroll_id = new_job.id + 2000
            new_job.save()

            new_payroll = Installer_Payroll(job=new_job, job_name=job_name,
                                            date_completed=date_completed, job_address=job_address,
                                            description=description, helper=helper,
                                            helper_name=helper_name, work_performed=work_performed,
                                            amount_owed=amount_owed)
            new_payroll.save()

            files_pay = Installer_Payroll.objects.get(pk=new_payroll.job)
            for contract in request.FILES.getlist('job_files'):
                add_files = Installer_Payroll(job=files_pay, job_file=contract)
                add_files.save()

            current_user = User.objects.get(username=request.user.username)
            log_entry2 = EntryLog(user_id=current_user,
                                action="{} submitted payroll item {} for {}.".format(
                                        current_user.username,
                                        new_job.payroll_id,
                                        new_job.user.first_name+" "+new_job.user.last_name
                                    ),
                                payroll=new_job,
                                entry_date=timezone.now())
            log_entry2.save()

            if 'submit' in request.POST:
                return redirect('confirm-submit-to-process', paypk=new_job.id)

            else:
                messages.success(request, 'successfully inserted')
                return redirect('payroll-detail', paypk=new_job.id)

    else:
        form = InstallerForm()

    context = {
        'form': form,
        'installer': installer
    }

    return render(request, 'submit_installer.html', context=context)

@login_required
def submit_staff(request, userid):
    staff_mem = User.objects.get(pk=userid)
    if request.method == "POST":
        form = StaffForm(request.POST, request.FILES)
        if form.is_valid():

            monday_date = form.cleaned_data['monday_date']
            monday_in_hr = form.cleaned_data['monday_in_hr']
            monday_in_min = form.cleaned_data['monday_in_min']
            monday_out_hr = form.cleaned_data['monday_out_hr']
            monday_out_min = form.cleaned_data['monday_out_min']
            monday_tot = form.cleaned_data['monday_tot']
            tuesday_date = form.cleaned_data['tuesday_date']
            tuesday_in_hr = form.cleaned_data['tuesday_in_hr']
            tuesday_in_min = form.cleaned_data['tuesday_in_min']
            tuesday_out_hr = form.cleaned_data['tuesday_out_hr']
            tuesday_out_min = form.cleaned_data['tuesday_out_min']
            tuesday_tot = form.cleaned_data['tuesday_tot']
            wednesday_date = form.cleaned_data['wednesday_date']
            wednesday_in_hr = form.cleaned_data['wednesday_in_hr']
            wednesday_in_min = form.cleaned_data['wednesday_in_min']
            wednesday_out_hr = form.cleaned_data['wednesday_out_hr']
            wednesday_out_min = form.cleaned_data['wednesday_out_min']
            wednesday_tot = form.cleaned_data['wednesday_tot']
            thursday_date = form.cleaned_data['thursday_date']
            thursday_in_hr = form.cleaned_data['thursday_in_hr']
            thursday_in_min = form.cleaned_data['thursday_in_min']
            thursday_out_hr = form.cleaned_data['thursday_out_hr']
            thursday_out_min = form.cleaned_data['thursday_out_min']
            thursday_tot = form.cleaned_data['thursday_tot']
            friday_date = form.cleaned_data['friday_date']
            friday_in_hr = form.cleaned_data['friday_in_hr']
            friday_in_min = form.cleaned_data['friday_in_min']
            friday_out_hr = form.cleaned_data['friday_out_hr']
            friday_out_min = form.cleaned_data['friday_out_min']
            friday_tot = form.cleaned_data['friday_tot']
            saturday_date = form.cleaned_data['saturday_date']
            saturday_in_hr = form.cleaned_data['saturday_in_hr']
            saturday_in_min = form.cleaned_data['saturday_in_min']
            saturday_out_hr = form.cleaned_data['saturday_out_hr']
            saturday_out_min = form.cleaned_data['saturday_out_min']
            saturday_tot = form.cleaned_data['saturday_tot']
            sunday_date = form.cleaned_data['sunday_date']
            sunday_in_hr = form.cleaned_data['sunday_in_hr']
            sunday_in_min = form.cleaned_data['sunday_in_min']
            sunday_out_hr = form.cleaned_data['sunday_out_hr']
            sunday_out_min = form.cleaned_data['sunday_out_min']
            sunday_tot = form.cleaned_data['sunday_tot']
            hourly_rate = form.cleaned_data['hourly_rate']
            weekly_start_date = form.cleaned_data['week_start_date']
            weekly_hours = form.cleaned_data['weekly_hours']
            payroll_notes = form.cleaned_data['payroll_notes']

            new_job = Payroll(archived=False, processed=False, user=staff_mem,
                              date_entered=datetime.now(), submitted=False)
            new_job.save()
            new_job.payroll_id = new_job.id + 2000
            new_job.save()

            new_payroll = Staff_Payroll(job=new_job,payroll_notes=payroll_notes, weekly_hours=weekly_hours,
                                        week_start_date=weekly_start_date, hourly_rate=hourly_rate,
                                        monday_date=monday_date, monday_in_hr=monday_in_hr,
                                        monday_in_min=monday_in_min, monday_out_hr=monday_out_hr,
                                        monday_out_min=monday_out_min, monday_tot=monday_tot,
                                        tuesday_date=tuesday_date, tuesday_in_hr=tuesday_in_hr,
                                        tuesday_in_min=tuesday_in_min, tuesday_out_hr=tuesday_out_hr,
                                        tuesday_out_min=tuesday_out_min, tuesday_tot=tuesday_tot,
                                        wednesday_date=wednesday_date, wednesday_in_hr=wednesday_in_hr,
                                        wednesday_in_min=wednesday_in_min, wednesday_out_hr=wednesday_out_hr,
                                        wednesday_out_min=wednesday_out_min, wednesday_tot=wednesday_tot,
                                        thursday_date=thursday_date, thursday_in_hr=thursday_in_hr,
                                        thursday_in_min=thursday_in_min, thursday_out_hr=thursday_out_hr,
                                        thursday_out_min=thursday_out_min, thursday_tot=thursday_tot,
                                        friday_date=friday_date, friday_in_hr=friday_in_hr,
                                        friday_in_min=friday_in_min, friday_out_hr=friday_out_hr,
                                        friday_out_min=friday_out_min, friday_tot=friday_tot,
                                        saturday_date=saturday_date, saturday_in_hr=saturday_in_hr,
                                        saturday_in_min=saturday_in_min, saturday_out_hr=saturday_out_hr,
                                        saturday_out_min=saturday_out_min, saturday_tot=saturday_tot,
                                        sunday_date=sunday_date, sunday_in_hr=sunday_in_hr,
                                        sunday_in_min=sunday_in_min, sunday_out_hr=sunday_out_hr,
                                        sunday_out_min=sunday_out_min, sunday_tot=sunday_tot)
            new_payroll.save()

            current_user = User.objects.get(username=request.user.username)
            log_entry2 = EntryLog(user_id=current_user,
                                  action="{} submitted payroll item {} for {}.".format(
                                    current_user.username,
                                    new_job.payroll_id,
                                    new_job.user.first_name+" "+new_job.user.last_name
                                ),
                              payroll=new_job,
                              entry_date=timezone.now())
            log_entry2.save()

            files_pay = Staff_Payroll.objects.get(pk=new_payroll.job)
            for contract in request.FILES.getlist('upload_files'):
                add_files = Staff_Payroll(job=files_pay, upload_file=contract)
                add_files.save()

            if 'submit' in request.POST:
                return redirect('confirm-submit-to-process', paypk=new_job.id)


            else:
                messages.success(request, 'successfully inserted')
                return redirect('payroll-detail', paypk=new_job.id)

            return redirect('my-payroll')

    form = StaffForm()

    context = {
        'form': form,
        'staff_mem': staff_mem
    }

    return render(request, 'submit_staff.html', context=context)

@login_required
def submit_sales(request, userid):
    associate = User.objects.get(pk=userid)
    goto = ''

    if request.method == "POST":
        formset = SalesFormSet(request.POST)
        # form = SalesForm(request.POST)
        if formset.is_valid():
            sales_text = request.POST.get('salesperson')
            date_added = request.POST.get('date_added')

            new_job = Payroll(archived=False, processed=False, user=associate,
            date_entered=datetime.now(), submitted=False)
            new_job.save()
            new_job.payroll_id = new_job.id + 2000
            new_job.save()

            current_user = User.objects.get(username=request.user.username)
            log_entry2 = EntryLog(user_id=current_user,
                                action="{} submitted payroll item {} for {}.".format(
                                        current_user.username,
                                        new_job.payroll_id,
                                        new_job.user.first_name+" "+new_job.user.last_name
                                    ),
                                payroll=new_job,
                                entry_date=timezone.now())
            log_entry2.save()

            for f in formset:
                f.save(commit=False)
                try:
                    id = f.cleaned_data['id']
                except KeyError:
                    id = None
                try:
                    job_name = f.cleaned_data['job_name']
                except KeyError:
                    job_name = ''
                try:
                    status = f.cleaned_data['status']
                except KeyError:
                    status = ''
                try:
                    contract_amount = f.cleaned_data['contract_amount']
                except KeyError:
                    contract_amount = 0
                try:
                    commission = f.cleaned_data['commission']
                except KeyError:
                    commission = 0

                if id == None:
                    new_payroll = Sales_Payroll(job=new_job, job_name=job_name,
                                salesperson=sales_text,
                                date_added=date_added,
                                status=status,
                                contract_amount=contract_amount,
                                commission=commission)
                    new_payroll.save()
                    goto = new_payroll.job.id

                else:
                    edit_sale_pay = Sales_Payroll.objects.get(pk='id')
                    edit_sale_pay.job_name = job_name
                    edit_sale_pay.salesperson = sales_text
                    edit_sale_pay.date_added = date_added
                    edit_sale_pay.status = status
                    edit_sale_pay.status = contract_amount
                    edit_sale_pay.commission = commission
                    edit_sale_pay.save()
                    goto = edit_sale_pay.job.id

            messages.success(request, 'successfully inserted')

            if 'submit' in request.POST:
                return redirect('confirm-submit-to-process', paypk=new_job.id)

            return redirect('payroll-detail', paypk=goto)

        else:
            messages.error(request, "Could not submit record. Please enter job name.")

    else:
        # form = SalesForm()
        formset = SalesFormSet(queryset=Sales_Payroll.objects.none())
        form = SalesForm()

        context = {
            'form': form,
            'formset': formset,
            'salesperson': associate
        }

        return render(request, 'submit_sales.html', context=context)

@login_required
def confirm_submit_to_process(request, paypk):
    pay_submit = Payroll.objects.get(id=paypk)
    if request.method == "POST":
            current_user = User.objects.get(username=request.user.username)
            log_entry2 = EntryLog(user_id=current_user,
                                    action="{} submitted payroll item {} for processing.".format(
                                        current_user.username,
                                        pay_submit.payroll_id
                                    ),
                                    entry_date=timezone.now(),
                                    payroll=pay_submit)
            log_entry2.save()

            pay_submit.submitted = True
            pay_submit.save()

            return redirect('my-payroll')
    else:

        context = {'pay_submit': pay_submit}

        return render(request, 'confirm_submit_to_process.html', context=context)

@login_required
def payroll_to_process(request):
    storage = messages.get_messages(request)
    storage.used = True

    if User.objects.filter(pk=request.user.id, groups__name="admin").exists():
        to_process = Payroll.objects.filter(processed=False, submitted=True).order_by('-payroll_id')
    else:
        to_process = Payroll.objects.filter(user=request.user.id,
                                            processed=False,
                                            submitted=True).order_by('-payroll_id')

    if request.method == "POST":
        form = SortPayProcessForm(request.POST)
        if form.is_valid():
            form.fields['sort_by'].required = False
            form.fields['order'].required = False

            if form.is_valid():
                sort_by = form.cleaned_data['sort_by']
                order = form.cleaned_data['order']

                if sort_by == "1": # payroll id
                    to_process = Payroll.objects.filter(processed=False).order_by('-payroll_id')
                if sort_by == "2": # installer
                    to_process = to_process.filter(user__groups__name='installer')
                if sort_by == "3": # staff
                    to_process = to_process.filter(user__groups__name='staff')
                if sort_by == "4": # salesperson
                    to_process = to_process.filter(user__groups__name='salesperson')
                if order == "1":
                    to_process = to_process.order_by('-payroll_id')
                if order == "2":
                    to_process = to_process.order_by('payroll_id')

    else:
        form = SortPayProcessForm()

    paginator = Paginator(to_process, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        pay = paginator.page(page)
    except(EmptyPage, InvalidPage):
        pay = paginator.page(paginator.num_pages)

    context = {
        'pay': pay,
        'form': form
    }

    return render(request, 'payroll_to_process.html', context)

@login_required
def edit_process_payroll(request, paypk):
    payChange = Payroll.objects.get(pk=paypk)
    staff_mem = ''
    form = ''
    formset = ''

    if request.method == "POST":
        current_user = User.objects.get(username=request.user.username)
        log_entry2 = EntryLog(user_id=current_user,
                              action="{} edited payroll item {} for {}.".format(
                                    current_user.username,
                                    payChange.payroll_id,
                                    payChange.user.first_name+" "+payChange.user.last_name
                                ),
                              payroll=payChange,
                              entry_date=timezone.now())
        log_entry2.save()

        if payChange.user.groups.filter(name="installer").exists():
            form = InstallerForm(request.POST, request.FILES)
            installerPay = Installer_Payroll.objects.get(job=payChange.id)
            if form.is_valid():
                job_name = form.cleaned_data['job_name']
                date_completed = form.cleaned_data['date_completed']
                job_address = form.cleaned_data['job_address']
                description = form.cleaned_data['description']
                helper = form.cleaned_data['helper']
                helper_name = form.cleaned_data['helper_name']
                work_performed = form.cleaned_data['work_performed']
                amount_owed = form.cleaned_data['amount_owed']

                installerPay.job_name = job_name
                installerPay.job_address = job_address
                installerPay.description = description
                installerPay.date_completed = date_completed
                installerPay.helper = helper
                installerPay.helper_name = helper_name
                installerPay.work_performed = work_performed
                installerPay.amount_owed = amount_owed
                installerPay.save()

                files_pay = Installer_Payroll.objects.get(pk=installerPay.job)
                for contract in request.FILES.getlist('job_files'):
                    add_files = Installer_Payroll(job=files_pay, job_file=contract)
                    add_files.save()

        if payChange.user.groups.filter(name="salesperson").exists():
            formset = SalesEditFormSet(request.POST)
            form = SalespersonPayEditForm(request.POST)
            if form.is_valid():
                sales_text = request.POST.get('salesperson')
                date_added = request.POST.get('date_added')

                if formset.is_valid():
                    for form in formset:
                        form.save(commit=False)
                        sales_job_id = form.cleaned_data['id']
                        job_name = form.cleaned_data['job_name']
                        status = form.cleaned_data['status']
                        contract_amount = form.cleaned_data['contract_amount']
                        commission = form.cleaned_data['commission']

                        # edit_sales_pay = Sales_Payroll.objects.get(id=sales_job_id)

                        # edit_sales_pay.job_name = job_name
                        # edit_sales_pay.date_added = date_added
                        # edit_sales_pay.status = status
                        # edit_sales_pay.contract_amount = contract_amount
                        # edit_sales_pay.commission = commission
                        # edit_sales_pay.save()
                        if sales_job_id == None:
                            new_payroll = Sales_Payroll(job=payChange, job_name=job_name,
                                salesperson=sales_text,
                                date_added=date_added,
                                status=status,
                                contract_amount=contract_amount,
                                commission=commission)
                            new_payroll.save()
                        else:
                            edit_pay = Sales_Payroll.objects.get(id=sales_job_id.id)

                            edit_pay.job_name=job_name
                            edit_pay.salesperson=sales_text
                            edit_pay.date_added=date_added
                            edit_pay.status=status
                            edit_pay.contract_amount=contract_amount
                            edit_pay.commission=commission
                            edit_pay.save()


                        messages.success(request, 'successfully inserted')

            else:
                return redirect(reverse('edit-process-payroll', kwargs={'paypk': payChange.id}))

        if payChange.user.groups.filter(name="staff").exists():
            form = StaffForm(request.POST, request.FILES)
            staffPay = Staff_Payroll.objects.get(job=payChange.id)
            if form.is_valid():
                monday_date = form.cleaned_data['monday_date']
                monday_in_hr = form.cleaned_data['monday_in_hr']
                monday_in_min = form.cleaned_data['monday_in_min']
                monday_out_hr = form.cleaned_data['monday_out_hr']
                monday_out_min = form.cleaned_data['monday_out_min']
                monday_tot = form.cleaned_data['monday_tot']
                tuesday_date = form.cleaned_data['tuesday_date']
                tuesday_in_hr = form.cleaned_data['tuesday_in_hr']
                tuesday_in_min = form.cleaned_data['tuesday_in_min']
                tuesday_out_hr = form.cleaned_data['tuesday_out_hr']
                tuesday_out_min = form.cleaned_data['tuesday_out_min']
                tuesday_tot = form.cleaned_data['tuesday_tot']
                wednesday_date = form.cleaned_data['wednesday_date']
                wednesday_in_hr = form.cleaned_data['wednesday_in_hr']
                wednesday_in_min = form.cleaned_data['wednesday_in_min']
                wednesday_out_hr = form.cleaned_data['wednesday_out_hr']
                wednesday_out_min = form.cleaned_data['wednesday_out_min']
                wednesday_tot = form.cleaned_data['wednesday_tot']
                thursday_date = form.cleaned_data['thursday_date']
                thursday_in_hr = form.cleaned_data['thursday_in_hr']
                thursday_in_min = form.cleaned_data['thursday_in_min']
                thursday_out_hr = form.cleaned_data['thursday_out_hr']
                thursday_out_min = form.cleaned_data['thursday_out_min']
                thursday_tot = form.cleaned_data['thursday_tot']
                friday_date = form.cleaned_data['friday_date']
                friday_in_hr = form.cleaned_data['friday_in_hr']
                friday_in_min = form.cleaned_data['friday_in_min']
                friday_out_hr = form.cleaned_data['friday_out_hr']
                friday_out_min = form.cleaned_data['friday_out_min']
                friday_tot = form.cleaned_data['friday_tot']
                saturday_date = form.cleaned_data['saturday_date']
                saturday_in_hr = form.cleaned_data['saturday_in_hr']
                saturday_in_min = form.cleaned_data['saturday_in_min']
                saturday_out_hr = form.cleaned_data['saturday_out_hr']
                saturday_out_min = form.cleaned_data['saturday_out_min']
                saturday_tot = form.cleaned_data['saturday_tot']
                sunday_date = form.cleaned_data['sunday_date']
                sunday_in_hr = form.cleaned_data['sunday_in_hr']
                sunday_in_min = form.cleaned_data['sunday_in_min']
                sunday_out_hr = form.cleaned_data['sunday_out_hr']
                sunday_out_min = form.cleaned_data['sunday_out_min']
                sunday_tot = form.cleaned_data['sunday_tot']
                weekly_hours = form.cleaned_data['weekly_hours']
                hourly_rate = form.cleaned_data['hourly_rate']
                week_start_date = form.cleaned_data['week_start_date']
                payroll_notes = form.cleaned_data['payroll_notes']
                upload_file = form.cleaned_data['upload_file']

                staffPay.monday_date = monday_date
                staffPay.monday_in_hr = monday_in_hr
                staffPay.monday_in_min = monday_in_min
                staffPay.monday_out_hr = monday_out_hr
                staffPay.monday_out_min = monday_out_min
                staffPay.monday_tot = monday_tot
                staffPay.tuesday_date = tuesday_date
                staffPay.tuesday_in_hr = tuesday_in_hr
                staffPay.tuesday_in_min = tuesday_in_min
                staffPay.tuesday_out_hr = tuesday_out_hr
                staffPay.tuesday_out_min = tuesday_out_min
                staffPay.tuesday_tot = tuesday_tot
                staffPay.wednesday_date = wednesday_date
                staffPay.wednesday_in_hr = wednesday_in_hr
                staffPay.wednesday_in_min = wednesday_in_min
                staffPay.wednesday_out_hr = wednesday_out_hr
                staffPay.wednesday_out_min = wednesday_out_min
                staffPay.wednesday_tot = wednesday_tot
                staffPay.thursday_date = thursday_date
                staffPay.thursday_in_hr = thursday_in_hr
                staffPay.thursday_in_min = thursday_in_min
                staffPay.thursday_out_hr = thursday_out_hr
                staffPay.thursday_out_min = thursday_out_min
                staffPay.thursday_tot = thursday_tot
                staffPay.friday_date = friday_date
                staffPay.friday_in_hr = friday_in_hr
                staffPay.friday_in_min = friday_in_min
                staffPay.friday_out_hr = friday_out_hr
                staffPay.friday_out_min = friday_out_min
                staffPay.friday_tot = friday_tot
                staffPay.saturday_date = saturday_date
                staffPay.saturday_in_hr = saturday_in_hr
                staffPay.saturday_in_min = saturday_in_min
                staffPay.saturday_out_hr = saturday_out_hr
                staffPay.saturday_out_min = saturday_out_min
                staffPay.saturday_tot = saturday_tot
                staffPay.sunday_date = sunday_date
                staffPay.sunday_in_hr = sunday_in_hr
                staffPay.sunday_in_min = sunday_in_min
                staffPay.sunday_out_hr = sunday_out_hr
                staffPay.sunday_out_min = sunday_out_min
                staffPay.sunday_tot = sunday_tot
                staffPay.weekly_hours = weekly_hours
                staffPay.hourly_rate = hourly_rate
                staffPay.week_start_date = week_start_date
                staffPay.payroll_notes = payroll_notes
                staffPay.upload_file = upload_file
                staffPay.save()

        return redirect(reverse('edit-process-payroll', kwargs={'paypk': payChange.id}))

    else:
        if payChange.user.groups.filter(name="installer").exists():
            form = InstallerForm(initial = {'job_file': payChange.installer_payroll.job_file,
                                            'job_name': payChange.installer_payroll.job_name,
                                            'date_completed': payChange.installer_payroll.date_completed,
                                            'job_address': payChange.installer_payroll.job_address,
                                            'description': payChange.installer_payroll.description,
                                            'helper': payChange.installer_payroll.helper,
                                            'helper_name': payChange.installer_payroll.helper_name,
                                            'work_performed': payChange.installer_payroll.work_performed,
                                            'amount_owed': payChange.installer_payroll.amount_owed})
            html = 'edit_installer.html'
        if payChange.user.groups.filter(name="salesperson").exists():
            sales_jobs = Sales_Payroll.objects.filter(job=payChange)
            formset = SalesEditFormSet(queryset = Sales_Payroll.objects.filter(job=payChange))
            sales_jobs_ex = sales_jobs.first()
            form = SalespersonPayEditForm(initial = {
                'salesperson': sales_jobs_ex.salesperson,
                'date_added': sales_jobs_ex.date_added
            })
            html = 'edit_sales.html'
        if payChange.user.groups.filter(name="staff").exists():
            edit_staffpay = Staff_Payroll.objects.get(pk=payChange.id)
            form = StaffForm(initial = {
                'monday_date': edit_staffpay.monday_date,
                'monday_in_hr': edit_staffpay.monday_in_hr,
                'monday_in_min': edit_staffpay.monday_in_min,
                'monday_out_hr': edit_staffpay.monday_out_hr,
                'monday_out_min': edit_staffpay.monday_out_min,
                'monday_tot': edit_staffpay.monday_tot,
                'tuesday_date': edit_staffpay.tuesday_date,
                'tuesday_in_hr': edit_staffpay.tuesday_in_hr,
                'tuesday_in_min': edit_staffpay.tuesday_in_min,
                'tuesday_out_hr': edit_staffpay.tuesday_out_hr,
                'tuesday_out_min': edit_staffpay.tuesday_out_min,
                'tuesday_tot': edit_staffpay.tuesday_tot,
                'wednesday_date': edit_staffpay.wednesday_date,
                'wednesday_in_hr': edit_staffpay.wednesday_in_hr,
                'wednesday_in_min': edit_staffpay.wednesday_in_min,
                'wednesday_out_hr': edit_staffpay.wednesday_out_hr,
                'wednesday_out_min': edit_staffpay.wednesday_out_min,
                'wednesday_tot': edit_staffpay.wednesday_tot,
                'thursday_date': edit_staffpay.thursday_date,
                'thursday_in_hr': edit_staffpay.thursday_in_hr,
                'thursday_in_min': edit_staffpay.thursday_in_min,
                'thursday_out_hr': edit_staffpay.thursday_out_hr,
                'thursday_out_min': edit_staffpay.thursday_out_min,
                'thursday_tot': edit_staffpay.thursday_tot,
                'friday_date': edit_staffpay.friday_date,
                'friday_in_hr': edit_staffpay.friday_in_hr,
                'friday_in_min': edit_staffpay.friday_in_min,
                'friday_out_hr': edit_staffpay.friday_out_hr,
                'friday_out_min': edit_staffpay.friday_out_min,
                'friday_tot': edit_staffpay.friday_tot,
                'saturday_date': edit_staffpay.saturday_date,
                'saturday_in_hr': edit_staffpay.saturday_in_hr,
                'saturday_in_min': edit_staffpay.saturday_in_min,
                'saturday_out_hr': edit_staffpay.saturday_out_hr,
                'saturday_out_min': edit_staffpay.saturday_out_min,
                'saturday_tot': edit_staffpay.saturday_tot,
                'sunday_date': edit_staffpay.sunday_date,
                'sunday_in_hr': edit_staffpay.sunday_in_hr,
                'sunday_in_min': edit_staffpay.sunday_in_min,
                'sunday_out_hr': edit_staffpay.sunday_out_hr,
                'sunday_out_min': edit_staffpay.sunday_out_min,
                'sunday_tot': edit_staffpay.sunday_tot,
                'weekly_hours': edit_staffpay.weekly_hours,
                'hourly_rate': edit_staffpay.hourly_rate,
                'week_start_date': edit_staffpay.week_start_date,
                'payroll_notes': edit_staffpay.payroll_notes,
                'upload_file': edit_staffpay.upload_file
            })
            html = 'edit_staff.html'
            staff_mem = payChange.user

    context = {
        'form': form,
        'formset': formset,
        'pay_change': payChange,
        'staff_mem': staff_mem
    }

    return render(request, html, context=context)

@login_required
def payroll_to_archive(request, paypk):
    to_archive = Payroll.objects.get(pk=paypk)

    if request.method == "POST":

        current_user = User.objects.get(username=request.user.username)
        log_entry2 = EntryLog(user_id=current_user,
                              action="{} moved payroll item {} for {} to the Payroll Archive.".format(
                                    current_user.username,
                                    to_archive.payroll_id,
                                    to_archive.user.first_name+" "+to_archive.user.last_name
                                ),
                                payroll=to_archive,
                                entry_date=timezone.now())
        log_entry2.save()

        to_archive.processed=True
        to_archive.archived=True
        to_archive.save()

        return redirect('payroll-to-process')

    context = {
        'to_archive': to_archive
    }

    return render (request, 'payroll_to_archive.html', context)

@login_required
def delete_payroll(request, paypk):
    del_pay = Payroll.objects.get(pk=paypk)

    if request.method == "POST":

        current_user = User.objects.get(username=request.user.username)
        log_entry2 = EntryLog(user_id=current_user,
                              action="{} deleted payroll item {} for {}.".format(
                                    current_user.username,
                                    del_pay.payroll_id,
                                    del_pay.user.first_name+" "+del_pay.user.last_name
                                ),
                                payroll=del_pay,
                                entry_date=timezone.now())
        log_entry2.save()
        del_pay.delete()

        return redirect('my-payroll')

    context = {
        'del_pay': del_pay
        }

    return render(request, 'delete_payroll.html', context)

@login_required
def payroll_archive(request):
    if User.objects.filter(pk=request.user.id, groups__name="admin").exists():
        archives = Payroll.objects.filter(archived=True).order_by('-payroll_id')
    else:
        archives = Payroll.objects.filter(user=request.user.id,
                                          archived=True).order_by('-payroll_id')

    if request.method == "POST":
        form = SortPayProcessForm(request.POST)
        if form.is_valid():
            form.fields['sort_by'].required = False
            form.fields['order'].required = False

            if form.is_valid():
                sort_by = form.cleaned_data['sort_by']
                order = form.cleaned_data['order']

                if sort_by == "1": # payroll id
                    archives = Payroll.objects.filter(archived=True).order_by('payroll_id')
                if sort_by == "2": # installer
                    archives = archives.filter(user__groups__name='installer')
                if sort_by == "3": # staff
                    archives = archives.filter(user__groups__name='staff')
                if sort_by == "4": # salesperson
                    archives = archives.filter(user__groups__name='salesperson')
                if order == "1":
                    archives = archives.order_by('-payroll_id')
                if order == "2":
                    archives = archives.order_by('payroll_id')

    else:
        form = SortPayProcessForm()

    paginator = Paginator(archives, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        pay = paginator.page(page)
    except(EmptyPage, InvalidPage):
        pay = paginator.page(paginator.num_pages)

    context = {
        'pay': pay,
        'form': form
    }

    return render(request, 'payroll_archive.html', context)

class InstallCalendarView(LoginRequiredMixin, ListView, generic.edit.ModelFormMixin):
    model = Installation
    template_name = 'install_calendar.html'
    form_class = SelectInstallerForm

    def get(self, request, *args, **kwargs):
        self.object = None
        self.form = self.get_form(self.form_class)

        return ListView.get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        self.form = self.get_form(self.form_class)

        if request.method == "POST":

            if self.form.is_valid():
                installer_form = self.form.cleaned_data['installer']
                installer = User.objects.get(username=installer_form)
                print(installer)

                return redirect('installer-schedule', pk=installer.id)
    
    def get_context_data(self, **kwargs):
        context = super(InstallCalendarView, self).get_context_data(**kwargs)

        # use today's date for the calendar
        d = get_date(self.request.GET.get('month', None))

        # Instantiate our calendar class with today's year and date
        cal = Calendar(d.year, d.month)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context

class EditInstallCalendarView(LoginRequiredMixin, ListView, generic.edit.ModelFormMixin):
    model = Installation
    template_name = 'edit_install_calendar.html'
    form_class = InstallAppointmentForm

    def get(self, request, *args, **kwargs):
        self.object = None
        self.form = self.get_form(self.form_class)
        return ListView.get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        self.form = self.get_form(self.form_class)

        if request.method == "POST":

            if self.form.is_valid():
                changeJob = Installation.objects.get(pk=self.kwargs['pk'])
                # self.object = self.form.save()
                installer = self.form.cleaned_data['installer']
                new_date = self.form.cleaned_data['install_schedule']
                changeJob.installer = installer
                changeJob.install_schedule = new_date
                changeJob.save()

            return self.get(request, *args, **kwargs)

    def get_initial(self, *args, **kwargs):
        changeJob = Installation.objects.get(pk=self.kwargs['pk'])
        initial = super().get_initial()
        initial['installer'] = changeJob.installer
        initial['install_schedule'] = changeJob.install_schedule
        return initial
    
    def get_context_data(self, **kwargs):
        context = super(EditInstallCalendarView, self).get_context_data(**kwargs)
        changeJob = Installation.objects.get(pk=self.kwargs['pk'])
        # use today's date for the calendar
        d = get_date(self.request.GET.get('month', None))
        # d = changeJob.install_schedule

        # Instantiate our calendar class with today's year and date
        cal = EditCalendar(d.year, d.month)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(withyear=True)
        context['job'] = changeJob
        context['editcalendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        context['form'] = self.form
        return context

class InstallerCalendarView(LoginRequiredMixin, ListView, generic.edit.ModelFormMixin):
    model = Installation
    template_name = 'installer_calendar.html'
    form_class = SelectInstallerForm

    def get(self, request, *args, **kwargs):
        self.object = None
        self.form = self.get_form(self.form_class)
        return ListView.get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        self.form = self.get_form(self.form_class)

        if request.method == "POST":

            if self.form.is_valid():
                installer_form = self.form.cleaned_data['installer']
                if not installer_form:
                    return redirect('install-schedule')
                else:
                    installer = User.objects.get(username=installer_form)
                    return redirect('installer-schedule', pk=installer.id)

    def get_initial(self):
        installer = User.objects.get(pk=self.kwargs['pk'])
        return {'installer': installer.first_name}
    
    def get_context_data(self, **kwargs):
        context = super(InstallerCalendarView, self).get_context_data(**kwargs)
        installer = User.objects.get(pk=self.kwargs['pk'])
        # use today's date for the calendar
        d = get_date(self.request.GET.get('month', None))
        # d = changeJob.install_schedule

        # Instantiate our calendar class with today's year and date
        cal = InstallerCalendar(installer.id, self.request, d.year, d.month)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(withyear=True)
        context['installer'] = installer
        context['installercalendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context

class AppointmentCalendarView(LoginRequiredMixin, ListView):
    model = Lead
    template_name = 'appointment_calendar.html'

    def get(self, request, *args, **kwargs):
        self.object = None

        return ListView.get(self, request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(AppointmentCalendarView, self).get_context_data(**kwargs)

        # use today's date for the calendar
        d = get_date(self.request.GET.get('month', None))

        # Instantiate our calendar class with today's year and date
        cal = AppointmentCalendar(d.year, d.month)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context

class EditInstallCalendarView(LoginRequiredMixin, ListView, generic.edit.ModelFormMixin):
    model = Installation
    template_name = 'edit_install_calendar.html'
    form_class = InstallAppointmentForm

    def get(self, request, *args, **kwargs):
        self.object = None
        self.form = self.get_form(self.form_class)
        return ListView.get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        self.form = self.get_form(self.form_class)

        if request.method == "POST":

            if self.form.is_valid():
                changeJob = Installation.objects.get(pk=self.kwargs['pk'])
                # self.object = self.form.save()
                installer = self.form.cleaned_data['installer']
                new_date = self.form.cleaned_data['install_schedule']
                changeJob.installer = installer
                changeJob.install_schedule = new_date
                changeJob.save()

            return self.get(request, *args, **kwargs)

    def get_initial(self, *args, **kwargs):
        changeJob = Installation.objects.get(pk=self.kwargs['pk'])
        initial = super().get_initial()
        initial['installer'] = changeJob.installer
        initial['install_schedule'] = changeJob.install_schedule
        return initial
    
    def get_context_data(self, **kwargs):
        context = super(EditInstallCalendarView, self).get_context_data(**kwargs)
        changeJob = Installation.objects.get(pk=self.kwargs['pk'])
        # use today's date for the calendar
        d = get_date(self.request.GET.get('month', None))
        # d = changeJob.install_schedule

        # Instantiate our calendar class with today's year and date
        cal = EditCalendar(d.year, d.month)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(withyear=True)
        context['job'] = changeJob
        context['editcalendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        context['form'] = self.form
        return context

class EditAppointmentCalendarView(LoginRequiredMixin, ListView, generic.edit.ModelFormMixin):
    model = Lead
    template_name = 'edit_appointment_calendar.html'
    form_class = EditAppointmentCalendarForm

    def get(self, request, *args, **kwargs):
        self.object = None
        self.form = self.get_form(self.form_class)
        return ListView.get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        self.form = self.get_form(self.form_class)

        if request.method == "POST":

            if self.form.is_valid():
                changeJob = Lead.objects.get(pk=self.kwargs['pk'])
                # self.object = self.form.save()
                salesperson = self.form.cleaned_data['salesperson']
                new_date = self.form.cleaned_data['appointment_date']
                new_time = self.form.cleaned_data['appointment_time']
                time_ap = self.form.cleaned_data['time_ap']

                a_or_p = 'AM' if time_ap=="1" else 'PM'
                t = str(new_time)+a_or_p
                appoint_sched = datetime.strptime(t, '%I:%M:%S%p')
                print(new_date)
                changeJob.salesperson = salesperson
                changeJob.appointment_date = new_date
                changeJob.appointment_time = appoint_sched
                changeJob.save()

            return self.get(request, *args, **kwargs)

    def get_initial(self, *args, **kwargs):
        changeJob = Lead.objects.get(pk=self.kwargs['pk'])
        if changeJob.appointment_time.hour <= 12:
            ap_init = "1"
        else:
            ap_init = "2"

        initial = super().get_initial()
        initial['salesperson'] = changeJob.salesperson
        initial['appointment_date'] = changeJob.appointment_date
        initial['appointment_time'] = changeJob.appointment_time.strftime("%-I:%M")
        initial['time_ap'] = ap_init
        return initial
    
    def get_context_data(self, **kwargs):
        context = super(EditAppointmentCalendarView, self).get_context_data(**kwargs)
        changeJob = Lead.objects.get(pk=self.kwargs['pk'])
        # use today's date for the calendar
        d = get_date(self.request.GET.get('month', None))
        # d = changeJob.install_schedule

        # Instantiate our calendar class with today's year and date
        cal = EditAppointmentCalendar(d.year, d.month)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(withyear=True)
        context['job'] = changeJob
        context['editcalendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        context['form'] = self.form
        return context

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month