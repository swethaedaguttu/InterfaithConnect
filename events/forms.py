# events/forms.py

from django import forms
from django.contrib.auth.models import User  # Import User model
from django.contrib.auth.forms import UserCreationForm  # Import UserCreationForm
from .models import Community, Event, User, Partnership, SupportRequest, Feedback  # Ensure all necessary models are imported

class CommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['name', 'description', 'created_by']  # Adjust based on your Community model fields

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'community', 
            'title', 
            'date', 
            'location', 
            'description', 
            'organizer', 
            'max_participants', 
            'rsvp_deadline'
        ]  # Ensure these fields exist in your Event model

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User  # Now this should work correctly
        fields = ['username', 'email', 'password1', 'password2']  # Use password1 and password2 for UserCreationForm

    # Optionally, you can add additional validation
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

class PartnershipForm(forms.ModelForm):
    class Meta:
        model = Partnership
        fields = ['community', 'partner_name', 'partnership_date', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'partnership_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(PartnershipForm, self).__init__(*args, **kwargs)
        self.fields['partner_name'].widget.attrs.update({'placeholder': 'Enter partner name'})
        self.fields['description'].widget.attrs.update({'placeholder': 'Enter description'})


class SupportForm(forms.ModelForm):
    class Meta:
        model = SupportRequest
        fields = ['community', 'user_name', 'request_details']
        widgets = {
            'request_details': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super(SupportForm, self).__init__(*args, **kwargs)
        self.fields['user_name'].widget.attrs.update({'placeholder': 'Enter your name'})
        self.fields['request_details'].widget.attrs.update({'placeholder': 'Describe your support request'})


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['community', 'user_name', 'feedback_text']
        widgets = {
            'feedback_text': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        self.fields['user_name'].widget.attrs.update({'placeholder': 'Enter your name'})
        self.fields['feedback_text'].widget.attrs.update({'placeholder': 'Enter your feedback'})
