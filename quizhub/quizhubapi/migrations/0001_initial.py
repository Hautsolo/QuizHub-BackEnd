# Generated by Django 4.2.7 on 2025-06-01 06:06

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('role', models.CharField(choices=[('owner', 'Owner'), ('admin', 'Admin'), ('moderator', 'Moderator'), ('user', 'User')], default='user', max_length=10)),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='profiles/')),
                ('points', models.IntegerField(default=0)),
                ('streak_days', models.IntegerField(default=0)),
                ('last_streak_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('suspended', 'Suspended'), ('banned', 'Banned')], default='active', max_length=10)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True)),
                ('image_url', models.URLField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Guest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(max_length=255, unique=True)),
                ('display_name', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_private', models.BooleanField(default=False)),
                ('allow_guests', models.BooleanField(default=True)),
                ('max_players', models.IntegerField(default=2)),
                ('status', models.CharField(choices=[('waiting', 'Waiting'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='waiting', max_length=15)),
                ('room_code', models.CharField(blank=True, max_length=8, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches_created', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MatchPlayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(default=0)),
                ('position', models.IntegerField(blank=True, null=True)),
                ('is_ready', models.BooleanField(default=False)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('guest', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='quizhubapi.guest')),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='players', to='quizhubapi.match')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('match', 'user', 'guest')},
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=500)),
                ('type', models.CharField(choices=[('multiple_choice', 'Multiple Choice'), ('true_false', 'True/False')], max_length=20)),
                ('difficulty', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions_created', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('difficulty', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics', to='quizhubapi.category')),
            ],
            options={
                'unique_together': {('category', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_type', models.CharField(choices=[('user', 'User'), ('question', 'Question'), ('match', 'Match'), ('chat', 'Chat Message')], max_length=20)),
                ('target_id', models.IntegerField()),
                ('reason', models.TextField(max_length=500)),
                ('additional_info', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('reviewed', 'Reviewed'), ('resolved', 'Resolved'), ('dismissed', 'Dismissed')], default='pending', max_length=10)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('resolution_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports_made', to=settings.AUTH_USER_MODEL)),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reports_reviewed', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('is_public', models.BooleanField(default=True)),
                ('max_questions', models.IntegerField(default=10)),
                ('time_limit', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quizzes', to='quizhubapi.category')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quizzes_created', to=settings.AUTH_USER_MODEL)),
                ('questions', models.ManyToManyField(blank=True, to='quizhubapi.question')),
                ('topics', models.ManyToManyField(blank=True, to='quizhubapi.topic')),
            ],
            options={
                'verbose_name_plural': 'Quizzes',
            },
        ),
        migrations.AddField(
            model_name='question',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='quizhubapi.topic'),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('friend_request', 'Friend Request'), ('match_invite', 'Match Invite'), ('friend_playing', 'Friend Playing'), ('match_started', 'Match Started'), ('support_received', 'Support Received'), ('moderation_action', 'Moderation Action'), ('quiz_approved', 'Quiz Approved'), ('quiz_rejected', 'Quiz Rejected')], max_length=20)),
                ('title', models.CharField(max_length=100)),
                ('message', models.TextField()),
                ('data', models.JSONField(blank=True, default=dict)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ModeratorAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[('warn', 'Warn'), ('suspend', 'Suspend'), ('ban', 'Ban'), ('delete', 'Delete Content'), ('approve', 'Approve'), ('reject', 'Reject')], max_length=10)),
                ('target_type', models.CharField(choices=[('user', 'User'), ('question', 'Question'), ('match', 'Match'), ('chat', 'Chat Message')], max_length=20)),
                ('target_id', models.IntegerField()),
                ('reason', models.TextField(max_length=500)),
                ('duration_hours', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('moderator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='moderator_actions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MatchInvite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=32, unique=True)),
                ('expires_at', models.DateTimeField()),
                ('max_uses', models.IntegerField(default=1)),
                ('use_count', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invites', to='quizhubapi.match')),
            ],
        ),
        migrations.AddField(
            model_name='match',
            name='quiz',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='quizhubapi.quiz'),
        ),
        migrations.CreateModel(
            name='LiveChat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(max_length=500)),
                ('is_system_message', models.BooleanField(default=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('guest', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='quizhubapi.guest')),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_messages', to='quizhubapi.match')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='BannedWord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=50, unique=True)),
                ('is_exact_match', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('banned_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('is_correct', models.BooleanField(default=False)),
                ('order', models.IntegerField(default=0)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='quizhubapi.question')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Spectator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('guest', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='quizhubapi.guest')),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='spectators', to='quizhubapi.match')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('match', 'user', 'guest')},
            },
        ),
        migrations.CreateModel(
            name='MatchSupport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supports', to='quizhubapi.match')),
                ('supported_player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quizhubapi.matchplayer')),
                ('supporter_guest', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='quizhubapi.guest')),
                ('supporter_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('match', 'supporter_user', 'supporter_guest')},
            },
        ),
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('blocked', 'Blocked')], default='pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friendships_initiated', to=settings.AUTH_USER_MODEL)),
                ('user2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friendships_received', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user1', 'user2')},
            },
        ),
        migrations.CreateModel(
            name='FriendRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=10)),
                ('message', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_requests', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('sender', 'receiver')},
            },
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('follower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL)),
                ('following', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('follower', 'following')},
            },
        ),
    ]
