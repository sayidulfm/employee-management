import random
from datetime import time, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from attendance.models import Attendance
from employees.models import Employee

User = get_user_model()

NAMA = [
    "Budi Santoso", "Siti Aminah", "Agus Pratama", "Dewi Lestari", "Rudi Hartono",
    "Rina Wulandari", "Eko Prasetyo", "Maya Sari", "Fajar Nugroho", "Indah Permata",
    "Hendra Wijaya", "Lina Marlina", "Tono Saputra", "Yuni Astuti", "Dimas Kurniawan",
]
JABATAN = ["Developer", "Designer", "HR", "Finance", "Marketing", "QA"]

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin12345"
EMPLOYEE_PASSWORD = "karyawan123"


class Command(BaseCommand):
    help = "Isi database dengan data demo (aman dijalankan berulang)."

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(42)

        admin, created = User.objects.get_or_create(
            username=ADMIN_USERNAME, defaults={"is_staff": True, "is_superuser": True}
        )
        if created:
            admin.set_password(ADMIN_PASSWORD)
            admin.save()

        today = timezone.localdate()
        for i, nama in enumerate(NAMA):
            username = nama.split()[0].lower()
            email = f"{username}@example.com"
            user, user_created = User.objects.get_or_create(username=username)
            if user_created:
                user.set_password(EMPLOYEE_PASSWORD)
                user.save()

            employee, _ = Employee.objects.get_or_create(
                user=user,
                defaults={
                    "nama": nama,
                    "email": email,
                    "jabatan": JABATAN[i % len(JABATAN)],
                    "tanggal_masuk": today - timedelta(days=random.randint(60, 900)),
                    "status_aktif": True,
                },
            )

            for d in range(14):
                tanggal = today - timedelta(days=d)
                if tanggal.weekday() >= 5 or random.random() < 0.1:
                    continue
                Attendance.objects.get_or_create(
                    employee=employee,
                    tanggal=tanggal,
                    defaults={
                        "jam_masuk": time(random.randint(7, 9), random.randint(0, 59)),
                        "jam_keluar": time(random.randint(16, 18), random.randint(0, 59)),
                    },
                )

        self.stdout.write(self.style.SUCCESS("Data demo siap."))
        self.stdout.write(f"Admin: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
        self.stdout.write(f"Karyawan (mis. budi): password {EMPLOYEE_PASSWORD}")