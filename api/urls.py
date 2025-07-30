from django.contrib import admin
from django.urls import path
from .views import EventListView, EventDetailView, RegistrationListView, RegistrationDetailsView, CreateNewUserView
from .views import login_view, register_event, event_view, registration_view, user_dashboard, admin_dashboard, get_user_info
from django.contrib.auth import views as auth_views
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    #event URLs
    path('events/main', views.EventListView.as_view(), name='event-list'),
    path('events/<int:pk>/', views.EventDetailView.as_view()),

    #registration URLs
    #when registering for an event
    path('events/<int:event_id>/register/', register_event),

    #registration list and details
    path('my-registrations/', views.RegistrationListView.as_view(), name='event-register'),
    path('registration/<int:event_id>/', views.RegistrationDetailsView.as_view()),

    #frontend views
    path('events/', event_view, name='event-view'),
    path('registration/user', registration_view, name='registration-view'),
    path('login/', login_view, name='login-view'),  
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('admin-dashboard/', admin_dashboard, name='dashboard'),
    path('dashboard/', user_dashboard, name='dashboard'),

    #get user info
    path('user/', get_user_info, name='info'),



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)