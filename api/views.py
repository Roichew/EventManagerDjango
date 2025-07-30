from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate, login
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
import logging
from .models import Event, Registration
from .serializers import EventSerializer, RegistrationSerializer, UserSerializer, CustomTokenObtainSerializer

logger = logging.getLogger(__name__)

class isAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

class EventListView(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.request.method in ['POST']:
            return [ isAdmin()]
        return [AllowAny()]

    def get_queryset(self):
        queryset = Event.objects.select_related().prefetch_related('registrations')
        
        # Filter out expired events or move them to bottom
        now = timezone.now()
        active_events = queryset.filter(event_date__gte=now)
        expired_events = queryset.filter(event_date__lt=now)
        
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )
        # Return active events first, then expired ones
        return queryset.extra(select={'is_future': 'event_date >= %s'},select_params=[now]).order_by('-is_future', 'event_date')

class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated()]
        return [AllowAny()]

#event registration views
class RegistrationListView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user_email = self.request.user.email
        return Registration.objects.filter(email=user_email).select_related('event')

class RegistrationDetailsView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer
    queryset = Registration.objects.select_related('event')

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_event(request, event_id):
    """Register a user for a specific event"""
    try:
        event = get_object_or_404(Event, id=event_id)
        
        # Check if event has already passed
        if event.event_date < timezone.now():
            return Response({
                'success': False, 
                'message': 'Cannot register for past events'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data.copy()
        email = data.get('email')
        
        if not email:
            return Response({
                'success': False, 
                'message': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check for duplicate registration
        if Registration.objects.filter(event=event, email=email).exists():
            return Response({
                'success': False, 
                'message': 'Already registered with this email'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check capacity
        if event.registrations.count() >= event.capacity:
            return Response({
                'success': False, 
                'message': 'Event is full'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data['event'] = event.id
        serializer = RegistrationSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save(event=event)
            return Response({
                'success': True, 
                'message': 'Registered successfully', 
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False, 
            'message': 'Registration failed', 
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Event.DoesNotExist:
        return Response({
            'success': False, 
            'message': 'Event not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
        return Response({
            'success': False, 
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Unexpected error in register_event: {e}")
        return Response({
            'success': False, 
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Template views
def event_view(request):
    """Display events page"""
    return render(request, 'index.html')

def login_view(request):
    """Display login page"""
    return render(request, 'login.html')

def registration_view(request):
    """Display registration page"""
    return render(request, 'registration.html')

@permission_classes([IsAuthenticated])
def user_dashboard(request):
    return render(request, 'user_dashboard.html')

@permission_classes([IsAuthenticated])
def admin_dashboard(request):
     return render(request, 'admin_dashboard.html')

class LogoutView(views.LogoutView):
    """Custom logout view"""
    next_page = '/login/'

    def get(self, request, *args, **kwargs):
        """Handle GET request for logout"""
        response = super().get(request, *args, **kwargs)
        response.data = {
            'success': True,
            'message': 'Logged out successfully'
        }
        return response
      
#create new user
class CreateNewUserView(generics.CreateAPIView):
    """Create a new user view"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

#obtain jwt token
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainSerializer

#retieve user info from jwt tokens
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    user = request.user
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "name": user.get_full_name()
    })