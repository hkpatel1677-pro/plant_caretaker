from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Plant, UserRegistration

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(required=False)
    dob = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    phone = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "full_name", "dob", "phone")

class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = UserRegistration
        fields = ['full_name', 'dob', 'phone', 'address', 'course']
        widgets = {'dob': forms.DateInput(attrs={'type': 'date'})}

class PlantForm(forms.ModelForm):
    class Meta:
        model = Plant
        fields = ['name', 'description', 'care_instructions', 'water_frequency', 'custom_interval', 'water_time']
        widgets = {
            'water_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 2}),
            'care_instructions': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned = super().clean()
        freq = cleaned.get('water_frequency')
        custom = cleaned.get('custom_interval')
        if freq == 'custom' and not custom:
            raise forms.ValidationError("Please provide a custom interval (number of days).")
        return cleaned