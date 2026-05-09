from django.contrib import admin
from django.urls import path, include
from core import views

urlpatterns = [
    # Auth
    path("login/", views.login_user, name="login"),
    path("register/", views.register_user, name="register"),
    path("logout/", views.logout_user, name="logout"),
    path("auth/", include("django.contrib.auth.urls")),
    # LMS Views
    path("", views.home, name="home"),
    path("course/<int:pk>/", views.course_detail, name="course_detail"),
    path("course/<int:pk>/enroll/", views.enroll_course, name="enroll_course"),
    path("course/<int:pk>/learn/", views.learn_course, name="learn_course"),
    path("assignment/<int:pk>/", views.assignment_detail, name="assignment_detail"),
    path("quiz/<int:pk>/", views.quiz_detail, name="quiz_detail"),
    path("course/<int:course_id>/forum/", views.forum_list, name="forum_list"),
    path("forum/<int:pk>/", views.forum_detail, name="forum_detail"),
    path(
        "course/<int:course_id>/attendance/",
        views.attendance_list,
        name="attendance_list",
    ),
    path(
        "attendance/<int:session_id>/mark/",
        views.attendance_mark,
        name="attendance_mark",
    ),
    path(
        "attendance/<int:session_id>/detail/",
        views.attendance_detail,
        name="attendance_detail",
    ),
    path("my-courses/", views.my_courses, name="my_courses"),
    # Admin & APIs
    path("admin/", admin.site.urls),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("silk/", include("silk.urls", namespace="silk")),
    path("api/all-course/", views.allCourse),
    path("api/user-courses/", views.userCourses),
    path("api/course-stat/", views.courseStat),
    path("api/course-member-stat/", views.courseMemberStat),
    path("stats/", views.userStat),
    path("export/grades/", views.export_grades_csv, name="export_grades_csv"),
    path(
        "export/attendance/", views.export_attendance_csv, name="export_attendance_csv"
    ),
]
