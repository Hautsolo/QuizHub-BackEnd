# quizhubapi/views/content.py - Add Missing Endpoints

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import Q, Count, Avg, Max
from ..models import Category, Topic, Question, Answer, Quiz, QuizAttempt, Leaderboard, LeaderboardEntry
from ..serializers import (CategorySerializer, TopicSerializer, 
                          QuestionSerializer, QuizSerializer, QuizAttemptCreateSerializer, 
                          QuizAttemptSerializer, LeaderboardSerializer)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().annotate(
            topics_count=Count('topics', filter=Q(topics__is_active=True))
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.filter(is_public=True)
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('category', 'created_by')
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        limit = self.request.query_params.get('limit')
        
        if category:
            queryset = queryset.filter(category_id=category)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
        
        queryset = queryset.order_by('-created_at')
        
        if limit:
            try:
                limit = int(limit)
                queryset = queryset[:limit]
            except (ValueError, TypeError):
                pass
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_quizzes(self, request):
        """Get current user's quizzes"""
        quizzes = Quiz.objects.filter(created_by=request.user).order_by('-created_at')
        serializer = self.get_serializer(quizzes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """Get questions for a specific quiz"""
        quiz = self.get_object()
        questions = quiz.questions.filter(status='approved').order_by('?')[:quiz.max_questions]
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

# ADD TO quizhubapi/views/solo.py - NEW FILE
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Count, Avg, Q
from ..models import QuizAttempt, QuizAnswer, Leaderboard, LeaderboardEntry, User, Guest
from ..serializers import QuizAttemptSerializer, QuizAttemptCreateSerializer, LeaderboardSerializer

class QuizAttemptViewSet(viewsets.ModelViewSet):
    queryset = QuizAttempt.objects.all()
    serializer_class = QuizAttemptSerializer
    permission_classes = [AllowAny]  # Allow guests
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return QuizAttempt.objects.filter(user=self.request.user).order_by('-started_at')
        return QuizAttempt.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return QuizAttemptCreateSerializer
        return QuizAttemptSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new quiz attempt (submit quiz results)"""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            attempt = serializer.save()
            
            # Update user points and streak
            if attempt.user:
                attempt.user.points += attempt.score
                attempt.user.update_streak()
                attempt.user.save()
            
            # Update leaderboards
            self.update_leaderboards(attempt)
            
            return Response(QuizAttemptSerializer(attempt).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update_leaderboards(self, attempt):
        """Update leaderboard entries after quiz completion"""
        user = attempt.user
        if not user:
            return
        
        # Update global leaderboard
        global_board, created = Leaderboard.objects.get_or_create(
            type='global',
            defaults={'name': 'Global Leaderboard'}
        )
        
        entry, created = LeaderboardEntry.objects.get_or_create(
            leaderboard=global_board,
            user=user,
            defaults={
                'score': user.points,
                'rank': 1,
                'total_quizzes': 1,
                'average_percentage': attempt.percentage,
                'best_streak': user.streak_days
            }
        )
        
        if not created:
            # Update existing entry
            entry.score = user.points
            entry.total_quizzes = QuizAttempt.objects.filter(
                user=user, status='completed'
            ).count()
            entry.average_percentage = QuizAttempt.objects.filter(
                user=user, status='completed'
            ).aggregate(avg=Avg('percentage'))['avg'] or 0
            entry.best_streak = user.streak_days
            entry.save()
        
        # Recalculate ranks
        self.recalculate_ranks(global_board)
    
    def recalculate_ranks(self, leaderboard):
        """Recalculate ranks for a leaderboard"""
        entries = LeaderboardEntry.objects.filter(
            leaderboard=leaderboard
        ).order_by('-score', '-average_percentage')
        
        for rank, entry in enumerate(entries, 1):
            entry.rank = rank
            entry.save(update_fields=['rank'])
    
    @action(detail=False, methods=['get'])
    def my_attempts(self, request):
        """Get current user's quiz attempts"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=401)
        
        attempts = QuizAttempt.objects.filter(
            user=request.user, status='completed'
        ).order_by('-completed_at')[:10]
        
        serializer = QuizAttemptSerializer(attempts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user's quiz statistics"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=401)
        
        attempts = QuizAttempt.objects.filter(
            user=request.user, status='completed'
        )
        
        stats = {
            'total_attempts': attempts.count(),
            'average_score': attempts.aggregate(avg=Avg('percentage'))['avg'] or 0,
            'total_points': request.user.points,
            'best_score': attempts.aggregate(max=Max('percentage'))['max'] or 0,
            'current_streak': request.user.streak_days,
        }
        
        return Response(stats)

class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Leaderboard.objects.all()
    serializer_class = LeaderboardSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def global_rankings(self, request):
        """Get global leaderboard rankings"""
        try:
            global_board = Leaderboard.objects.get(type='global')
            entries = LeaderboardEntry.objects.filter(
                leaderboard=global_board
            ).select_related('user').order_by('rank')[:50]
            
            data = []
            for entry in entries:
                data.append({
                    'rank': entry.rank,
                    'user': entry.user.id if entry.user else None,
                    'user_name': entry.user.username if entry.user else None,
                    'score': entry.score,
                    'total_quizzes': entry.total_quizzes,
                    'average_percentage': entry.average_percentage,
                    'best_streak': entry.best_streak
                })
            
            return Response({'entries': data})
        except Leaderboard.DoesNotExist:
            return Response({'entries': []})
    
    @action(detail=False, methods=['get'])
    def category_rankings(self, request):
        """Get category-specific leaderboard rankings"""
        category_id = request.query_params.get('category')
        if not category_id:
            return Response({'error': 'Category ID required'}, status=400)
        
        try:
            category_board = Leaderboard.objects.get(
                type='category', category_id=category_id
            )
            entries = LeaderboardEntry.objects.filter(
                leaderboard=category_board
            ).select_related('user').order_by('rank')[:50]
            
            data = []
            for entry in entries:
                data.append({
                    'rank': entry.rank,
                    'user': entry.user.id if entry.user else None,
                    'user_name': entry.user.username if entry.user else None,
                    'score': entry.score,
                    'total_quizzes': entry.total_quizzes,
                    'average_percentage': entry.average_percentage,
                    'best_streak': entry.best_streak
                })
            
            return Response({'entries': data})
        except Leaderboard.DoesNotExist:
            return Response({'entries': []})

# ADD TO quizhubapi/views/match.py - UPDATE EXISTING
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import models
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ..models import Match, MatchPlayer, Guest, MatchInvite, Quiz
from ..serializers import MatchSerializer, GuestSerializer

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [AllowAny]  # Allow guests to view
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'quiz', 'created_by'
        ).prefetch_related('players')
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Show public matches and user's own matches
        if self.request.user.is_authenticated and not self.request.user.role in ['admin', 'moderator']:
            queryset = queryset.filter(
                models.Q(is_private=False) | 
                models.Q(created_by=self.request.user)
            )
        elif not self.request.user.is_authenticated:
            # For guests, only show public matches
            queryset = queryset.filter(is_private=False)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=401)
        serializer.save(created_by=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Create a new match"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Validate quiz exists
        quiz_id = request.data.get('quiz')
        if quiz_id:
            try:
                quiz = Quiz.objects.get(id=quiz_id)
                if not quiz.is_public and quiz.created_by != request.user:
                    return Response({'error': 'Quiz not accessible'}, status=status.HTTP_403_FORBIDDEN)
            except Quiz.DoesNotExist:
                return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            match = serializer.save(created_by=request.user)
            
            # Auto-join creator to the match
            MatchPlayer.objects.create(
                match=match,
                user=request.user,
                is_ready=True
            )
            
            return Response(
                MatchSerializer(match, context={'request': request}).data, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)