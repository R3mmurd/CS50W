
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("following/", views.following, name="following"),
    path("profiles/<str:username>/", views.profile, name="profile"),

    # API routes
    path("posts/", views.create_post, name="create_post"),
    path("posts/<str:which>/", views.get_posts, name="get_posts"),
    path("toggle_follow/<str:username>/", views.toggle_follow,
         name="toggle_follow"),
    path("posts/<int:pk>/edit/", views.edit_post, name="edit_post"),
    path("posts/<int:pk>/toggle_like/", views.toggle_like, name="toggle_like")
]
