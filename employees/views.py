from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreatView, CreateView, DeleteView, ListView, UpdateView

from .forms import EmployeeForm
from .mixins import AdminRequiredMixin
from .models import Employee


@login_required
def home(request):
    '''Admin ke daftar karyawan, user ke halaman absensi.'''
    if request.user.is_staff:
        return redirect('employees:employee_list')
    return redirect('attendance:attendance_list')

class EmployeeListView(AdminRequiredMixin, ListView):
    model = Employee
    template_name = 'employees/list.html'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(nama__icontains=q) |
                Q(email__icontains=q) |
                Q(jabatan__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '') 
        return context

class EmployeeCreateView(AdminRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/form.html'
    success_url = reverse_lazy('employees:employee_list')

class EmployeeUpdateView(AdminRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/form.html'
    success_url = reverse_lazy('employees:employee_list')

class EmployeeDeleteView(AdminRequiredMixin, DeleteView):
    model = Employee
    template_name = 'employees/confirm_delete.html'
    success_url = reverse_lazy('employees:employee_list')

    def form_valid(self, form):
        # Hapus juga akun login-nya supaya tidak jadi data yatim
        user = self.object.user
        response = super().form_valid(form)
        user.delete()
        return response
    