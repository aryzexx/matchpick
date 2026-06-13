from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import CompetitionGroup, GroupMember, Match, Prediction


class MatchPickCoreTests(TestCase):
    """
    Automated tests for the core MatchPick application workflow.

    These tests cover:
    - data minimisation during registration
    - invite-code joining
    - protected pages
    - prediction voting
    - voting lock rules
    - result calculation
    - leaderboard behaviour
    - password hashing
    """

    def setUp(self):
        """
        Creates reusable test data for the test suite.
        """

        self.admin_user = User.objects.create_user(
            username="adminuser",
            password="AdminPass123!",
            is_staff=True,
            is_superuser=True,
        )

        self.normal_user = User.objects.create_user(
            username="testuser1",
            password="TestPass123!",
        )

        self.second_user = User.objects.create_user(
            username="testuser2",
            password="TestPass123!",
        )

        self.group = CompetitionGroup.objects.create(
            name="Family League",
            invite_code="FAMILY26",
            created_by=self.admin_user,
        )

        GroupMember.objects.create(
            user=self.normal_user,
            group=self.group,
            role=GroupMember.ROLE_MEMBER,
        )

        GroupMember.objects.create(
            user=self.second_user,
            group=self.group,
            role=GroupMember.ROLE_MEMBER,
        )

        self.future_match = Match.objects.create(
            home_team="Argentina",
            away_team="Spain",
            kickoff_time=timezone.now() + timedelta(days=10),
            stage=Match.STAGE_GROUP,
            status=Match.STATUS_SCHEDULED,
        )

        self.past_match = Match.objects.create(
            home_team="England",
            away_team="Brazil",
            kickoff_time=timezone.now() - timedelta(days=1),
            stage=Match.STAGE_GROUP,
            status=Match.STATUS_FINISHED,
            home_score=2,
            away_score=1,
        )

    def test_password_is_hashed_not_stored_as_plaintext(self):
        """
        Confirms that Django stores a password hash rather than the raw password.
        """

        user = User.objects.get(username="testuser1")

        self.assertNotEqual(user.password, "TestPass123!")
        self.assertTrue(user.check_password("TestPass123!"))

    def test_registration_rejects_invalid_invite_code(self):
        """
        Confirms that users cannot register with a fake invite code.
        """

        response = self.client.post(
            reverse("register"),
            {
                "username": "badinviteuser",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
                "invite_code": "WRONGCODE",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="badinviteuser").exists())
        self.assertContains(response, "This invite code is not valid")

    def test_registration_with_valid_invite_creates_user_and_membership(self):
        """
        Confirms that a valid invite code creates both a user and group membership.
        """

        response = self.client.post(
            reverse("register"),
            {
                "username": "newmember",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
                "invite_code": "FAMILY26",
            },
        )

        self.assertEqual(response.status_code, 302)

        user = User.objects.get(username="newmember")

        self.assertEqual(user.email, "")
        self.assertTrue(
            GroupMember.objects.filter(user=user, group=self.group).exists()
        )

    def test_matches_page_requires_login(self):
        """
        Confirms that logged-out visitors cannot view the matches page.
        """

        response = self.client.get(reverse("matches"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_leaderboard_page_requires_login(self):
        """
        Confirms that logged-out visitors cannot view the leaderboard page.
        """

        response = self.client.get(reverse("leaderboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_normal_user_does_not_see_admin_link(self):
        """
        Confirms that normal users do not see the admin navigation link.
        """

        self.client.login(username="testuser1", password="TestPass123!")

        response = self.client.get(reverse("matches"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'href="/admin/"')

    def test_staff_user_can_see_admin_link(self):
        """
        Confirms that staff/admin users can see the admin navigation link.
        """

        self.client.login(username="adminuser", password="AdminPass123!")

        response = self.client.get(reverse("matches"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/admin/"')

    def test_prediction_can_be_created_before_kickoff(self):
        """
        Confirms that a logged-in group member can submit a prediction
        before kickoff.
        """

        self.client.login(username="testuser1", password="TestPass123!")

        response = self.client.post(
            reverse("submit_prediction", args=[self.future_match.id]),
            {
                "prediction": Prediction.PREDICTION_HOME,
            },
        )

        self.assertEqual(response.status_code, 302)

        prediction = Prediction.objects.get(
            user=self.normal_user,
            group=self.group,
            match=self.future_match,
        )

        self.assertEqual(prediction.prediction, Prediction.PREDICTION_HOME)

    def test_prediction_can_be_updated_before_kickoff(self):
        """
        Confirms that a user can update their prediction before kickoff
        without creating duplicate prediction rows.
        """

        self.client.login(username="testuser1", password="TestPass123!")

        self.client.post(
            reverse("submit_prediction", args=[self.future_match.id]),
            {
                "prediction": Prediction.PREDICTION_HOME,
            },
        )

        self.client.post(
            reverse("submit_prediction", args=[self.future_match.id]),
            {
                "prediction": Prediction.PREDICTION_AWAY,
            },
        )

        predictions = Prediction.objects.filter(
            user=self.normal_user,
            group=self.group,
            match=self.future_match,
        )

        self.assertEqual(predictions.count(), 1)
        self.assertEqual(predictions.first().prediction, Prediction.PREDICTION_AWAY)

    def test_prediction_is_rejected_after_voting_locked(self):
        """
        Confirms that users cannot vote once a match is no longer open.
        """

        self.client.login(username="testuser1", password="TestPass123!")

        response = self.client.post(
            reverse("submit_prediction", args=[self.past_match.id]),
            {
                "prediction": Prediction.PREDICTION_HOME,
            },
        )

        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            Prediction.objects.filter(
                user=self.normal_user,
                group=self.group,
                match=self.past_match,
            ).exists()
        )

    def test_prediction_is_rejected_for_user_without_group(self):
        """
        Confirms that a logged-in user without group membership cannot vote.
        """

        no_group_user = User.objects.create_user(
            username="nogroup",
            password="TestPass123!",
        )

        self.client.login(username="nogroup", password="TestPass123!")

        response = self.client.post(
            reverse("submit_prediction", args=[self.future_match.id]),
            {
                "prediction": Prediction.PREDICTION_HOME,
            },
        )

        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            Prediction.objects.filter(
                user=no_group_user,
                match=self.future_match,
            ).exists()
        )

    def test_match_result_is_calculated_from_finished_score(self):
        """
        Confirms that a finished match with a score automatically gets a result.
        """

        match = Match.objects.create(
            home_team="France",
            away_team="Germany",
            kickoff_time=timezone.now() - timedelta(days=1),
            stage=Match.STAGE_GROUP,
            status=Match.STATUS_FINISHED,
            home_score=1,
            away_score=1,
        )

        self.assertEqual(match.result, Match.RESULT_DRAW)

    def test_prediction_points_awarded_when_prediction_matches_result(self):
        """
        Confirms that correct predictions are worth 3 points.
        """

        finished_match = Match.objects.create(
            home_team="Portugal",
            away_team="Netherlands",
            kickoff_time=timezone.now() - timedelta(days=1),
            stage=Match.STAGE_GROUP,
            status=Match.STATUS_FINISHED,
            home_score=3,
            away_score=0,
        )

        prediction = Prediction.objects.create(
            user=self.normal_user,
            group=self.group,
            match=finished_match,
            prediction=Prediction.PREDICTION_HOME,
        )

        self.assertEqual(prediction.points_awarded, 3)

    def test_prediction_points_zero_when_prediction_is_wrong(self):
        """
        Confirms that incorrect predictions are worth 0 points.
        """

        finished_match = Match.objects.create(
            home_team="Japan",
            away_team="USA",
            kickoff_time=timezone.now() - timedelta(days=1),
            stage=Match.STAGE_GROUP,
            status=Match.STATUS_FINISHED,
            home_score=0,
            away_score=2,
        )

        prediction = Prediction.objects.create(
            user=self.normal_user,
            group=self.group,
            match=finished_match,
            prediction=Prediction.PREDICTION_HOME,
        )

        self.assertEqual(prediction.points_awarded, 0)

    def test_leaderboard_displays_group_members_and_points(self):
        """
        Confirms that the leaderboard page displays real group members and points.
        """

        finished_match = Match.objects.create(
            home_team="Morocco",
            away_team="Croatia",
            kickoff_time=timezone.now() - timedelta(days=1),
            stage=Match.STAGE_GROUP,
            status=Match.STATUS_FINISHED,
            home_score=2,
            away_score=0,
        )

        Prediction.objects.create(
            user=self.normal_user,
            group=self.group,
            match=finished_match,
            prediction=Prediction.PREDICTION_HOME,
        )

        Prediction.objects.create(
            user=self.second_user,
            group=self.group,
            match=finished_match,
            prediction=Prediction.PREDICTION_AWAY,
        )

        self.client.login(username="testuser1", password="TestPass123!")

        response = self.client.get(reverse("leaderboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser1")
        self.assertContains(response, "testuser2")
        self.assertContains(response, "3")
        self.assertContains(response, "You")