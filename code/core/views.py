from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db.models import Max, Min, Avg, Count
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core import serializers
from .models import (
    Course,
    CourseMember,
    Assignment,
    AssignmentSubmission,
    Quiz,
    QuizOption,
    QuizAttempt,
    ForumThread,
    ForumReply,
    AttendanceSession,
    AttendanceRecord,
)
from django.utils import timezone
import json
import csv


# === API ENDPOINTS (DASHBOARD) ===
def courseStat(request):
    courses = Course.objects.all()
    stats = courses.aggregate(
        max_price=Max("price"), min_price=Min("price"), avg_price=Avg("price")
    )
    cheapest = courses.filter(price=stats["min_price"]).first()
    expensive = courses.filter(price=stats["max_price"]).first()
    response = {
        "course_count": courses.count(),
        "courses": stats,
        "cheapest": (
            json.loads(serializers.serialize("json", [cheapest]))[0]
            if cheapest
            else None
        ),
        "expensive": (
            json.loads(serializers.serialize("json", [expensive]))[0]
            if expensive
            else None
        ),
    }
    return JsonResponse(response)


def userStat(request):
    users = User.objects.all()
    total_users = users.count()
    users_with_courses = users.annotate(num_courses=Count("enrolled_courses")).filter(
        num_courses__gt=0
    )
    top_user_obj = (
        users.annotate(num_courses_taught=Count("courses_taught"))
        .order_by("-num_courses_taught")
        .first()
    )
    response = {
        "total_non_admin_users": total_users,
        "total_users_with_courses": users_with_courses.count(),
        "average_courses_per_user": (
            Course.objects.count() / total_users if total_users > 0 else 0
        ),
        "top_user": (
            {
                "username": top_user_obj.username,
                "email": top_user_obj.email,
                "total_courses": top_user_obj.num_courses_taught,
            }
            if top_user_obj
            else None
        ),
    }
    return JsonResponse(response)


def allCourse(request):
    courses = Course.objects.select_related("teacher").all()
    data = [
        {
            "id": course.id,
            "name": course.name,
            "description": course.description,
            "price": course.price,
            "teacher": course.teacher.username,
            "level": course.get_level_display(),
            "status": course.get_status_display(),
            "created_at": course.created_at.isoformat(),
        }
        for course in courses
    ]
    return JsonResponse({"courses": data})


def userCourses(request):
    user_id = request.GET.get("user_id")
    members = CourseMember.objects.select_related("course", "user").all()
    if user_id:
        members = members.filter(user_id=user_id)
    data = [
        {
            "course": member.course.name,
            "user": member.user.username,
            "role": member.get_roles_display(),
            "joined_at": member.created_at.isoformat(),
        }
        for member in members
    ]
    return JsonResponse({"user_courses": data})


def courseMemberStat(request):
    stats = (
        CourseMember.objects.values("course__name")
        .annotate(member_count=Count("id"))
        .order_by("-member_count")
    )
    return JsonResponse({"course_member_stats": list(stats)})


# === HTML VIEWS ===
def admin_dashboard(request):
    return render(request, "core/index.html")


def home(request):
    courses = Course.objects.filter(status="published").order_by("-created_at")
    return render(request, "core/home.html", {"courses": courses})


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk, status="published")
    is_enrolled = False
    is_teacher_or_admin = False

    if request.user.is_authenticated:
        is_enrolled = CourseMember.objects.filter(
            course=course, user=request.user
        ).exists()
        if request.user == course.teacher or request.user.is_staff:
            is_teacher_or_admin = True

    return render(
        request,
        "core/detail.html",
        {
            "course": course,
            "is_enrolled": is_enrolled,
            "is_teacher_or_admin": is_teacher_or_admin,
        },
    )


@login_required
def enroll_course(request, pk):
    course = get_object_or_404(Course, pk=pk, status="published")

    # Blokir pengajar atau admin agar tidak bisa mendaftar (karena sudah punya akses penuh)
    if request.user == course.teacher or request.user.is_staff:
        messages.info(
            request,
            "Sebagai pengajar atau admin, Anda memiliki akses otomatis dan tidak perlu mendaftar.",
        )
        return redirect("course_detail", pk=pk)

    CourseMember.objects.get_or_create(
        course=course, user=request.user, defaults={"roles": "std"}
    )
    messages.success(request, f"Berhasil mendaftar ke kursus: {course.name}")
    return redirect("my_courses")


@login_required
def my_courses(request):
    memberships = CourseMember.objects.filter(user=request.user).select_related(
        "course"
    )
    return render(request, "core/my_courses.html", {"memberships": memberships})


@login_required
def learn_course(request, pk):
    course = get_object_or_404(Course, pk=pk)

    # Pengecekan akses: Tolak jika bukan member, bukan pengajar kursus tsb, dan bukan admin/staff
    if (
        not CourseMember.objects.filter(course=course, user=request.user).exists()
        and course.teacher != request.user
        and not request.user.is_staff
    ):
        messages.error(request, "Anda belum terdaftar di kursus ini.")
        return redirect("course_detail", pk=pk)

    contents = course.contents.all().order_by("order", "created_at")
    assignments = course.assignments.all().order_by("deadline")
    quizzes = course.quizzes.all().order_by("deadline")

    return render(
        request,
        "core/learn.html",
        {
            "course": course,
            "contents": contents,
            "assignments": assignments,
            "quizzes": quizzes,
        },
    )


