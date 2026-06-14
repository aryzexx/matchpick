import io
import re
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.management import call_command
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import JoinLeagueForm, RegisterForm
from .models import CompetitionGroup, GroupMember, Match, Prediction


User = get_user_model()

PREDICTION_OPEN_HOURS = 48

PLACEHOLDER_TERMS = [
    "tbc",
    "tbd",
    "to be confirmed",
    "to be decided",
    "to be determined",
    "winner",
    "runner-up",
    "runner up",
    "third place",
    "placeholder",
]

GROUP_PLACEHOLDER_PATTERN = re.compile(
    r"^([123][a-h]|[a-h][123]|winner\s+group|runner[- ]?up\s+group)",
    re.IGNORECASE,
)


def team_name_is_confirmed(team_name):
    if not team_name:
        return False

    normalised_name = team_name.strip().lower()

    if not normalised_name:
        return False

    for term in PLACEHOLDER_TERMS:
        if term in normalised_name:
            return False

    if GROUP_PLACEHOLDER_PATTERN.search(normalised_name):
        return False

    return True


def match_teams_are_confirmed(match):
    return team_name_is_confirmed(match.home_team) and team_name_is_confirmed(
        match.away_team
    )


def get_prediction_availability(match):
    now = timezone.now()

    if match.status != Match.STATUS_SCHEDULED:
        return False, "Voting is locked because this match is not scheduled."

    if not match_teams_are_confirmed(match):
        return False, "Voting is locked until both teams are confirmed."

    if match.kickoff_time <= now:
        return False, "Voting is locked because kickoff has already passed."

    voting_opens_at = match.kickoff_time - timedelta(hours=PREDICTION_OPEN_HOURS)

    if now < voting_opens_at:
        local_opens_at = timezone.localtime(voting_opens_at).strftime(
            "%a, %d %b %H:%M"
        )

        return False, f"Voting opens 48 hours before kickoff: {local_opens_at}."

    return True, "Voting is open."


def voting_trends_are_visible(match):
    """
    Voting trends are only shown once voting can no longer influence a user's pick.

    This means trends are hidden before kickoff, even if the user has already
    submitted a prediction. Once kickoff has passed, or the match is no longer
    scheduled, the percentages can be shown.
    """
    return match.status != Match.STATUS_SCHEDULED or timezone.now() >= match.kickoff_time


def percentage(count, total):
    if total <= 0:
        return 0

    return round((count / total) * 100)


def get_prediction_trends_for_match(match):
    predictions = Prediction.objects.filter(match=match)

    counts = {
        Prediction.PREDICTION_HOME: 0,
        Prediction.PREDICTION_DRAW: 0,
        Prediction.PREDICTION_AWAY: 0,
    }

    for prediction in predictions:
        if prediction.prediction in counts:
            counts[prediction.prediction] += 1

    total_predictions = sum(counts.values())

    options = [
        {
            "key": Prediction.PREDICTION_HOME,
            "label": f"{match.home_team} win",
            "short_label": match.home_team,
            "count": counts[Prediction.PREDICTION_HOME],
            "percentage": percentage(
                counts[Prediction.PREDICTION_HOME],
                total_predictions,
            ),
        },
        {
            "key": Prediction.PREDICTION_DRAW,
            "label": "Draw",
            "short_label": "Draw",
            "count": counts[Prediction.PREDICTION_DRAW],
            "percentage": percentage(
                counts[Prediction.PREDICTION_DRAW],
                total_predictions,
            ),
        },
        {
            "key": Prediction.PREDICTION_AWAY,
            "label": f"{match.away_team} win",
            "short_label": match.away_team,
            "count": counts[Prediction.PREDICTION_AWAY],
            "percentage": percentage(
                counts[Prediction.PREDICTION_AWAY],
                total_predictions,
            ),
        },
    ]

    top_option = None

    if total_predictions > 0:
        top_option = sorted(
            options,
            key=lambda option: (
                -option["count"],
                -option["percentage"],
                option["label"],
            ),
        )[0]

    return {
        "total_predictions": total_predictions,
        "options": options,
        "top_option": top_option,
    }


