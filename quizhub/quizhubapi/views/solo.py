# quizhubapi/views/solo.py - NEW FILE for Solo Play Features
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Count, Avg, Max, Q
from ..models import QuizAttempt, QuizAnswer, Leaderboard, LeaderboardEntry, User, Guest
from ..serializers import QuizAttemptSerializer, QuizAttemptCreateSerializer, LeaderboardSerializer

class QuizAttemptViewSet(viewsets.ModelViewSet):
    """Handle solo quiz attempts and scoring"""
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
        
        # Update category leaderboard
        if attempt.quiz and attempt.quiz.category:
            category_board, created = Leaderboard.objects.get_or_create(
                type='category',
                category=attempt.quiz.category,
                defaults={'name': f'{attempt.quiz.category.name} Leaderboard'}
            )
            
            # Similar logic for category leaderboard
            cat_entry, created = LeaderboardEntry.objects.get_or_create(
                leaderboard=category_board,
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
                cat_entry.score = user.points
                cat_entry.total_quizzes = QuizAttempt.objects.filter(
                    user=user, status='completed', quiz__category=attempt.quiz.category
                ).count()
                cat_entry.average_percentage = QuizAttempt.objects.filter(
                    user=user, status='completed', quiz__category=attempt.quiz.category
                ).aggregate(avg=Avg('percentage'))['avg'] or 0
                cat_entry.best_streak = user.streak_days
                cat_entry.save()
            
            self.recalculate_ranks(category_board)
    
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
        ).select_related('quiz').order_by('-completed_at')[:10]
        
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
    """Handle leaderboard data and rankings"""
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
    
    @action(detail=False, methods=['get'])
    def quiz_rankings(self, request):
        """Get quiz-specific leaderboard rankings"""
        quiz_id = request.query_params.get('quiz')
        if not quiz_id:
            return Response({'error': 'Quiz ID required'}, status=400)
        
        # Get top attempts for this specific quiz
        attempts = QuizAttempt.objects.filter(
            quiz_id=quiz_id, status='completed'
        ).select_related('user').order_by('-score', '-percentage')[:50]
        
        data = []
        for rank, attempt in enumerate(attempts, 1):
            data.append({
                'rank': rank,
                'user': attempt.user.id if attempt.user else None,
                'user_name': attempt.user.username if attempt.user else None,
                'score': attempt.score,
                'percentage': attempt.percentage,
                'time_taken': attempt.time_taken,
                'completed_at': attempt.completed_at
            })
        
        return Response({'entries': data})