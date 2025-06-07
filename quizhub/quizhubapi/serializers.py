# quizhubapi/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.db import models
from django.utils import timezone
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

class MediaFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MediaFile
        fields = ['id', 'file', 'file_url', 'media_type', 'original_filename', 
                 'file_size', 'mime_type', 'duration', 'width', 'height', 'uploaded_at']
        read_only_fields = ['uploaded_by', 'uploaded_at']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)

class AnswerSerializer(serializers.ModelSerializer):
    media_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct', 'order', 'media_type', 
                 'image', 'audio', 'video', 'media_url', 'media_description']
    
    def get_media_url(self, obj):
        return obj.get_media_url()

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    category_name = serializers.CharField(source='topic.category.name', read_only=True)
    creator_name = serializers.CharField(source='created_by.username', read_only=True)
    media_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'type', 'difficulty', 'topic', 'topic_name',
                 'category_name', 'status', 'created_by', 'creator_name', 
                 'created_at', 'answers', 'media_type', 'image', 'audio', 'video',
                 'media_url', 'media_description', 'duration']
    
    def get_media_url(self, obj):
        return obj.get_media_url()
    
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

# Solo Play Serializers
class QuizAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAnswer
        fields = ['question', 'selected_answer', 'is_correct', 'time_taken']

class QuizAttemptSerializer(serializers.ModelSerializer):
    answers = QuizAnswerSerializer(many=True, read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    user_display = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'quiz_title', 'user', 'guest', 'user_display',
                 'score', 'total_questions', 'correct_answers', 'percentage',
                 'time_taken', 'status', 'started_at', 'completed_at', 'answers']
        read_only_fields = ['percentage']
    
    def get_user_display(self, obj):
        if obj.user:
            return obj.user.username
        elif obj.guest:
            return obj.guest.display_name
        return 'Anonymous'

class QuizAttemptCreateSerializer(serializers.ModelSerializer):
    answers = serializers.ListField(write_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = ['quiz', 'answers', 'time_taken']
    
    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        user = self.context['request'].user if self.context['request'].user.is_authenticated else None
        
        # Create the attempt
        attempt = QuizAttempt.objects.create(
            user=user,
            total_questions=len(answers_data),
            **validated_data
        )
        
        # Create individual answers
        correct_count = 0
        for answer_data in answers_data:
            is_correct = answer_data.get('is_correct', False)
            if is_correct:
                correct_count += 1
                
            QuizAnswer.objects.create(
                attempt=attempt,
                question_id=answer_data['question_id'],
                selected_answer_id=answer_data.get('selected_answer_id'),
                is_correct=is_correct,
                time_taken=answer_data.get('time_taken')
            )
        
        # Update attempt stats
        attempt.correct_answers = correct_count
        attempt.percentage = attempt.calculate_percentage()
        attempt.score = attempt.award_points()
        attempt.status = 'completed'
        attempt.completed_at = timezone.now()
        attempt.save()
        
        # Award points to user
        if attempt.user:
            attempt.user.points += attempt.score
            attempt.user.save()
        
        return attempt

class LeaderboardEntrySerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    guest_name = serializers.CharField(source='guest.display_name', read_only=True)
    
    class Meta:
        model = LeaderboardEntry
        fields = ['rank', 'user', 'guest', 'user_name', 'guest_name', 'score', 
                 'total_quizzes', 'average_percentage', 'best_streak']
    
    def get_user_name(self, obj):
        return obj.user.username if obj.user else None

class LeaderboardSerializer(serializers.ModelSerializer):
    entries = LeaderboardEntrySerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    
    class Meta:
        model = Leaderboard
        fields = ['id', 'name', 'type', 'category', 'category_name', 
                 'quiz', 'quiz_title', 'entries', 'last_updated']

# Match Serializers
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

# Social Serializers
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

# Notification Serializers
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'type', 'title', 'message', 'data', 'is_read', 'created_at']

# Moderation Serializers
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