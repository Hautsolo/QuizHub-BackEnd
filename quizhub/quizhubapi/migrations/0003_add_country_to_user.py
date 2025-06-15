# Create a new migration file: quizhubapi/migrations/0003_add_country_to_user.py

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizhubapi', '0002_leaderboard_answer_audio_answer_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='country',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='country_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='country_rank',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='global_rank',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='leaderboard',
            name='country',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
    ]