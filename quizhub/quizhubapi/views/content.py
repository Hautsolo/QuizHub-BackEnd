from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import Q
from ..models import Category, Topic, Question, Answer, Quiz
from ..serializers import (CategorySerializer, TopicSerializer, 
                          QuestionSerializer, QuizSerializer)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Topic.objects.filter(is_active=True)
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        return queryset

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.filter(status='approved')
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        topic = self.request.query_params.get('topic')
        difficulty = self.request.query_params.get('difficulty')
        
        if topic:
            queryset = queryset.filter(topic_id=topic)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_questions(self, request):
        questions = Question.objects.filter(created_by=request.user)
        serializer = self.get_serializer(questions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        if not request.user.role in ['admin', 'moderator']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        questions = Question.objects.filter(status='pending')
        serializer = self.get_serializer(questions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        if not request.user.role in ['admin', 'moderator']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        question = self.get_object()
        question.status = 'approved'
        question.save()
        return Response({'message': 'Question approved'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        if not request.user.role in ['admin', 'moderator']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        question = self.get_object()
        question.status = 'rejected'
        question.save()
        return Response({'message': 'Question rejected'})

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.filter(is_public=True)
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        
        if category:
            queryset = queryset.filter(category_id=category)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_quizzes(self, request):
        quizzes = Quiz.objects.filter(created_by=request.user)
        serializer = self.get_serializer(quizzes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        quiz = self.get_object()
        questions = quiz.questions.filter(status='approved')[:quiz.max_questions]
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)