def build_prediction_insights():
    trend_matches = []
    team_support = {}
    favourite_candidates = []
    draw_candidates = []

    matches = Match.objects.all().order_by("-kickoff_time", "home_team")

    for match in matches:
        if not voting_trends_are_visible(match):
            continue

        trends = get_prediction_trends_for_match(match)

        if trends["total_predictions"] == 0:
            continue

        trend_match = {
            "match": match,
            "trends": trends,
        }

        trend_matches.append(trend_match)

        for option in trends["options"]:
            if option["count"] <= 0:
                continue

            if option["key"] == Prediction.PREDICTION_HOME:
                team_support[match.home_team] = (
                    team_support.get(match.home_team, 0) + option["count"]
                )

                favourite_candidates.append(
                    {
                        "match": match,
                        "label": option["label"],
                        "team": match.home_team,
                        "count": option["count"],
                        "percentage": option["percentage"],
                    }
                )

            elif option["key"] == Prediction.PREDICTION_AWAY:
                team_support[match.away_team] = (
                    team_support.get(match.away_team, 0) + option["count"]
                )

                favourite_candidates.append(
                    {
                        "match": match,
                        "label": option["label"],
                        "team": match.away_team,
                        "count": option["count"],
                        "percentage": option["percentage"],
                    }
                )

            elif option["key"] == Prediction.PREDICTION_DRAW:
                draw_candidates.append(
                    {
                        "match": match,
                        "label": f"{match.home_team} vs {match.away_team}",
                        "count": option["count"],
                        "percentage": option["percentage"],
                    }
                )

    most_backed_team = None

    if team_support:
        team_name, support_count = sorted(
            team_support.items(),
            key=lambda item: (-item[1], item[0]),
        )[0]

        most_backed_team = {
            "team": team_name,
            "count": support_count,
        }

    biggest_favourite = None

    if favourite_candidates:
        biggest_favourite = sorted(
            favourite_candidates,
            key=lambda item: (
                -item["percentage"],
                -item["count"],
                item["team"],
            ),
        )[0]

    most_predicted_draw = None

    if draw_candidates:
        most_predicted_draw = sorted(
            draw_candidates,
            key=lambda item: (
                -item["percentage"],
                -item["count"],
                item["label"],
            ),
        )[0]

    most_divided_match = None
    divided_candidates = []

    for trend_match in trend_matches:
        trends = trend_match["trends"]

        if trends["total_predictions"] < 2:
            continue

        percentages = [option["percentage"] for option in trends["options"]]
        spread = max(percentages) - min(percentages)

        divided_candidates.append(
            {
                "match": trend_match["match"],
                "trends": trends,
                "spread": spread,
            }
        )

    if divided_candidates:
        most_divided_match = sorted(
            divided_candidates,
            key=lambda item: (
                item["spread"],
                -item["trends"]["total_predictions"],
                item["match"].kickoff_time,
            ),
        )[0]

    return {
        "trend_matches": trend_matches,
        "recent_trend_matches": trend_matches[:5],
        "trend_match_count": len(trend_matches),
        "total_locked_predictions": sum(
            item["trends"]["total_predictions"] for item in trend_matches
        ),
        "most_backed_team": most_backed_team,
        "biggest_favourite": biggest_favourite,
        "most_divided_match": most_divided_match,
        "most_predicted_draw": most_predicted_draw,
    }


def get_user_memberships(user):
    return (
        GroupMember.objects.filter(user=user)
        .select_related("group")
        .order_by("group__name")
    )


def get_global_predictions_for_user(user, matches_list=None):
    predictions = Prediction.objects.filter(user=user).select_related("match")

    if matches_list is not None:
        predictions = predictions.filter(match__in=matches_list)

    return {
        prediction.match_id: prediction
        for prediction in predictions.order_by("match_id")
    }


