from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    LEVEL_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
    ]

    name = models.CharField("nama matkul", max_length=100)
    description = models.TextField("deskripsi", default="-")
    price = models.IntegerField("harga", default=10000)
    image = models.ImageField(
        "gambar", upload_to="courses/images/", null=True, blank=True
    )
    teacher = models.ForeignKey(
        User,
        related_name="courses_taught",
        verbose_name="pengajar",
        on_delete=models.RESTRICT,
    )
    level = models.CharField(
        "tingkat", max_length=20, choices=LEVEL_CHOICES, default="beginner"
    )
    status = models.CharField(
        "status", max_length=20, choices=STATUS_CHOICES, default="draft"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mata Kuliah"
        verbose_name_plural = "Mata Kuliah"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name + " (Rp " + str(self.price) + ")"


class CourseMember(models.Model):
    ROLE_OPTIONS = [("std", "Siswa"), ("ast", "Asisten")]

    course = models.ForeignKey(
        Course, related_name="members", verbose_name="matkul", on_delete=models.RESTRICT
    )
    user = models.ForeignKey(
        User,
        related_name="enrolled_courses",
        verbose_name="siswa",
        on_delete=models.RESTRICT,
    )
    roles = models.CharField("peran", max_length=3, choices=ROLE_OPTIONS, default="std")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Subscriber Matkul"
        verbose_name_plural = "Subscriber Matkul"
        unique_together = ("course", "user")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.course.name} - {self.user.username}"


class CourseContent(models.Model):
    name = models.CharField("judul konten", max_length=200)
    description = models.TextField("deskripsi", default="-")
    video_url = models.URLField("URL Video", max_length=500, null=True, blank=True)
    file_attachment = models.FileField(
        "File", upload_to="courses/attachments/", null=True, blank=True
    )
    course = models.ForeignKey(
        Course, related_name="contents", verbose_name="matkul", on_delete=models.CASCADE
    )
    parent = models.ForeignKey(
        "self",
        related_name="children",
        verbose_name="induk",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    order = models.IntegerField("urutan", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Konten Matkul"
        verbose_name_plural = "Konten Matkul"
        ordering = ["order", "created_at"]

    def __str__(self) -> str:
        return f"[{self.course.name}] {self.name}"


class Comment(models.Model):
    content = models.ForeignKey(
        CourseContent,
        related_name="comments",
        verbose_name="konten",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User, related_name="comments", verbose_name="pengguna", on_delete=models.CASCADE
    )
    comment = models.TextField("komentar")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Komentar"
        verbose_name_plural = "Komentar"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Komen {self.content.name} oleh {self.user.username}"


class CourseProgress(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="progress_records"
    )
    content = models.ForeignKey(
        CourseContent, on_delete=models.CASCADE, related_name="progress_records"
    )
    is_completed = models.BooleanField("Selesai", default=False)
    last_accessed = models.DateTimeField("Terakhir Diakses", auto_now=True)

    class Meta:
        verbose_name = "Progres Belajar"
        verbose_name_plural = "Progres Belajar"
        unique_together = ("user", "content")

    def __str__(self) -> str:
        return f"{self.user.username} - {self.content.name} ({'Selesai' if self.is_completed else 'Belum'})"


# === ASSIGNMENT & QUIZ ===


class Assignment(models.Model):
    course = models.ForeignKey(
        Course,
        related_name="assignments",
        verbose_name="matkul",
        on_delete=models.CASCADE,
    )
    title = models.CharField("judul tugas", max_length=200)
    description = models.TextField("deskripsi")
    attachment = models.FileField(
        "lampiran", upload_to="assignments/attachments/", null=True, blank=True
    )
    deadline = models.DateTimeField("batas waktu")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tugas"
        verbose_name_plural = "Tugas"
        ordering = ["-deadline"]

    def __str__(self):
        return f"[{self.course.name}] {self.title}"


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        related_name="submissions",
        verbose_name="tugas",
        on_delete=models.CASCADE,
    )
    student = models.ForeignKey(
        User,
        related_name="assignment_submissions",
        verbose_name="mahasiswa",
        on_delete=models.CASCADE,
    )
    file = models.FileField("file jawaban", upload_to="assignments/submissions/")
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.IntegerField("nilai", null=True, blank=True)
    feedback = models.TextField("feedback pengajar", null=True, blank=True)

    class Meta:
        verbose_name = "Pengumpulan Tugas"
        verbose_name_plural = "Pengumpulan Tugas"
        unique_together = ("assignment", "student")
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"

    @property
    def is_late(self):
        return self.submitted_at > self.assignment.deadline


class Quiz(models.Model):
    course = models.ForeignKey(
        Course, related_name="quizzes", verbose_name="matkul", on_delete=models.CASCADE
    )
    title = models.CharField("judul kuis", max_length=200)
    description = models.TextField("deskripsi", blank=True)
    deadline = models.DateTimeField("batas waktu")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kuis"
        verbose_name_plural = "Kuis"
        ordering = ["-deadline"]

    def __str__(self):
        return f"[{self.course.name}] {self.title}"


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(
        Quiz, related_name="questions", verbose_name="kuis", on_delete=models.CASCADE
    )
    text = models.TextField("pertanyaan")
    points = models.IntegerField("poin", default=10)

    class Meta:
        verbose_name = "Pertanyaan Kuis"
        verbose_name_plural = "Pertanyaan Kuis"

    def __str__(self):
        return self.text


class QuizOption(models.Model):
    question = models.ForeignKey(
        QuizQuestion,
        related_name="options",
        verbose_name="pertanyaan",
        on_delete=models.CASCADE,
    )
    text = models.CharField("pilihan jawaban", max_length=200)
    is_correct = models.BooleanField("jawaban benar", default=False)

    class Meta:
        verbose_name = "Pilihan Kuis"
        verbose_name_plural = "Pilihan Kuis"

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(
        Quiz, related_name="attempts", verbose_name="kuis", on_delete=models.CASCADE
    )
    student = models.ForeignKey(
        User,
        related_name="quiz_attempts",
        verbose_name="mahasiswa",
        on_delete=models.CASCADE,
    )
    score = models.IntegerField("nilai", default=0)
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Percobaan Kuis"
        verbose_name_plural = "Percobaan Kuis"
        unique_together = ("quiz", "student")

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} ({self.score})"


