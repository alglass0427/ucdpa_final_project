from rest_framework import serializers
from portfolios.models import Portfolio , PortfolioAsset ,Cash,Asset
from users.models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = '__all__'

class PortfolioAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioAsset
        fields = '__all__'



# Serializer for Total Users
class TotalUsersSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()

# Serializer for Top 5 Invested Stocks
class TopInvestedStocksSerializer(serializers.Serializer):
    asset_ticker = serializers.CharField(source='asset__ticker')
    total_value = serializers.FloatField()

# class TopInvestedStocksSerializer(serializers.Serializer):
#     labels = serializers.ListField(child=serializers.CharField())
#     data = serializers.ListField(child=serializers.FloatField())

# Serializer for Total Portfolio Value
class TotalPortfolioValueSerializer(serializers.Serializer):
    total_value = serializers.FloatField()

# Serializer for User Growth Over Time
class UserGrowthOverTimeSerializer(serializers.Serializer):
    day = serializers.DateField()
    total_users = serializers.IntegerField()

# Serializer for Average Portfolio Size
class AveragePortfolioSizeSerializer(serializers.Serializer):
    average_size = serializers.FloatField()

# Serializer for Top Industries by Value
class TopIndustriesSerializer(serializers.Serializer):
    industry = serializers.CharField(source='asset__industry')
    total_value = serializers.FloatField()
