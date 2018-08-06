from datetime import datetime

from django.contrib.auth.models import User, Permission
from django.core import exceptions
from django.db import models


class RobustBooleanField(models.BooleanField):
    def to_python(self, value):
        if value in (True, False):
            # if value is 1 or 0 than it's equal to True or False, but we want
            # to return a true bool for semantic reasons.
            return bool(value)
        if value in ('t', 'True', '1', 'Yes', 'Y', 'on'):
            return True
        if value in ('f', 'False', '0', 'No', 'N', 'off'):
            return False
        raise exceptions.ValidationError(
            self.error_messages['invalid'],
            code='invalid',
            params={'value': value},
        )


class Applicant(models.Model):
    name = models.CharField(max_length=256)
    mobile_num = models.CharField(max_length=20, unique=True)  # Skipped validation
    email_id = models.CharField(max_length=256, unique=True)
    resume = RobustBooleanField()
    work_exp = models.DecimalField(decimal_places=2, max_digits=12, default=0)
    analytics_exp = models.DecimalField(decimal_places=2, max_digits=12, default=0)
    current_loc = models.CharField(max_length=256)
    corrected_loc = models.CharField(max_length=256)
    near_city = models.CharField(max_length=256)
    preferred_loc = models.CharField(max_length=256)
    ctc = models.DecimalField(decimal_places=2, max_digits=12, default=0)
    current_employer = models.CharField(max_length=256, null=True)
    current_designation = models.CharField(max_length=256, null=True)
    skills = models.CharField(max_length=700, null=True)

    def __str__(self):
        return self.name + ":   " + self.mobile_num + ": " + self.email_id


class Course(models.Model):
    UNDERGRADUATE = 'UG'
    POSTGRADUATE = 'PG'
    POST_2_GRADUATE = 'PPG'

    COURSE_CHOICE = (
        (UNDERGRADUATE, 'U.G. Course'),
        (POSTGRADUATE, 'P.G. Course'),
        (POST_2_GRADUATE, 'Post P.G. Course'),
    )
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    course_type = models.CharField(max_length=3, choices=COURSE_CHOICE,)
    course_name = models.CharField(max_length=100)
    correct_course_name = models.CharField(max_length=100)
    institute_name = models.CharField(max_length=256)
    tier1 = RobustBooleanField(default=False)
    passing_year = models.CharField(max_length=4)


    def __str__(self):
        return self.applicant.name + ": " + self.course_name + ":    " + self.passing_year


class Recruiter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'is_superuser': False})
    download_limit = models.IntegerField(default=5)
    today_download = models.IntegerField(default=0)
    last_download = models.DateTimeField(default=datetime.now)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.user.is_superuser = False
        self.user.is_staff = True
        self.user.user_permissions.add(Permission.objects.get(name='Can change applicant'))
        self.user.save()
        super().save(force_insert, force_update, using, update_fields)
