from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    ROLES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('user', 'User')
    ]
    
    STATUSES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('banned', 'Banned')
    ]
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLES, default='user')
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    points = models.IntegerField(default=0)
    streak_days = models.IntegerField(default=0)
    last_streak_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUSES, default='active')
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Country information
    country = models.CharField(max_length=2, null=True, blank=True)  # ISO country code
    country_name = models.CharField(max_length=100, null=True, blank=True)
    country_rank = models.IntegerField(null=True, blank=True)
    global_rank = models.IntegerField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        app_label = 'quizhubapi'
    
    def update_streak(self):
        today = timezone.now().date()
        if self.last_streak_date:
            if self.last_streak_date == today - timezone.timedelta(days=1):
                self.streak_days += 1
            elif self.last_streak_date != today:
                self.streak_days = 1
        else:
            self.streak_days = 1
        self.last_streak_date = today
        self.save()

class Guest(models.Model):
    session_id = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'quizhubapi'