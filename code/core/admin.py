from django.contrib import admin
from .models import Course, CourseMember, CourseContent, Comment

# Mendaftarkan model agar muncul di halaman Admin
admin.site.register(Course)
admin.site.register(CourseMember)
admin.site.register(CourseContent)
admin.site.register(Comment)