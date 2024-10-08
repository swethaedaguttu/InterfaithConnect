from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models.signals import post_save
import pyotp  # You'll need to install the pyotp package for generating TOTP

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_2fa_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


def create_user_profile(sender, instance, created, **kwargs):
    """Signal to create a UserProfile when a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)

# Connecting the signal
post_save.connect(create_user_profile, sender=User)


# Model representing a Community
class Community(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Community name, must be unique
    description = models.TextField()  # Description of the community
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)  # User who created the community
    is_interfaith = models.BooleanField(default=False)  # Flag to identify interfaith communities

    def __str__(self):
        return self.name  # Display community name in the admin interface and other uses


# Model representing an Event
class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('interfaith', 'Interfaith'),
    ]

    community = models.ForeignKey(Community, on_delete=models.CASCADE)  # Event belongs to a community
    title = models.CharField(max_length=200)  # Event title
    date = models.DateTimeField(null=True, blank=True)  # Date and time of the event
    location = models.CharField(max_length=200)  # Location of the event
    description = models.TextField()  # Detailed description of the event
    organizer = models.CharField(max_length=100)  # Name of the event organizer
    max_participants = models.PositiveIntegerField(null=True, blank=True)  # Maximum participants, can be null
    rsvp_deadline = models.DateTimeField(null=True, blank=True)  # Deadline for RSVPs, optional
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)  # User who created the event
    type = models.CharField(max_length=10, choices=EVENT_TYPE_CHOICES, default='public')  # Event type (public/private)

    def clean(self):
        # Validate that the event date is not in the past
        if self.date and self.date < timezone.now():
            raise ValidationError('Event date cannot be in the past.')
        
        # Validate that RSVP deadline is before the event date
        if self.rsvp_deadline and self.date and self.rsvp_deadline >= self.date:
            raise ValidationError('RSVP deadline must be before the event date.')

    def __str__(self):
        return f"{self.title} ({self.community.name})"  # Display event title and community in the admin interface


# Model representing a Unified Night event (if applicable)
class UnifiedNight(models.Model):
    name = models.CharField(max_length=100)  # Name of the unified night event
    date = models.DateField()  # Date of the event
    location = models.CharField(max_length=255)  # Location where the event takes place
    description = models.TextField(blank=True)  # Optional description of the event

    def __str__(self):
        return self.name  # Display name in the admin interface


# Model representing an Activity
class Activity(models.Model):
    name = models.CharField(max_length=100)  # Name of the activity
    date = models.DateField()  # Date when the activity will take place
    description = models.TextField(blank=True)  # Optional description of the activity

    def __str__(self):
        return self.name  # Display name of the activity in the admin interface


# Model representing a Partnership
class Partnership(models.Model):
    community = models.ForeignKey(Community, related_name='partnerships', on_delete=models.CASCADE)
    partner_name = models.CharField(max_length=100)
    partnership_date = models.DateField()
    description = models.TextField()

    def __str__(self):
        return self.partner_name


# Model representing a Support Request
class SupportRequest(models.Model):
    community = models.ForeignKey(Community, related_name='support_requests', on_delete=models.CASCADE)
    user_name = models.CharField(max_length=100)
    request_date = models.DateTimeField(auto_now_add=True)
    request_details = models.TextField()

    def __str__(self):
        return f"Support Request by {self.user_name}"


# Model representing a Resource
class Resource(models.Model):
    community = models.ForeignKey(Community, related_name='resources', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    link = models.URLField()

    def __str__(self):
        return self.title


# Model representing a Notification
class Notification(models.Model):
    community = models.ForeignKey(Community, related_name='notifications', on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message[:50]  # Display first 50 characters


# Model representing Feedback
class Feedback(models.Model):
    community = models.ForeignKey(Community, related_name='feedbacks', on_delete=models.CASCADE)
    user_name = models.CharField(max_length=100)
    feedback_date = models.DateTimeField(auto_now_add=True)
    feedback_text = models.TextField()

    def __str__(self):
        return f"Feedback from {self.user_name}"
