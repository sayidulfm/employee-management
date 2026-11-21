from django.db import models
from django.utils import timezone

from employees.models import Employee

class Attendance(models.Model):
    employee = models.ForeignKey (Employee, on_delete=models.CASCADE, related_name="attendances")

    tanggal = models.DateField(default=timezone.localdate)
    jam_masuk = models.TimeField(null=True, blank=True)
    jam_keluar = models.TimeField(null=True, blank=True)

    class Meta:
        ordering = ['-tanggal', 'employee__nama']
        constraints = [
            models.UniqueConstraint(fields=['employee', 'tanggal'], name='unique_attendance_per_day')
        ]

    def __str__(self):
        return f"{self.employee.nama} - {self.tanggal}"
    
# Create your models here.
