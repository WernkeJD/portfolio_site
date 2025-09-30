from django.db import models

# Create your models here.
class Tickers(models.Model):
    stock = models.CharField()
    ticker = models.CharField()


class DailySelections(models.Model):
    date = models.DateField()
    crypto_1 = models.CharField()
    crypto_1_selections = models.IntegerField(default=0)
    crypto_1_price = models.FloatField(default=0)
    crypto_2 = models.CharField()
    crypto_2_selections = models.IntegerField(default=0)
    crypto_2_price = models.FloatField(default=0)
    stock_1 = models.CharField()
    stock_1_selections = models.IntegerField(default=0)
    stock_1_price = models.FloatField(default=0)
    stock_2 = models.CharField()
    stock_2_selections = models.IntegerField(default=0)
    stock_2_price = models.FloatField(default=0)


class Selections(models.Model):
    date = models.DateField()
    crypto_selection = models.CharField()
    crypto_price = models.FloatField()
    number_of_coins_purchased = models.IntegerField()
    stock_selection = models.CharField()
    stock_price = models.FloatField()
    number_of_stock_purchased = models.IntegerField()

class Portfolio(models.Model):
    date = models.DateField()
    crypto_portfolio_value = models.FloatField(default=10000)
    stock_portfolio_value = models.FloatField(default=10000)
    crypto_cash = models.FloatField(default=10000)
    stock_cash = models.FloatField(default=10000)

