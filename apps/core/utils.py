# management/utils.py

from datetime import datetime, timedelta
from calendar import HTMLCalendar
from .models import Installation, Lead, Customer
from apps.core.forms import InstallAppointmentForm, EditAppointmentCalendarForm
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

class Calendar(HTMLCalendar):
	def __init__(self, year=None, month=None):
		self.year = year
		self.month = month
		super(Calendar, self).__init__()

	# formats a day as a td
	# filter events by day
	def formatday(self, day, events):
		events_per_day = events.filter(install_schedule__day=day)
		d = ''
		phone_list = []
		for event in events_per_day:
			if event.job.client_id.home_phone:
				phone_list.append(event.job.client_id.home_phone)
			else:
				phone_list.append('')
			if event.job.client_id.cell_phone:
				phone_list.append(event.job.client_id.cell_phone)
			else:
				phone_list.append('')
			pTypes=[]
			for pt in event.job.project_type.all():
				pTypes.append(str(pt))
			projects = ','.join(pTypes)

			if event.job.priority:
				leadtag = ' id="priority" '
				leadspan = '<span class="CalComment">' + event.job.priority_msg + '</span>'
			else:
				leadtag = ''
				leadspan = ''

			d += '<li'+leadtag+'><a href="'+event.job.get_absolute_url()+f'">{event.job.client_id}</a>' + leadspan +'''</li>
			\n<table class='job-table'>
			    <tr>
			      <td>Installer</td><td>'''+f'{event.installer}</td>'+'''
				</tr>
				<tr>
			      <td>Address</td><td>'''+f'{event.job.client_id.address} {event.job.client_id.address1}</td>'+'''
				</tr>
				<tr>
				  <td>City</td><td>'''+f'{event.job.client_id.city}</td>'+'''
				</tr>
				<tr>
				  <td>Gate Code</td><td>'''+f'{event.job.client_id.gate_code}</td>'+'''
				</tr>
				<tr>
				  <td>Phone</td><td>'''+f'{phone_list[0]}\n{phone_list[1]}'+'''</td>
				</tr>
				<tr>
				  <td>Project Type</td><td>'''+f'{projects}'+'''</td>
				</tr>
				<tr>
				  <td class="install-trigger" colspan="2" style="text-align:center;">
				    <a href="'''+event.get_absolute_url()+'''">Edit</a></td>
				</tr>
			</table>
			<br><br>'''

		if day != 0:
			if '<tr>' in d:
				return f"<td class='full'><span class='date'>{day}</span><ul style='list-style:none;'> {d} </ul></td>"
			else:
				return f"<td class='empty'><span class='date'>{day}</span><ul> {d} </ul></td>"
		return '<td></td>'

	# formats a week as a tr 
	def formatweek(self, theweek, events):
		week = ''
		dow = ''
		for d, weekday in theweek:
			week += self.formatday(d, events)
		if '<li>' in week:
			return f'<tr> {week} </tr>'
		else:
			return f'<tr class="empty"> {week} </tr>'

	# formats a month as a table
	# filter events by year and month
	def formatmonth(self, withyear=True):
		events = Installation.objects.filter(install_schedule__year=self.year, install_schedule__month=self.month)

		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
		cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		cal += f'{self.formatweekheader()}\n'
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week, events)}\n'
		return cal

