# plants/admin.py
from django.contrib import admin
from .models import Plant, WaterSchedule, UserRegistration

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('name', 'added_by', 'water_frequency', 'water_time', 'last_watered')
    search_fields = ('name', 'added_by__username')
    list_filter = ('water_frequency',)

@admin.register(WaterSchedule)
class WaterScheduleAdmin(admin.ModelAdmin):
    list_display = ('plant', 'scheduled_date', 'scheduled_time', 'done')
    list_filter = ('done', 'scheduled_date')

@admin.register(UserRegistration)
class UserRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone')
