"""Validated Django forms for CU-VTS Fleet Management."""

from __future__ import annotations

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from apps.accounts.models import DriverProfile

from .models import Vehicle


class VehicleForm(forms.Form):
    """Create or edit (including rename) a fleet vehicle."""

    bus_number = forms.CharField(max_length=32, strip=True)
    registration_number = forms.CharField(max_length=64, required=False, strip=True)
    route_label = forms.CharField(max_length=120, required=False, strip=True)
    admin_description = forms.CharField(max_length=280, required=False, strip=True)
    is_active = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, instance: Vehicle | None = None, **kwargs) -> None:
        self.instance = instance
        super().__init__(*args, **kwargs)

    def clean_bus_number(self) -> str:
        value = self.cleaned_data["bus_number"].strip()
        if not value:
            raise forms.ValidationError("Vehicle name / bus number is required.")
        qs = Vehicle.objects.filter(bus_number__iexact=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f'A vehicle named "{value}" already exists.')
        return value

    def clean_registration_number(self) -> str:
        value = (self.cleaned_data.get("registration_number") or "").strip()
        if not value:
            return ""
        qs = Vehicle.objects.filter(registration_number__iexact=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f'Registration "{value}" is already assigned to another vehicle.')
        return value


class AssignDriverForm(forms.Form):
    """Assign an active driver to an active vehicle."""

    vehicle = forms.ModelChoiceField(
        queryset=Vehicle.objects.filter(is_active=True).order_by("bus_number"),
        error_messages={"invalid_choice": "Please choose an active vehicle."},
    )
    driver = forms.ModelChoiceField(
        queryset=DriverProfile.objects.filter(is_active=True)
        .select_related("user")
        .order_by("user__first_name", "user__username"),
        error_messages={"invalid_choice": "Please choose an active driver."},
    )


class DriverCreateForm(forms.Form):
    """Create a new driver account and profile."""

    username = forms.CharField(max_length=150, strip=True)
    first_name = forms.CharField(max_length=150, required=False, strip=True)
    last_name = forms.CharField(max_length=150, required=False, strip=True)
    employee_id = forms.CharField(max_length=50, required=False, strip=True)
    phone_number = forms.CharField(max_length=32, required=False, strip=True)
    password = forms.CharField(min_length=8, widget=forms.PasswordInput)

    def clean_username(self) -> str:
        value = self.cleaned_data["username"].strip()
        if not value:
            raise forms.ValidationError("Username is required.")
        if User.objects.filter(username__iexact=value).exists():
            raise forms.ValidationError(f'Username "{value}" is already taken.')
        return value

    def clean_employee_id(self) -> str:
        value = (self.cleaned_data.get("employee_id") or "").strip()
        if value and DriverProfile.objects.filter(employee_id__iexact=value).exists():
            raise forms.ValidationError(f'Employee ID "{value}" is already assigned.')
        return value

    def clean_password(self) -> str:
        password = self.cleaned_data["password"]
        validate_password(password)
        return password


class DriverEditForm(forms.Form):
    """Edit an existing driver profile and optionally reset their password."""

    first_name = forms.CharField(max_length=150, required=False, strip=True)
    last_name = forms.CharField(max_length=150, required=False, strip=True)
    employee_id = forms.CharField(max_length=50, required=False, strip=True)
    phone_number = forms.CharField(max_length=32, required=False, strip=True)
    new_password = forms.CharField(required=False, widget=forms.PasswordInput)

    def __init__(self, *args, instance: DriverProfile, **kwargs) -> None:
        self.instance = instance
        super().__init__(*args, **kwargs)

    def clean_employee_id(self) -> str:
        value = (self.cleaned_data.get("employee_id") or "").strip()
        if (
            value
            and DriverProfile.objects.filter(employee_id__iexact=value)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError(f'Employee ID "{value}" is already assigned.')
        return value

    def clean_new_password(self) -> str:
        password = self.cleaned_data.get("new_password") or ""
        if password:
            validate_password(password, user=self.instance.user)
        return password
