"""Admin configuration for bookings app."""
from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin for Booking model."""
    
    list_display = ('patient', 'doctor', 'slot', 'created_at')
    list_filter = ('created_at', 'doctor')
    search_fields = ('patient__email', 'doctor__email')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
