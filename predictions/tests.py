from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import CompetitionGroup, GroupMember, Match, Prediction


User = get_user_model()


class MatchPickUpdateOneTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            password="Testpass123!",
        )

        self.aryan = User.objects.create_user(
            username="aryan",
            password="Testpass123!",
        )

        self.friend = User.objects.create_user(
            username="friend",
            password="Testpass123!",
        )

        self.family = CompetitionGroup.objects.create(
            name="Family League",
            invite_code="FAMILY26",
            created_by=self.owner,
        )

        self.friends = CompetitionGroup.objects.create(
            name="Friends League",
            invite_code="FRIENDS26",
            created_by=self.owner,
        )

        GroupMember.objects.create(
            user=self.aryan,
            group=self.family,
            role=GroupMember.ROLE_MEMBER,
        )

        GroupMember.objects.create(
            user=self.friend,
            group=self.friends,
            role=GroupMember.ROLE_MEMBER,
        )

    def create_match(
        self,
        home_team="Argentina",
        away_team="Brazil",
        kickoff_delta_hours=24,
        status=None,
        result=None,
    ):
        if status is None:
            status = Match.STATUS_SCHEDULED

        return Match.objects.create(
            home_team=home_team,
            away_team=away_team,
            kickoff_time=timezone.now() + timedelta(hours=kickoff_delta_hours),
            stage=Match.STAGE_GROUP,
            status=status,
            result=result,
        )

    def login_as_aryan(self):
        self.client.login(username="aryan", password="Testpass123!")

    def test_user_can_join_second_league_after_registration(self):
        self.login_as_aryan()

        response = self.client.post(
            reverse("leagues"),
            {
                "invite_code": "FRIENDS26",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            GroupMember.objects.filter(
                user=self.aryan,
                group=self.friends,
            ).exists()
        )

    def test_user_cannot_join_same_league_twice(self):
        self.login_as_aryan()

        self.client.post(
            reverse("leagues"),
            {
                "invite_code": "FAMILY26",
            },
            follow=True,
        )

        membership_count = GroupMember.objects.filter(
            user=self.aryan,
            group=self.family,
        ).count()

        self.assertEqual(membership_count, 1)

    def test_one_prediction_is_synced_across_all_user_leagues(self):
        GroupMember.objects.create(
            user=self.aryan,
            group=self.friends,
            role=GroupMember.ROLE_MEMBER,
        )

        match = self.create_match()

        self.login_as_aryan()

        response = self.client.post(
            reverse("submit_prediction", args=[match.id]),
            {
                "prediction": Prediction.PREDICTION_HOME,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        predictions = Prediction.objects.filter(
            user=self.aryan,
            match=match,
        )

        self.assertEqual(predictions.count(), 2)

        prediction_values = set(
            predictions.values_list("prediction", flat=True)
        )

        self.assertEqual(prediction_values, {Prediction.PREDICTION_HOME})

    def test_prediction_is_blocked_more_than_48_hours_before_kickoff(self):
        match = self.create_match(kickoff_delta_hours=72)

        self.login_as_aryan()

        self.client.post(
            reverse("submit_prediction", args=[match.id]),
            {
                "prediction": Prediction.PREDICTION_HOME,
            },
            follow=True,
        )

        self.assertFalse(
            Prediction.objects.filter(
                user=self.aryan,
                match=match,
            ).exists()
        )

    def test_prediction_is_blocked_for_placeholder_teams(self):
        match = self.create_match(
            home_team="Winner Group A",
            away_team="Runner-up Group B",
            kickoff_delta_hours=24,
        )

        self.login_as_aryan()

        self.client.post(
            reverse("submit_prediction", args=[match.id]),
            {
                "prediction": Prediction.PREDICTION_HOME,
            },
            follow=True,
        )

        self.assertFalse(
            Prediction.objects.filter(
                user=self.aryan,
                match=match,
            ).exists()
        )

    def test_global_leaderboard_is_visible_to_logged_in_users(self):
        self.login_as_aryan()

        response = self.client.get(reverse("leaderboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Global Leaderboard")
        self.assertContains(response, "aryan")
        self.assertContains(response, "friend")

    def test_global_leaderboard_requires_login(self):
        response = self.client.get(reverse("leaderboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_league_detail_only_shows_members_of_that_league(self):
        self.login_as_aryan()

        response = self.client.get(
            reverse("league_detail", args=[self.family.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Family League")
        self.assertContains(response, "aryan")
        self.assertNotContains(response, "friend")

    def test_user_cannot_view_league_they_are_not_a_member_of(self):
        self.login_as_aryan()

        response = self.client.get(
            reverse("league_detail", args=[self.friends.id]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You are not a member of that league.")

    def test_league_and_global_leaderboards_use_same_prediction_points(self):
        GroupMember.objects.create(
            user=self.aryan,
            group=self.friends,
            role=GroupMember.ROLE_MEMBER,
        )

        finished_match = Match.objects.create(
            home_team="Argentina",
            away_team="Brazil",
            kickoff_time=timezone.now() - timedelta(hours=2),
            stage=Match.STAGE_GROUP,
            status=Match.STATUS_FINISHED,
            home_score=2,
            away_score=1,
            result=Match.RESULT_HOME,
        )

        Prediction.objects.create(
            user=self.aryan,
            group=self.family,
            match=finished_match,
            prediction=Prediction.PREDICTION_HOME,
        )

        self.login_as_aryan()

        global_response = self.client.get(reverse("leaderboard"))
        family_response = self.client.get(
            reverse("league_detail", args=[self.family.id])
        )
        friends_response = self.client.get(
            reverse("league_detail", args=[self.friends.id])
        )

        self.assertContains(global_response, "3")
        self.assertContains(family_response, "3")
        self.assertContains(friends_response, "3")