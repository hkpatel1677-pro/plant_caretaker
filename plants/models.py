# plants/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, datetime, time as dtime

class UserRegistration(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=200, blank=True)
    dob = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    course = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.full_name or self.user.username

class Plant(models.Model):
    FREQUENCY_CHOICES = [
        ('1', 'Daily'),
        ('2', 'Every 2 days'),
        ('3', 'Every 3 days'),
        ('7', 'Weekly (every 7 days)'),
        ('custom', 'Custom (days)'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    care_instructions = models.TextField(blank=True)
    water_frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='7')
    custom_interval = models.PositiveIntegerField(null=True, blank=True,
                                                  help_text="If frequency is Custom, number of days between watering.")
    water_time = models.TimeField(default=dtime(hour=9, minute=0))
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plants')
    created_at = models.DateTimeField(auto_now_add=True)
    last_watered = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_interval_days(self):
        if self.water_frequency == 'custom':
            return self.custom_interval or 1
        try:
            return int(self.water_frequency)
        except Exception:
            return 7

class WaterSchedule(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='schedules')
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    done = models.BooleanField(default=False)
    done_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['scheduled_date', 'scheduled_time']
        unique_together = ('plant', 'scheduled_date', 'scheduled_time')

    def mark_done(self, by_user=None):
        self.done = True
        self.done_at = timezone.now()
        self.save()

    def mark_undone(self):
        self.done = False
        self.done_at = None
        self.save()

    def __str__(self):
        return f"{self.plant.name} on {self.scheduled_date} @ {self.scheduled_time}"