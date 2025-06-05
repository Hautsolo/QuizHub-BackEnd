# quizhubapi/models/moderation.py
from django.db import models
from .user import User, Guest

class Report(models.Model):
    TARGET_TYPES = [
        ('user', 'User'),
        ('question', 'Question'),
        ('match', 'Match'),
        ('chat', 'Chat Message')
    ]
    
    STATUSES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed')
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    target_type = models.CharField(max_length=20, choices=TARGET_TYPES)
    target_id = models.IntegerField()
    reason = models.TextField(max_length=500)
    additional_info = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUSES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports_reviewed')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'quizhubapi'

class ModeratorAction(models.Model):
    ACTION_TYPES = [
        ('warn', 'Warn'),
        ('suspend', 'Suspend'),
        ('ban', 'Ban'),
        ('delete', 'Delete Content'),
        ('approve', 'Approve'),
        ('reject', 'Reject')
    ]
    
    TARGET_TYPES = [
        ('user', 'User'),
        ('question', 'Question'),
        ('match', 'Match'),
        ('chat', 'Chat Message')
    ]
    
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moderator_actions')
    action_type = models.CharField(max_length=10, choices=ACTION_TYPES)
    target_type = models.CharField(max_length=20, choices=TARGET_TYPES)
    target_id = models.IntegerField()
    reason = models.TextField(max_length=500)
    duration_hours = models.IntegerField(null=True, blank=True)  # For suspensions
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'quizhubapi'

class BannedWord(models.Model):
    word = models.CharField(max_length=50, unique=True)
    is_exact_match = models.BooleanField(default=False)
    banned_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'quizhubapi'

class LiveChat(models.Model):
    match = models.ForeignKey('Match', on_delete=models.CASCADE, related_name='chat_messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField(max_length=500)
    is_system_message = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'quizhubapi'
        ordering = ['created_at']
    
    @property
    def sender_name(self):
        if self.user:
            return self.user.username
        return self.guest.display_name if self.guest else 'System'