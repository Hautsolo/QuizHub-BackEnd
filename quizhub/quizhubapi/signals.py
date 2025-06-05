# quizhubapi/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import MatchPlayer, LiveChat, MatchSupport

@receiver(post_save, sender=MatchPlayer)
def player_joined_match(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        # Only send if channel layer is properly configured
        if channel_layer is not None:
            try:
                async_to_sync(channel_layer.group_send)(
                    f'match_{instance.match.id}',
                    {
                        'type': 'player_joined',
                        'data': {
                            'player_id': instance.id,
                            'display_name': instance.display_name,
                            'players_count': instance.match.players.count()
                        }
                    }
                )
            except Exception:
                # Silently ignore channel layer errors during fixture loading
                pass

@receiver(post_delete, sender=MatchPlayer)
def player_left_match(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    # Only send if channel layer is properly configured
    if channel_layer is not None:
        try:
            async_to_sync(channel_layer.group_send)(
                f'match_{instance.match.id}',
                {
                    'type': 'player_left',
                    'data': {
                        'player_id': instance.id,
                        'display_name': instance.display_name,
                        'players_count': instance.match.players.count()
                    }
                }
            )
        except Exception:
            # Silently ignore channel layer errors during fixture loading
            pass