class EditCalendar(HTMLCalendar):
	def __init__(self, year=None, month=None):
		self.year = year
		self.month = month
		super(EditCalendar, self).__init__()

	# formats a day as a td
	# filter events by day
	def formatday(self, day, events):
		events_per_day = events.filter(install_schedule__day=day)
		d = ''
		phone_list = []
		for event in events_per_day:
			if event.job.client_id.home_phone:
				phone_list.append(event.job.client_id.home_phone)
			else:
				phone_list.append('')
			if event.job.client_id.cell_phone:
				phone_list.append(event.job.client_id.cell_phone)
			else:
				phone_list.append('')
			pTypes=[]
			for pt in event.job.project_type.all():
				pTypes.append(str(pt))
			projects = ','.join(pTypes)
			form = InstallAppointmentForm(initial = {
				'installer': event.installer,
				'install_schedule': event.install_schedule
			})

			d += '<li><a href="'+event.job.get_absolute_url()+f'">{event.job.client_id}</a></li>'+'''
			\n<table class='calendar-table'>
			    <tr>
			      <td>Installer</td><td>'''+f'{event.installer}</td>'+'''
				</tr>
				<tr>
				  <td>Project Type</td><td>'''+f'{projects}'+'''</td>
				</tr>
			</table>
			<br>'''

		if day != 0:
			if '<li>' in d:
				return f"<td class='full'><span class='date'>{day}</span><ul style='list-style:none;'> {d} </ul></td>"
			else:

				return f"<td class='empty'><span class='date'>{day}</span><ul> {d} </ul></td>"
		return '<td></td>'

	# formats a week as a tr 
	def formatweek(self, theweek, events):
		week = ''
		dow = ''
		for d, weekday in theweek:
			week += self.formatday(d, events)
		if '<li>' in week:
			return f'<tr> {week} </tr>'
		else:
			return f'<tr class="empty"> {week} </tr>'

	# formats a month as a table
	# filter events by year and month
	def formatmonth(self, withyear=True):
		events = Installation.objects.filter(install_schedule__year=self.year, install_schedule__month=self.month)

		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="editcalendar">\n'
		cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		cal += f'{self.formatweekheader()}\n'
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week, events)}\n'
		return cal

class InstallerCalendar(HTMLCalendar):
	def __init__(self, installer, request, year=None, month=None):
		self.installer = installer
		self.request = request
		self.year = year
		self.month = month
		super(InstallerCalendar, self).__init__()

	# formats a day as a td
	# filter events by day
	def formatday(self, day, events, *args, **kwargs):
		events_per_day = events.filter(install_schedule__day=day, installer=self.installer)

		d = ''
		phone_list = []
		for event in events_per_day:
			if event.job.client_id.home_phone:
				phone_list.append(event.job.client_id.home_phone)
			else:
				phone_list.append('')
			if event.job.client_id.cell_phone:
				phone_list.append(event.job.client_id.cell_phone)
			else:
				phone_list.append('')
			pTypes=[]
			for pt in event.job.project_type.all():
				pTypes.append(str(pt))
			projects = ','.join(pTypes)

			d += '<li><a href="'+event.job.get_absolute_url()+f'">{event.job.client_id}</a></li>'+'''
			\n<table class='job-table'>
			    <tr>
			      <td>Installer</td><td>'''+f'{event.installer}</td>'+'''
				</tr>
				<tr>
			      <td>Address</td><td>'''+f'{event.job.client_id.address} {event.job.client_id.address1}</td>'+'''
				</tr>
				<tr>
				  <td>City</td><td>'''+f'{event.job.client_id.city}</td>'+'''
				</tr>
				<tr>
				  <td>Gate Code</td><td>'''+f'{event.job.client_id.gate_code}</td>'+'''
				</tr>
				<tr>
				  <td>Phone</td><td>'''+f'{phone_list[0]}\n{phone_list[1]}'+'''</td>
				</tr>
				<tr>
				  <td>Project Type</td><td>'''+f'{projects}'+'''</td>
				</tr>'''

			if self.request.user.groups.filter(name='installer'):
				d +='''
			</table>
			<br><br>'''
			else:
				d += '''
				<tr>
				  <td class="install-trigger" colspan="2" style="text-align:center;">
				    <a href="'''+event.get_absolute_url()+'''">Edit</a></td>
				</tr>
			</table>
			<br><br>'''

		if day != 0:
			if '<li>' in d:
				return f"<td class='full'><span class='date'>{day}</span><ul style='list-style:none;'> {d} </ul></td>"
			else:

				return f"<td class='empty'><span class='date'>{day}</span><ul> {d} </ul></td>"
		return '<td></td>'

	# formats a week as a tr 
	def formatweek(self, theweek, events):
		week = ''
		dow = ''
		for d, weekday in theweek:
			week += self.formatday(d, events)
		if '<li>' in week:
			return f'<tr> {week} </tr>'
		else:
			return f'<tr class="empty"> {week} </tr>'

	# formats a month as a table
	# filter events by year and month
	def formatmonth(self, withyear=True, *args, **kwargs):

		events = Installation.objects.filter(
			install_schedule__year=self.year, install_schedule__month=self.month
		)

		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
		cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		cal += f'{self.formatweekheader()}\n'
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week, events)}\n'
		return cal

