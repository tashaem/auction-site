from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    owner=models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_listings")
    active= models.BooleanField(default=True)
    title=models.CharField(max_length=64)
    desc= models.CharField(max_length=1024)
    starting_bid= models.DecimalField(max_digits=6, decimal_places=2)
    current_price=models.DecimalField(max_digits=6, decimal_places=2)
    image= models.URLField(blank=True)
    num_bids=models.IntegerField(default=0)

class Watchlist(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    listing=models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="on_watchlists")

class Bid(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing=models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    new_bid=models.DecimalField(max_digits=6, decimal_places=2)

class Comment(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    listing=models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="commented_listings")
