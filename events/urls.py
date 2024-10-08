from django.urls import path
from .views import (
    home,
    index,  # Ensure this matches the function name in views.py
    register,
    user_login,
    user_logout,
    community_list_view,
    community_details_view,
    community_create_view,
    event_list_view,
    event_details_view,  # Make sure this is correct
    event_create_view,
    interfaith_networking,
    CustomLoginView,
    about_us,
    contact,
    
)

urlpatterns = [
    path('', home, name='home'),
    path('index/', index, name='index'),  # Ensure the function name matches
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', user_logout, name='logout'),
    path('communities/', community_list_view, name='community_list'),
    path('communities/<int:community_id>/', community_details_view, name='community_details'),  # Ensure consistent naming
    path('communities/create/', community_create_view, name='community_create'),
    path('events/', event_list_view, name='event_list'),
    path('events/<int:event_id>/', event_details_view, name='event_details'),  # Use 'event_details' for consistency
    path('events/create/', event_create_view, name='event_create'),
    path('interfaith_networking/', interfaith_networking, name='interfaith_networking'),
    path('about/', about_us, name='about_us'),  # Example pattern
    path('contact/', contact, name='contact'),  # Example pattern


]
