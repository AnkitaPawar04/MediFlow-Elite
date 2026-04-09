"""URLs for bookings app."""
from django.urls import path
from . import views

urlpatterns = [
    path('book/<int:slot_id>/', views.book_appointment, name='book_appointment'),
    path('cancel/', views.cancel_booking, name='cancel_booking'),
    path('payment/<int:booking_id>/', views.initiate_payment, name='initiate_payment'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
]
