from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("matches/", views.matches, name="matches"),
    path("my-picks/", views.my_picks, name="my_picks"),
    path("users/<int:user_id>/picks/", views.user_picks, name="user_picks"),
    path(
        "matches/<int:match_id>/predict/",
        views.submit_prediction,
        name="submit_prediction",
    ),
    path("leagues/", views.leagues, name="leagues"),
    path("leagues/<int:group_id>/", views.league_detail, name="league_detail"),
    path("leaderboard/", views.global_leaderboard, name="leaderboard"),
    path("insights/", views.insights, name="insights"),
    path(
        "staff/sync-results/",
        views.sync_latest_results,
        name="sync_latest_results",
    ),
]
