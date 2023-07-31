from django.db import models
from django.urls import reverse
from phone_field import PhoneField
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

# Create your models here.
def set_deleted_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]

def set_deleted_group():
    return ProjectGroup.objects.get_or_create(name='deleted')[0]

def set_deleted_jurisdiction():
    return Jurisdiction.objects.get_or_create(name='deleted')[0]

def set_deleted_type():
    return 

class ProjectGroup(models.Model):
    name = models.CharField(max_length=80)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class ProjectType(models.Model):
    proj_type = models.CharField(max_length=80)
    group = models.ForeignKey(ProjectGroup, on_delete=models.SET(set_deleted_group))
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['proj_type']

    def __str__(self):
        return self.proj_type

class SourceGroup(models.Model):
    name = models.CharField(max_length=40)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

def set_deleted_source_grp():
    return SourceGroup.objects.get_or_create(name='deleted')[0]

class Customer(models.Model):
    name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=60, blank=True)
    address = models.CharField(max_length=60)
    address1 = models.CharField(max_length=60, blank=True)
    city = models.CharField(max_length=60)
    state = models.CharField(max_length=60)
    zip_code = models.CharField(max_length=12, blank=True)
    nmc_street = models.CharField(max_length=80,
                                  help_text="Nearest Major Cross Streets",
                                  blank=True)
    home_phone = PhoneField(blank=True)
    cell_phone = PhoneField(blank=True)
    email_address = models.EmailField(blank=True)
    fax_number = PhoneField(blank=True)
    gate_code = models.CharField(max_length=20, blank=True)
    entry_date = models.DateTimeField()

    class Meta:
        ordering = ['last_name']

    def __str__(self):
        return "{} {}".format(self.name, self.last_name)

    def get_absolute_url(self):
        return reverse('edit-appointment', kwargs={'leadpk': self.id})

class Lead(models.Model):
    client_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    appointment_date = models.DateField(blank=True, null=True)
    appointment_time = models.TimeField(blank=True, null=True)
    salesperson = models.ForeignKey(User, limit_choices_to={'groups__name': "salesperson"},
                                          blank=True,
                                          null=True,
                                          on_delete=models.SET(set_deleted_user),
                                          related_name='salesperson_group')
    project_type = models.ManyToManyField(ProjectType, blank=True)
    project_notes = models.TextField(blank=True)
    priority = models.BooleanField(default=False)
    priority_msg = models.TextField(blank=True)
    contract_amount = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True) 

    LEAD_STATUS_CHOICES = (
        (1, 'none'),
        (2, 'open lead'),
        (3, 'archives'),
        (4, 'accounts receivable'),
        (5, 'job in progress'),
        (6, 'appointment scheduled')
    )

    lead_status = models.CharField(max_length=1,
                                   choices=LEAD_STATUS_CHOICES,
                                   default=1)

    NONE = None
    COLD = 'CD'
    WARM = 'WM'
    HOT = 'HT'
    LEAD_CUR_STATUS_CHOICES = [
        (NONE, 'Select...'),
        (COLD, 'Cold Lead'),
        (WARM, 'Warm Lead'),
        (HOT, 'Hot Lead')
    ]

    lead_cur_status = models.CharField(max_length=2,
                                       choices=LEAD_CUR_STATUS_CHOICES,
                                       blank=True, null=True)
    source = models.ForeignKey(SourceGroup, on_delete=models.SET(set_deleted_source_grp),
                                            blank=True, null=True)
    entry_date = models.DateTimeField()

    class Meta:
        ordering = ['-entry_date']

    def __str__(self):
        return self.client_id

    def get_absolute_url(self):
        return reverse('job-detail', kwargs={'pk': self.id})

    def get_appointment_url(self):
        return reverse('appointment-detail', kwargs={'pk': self.id})

    def get_edit_calendar_url(self):
        return reverse('edit-appointment-calendar', kwargs={'pk':self.id})

    def get_status_display(self):
        return self.get_lead_status_display()

class Contracts(models.Model):
    job = models.ForeignKey(Lead, on_delete=models.CASCADE)
    document = models.FileField(upload_to='contracts/')
    
    class Meta:
        ordering = ['-job']

class Pictures(models.Model):
    job = models.ForeignKey(Lead, on_delete=models.CASCADE)
    photos = models.ImageField(upload_to='images/')

    class Meta:
        ordering = ['-job']

