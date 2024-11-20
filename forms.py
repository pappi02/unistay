from django import forms
from hostels.models import Hostel

class BookingForm(forms.Form):
    # Personal Information
    full_name = forms.CharField(
        max_length=100, 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder': 'Full name'})
    )
    admission_number = forms.CharField(
        max_length=20, 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder': 'Admission number'})
    )
    phone_number = forms.CharField(
        max_length=15, 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder': 'Phone number'})
    )
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'placeholder': 'Email address'})
    )
    semester = forms.CharField(
        max_length=50, 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Semester 1, Year 2'})
    )

    # Emergency Contact Information
    emergency_name = forms.CharField(  
        max_length=100, 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder': 'Name'})
    )
    emergency_phone = forms.CharField(  
        max_length=15, 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder': 'Number'})
    )
    emergency_relationship = forms.CharField(  
        max_length=50, 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder': 'Relationship to you'})
    )

    # Room Details
    hostel_name = forms.ChoiceField(choices=[], required=True)  # Dynamically populated in the view
    room_type = forms.ChoiceField(
        choices=[('Single', 'Single'), ('Double', 'Double')], 
        required=True
    )
    room_number = forms.CharField(
        max_length=20, 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder': 'Room number'})
    )

    # Terms and Conditions
    terms_accepted = forms.BooleanField(
        required=True, 
        widget=forms.CheckboxInput(attrs={'class': 'terms-checkbox,'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Initialize parent class first

        # Dynamically populate the hostel_name choices from the Hostel model
        hostels = Hostel.objects.all()
        hostel_choices = [(hostel.id, hostel.name) for hostel in hostels]
        self.fields['hostel_name'].choices = hostel_choices

    def clean_terms_accepted(self):
        """ Custom validation for terms acceptance """
        if not self.cleaned_data.get('terms_accepted'):
            raise forms.ValidationError('You must accept the terms and conditions.')
        return self.cleaned_data['terms_accepted']
