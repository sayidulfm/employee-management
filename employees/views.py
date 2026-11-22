from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.aggregates import Count
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, TemplateView

from attendance.models import Attendance

from .exports import export_csv, export_excel
from .forms import EmployeeForm
from .mixins import AdminRequiredMixin
from .models import Employee


@login_required
def home(request):
    """Admin ke daftar karyawan, karyawan biasa ke halaman absensi."""
    if request.user.is_staff:
        return redirect("employee-list")
    return redirect("attendance-list")


def search_employees(request):
    qs = Employee.objects.all()
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(nama__icontains=q) | Q(email__icontains=q) | Q(jabatan__icontains=q)
        )
    return qs


class EmployeeListView(AdminRequiredMixin, ListView):
    model = Employee
    template_name = "employees/list.html"
    paginate_by = 10

    def get_queryset(self):
        return search_employees(self.request)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


class EmployeeCreateView(AdminRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "employees/form.html"
    success_url = reverse_lazy("employee-list")


class EmployeeUpdateView(AdminRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "employees/form.html"
    success_url = reverse_lazy("employee-list")


class EmployeeDeleteView(AdminRequiredMixin, DeleteView):
    model = Employee
    template_name = "employees/confirm_delete.html"
    success_url = reverse_lazy("employee-list")

    def form_valid(self, form):
        # hapus juga akun login-nya supaya tidak jadi data yatim
        user = self.object.user
        response = super().form_valid(form)
        user.delete()
        return response


class EmployeeExportView(AdminRequiredMixin, View):
    def get(self, request):
        headers = ["Nama", "Email", "Jabatan", "Tanggal Masuk", "Status"]
        rows = [
            [
                e.nama,
                e.email,
                e.jabatan,
                e.tanggal_masuk.isoformat(),
                "Aktif" if e.status_aktif else "Nonaktif",
            ]
            for e in search_employees(request)
        ]
        if request.GET.get("format") == "xlsx":
            return export_excel("karyawan", headers, rows)
        return export_csv("karyawan", headers, rows)

class DashboardView(AdminRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super() .get_context_data(**kwargs)

        per_jabatan = (
            Employee.objects.values("jabatan")
            .annotate(total=Count("id"))
            .order_by("-total")
        )    
        ctx["jabatan_labels"] = [r["jabatan"] for r in per_jabatan]
        ctx["jabatan_data"] = [r["total"] for r in per_jabatan]

        today = timezone.localdate()
        days = [today - timedelta(days=i) for i in range(6, -1, -1)]
        hadir = dict(
            Attendance.objects.filter(tanggal__gte=days[0])
            .values_list("tanggal")
            .annotate(total=Count("id"))
        )
        ctx["hari_labels"] = [d.strftime("%d %b") for d in days]
        ctx["hari_data"] = [hadir.get(d, 0) for d in days]

        ctx["total_karyawan"] = Employee.objects.count()
        ctx["total_aktif"] = Employee.objects.filter(status_aktif=True).count()
        return ctx