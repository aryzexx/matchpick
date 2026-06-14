import uuid

from django.conf import settings
from django.db import models


TEAM_FLAG_MAP = {
    "algeria": "🇩🇿",
    "argentina": "🇦🇷",
    "australia": "🇦🇺",
    "austria": "🇦🇹",
    "belgium": "🇧🇪",
    "bosnia and herzegovina": "🇧🇦",
    "bosnia & herzegovina": "🇧🇦",
    "bosnia-herzegovina": "🇧🇦",
    "bosnia herzegovina": "🇧🇦",
    "bosnia": "🇧🇦",
    "brazil": "🇧🇷",
    "canada": "🇨🇦",
    "cape verde": "🇨🇻",
    "colombia": "🇨🇴",
    "croatia": "🇭🇷",
    "curacao": "🇨🇼",
    "curaçao": "🇨🇼",
    "czechia": "🇨🇿",
    "czech republic": "🇨🇿",
    "dr congo": "🇨🇩",
    "d.r. congo": "🇨🇩",
    "democratic republic of the congo": "🇨🇩",
    "ecuador": "🇪🇨",
    "egypt": "🇪🇬",
    "england": "🏴",
    "france": "🇫🇷",
    "germany": "🇩🇪",
    "ghana": "🇬🇭",
    "haiti": "🇭🇹",
    "iran": "🇮🇷",
    "iraq": "🇮🇶",
    "ivory coast": "🇨🇮",
    "cote d'ivoire": "🇨🇮",
    "côte d'ivoire": "🇨🇮",
    "côte d’ivoire": "🇨🇮",
    "japan": "🇯🇵",
    "jordan": "🇯🇴",
    "mexico": "🇲🇽",
    "morocco": "🇲🇦",
    "netherlands": "🇳🇱",
    "new zealand": "🇳🇿",
    "norway": "🇳🇴",
    "panama": "🇵🇦",
    "paraguay": "🇵🇾",
    "portugal": "🇵🇹",
    "qatar": "🇶🇦",
    "saudi arabia": "🇸🇦",
    "scotland": "🏴",
    "senegal": "🇸🇳",
    "south africa": "🇿🇦",
    "south korea": "🇰🇷",
    "korea republic": "🇰🇷",
    "republic of korea": "🇰🇷",
    "spain": "🇪🇸",
    "sweden": "🇸🇪",
    "switzerland": "🇨🇭",
    "tunisia": "🇹🇳",
    "turkey": "🇹🇷",
    "turkiye": "🇹🇷",
    "türkiye": "🇹🇷",
    "united states": "🇺🇸",
    "united states of america": "🇺🇸",
    "usa": "🇺🇸",
    "uruguay": "🇺🇾",
    "uzbekistan": "🇺🇿",
}


TEAM_FLAG_CODE_MAP = {
    "algeria": "dz",
    "argentina": "ar",
    "australia": "au",
    "austria": "at",
    "belgium": "be",
    "bosnia and herzegovina": "ba",
    "bosnia & herzegovina": "ba",
    "bosnia-herzegovina": "ba",
    "bosnia herzegovina": "ba",
    "bosnia": "ba",
    "brazil": "br",
    "canada": "ca",
    "cape verde": "cv",
    "colombia": "co",
    "croatia": "hr",
    "curacao": "cw",
    "curaçao": "cw",
    "czechia": "cz",
    "czech republic": "cz",
    "dr congo": "cd",
    "d.r. congo": "cd",
    "democratic republic of the congo": "cd",
    "ecuador": "ec",
    "egypt": "eg",
    "england": "gb-eng",
    "france": "fr",
    "germany": "de",
    "ghana": "gh",
    "haiti": "ht",
    "iran": "ir",
    "iraq": "iq",
    "ivory coast": "ci",
    "cote d'ivoire": "ci",
    "côte d'ivoire": "ci",
    "côte d’ivoire": "ci",
    "japan": "jp",
    "jordan": "jo",
    "mexico": "mx",
    "morocco": "ma",
    "netherlands": "nl",
    "new zealand": "nz",
    "norway": "no",
    "panama": "pa",
    "paraguay": "py",
    "portugal": "pt",
    "qatar": "qa",
    "saudi arabia": "sa",
    "scotland": "gb-sct",
    "senegal": "sn",
    "south africa": "za",
    "south korea": "kr",
    "korea republic": "kr",
    "republic of korea": "kr",
    "spain": "es",
    "sweden": "se",
    "switzerland": "ch",
    "tunisia": "tn",
    "turkey": "tr",
    "turkiye": "tr",
    "türkiye": "tr",
    "united states": "us",
    "united states of america": "us",
    "usa": "us",
    "uruguay": "uy",
    "uzbekistan": "uz",
}


def normalise_team_name(team_name):
    if not team_name:
        return ""

    return team_name.strip().lower()


def get_team_flag(team_name):
    return TEAM_FLAG_MAP.get(normalise_team_name(team_name), "")


