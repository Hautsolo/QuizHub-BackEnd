# quizhubapi/utils/rankings.py
from django.db.models import Count, Q
from ..models import User, LeaderboardEntry, Leaderboard

def update_user_rankings():
    """Update country and global rankings for all users"""
    
    # Update global rankings
    users = User.objects.filter(status='active').order_by('-points', '-streak_days')
    for rank, user in enumerate(users, 1):
        user.global_rank = rank
        user.save(update_fields=['global_rank'])
    
    # Update country rankings
    countries = User.objects.filter(
        status='active', 
        country__isnull=False
    ).values_list('country', flat=True).distinct()
    
    for country in countries:
        country_users = User.objects.filter(
            status='active',
            country=country
        ).order_by('-points', '-streak_days')
        
        for rank, user in enumerate(country_users, 1):
            user.country_rank = rank
            user.save(update_fields=['country_rank'])
    
    # Update leaderboard entries
    update_leaderboard_rankings()

def update_leaderboard_rankings():
    """Update all leaderboard entries with current rankings"""
    
    # Global leaderboard
    global_board, _ = Leaderboard.objects.get_or_create(
        type='global',
        defaults={'name': 'Global Leaderboard'}
    )
    
    # Clear and rebuild
    global_board.entries.all().delete()
    
    top_users = User.objects.filter(
        status='active'
    ).order_by('-points', '-streak_days')[:100]
    
    for rank, user in enumerate(top_users, 1):
        LeaderboardEntry.objects.create(
            leaderboard=global_board,
            user=user,
            rank=rank,
            score=user.points,
            best_streak=user.streak_days
        )
    
    # Country leaderboards
    countries = User.objects.filter(
        status='active',
        country__isnull=False
    ).values_list('country', 'country_name').distinct()
    
    for country_code, country_name in countries:
        country_board, _ = Leaderboard.objects.get_or_create(
            type='country',
            country=country_code,
            defaults={'name': f'{country_name} Leaderboard'}
        )
        
        country_board.entries.all().delete()
        
        country_users = User.objects.filter(
            status='active',
            country=country_code
        ).order_by('-points', '-streak_days')[:50]
        
        for rank, user in enumerate(country_users, 1):
            LeaderboardEntry.objects.create(
                leaderboard=country_board,
                user=user,
                rank=rank,
                score=user.points,
                best_streak=user.streak_days
            )

def get_user_ranking_display(user):
    """Get formatted ranking display for a user"""
    rankings = []
    
    if user.country_rank and user.country_rank <= 10:
        rank_text = get_rank_text(user.country_rank)
        rankings.append({
            'type': 'country',
            'rank': user.country_rank,
            'text': f'{rank_text} in {user.country_name}',
            'badge_color': get_rank_color(user.country_rank)
        })
    
    if user.global_rank and user.global_rank <= 10:
        rank_text = get_rank_text(user.global_rank)
        rankings.append({
            'type': 'global',
            'rank': user.global_rank,
            'text': f'{rank_text} Global',
            'badge_color': get_rank_color(user.global_rank)
        })
    
    return rankings

def get_rank_text(rank):
    """Get display text for a rank"""
    if rank == 1:
        return '1st'
    elif rank == 2:
        return '2nd'
    elif rank == 3:
        return '3rd'
    elif rank <= 5:
        return 'Top 5'
    elif rank <= 10:
        return 'Top 10'
    else:
        return f'#{rank}'

def get_rank_color(rank):
    """Get color for a rank badge"""
    if rank == 1:
        return 'gold'
    elif rank == 2:
        return 'silver'
    elif rank == 3:
        return 'bronze'
    elif rank <= 5:
        return 'success'
    elif rank <= 10:
        return 'info'
    else:
        return 'secondary'