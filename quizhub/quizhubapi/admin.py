from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'points', 'status', 'date_joined']
    list_filter = ['role', 'status', 'date_joined']
    search_fields = ['username', 'email']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('role', 'profile_image', 'points', 'streak_days', 
                      'last_streak_date', 'status')
        }),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'difficulty', 'is_active']
    list_filter = ['category', 'difficulty', 'is_active']
    search_fields = ['name']

@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'media_type', 'file_size', 'uploaded_by', 'uploaded_at']
    list_filter = ['media_type', 'uploaded_at']
    search_fields = ['original_filename', 'uploaded_by__username']
    readonly_fields = ['file_size', 'mime_type', 'width', 'height', 'duration']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'topic', 'type', 'media_type', 'difficulty', 'status', 'created_by']
    list_filter = ['type', 'media_type', 'difficulty', 'status', 'topic__category']
    search_fields = ['text']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['text', 'question', 'media_type', 'is_correct', 'order']
    list_filter = ['media_type', 'is_correct']
    search_fields = ['text']

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'created_by', 'is_public', 'created_at']
    list_filter = ['category', 'is_public']
    search_fields = ['title']

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score', 'percentage', 'status', 'started_at']
    list_filter = ['status', 'quiz__category', 'started_at']
    search_fields = ['user__username', 'quiz__title']
    readonly_fields = ['percentage']

@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'is_correct', 'answered_at']
    list_filter = ['is_correct', 'answered_at']

@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'category', 'quiz', 'last_updated']
    list_filter = ['type', 'category']

@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = ['leaderboard', 'user', 'rank', 'score', 'updated_at']
    list_filter = ['leaderboard__type', 'rank']
    ordering = ['leaderboard', 'rank']

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['id', 'quiz', 'created_by', 'status', 'room_code', 'created_at']
    list_filter = ['status', 'is_private', 'allow_guests']
    search_fields = ['room_code']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'target_type', 'target_id', 'status', 'created_at']
    list_filter = ['target_type', 'status']
    search_fields = ['reason']