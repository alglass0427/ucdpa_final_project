from django.db import models
import uuid
from users.models import Profile
# Create your models here.


class Portfolio(models.Model):
    owner = models.ForeignKey(Profile,null= True,blank=True,on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True) 
    portfolio_desc = models.TextField(null=True, blank=False) ##blank tells django wether to Allow blank on the formas for this filed
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # ordering = ['created'] # "-" orders by descending
        ordering = ['portfolio_desc']

    def __str__(self):
        return self.portfolio_desc
    


    @classmethod
    def get_profiles_by_name(cls):
        return cls.objects.all().order_by('portfolio_desc')


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
    ticker = models.CharField(max_length=10, unique=True)
    company_name = models.CharField(max_length=255)
    industry = models.CharField(max_length=255, null=True, blank=True)

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
        return cls.objects.all().order_by('ticker')




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