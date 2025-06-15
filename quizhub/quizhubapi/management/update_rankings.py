# quizhubapi/management/commands/update_rankings.py
from django.core.management.base import BaseCommand
from quizhubapi.utils.rankings import update_user_rankings

class Command(BaseCommand):
    help = 'Update user rankings (global and country)'

    def handle(self, *args, **options):
        self.stdout.write('Updating user rankings...')
        update_user_rankings()
        self.stdout.write(self.style.SUCCESS('Successfully updated all user rankings'))