def login_user(request):
    if request.method == "POST":
        u = request.POST.get("username")
        p = request.POST.get("password")
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Username atau password salah.")
    return render(request, "core/login.html")


def register_user(request):
    if request.method == "POST":
        u = request.POST.get("username")
        e = request.POST.get("email")
        p = request.POST.get("password")
        if User.objects.filter(username=u).exists():
            messages.error(request, "Username sudah dipakai.")
        else:
            user = User.objects.create_user(username=u, email=e, password=p)
            mahasiswa_group, _ = Group.objects.get_or_create(name="Mahasiswa")
            user.groups.add(mahasiswa_group)
            login(request, user)
            return redirect("home")
    return render(request, "core/register.html")


def logout_user(request):
    logout(request)
    return redirect("home")


@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)

    # Check if user is enrolled or teacher
    is_teacher_or_admin = (
        request.user == assignment.course.teacher or request.user.is_staff
    )
    is_enrolled = CourseMember.objects.filter(
        course=assignment.course, user=request.user
    ).exists()

    if not is_teacher_or_admin and not is_enrolled:
        messages.error(request, "Anda tidak memiliki akses ke tugas ini.")
        return redirect("course_detail", pk=assignment.course.pk)

    submission = AssignmentSubmission.objects.filter(
        assignment=assignment, student=request.user
    ).first()

    if request.method == "POST" and not is_teacher_or_admin:
        if not submission:
            if "file" in request.FILES:
                submission = AssignmentSubmission(
                    assignment=assignment,
                    student=request.user,
                    file=request.FILES["file"],
                )
                submission.save()
                messages.success(request, "Tugas berhasil dikumpulkan.")
                return redirect("assignment_detail", pk=pk)
            else:
                messages.error(request, "Harap unggah file tugas.")
        else:
            messages.error(request, "Anda sudah mengumpulkan tugas ini.")

    return render(
        request,
        "core/assignment_detail.html",
        {
            "assignment": assignment,
            "submission": submission,
            "course": assignment.course,
            "is_teacher": is_teacher_or_admin,
        },
    )


@login_required
def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)

    is_teacher_or_admin = request.user == quiz.course.teacher or request.user.is_staff
    is_enrolled = CourseMember.objects.filter(
        course=quiz.course, user=request.user
    ).exists()

    if not is_teacher_or_admin and not is_enrolled:
        messages.error(request, "Anda tidak memiliki akses ke kuis ini.")
        return redirect("course_detail", pk=quiz.course.pk)

    attempt = QuizAttempt.objects.filter(quiz=quiz, student=request.user).first()
    questions = quiz.questions.all().prefetch_related("options")

    if request.method == "POST" and not is_teacher_or_admin:
        if not attempt:
            score = 0
            for question in questions:
                selected_option_id = request.POST.get(f"question_{question.id}")
                if selected_option_id:
                    option = QuizOption.objects.filter(id=selected_option_id).first()
                    if option and option.is_correct:
                        score += question.points

            attempt = QuizAttempt.objects.create(
                quiz=quiz, student=request.user, score=score
            )
            messages.success(request, f"Kuis selesai. Nilai Anda: {score}")
            return redirect("quiz_detail", pk=pk)
        else:
            messages.error(request, "Anda sudah mencoba kuis ini.")

    return render(
        request,
        "core/quiz_detail.html",
        {
            "quiz": quiz,
            "attempt": attempt,
            "questions": questions,
            "course": quiz.course,
            "is_teacher": is_teacher_or_admin,
        },
    )


