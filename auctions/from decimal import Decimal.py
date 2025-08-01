from decimal import Decimal
from django.http import HttpResponseRedirect
from django.urls import reverse

def process_bid(bid_amount, id):
    try:
        bid_amount = Decimal(bid_amount)
    except:
        return HttpResponseRedirect(reverse("listing", args=(id, )))