class JobStatus(models.Model):
    lead = models.OneToOneField(Lead, on_delete=models.CASCADE,
                                      primary_key=True)
    sale_date = models.DateField(blank=True, null=True)

    NONE = None
    YES = 'YS'
    NO = 'NO'
    PWORK = 'PW'
    APPR = 'AP'
    DENY = 'DN'
    ASSOC_APPROV_NEEDED_CHOICES = [
        (NONE, 'Select...'),
        (YES, 'Yes'),
        (NO, 'No'),
        (PWORK, 'Paper Work Submitted and Waiting for Approval'),
        (APPR, 'Approved'),
        (DENY, 'Denied')
    ]

    association_approval = models.CharField(max_length=4, null=True,
                                            choices=ASSOC_APPROV_NEEDED_CHOICES,
                                            default=NONE)
    materials_ordered = models.BooleanField(default=False)

    NONE = None
    YES = 'YS'
    CUST = 'CU'
    SS = 'SS'
    CONCRETE_EXISTING_CHOICES = [
        (NONE, 'Select...'),
        (YES, 'yes'),
        (CUST, 'To be poured by customer'),
        (SS, 'To be poured by Sunshield')
    ]

    concrete_existing = models.CharField(max_length=2,
                                         choices=CONCRETE_EXISTING_CHOICES,
                                         blank=True)

    NONE = None
    YES = 'YS'
    NO = 'NO'
    FOOTER_NEEDED_CHOICES = [
        (NONE, 'Select...'),
        (YES, 'yes'),
        (NO, 'no')
    ]

    footer_needed = models.CharField(max_length=2,
                                     choices=FOOTER_NEEDED_CHOICES,
                                     blank=True)
    safety_stakes = models.BooleanField(default=False)

    NONE = None
    CO = 'CO'
    ST = 'ST'
    CP = 'CP'
    GU = 'GU'
    ALUMALATTICE_CHOICES = [
        (NONE, 'Select...'),
        (CO, 'Combination Solid / Open Cover'),
        (ST, 'Standard Aluminum Cover'),
        (CP, 'Carport'),
        (GU, 'Gutters')
    ]

    alumalattice = models.CharField(choices=ALUMALATTICE_CHOICES,
                                    max_length=2,
                                    blank=True)

    completion_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = 'Job Status'

class Payment(models.Model):
    job = models.OneToOneField(Lead, on_delete=models.CASCADE,
                                     primary_key=True)

    NONE = None
    PAID = 'PD'
    DEP = 'DP'
    DUE = 'DU'
    PAYMENTS_CHOICES = [
        (NONE, 'Select...'),
        (PAID, 'Paid in Full'),
        (DEP, 'Paid Deposit'),
        (DUE, 'Will Pay Upon Completion')
    ]

    status = models.CharField(max_length=2,
                              choices=PAYMENTS_CHOICES,
                              blank=True)
    amount = models.DecimalField(max_digits=14,
                                 decimal_places=2,
                                 blank=True,
                                 null=True)
    breakdown = models.CharField(max_length=200, blank=True)
    archive_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return job.lead.client_id

class Jurisdiction(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Permit(models.Model):
    job = models.OneToOneField(Lead, on_delete=models.CASCADE,
                                     primary_key=True)
    permit = models.CharField(max_length=48, blank=True)
    jurisdiction = models.ForeignKey(Jurisdiction, on_delete=models.SET(set_deleted_jurisdiction),
                                                   blank=True, null=True)

    NONE = None
    YES = 'YS'
    NO = 'NO'
    WOP = 'WP'
    WOE = 'WE'
    PAW = 'PW'
    FID = 'ID'
    FIA = 'IA'
    PERMIT_CHOICES = [
        (NONE, 'Select...'),
        (YES, 'Yes'),
        (NO, 'No'),
        (WOP, 'Waiting on Permit'),
        (WOE, 'Waiting for Engineering'),
        (PAW, 'Permit Approved Through Building Department (Waiting for Inspections)'),
        (FID, 'Final Inspection Denied'),
        (FIA, 'Final Inspection Approved')
    ]

    status = models.CharField(max_length=2,
                              choices=PERMIT_CHOICES)
    description = models.TextField(blank=True)
    archive = models.BooleanField(default=False)
    archive_date = models.DateField(blank=True, null=True)

class Installation(models.Model):
    job = models.OneToOneField(Lead, on_delete=models.CASCADE,
                                     primary_key=True)
    footer_dig_date = models.DateField(blank=True, null=True)
    footer_pour_date = models.DateField(blank=True, null=True)
    footer_inspection_date = models.DateField(blank=True, null=True)
    install_schedule = models.DateField(blank=True, null=True)
    installer = models.ForeignKey(User, limit_choices_to={'groups__name': "installer"},
                                        blank=True, null=True,
                                        on_delete=models.SET(set_deleted_user),
                                        related_name='installer_group')
    expected_completion = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['-install_schedule']

    def get_absolute_url(self):
        return reverse('edit-install-schedule', kwargs={'pk': self.job.id})

class Services(models.Model):
    customer_name = models.CharField(max_length=100)
    customer_address = models.CharField(max_length=120)
    cust_called = models.DateField(blank=True, null=True)
    service_schedule = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    phone_number = PhoneField(blank=True)
    installer = models.ForeignKey(User, limit_choices_to={'groups__name': "installer"},
                                        blank=True, null=True,
                                        on_delete=models.SET(set_deleted_user),
                                        related_name='services_group')
    archive = models.BooleanField(default=False)

    class Meta:
        ordering = ['-cust_called']

    def get_absolute_url(self):
        return reverse('service-detail', kwargs={'pk': self.id})

    def __str__(self):
        return self.customer_name

class Message(models.Model):
    text = models.TextField()
    user_id = models.ForeignKey(User, on_delete=models.SET(set_deleted_user))
    # user_id = models.CharField(max_length=25, blank=True)
    datetime = models.DateTimeField()

    class Meta:
        ordering = ['-datetime']

    def __str__(self):
        return self.text

class Payroll(models.Model):
    payroll_id = models.DecimalField(max_digits=1000, decimal_places=0, blank=True, null=True)
    archived = models.BooleanField(default=False)
    date_archived = models.DateField(blank=True, null=True)
    processed = models.BooleanField(default=False)
    date_processed = models.DateField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET(set_deleted_user))
    date_entered = models.DateField(blank=True, null=True)
    submitted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_entered']

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)

    def get_absolute_url(self):
        return reverse('payroll-detail', kwargs={'paypk': self.id})

