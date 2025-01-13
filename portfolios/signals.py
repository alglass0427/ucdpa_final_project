from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from .models import Cash, Portfolio


@receiver(post_save, sender=Cash)
def update_portfolio_cash_balance_on_save(sender, instance, **kwargs):
    total_cash = Cash.objects.filter(portfolio_id=instance.portfolio_id).aggregate(
        total=Sum('balance')
    )['total'] or 0
    Portfolio.objects.filter(id=instance.portfolio_id).update(total_cash_balance=total_cash)


@receiver(post_delete, sender=Cash)
def update_portfolio_cash_balance_on_delete(sender, instance, **kwargs):
    total_cash = Cash.objects.filter(portfolio_id=instance.portfolio_id).aggregate(
        total=Sum('balance')
    )['total'] or 0
    Portfolio.objects.filter(id=instance.portfolio_id).update(total_cash_balance=total_cash)

