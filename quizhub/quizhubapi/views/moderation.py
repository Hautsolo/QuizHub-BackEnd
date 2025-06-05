# quizhubapi/views/moderation.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ..models import Report, ModeratorAction, BannedWord, Notification
from ..serializers import ReportSerializer, NotificationSerializer

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Regular users can only see their own reports
        if not self.request.user.role in ['admin', 'moderator']:
            queryset = queryset.filter(reporter=self.request.user)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)
    
    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        if not request.user.role in ['admin', 'moderator']:
            return Response({'error': 'Permission denied'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        report = self.get_object()
        action = request.data.get('action')  # 'resolve', 'dismiss'
        resolution_notes = request.data.get('resolution_notes', '')
        
        if action not in ['resolve', 'dismiss']:
            return Response({'error': 'Invalid action'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        report.status = 'resolved' if action == 'resolve' else 'dismissed'
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.resolution_notes = resolution_notes
        report.save()
        
        # Create moderator action record
        ModeratorAction.objects.create(
            moderator=request.user,
            action_type=action,
            target_type='report',
            target_id=report.id,
            reason=resolution_notes
        )
        
        # Notify reporter
        Notification.objects.create(
            user=report.reporter,
            type='moderation_action',
            title='Report Updated',
            message=f'Your report has been {action}d by a moderator'
        )
        
        return Response({'message': f'Report {action}d successfully'})

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()  # Add this line
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'message': 'All notifications marked as read'})