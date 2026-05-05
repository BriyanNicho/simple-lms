from django.http import JsonResponse
from django.db.models import Max, Min, Avg, Count
from django.contrib.auth.models import User
from .models import Course, CourseMember
from django.core import serializers
import json

# a. Course Statistik
def courseStat(request):
    courses = Course.objects.all()
    stats = courses.aggregate(
        max_price=Max('price'),
        min_price=Min('price'),
        avg_price=Avg('price')
    )
    
    # Mencari objek kursus termurah dan termahal
    cheapest = courses.filter(price=stats['min_price']).first()
    expensive = courses.filter(price=stats['max_price']).first()
    
    response = {
        "course_count": courses.count(),
        "courses": stats,
        "cheapest": json.loads(serializers.serialize('json', [cheapest]))[0] if cheapest else None,
        "expensive": json.loads(serializers.serialize('json', [expensive]))[0] if expensive else None,
    }
    return JsonResponse(response)

# b. User Statistik
def userStat(request):
    users = User.objects.all()
    total_users = users.count()
    
    # Menghitung user yang memiliki kursus dan yang tidak
    users_with_courses = users.annotate(num_courses=Count('course')).filter(num_courses__gt=0)
    
    # Top User (pengajar dengan kursus terbanyak)
    top_user_obj = users.annotate(num_courses=Count('course')).order_by('-num_courses').first()
    
    response = {
        "total_non_admin_users": total_users,
        "total_users_with_courses": users_with_courses.count(),
        "average_courses_per_user": Course.objects.count() / total_users if total_users > 0 else 0,
        "top_user": {
            "username": top_user_obj.username,
            "email": top_user_obj.email,
            "total_courses": top_user_obj.num_courses
        } if top_user_obj else None
    }
    return JsonResponse(response)


def allCourse(request):
    courses = Course.objects.all()
    data = json.loads(serializers.serialize('json', courses))
    return JsonResponse({"courses": data})


def userCourses(request):
    user_id = request.GET.get('user_id')
    members = CourseMember.objects.all()
    if user_id:
        members = members.filter(user_id__id=user_id)

    data = [
        {
            "course": member.course_id.name,
            "user": member.user_id.username,
            "role": member.roles,
            "joined_at": member.created_at.isoformat(),
        }
        for member in members
    ]
    return JsonResponse({"user_courses": data})


def courseMemberStat(request):
    stats = CourseMember.objects.values('course_id__name').annotate(member_count=Count('id')).order_by('-member_count')
    return JsonResponse({"course_member_stats": list(stats)})