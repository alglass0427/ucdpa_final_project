from django.db import models
import uuid
from users.models import Profile
from django.db.models import Case, When, BooleanField

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# Create your models here.


class Portfolio(models.Model):
    owner = models.ForeignKey(Profile,null= True,blank=True,on_delete=models.CASCADE)
    # id = models.AutoField(primary_key=True) 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio_desc = models.TextField(null=True, blank=False) ##blank tells django wether to Allow blank on the formas for this filed
    created = models.DateTimeField(auto_now_add=True)
    total_cash_balance = models.FloatField(default=0)  # New field to track total cash balance
    units = models.FloatField(default=1)
    
    class Meta:
        # ordering = ['created'] # "-" orders by descending
        ordering = ['portfolio_desc']

    def __str__(self):
        return f"Owner : {self.owner.name} - Portfolio : {self.portfolio_desc} - Cash : {self.total_cash_balance} "
    
    def total_holding_value(self):
        """
        Calculate the total holding value of all assets in the portfolio.
        """
        return self.portfolio_assets.aggregate(total_value=models.Sum('holding_value'))['total_value'] or 0
    
    
    @classmethod
    def get_profiles_by_name(cls):
        return cls.objects.all().order_by('portfolio_desc')
    
    def check_portfolio_exists(portfolio_name):
        portfolio_names = Portfolio.get_profiles_by_name().values_list('portfolio_desc', flat=True)
        return portfolio_name in portfolio_names



class Cash(models.Model):
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="cash_accounts"
    )
    # Add these fields for generic ownership
    owner_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={'model__in': ['profile', 'portfolio']},  # Limit to specific models
        null=True,
        blank=True
    )
    owner_object_id = models.UUIDField(
        null=True,
        blank=True,
    ) 
    owner = GenericForeignKey('owner_content_type', 'owner_object_id')

    balance = models.FloatField(default=0)  # The cash balance
    currency = models.CharField(max_length=10, default="USD")  # Support for multiple currencies
    units = models.FloatField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        owner_type = "User" if self.owner_content_type.model == "profile" else "Portfolio"
        print("OWNER",self.owner_object_id)
        
        portfolio = Portfolio.objects.filter(id=self.owner_object_id).first()
        owner = (
            self.owner.name 
            if self.owner_content_type.model == "profile" 
            else portfolio.portfolio_desc if portfolio else "Unknown Portfolio"
            )           
        return f"Owner Type: {owner_type} - Owner: {owner} - Value : {self.balance} - Portfolio Bought: {self.portfolio.portfolio_desc} -  Units: {self.units}"






class PortfolioAsset(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    owner = models.ForeignKey (Profile, 
                               on_delete=models.CASCADE, null = True, 
                               related_name='portfolio_assets' # Reverse relation
                               )
    portfolio = models.ForeignKey(Portfolio,
                                on_delete=models.CASCADE,  # Cascade delete
                                related_name='portfolio_assets'  # Reverse relation
                                )
    asset = models.ForeignKey(
        'Asset',
        on_delete=models.CASCADE,  # Cascade delete
        related_name='portfolio_assets'  # Back reference to Asset
    )
    
    buy_price = models.FloatField(default=0,null=True,blank=True)
    no_of_shares = models.IntegerField(default=0,null=True,blank=True)
    no_of_trades = models.IntegerField(default=0,null=True,blank=True)
    holding_value = models.FloatField(default=0,null=True,blank=True)
    stop_loss = models.FloatField(default=0,null=True,blank=True)
    cash_out = models.FloatField(default=0,null=True,blank=True)
    comment = models.TextField(null=True, blank=False)
    svg_content = models.TextField(null=True)


    class Meta:
        ordering = ['portfolio']

    def __str__(self):
        return f"{self.id} - for Portfolio {self.portfolio.portfolio_desc} and Asset {self.asset.ticker}"
    



class Asset(models.Model):
    id = models.AutoField(primary_key=True)
    ticker = models.CharField(max_length=100, unique=True)
    company_name = models.CharField(max_length=255)
    industry = models.CharField(max_length=255, null=True, blank=True)
    is_portfolio = models.BooleanField(default=False)
    portfolio = models.OneToOneField(
        'Portfolio', null=True, blank=True, on_delete=models.CASCADE
    )
    def to_json(self):
        return {
            'id': self.id,
            'ticker': self.ticker,
            'company_name': self.company_name,
            'industry': self.industry,
        }

    @classmethod
    def get_assets_by_ticker(cls):
        """
        Retrieve all assets sorted by ticker in ascending order.
        """
        assets = Asset.objects.annotate(
        starts_with_fof=Case(
            When(ticker__startswith="FOF-", then=True),
            default=False,
            output_field=BooleanField(),
                )
            ).order_by('-starts_with_fof', 'ticker')

        return assets


    def __str__(self):
        return self.ticker



class AssetHistory(models.Model):
    asset = models.ForeignKey(
        'Asset',  # Refers to the related Asset model
        on_delete=models.CASCADE,  # Deletes history entries if the Asset is deleted
        related_name='history'  # Enables reverse access (e.g., asset.history.all())
    )
    date = models.DateField()  # Equivalent to db.Column(db.Date, nullable=False)
    open_price = models.FloatField(null=True, blank=True)
    high_price = models.FloatField(null=True, blank=True)
    low_price = models.FloatField(null=True, blank=True)
    close_price = models.FloatField()
    volume = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.asset.ticker} - {self.date.strftime("%Y-%m-%d")}'