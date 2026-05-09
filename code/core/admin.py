from django.contrib import admin
from .models import (
    Course, CourseMember, CourseContent, Comment, CourseProgress,
    Assignment, AssignmentSubmission, Quiz, QuizQuestion, QuizOption, QuizAttempt,
    ForumThread, ForumReply, AttendanceSession, AttendanceRecord
)

# Kustomisasi Tampilan Utama Header & Title Admin
admin.site.site_header = "LMS Pro Administration"
admin.site.site_title = "LMS Pro Admin Portal"
admin.site.index_title = "Welcome to LMS Pro Management"

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'price_formatted', 'level', 'status', 'created_at')
    list_filter = ('status', 'level', 'created_at')
    search_fields = ('name', 'description', 'teacher__username')
    list_editable = ('status', 'level') # Memungkinkan edit langsung dari tabel
    ordering = ('-created_at',)
    raw_id_fields = ('teacher',)
    
    def price_formatted(self, obj):
        return f"Rp {obj.price:,}"
    price_formatted.short_description = "Harga"

@admin.register(CourseMember)
class CourseMemberAdmin(admin.ModelAdmin):
    list_display = ('course', 'user', 'roles', 'created_at')
    list_filter = ('roles', 'course')
    search_fields = ('user__username', 'user__email', 'course__name')
    raw_id_fields = ('user', 'course')
    ordering = ('-created_at',)

@admin.register(CourseContent)
class CourseContentAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'parent', 'order', 'created_at')
    list_filter = ('course',)
    search_fields = ('name', 'description', 'course__name')
    list_editable = ('order',)
    raw_id_fields = ('course', 'parent')
    ordering = ('course', 'order')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'user', 'short_comment', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('comment', 'user__username', 'content__name')
    raw_id_fields = ('content', 'user')
    ordering = ('-created_at',)

    def short_comment(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    short_comment.short_description = "Komentar"

@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'is_completed', 'last_accessed')
    list_filter = ('is_completed',)
    search_fields = ('user__username', 'content__name')
    raw_id_fields = ('user', 'content')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'deadline', 'created_at')
    list_filter = ('course', 'deadline')
    search_fields = ('title', 'course__name')

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submitted_at', 'grade', 'is_late')
    list_filter = ('assignment', 'student')

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'deadline', 'created_at')

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'points')

@admin.register(QuizOption)
class QuizOptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score', 'attempted_at')

@admin.register(ForumThread)
class ForumThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'author', 'created_at')

@admin.register(ForumReply)
class ForumReplyAdmin(admin.ModelAdmin):
    list_display = ('thread', 'author', 'created_at')

@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'date', 'start_time', 'end_time')

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('session', 'student', 'status', 'timestamp')
    list_filter = ('session', 'status')