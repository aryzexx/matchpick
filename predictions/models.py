from django.conf import settings
from django.db import models
from django.utils import timezone


class CompetitionGroup(models.Model):
    """
    A private prediction group, such as a family group or friends group.
    Users join this group using an invite code.
    """

    name = models.CharField(max_length=100)
    invite_code = models.CharField(max_length=30, unique=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_competition_groups",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class GroupMember(models.Model):
    """
    Connects a user to a competition group.
    This allows the same user to join more than one private competition.
    """

    ROLE_ADMIN = "admin"
    ROLE_MEMBER = "member"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_MEMBER, "Member"),
    ]

    group = models.ForeignKey(
        CompetitionGroup,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="group_memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_MEMBER,
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["group", "user"]
        ordering = ["group", "user"]

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"


class Match(models.Model):
    """
    A football match that users can predict.

    This model supports both manual fixture/result entry and import from
    a free fixture/result data source.
    """

    STAGE_GROUP = "group"
    STAGE_ROUND_OF_32 = "round_of_32"
    STAGE_ROUND_OF_16 = "round_of_16"
    STAGE_QUARTER_FINAL = "quarter_final"
    STAGE_SEMI_FINAL = "semi_final"
    STAGE_THIRD_PLACE = "third_place"
    STAGE_FINAL = "final"

    STAGE_CHOICES = [
        (STAGE_GROUP, "Group Stage"),
        (STAGE_ROUND_OF_32, "Round of 32"),
        (STAGE_ROUND_OF_16, "Round of 16"),
        (STAGE_QUARTER_FINAL, "Quarter-final"),
        (STAGE_SEMI_FINAL, "Semi-final"),
        (STAGE_THIRD_PLACE, "Third-place Play-off"),
        (STAGE_FINAL, "Final"),
    ]

    STATUS_SCHEDULED = "scheduled"
    STATUS_FINISHED = "finished"
    STATUS_POSTPONED = "postponed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_FINISHED, "Finished"),
        (STATUS_POSTPONED, "Postponed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    RESULT_HOME = "home"
    RESULT_DRAW = "draw"
    RESULT_AWAY = "away"

    RESULT_CHOICES = [
        (RESULT_HOME, "Home team win"),
        (RESULT_DRAW, "Draw"),
        (RESULT_AWAY, "Away team win"),
    ]

    external_source = models.CharField(
        max_length=50,
        blank=True,
        help_text="Optional source name for imported fixtures, e.g. openfootball.",
    )
    external_match_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional match ID from the external fixture/result source.",
    )

    home_team = models.CharField(max_length=80)
    away_team = models.CharField(max_length=80)
    kickoff_time = models.DateTimeField()
    stage = models.CharField(
        max_length=30,
        choices=STAGE_CHOICES,
        default=STAGE_GROUP,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_SCHEDULED,
    )

    home_score = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text="Final home team score. Leave blank before the match is finished.",
    )
    away_score = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text="Final away team score. Leave blank before the match is finished.",
    )

    result = models.CharField(
        max_length=10,
        choices=RESULT_CHOICES,
        blank=True,
        null=True,
        help_text="Final outcome used for scoring predictions.",
    )

    last_synced_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When this match was last updated from an external source.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["kickoff_time", "home_team"]
        verbose_name = "Match"
        verbose_name_plural = "Matches"

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"

    @property
    def is_voting_open(self):
        """
        Voting is open only before kickoff and only for scheduled matches.
        """
        return (
            self.status == self.STATUS_SCHEDULED
            and timezone.now() < self.kickoff_time
        )

    @property
    def has_result(self):
        """
        A match has a result once the result field contains home, draw or away.
        """
        return self.result is not None and self.result != ""

    @property
    def score_display(self):
        """
        Returns a readable score if both scores are available.
        """
        if self.home_score is None or self.away_score is None:
            return "No score yet"

        return f"{self.home_score}-{self.away_score}"

    def calculate_result_from_score(self):
        """
        Works out the match outcome from the stored final score.

        This is used for normal result-based prediction scoring:
        - home score greater than away score = home win
        - equal scores = draw
        - away score greater than home score = away win
        """
        if self.home_score is None or self.away_score is None:
            return None

        if self.home_score > self.away_score:
            return self.RESULT_HOME

        if self.home_score < self.away_score:
            return self.RESULT_AWAY

        return self.RESULT_DRAW

    def save(self, *args, **kwargs):
        """
        If the match is marked as finished and both scores are available,
        automatically set the result from the final score.

        The result can still be corrected manually in admin if needed.
        """
        if self.status == self.STATUS_FINISHED:
            calculated_result = self.calculate_result_from_score()

            if calculated_result is not None:
                self.result = calculated_result

        super().save(*args, **kwargs)


class Prediction(models.Model):
    """
    Stores one user's prediction for one match.

    A prediction is no longer tied to a specific group because the same pick
    should count across every league the user belongs to.
    """

    PREDICTION_HOME = "home"
    PREDICTION_DRAW = "draw"
    PREDICTION_AWAY = "away"

    PREDICTION_CHOICES = [
        (PREDICTION_HOME, "Home team win"),
        (PREDICTION_DRAW, "Draw"),
        (PREDICTION_AWAY, "Away team win"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="predictions",
    )
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="predictions",
    )
    prediction = models.CharField(
        max_length=10,
        choices=PREDICTION_CHOICES,
    )
    points_awarded = models.PositiveIntegerField(default=0)

    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "match"]
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.user.username} predicted {self.prediction} for {self.match}"

    def calculate_points(self):
        """
        Returns 3 points if the prediction matches the match result.
        Otherwise, returns 0.
        """
        if not self.match.has_result:
            return 0

        if self.prediction == self.match.result:
            return 3

        return 0

    def save(self, *args, **kwargs):
        """
        Whenever a prediction is saved, points are recalculated based on
        the current match result.
        """
        self.points_awarded = self.calculate_points()
        super().save(*args, **kwargs)