@login_required
def forum_list(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    is_teacher_or_admin = request.user == course.teacher or request.user.is_staff
    is_enrolled = CourseMember.objects.filter(course=course, user=request.user).exists()

    if not is_teacher_or_admin and not is_enrolled:
        messages.error(request, "Anda tidak memiliki akses ke forum ini.")
        return redirect("course_detail", pk=course.pk)

    threads = course.forum_threads.all()

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        if title and content:
            ForumThread.objects.create(
                course=course, author=request.user, title=title, content=content
            )
            messages.success(request, "Diskusi baru berhasil dibuat.")
            return redirect("forum_list", course_id=course.id)

    return render(
        request, "core/forum_list.html", {"course": course, "threads": threads}
    )


@login_required
def forum_detail(request, pk):
    thread = get_object_or_404(ForumThread, pk=pk)
    course = thread.course
    is_teacher_or_admin = request.user == course.teacher or request.user.is_staff
    is_enrolled = CourseMember.objects.filter(course=course, user=request.user).exists()

    if not is_teacher_or_admin and not is_enrolled:
        messages.error(request, "Anda tidak memiliki akses ke diskusi ini.")
        return redirect("course_detail", pk=course.pk)

    replies = thread.replies.all()

    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            ForumReply.objects.create(
                thread=thread, author=request.user, content=content
            )
            messages.success(request, "Balasan berhasil ditambahkan.")
            return redirect("forum_detail", pk=thread.id)

    return render(
        request,
        "core/forum_detail.html",
        {"thread": thread, "course": course, "replies": replies},
    )


@login_required
def attendance_list(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    is_teacher_or_admin = request.user == course.teacher or request.user.is_staff
    is_enrolled = CourseMember.objects.filter(course=course, user=request.user).exists()

    if not is_teacher_or_admin and not is_enrolled:
        messages.error(request, "Anda tidak memiliki akses ke presensi kursus ini.")
        return redirect("course_detail", pk=course.pk)

    sessions = course.attendance_sessions.all()
    records = []

    if not is_teacher_or_admin:
        user_records = AttendanceRecord.objects.filter(
            student=request.user, session__course=course
        )
        records_dict = {r.session_id: r for r in user_records}

        # We need local time to compare correctly. Using timezone.localtime()
        now_date = timezone.localtime().date()
        now_time = timezone.localtime().time()

        for session in sessions:
            record = records_dict.get(session.id)
            is_active = (
                session.date == now_date
                and session.start_time <= now_time <= session.end_time
            )
            records.append(
                {"session": session, "record": record, "is_active": is_active}
            )

    return render(
        request,
        "core/attendance_list.html",
        {
            "course": course,
            "sessions": sessions,
            "records": records,
            "is_teacher": is_teacher_or_admin,
        },
    )


@login_required
def attendance_mark(request, session_id):
    session = get_object_or_404(AttendanceSession, pk=session_id)
    course = session.course

    if not CourseMember.objects.filter(course=course, user=request.user).exists():
        messages.error(request, "Anda bukan mahasiswa di kursus ini.")
        return redirect("attendance_list", course_id=course.id)

    now_date = timezone.localtime().date()
    now_time = timezone.localtime().time()

    if (
        session.date != now_date
        or now_time < session.start_time
        or now_time > session.end_time
    ):
        messages.error(request, "Sesi presensi ini tidak sedang aktif.")
        return redirect("attendance_list", course_id=course.id)

    record, created = AttendanceRecord.objects.get_or_create(
        session=session, student=request.user, defaults={"status": "present"}
    )
    if created:
        messages.success(request, f"Berhasil presensi untuk {session.title}.")
    else:
        messages.info(request, "Anda sudah melakukan presensi sebelumnya.")

    return redirect("attendance_list", course_id=course.id)


@login_required
def attendance_detail(request, session_id):
    session = get_object_or_404(AttendanceSession, pk=session_id)
    course = session.course

    if request.user != course.teacher and not request.user.is_staff:
        messages.error(request, "Hanya pengajar yang dapat melihat detail presensi.")
        return redirect("attendance_list", course_id=course.id)

    records = session.records.all().select_related("student")
    students = CourseMember.objects.filter(course=course, roles="std")

    attendance_data = []
    record_dict = {r.student_id: r for r in records}

    for member in students:
        record = record_dict.get(member.user_id)
        attendance_data.append(
            {
                "student": member.user,
                "status": record.get_status_display() if record else "Alpa",
                "time": record.timestamp if record else None,
            }
        )

    return render(
        request,
        "core/attendance_detail.html",
        {"session": session, "course": course, "attendance_data": attendance_data},
    )


@login_required
def export_grades_csv(request):
    if not request.user.is_staff:
        messages.error(request, "Akses ditolak.")
        return redirect("home")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="laporan_nilai.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ["Mahasiswa", "Kursus", "Tipe", "Judul", "Nilai", "Waktu Pengumpulan"]
    )

    submissions = AssignmentSubmission.objects.select_related(
        "student", "assignment__course"
    ).all()
    for sub in submissions:
        grade = sub.grade if sub.grade is not None else "Belum Dinilai"
        writer.writerow(
            [
                sub.student.username,
                sub.assignment.course.name,
                "Tugas",
                sub.assignment.title,
                grade,
                sub.submitted_at.strftime("%Y-%m-%d %H:%M"),
            ]
        )

    attempts = QuizAttempt.objects.select_related("student", "quiz__course").all()
    for att in attempts:
        writer.writerow(
            [
                att.student.username,
                att.quiz.course.name,
                "Kuis",
                att.quiz.title,
                att.score,
                att.attempted_at.strftime("%Y-%m-%d %H:%M"),
            ]
        )

    return response


@login_required
def export_attendance_csv(request):
    if not request.user.is_staff:
        messages.error(request, "Akses ditolak.")
        return redirect("home")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="laporan_kehadiran.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ["Mahasiswa", "Kursus", "Sesi", "Tanggal", "Status", "Waktu Presensi"]
    )

    records = AttendanceRecord.objects.select_related(
        "student", "session__course"
    ).all()
    for rec in records:
        writer.writerow(
            [
                rec.student.username,
                rec.session.course.name,
                rec.session.title,
                rec.session.date.strftime("%Y-%m-%d"),
                rec.get_status_display(),
                rec.timestamp.strftime("%H:%M:%S") if rec.timestamp else "",
            ]
        )

    return response
