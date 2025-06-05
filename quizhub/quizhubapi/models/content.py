# quizhubapi/models/content.py
from django.db import models
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

class Question(models.Model):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False')
    ]
    
    STATUSES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    
    DIFFICULTY_CHOICES = [(i, str(i)) for i in range(1, 6)]
    
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(max_length=500)
    type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions_created')
    status = models.CharField(max_length=10, choices=STATUSES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'quizhubapi'
    
    def __str__(self):
        return self.text[:50]

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    class Meta:
        app_label = 'quizhubapi'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.question.text[:30]} - {self.text}"

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