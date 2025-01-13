from django.contrib import admin

# Register your models here.

from .models import PortfolioAsset, Asset, Portfolio, AssetHistory, Cash

admin.site.register(PortfolioAsset)
admin.site.register(Asset)
admin.site.register(Portfolio)
admin.site.register(AssetHistory)
admin.site.register(Cash)