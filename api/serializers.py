from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Event, Registration
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone

class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = '__all__'  # Serialize all fields of the Event model

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None
    def get_registration_count(self, obj):
        """Return the count of registrations for the event."""
        return obj.registrations.count()
    
    def validate_capacity(self, value):
        """Ensure the capacity is a positive integer."""
        if value <= 0:
            raise serializers.ValidationError("Event is fully booked.")
        return value
    def validate_event_date(self, value):
        """Ensure the event date is in the future."""
        if value <= timezone.now():
            raise serializers.ValidationError("Event date expired.")
        return value
    def update(self, instance, validated_data):
        media = validated_data.pop('image', None)
        if media is None and hasattr(instance, 'image'):
            validated_data['image'] = instance.image
        return super().update(instance, validated_data)

class RegistrationSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    event_name = serializers.CharField(source='event.name', read_only=True)
    class Meta:
        model = Registration
        fields = ['id', 'name', 'email', 'registered_at', 'event', 'event_name'] # Serialize all fields of the Registration model

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ["id","username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def validate_email(self, value):
        """Ensure the email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value
    
class CustomTokenObtainSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['is_superuser'] = user.is_superuser
        token['is_staff'] = user.is_staff

        return token