# utils.py
from portfolios.models import Portfolio, PortfolioAsset, Asset, AssetHistory


def calculate_holding_value(portfolio_id):
    """Utility function to calculate holding value for a portfolio."""
    assets = PortfolioAsset.objects.filter(portfolio_id=portfolio_id)
    holding_value = sum(asset.holding_value for asset in assets)
    return holding_value


def get_asset_tickers():
    """Utility function to get a list of all asset tickers."""
    return Asset.objects.values_list('ticker', flat=True)
