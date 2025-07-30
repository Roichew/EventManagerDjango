from django.db import models
from django.utils import timezone
# Create your models here.

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateTimeField()
    location = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='events_images/', null=True, blank=True)

    def __str__(self):
        return self.name 
    
    @property
    def is_full(self):
        """Check if the event is fully booked."""
        return self.registrations.count() >= self.capacity
    
    @property
    def check_availability(self):
        return self.capacity - self.registrations.count()
    
    @property
    def is_expired(self):
        """Check if the event date has passed."""
        return self.event_date < timezone.now()  
    
class Registration(models.Model):
    event = models.ForeignKey(Event, related_name='registrations', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    registered_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_event_name(self):
        """Get the name of the event."""
        return self.event.name
    
    def __str__(self):
        return f"{self.name} - {self.event.name}"  
    
