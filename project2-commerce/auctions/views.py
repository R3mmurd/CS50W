import decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import User, Listing, Bid, Comment, Category


def index(request):
    return render(request, "auctions/index.html", {
        'listings': Listing.objects.filter(active=True).order_by('-created')
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


@login_required(login_url='/login/')
def create_listing(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        amount = request.POST['amount']
        image_url = request.POST['image_url']
        category = int(request.POST['category'])

        if category == 0:
            category = None
        else:
            category = Category.objects.get(pk=category)

        Listing.objects.create(
            title=title, description=description, current_amount=amount,
            image_url=image_url, listed_by=request.user, category=category
        )
        messages.success(request, 'Listing created successfully')
        return HttpResponseRedirect(reverse('index'))

    return render(request, 'auctions/create_listing.html', {
        'categories': Category.objects.order_by('name')
    })


def view_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    return render(request, 'auctions/view_listing.html', {
        'listing': listing,
        'bids': listing.listing_bids.order_by('-created'),
        'comments': listing.listing_comments.order_by('-created'),
        'in_watchlist': (request.user.is_authenticated
                         and listing in request.user.watchlist.all())
    })


@login_required(login_url='/login/')
def toggle_watchlist(request, pk):
    listing = get_object_or_404(Listing, pk=pk, active=True)

    watched = request.user.watchlist.filter(pk=pk).first()

    if watched is None:
        messages.success(request, 'Listing added to watchlist successfully.')
        request.user.watchlist.add(listing)
    else:
        messages.success(request, 'Listing removed to watchlist successfully.')
        request.user.watchlist.remove(listing)

    return HttpResponseRedirect(reverse('view_listing', args=(pk,)))


@login_required(login_url='/login/')
@require_POST
def add_bid(request, pk):
    listing = get_object_or_404(Listing, pk=pk, active=True)

    amount = decimal.Decimal(request.POST['bid'])

    if amount <= listing.current_amount:
        messages.error(
            request,
            f"Bid value must be greater than ${listing.current_amount}."
        )
    else:
        Bid.objects.create(
            amount=amount, listing=listing, author=request.user
        )
        listing.current_amount = amount
        listing.save()
        messages.success(request, "Bid added successfully.")

    return HttpResponseRedirect(reverse('view_listing', args=(pk,)))


@login_required(login_url='/login/')
@require_POST
def close(request, pk):
    listing = get_object_or_404(Listing, pk=pk, active=True)
    listing.active = False
    listing.save()
    messages.success(request, "Listing closed successfully.")
    return HttpResponseRedirect(reverse('view_listing', args=(pk,)))


@login_required(login_url='/login/')
@login_required(login_url='/login/')
@require_POST
def add_message(request, pk):
    listing = get_object_or_404(Listing, pk=pk, active=True)
    text = request.POST['text']
    Comment.objects.create(
        text=text, listing=listing, author=request.user
    )
    return HttpResponseRedirect(reverse('view_listing', args=(pk,)))


@login_required(login_url='/login/')
def watchlist(request):
    return render(request, 'auctions/watchlist.html', {
        'watchlist': request.user.watchlist.all()
    })


def categories(request):
    return render(request, 'auctions/categories.html', {
        'categories': Category.objects.order_by('name')
    })


def listing_by_category(request, pk):
    category = None if pk == 0 else Category.objects.get(pk=pk)
    listings = Listing.objects.filter(
        active=True, category=category
    ).order_by('-created')

    return render(request, 'auctions/listings_by_category.html', {
        'category': category,
        'listings': listings
    })
