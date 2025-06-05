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
from ..models import Match, MatchPlayer, Guest, MatchInvite
from ..serializers import MatchSerializer, GuestSerializer

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Show public matches and user's own matches
        if not self.request.user.role in ['admin', 'moderator']:
            queryset = queryset.filter(
                models.Q(is_private=False) | 
                models.Q(created_by=self.request.user)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        match = self.get_object()
        if match.created_by != request.user:
            return Response({'error': 'Only match creator can start the match'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        if match.status != 'waiting':
            return Response({'error': 'Match is not in waiting state'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        match.start_match()
        
        # Notify via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'match_{match.id}',
            {
                'type': 'match_started',
                'data': MatchSerializer(match).data
            }
        )
        
        return Response({'message': 'Match started'})
    
    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        match = self.get_object()
        if match.created_by != request.user and not request.user.role in ['admin', 'moderator']:
            return Response({'error': 'Permission denied'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        match.end_match()
        return Response({'message': 'Match ended'})

class JoinMatchView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, match_id):
        match = get_object_or_404(Match, id=match_id)
        
        if match.status != 'waiting':
            return Response({'error': 'Match is not accepting players'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        if match.players.count() >= match.max_players:
            return Response({'error': 'Match is full'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user is already in match
        if match.players.filter(user=request.user).exists():
            return Response({'error': 'Already in this match'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Add player to match
        player = MatchPlayer.objects.create(
            match=match,
            user=request.user
        )
        
        # Notify via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'match_{match.id}',
            {
                'type': 'player_joined',
                'data': {
                    'player_id': player.id,
                    'display_name': player.display_name,
                    'players_count': match.players.count()
                }
            }
        )
        
        return Response({'message': 'Joined match successfully'})

class LeaveMatchView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, match_id):
        match = get_object_or_404(Match, id=match_id)
        
        try:
            player = match.players.get(user=request.user)
            player.delete()
            
            # Notify via WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'match_{match.id}',
                {
                    'type': 'player_left',
                    'data': {
                        'user_id': request.user.id,
                        'display_name': request.user.username,
                        'players_count': match.players.count()
                    }
                }
            )
            
            return Response({'message': 'Left match successfully'})
        except MatchPlayer.DoesNotExist:
            return Response({'error': 'Not in this match'}, 
                          status=status.HTTP_400_BAD_REQUEST)

class JoinMatchByCodeView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        room_code = request.data.get('room_code')
        guest_name = request.data.get('guest_name')
        
        if not room_code:
            return Response({'error': 'Room code is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            match = Match.objects.get(room_code=room_code.upper())
        except Match.DoesNotExist:
            return Response({'error': 'Invalid room code'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        if match.status != 'waiting':
            return Response({'error': 'Match is not accepting players'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        if match.players.count() >= match.max_players:
            return Response({'error': 'Match is full'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Handle guest or authenticated user
        if request.user.is_authenticated:
            # Check if user is already in match
            if match.players.filter(user=request.user).exists():
                return Response({'error': 'Already in this match'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            player = MatchPlayer.objects.create(
                match=match,
                user=request.user
            )
        else:
            if not match.allow_guests:
                return Response({'error': 'Guests not allowed in this match'}, 
                              status=status.HTTP_403_FORBIDDEN)
            
            if not guest_name:
                return Response({'error': 'Guest name is required'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Create guest
            guest = Guest.objects.create(
                session_id=request.session.session_key or 'anonymous',
                display_name=guest_name
            )
            
            player = MatchPlayer.objects.create(
                match=match,
                guest=guest
            )
        
        return Response({
            'message': 'Joined match successfully',
            'match': MatchSerializer(match).data
        })

class SupportPlayerView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, match_id, player_id):
        match = get_object_or_404(Match, id=match_id)
        player = get_object_or_404(MatchPlayer, id=player_id, match=match)
        
        # Create or update support
        from ..models import MatchSupport
        guest_id = request.data.get('guest_id')
        guest = None
        
        if guest_id:
            try:
                guest = Guest.objects.get(id=guest_id)
            except Guest.DoesNotExist:
                pass
        
        # Remove existing support from this user/guest
        MatchSupport.objects.filter(
            match=match,
            supporter_user=request.user if request.user.is_authenticated else None,
            supporter_guest=guest
        ).delete()
        
        # Add new support
        MatchSupport.objects.create(
            match=match,
            supporter_user=request.user if request.user.is_authenticated else None,
            supporter_guest=guest,
            supported_player=player
        )
        
        return Response({'message': 'Support added successfully'})

class CreateGuestView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        display_name = request.data.get('display_name')
        
        if not display_name:
            return Response({'error': 'Display name is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        guest = Guest.objects.create(
            session_id=request.session.session_key or 'anonymous',
            display_name=display_name
        )
        
        serializer = GuestSerializer(guest)
        return Response(serializer.data, status=status.HTTP_201_CREATED)