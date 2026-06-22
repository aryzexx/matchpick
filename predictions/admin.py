from django.contrib import admin

from .models import CompetitionGroup, GroupMember, Match, Prediction
from .views import get_prediction_availability


class GroupMemberInline(admin.TabularInline):
    """
    Allows admins to view group members directly inside a competition group.
    """

    model = GroupMember
    extra = 1


@admin.register(CompetitionGroup)
class CompetitionGroupAdmin(admin.ModelAdmin):
    """
    Admin configuration for private prediction groups.
    """

    list_display = ("name", "invite_code", "created_by", "created_at")
    search_fields = ("name", "invite_code", "created_by__username")
    list_filter = ("created_at",)
    inlines = [GroupMemberInline]


@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    """
    Admin configuration for group memberships.
    """

    list_display = ("user", "group", "role", "joined_at")
    search_fields = ("user__username", "group__name")
    list_filter = ("role", "joined_at")


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    """
    Admin configuration for football matches.
    """

    list_display = (
        "home_team",
        "away_team",
        "kickoff_time",
        "stage",
        "status",
        "score_display",
        "result",
        "voting_status",
        "external_source",
        "last_synced_at",
    )
    search_fields = (
        "home_team",
        "away_team",
        "external_source",
        "external_match_id",
    )
    list_filter = (
        "stage",
        "status",
        "result",
        "external_source",
        "kickoff_time",
    )
    ordering = ("kickoff_time",)
    date_hierarchy = "kickoff_time"

    fieldsets = (
        (
            "Fixture details",
            {
                "fields": (
                    "home_team",
                    "away_team",
                    "kickoff_time",
                    "stage",
                    "status",
                )
            },
        ),
        (
            "Score and result",
            {
                "fields": (
                    "home_score",
                    "away_score",
                    "result",
                ),
                "description": (
                    "If status is Finished and both scores are entered, "
                    "the result will be calculated automatically."
                ),
            },
        ),
        (
            "External import tracking",
            {
                "fields": (
                    "external_source",
                    "external_match_id",
                    "last_synced_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def voting_status(self, obj):
        """
        Shows whether prediction voting is currently open or locked.
        """
        voting_is_open, _ = get_prediction_availability(obj)

        if voting_is_open:
            return "Open"

        return "Locked"

    voting_status.short_description = "Voting"

    def save_model(self, request, obj, form, change):
        """
        Saves the match first, then recalculates points for all predictions
        linked to this match.

        This is important because results are usually entered after users
        have already submitted predictions.
        """
        super().save_model(request, obj, form, change)

        for prediction in obj.predictions.all():
            prediction.points_awarded = prediction.calculate_points()
            prediction.save()


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    """
    Admin configuration for user predictions.

    Predictions are now stored once per user and match, rather than once per
    user, group and match.
    """

    list_display = (
        "user",
        "match",
        "prediction",
        "points_awarded",
        "submitted_at",
    )
    search_fields = (
        "user__username",
        "match__home_team",
        "match__away_team",
    )
    list_filter = ("prediction", "points_awarded", "submitted_at")
    readonly_fields = ("points_awarded", "submitted_at", "updated_at")
    ordering = ("-submitted_at",)
