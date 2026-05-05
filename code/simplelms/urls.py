from django.contrib import admin
from django.urls import path, include
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('silk/', include('silk.urls', namespace='silk')),
    path('course-stat/', views.courseStat),
    path('stats/', views.userStat),
    path('api/all-course/', views.allCourse),
    path('api/user-courses/', views.userCourses),
    path('api/course-stat/', views.courseStat),
    path('api/course-member-stat/', views.courseMemberStat),
]