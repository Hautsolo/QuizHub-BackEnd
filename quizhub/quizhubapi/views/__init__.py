# quizhubapi/views/__init__.py

# Authentication views
from .auth import RegisterView, LoginView, RefreshTokenView, LogoutView, ProfileView

# User views
from .user import UserViewSet

# Content views  
from .content import CategoryViewSet, TopicViewSet, QuestionViewSet, QuizViewSet

# Match views
from .match import (
    MatchViewSet, JoinMatchView, LeaveMatchView, 
    JoinMatchByCodeView, SupportPlayerView, CreateGuestView
)

# Social views
from .social import (
    FriendListView, FriendRequestListView, SendFriendRequestView,
    RespondFriendRequestView, FollowUserView, UnfollowUserView
)

# Moderation views
from .moderation import ReportViewSet, NotificationViewSet

__all__ = [
    # Auth views
    'RegisterView', 'LoginView', 'RefreshTokenView', 'LogoutView', 'ProfileView',
    
    # ViewSets
    'UserViewSet', 'CategoryViewSet', 'TopicViewSet', 'QuestionViewSet', 
    'QuizViewSet', 'MatchViewSet', 'NotificationViewSet', 'ReportViewSet',
    
    # Match views
    'JoinMatchView', 'LeaveMatchView', 'JoinMatchByCodeView', 
    'SupportPlayerView', 'CreateGuestView',
    
    # Social views
    'FriendListView', 'FriendRequestListView', 'SendFriendRequestView',
    'RespondFriendRequestView', 'FollowUserView', 'UnfollowUserView',
]