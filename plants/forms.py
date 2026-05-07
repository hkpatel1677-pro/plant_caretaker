from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Plant, UserRegistration

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}))


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(required=False)
    dob = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    phone = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'autocomplete': 'username'})
        self.fields['email'].widget.attrs.update({'autocomplete': 'email'})
        self.fields['password1'].widget.attrs.update({'autocomplete': 'new-password'})
        self.fields['password2'].widget.attrs.update({'autocomplete': 'new-password'})
        self.fields['full_name'].widget.attrs.update({'autocomplete': 'name'})
        self.fields['phone'].widget.attrs.update({'autocomplete': 'tel'})

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "full_name", "dob", "phone")

class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = UserRegistration
        fields = ['full_name', 'dob', 'phone', 'address', 'course']
        widgets = {
            'full_name': forms.TextInput(attrs={'autocomplete': 'name'}),
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'phone': forms.TextInput(attrs={'autocomplete': 'tel'}),
            'address': forms.Textarea(attrs={'autocomplete': 'street-address', 'rows': 3}),
            'course': forms.TextInput(attrs={'autocomplete': 'organization-title'}),
        }

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