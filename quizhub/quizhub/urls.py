# quizhub/quizhub/urls.py - Updated with Missing Endpoints
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

# Import ViewSets
from quizhubapi.views.user import UserViewSet
from quizhubapi.views.content import CategoryViewSet, TopicViewSet, QuestionViewSet, QuizViewSet
from quizhubapi.views.match import MatchViewSet
from quizhubapi.views.moderation import ReportViewSet, NotificationViewSet

# Import new Solo Play ViewSets
from quizhubapi.views.solo import QuizAttemptViewSet, LeaderboardViewSet

# Import API Views
from quizhubapi.views.auth import RegisterView, LoginView, RefreshTokenView, LogoutView, ProfileView
from quizhubapi.views.social import (
    FriendListView, FriendRequestListView, SendFriendRequestView, 
    RespondFriendRequestView, FollowUserView, UnfollowUserView
)
from quizhubapi.views.match import (
    JoinMatchView, LeaveMatchView, SupportPlayerView, 
    JoinMatchByCodeView, CreateGuestView
)

# Create router and register ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'topics', TopicViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'quizzes', QuizViewSet)
router.register(r'matches', MatchViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'reports', ReportViewSet)

# NEW: Register Solo Play ViewSets
router.register(r'quiz-attempts', QuizAttemptViewSet, basename='quizattempt')
router.register(r'leaderboards', LeaderboardViewSet, basename='leaderboard')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Include router URLs under /api/
    path('api/', include(router.urls)),
    
    # Authentication endpoints
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/profile/', ProfileView.as_view(), name='profile'),
    
    # Social endpoints
    path('api/social/friends/', FriendListView.as_view(), name='friends'),
    path('api/social/friend-requests/', FriendRequestListView.as_view(), name='friend-requests'),
    path('api/social/send-friend-request/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('api/social/respond-friend-request/<int:pk>/', RespondFriendRequestView.as_view(), name='respond-friend-request'),
    path('api/social/follow/<int:user_id>/', FollowUserView.as_view(), name='follow-user'),
    path('api/social/unfollow/<int:user_id>/', UnfollowUserView.as_view(), name='unfollow-user'),
    
    # Match endpoints
    path('api/matches/<int:match_id>/join/', JoinMatchView.as_view(), name='join-match'),
    path('api/matches/<int:match_id>/leave/', LeaveMatchView.as_view(), name='leave-match'),
    path('api/matches/<int:match_id>/support/<int:player_id>/', SupportPlayerView.as_view(), name='support-player'),
    path('api/matches/join-by-code/', JoinMatchByCodeView.as_view(), name='join-by-code'),
    
    # Guest endpoints
    path('api/guest/create/', CreateGuestView.as_view(), name='create-guest'),
    
    # Allauth URLs
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)