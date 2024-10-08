# events/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Community, Event, UnifiedNight, Activity, Partnership, SupportRequest, Resource, Notification, Feedback, UserProfile  # Import your UserProfile model
from .forms import CommunityForm, EventForm, UserRegistrationForm, PartnershipForm, SupportForm, FeedbackForm  # Import your forms
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required  # Import login_required
from features.models import Feature  # Import your Feature model
from django.contrib.auth.views import LoginView
from django.utils import timezone
from django.core.paginator import Paginator
from django_otp.decorators import otp_required
from django.conf import settings
from django.db import IntegrityError
from django.contrib.auth.models import User  # Import the User model
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail

import openai  # Assuming OpenAI API is used for AI-powered features
import random

def send_otp(email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP code is: {otp}'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])


def verify_otp(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        username = request.session.get('username')

        if user_otp and stored_otp and int(user_otp) == int(stored_otp):
            # If OTP is valid, log the user in
            user = authenticate(request, username=username)
            if user:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                del request.session['otp']  # Remove OTP from session
                del request.session['username']  # Remove username from session
                return redirect('home')  # Redirect to home
            else:
                messages.error(request, 'Authentication failed.')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'events/verify_otp.html')


def home(request):
    communities = Community.objects.all()
    unified_nights = UnifiedNight.objects.all()
    events = Event.objects.all()
    features = Feature.objects.all()
    activities = Activity.objects.all()

    search_query = request.GET.get('search', '')
    if search_query:
        # Ensure you're filtering events using the correct field
        communities = communities.filter(name__icontains=search_query)
        events = events.filter(title__icontains=search_query)

    context = {
        'communities': communities,
        'unified_nights': unified_nights,
        'events': events,
        'features': features,
        'activities': activities,
        'search_query': search_query,  # Include the search query in the context
    }
    return render(request, 'events/home.html', context)

def index(request):
    query = request.GET.get('search', '')  # Default to empty string if not provided
    communities = Community.objects.all()
    events = Event.objects.all()

    if query:
        communities = communities.filter(name__icontains=query)  # Adjust the field name accordingly
        events = events.filter(title__icontains=query)  # Use the correct field for filtering

    context = {
        'communities': communities,
        'events': events,
        'search_query': query,  # Include the search query in the context
    }
    return render(request, 'events/index.html', context)  # Fixed the backslash to forward slash

# Authentication Views

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'  # Your login template

    def get(self, request, *args, **kwargs):
        # Check if there is a message in the session to display
        message = request.GET.get('message')
        if message:
            messages.error(request, message)
        return super().get(request, *args, **kwargs)

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Create the user without password confirmation
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('home')  # Redirect to home after successful registration

        except IntegrityError:
            messages.error(request, 'Username or email already exists.')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')

    return render(request, 'events/register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate the user with username and password
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log the user in and redirect to home
            login(request, user)
            return redirect('home')  # Redirect to the home page after login
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'events/login.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

# Community Views

def about_us(request):
    return render(request, 'events/about_us.html')  # Adjust the template name as necessary

def contact(request):
    return render(request, 'events/contact.html')  # Adjust the template name as necessary

def profile(request):
    return render(request, 'profile.html')  # Make sure this template exists

 # Ensure only logged-in users can create communities
def community_list_view(request):
    communities = Community.objects.all()
    return render(request, 'events/community_list.html', {'communities': communities})

 # Ensure only logged-in users can view community details
def community_details_view(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    events = Event.objects.filter(community=community)
    return render(request, 'events/community_details.html', {'community': community, 'events': events})

 # Ensure only logged-in users can create communities
def community_create_view(request):
    if request.method == 'POST':
        form = CommunityForm(request.POST)
        if form.is_valid():
            community = form.save(commit=False)
            community.created_by = request.user  # Assign the logged-in user
            community.save()
            messages.success(request, f'Community "{community.name}" created successfully!')
            return redirect('community_detail', community_id=community.id)
    else:
        form = CommunityForm()
    return render(request, 'events/community_form.html', {'form': form})

# Event Views

  # Ensure only logged-in users can view events
def event_list_view(request):
    events = Event.objects.all()
    return render(request, 'events/event_list.html', {'events': events})

  # Ensure only logged-in users can view event details
def event_details_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/event_details.html', {'event': event})

  # Ensure only logged-in users can create events
def event_create_view(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user  # Assign the logged-in user
            event.save()
            messages.success(request, f'Event "{event.title}" created successfully!')
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form})

def interfaith_networking(request):
    # Fetch communities involved in interfaith activities
    communities = Community.objects.filter(is_interfaith=True)  # Filter communities based on some criteria
    # Fetch upcoming events related to interfaith networking
    events = Event.objects.filter(type='interfaith').order_by('date')  # Assuming you have a 'type' field

    context = {
        'title': 'Interfaith Networking',
        'description': 'Connect with people from different religious backgrounds to share experiences and insights.',
        'communities': communities,
        'events': events,
    }
    
    return render(request, 'events/interfaith_networking.html', context)


def create_event_view(request):
    communities = Community.objects.all()  # Fetch all communities

    if request.method == 'POST':
        # Handle form submission with some validation checks
        try:
            title = request.POST['title']
            community_id = request.POST['community']
            location = request.POST['location']
            date = request.POST['date']
            description = request.POST['description']
            organizer = request.user.username  # Organizer is the logged-in user

            # Fetch selected community, raise 404 if not found
            community = Community.objects.get(id=community_id)

            # Convert the date string to datetime if necessary
            try:
                date = timezone.make_aware(timezone.datetime.strptime(date, '%Y-%m-%dT%H:%M'))
            except ValueError:
                messages.error(request, 'Invalid date format. Please try again.')
                return render(request, 'events/event_form.html', {'communities': communities})

            # Create the new event and save it
            event = Event(title=title, location=location, date=date, description=description, organizer=organizer, community=community)
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_detail', event_id=event.id)

        except Community.DoesNotExist:
            messages.error(request, 'Community does not exist.')
            return render(request, 'events/event_form.html', {'communities': communities})

    return render(request, 'events/create_event.html', {'communities': communities})

def partnership_create_view(request):
    if request.method == 'POST':
        form = PartnershipForm(request.POST)
        if form.is_valid():
            partnership = form.save(commit=False)
            partnership.created_by = request.user  # Assign the logged-in user
            partnership.save()
            messages.success(request, 'Partnership created successfully!')
            return redirect('partnership_detail', partnership_id=partnership.id)
    else:
        form = PartnershipForm()
    return render(request, 'events/partnership_form.html', {'form': form})


def support_request_view(request):
    if request.method == 'POST':
        form = SupportForm(request.POST)
        if form.is_valid():
            support_request = form.save(commit=False)
            support_request.created_by = request.user  # Assign the logged-in user
            support_request.save()
            messages.success(request, 'Support request submitted successfully!')
            return redirect('support_request_detail', support_request_id=support_request.id)
    else:
        form = SupportForm()
    return render(request, 'events/support_request_form.html', {'form': form})


def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user  # Assign the logged-in user
            feedback.save()
            messages.success(request, 'Feedback submitted successfully!')
            return redirect('home')
    else:
        form = FeedbackForm()
    return render(request, 'events/feedback_form.html', {'form': form})


def community_delete_view(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    if request.method == 'POST':
        community.delete()
        messages.success(request, 'Community deleted successfully!')
        return redirect('community_list')  # Adjust the redirect as needed
    return render(request, 'events/community_confirm_delete.html', {'community': community})


def event_delete_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('event_list')  # Adjust the redirect as needed
    return render(request, 'events/event_confirm_delete.html', {'event': event})

def ai_response(prompt):
    try:
        openai.api_key = 'your_openai_api_key'  # Use environment variables for sensitive data
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    except openai.error.OpenAIError as e:
        return "AI is currently unavailable. Please try again later."


def ai_chat_view(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        ai_reply = ai_response(user_input)
        return render(request, 'events/ai_chat.html', {'ai_reply': ai_reply, 'user_input': user_input})

    return render(request, 'events/ai_chat.html')

def feedback_list_view(request):
    feedbacks = Feedback.objects.all()
    return render(request, 'events/feedback_list.html', {'feedbacks': feedbacks})

def notification_list_view(request):
    notifications = Notification.objects.filter(user=request.user)  # Adjust as per your notification model
    return render(request, 'events/notification_list.html', {'notifications': notifications})


def resources_view(request):
    resources = Resource.objects.all()
    return render(request, 'events/resources.html', {'resources': resources})
