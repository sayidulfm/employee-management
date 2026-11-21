from django import forms
from django.contrib.auth.forms import get_user_model
from django.db import transaction

from .models import Employee

User = get_user_model()

class EmployeeForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(
        widget=forms.PasswordInput, 
        required=False,
        help_text='wajib saat tambah. Kosongkan saat edit jika tidak diubah.' \
        ''
    )

    class Meta:
        model = Employee
        fields = ['nama', 'email', 'jabatan', 'tanggal_masuk', 'status_aktif']
        widgets = {'tanggal_masuk': forms.DateInput(attrs={'type': 'date'}),}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['username'].initial = self.instance.user.username
            self.fields['password'].required = False
       
    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.pk:
            if not cleaned_data.get('password'):
                self.add_error('password', 'Password wajib diisi untuk karyawan baru.')
            username = cleaned_data.get('username')
            if username and User.objects.filter(username=username).exists():
                self.add_error('username', 'Username sudah dipakai.')
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        employee = super().save(commit=False)
        if not employee.pk:
           employee.user = User.objects.create_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password'],
                email=employee.email,
           )
        elif self.cleaned_data['password']:
            employee.user.set_password(self.cleaned_data['password'])
            employee.user.save()
        employee.save()
        return employee
    