from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import RegisterForm
from .models import GroupMember, Match, Prediction


def home(request):
    """
    Displays the MatchPick homepage.
    """

    return render(request, "predictions/home.html")


def register(request):
    """
    Allows a new user to create an account using a username, password
    and invite code.

    If the invite code is valid, the user is automatically added to the
    matching competition group.
    """

    if request.user.is_authenticated:
        return redirect("matches")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            group = form.invite_group

            GroupMember.objects.create(
                user=user,
                group=group,
                role=GroupMember.ROLE_MEMBER,
            )

            login(request, user)

            messages.success(
                request,
                f"Account created successfully. You joined {group.name}.",
            )

            return redirect("matches")
    else:
        form = RegisterForm()

    return render(request, "predictions/register.html", {"form": form})


def user_login(request):
    """
    Allows an existing user to log in using username and password.
    """

    if request.user.is_authenticated:
        return redirect("matches")

    next_url = request.GET.get("next", "")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        next_url = request.POST.get("next", "")

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            safe_next_url = url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            )

            if safe_next_url:
                return redirect(next_url)

            return redirect("matches")
    else:
        form = AuthenticationForm()

    return render(
        request,
        "predictions/login.html",
        {
            "form": form,
            "next": next_url,
        },
    )


@login_required
@require_POST
def user_logout(request):
    """
    Logs out the current user.

    Logout uses POST rather than a normal link because this is safer than
    logging users out through a simple GET request.
    """

    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")


@login_required
def matches(request):
    """
    Displays real matches from the database.

    This view also attaches the current user's prediction to each match
    so the page can show whether they have already voted.
    """

    user_memberships = (
        GroupMember.objects.filter(user=request.user)
        .select_related("group")
        .order_by("group__name")
    )

    primary_membership = user_memberships.first()

    matches_list = list(
        Match.objects.all().order_by("kickoff_time", "home_team")
    )

    if primary_membership:
        user_predictions = Prediction.objects.filter(
            user=request.user,
            group=primary_membership.group,
            match__in=matches_list,
        ).select_related("match")

        predictions_by_match_id = {
            prediction.match_id: prediction for prediction in user_predictions
        }
    else:
        predictions_by_match_id = {}

    for match in matches_list:
        match.user_prediction = predictions_by_match_id.get(match.id)

    context = {
        "user_memberships": user_memberships,
        "primary_membership": primary_membership,
        "matches": matches_list,
        "total_matches": len(matches_list),
        "scheduled_matches": Match.objects.filter(
            status=Match.STATUS_SCHEDULED
        ).count(),
        "finished_matches": Match.objects.filter(
            status=Match.STATUS_FINISHED
        ).count(),
    }

    return render(request, "predictions/matches.html", context)


@login_required
@require_POST
def submit_prediction(request, match_id):
    """
    Allows a logged-in user to submit or update a prediction for a match.

    Normal browser form submission still works as a fallback. When the request
    comes from JavaScript, the view returns JSON so the page can update smoothly
    without refreshing.
    """

    match = get_object_or_404(Match, id=match_id)
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
    match_anchor_url = f"{reverse('matches')}#match-{match.id}"

    membership = (
        GroupMember.objects.filter(user=request.user)
        .select_related("group")
        .first()
    )

    if membership is None:
        error_message = (
            "You are not linked to a competition group, so you cannot submit predictions."
        )

        if is_ajax:
            return JsonResponse(
                {
                    "success": False,
                    "message": error_message,
                },
                status=400,
            )

        messages.error(request, error_message)
        return redirect(match_anchor_url)

    if not match.is_voting_open:
        error_message = (
            "Voting for this match is locked because kickoff has already passed "
            "or the match is not scheduled."
        )

        if is_ajax:
            return JsonResponse(
                {
                    "success": False,
                    "message": error_message,
                },
                status=400,
            )

        messages.error(request, error_message)
        return redirect(match_anchor_url)

    prediction_choice = request.POST.get("prediction")

    valid_choices = [
        Prediction.PREDICTION_HOME,
        Prediction.PREDICTION_DRAW,
        Prediction.PREDICTION_AWAY,
    ]

    if prediction_choice not in valid_choices:
        error_message = "Invalid prediction option."

        if is_ajax:
            return JsonResponse(
                {
                    "success": False,
                    "message": error_message,
                },
                status=400,
            )

        messages.error(request, error_message)
        return redirect(match_anchor_url)

    prediction, created = Prediction.objects.update_or_create(
        user=request.user,
        group=membership.group,
        match=match,
        defaults={
            "prediction": prediction_choice,
        },
    )

    if created:
        success_message = f"Prediction saved for {match.home_team} vs {match.away_team}."
    else:
        success_message = f"Prediction updated for {match.home_team} vs {match.away_team}."

    if is_ajax:
        return JsonResponse(
            {
                "success": True,
                "message": success_message,
                "prediction": prediction.prediction,
                "prediction_display": prediction.get_prediction_display(),
                "match_id": match.id,
            }
        )

    messages.success(request, success_message)
    return redirect(match_anchor_url)


