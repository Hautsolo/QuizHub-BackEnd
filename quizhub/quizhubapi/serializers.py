# quizhubapi/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.db import models
from .models import *

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'profile_image', 
                 'points', 'streak_days', 'status', 'date_joined', 'last_login']
        read_only_fields = ['id', 'points', 'streak_days', 'date_joined', 'last_login']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    friends_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile_image', 'points', 
                 'streak_days', 'status', 'followers_count', 'following_count', 'friends_count']
    
    def get_followers_count(self, obj):
        return obj.followers.count()
    
    def get_following_count(self, obj):
        return obj.following.count()
    
    def get_friends_count(self, obj):
        return Friendship.objects.filter(
            models.Q(user1=obj, status='accepted') | 
            models.Q(user2=obj, status='accepted')
        ).count()

class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['id', 'session_id', 'display_name', 'created_at']

class CategorySerializer(serializers.ModelSerializer):
    topics_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image_url', 'is_active', 'topics_count']
    
    def get_topics_count(self, obj):
        return obj.topics.filter(is_active=True).count()

class TopicSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    questions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Topic
        fields = ['id', 'name', 'difficulty', 'category', 'category_name', 
                 'is_active', 'questions_count']
    
    def get_questions_count(self, obj):
        return obj.questions.filter(status='approved').count()

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct', 'order']

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    category_name = serializers.CharField(source='topic.category.name', read_only=True)
    creator_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'type', 'difficulty', 'topic', 'topic_name',
                 'category_name', 'status', 'created_by', 'creator_name', 
                 'created_at', 'answers']
    
    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        question = Question.objects.create(**validated_data)
        
        for answer_data in answers_data:
            Answer.objects.create(question=question, **answer_data)
        
        return question

class QuizSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    creator_name = serializers.CharField(source='created_by.username', read_only=True)
    questions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'category', 'category_name',
                 'creator_name', 'is_public', 'max_questions', 'time_limit',
                 'questions_count', 'created_at']
    
    def get_questions_count(self, obj):
        return obj.questions.count()

class MatchPlayerSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)
    user_data = UserSerializer(source='user', read_only=True)
    guest_data = GuestSerializer(source='guest', read_only=True)
    
    class Meta:
        model = MatchPlayer
        fields = ['id', 'user', 'guest', 'display_name', 'user_data', 'guest_data',
                 'score', 'position', 'is_ready', 'joined_at']

class MatchSerializer(serializers.ModelSerializer):
    players = MatchPlayerSerializer(many=True, read_only=True)
    creator_name = serializers.CharField(source='created_by.username', read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    players_count = serializers.SerializerMethodField()
    spectators_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Match
        fields = ['id', 'quiz', 'quiz_title', 'created_by', 'creator_name',
                 'is_private', 'allow_guests', 'max_players', 'status',
                 'room_code', 'players_count', 'spectators_count',
                 'created_at', 'started_at', 'ended_at', 'players']
    
    def get_players_count(self, obj):
        return obj.players.count()
    
    def get_spectators_count(self, obj):
        return obj.spectators.count()

class MatchSupportSerializer(serializers.ModelSerializer):
    supporter_name = serializers.SerializerMethodField()
    
    class Meta:
        model = MatchSupport
        fields = ['id', 'supporter_user', 'supporter_guest', 'supporter_name',
                 'supported_player', 'created_at']
    
    def get_supporter_name(self, obj):
        if obj.supporter_user:
            return obj.supporter_user.username
        return obj.supporter_guest.display_name if obj.supporter_guest else 'Anonymous'

class FriendRequestSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    receiver_name = serializers.CharField(source='receiver.username', read_only=True)
    
    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'sender_name', 'receiver_name',
                 'status', 'message', 'created_at']

class FriendshipSerializer(serializers.ModelSerializer):
    friend = serializers.SerializerMethodField()
    
    class Meta:
        model = Friendship
        fields = ['id', 'friend', 'status', 'created_at']
    
    def get_friend(self, obj):
        user = self.context['request'].user
        friend = obj.user2 if obj.user1 == user else obj.user1
        return UserSerializer(friend).data

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'type', 'title', 'message', 'data', 'is_read', 'created_at']

class ReportSerializer(serializers.ModelSerializer):
    reporter_name = serializers.CharField(source='reporter.username', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.username', read_only=True)
    
    class Meta:
        model = Report
        fields = ['id', 'reporter', 'reporter_name', 'target_type', 'target_id',
                 'reason', 'additional_info', 'status', 'reviewed_by', 'reviewed_by_name',
                 'reviewed_at', 'resolution_notes', 'created_at']

class LiveChatSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = LiveChat
        fields = ['id', 'match', 'user', 'guest', 'sender_name', 'message',
                 'is_system_message', 'is_deleted', 'created_at']