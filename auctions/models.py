from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.http import HttpResponse
from django.shortcuts import render


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=54)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    price = models.ForeignKey('Bid', on_delete=models.CASCADE, blank=True, null=True, related_name="listings_with_this_price")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="listings")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="listings")
    watchlist = models.ManyToManyField(User, related_name="listingWatchlist", blank=True) 

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if isinstance(self.starting_bid, str):
            from decimal import Decimal
            self.starting_bid = Decimal(self.starting_bid)
        super().save(*args, **kwargs)

class Comment(models.Model):  
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listingcomment") 
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usercomment")
    message = models.CharField(max_length=255)

class Bid(models.Model):
    bid = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="UserBid")

    def __str__(self):
        return str(self.bid)
