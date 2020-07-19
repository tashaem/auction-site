from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import *

#class PlaceNewBid(forms.Form, min_value):
#    new_bid=forms.DecimalField(max_digits=6, decimal_places=2, min_value=min_value)

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

    if request.method=="POST":

        if 'addwatchlist' in request.POST:
            # "add to watchlist"-> if user is authenticated -> add to watchlist
                if request.user.is_authenticated:
                    new_item = Watchlist(user= request.user,listing=listing)
                    new_item.save()
            #                       else --> pop up
        elif 'removewatchlist' in request.POST:
            Watchlist.objects.filter(user=request.user,listing=listing).delete()
        #else:
        # add bid -> if user isnt authenticated -> grayed out + note
        #                           else --> can make a bid

    # Allows listing page to show appropriate content depending on whether or not listing is in user's watchlist

    try:
        match_in_watchlist = Watchlist.objects.get(user=request.user, listing=listing)
    except Watchlist.DoesNotExist:
        match_in_watchlist = None

    if match_in_watchlist !=None:
        onwatchlist=True
    else:
        onwatchlist=False

    return render(request, "auctions/listing.html",{
        "listing": listing,
        "onwatchlist": onwatchlist
    })
