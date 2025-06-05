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

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'topic', 'type', 'difficulty', 'status', 'created_by']
    list_filter = ['type', 'difficulty', 'status', 'topic__category']
    search_fields = ['text']

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'created_by', 'is_public', 'created_at']
    list_filter = ['category', 'is_public']
    search_fields = ['title']

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