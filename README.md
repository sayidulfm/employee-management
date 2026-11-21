# Employee Management

Aplikasi manajemen karyawan berbasis Django: autentikasi dua peran,
CRUD karyawan, absensi harian, laporan, export CSV/Excel, dan REST API.

## Fitur
- Login Admin dan Karyawan (akses dibatasi di backend)
- CRUD karyawan (admin)
- Check-in / check-out sekali per hari (UniqueConstraint di database)
- Laporan absensi: admin melihat semua, karyawan hanya miliknya
- Search dan pagination diproses di server (Django)
- Export karyawan dan absensi ke CSV dan Excel (mengikuti filter aktif)
- REST API (Django REST Framework)

## Tech Stack
Python, Django, Django REST Framework, SQLite, openpyxl

## Setup Lokal
```bash
git clone https://github.com/sayidulfm/employee-management.git
cd employee-management
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```
Buka http://127.0.0.1:8000/login/

## Akun Demo
| Peran | Username | Password |
|---|---|---|
| Admin | admin | admin12345 |
| Karyawan | budi | karyawan123 |

## Endpoint API
Autentikasi memakai session (login dulu lewat /login/).

| Method | URL | Akses |
|---|---|---|
| GET/POST | /api/employees/ | Admin |
| GET/PUT/PATCH/DELETE | /api/employees/{id}/ | Admin |
| GET | /api/attendance/ | Admin: semua, Karyawan: milik sendiri |
| POST | /api/attendance/check-in/ | Karyawan |
| POST | /api/attendance/check-out/ | Karyawan |

Parameter: `?search=` dan `?page=`.

## Keputusan Desain
- User bawaan Django berelasi OneToOne dengan Employee; admin = `is_staff`.
- Aturan "sekali per hari" memakai UniqueConstraint (employee, tanggal).
- Filter hak akses dilakukan di `get_queryset()`, bukan di frontend.
- Logika filter dipakai bersama oleh halaman list dan export.

## Status
Dikerjakan: autentikasi, CRUD, absensi, laporan, search/pagination, export, REST API.
Belum dikerjakan: dashboard, Docker, deploy.