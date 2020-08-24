from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("listings/", views.create_listing, name="create_listing"),
    path("listings/<int:pk>/", views.view_listing, name="view_listing"),
    path("listings/<int:pk>/watchlist/", views.toggle_watchlist,
         name="toggle_watchlist"),
    path("listings/<int:pk>/add_bid/", views.add_bid, name="add_bid"),
    path("listings/<int:pk>/close/", views.close, name="close_listing"),
    path("listings/<int:pk>/add_message/", views.add_message,
         name="add_message"),
    path("listings/<int:pk>/add_message/", views.add_message,
         name="add_message"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("categories/", views.categories, name="categories"),
    path("categories/<int:pk>/", views.listing_by_category,
         name="listing_by_category"),
]
