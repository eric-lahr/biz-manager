from django.contrib import admin
from .models import (Jurisdiction, Employee_Documents, SourceGroup, ProjectGroup,
Employee_Files)
from management.forms import EmployeeDocsForm

# Register your models here.

admin.site.register(ProjectGroup)
admin.site.register(SourceGroup)
admin.site.register(Jurisdiction)
admin.site.register(Employee_Documents)
admin.site.register(Employee_Files)

class EmployeeFormsAndDocs(admin.ModelAdmin):
    form = EmployeeDocsForm

    def has_add_permission(self, request):
        if self.model.objects.count() > 0:
            return False
        else:
            return True
