from django import forms
from hostels.models import Booking


class BookingForm(forms.ModelForm):
    terms_and_conditions = forms.BooleanField(
        required=True,
        label="I accept the Terms and Conditions",
        error_messages={'required': 'You must accept the terms and conditions to proceed.'}
    )

    class Meta:
        model = Booking
        fields = [
            'full_name', 'admission_number', 'phone_number', 'email', 'semester',
            'emergency_name', 'emergency_phone', 'emergency_relationship',
            'room_type', 'transaction_message'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'admission_number': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'semester': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_relationship': forms.TextInput(attrs={'class': 'form-control'}),
            'room_type': forms.Select(attrs={'class': 'form-control'}),
            'transaction_message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter transaction details here...',
            }),
        }