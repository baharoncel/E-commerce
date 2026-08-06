"""
PazarClub Loyalty & Rewards Service
"""
from decimal import Decimal
from marketplace.models import UserLoyalty

def get_or_create_user_loyalty(user):
    """
    Retrieves or initializes the UserLoyalty profile for a user.
    """
    if not user.is_authenticated:
        return None
    loyalty, created = UserLoyalty.objects.get_or_create(user=user)
    return loyalty

def add_loyalty_points_for_purchase(user, purchase_amount):
    """
    Calculates and awards PazarPuan for a purchase (%5 of total spent).
    Recalculates tier and returns earned points.
    """
    if not user.is_authenticated:
        return 0

    loyalty, _ = UserLoyalty.objects.get_or_create(user=user)
    earned_points = int(Decimal(purchase_amount) * Decimal('0.05'))
    
    # Tier multipliers
    if loyalty.tier == 'PLATINUM':
        earned_points = int(earned_points * 2)
    elif loyalty.tier == 'GOLD':
        earned_points = int(earned_points * 1.5)

    loyalty.points += earned_points
    loyalty.total_spent += Decimal(purchase_amount)
    loyalty.calculate_tier()
    return earned_points
