# Add to quizhubapi/views/content.py or create quizhubapi/views/media.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import default_storage
from PIL import Image
import os
import mimetypes
from ..models import MediaFile
from ..serializers import MediaFileSerializer

class MediaFileViewSet(viewsets.ModelViewSet):
    queryset = MediaFile.objects.all()
    serializer_class = MediaFileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        # Users can only see their own uploaded media
        return MediaFile.objects.filter(uploaded_by=self.request.user)
    
    def create(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file type
        mime_type, _ = mimetypes.guess_type(file_obj.name)
        if not mime_type:
            return Response({'error': 'Could not determine file type'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Determine media type
        if mime_type.startswith('image/'):
            media_type = 'image'
            max_size = 10 * 1024 * 1024  # 10MB for images
        elif mime_type.startswith('audio/'):
            media_type = 'audio'
            max_size = 50 * 1024 * 1024  # 50MB for audio
        elif mime_type.startswith('video/'):
            media_type = 'video'
            max_size = 100 * 1024 * 1024  # 100MB for video
        else:
            return Response({'error': 'Unsupported file type'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check file size
        if file_obj.size > max_size:
            return Response({
                'error': f'File too large. Maximum size for {media_type} is {max_size // (1024*1024)}MB'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create media file record
        media_file = MediaFile(
            file=file_obj,
            media_type=media_type,
            original_filename=file_obj.name,
            file_size=file_obj.size,
            mime_type=mime_type,
            uploaded_by=request.user
        )
        
        # Get additional metadata for images
        if media_type == 'image':
            try:
                image = Image.open(file_obj)
                media_file.width, media_file.height = image.size
            except Exception:
                pass
        
        media_file.save()
        
        serializer = self.get_serializer(media_file, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def upload_question_media(self, request):
        """Upload media specifically for questions"""
        return self.create(request)
    
    @action(detail=False, methods=['post'])
    def upload_answer_media(self, request):
        """Upload media specifically for answers"""
        return self.create(request)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get media files by type"""
        media_type = request.query_params.get('type')
        if media_type in ['image', 'audio', 'video']:
            media_files = self.get_queryset().filter(media_type=media_type)
            serializer = self.get_serializer(media_files, many=True, context={'request': request})
            return Response(serializer.data)
        return Response({'error': 'Invalid media type'}, status=status.HTTP_400_BAD_REQUEST)