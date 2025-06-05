from django.db import models
from .user import User

class Notification(models.Model):
    TYPES = [
        ('friend_request', 'Friend Request'),
        ('match_invite', 'Match Invite'),
        ('friend_playing', 'Friend Playing'),
        ('match_started', 'Match Started'),
        ('support_received', 'Support Received'),
        ('moderation_action', 'Moderation Action'),
        ('quiz_approved', 'Quiz Approved'),
        ('quiz_rejected', 'Quiz Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPES)
    title = models.CharField(max_length=100)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True)  # Extra payload
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'quizhubapi'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"