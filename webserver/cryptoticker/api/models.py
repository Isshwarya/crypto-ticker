from django.db import models

# A base class to accommodate future changes or features needed
# across all models
class CustomBaseModel(models.Model):
    def save(self, *args, **kwargs):
        # Does validation
        self.full_clean()
        return super(CustomBaseModel, self).save(*args, **kwargs)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class CryptoPrice(CustomBaseModel):

    datetime = models.DateTimeField("Datetime")
    symbol = models.CharField("Symbol", max_length=20)
    price = models.FloatField("Price")

    def __str__(self):
        return "DateTime: {}, Symbol: {}, Price: {}".format(
            self.datetime, self.symbol, self.price)

    class Meta:
        managed = False

class LatestCryptoPrice(CustomBaseModel):

    datetime = models.DateTimeField("Datetime")
    symbol = models.CharField("Symbol", max_length=20, unique=True)
    price = models.FloatField("Price")

    def __str__(self):
        return "DateTime: {}, Symbol: {}, Price: {}".format(
            self.datetime, self.symbol, self.price)

    class Meta:
        managed = False