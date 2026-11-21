from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from employees.exports import export_csv, export_excel, fmt_time
from employees.mixins import AdminRequiredMixin

from .models import Attendance


def _parse_date(value):
    """Kembalikan date, atau None jika kosong/format salah."""
    try:
        return parse_date(value) if value else None
    except ValueError:
        return None


def filter_attendance(request):
    """Satu sumber aturan filter, dipakai oleh halaman list DAN export."""
    qs = Attendance.objects.select_related("employee")

    if not request.user.is_staff:
        qs = qs.filter(employee__user=request.user)

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(employee__nama__icontains=q)

    date_from = _parse_date(request.GET.get("date_from"))
    date_to = _parse_date(request.GET.get("date_to"))
    if date_from:
        qs = qs.filter(tanggal__gte=date_from)
    if date_to:
        qs = qs.filter(tanggal__lte=date_to)
    return qs


class AttendanceListView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = "attendance/list.html"
    paginate_by = 10

    def get_queryset(self):
        return filter_attendance(self.request)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        get = self.request.GET
        ctx["q"] = get.get("q", "")
        ctx["date_from"] = get.get("date_from", "")
        ctx["date_to"] = get.get("date_to", "")

        employee = getattr(self.request.user, "employee", None)
        ctx["employee"] = employee
        if employee:
            ctx["today"] = Attendance.objects.filter(
                employee=employee, tanggal=timezone.localdate()
            ).first()
        return ctx


@login_required
@require_POST
def check_in(request):
    employee = getattr(request.user, "employee", None)
    if employee is None:
        messages.error(request, "Akun ini tidak terhubung ke data karyawan.")
        return redirect("attendance-list")
    if not employee.status_aktif:
        messages.error(request, "Karyawan nonaktif tidak dapat check-in.")
        return redirect("attendance-list")

    now = timezone.localtime()
    _, created = Attendance.objects.get_or_create(
        employee=employee,
        tanggal=now.date(),
        defaults={"jam_masuk": now.time()},
    )
    if created:
        messages.success(request, "Check-in berhasil.")
    else:
        messages.warning(request, "Anda sudah check-in hari ini.")
    return redirect("attendance-list")


@login_required
@require_POST
def check_out(request):
    employee = getattr(request.user, "employee", None)
    if employee is None:
        messages.error(request, "Akun ini tidak terhubung ke data karyawan.")
        return redirect("attendance-list")

    now = timezone.localtime()
    attendance = Attendance.objects.filter(
        employee=employee, tanggal=now.date()
    ).first()

    if attendance is None:
        messages.error(request, "Anda belum check-in hari ini.")
    elif attendance.jam_keluar:
        messages.warning(request, "Anda sudah check-out hari ini.")
    else:
        attendance.jam_keluar = now.time()
        attendance.save(update_fields=["jam_keluar"])
        messages.success(request, "Check-out berhasil.")
    return redirect("attendance-list")


class AttendanceExportView(AdminRequiredMixin, View):
    """Export absensi (admin only), mengikuti filter yang sedang aktif."""

    def get(self, request):
        headers = ["Nama", "Tanggal", "Jam Masuk", "Jam Keluar"]
        rows = [
            [a.employee.nama, a.tanggal.isoformat(), fmt_time(a.jam_masuk), fmt_time(a.jam_keluar)]
            for a in filter_attendance(request)
        ]
        if request.GET.get("format") == "xlsx":
            return export_excel("absensi", headers, rows)
        return export_csv("absensi", headers, rows)