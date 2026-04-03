"""Admin configuration for doctors app."""
from django.contrib import admin
from .models import AvailabilitySlot


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    """Admin for AvailabilitySlot model."""
    
    list_display = ('doctor', 'date', 'start_time', 'end_time', 'is_booked')
    list_filter = ('date', 'is_booked', 'doctor')
    search_fields = ('doctor__email', 'date')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
