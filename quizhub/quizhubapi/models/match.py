# quizhubapi/models/match.py
from django.db import models
from django.utils import timezone
from .user import User, Guest
import uuid

class Match(models.Model):
    STATUSES = [
        ('waiting', 'Waiting'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    
    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_created')
    is_private = models.BooleanField(default=False)
    allow_guests = models.BooleanField(default=True)
    max_players = models.IntegerField(default=2)
    status = models.CharField(max_length=15, choices=STATUSES, default='waiting')
    room_code = models.CharField(max_length=8, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'quizhubapi'
    
    def save(self, *args, **kwargs):
        if not self.room_code:
            self.room_code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)
    
    def start_match(self):
        self.status = 'in_progress'
        self.started_at = timezone.now()
        self.save()
    
    def end_match(self):
        self.status = 'completed'
        self.ended_at = timezone.now()
        self.save()

class MatchPlayer(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='players')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, null=True, blank=True)
    score = models.IntegerField(default=0)
    position = models.IntegerField(null=True, blank=True)
    is_ready = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'quizhubapi'
        unique_together = ['match', 'user', 'guest']
    
    @property
    def display_name(self):
        if self.user:
            return self.user.username
        return self.guest.display_name if self.guest else 'Anonymous'

class MatchInvite(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='invites')
    token = models.CharField(max_length=32, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    expires_at = models.DateTimeField()
    max_uses = models.IntegerField(default=1)
    use_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        app_label = 'quizhubapi'
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str(uuid.uuid4()).replace('-', '')
        super().save(*args, **kwargs)
    
    def is_valid(self):
        return (self.is_active and 
                self.expires_at > timezone.now() and 
                self.use_count < self.max_uses)

class MatchSupport(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='supports')
    supporter_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    supporter_guest = models.ForeignKey(Guest, on_delete=models.CASCADE, null=True, blank=True)
    supported_player = models.ForeignKey(MatchPlayer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'quizhubapi'
        unique_together = ['match', 'supporter_user', 'supporter_guest']

class Spectator(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='spectators')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'quizhubapi'
        unique_together = ['match', 'user', 'guest']