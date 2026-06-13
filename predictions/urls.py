from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("matches/", views.matches, name="matches"),
    path("matches/<int:match_id>/predict/", views.submit_prediction, name="submit_prediction"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
]