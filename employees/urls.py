from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("employees/", views.EmployeeListView.as_view(), name="employee-list"),
    path("employees/add/", views.EmployeeCreateView.as_view(), name="employee-create"),
    path("employees/export/", views.EmployeeExportView.as_view(), name="employee-export"),
    path("employees/<int:pk>/edit/", views.EmployeeUpdateView.as_view(), name="employee-update"),
    path("employees/<int:pk>/delete/", views.EmployeeDeleteView.as_view(), name="employee-delete"),
]