@login_required
def leaderboard(request):
    """
    Displays a real leaderboard for the current user's primary competition group.
    """

    user_memberships = (
        GroupMember.objects.filter(user=request.user)
        .select_related("group")
        .order_by("group__name")
    )

    primary_membership = user_memberships.first()

    if primary_membership is None:
        context = {
            "primary_membership": None,
            "leaderboard_rows": [],
            "finished_matches_count": 0,
            "total_members": 0,
            "total_predictions": 0,
            "highest_points": 0,
        }

        return render(request, "predictions/leaderboard.html", context)

    group = primary_membership.group

    group_memberships = (
        GroupMember.objects.filter(group=group)
        .select_related("user")
        .order_by("user__username")
    )

    finished_matches = Match.objects.filter(
        status=Match.STATUS_FINISHED,
        result__isnull=False,
    )

    finished_matches_count = finished_matches.count()

    leaderboard_rows = []

    for membership in group_memberships:
        user = membership.user

        user_predictions = Prediction.objects.filter(
            user=user,
            group=group,
        ).select_related("match")

        total_points = 0
        predictions_made = 0
        scored_predictions = 0
        correct_predictions = 0

        for prediction in user_predictions:
            predictions_made += 1
            total_points += prediction.points_awarded

            if prediction.match.has_result:
                scored_predictions += 1

                if prediction.points_awarded > 0:
                    correct_predictions += 1

        if scored_predictions > 0:
            accuracy = round((correct_predictions / scored_predictions) * 100, 1)
        else:
            accuracy = 0

        missed_finished_matches = finished_matches_count - scored_predictions

        if missed_finished_matches < 0:
            missed_finished_matches = 0

        leaderboard_rows.append(
            {
                "username": user.username,
                "role": membership.get_role_display(),
                "total_points": total_points,
                "predictions_made": predictions_made,
                "scored_predictions": scored_predictions,
                "correct_predictions": correct_predictions,
                "missed_finished_matches": missed_finished_matches,
                "accuracy": accuracy,
                "is_current_user": user == request.user,
            }
        )

    leaderboard_rows.sort(
        key=lambda row: (
            -row["total_points"],
            -row["correct_predictions"],
            row["username"].lower(),
        )
    )

    for index, row in enumerate(leaderboard_rows, start=1):
        row["rank"] = index

    highest_points = 0

    if leaderboard_rows:
        highest_points = leaderboard_rows[0]["total_points"]

    total_predictions = sum(row["predictions_made"] for row in leaderboard_rows)

    context = {
        "primary_membership": primary_membership,
        "leaderboard_rows": leaderboard_rows,
        "finished_matches_count": finished_matches_count,
        "total_members": len(leaderboard_rows),
        "total_predictions": total_predictions,
        "highest_points": highest_points,
    }

    return render(request, "predictions/leaderboard.html", context)