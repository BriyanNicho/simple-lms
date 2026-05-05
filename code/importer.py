import os
import sys
import csv

# Mengatur environment agar script ini bisa menggunakan fitur Django
sys.path.append(os.path.abspath(os.path.join(__file__, *[os.pardir] * 3)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'simplelms.settings'
import django
django.setup()

from django.contrib.auth.models import User
from core.models import Course, CourseMember

# 1. Import Data User
with open('./csv_data/user-data.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for num, row in enumerate(reader):
        if not User.objects.filter(username=row['username']).exists():
            User.objects.create_user(
                id=num+2, 
                username=row['username'],
                password=row['password'],
                email=row['email']
            )
    print("Berhasil import data User!")

# 2. Import Data Course
with open('./csv_data/course-data.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for num, row in enumerate(reader):
        if not Course.objects.filter(pk=num+1).exists():
            Course.objects.create(
                id=num+1, 
                name=row['name'],
                description=row['description'],
                price=row['price'],
                teacher=User.objects.get(pk=int(row['teacher']))
            )
    print("Berhasil import data Course!")

# 3. Import Data Member (CourseMember)
with open('./csv_data/member-data.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for num, row in enumerate(reader):
        if not CourseMember.objects.filter(pk=num+1).exists():
            CourseMember.objects.create(
                id=num+1,
                course_id=Course.objects.get(pk=int(row['course_id'])),
                user_id=User.objects.get(pk=int(row['user_id'])),
                roles=row['roles']
            )
    print("Berhasil import data Course Member!")