def build_leaderboard_rows(users, current_user, role_by_user_id=None):
    finished_matches = [
        match
        for match in Match.objects.filter(status=Match.STATUS_FINISHED).order_by(
            "kickoff_time"
        )
        if match.has_result
    ]

    finished_matches_count = len(finished_matches)
    leaderboard_rows = []

    for user in users:
        predictions_by_match_id = get_global_predictions_for_user(user)

        total_points = 0
        predictions_made = 0
        scored_predictions = 0
        correct_predictions = 0

        for prediction in predictions_by_match_id.values():
            predictions_made += 1
            total_points += prediction.points_awarded

            if prediction.match.has_result:
                scored_predictions += 1

                if prediction.points_awarded > 0:
                    correct_predictions += 1

        incorrect_predictions = scored_predictions - correct_predictions

        if incorrect_predictions < 0:
            incorrect_predictions = 0

        if scored_predictions > 0:
            accuracy = round((correct_predictions / scored_predictions) * 100, 1)
        else:
            accuracy = 0

        missed_finished_matches = finished_matches_count - scored_predictions

        if missed_finished_matches < 0:
            missed_finished_matches = 0

        if role_by_user_id:
            role = role_by_user_id.get(user.id, "Member")
        else:
            role = "Player"

        leaderboard_rows.append(
            {
                "username": user.username,
                "role": role,
                "total_points": total_points,
                "predictions_made": predictions_made,
                "scored_predictions": scored_predictions,
                "correct_predictions": correct_predictions,
                "incorrect_predictions": incorrect_predictions,
                "missed_finished_matches": missed_finished_matches,
                "accuracy": accuracy,
                "is_current_user": user == current_user,
            }
        )

    leaderboard_rows.sort(
        key=lambda row: (
            -row["total_points"],
            -row["correct_predictions"],
            row["missed_finished_matches"],
            row["username"].lower(),
        )
    )

    for index, row in enumerate(leaderboard_rows, start=1):
        row["rank"] = index

    highest_points = 0
    average_accuracy = 0
    top_scorer = None
    most_accurate = None
    fewest_missed = None

    if leaderboard_rows:
        highest_points = leaderboard_rows[0]["total_points"]
        top_scorer = leaderboard_rows[0]

        rows_with_scored_predictions = [
            row for row in leaderboard_rows if row["scored_predictions"] > 0
        ]

        if rows_with_scored_predictions:
            average_accuracy = round(
                sum(row["accuracy"] for row in rows_with_scored_predictions)
                / len(rows_with_scored_predictions),
                1,
            )

            most_accurate = sorted(
                rows_with_scored_predictions,
                key=lambda row: (
                    -row["accuracy"],
                    -row["correct_predictions"],
                    row["username"].lower(),
                ),
            )[0]

        fewest_missed = sorted(
            leaderboard_rows,
            key=lambda row: (
                row["missed_finished_matches"],
                -row["total_points"],
                row["username"].lower(),
            ),
        )[0]

    total_predictions = sum(row["predictions_made"] for row in leaderboard_rows)

    return {
        "leaderboard_rows": leaderboard_rows,
        "finished_matches_count": finished_matches_count,
        "total_members": len(leaderboard_rows),
        "total_predictions": total_predictions,
        "highest_points": highest_points,
        "average_accuracy": average_accuracy,
        "top_scorer": top_scorer,
        "most_accurate": most_accurate,
        "fewest_missed": fewest_missed,
    }


