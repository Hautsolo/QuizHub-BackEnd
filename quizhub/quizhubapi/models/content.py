# quizhubapi/models/content.py
from django.db import models
from django.utils import timezone
from .user import User

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'quizhubapi'
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name

class Topic(models.Model):
    DIFFICULTY_CHOICES = [(i, str(i)) for i in range(1, 6)]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='topics')
    name = models.CharField(max_length=50)
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'quizhubapi'
        unique_together = ['category', 'name']
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"

class MediaFile(models.Model):
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('audio', 'Audio'),
        ('video', 'Video'),
    ]
    
    file = models.FileField(upload_to='media/')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    original_filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField()  # in bytes
    mime_type = models.CharField(max_length=100)
    duration = models.IntegerField(null=True, blank=True)  # for audio/video
    width = models.IntegerField(null=True, blank=True)  # for images/video
    height = models.IntegerField(null=True, blank=True)  # for images/video
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'quizhubapi'
    
    def __str__(self):
        return f"{self.media_type.title()}: {self.original_filename}"

class Question(models.Model):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('image_choice', 'Image Choice'),
        ('audio_choice', 'Audio Choice'),
        ('video_choice', 'Video Choice'),
    ]
    
    MEDIA_TYPES = [
        ('text', 'Text Only'),
        ('image', 'Image'),
        ('audio', 'Audio'),
        ('video', 'Video'),
    ]
    
    STATUSES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    
    DIFFICULTY_CHOICES = [(i, str(i)) for i in range(1, 6)]
    
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(max_length=500, blank=True)  # Made optional for media-only questions
    type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions_created')
    status = models.CharField(max_length=10, choices=STATUSES, default='pending')
    
    # Multimedia fields
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, default='text')
    image = models.ImageField(upload_to='questions/images/', null=True, blank=True)
    audio = models.FileField(upload_to='questions/audio/', null=True, blank=True)
    video = models.FileField(upload_to='questions/videos/', null=True, blank=True)
    media_url = models.URLField(blank=True)  # For external media (YouTube, etc.)
    
    # Additional metadata
    media_description = models.TextField(max_length=200, blank=True)  # Alt text/description
    duration = models.IntegerField(null=True, blank=True)  # For audio/video in seconds
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'quizhubapi'
    
    def __str__(self):
        if self.text:
            return self.text[:50]
        return f"{self.media_type.title()} Question - {self.topic.name}"
    
    def get_media_url(self):
        """Get the appropriate media URL"""
        if self.media_url:
            return self.media_url
        elif self.image:
            return self.image.url
        elif self.audio:
            return self.audio.url
        elif self.video:
            return self.video.url
        return None

class Answer(models.Model):
    MEDIA_TYPES = [
        ('text', 'Text Only'),
        ('image', 'Image'),
        ('audio', 'Audio'),
        ('video', 'Video'),
    ]
    
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255, blank=True)  # Made optional for media-only answers
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    # Multimedia fields
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, default='text')
    image = models.ImageField(upload_to='answers/images/', null=True, blank=True)
    audio = models.FileField(upload_to='answers/audio/', null=True, blank=True)
    video = models.FileField(upload_to='answers/videos/', null=True, blank=True)
    media_url = models.URLField(blank=True)  # For external media
    
    # Additional metadata
    media_description = models.TextField(max_length=200, blank=True)  # Alt text/description
    
    class Meta:
        app_label = 'quizhubapi'
        ordering = ['order']
    
    def __str__(self):
        if self.text:
            return f"{self.question.text[:30]} - {self.text}"
        return f"{self.question.text[:30]} - {self.media_type.title()} Answer"
    
    def get_media_url(self):
        """Get the appropriate media URL"""
        if self.media_url:
            return self.media_url
        elif self.image:
            return self.image.url
        elif self.audio:
            return self.audio.url
        elif self.video:
            return self.video.url
        return None

class Quiz(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='quizzes')
    topics = models.ManyToManyField(Topic, blank=True)
    questions = models.ManyToManyField(Question, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes_created')
    is_public = models.BooleanField(default=True)
    max_questions = models.IntegerField(default=10)
    time_limit = models.IntegerField(null=True, blank=True)  # seconds
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'quizhubapi'
        verbose_name_plural = 'Quizzes'
    
    def __str__(self):
        return self.title

# Solo Play Models
class QuizAttempt(models.Model):
    """Store individual solo quiz attempts"""
    STATUSES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts', null=True, blank=True)
    guest = models.ForeignKey('Guest', on_delete=models.CASCADE, null=True, blank=True)
    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE, related_name='attempts')
    
    # Performance metrics
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField()
    correct_answers = models.IntegerField(default=0)
    time_taken = models.IntegerField(null=True, blank=True)  # seconds
    percentage = models.FloatField(default=0.0)
    
    # Metadata
    status = models.CharField(max_length=15, choices=STATUSES, default='in_progress')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'quizhubapi'
        ordering = ['-started_at']
    
    def calculate_percentage(self):
        if self.total_questions > 0:
            self.percentage = (self.correct_answers / self.total_questions) * 100
        return self.percentage
    
    def award_points(self):
        """Calculate points based on performance"""
        base_points = self.correct_answers * 10
        
        # Bonus for perfect score
        if self.percentage == 100:
            base_points += 50
        
        # Bonus for speed (if completed in less than 60% of time limit)
        if self.quiz.time_limit and self.time_taken:
            if self.time_taken < (self.quiz.time_limit * 0.6):
                base_points += 25
        
        return base_points

class QuizAnswer(models.Model):
    """Store individual answers for quiz attempts"""
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    selected_answer = models.ForeignKey('Answer', on_delete=models.CASCADE, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    time_taken = models.IntegerField(null=True, blank=True)  # seconds for this question
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'quizhubapi'
        unique_together = ['attempt', 'question']

class Leaderboard(models.Model):
    """Different types of leaderboards"""
    TYPES = [
        ('global', 'Global'),
        ('category', 'Category'),
        ('quiz', 'Quiz Specific'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ]
    
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPES)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)
    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE, null=True, blank=True)
    
    # Auto-update timestamps
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'quizhubapi'

class LeaderboardEntry(models.Model):
    """Individual entries in leaderboards"""
    leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE, related_name='entries')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    guest = models.ForeignKey('Guest', on_delete=models.CASCADE, null=True, blank=True)
    
    score = models.IntegerField()
    rank = models.IntegerField()
    
    # Additional stats
    total_quizzes = models.IntegerField(default=0)
    average_percentage = models.FloatField(default=0.0)
    best_streak = models.IntegerField(default=0)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'quizhubapi'
        unique_together = ['leaderboard', 'user', 'guest']
        ordering = ['rank']