class AppointmentCalendar(HTMLCalendar):
	def __init__(self, year=None, month=None):
		self.year = year
		self.month = month
		super(AppointmentCalendar, self).__init__()

	# formats a day as a td
	# filter events by day
	def formatday(self, day, events):
		events_per_day = events.filter(appointment_date__day=day).order_by('appointment_time')
		d = ''
		for event in events_per_day:

			d += '<li><a href="'+event.get_appointment_url()+f'">{event.client_id}</a></li>'+'''
			\n<table class='job-table'>
			    <tr>
			      <td>NMC Street</td><td>'''+f'{event.client_id.nmc_street}</td>'+'''
				</tr>
				<tr>
			      <td>City</td><td>'''+f'{event.client_id.city}</td>'+'''
				</tr>
				<tr>
				  <td>Time</td><td>'''+f'{event.appointment_time.strftime("%I:%M %p")}</td>'+'''
				</tr>
				<tr>
				  <td>Salesperson</td><td>'''+f'{event.salesperson}'+'''</td>
				</tr>
				<tr>
				  <td class="install-trigger" colspan="2" style="text-align:center;">
				    <a href="'''+event.get_edit_calendar_url()+'''">Edit</a></td>
				</tr>
			</table>
			<br><br>'''

		if day != 0:
			if '<li>' in d:
				return f"<td class='full'><span class='date'>{day}</span><ul style='list-style:none;'> {d} </ul></td>"
			else:

				return f"<td class='empty'><span class='date'>{day}</span><ul> {d} </ul></td>"
		return '<td></td>'

	# formats a week as a tr 
	def formatweek(self, theweek, events):
		week = ''
		dow = ''
		for d, weekday in theweek:
			week += self.formatday(d, events)
		if '<li>' in week:
			return f'<tr> {week} </tr>'
		else:
			return f'<tr class="empty"> {week} </tr>'

	# formats a month as a table
	# filter events by year and month
	def formatmonth(self, withyear=True):
		events = Lead.objects.filter(appointment_date__year=self.year,
									 appointment_date__month=self.month,
									 lead_status='6')

		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
		cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		cal += f'{self.formatweekheader()}\n'
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week, events)}\n'
		return cal

class EditAppointmentCalendar(HTMLCalendar):
	def __init__(self, year=None, month=None):
		self.year = year
		self.month = month
		super(EditAppointmentCalendar, self).__init__()

	# formats a day as a td
	# filter events by day
	def formatday(self, day, events):
		events_per_day = events.filter(appointment_date__day=day)
		d = ''
		for event in events_per_day:
			form = EditAppointmentCalendarForm(initial = {
				'salesperson': event.salesperson,
				'appointment_date': event.appointment_date,
				'appointment_time': event.appointment_time
			})

			d += '<li><a href="'+event.get_appointment_url()+f'">{event.client_id}</a></li>'+'''
			\n<table class='edit-appointment-table'>
				  <td>Time</td><td>'''+f'{event.appointment_time.strftime("%I:%M %p")}</td>'+'''
				</tr>
				<tr>
				  <td>Salesperson</td><td>'''+f'{event.salesperson}'+'''</td>
				</tr>
				<tr>
				  <td class="install-trigger" colspan="2" style="text-align:center;">
				    <a href="'''+event.get_edit_calendar_url()+'''">Edit</a></td>
				</tr>
			</table>
			<br>'''

		if day != 0:
			if '<li>' in d:
				return f"<td class='full'><span class='date'>{day}</span><ul style='list-style:none;'> {d} </ul></td>"
			else:

				return f"<td class='empty'><span class='date'>{day}</span><ul> {d} </ul></td>"
		return '<td></td>'

	# formats a week as a tr 
	def formatweek(self, theweek, events):
		week = ''
		dow = ''
		for d, weekday in theweek:
			week += self.formatday(d, events)
		if '<li>' in week:
			return f'<tr> {week} </tr>'
		else:
			return f'<tr class="empty"> {week} </tr>'

	# formats a month as a table
	# filter events by year and month
	def formatmonth(self, withyear=True):
		events = Lead.objects.filter(appointment_date__year=self.year, appointment_date__month=self.month)

		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="editcalendar">\n'
		cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		cal += f'{self.formatweekheader()}\n'
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week, events)}\n'
		return cal
