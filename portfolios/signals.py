from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum , F

from .models import Cash, Portfolio

# @receiver(post_save, sender=Cash)
# def update_portfolio_cash_balance_on_save(sender, instance, created, **kwargs):
#     if created:
#         print(f"Signal triggered for Cash: {instance} (Created: {created})")
#         # For a newly created Cash instance, add the balance and units
#         Portfolio.objects.filter(id=instance.portfolio_id).update(
#             total_cash_balance=F('total_cash_balance') + instance.balance,
#             units=F('units') + instance.units
#         )
#     else:
#         # If updating an existing instance, calculate the difference and update
#         print(f"Signal triggered for Cash: {instance} (Created: {created}) ")
#         previous = sender.objects.get(pk=instance.pk)
#         print(previous)
#         balance_diff = instance.balance - previous.balance
#         units_diff = instance.units - previous.units
#         print(balance_diff)
#         Portfolio.objects.filter(id=instance.portfolio_id).update(
#             total_cash_balance=F('total_cash_balance') + balance_diff,
#             units=F('units') + units_diff
#         )


# @receiver(post_delete, sender=Cash)
# def update_portfolio_cash_balance_on_delete(sender, instance, **kwargs):
#     # Calculate the total cash balance for the portfolio
#     total_cash = Cash.objects.filter(portfolio_id=instance.portfolio_id).aggregate(
#         total_cash=Sum('balance')
#     )['total_cash'] or 0

#     # Calculate the total units for the portfolio
#     total_units = Cash.objects.filter(portfolio_id=instance.portfolio_id).aggregate(
#         total_units=Sum('units')
#     )['total_units'] or 0

#     # Update the Portfolio with the new totals
#     Portfolio.objects.filter(id=instance.portfolio_id).update(
#         total_cash_balance=total_cash,
#         units=total_units
#     )

