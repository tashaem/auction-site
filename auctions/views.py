from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required

from .models import *

def index(request):

    # Retrieve active listings from database
    active_listings = Listing.objects.filter(active=True)

    return render(request, "auctions/index.html", {
        "active_listings": active_listings
    })

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
    if request.method=="POST":

        # Extracts form data from auctions/create.html
        title= request.POST["title"]
        desc=request.POST["desc"]
        starting_bid = request.POST["starting_bid"]
        image = request.POST["image_url"]

        new_listing = Listing(owner= request.user, title=title,desc=desc, starting_bid=starting_bid,current_price=starting_bid, image=image)
        new_listing.save()
        return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/create.html")

def listing(request, listing_id):

    # Retrieves info of requested listing in database
    listing = Listing.objects.get(pk=listing_id)


    # Initializing additional HTML features' / error indicators as False
    active = True
    winning_user = False
    onwatchlist = False
    watchlist_disable = False
    bid_disable = False
    bid_error = False
    owner = False

    if listing.active == True:


        if request.method=="POST":

            if 'addwatchlist' in request.POST:

                # Adds to watchlist if user is authenticated and displays pop up text otherwise
                if request.user.is_authenticated:
                    new_item = Watchlist(user= request.user,listing=listing)
                    new_item.save()
                else:
                    watchlist_disable = True

            elif 'removewatchlist' in request.POST:

                # Removes listing item from user's watchlist
                Watchlist.objects.filter(user=request.user,listing=listing).delete()

            elif 'placebid' in request.POST:

                # Tries to add newly placed bid to DB if user is authenticated
                if request.user.is_authenticated:
                    new_bid = float(request.POST["new_bid"])

                    # Checks if bid matches min requirements
                    if (new_bid <= listing.current_price):
                        bid_error=True
                    else:
                        # Adds to Bid model
                        bid=Bid(user=request.user,listing=listing, new_bid=new_bid)
                        bid.save()

                        # Updates Listing model
                        listing.current_price = new_bid
                        listing.save()
                        listing.num_bids += 1
                        listing.save()
                else:
                    bid_disable = True

            elif 'closeauction' in request.POST:

                # Renders the listing no longer active
                listing.active = False
                listing.save()

        try:
            match_in_watchlist = Watchlist.objects.get(user=request.user, listing=listing)
        except Watchlist.DoesNotExist: # should no such row exist in the database
            match_in_watchlist = None
        except: # should a user not be logged in hence AttributeError and TypeErrors surface
            match_in_watchlist = None

        # Allows listing page to show appropriate content depending on whether or not listing is in user's watchlist
        if match_in_watchlist !=None:
            onwatchlist=True

        # Checks if user is listing's owner
        if request.user.is_authenticated:
            if (request.user == listing.owner):
                owner = True

    # Note: If instead of Elif to accomodate the case the auction was just active
    if listing.active==False:
        active = False

        # Retrieves from the DB the winning user
        winner = Bid.objects.get(listing=listing, new_bid=listing.current_price).user

        if request.user.is_authenticated:
            if (request.user == winner):
                winning_user = True

    # Saves new comment into DB
    if request.user.is_authenticated:
        if request.method=="POST":
            if 'commentbtn' in request.POST:
                comment = request.POST["commentbox"]
                new_comment = Comment(user=request.user, listing=listing, comment=comment)
                new_comment.save()

    # Fetches all existing comments from DB
    comments = Comment.objects.filter(listing=listing).order_by('-id')

    return render(request, "auctions/listing.html",{
        "active":active,
        "listing": listing,
        "onwatchlist": onwatchlist,
        "watchlist_disable": watchlist_disable,
        "bid_disable": bid_disable,
        "bid_error": bid_error,
        "owner": owner,
        "winning_user": winning_user,
        "comments":comments
    })


@login_required
def watchlist(request):
    watchlist = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html",{
        "watchlist":watchlist
    })
