from django.http import HttpResponse
from django.urls import path

def placeholder(request):
    return HttpResponse("Halaman absensi (segerea dibuat)")

urlpatterns = [
    path('', placeholder, name='attendance_list'),
]
