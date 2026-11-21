from django.urls import path

from . import views

urlpatterns = [
    path("", views.AttendanceListView.as_view(), name="attendance-list"),
    path("check-in/", views.check_in, name="attendance-check-in"),
    path("check-out/", views.check_out, name="attendance-check-out"),
    path("export/", views.AttendanceExportView.as_view(), name="attendance-export"),
]