def get_safe_redirect_url(request, fallback_url_name="matches"):
    redirect_target = request.POST.get("next") or request.GET.get("next")

    if redirect_target and url_has_allowed_host_and_scheme(
        url=redirect_target,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect_target

    return reverse(fallback_url_name)


def home(request):
    return render(request, "predictions/home.html")


def register(request):
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
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")


@login_required
@require_POST
def sync_latest_results(request):
    if not request.user.is_staff:
        messages.error(request, "Only staff users can sync fixtures and results.")
        return redirect("matches")

    output_buffer = io.StringIO()
    error_buffer = io.StringIO()

    try:
        call_command(
            "import_openfootball_worldcup",
            stdout=output_buffer,
            stderr=error_buffer,
        )
    except Exception as error:
        messages.error(
            request,
            f"Result sync failed: {error}",
        )

        return redirect(get_safe_redirect_url(request))

    command_output = output_buffer.getvalue().strip()
    command_errors = error_buffer.getvalue().strip()

    if command_errors:
        messages.warning(
            request,
            f"Sync completed with warnings: {command_errors[:300]}",
        )
    elif command_output:
        messages.success(
            request,
            f"Latest fixtures and results synced. {command_output[:300]}",
        )
    else:
        messages.success(
            request,
            "Latest fixtures and results synced successfully.",
        )

    return redirect(get_safe_redirect_url(request))


@login_required
def matches(request):
    user_memberships = get_user_memberships(request.user)

    matches_list = list(Match.objects.all().order_by("kickoff_time", "home_team"))

    predictions_by_match_id = get_global_predictions_for_user(
        request.user,
        matches_list,
    )

    open_matches_count = 0

    for match in matches_list:
        match.user_prediction = predictions_by_match_id.get(match.id)

        voting_is_open, voting_message = get_prediction_availability(match)

        match.voting_is_open = voting_is_open
        match.voting_message = voting_message
        match.trends_visible = voting_trends_are_visible(match)

        if match.trends_visible:
            match.prediction_trends = get_prediction_trends_for_match(match)
        else:
            match.prediction_trends = None

        if voting_is_open:
            open_matches_count += 1

    open_match_ids = [match.id for match in matches_list if match.voting_is_open]

    if open_match_ids:
        user_open_predictions_made = (
            Prediction.objects.filter(
                user=request.user,
                match_id__in=open_match_ids,
            )
            .values("match_id")
            .distinct()
            .count()
        )
    else:
        user_open_predictions_made = 0

    user_open_predictions_pending = open_matches_count - user_open_predictions_made

    if user_open_predictions_pending < 0:
        user_open_predictions_pending = 0

    locked_matches_count = len(matches_list) - open_matches_count

    context = {
        "user_memberships": user_memberships,
        "primary_membership": user_memberships.first(),
        "matches": matches_list,
        "total_matches": len(matches_list),
        "scheduled_matches": Match.objects.filter(
            status=Match.STATUS_SCHEDULED
        ).count(),
        "finished_matches": Match.objects.filter(
            status=Match.STATUS_FINISHED
        ).count(),
        "open_matches_count": open_matches_count,
        "locked_matches_count": locked_matches_count,
        "user_open_predictions_made": user_open_predictions_made,
        "user_open_predictions_pending": user_open_predictions_pending,
    }

    return render(request, "predictions/matches.html", context)


@login_required
@require_POST
def submit_prediction(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
    match_anchor_url = f"{reverse('matches')}#match-{match.id}"

    memberships = list(get_user_memberships(request.user))

    if not memberships:
        error_message = (
            "You are not linked to any league, so you cannot submit predictions."
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

    voting_is_open, voting_message = get_prediction_availability(match)

    if not voting_is_open:
        if is_ajax:
            return JsonResponse(
                {
                    "success": False,
                    "message": voting_message,
                },
                status=400,
            )

        messages.error(request, voting_message)
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
        match=match,
        defaults={
            "prediction": prediction_choice,
        },
    )

    if created:
        success_message = f"Prediction saved for {match.home_team} vs {match.away_team}."
    else:
        success_message = (
            f"Prediction updated for {match.home_team} vs {match.away_team}."
        )

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
def leagues(request):
    if request.method == "POST":
        join_form = JoinLeagueForm(request.POST)

        if join_form.is_valid():
            group = join_form.invite_group

            already_member = GroupMember.objects.filter(
                user=request.user,
                group=group,
            ).exists()

            if already_member:
                messages.info(request, f"You are already a member of {group.name}.")
            else:
                GroupMember.objects.create(
                    user=request.user,
                    group=group,
                    role=GroupMember.ROLE_MEMBER,
                )

                messages.success(request, f"You joined {group.name}.")

            return redirect("league_detail", group_id=group.id)
    else:
        join_form = JoinLeagueForm()

    user_memberships = get_user_memberships(request.user)

    context = {
        "join_form": join_form,
        "user_memberships": user_memberships,
        "primary_membership": user_memberships.first(),
    }

    return render(request, "predictions/leagues.html", context)


@login_required
def league_detail(request, group_id):
    group = get_object_or_404(CompetitionGroup, id=group_id)

    current_membership = GroupMember.objects.filter(
        user=request.user,
        group=group,
    ).first()

    if current_membership is None:
        messages.error(request, "You are not a member of that league.")
        return redirect("leagues")

    group_memberships = (
        GroupMember.objects.filter(group=group)
        .select_related("user")
        .order_by("user__username")
    )

    users = [membership.user for membership in group_memberships]

    role_by_user_id = {
        membership.user_id: membership.get_role_display()
        for membership in group_memberships
    }

    leaderboard_context = build_leaderboard_rows(
        users=users,
        current_user=request.user,
        role_by_user_id=role_by_user_id,
    )

    user_memberships = get_user_memberships(request.user)

    context = {
        "group": group,
        "current_membership": current_membership,
        "user_memberships": user_memberships,
        "primary_membership": user_memberships.first(),
        **leaderboard_context,
    }

    return render(request, "predictions/league_detail.html", context)


@login_required
def global_leaderboard(request):
    user_ids = GroupMember.objects.values_list("user_id", flat=True).distinct()

    users = User.objects.filter(id__in=user_ids).order_by("username")

    leaderboard_context = build_leaderboard_rows(
        users=users,
        current_user=request.user,
    )

    user_memberships = get_user_memberships(request.user)

    context = {
        "user_memberships": user_memberships,
        "primary_membership": user_memberships.first(),
        **leaderboard_context,
    }

    return render(request, "predictions/leaderboard.html", context)


@login_required
def insights(request):
    user_memberships = get_user_memberships(request.user)
    insight_context = build_prediction_insights()

    context = {
        "user_memberships": user_memberships,
        "primary_membership": user_memberships.first(),
        **insight_context,
    }

    return render(request, "predictions/insights.html", context)