def get_team_flag_code(team_name):
    return TEAM_FLAG_CODE_MAP.get(normalise_team_name(team_name), "")


def get_team_flag_url(team_name):
    flag_code = get_team_flag_code(team_name)

    if not flag_code:
        return ""

    return f"https://flagcdn.com/w40/{flag_code}.png"


def team_name_with_flag(team_name):
    flag = get_team_flag(team_name)

    if flag:
        return f"{flag} {team_name}"

    return team_name


class CompetitionGroup(models.Model):
    name = models.CharField(max_length=100)
    invite_code = models.CharField(max_length=20, unique=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_prediction_groups",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = uuid.uuid4().hex[:8].upper()

        self.invite_code = self.invite_code.upper()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class GroupMember(models.Model):
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
        related_name="prediction_group_memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_MEMBER,
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["group", "user"]
        ordering = ["group__name", "user__username"]

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"


class Match(models.Model):
    STATUS_SCHEDULED = "scheduled"
    STATUS_FINISHED = "finished"

    STATUS_CHOICES = [
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_FINISHED, "Finished"),
    ]

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
        (STAGE_QUARTER_FINAL, "Quarter Final"),
        (STAGE_SEMI_FINAL, "Semi Final"),
        (STAGE_THIRD_PLACE, "Third Place Play-off"),
        (STAGE_FINAL, "Final"),
    ]

    RESULT_HOME = "home"
    RESULT_DRAW = "draw"
    RESULT_AWAY = "away"

    RESULT_CHOICES = [
        (RESULT_HOME, "Home win"),
        (RESULT_DRAW, "Draw"),
        (RESULT_AWAY, "Away win"),
    ]

    external_source = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )
    external_match_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
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
    home_score = models.PositiveIntegerField(
        null=True,
        blank=True,
    )
    away_score = models.PositiveIntegerField(
        null=True,
        blank=True,
    )
    result = models.CharField(
        max_length=10,
        choices=RESULT_CHOICES,
        blank=True,
        null=True,
    )
    last_synced_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["kickoff_time", "home_team"]
        constraints = [
            models.UniqueConstraint(
                fields=["external_source", "external_match_id"],
                name="unique_external_match",
            )
        ]

    @property
    def has_result(self):
        return self.result in {
            self.RESULT_HOME,
            self.RESULT_DRAW,
            self.RESULT_AWAY,
        }

    @property
    def score_display(self):
        if self.home_score is None or self.away_score is None:
            return "Not played"

        return f"{self.home_score} - {self.away_score}"

    @property
    def home_team_flag(self):
        return get_team_flag(self.home_team)

    @property
    def away_team_flag(self):
        return get_team_flag(self.away_team)

    @property
    def home_team_flag_code(self):
        return get_team_flag_code(self.home_team)

    @property
    def away_team_flag_code(self):
        return get_team_flag_code(self.away_team)

    @property
    def home_team_flag_url(self):
        return get_team_flag_url(self.home_team)

    @property
    def away_team_flag_url(self):
        return get_team_flag_url(self.away_team)

    @property
    def home_team_with_flag(self):
        return team_name_with_flag(self.home_team)

    @property
    def away_team_with_flag(self):
        return team_name_with_flag(self.away_team)

    @property
    def display_name_with_flags(self):
        return f"{self.home_team_with_flag} vs {self.away_team_with_flag}"

    @property
    def display_name_plain(self):
        return f"{self.home_team} vs {self.away_team}"

    def calculate_result_from_score(self):
        """
        Calculates the match result from the stored score.

        This method is used by the result sync management command, so it must
        remain available even though the model also auto-calculates the result
        when a finished match is saved.
        """
        if self.home_score is None or self.away_score is None:
            return None

        if self.home_score > self.away_score:
            return self.RESULT_HOME

        if self.home_score < self.away_score:
            return self.RESULT_AWAY

        return self.RESULT_DRAW

    def save(self, *args, **kwargs):
        if self.status == self.STATUS_FINISHED:
            calculated_result = self.calculate_result_from_score()

            if calculated_result:
                self.result = calculated_result

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"


class Prediction(models.Model):
    """
    Stores one user's prediction for one match.

    A user can belong to multiple leagues, but the prediction itself is only
    stored once. The same prediction is then used when calculating every league
    leaderboard that the user is part of.
    """

    PREDICTION_HOME = "home"
    PREDICTION_DRAW = "draw"
    PREDICTION_AWAY = "away"

    PREDICTION_CHOICES = [
        (PREDICTION_HOME, "Home win"),
        (PREDICTION_DRAW, "Draw"),
        (PREDICTION_AWAY, "Away win"),
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

    def calculate_points(self):
        if not self.match.has_result:
            return 0

        if self.prediction == self.match.result:
            return 3

        return 0

    def save(self, *args, **kwargs):
        self.points_awarded = self.calculate_points()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.match} - {self.prediction}"