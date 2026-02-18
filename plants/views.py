# plants/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta

from .forms import SignUpForm, PlantForm, UserRegistrationForm
from .models import Plant, WaterSchedule, UserRegistration

from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # create profile if extra fields present
            full_name = form.cleaned_data.get('full_name', '')
            dob = form.cleaned_data.get('dob', None)
            phone = form.cleaned_data.get('phone', '')
            UserRegistration.objects.create(user=user, full_name=full_name, dob=dob, phone=phone)
            login(request, user)
            messages.success(request, "Account created and logged in.")
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'plants/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'plants/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    # summary and upcoming schedule
    profile = getattr(request.user, 'profile', None)
    total_plants = request.user.plants.count()
    upcoming = WaterSchedule.objects.filter(plant__added_by=request.user, scheduled_date__gte=date.today())[:10]
    missed = WaterSchedule.objects.filter(plant__added_by=request.user, scheduled_date__lt=date.today(), done=False)[:10]
    return render(request, 'plants/dashboard.html', {
        'profile': profile,
        'total_plants': total_plants,
        'upcoming_schedules': upcoming,
        'missed_schedules': missed,
    })

@login_required
def user_registration(request):
    try:
        profile = request.user.profile
    except UserRegistration.DoesNotExist:
        profile = UserRegistration(user=request.user)

    if request.method == 'POST':
        profile_form = UserRegistrationForm(request.POST, instance=profile)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Profile updated.")
            return redirect('dashboard')
    else:
        profile_form = UserRegistrationForm(instance=profile)
    return render(request, 'plants/user_registration.html', {'profile_form': profile_form})

@login_required
def plant_list(request):
    plants = request.user.plants.all()
    return render(request, 'plants/plant_list.html', {'plants': plants})

def _generate_schedule_for_plant(plant, days=7):
    """
    Create schedule entries for the next `days` days based on plant.get_interval_days() and water_time.
    If duplicate entries exist for the same day/time, ignore.
    """
    interval = plant.get_interval_days()
    start_date = date.today()
    created = 0
    for i in range(days):
        scheduled_date = start_date + timedelta(days=i * 1)  # we'll pick days and then filter by interval
        # Only create those where (difference days) % interval == 0
        delta_days = (scheduled_date - start_date).days
        if (delta_days % interval) == 0:
            # create if not exists
            obj, created_flag = WaterSchedule.objects.get_or_create(
                plant=plant,
                scheduled_date=scheduled_date,
                scheduled_time=plant.water_time,
                defaults={}
            )
            if created_flag:
                created += 1
    return created

@login_required
def plant_create(request):
    if request.method == 'POST':
        form = PlantForm(request.POST)
        if form.is_valid():
            plant = form.save(commit=False)
            plant.added_by = request.user
            plant.save()
            # generate schedule
            _generate_schedule_for_plant(plant, days=14)  # generate 2 weeks to be safe
            messages.success(request, "Plant added and schedule generated.")
            return redirect('plant_list')
    else:
        form = PlantForm()
    return render(request, 'plants/plant_form.html', {'form': form, 'form_title': 'Add Plant', 'button_text': 'Add Plant'})

@login_required
def plant_update(request, pk):
    plant = get_object_or_404(Plant, pk=pk, added_by=request.user)
    if request.method == 'POST':
        form = PlantForm(request.POST, instance=plant)
        if form.is_valid():
            plant = form.save()
            # optionally regenerate schedule: simple approach — delete future schedules and recreate
            WaterSchedule.objects.filter(plant=plant, scheduled_date__gte=date.today()).delete()
            _generate_schedule_for_plant(plant, days=14)
            messages.success(request, "Plant updated and future schedule regenerated.")
            return redirect('plant_list')
    else:
        form = PlantForm(instance=plant)
    return render(request, 'plants/plant_form.html', {'form': form, 'form_title': 'Edit Plant', 'button_text': 'Save Changes'})

@login_required
def plant_delete(request, pk):
    plant = get_object_or_404(Plant, pk=pk, added_by=request.user)
    if request.method == 'POST':
        plant.delete()
        messages.success(request, "Plant deleted.")
        return redirect('plant_list')
    return render(request, 'plants/plant_confirm_delete.html', {'plant': plant})

@login_required
def schedule_toggle_done(request, pk):
    sched = get_object_or_404(WaterSchedule, pk=pk, plant__added_by=request.user)
    if request.method == 'POST':
        if sched.done:
            # If unmarking, also clear last_watered if it matches this done_at
            if sched.plant.last_watered and sched.done_at and sched.plant.last_watered == sched.done_at:
                sched.plant.last_watered = None
                sched.plant.save()
            sched.mark_undone()
        else:
            sched.mark_done(by_user=request.user)
            # ✅ Update the plant’s last_watered timestamp
            sched.plant.last_watered = timezone.now()
            sched.plant.save()

        return redirect(request.META.get('HTTP_REFERER', reverse('dashboard')))
    return redirect('dashboard')
