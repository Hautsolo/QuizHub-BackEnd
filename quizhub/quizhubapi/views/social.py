from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from ..models import User, Follow, Friendship, FriendRequest, Notification
from ..serializers import (UserProfileSerializer, FriendRequestSerializer, 
                          FriendshipSerializer)

class FriendListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        friendships = Friendship.objects.filter(
            (Q(user1=request.user) | Q(user2=request.user)) & 
            Q(status='accepted')
        )
        
        serializer = FriendshipSerializer(
            friendships, many=True, context={'request': request}
        )
        return Response(serializer.data)

class FriendRequestListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get incoming friend requests
        incoming = FriendRequest.objects.filter(
            receiver=request.user, status='pending'
        )
        
        # Get outgoing friend requests
        outgoing = FriendRequest.objects.filter(
            sender=request.user, status='pending'
        )
        
        return Response({
            'incoming': FriendRequestSerializer(incoming, many=True).data,
            'outgoing': FriendRequestSerializer(outgoing, many=True).data
        })

class SendFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        receiver_id = request.data.get('receiver_id')
        message = request.data.get('message', '')
        
        if not receiver_id:
            return Response({'error': 'Receiver ID is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        receiver = get_object_or_404(User, id=receiver_id)
        
        if receiver == request.user:
            return Response({'error': 'Cannot send friend request to yourself'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Check if request already exists
        if FriendRequest.objects.filter(
            sender=request.user, receiver=receiver
        ).exists():
            return Response({'error': 'Friend request already sent'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already friends
        if Friendship.objects.filter(
            (Q(user1=request.user, user2=receiver) | 
             Q(user1=receiver, user2=request.user)) &
            Q(status='accepted')
        ).exists():
            return Response({'error': 'Already friends'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Create friend request
        friend_request = FriendRequest.objects.create(
            sender=request.user,
            receiver=receiver,
            message=message
        )
        
        # Create notification
        Notification.objects.create(
            user=receiver,
            type='friend_request',
            title='New Friend Request',
            message=f'{request.user.username} sent you a friend request',
            data={'friend_request_id': friend_request.id}
        )
        
        return Response({'message': 'Friend request sent successfully'})

class RespondFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        action = request.data.get('action')  # 'accept' or 'reject'
        
        if action not in ['accept', 'reject']:
            return Response({'error': 'Invalid action'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        friend_request = get_object_or_404(
            FriendRequest, id=pk, receiver=request.user, status='pending'
        )
        
        friend_request.status = 'accepted' if action == 'accept' else 'rejected'
        friend_request.save()
        
        if action == 'accept':
            # Create friendship
            Friendship.objects.create(
                user1=friend_request.sender,
                user2=friend_request.receiver,
                status='accepted'
            )
            
            # Create notification for sender
            Notification.objects.create(
                user=friend_request.sender,
                type='friend_request',
                title='Friend Request Accepted',
                message=f'{request.user.username} accepted your friend request'
            )
        
        return Response({'message': f'Friend request {action}ed successfully'})

class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        user_to_follow = get_object_or_404(User, id=user_id)
        
        if user_to_follow == request.user:
            return Response({'error': 'Cannot follow yourself'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )
        
        if created:
            # Create notification
            Notification.objects.create(
                user=user_to_follow,
                type='friend_playing',
                title='New Follower',
                message=f'{request.user.username} started following you'
            )
            return Response({'message': 'Successfully followed user'})
        else:
            return Response({'error': 'Already following this user'}, 
                          status=status.HTTP_400_BAD_REQUEST)

class UnfollowUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        user_to_unfollow = get_object_or_404(User, id=user_id)
        
        try:
            follow = Follow.objects.get(
                follower=request.user,
                following=user_to_unfollow
            )
            follow.delete()
            return Response({'message': 'Successfully unfollowed user'})
        except Follow.DoesNotExist:
            return Response({'error': 'Not following this user'}, 
                          status=status.HTTP_400_BAD_REQUEST)