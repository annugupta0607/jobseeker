import csv
from datetime import datetime

from django.contrib import admin, messages
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from django.views.decorators.cache import never_cache
from django.http import HttpResponse

from .models import Applicant, Course, Recruiter


class CustomAdminSite(AdminSite):
    @never_cache
    def index(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        extra_context['fields'] = [f.name for f in Applicant._meta.get_fields()]

        return super().index(request, extra_context)


admin_site = CustomAdminSite(name='customadmin')


admin_site.register(Course)


class StudentCoursesInline(admin.TabularInline):
    model = Course
    extra = 0
    verbose_name_plural = 'Courses'


def make_published(self, request, queryset):
    recruiter = Recruiter.objects.get(user=request.user)
    if recruiter.last_download.date() < datetime.now().date():
        recruiter.last_download = datetime.now()
        recruiter.today_download = 0
        recruiter.save()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
    writer = csv.writer(response)
    writer.writerow(['NAME', 'EMAIL'])

    for applicant in queryset:
        if recruiter.today_download >= recruiter.download_limit:
            writer.writerow(["ERROR", "Download limit reached"])
            break
        writer.writerow([applicant.name, applicant.email_id])
        recruiter.today_download += 1
    recruiter.last_download = datetime.now()
    recruiter.save()

    return response

make_published.short_description = "Save as CSV"


class ApplicantAdmin(admin.ModelAdmin):
    inlines = [StudentCoursesInline, ]
    list_display = ["name", "mobile_num", "email_id"]
    actions = [make_published]
    change_list_template = "applicant_list.html"

    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
            super().save_model(request, obj, form, change)
        else:
            messages.error(request, "Discarding your changes. You are not authorized to change data")

    def get_list_display_links(self, request, list_display):
        if request.user.is_superuser:
            return super().get_list_display_links(request, list_display)
        else:
            return []


admin_site.register(Applicant, ApplicantAdmin)

admin_site.index_template = "applicant_admin.html"

admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)


class RecruiterAdmin(admin.ModelAdmin):
    list_display = ["user", "download_limit", "today_download", "last_download"]


admin_site.register(Recruiter, RecruiterAdmin)