# === FORUM DISKUSI ===


class ForumThread(models.Model):
    course = models.ForeignKey(
        Course,
        related_name="forum_threads",
        verbose_name="matkul",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name="forum_threads",
        verbose_name="penulis",
        on_delete=models.CASCADE,
    )
    title = models.CharField("judul diskusi", max_length=200)
    content = models.TextField("isi diskusi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Forum Diskusi"
        verbose_name_plural = "Forum Diskusi"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ForumReply(models.Model):
    thread = models.ForeignKey(
        ForumThread,
        related_name="replies",
        verbose_name="thread",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name="forum_replies",
        verbose_name="penulis",
        on_delete=models.CASCADE,
    )
    content = models.TextField("balasan")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Balasan Forum"
        verbose_name_plural = "Balasan Forum"
        ordering = ["created_at"]

    def __str__(self):
        return f"Balasan dari {self.author.username} di {self.thread.title}"


# === PRESENSI (ATTENDANCE) ===


class AttendanceSession(models.Model):
    course = models.ForeignKey(
        Course,
        related_name="attendance_sessions",
        verbose_name="matkul",
        on_delete=models.CASCADE,
    )
    title = models.CharField("judul pertemuan", max_length=100)
    date = models.DateField("tanggal")
    start_time = models.TimeField("waktu mulai")
    end_time = models.TimeField("waktu selesai")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sesi Presensi"
        verbose_name_plural = "Sesi Presensi"
        ordering = ["-date", "-start_time"]

    def __str__(self):
        return f"{self.course.name} - {self.title}"


class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ("present", "Hadir"),
        ("late", "Terlambat"),
        ("absent", "Alpa"),
    ]
    session = models.ForeignKey(
        AttendanceSession,
        related_name="records",
        verbose_name="sesi",
        on_delete=models.CASCADE,
    )
    student = models.ForeignKey(
        User,
        related_name="attendance_records",
        verbose_name="mahasiswa",
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        "status kehadiran", max_length=10, choices=STATUS_CHOICES, default="present"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Catatan Presensi"
        verbose_name_plural = "Catatan Presensi"
        unique_together = ("session", "student")

    def __str__(self):
        return f"{self.student.username} - {self.session.title} ({self.get_status_display()})"
