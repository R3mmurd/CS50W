import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import User, Post


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

def index(request):
    return render(request, "network/index.html")


@login_required(login_url='login')
def following(request):
    return render(request, "network/following.html")


def profile(request, username):
    me = request.user
    user = get_object_or_404(User, username=username)

    return render(request, "network/profile.html", {
        'user_info': user.serialize(),
        'me': me.is_authenticated and user == me,
        'followed': me.is_authenticated and user in me.following.all()
    })


@csrf_exempt
def create_post(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': "User not authenticated."}, status=401)

    if request.method != 'POST':
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)
    text = data['text']

    if not text:
        return JsonResponse({'error': "Text can not be blank."}, status=400)

    post = Post.objects.create(text=text, author=request.user)

    return JsonResponse(post.serialize(), status=201)


@csrf_exempt
def edit_post(request, pk):
    me = request.user

    if not me.is_authenticated:
        return JsonResponse({'error': "User not authenticated."}, status=401)
    
    if request.method != 'PUT':
        return JsonResponse({"error": "PUT request required."}, status=400)

    post = Post.objects.filter(pk=pk).first()

    if post is None:
        return JsonResponse({'error': "Post not found."}, status=404)

    if me != post.author:
        return JsonResponse(
            {'error': "You are not the post owner."},
            status=403
        )

    data = json.loads(request.body)
    text = data['text']

    if not text:
        return JsonResponse({'error': "Text can not be blank."}, status=400)
    
    post.text = text
    post.save()

    return JsonResponse({}, status=204)


def get_posts(request, which):
    if which == 'all':
        qs = Post.objects.order_by('-timestamp').all()
    elif which == 'following':
        if not request.user.is_authenticated:
            return JsonResponse(
                {'error': "User not authenticated."},
                status=401
            )
        qs = Post.objects.order_by('-timestamp').filter(
            author__in=request.user.following.all()
        )
    else:
        author = User.objects.filter(username=which).first()

        if author is None:
            return JsonResponse(
                {'error': f"User {which} not found."},
                status=404
            )
        
        qs = Post.objects.order_by('-timestamp').filter(author=author)

    paginator = Paginator(qs, 10)
    page_number = int(request.GET.get('page', 1))
    page_number = max(0, min(page_number, paginator.num_pages))
    page = paginator.get_page(page_number)

    posts = []
    
    for item in page:
        post = item.serialize()
        post['me'] = (request.user.is_authenticated
                and request.user == item.author)
        post['liked'] = (request.user.is_authenticated
                and request.user in item.liked_by.all())
        post['can_toggle_like'] = request.user.is_authenticated
        posts.append(post)

    result = {
        'posts': posts,
        'num_pages': paginator.num_pages,
        'page_number': page_number
    }

    return JsonResponse(result)


@csrf_exempt
def toggle_follow(request, username):
    me = request.user

    if not me.is_authenticated:
        return JsonResponse({'error': "User not authenticated."}, status=401)
    
    if request.method != 'PUT':
        return JsonResponse({"error": "PUT request required."}, status=400)
    
    user = User.objects.filter(username=username).first()

    if user is None:
        return JsonResponse(
            {'error': f"User {username} not found."},
            status=404
        )
        
    if user in me.following.all():
        me.following.remove(user)
    else:
        me.following.add(user)
    
    return JsonResponse({}, status=204)


@csrf_exempt
def toggle_like(request, pk):
    me = request.user

    if not me.is_authenticated:
        return JsonResponse({'error': "User not authenticated."}, status=401)
    
    if request.method != 'PUT':
        return JsonResponse({"error": "PUT request required."}, status=400)
    
    post = Post.objects.filter(pk=pk).first()

    if post is None:
        return JsonResponse({'error': "Post not found."}, status=404)
        
    if me in post.liked_by.all():
        post.liked_by.remove(me)
    else:
        post.liked_by.add(me)
    
    return JsonResponse({}, status=204)
