"""URL Configuration for HMS."""
from django.contrib import admin
from django.urls import path, include
from accounts.views import home
from accounts.views import google_calendar_callback

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    path('doctors/', include('doctors.urls')),
    path('patients/', include('patients.urls')),
    path('bookings/', include('bookings.urls')),
    path('google/callback/', google_calendar_callback, name='google_calendar_callback'),

]