class EntryLog(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.SET(set_deleted_user))
    action = models.CharField(max_length=200)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, blank=True, null=True)
    service = models.ForeignKey(Services, on_delete=models.CASCADE, blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, blank=True, null=True)
    entry_date = models.DateTimeField(blank=True, default=timezone.now)

    class Meta:
        ordering = ['-entry_date']

class Installer_Payroll(models.Model):
    job = models.OneToOneField(Payroll, on_delete=models.CASCADE,
                                        primary_key=True)
    job_file = models.FileField(upload_to='other/')
    job_name = models.CharField(max_length=100)
    date_completed = models.DateField(blank=True, null=True)
    job_address = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    helper = models.BooleanField(default=False)
    helper_name = models.CharField(max_length=100, blank=True, null=True)
    work_performed = models.TextField()
    amount_owed = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.job_name

class Staff_Payroll(models.Model):
    job = models.OneToOneField(Payroll, on_delete=models.CASCADE, primary_key=True)
    week_start_date = models.DateField(blank=True, null=True)
    monday_date = models.DateField(blank=True, null=True)
    monday_in_hr = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    monday_in_min = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    monday_out_hr = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    monday_out_min = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    monday_tot = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    tuesday_date = models.DateField(blank=True, null=True)
    tuesday_in_hr = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    tuesday_in_min = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    tuesday_out_hr = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    tuesday_out_min = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    tuesday_tot = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    wednesday_date = models.DateField(blank=True, null=True)
    wednesday_in_hr = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    wednesday_in_min = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    wednesday_out_hr = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    wednesday_out_min = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    wednesday_tot = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    thursday_date = models.DateField(blank=True, null=True)
    thursday_in_hr = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    thursday_in_min = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    thursday_out_hr = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    thursday_out_min = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    thursday_tot = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    friday_date = models.DateField(blank=True, null=True)
    friday_in_hr = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    friday_in_min = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    friday_out_hr = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    friday_out_min = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    friday_tot = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    saturday_date = models.DateField(blank=True, null=True)
    saturday_in_hr = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    saturday_in_min = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    saturday_out_hr = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    saturday_out_min = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    saturday_tot = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    sunday_date = models.DateField(blank=True, null=True)
    sunday_in_hr = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    sunday_in_min = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    sunday_out_hr = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    sunday_out_min = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    sunday_tot = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    weekly_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    payroll_notes = models.TextField(blank=True)
    upload_file = models.FileField(upload_to='other/', blank=True, null=True)

    def __str__(self):
        return "{}, {}".format(self.job.user, self.weekly_start_date)

    class Meta:
        ordering = ['-week_start_date']

class Sales_Payroll(models.Model):
    id = models.AutoField(primary_key=True)
    job = models.ForeignKey(Payroll, on_delete=models.CASCADE)
    salesperson = models.CharField(max_length=80, blank=True, null=True)
    job_name = models.CharField(max_length=100)
    date_added = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=250, blank=True, null=True)
    commission = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    contract_amount = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.job_name

class Employee_Documents(models.Model):
    headline = models.CharField(max_length=250, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Employee Document"
        verbose_name_plural = "Employee Documents"

    def __str__(self):
        return self.headline

class Employee_Files(models.Model):
    record = models.ForeignKey(Employee_Documents, on_delete=models.CASCADE)
    document = models.FileField(upload_to='other/')
    title = models.CharField(max_length=80, blank=False, default="file title")
    
    class Meta:
        ordering = ['-record']
        verbose_name = 'Employee File'
        verbose_name_plural = 'Employee Files'

    def __str__(self):
        return self.title