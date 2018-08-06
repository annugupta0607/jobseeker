import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobseeker.settings')

import django
django.setup()

import csv
from jobseeker.models import Applicant, Course

with open("jobseeker/Data.csv", 'r') as csvfile:
    next(csvfile)
    reader = csv.reader(csvfile)

    for i, row in enumerate(reader):
        print(len(row))

        applicant = Applicant.objects.create(name=row[2], mobile_num=str(i)+row[3], email_id=str(i)+row[4], resume=row[1],
                                             work_exp=row[5] if row[5] else 0, analytics_exp=row[6] if row[6] else 0,
                                             current_loc=row[7], corrected_loc=row[8], near_city=row[9],
                                             preferred_loc=row[10], ctc=row[11], current_employer=row[12],
                                             current_designation=row[13], skills=row[14])

        if row[15].strip:
            course = Course.objects.create(applicant=applicant, course_type="UG", course_name=row[15],
                                            correct_course_name=row[16], institute_name=row[17],
                                            tier1=row[18], passing_year=row[19])

        if row[20].strip:
            course = Course.objects.create(applicant=applicant, course_type="PG", course_name=row[20],
                                           correct_course_name=row[21], institute_name=row[22],
                                           tier1=row[23], passing_year=row[24])


        if row[25].strip:
            course = Course.objects.create(applicant=applicant, course_type="PPG", course_name=row[25],
                                           correct_course_name=row[26] )