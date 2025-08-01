from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import User, Listing, Category, Comment, Bid
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.contrib import messages


def index(request):
    activeListings = Listing.objects.filter(is_active=True)
    categories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "Listings": activeListings,
        "categories": categories
    })

def createListing(request):
    if request.method == "POST":
        starting_bid = request.POST.get("starting_bid")
        if starting_bid is None:
            categories = Category.objects.all()
            return render(request, "auctions/create.html", {
                "error": "Starting bid is required.",
                "categories": categories
            })
        title = request.POST["title"]
        description = request.POST["description"]
        image_url = request.POST.get("image_url", "")
        category_name = request.POST["category"]
        currentUser = request.user

        # Get the category object safely
        try:
            categoryData = Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            categories = Category.objects.all()
            return render(request, "auctions/create.html", {
                "error": "Category does not exist.",
                "categories": categories
            })

        # Create and save listing
        bid = Bid(bid=Decimal(starting_bid), user=currentUser)
        bid.save()  # Save the bid object first

        newListing = Listing(
            title=title,
            description=description,
            starting_bid=starting_bid,
            image_url=image_url,
            owner=currentUser,
            category=categoryData,
            is_active=True,
            price=bid  # <-- assign the bid object here
        )
        newListing.save()

        return redirect("index")  # or your success url
    else:
        categories = Category.objects.all()
        return render(request, "auctions/create.html", {"categories": categories})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create(request):
    if request.method == "POST":
        starting_bid = request.POST.get("starting_bid")
        if starting_bid is None:
            categories = Category.objects.all()
            return render(request, "auctions/create.html", {
                "error": "Starting bid is required.",
                "categories": categories
            })
        title = request.POST["title"]
        description = request.POST["description"]
        image_url = request.POST.get("image_url", "")
        category_name = request.POST["category"]
        currentUser = request.user

        # Get the category object safely
        try:
            categoryData = Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            categories = Category.objects.all()
            return render(request, "auctions/create.html", {
                "error": "Category does not exist.",
                "categories": categories
            })
        #create a bidobject
        bid = Bid(bid=int(starting_bid), user=currentUser)
        bid.save()  # Save the bid object first

        # Create and save listing, now with price=bid
        newListing = Listing(
            title=title,
            description=description,
            starting_bid=starting_bid,
            image_url=image_url,
            owner=currentUser,
            category=categoryData,
            is_active=True,
            price=bid  # <-- assign the bid object here
        )
        newListing.save()

        return redirect("index")  # or your success url
    else:
        categories = Category.objects.all()
        return render(request, "auctions/create.html", {"categories": categories})

def displayCategory(request):
    if request.method == "POST":
        CategoryFromForm = request.POST.get("category")
        category = Category.objects.get(name=CategoryFromForm)
        activeListings = Listing.objects.filter(is_active=True, category=category)
        categories = Category.objects.all()
        return render(request, "auctions/index.html", {
            "Listings": activeListings,
            "categories": categories
        })
def listing(request, id):
    listingData = Listing.objects.get(pk=id)
    isListingInWatchlist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    isOwwner = request.user.username == listingData.owner.username
    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatch": isListingInWatchlist,
        "allComments": allComments,
        "isOwner": isOwwner
    })

def listingDetail(request, listing_id):
    # your logic here
    pass
def removeWatchlist(request, id):
    listingData =Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

   
def addWatchlist(request, id):
    listing = Listing.objects.get(pk=id)
    currentUser = request.user
    listing.watchlist.add(currentUser)
    print(listing.watchlist.all())  # Debug: See if user is added
    return HttpResponseRedirect(reverse("listing", args=(id, )))


@login_required
def watchlist(request):
    currentUser = request.user
    listings = currentUser.listingWatchlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })
def addComment(request, id):
    if request.method == "POST":
        message = request.POST.get("message")  # <-- fix here
        currentUser = request.user

        listingData = Listing.objects.get(pk=id)
        newComment = Comment(
            author=currentUser,
            listing=listingData,
            message=message
        )
        newComment.save()
        return HttpResponseRedirect(reverse("listing", args=(id, )))

def addBid(request, id):
    if request.method == "POST":
        bid_amount = request.POST.get("bid_amount")
        currentUser = request.user
        listing = Listing.objects.get(pk=id)
        isListinginWatchlist = request.user in listing.watchlist.all()
        allComments = Comment.objects.filter(listing=listing)
        sowner = request.user.username == listing.owner.username

           
    
        # Validate bid
        try:
            bid_amount = Decimal(bid_amount)
        except:
            messages.error(request, "Invalid bid amount.")
            return HttpResponseRedirect(reverse("listing", args=(id, )))

        # Always require bid to be greater than starting_bid
        if bid_amount < listing.starting_bid:
            messages.error(
                request,
                f"Your bid was unsuccessful. Bid must be at least the initial price (${listing.starting_bid})."
            )
            return HttpResponseRedirect(reverse("listing", args=(id, )))

        # If there is a current bid, require higher than that too
        current_price = listing.price.bid if listing.price else listing.starting_bid
        if bid_amount <= current_price:
            messages.error(
                request,
                f"Your bid was unsuccessful. Bid must be higher than the current bid (${current_price})."
            )
            return HttpResponseRedirect(reverse("listing", args=(id, )))

        # Save new bid
        new_bid = Bid(bid=bid_amount, user=request.user)
        new_bid.save()
        listing.price = new_bid
        listing.save()
        messages.success(request, "Your Bid was Successful")
        return HttpResponseRedirect(reverse("listing", args=(id, )))
    else:
        messages.error(request, "Your Bid Was Unsuccessful. Please try again.")
        return HttpResponseRedirect(reverse("listing", args=(id, )))

def closeAuction(request, id):
    listing = Listing.objects.get(pk=id)
    if request.method == "POST":
        if request.user == listing.owner and listing.is_active:
            listing.is_active = False
            listing.save()
            messages.success(request, "Auction closed successfully.")
        else:
            messages.error(request, "You are not allowed to close this auction.")
        return redirect("listing", id=listing.id)
    return redirect("listing", id=listing.id)

def closeListing(request, id):
    # Your logic here
    pass

