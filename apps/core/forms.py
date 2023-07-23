from django import forms
from django.forms import ModelForm, Textarea, HiddenInput
from management.models import (Message, Customer, Lead, ProjectType, SourceGroup, ProjectGroup,
JobStatus, Jurisdiction, Installation, Employee_Documents, Sales_Payroll)
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from datetime import datetime, date, time, timedelta
from django.forms import modelformset_factory, formset_factory

class DateInput(forms.DateInput):
    input_type = 'date'

class DashboardForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']
        labels = {
            'text': '',
        }

class NewUserForm(forms.Form):
    first_name = forms.CharField(label='First Name',
                                 max_length=30,
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    last_name = forms.CharField(label='Last Name',
                                max_length=30,
                                widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    username = forms.CharField(label='User Name',
                               max_length=30,
                               widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    password = forms.CharField(label='Password',
                               max_length=30,
                               widget = forms.PasswordInput(attrs={'style': 'width:20em;', 'rows':1}))
    confirm = forms.CharField(label='Confirm Password',
                              max_length=30, 
                              widget = forms.PasswordInput(attrs={'style': 'width:20em;', 'rows':1}))
    email = forms.EmailField(label='Email Address')
    c = [("1", "Admin"), ("2", "Installer"),
    ("3", "Salesperson"), ("4", "Staff")]
    user_type = forms.ChoiceField(choices=c,
                                  label="User Type",
                                  widget = forms.Select(attrs={'style': 'width:20em'}))

    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-8'

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get("password")
        pwd_conf = cleaned_data.get("confirm")

        if pwd != pwd_conf:
            raise forms.ValidationError({'password': ["Password fields do not match."]})

        return cleaned_data

default_source_group = SourceGroup.objects.get_or_create(name='none')

valid_time_inputs = ['%H', '%H:%M']

class NewAppointmentForm(forms.Form):
    name = forms.CharField(label='First Name',
                                 max_length=30,
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    last_name = forms.CharField(label='Last Name',
                                max_length=30,
                                widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    address = forms.CharField(label='Address',
                                 max_length=30,
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    address1 = forms.CharField(label='Address1',
                                max_length=30,
                                widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    city = forms.CharField(label='City',
                                 max_length=30,
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    state = forms.CharField(label='State',
                                max_length=30,
                                widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    zip_code = forms.CharField(label='Zipcode',
                                 max_length=30,
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    gate_code = forms.CharField(label='Gate Code',
                                max_length=30,
                                widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    nmc_street = forms.CharField(label='Nearest Major Cross Streets',
                                max_length=60,
                                widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    home_phone = forms.CharField(required=False,
                                 help_text='10 digits, numbers only.',
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    cell_phone = forms.CharField(required=False,
                                 help_text='10 digits, numbers only.',
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    email = forms.CharField(label='Email Address',
                                max_length=50,
                                widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    detailed_instr = forms.CharField(label='Detailed Instructions',
                                     widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':8}))
    contracts = forms.FileField(label="Contracts",
                                widget=forms.ClearableFileInput(attrs={'multiple': True}))
    images = forms.FileField(label="Images",
                                widget=forms.ClearableFileInput(attrs={'multiple': True}))
    salesperson = forms.ModelChoiceField(queryset=User.objects.filter(groups__name='salesperson')
                                                              .filter(is_active=True),
                                                                      to_field_name='username')
    date = forms.DateField(widget=DateInput, label='Date and Time')
    time = forms.TimeField(label = ' ', required=False, input_formats=valid_time_inputs,
                           widget=forms.TimeInput(attrs={'style': 'width:5em;', 'rows':1}))
    ap = [("1", "AM"), ("2", "PM")]
    time_ap = forms.ChoiceField(choices=ap, label=' ', required=False,
                                widget = forms.Select(attrs={'style': 'width:6em'}))
    found_us = forms.ModelChoiceField(queryset=SourceGroup.objects.all(), to_field_name='name',
                                      initial=default_source_group)

    def __init__(self, *args, **kwargs):
        super(NewAppointmentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.fields['time'].label = False
        self.fields['time_ap'].label = False
        self.fields['date'].widget.attrs.update({'id': 'appointment_date'})

default_project_type = ProjectGroup.objects.get_or_create(name='none')

class NewProjectTypeForm(forms.Form):
    project_type = forms.CharField(label='Project type', max_length=80,
                                   widget=forms.Textarea(attrs={'style': 'width:30em;', 'rows':1}))
    project_category = forms.ModelChoiceField(queryset=ProjectGroup.objects.all(), to_field_name='name',
                                              initial=default_project_type)

class SortLeadsRunForm(forms.Form):
    sort_choice = [
        ('1', 'Customer Name'),
        ('2', 'Address'),
        ('3', 'City'),
        ('4', 'Date Appointment Ran'),
        ('5', 'Nearest Cross Street')
        ]
    sort_by = forms.ChoiceField(choices=sort_choice, required=False, initial="4",
                                widget = forms.Select(attrs={'style': 'width:6em'}))
    ch = [
        ('1', 'DESC'), ('2', 'ASC')
    ]
    order = forms.ChoiceField(choices=ch, required=False, initial="1",
                              widget = forms.Select(attrs={'style': 'width:6em'}))

    def __init__(self, *args, **kwargs):
        super(SortLeadsRunForm, self).__init__(*args, **kwargs)
        self.fields['sort_by'].label = False
        self.fields['order'].label = False

class NewLeadForm(forms.Form):
    name = forms.CharField(label='First Name',
                                 max_length=30,
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    last_name = forms.CharField(label='Last Name',
                                max_length=30,
                                widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    address = forms.CharField(label='Address',
                                 max_length=30,
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    address1 = forms.CharField(label='Address1',
                                max_length=30,
                                required=False,
                                widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    city = forms.CharField(label='City',
                                 max_length=30,
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    state = forms.CharField(label='State',
                                max_length=30,
                                required=False,
                                widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    zip_code = forms.CharField(label='Zipcode',
                                 max_length=30,
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    nmc_street = forms.CharField(label='Nearest Major Cross Streets',
                                max_length=60,
                                required=False,
                                widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    home_phone = forms.CharField(required=False,
                                 help_text='10 digits, numbers only.',
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    cell_phone = forms.CharField(required=False,
                                 help_text='10 digits, numbers only.',
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    fax_number = forms.CharField(required=False,
                                 help_text='10 digits, numbers only.',
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    email = forms.CharField(label='Email Address',
                                max_length=50,
                                required=False,
                                widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    detailed_instr = forms.CharField(label='Detailed Instructions',
                                     required=False,
                                     widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':8}))
    priority = forms.BooleanField(label='Priority', required=False, 
                                  widget=forms.CheckboxInput(attrs={'name':'form-trigger',
                                                                    'id':'form-trigger-priority'}))
    priority_notes = forms.CharField(widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':8,
                                                                    'name':'form-content-notes'}),
                                                                    required=False)
    salesperson = forms.ModelChoiceField(queryset=User.objects.filter(groups__name='salesperson')
                                                              .filter(is_active=True),
                                                                      to_field_name='username',
                                                                      required=False)
    sales_date = forms.DateField(widget=DateInput, label='Sales Date', required=False)
    date_appointment_run = forms.DateField(widget=DateInput, label='Date Appointment Run', required=False)
    time = forms.TimeField(label = 'Time', required=False, input_formats=valid_time_inputs,
                           widget=forms.TimeInput(attrs={'style': 'width:6em;', 'rows':1}))
    ap = [("1", "AM"), ("2", "PM")]
    time_ap = forms.ChoiceField(choices=ap, required=False,
                                widget = forms.Select(attrs={'style': 'width:6em'}))

    def get_type_choices():
        TYPE_CHOICES = []
        for g in ProjectGroup.objects.all():
            group_tup = []
            for pt in ProjectType.objects.filter(group=g.id, active=True):
                choice_tup = (pt.id, pt.proj_type)
                group_tup.append(choice_tup)
            full_group = (g.name, tuple(group_tup))
            TYPE_CHOICES.append(full_group)
            
        return TYPE_CHOICES

    project_type = forms.MultipleChoiceField(choices=get_type_choices,
                                             label="Project Type",
                                             required=False)

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

    association_approval = forms.ChoiceField(
                                choices = ASSOC_APPROV_NEEDED_CHOICES,
                                label='Association Approval Needed',
                                required=False,
                                widget = forms.Select(attrs={'style': 'width:20em; height:2em;'})
                                )
    
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

    permits = forms.ChoiceField(choices=PERMIT_CHOICES,
                                label='Permits',
                                required=False,
                                widget = forms.Select(attrs={'style': 'width:20em; height:2em'}))
    materials_ordered = forms.BooleanField(label='Materials Ordered ?', required=False)

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

    concrete_existing = forms.ChoiceField(choices=CONCRETE_EXISTING_CHOICES,
                                          label='Concrete Existing',
                                          required=False,
                                          widget= forms.Select(attrs={'style': 'width:20em; height:2em;'}))

    NONE = None
    YES = 'YS'
    NO = 'NO'
    FOOTER_NEEDED_CHOICES = [
        (NONE, 'Select...'),
        (YES, 'yes'),
        (NO, 'no')
    ]

    footer_needed = forms.ChoiceField(choices=FOOTER_NEEDED_CHOICES,
                                      label='Footer Needed',
                                      required=False,
                                      widget= forms.Select(attrs={'style': 'width:20em; height:2em;',
                                                           #       'onchange':'showDiv(this)',
                                                                  'id':'footer_form_drop'}))
    footer_dig_date = forms.DateField(widget=DateInput, label='Footer Dig Date', required=False)
    footer_inspection_date = forms.DateField(widget=DateInput, label='Footer Inspection Date', required=False)
    footer_pour_date = forms.DateField(widget=DateInput, label='Footer Pour Date', required=False)
    safety_stakes = forms.BooleanField(label='Safety Stakes', required=False)

    contracts = forms.FileField(label="Contracts",
                                required=False,
                                widget=forms.ClearableFileInput(attrs={'multiple': True, 'style': 'width:20em; height:6em;'}))
    images = forms.FileField(label="Images",
                             required=False,
                             widget=forms.ClearableFileInput(attrs={'multiple': True, 'style': 'width:20em; height:4em;'}))
    total_contract_amount = forms.DecimalField(label='Total Contract Amount',
                                               max_digits=14,
                                               min_value=0,
                                               decimal_places=2,
                                               required=False)

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

    payments = forms.ChoiceField(choices=PAYMENTS_CHOICES,
                                 required=False,
                                 label='Payments',
                                 widget= forms.Select(attrs={'style': 'width:20em; height:2em;',
                                                     #        'onchange':'showPayDiv(this)',
                                                             'id':'payment_form_drop'}))
    downpayment = forms.DecimalField(label='Amount',
                                     max_digits=14,
                                     min_value=0,
                                     decimal_places=2,
                                     required=False)

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

    lead_status = forms.ChoiceField(choices=LEAD_CUR_STATUS_CHOICES,
                                    label='Lead Status',
                                    required=False,
                                    widget= forms.Select(attrs={'style': 'width:20em; height:2em;'}))

    def __init__(self, *args, **kwargs):
        super(NewLeadForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4'
        self.helper.field_class = 'col-md-8'
        self.fields['time_ap'].label = False
        self.fields['date_appointment_run'].label = False
        self.fields['priority_notes'].label = False
        self.fields['footer_dig_date'].label = False
        self.fields['footer_inspection_date'].label = False
        self.fields['footer_pour_date'].label = False

class SortJIPForm(forms.Form):
    sort_choice = [
        ('1', 'Customer Name'),
        ('2', 'Address'),
        ('3', 'City'),
        ('4', 'Installation Date'),
        ('5', 'Project Type'),
        ('6', 'Installer'),
        ]
    sort_by = forms.ChoiceField(choices=sort_choice, required=False, initial="1",
                                widget = forms.Select(attrs={'style': 'width:6em'}))
    ch = [
        ('1', 'DESC'), ('2', 'ASC')
    ]
    order = forms.ChoiceField(choices=ch, required=False, initial="1",
                              widget = forms.Select(attrs={'style': 'width:6em'}))

    def __init__(self, *args, **kwargs):
        super(SortJIPForm, self).__init__(*args, **kwargs)
        self.fields['sort_by'].label = False
        self.fields['order'].label = False

class SortAccountsForm(forms.Form):
    sort_choice = [
        ('1', 'Customer Name'),
        ('2', 'Address'),
        ('3', 'Contract Amount')
        ]
    sort_by = forms.ChoiceField(choices=sort_choice, required=False, initial="1",
                                widget = forms.Select(attrs={'style': 'width:6em'}))
    ch = [
        ('1', 'DESC'), ('2', 'ASC')
    ]
    order = forms.ChoiceField(choices=ch, required=False, initial="1",
                              widget = forms.Select(attrs={'style': 'width:6em'}))

    def __init__(self, *args, **kwargs):
        super(SortAccountsForm, self).__init__(*args, **kwargs)
        self.fields['sort_by'].label = False
        self.fields['order'].label = False

class SortArchivesForm(forms.Form):
    sort_choice = [
        ('1', 'Customer Name'),
        ('2', 'Date Order Complete')
        ]
    sort_by = forms.ChoiceField(choices=sort_choice, required=False, initial="2",
                                widget = forms.Select(attrs={'style': 'width:6em'}))
    ch = [
        ('1', 'DESC'), ('2', 'ASC')
    ]
    order = forms.ChoiceField(choices=ch, required=False, initial="1",
                              widget = forms.Select(attrs={'style': 'width:6em'}))

    def __init__(self, *args, **kwargs):
        super(SortArchivesForm, self).__init__(*args, **kwargs)
        self.fields['sort_by'].label = False
        self.fields['order'].label = False

class SortPayrollForm(forms.Form):
    ch = [
        ('1', 'DESC'), ('2', 'ASC')
    ]
    order = forms.ChoiceField(choices=ch, required=False, initial="1",
                              widget = forms.Select(attrs={'style': 'width:6em'}))

    def __init__(self, *args, **kwargs):
        super(SortPayrollForm, self).__init__(*args, **kwargs)
        self.fields['order'].label = False

class SortPayProcessForm(forms.Form):
    sort_choice = [
        ('1', 'Payroll ID'),
        ('2', 'Installer'),
        ('3', 'Staff'),
        ('4', 'Salesperson')
        ]
    sort_by = forms.ChoiceField(choices=sort_choice, required=False, initial="1",
                                widget = forms.Select(attrs={'style': 'width:6em'}))
    ch = [
        ('1', 'DESC'), ('2', 'ASC')
    ]
    order = forms.ChoiceField(choices=ch, required=False, initial="1",
                              widget = forms.Select(attrs={'style': 'width:6em'}))

    def __init__(self, *args, **kwargs):
        super(SortPayProcessForm, self).__init__(*args, **kwargs)
        self.fields['sort_by'].label = False
        self.fields['order'].label = False

class EditJobForm(forms.Form):
    name = forms.CharField(label='First Name',
                                 max_length=30,
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    last_name = forms.CharField(label='Last Name',
                                max_length=30,
                                widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    address = forms.CharField(label='Address',
                                 max_length=30,
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    address1 = forms.CharField(label='Address1',
                                max_length=30,
                                required=False,
                                widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    city = forms.CharField(label='City',
                                 max_length=30,
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    state = forms.CharField(label='State',
                                max_length=30,
                                required=False,
                                widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    zip_code = forms.CharField(label='Zipcode',
                                 max_length=30,
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    gate_code = forms.CharField(label='Gatecode',
                                 max_length=30,
                                 required=False,
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    nmc_street = forms.CharField(label='Nearest Major Cross Streets',
                                max_length=60,
                                required=False,
                                widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    home_phone = forms.CharField(required=False,
                                 help_text='10 digits, numbers only.',
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    cell_phone = forms.CharField(required=False,
                                 help_text='10 digits, numbers only.',
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    email = forms.CharField(label='Email Address',
                                max_length=50,
                                required=False,
                                widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    detailed_instr = forms.CharField(label='Detailed Instructions',
                                     required=False,
                                     widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':8}))
    priority = forms.BooleanField(label='Priority', required=False, 
                                  widget=forms.CheckboxInput(attrs={'name':'form-trigger',
                                                                    'id':'form-trigger-priority'}))
    priority_notes = forms.CharField(widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':8,
                                                                    'name':'form-content-notes'}),
                                                                    required=False)
    salesperson = forms.ModelChoiceField(queryset=User.objects.filter(groups__name='salesperson')
                                                              .filter(is_active=True),
                                                                      to_field_name='username',
                                                                      required=False)
    sales_date = forms.DateField(widget=DateInput, label='Sales Date', required=False)
    install_schedule = forms.DateField(widget=DateInput, label='Installation Date', required=False)

    def get_type_choices():
        TYPE_CHOICES = []
        for g in ProjectGroup.objects.all():
            group_tup = []
            for pt in ProjectType.objects.filter(group=g.id, active=True):
                choice_tup = (pt.id, pt.proj_type)
                group_tup.append(choice_tup)
            full_group = (g.name, tuple(group_tup))
            TYPE_CHOICES.append(full_group)
            
        return TYPE_CHOICES

    project_type = forms.MultipleChoiceField(choices=get_type_choices,
                                             label="Project Type",
                                             required=False)

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

    association_approval = forms.ChoiceField(
                                choices = ASSOC_APPROV_NEEDED_CHOICES,
                                label='Association Approval Needed',
                                required=False,
                                widget = forms.Select(attrs={'style': 'width:20em; height:2em;'})
                                )
    
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

    permits = forms.ChoiceField(choices=PERMIT_CHOICES,
                                label='Permits',
                                required=False,
                                widget = forms.Select(attrs={'style': 'width:20em; height:2em'}))
    materials_ordered = forms.BooleanField(label='Materials Ordered ?', required=False)

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

    concrete_existing = forms.ChoiceField(choices=CONCRETE_EXISTING_CHOICES,
                                          label='Concrete Existing',
                                          required=False,
                                          widget= forms.Select(attrs={'style': 'width:20em; height:2em;'}))

    NONE = None
    YES = 'YS'
    NO = 'NO'
    FOOTER_NEEDED_CHOICES = [
        (NONE, 'Select...'),
        (YES, 'yes'),
        (NO, 'no')
    ]

    footer_needed = forms.ChoiceField(choices=FOOTER_NEEDED_CHOICES,
                                      label='Footer Needed',
                                      required=False,
                                      widget= forms.Select(attrs={'style': 'width:20em; height:2em;',
                                                           #       'onchange':'showDiv(this)',
                                                                  'id':'footer_form_drop'}))
    footer_dig_date = forms.DateField(widget=DateInput, label='Footer Dig Date', required=False)
    footer_inspection_date = forms.DateField(widget=DateInput, label='Footer Inspection Date', required=False)
    footer_pour_date = forms.DateField(widget=DateInput, label='Footer Pour Date', required=False)
    safety_stakes = forms.BooleanField(label='Safety Stakes', required=False)

    contracts = forms.FileField(label="Contracts",
                                required=False,
                                widget=forms.ClearableFileInput(attrs={'multiple': True, 'style': 'width:20em; height:6em;'}))
    images = forms.FileField(label="Images",
                             required=False,
                             widget=forms.ClearableFileInput(attrs={'multiple': True, 'style': 'width:20em; height:4em;'}))
    contract_amount = forms.DecimalField(label='Total Contract Amount',
                                         max_digits=14,
                                         min_value=0,
                                         decimal_places=2,
                                         required=False)

    price_breakdown = forms.CharField(widget = forms.Textarea(attrs={'style': 'width:15em;', 'rows':4,
                                                                    'name':'form-content-breakdown'}),
                                                                    required=False)

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

    payments = forms.ChoiceField(choices=PAYMENTS_CHOICES,
                                 required=False,
                                 label='Payments',
                                 widget= forms.Select(attrs={'style': 'width:20em; height:2em;',
                                                     #        'onchange':'showPayDiv(this)',
                                                             'id':'payment_form_drop'}))
    downpayment = forms.DecimalField(label='Amount',
                                     max_digits=14,
                                     min_value=0,
                                     decimal_places=2,
                                     required=False)

    installer = forms.ModelChoiceField(queryset=User.objects.filter(groups__name='installer')
                                                              .filter(is_active=True),
                                                                      to_field_name='username',
                                                                      required=False)

    def __init__(self, *args, **kwargs):
        super(EditJobForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4'
        self.helper.field_class = 'col-md-8'
        self.fields['priority_notes'].label = False
        self.fields['footer_dig_date'].label = False
        self.fields['footer_inspection_date'].label = False
        self.fields['footer_pour_date'].label = False

class EditPermitForm(forms.Form):
    name = forms.CharField(label='First Name',
                                 max_length=30,
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    last_name = forms.CharField(label='Last Name',
                                max_length=30,
                                widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))

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

    status = forms.ChoiceField(choices=PERMIT_CHOICES,
                                label='Permits',
                                required=False,
                                widget = forms.Select(attrs={'style': 'width:40em; height:2em'}))
    jurisdiction = forms.ModelChoiceField(queryset=Jurisdiction.objects.filter(active=True))
    permit_number = forms.CharField(label='Permit Number',
                                    max_length=50,
                                    required=False,
                                    widget=forms.Textarea(attrs={'style': 'width:30em;', 'rows':1}))
    description = forms.CharField(label='Description',
                                     required=False,
                                     widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':8}))

class EditAccountForm(forms.Form):
    name = forms.CharField(label='First Name',
                                 max_length=30,
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    last_name = forms.CharField(label='Last Name',
                                max_length=30,
                                widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    address = forms.CharField(label='Address',
                                 max_length=30,
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    address1 = forms.CharField(label='Address1',
                                max_length=30,
                                required=False,
                                widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    city = forms.CharField(label='City',
                                 max_length=30,
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    state = forms.CharField(label='State',
                                max_length=30,
                                required=False,
                                widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    zip_code = forms.CharField(label='Zipcode',
                                 max_length=30,
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    nmc_street = forms.CharField(label='Nearest Major Cross Streets',
                                max_length=60,
                                required=False,
                                widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    home_phone = forms.CharField(required=False,
                                 help_text='10 digits, numbers only.',
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    cell_phone = forms.CharField(required=False,
                                 help_text='10 digits, numbers only.',
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    fax_number = forms.CharField(required=False,
                                 help_text='10 digits, numbers only.',
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    email = forms.CharField(label='Email Address',
                                max_length=50,
                                required=False,
                                widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    detailed_instr = forms.CharField(label='Detailed Instructions',
                                     required=False,
                                     widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':8}))
    priority = forms.BooleanField(label='Priority', required=False, 
                                  widget=forms.CheckboxInput(attrs={'name':'form-trigger',
                                                                    'id':'form-trigger-priority'}))
    priority_notes = forms.CharField(widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':8,
                                                                    'name':'form-content-notes'}),
                                                                    required=False)
    salesperson = forms.ModelChoiceField(queryset=User.objects.filter(groups__name='salesperson')
                                                              .filter(is_active=True),
                                                                      to_field_name='username',
                                                                      required=False)
    schedule_date = forms.DateField(widget=DateInput, label='Schedule Date', required=False)

    def get_type_choices():
        TYPE_CHOICES = []
        for g in ProjectGroup.objects.all():
            group_tup = []
            for pt in ProjectType.objects.filter(group=g.id, active=True):
                choice_tup = (pt.id, pt.proj_type)
                group_tup.append(choice_tup)
            full_group = (g.name, tuple(group_tup))
            TYPE_CHOICES.append(full_group)
            
        return TYPE_CHOICES

    project_type = forms.MultipleChoiceField(choices=get_type_choices,
                                             label="Project Type",
                                             required=False)

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

    alumalattice = forms.ChoiceField(choices=ALUMALATTICE_CHOICES,
                                 required=False,
                                 label='Open Allumalattice',
                                 widget= forms.Select(attrs={'style': 'width:20em; height:2em;',
                                                             'id':'payment_form_drop'}))
    
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

    association_approval = forms.ChoiceField(
                                choices = ASSOC_APPROV_NEEDED_CHOICES,
                                label='Association Approval Needed',
                                required=False,
                                widget = forms.Select(attrs={'style': 'width:20em; height:2em;'})
                                )
    
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

    permits = forms.ChoiceField(choices=PERMIT_CHOICES,
                                label='Permits',
                                required=False,
                                widget = forms.Select(attrs={'style': 'width:20em; height:2em'}))
    materials_ordered = forms.BooleanField(label='Materials Ordered ?', required=False)

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

    concrete_existing = forms.ChoiceField(choices=CONCRETE_EXISTING_CHOICES,
                                          label='Concrete Existing',
                                          required=False,
                                          widget= forms.Select(attrs={'style': 'width:20em; height:2em;'}))

    NONE = None
    YES = 'YS'
    NO = 'NO'
    FOOTER_NEEDED_CHOICES = [
        (NONE, 'Select...'),
        (YES, 'yes'),
        (NO, 'no')
    ]

    footer_needed = forms.ChoiceField(choices=FOOTER_NEEDED_CHOICES,
                                      label='Footer Needed',
                                      required=False,
                                      widget= forms.Select(attrs={'style': 'width:20em; height:2em;',
                                                                  'id':'footer_form_drop'}))
    footer_dig_date = forms.DateField(widget=DateInput, label='Footer Dig Date', required=False)
    footer_inspection_date = forms.DateField(widget=DateInput, label='Footer Inspection Date', required=False)
    footer_pour_date = forms.DateField(widget=DateInput, label='Footer Pour Date', required=False)
    safety_stakes = forms.BooleanField(label='Safety Stakes', required=False)
    contracts = forms.FileField(label="Contracts",
                                required=False,
                                widget=forms.ClearableFileInput(attrs={'multiple': True, 'style': 'width:20em; height:6em;'}))
    images = forms.FileField(label="Images",
                             required=False,
                             widget=forms.ClearableFileInput(attrs={'multiple': True, 'style': 'width:20em; height:4em;'}))
    contract_amount = forms.DecimalField(label='Total Contract Amount',
                                         max_digits=14,
                                         min_value=0,
                                         decimal_places=2,
                                         required=False)

    price_breakdown = forms.CharField(widget = forms.Textarea(attrs={'style': 'width:15em;', 'rows':4,
                                                                    'name':'form-content-breakdown'}),
                                                                    required=False)

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

    payments = forms.ChoiceField(choices=PAYMENTS_CHOICES,
                                 required=False,
                                 label='Payments',
                                 widget= forms.Select(attrs={'style': 'width:20em; height:2em;',
                                                     #        'onchange':'showPayDiv(this)',
                                                             'id':'payment_form_drop'}))
    downpayment = forms.DecimalField(label='Amount',
                                     max_digits=14,
                                     min_value=0,
                                     decimal_places=2,
                                     required=False)

    installer = forms.ModelChoiceField(queryset=User.objects.filter(groups__name='installer')
                                                              .filter(is_active=True),
                                                                      to_field_name='username',
                                                                      required=False)

    def __init__(self, *args, **kwargs):
        super(EditAccountForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4'
        self.helper.field_class = 'col-md-8'
        self.fields['priority_notes'].label = False
        self.fields['footer_dig_date'].label = False
        self.fields['footer_inspection_date'].label = False
        self.fields['footer_pour_date'].label = False

class ServiceForm(forms.Form):
    name = forms.CharField(label='Name',
                                 max_length=80,
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    address = forms.CharField(label='Address',
                                 max_length=120,
                                 widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':1}))
    cust_called = forms.DateField(widget=DateInput, label='Date Customer Called', required=False)
    service_sched = forms.DateField(widget=DateInput, label='Date Service Scheduled', required=False)
    description = forms.CharField(widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':8}),
                                                                    required=False)
    phone_number = forms.CharField(required=False,
                                   help_text='10 digits, numbers only.')
    installer = forms.ModelChoiceField(queryset=User.objects.filter(groups__name='installer')
                                                              .filter(is_active=True),
                                                                      to_field_name='username',
                                                                      required=False)

    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4'
        self.helper.field_class = 'col-md-8'

class InstallerForm(forms.Form):
    job_file = forms.FileField(label='Files',
                               required=False,
                               widget=forms.ClearableFileInput(
                               attrs={'style': 'width:20em; height:6em;'}
                                ))
    job_name = forms.CharField(label="Job Name",
                               max_length=80)
    date_completed = forms.DateField(widget=DateInput, label='Date Completed')
    job_address = forms.CharField(label='Job Address',
                                  max_length=120,
                                  required=False)
    description = forms.CharField(widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':8}),
                                                                    required=False)
    helper = forms.BooleanField(label='Helper', required=False)
    helper_name = forms.CharField(label='Helper Name', max_length=60, required=False)
    work_performed = forms.CharField(widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':8}),
                                    required=False)
    amount_owed = forms.DecimalField(label='Amount Owed',
                                     max_digits=14,
                                     min_value=0,
                                     decimal_places=2,
                                     required=False)

    def __init__(self, *args, **kwargs):
        super(InstallerForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

class StaffForm(forms.Form):
    monday_date = forms.DateField(widget=DateInput, required=False)
    monday_in_hr = forms.DecimalField(max_digits=4, min_value=1, decimal_places=0, required=False)
    monday_in_min = forms.DecimalField(max_digits=4, min_value=0, decimal_places=0, required=False)
    monday_out_hr = forms.DecimalField(max_digits=4, min_value=1, decimal_places=0, required=False)
    monday_out_min = forms.DecimalField(max_digits=4, min_value=0, decimal_places=0, required=False)
    monday_tot = forms.DecimalField(max_digits=4, min_value=0, decimal_places=2, required=False,
                                    widget=forms.NumberInput(attrs={'class':'day-tot'}))
    tuesday_date = forms.DateField(widget=DateInput, required=False)
    tuesday_in_hr = forms.DecimalField(max_digits=4, min_value=1, decimal_places=0, required=False)
    tuesday_in_min = forms.DecimalField(max_digits=4, min_value=0, decimal_places=0, required=False)
    tuesday_out_hr = forms.DecimalField(max_digits=4, min_value=1, decimal_places=0, required=False)
    tuesday_out_min = forms.DecimalField(max_digits=4, min_value=0, decimal_places=0, required=False)
    tuesday_tot = forms.DecimalField(max_digits=4, min_value=0, decimal_places=2, required=False,
                                     widget=forms.NumberInput(attrs={'class':'day-tot'}))
    wednesday_date = forms.DateField(widget=DateInput, required=False)
    wednesday_in_hr = forms.DecimalField(max_digits=4, min_value=1, decimal_places=0, required=False)
    wednesday_in_min = forms.DecimalField(max_digits=4, min_value=0, decimal_places=0, required=False)
    wednesday_out_hr = forms.DecimalField(max_digits=4, min_value=1, decimal_places=0, required=False)
    wednesday_out_min = forms.DecimalField(max_digits=4, min_value=0, decimal_places=0, required=False)
    wednesday_tot = forms.DecimalField(max_digits=4, min_value=0, decimal_places=2, required=False,
                                       widget=forms.NumberInput(attrs={'class':'day-tot'}))
    thursday_date = forms.DateField(widget=DateInput, required=False)
    thursday_in_hr = forms.DecimalField(max_digits=4, min_value=1, decimal_places=0, required=False)
    thursday_in_min = forms.DecimalField(max_digits=4, min_value=0, decimal_places=0, required=False)
    thursday_out_hr = forms.DecimalField(max_digits=4, min_value=1, decimal_places=0, required=False)
    thursday_out_min = forms.DecimalField(max_digits=4, min_value=0, decimal_places=0, required=False)
    thursday_tot = forms.DecimalField(max_digits=4, min_value=0, decimal_places=2, required=False,
                                      widget=forms.NumberInput(attrs={'class':'day-tot'}))
    friday_date = forms.DateField(widget=DateInput, required=False)
    friday_in_hr = forms.DecimalField(max_digits=4, min_value=1, decimal_places=0, required=False)
    friday_in_min = forms.DecimalField(max_digits=4, min_value=0, decimal_places=0, required=False)
    friday_out_hr = forms.DecimalField(max_digits=4, min_value=1, decimal_places=0, required=False)
    friday_out_min = forms.DecimalField(max_digits=4, min_value=0, decimal_places=0, required=False)
    friday_tot = forms.DecimalField(max_digits=4, min_value=0, decimal_places=2, required=False,
                                    widget=forms.NumberInput(attrs={'class':'day-tot'}))
    saturday_date = forms.DateField(widget=DateInput, required=False)
    saturday_in_hr = forms.DecimalField(max_digits=4, min_value=1, decimal_places=0, required=False)
    saturday_in_min = forms.DecimalField(max_digits=4, min_value=0, decimal_places=0, required=False)
    saturday_out_hr = forms.DecimalField(max_digits=4, min_value=1, decimal_places=0, required=False)
    saturday_out_min = forms.DecimalField(max_digits=4, min_value=0, decimal_places=0, required=False)
    saturday_tot = forms.DecimalField(max_digits=4, min_value=0, decimal_places=2, required=False,
                                      widget=forms.NumberInput(attrs={'class':'day-tot'}))
    sunday_date = forms.DateField(widget=DateInput, required=False)
    sunday_in_hr = forms.DecimalField(max_digits=4, min_value=1, decimal_places=0, required=False)
    sunday_in_min = forms.DecimalField(max_digits=4, min_value=0, decimal_places=0, required=False)
    sunday_out_hr = forms.DecimalField(max_digits=4, min_value=1, decimal_places=0, required=False)
    sunday_out_min = forms.DecimalField(max_digits=4, min_value=0, decimal_places=0, required=False)
    sunday_tot = forms.DecimalField(max_digits=4, min_value=0, decimal_places=2, required=False,
                                    widget=forms.NumberInput(attrs={'class':'day-tot'}))
    weekly_hours = forms.DecimalField(max_digits=4, min_value=0, decimal_places=2)
    hourly_rate = forms.DecimalField(max_digits=14, min_value=1, decimal_places=2, label="Hourly Rate")
    week_start_date = forms.DateField(widget=DateInput, required=False, label="Week Start Date")
    payroll_notes = forms.CharField(widget = forms.Textarea(attrs={'style': 'width:12em;', 'rows':1,
                                                                    'name':'form-content-breakdown'}),
                                                                    required=False,
                                                                    label="Payroll Notes")
    upload_file = forms.FileField(label="Upload File",
                                required=False,
                                widget=forms.ClearableFileInput(
                                    attrs={'style': 'width:20em; height:6em;'})
                                )

    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['monday_date'].label = False
        self.fields['monday_in_hr'].label = False
        self.fields['monday_in_min'].label = False
        self.fields['monday_out_hr'].label = False
        self.fields['monday_out_min'].label = False
        self.fields['monday_tot'].label = False
        self.fields['tuesday_date'].label = False
        self.fields['tuesday_in_hr'].label = False
        self.fields['tuesday_in_min'].label = False
        self.fields['tuesday_out_hr'].label = False
        self.fields['tuesday_out_min'].label = False
        self.fields['tuesday_tot'].label = False
        self.fields['wednesday_date'].label = False
        self.fields['wednesday_in_hr'].label = False
        self.fields['wednesday_in_min'].label = False
        self.fields['wednesday_out_hr'].label = False
        self.fields['wednesday_out_min'].label = False
        self.fields['wednesday_tot'].label = False
        self.fields['thursday_date'].label = False
        self.fields['thursday_in_hr'].label = False
        self.fields['thursday_in_min'].label = False
        self.fields['thursday_out_hr'].label = False
        self.fields['thursday_out_min'].label = False
        self.fields['thursday_tot'].label = False
        self.fields['friday_date'].label = False
        self.fields['friday_in_hr'].label = False
        self.fields['friday_in_min'].label = False
        self.fields['friday_out_hr'].label = False
        self.fields['friday_out_min'].label = False
        self.fields['friday_tot'].label = False
        self.fields['saturday_date'].label = False
        self.fields['saturday_in_hr'].label = False
        self.fields['saturday_in_min'].label = False
        self.fields['saturday_out_hr'].label = False
        self.fields['saturday_out_min'].label = False
        self.fields['saturday_tot'].label = False
        self.fields['sunday_date'].label = False
        self.fields['sunday_in_hr'].label = False
        self.fields['sunday_in_min'].label = False
        self.fields['sunday_out_hr'].label = False
        self.fields['sunday_out_min'].label = False
        self.fields['sunday_tot'].label = False

class SalesForm(ModelForm):
    class Meta:
        model = Sales_Payroll
        fields = ['salesperson', 'job_name', 'date_added', 'status', 'contract_amount', 'commission']
        widgets = {
            'date_added': DateInput
        }

    def __init__(self, *args, **kwargs):
        super(SalesForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['salesperson'].widget.attrs={'id': 'salesperson-pay'}
        self.fields['job_name'].widget.attrs={'id': 'job-name-sales-pay'}
        self.fields['date_added'].widget.attrs={'id': 'date-added-sales-pay'}
        self.fields['date_added'].required = True
        self.fields['status'].widget.attrs={'id': 'status-sales-pay'}
        self.fields['job_name'].label = ''
        self.fields['status'].label = ''
        self.fields['contract_amount'].label = ''
        self.fields['commission'].label = ''

    def clean(self):
        cleaned_data = self.cleaned_data

        return cleaned_data

class SalespersonPayEditForm(ModelForm):
    class Meta:
        model = Sales_Payroll
        fields = ['salesperson', 'date_added']
        widgets = {
            'date_added': DateInput
        }

    def __init__(self, *args, **kwargs):
        super(SalespersonPayEditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['salesperson'].widget.attrs={'id': 'salesperson-pay'}
        self.fields['date_added'].widget.attrs={'id': 'date-added-sales-pay'}

    def clean(self):
        cleaned_data = self.cleaned_data

        return cleaned_data

class SalesPayEditForm(ModelForm):
    class Meta:
        model = Sales_Payroll
        fields = ['id', 'job_name', 'status', 'contract_amount', 'commission']

    def __init__(self, *args, **kwargs):
        super(SalesPayEditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['job_name'].label = False
        self.fields['status'].label = False
        self.fields['contract_amount'].label = False
        self.fields['commission'].label = False
        

    def clean(self):
        # cleaned_data = self.cleaned_data
        cleaned_data = super(SalesPayEditForm, self).clean()
        id = cleaned_data['id']

        return cleaned_data

SalesEditFormSet = modelformset_factory(
    Sales_Payroll,
    fields=('id', 'job_name', 'status', 'contract_amount', 'commission'),
    form=SalesPayEditForm,
    extra=0,
    widgets={
        'date_added': DateInput,
        # 'id': HiddenInput()
    }
)

SalesFormSet = modelformset_factory(
    Sales_Payroll,
    fields=('id', 'job_name', 'status', 'contract_amount', 'commission', 'salesperson', 'date_added'),
    form=SalesForm,
    extra=1,
    widgets={
        'date_added': DateInput
    }
)

class InstallAppointmentForm(ModelForm):
    class Meta:
        model = Installation
        fields = ['installer', 'install_schedule']
        widgets = {
            'install_schedule': DateInput
        }
        labels = {
            'install_schedule': 'Date'
        }

    def __init__(self, *args, **kwargs):
        super(InstallAppointmentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['installer'].widget.attrs={'id': 'edit-installer-cal'}
        self.fields['install_schedule'].widget.attrs={'id': 'edit-install-date-cal'}

    def clean(self):
        cleaned_data = self.cleaned_data

        return cleaned_data

class SelectInstallerForm(ModelForm):

    installer = forms.ModelChoiceField(queryset=User.objects.filter(groups__name='installer')
                                                              .filter(is_active=True),
                                                                      to_field_name='username',
                                                                      required=False,
                                                                      initial='all',
                                                                      widget=forms.Select(attrs={
                                                                          'onchange': 'this.form.submit();'
                                                                      }),
                                       empty_label="all",
                                       label="Installer:")
    class Meta:
        model = Installation
        fields = ['installer']

    def __init__(self, *args, **kwargs):
        super(SelectInstallerForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

class EditAppointmentCalendarForm(ModelForm):
    salesperson = forms.ModelChoiceField(queryset=User.objects.filter(groups__name='salesperson')
                                                            .filter(is_active=True),
                                                                    to_field_name='username')
    appointment_date = forms.DateField(widget=DateInput, label='Date and Time')
    appointment_time = forms.TimeField(label = ' ', required=False, input_formats=valid_time_inputs,
                           widget=forms.TimeInput(attrs={'style': 'width:5em;', 'rows':1}))
    ap = [("1", "AM"), ("2", "PM")]
    time_ap = forms.ChoiceField(choices=ap, label=' ', required=False,
                                widget = forms.Select(attrs={'style': 'width:6em'}))

    class Meta:
        model = Lead
        fields = ['salesperson', 'appointment_date', 'appointment_time']
        labels = {
            'appointment_date': 'Date',
            'appointment_time': 'Time'
        }

    def __init__(self, *args, **kwargs):
        super(EditAppointmentCalendarForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['salesperson'].widget.attrs={'id': 'edit-salesperson-cal'}
        self.fields['appointment_date'].widget.attrs={'id': 'edit-appointment-date-cal'}
        self.fields['appointment_time'].widget.attrs={'id': 'edit-appointment-time-cal',
                                                      'style': 'width:6em;', 'rows':1}
    def clean(self):
        cleaned_data = self.cleaned_data

        return cleaned_data

class EmployeeDocsForm(ModelForm):
    headline = forms.CharField(max_length=250, required=False)
    description = forms.CharField(widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':8}),
                                                                    required=False)
    
    class Meta:
        model = Employee_Documents
        fields = ['headline', 'description']

    def __init__(self, *args, **kwargs):
        super(EmployeeDocsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

class JobSearchForm(forms.Form):
    first_name = forms.CharField(max_length=40, required=False, label='First Name:')
    last_name = forms.CharField(max_length=40, required=False, label='Last Name:')
    address = forms.CharField(max_length=100, required=False, label='Address:')
    city = forms.CharField(max_length=40, required=False, label='City:')
    state = forms.CharField(max_length=20, required=False, label='State:')
    phone_number = forms.CharField(max_length=20, required=False, label='Phone Number:')
    cross_streets = forms.CharField(max_length=150, required=False, label='Cross Streets:')
    project_notes = forms.CharField(required=False,
                                    label='Project Notes:',
                                    widget = forms.Textarea(attrs={'style': 'width:20em;', 'rows':4}))

    def get_type_choices():
        TYPE_CHOICES = []
        for g in ProjectGroup.objects.all():
            group_tup = []
            for pt in ProjectType.objects.filter(group=g.id):
                choice_tup = (pt.id, pt.proj_type)
                group_tup.append(choice_tup)
            full_group = (g.name, tuple(group_tup))
            TYPE_CHOICES.append(full_group)
        none = (None, 'Select...')
        TYPE_CHOICES.append(none)
            
        return TYPE_CHOICES

    project_type = forms.ChoiceField(choices=get_type_choices,
                                     label="Project Type:",
                                     required=False)
    salesperson = forms.ModelChoiceField(queryset=User.objects.filter(groups__name='salesperson'),
                                                                      to_field_name='username',
                                                                      required=False,
                                                                      label='Salesperson:')

    def __init__(self, *args, **kwargs):
        super(JobSearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.fields['project_type'].widget.attrs={'id': 'search-type'}