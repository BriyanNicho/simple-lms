import random
from django.contrib.auth.models import User
from core.models import Course, CourseMember, CourseContent

print("Membuat data dummy...")

# 1. Buat beberapa User/Siswa/Pengajar
users_data = ['Andi', 'Budi', 'Citra', 'Dewi', 'Eka']
users = []
for name in users_data:
    user, created = User.objects.get_or_create(username=name.lower())
    if created:
        user.set_password('password123')
        user.save()
    users.append(user)

# 2. Buat beberapa Course
courses_data = [
    {
        'name': 'Fullstack Web Development with Django',
        'description': 'Belajar membangun aplikasi web utuh dengan Django dan Vanilla JS. Sangat cocok untuk pemula hingga menengah.',
        'price': 450000,
        'level': 'intermediate',
        'status': 'published'
    },
    {
        'name': 'Mastering React & Next.js',
        'description': 'Eksplorasi mendalam tentang React dan Next.js untuk Frontend modern.',
        'price': 550000,
        'level': 'advanced',
        'status': 'published'
    },
    {
        'name': 'Python for Data Science',
        'description': 'Menganalisa data menggunakan Pandas, Numpy, dan Scikit-Learn.',
        'price': 350000,
        'level': 'beginner',
        'status': 'published'
    },
    {
        'name': 'UI/UX Design Principles',
        'description': 'Pelajari cara membuat antarmuka yang user-friendly dan memukau menggunakan Figma.',
        'price': 250000,
        'level': 'beginner',
        'status': 'published'
    },
    {
        'name': 'DevOps Engineering for Beginners',
        'description': 'Pengenalan Docker, CI/CD, dan Kubernetes.',
        'price': 600000,
        'level': 'intermediate',
        'status': 'published'
    }
]

courses = []
pengajar = User.objects.get(username='briyan') # Menggunakan superuser yang baru dibuat

for item in courses_data:
    course, created = Course.objects.get_or_create(
        name=item['name'],
        defaults={
            'description': item['description'],
            'price': item['price'],
            'level': item['level'],
            'status': item['status'],
            'teacher': pengajar
        }
    )
    courses.append(course)

# 3. Buat Member/Enrollment untuk tiap Course secara random
for course in courses:
    num_members = random.randint(2, 5)
    selected_users = random.sample(users, num_members)
    for u in selected_users:
        CourseMember.objects.get_or_create(
            course=course,
            user=u,
            defaults={'roles': 'std'}
        )

print("Data dummy berhasil dibuat! Silakan cek dashboard LMS Anda.")
