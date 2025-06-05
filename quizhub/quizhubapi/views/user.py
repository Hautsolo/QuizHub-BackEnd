# quizhubapi/views/user.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from ..models import User
from ..serializers import UserSerializer, UserProfileSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(status='active')
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) | 
                Q(email__icontains=search)
            )
        return queryset
    
    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        user = self.get_object()
        serializer = UserProfileSerializer(user, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        users = self.get_queryset().order_by('-points')[:50]
        serializer = UserProfileSerializer(users, many=True, context={'request': request})
        return Response(serializer.data)