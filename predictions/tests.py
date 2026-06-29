from datetime import timedelta
from unittest.mock import patch

from django.contrib import admin as django_admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .admin import MatchAdmin
from .data.fifa_rankings_snapshot import get_team_ranking, is_placeholder_team_name
from .models import CompetitionGroup, GroupMember, Match, Prediction
from .views import build_pick_style, build_user_vs_crowd


User = get_user_model()


class MatchPickUpdateThreeTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            password="Testpass123!",
        )

        self.staff_user = User.objects.create_user(
            username="staffadmin",
            password="Testpass123!",
            is_staff=True,
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
            role=GroupMember.ROLE_ADMIN,
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
        home_score=None,
        away_score=None,
        stage=Match.STAGE_GROUP,
        qualified_team=None,
        kickoff_time=None,
    ):
        if status is None:
            status = Match.STATUS_SCHEDULED

        if kickoff_time is None:
            kickoff_time = timezone.now() + timedelta(hours=kickoff_delta_hours)

        return Match.objects.create(
            home_team=home_team,
            away_team=away_team,
            kickoff_time=kickoff_time,
            stage=stage,
            status=status,
            result=result,
            home_score=home_score,
            away_score=away_score,
            qualified_team=qualified_team,
        )

    def login_as_aryan(self):
        self.client.login(username="aryan", password="Testpass123!")

    def login_as_staff(self):
        self.client.login(username="staffadmin", password="Testpass123!")

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

    def test_one_prediction_is_stored_once_even_across_multiple_leagues(self):
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

        self.assertEqual(predictions.count(), 1)
        self.assertEqual(predictions.first().prediction, Prediction.PREDICTION_HOME)

    def test_prediction_update_changes_same_row_not_new_row(self):
        match = self.create_match()

        self.login_as_aryan()

        self.client.post(
            reverse("submit_prediction", args=[match.id]),
            {
                "prediction": Prediction.PREDICTION_HOME,
            },
            follow=True,
        )

        self.client.post(
            reverse("submit_prediction", args=[match.id]),
            {
                "prediction": Prediction.PREDICTION_AWAY,
            },
            follow=True,
        )

        predictions = Prediction.objects.filter(
            user=self.aryan,
            match=match,
        )

        self.assertEqual(predictions.count(), 1)
        self.assertEqual(predictions.first().prediction, Prediction.PREDICTION_AWAY)

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

        response = self.client.get(reverse("league_detail", args=[self.family.id]))

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

    def test_leaderboard_shows_clearer_columns(self):
        self.login_as_aryan()

        response = self.client.get(reverse("leaderboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Correct Picks")
        self.assertContains(response, "Incorrect Picks")
        self.assertContains(response, "Missed Picks")
        self.assertContains(response, "Accuracy")

    def test_leaderboard_rows_link_to_user_picks_pages(self):
        GroupMember.objects.create(
            user=self.friend,
            group=self.family,
            role=GroupMember.ROLE_MEMBER,
        )

        self.login_as_aryan()

        global_response = self.client.get(reverse("leaderboard"))
        league_response = self.client.get(reverse("league_detail", args=[self.family.id]))

        self.assertEqual(global_response.status_code, 200)
        self.assertEqual(league_response.status_code, 200)
        self.assertContains(global_response, reverse("user_picks", args=[self.aryan.id]))
        self.assertContains(league_response, reverse("user_picks", args=[self.friend.id]))

    def test_matches_page_shows_personal_prediction_progress_cards(self):
        self.create_match(kickoff_delta_hours=24)

        self.login_as_aryan()

        response = self.client.get(reverse("matches"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your prediction progress")
        self.assertContains(response, "Open Matches")
        self.assertContains(response, "Picks Made")
        self.assertContains(response, "Still Pending")

    def test_match_admin_voting_status_uses_current_voting_rules(self):
        open_match = self.create_match(kickoff_delta_hours=24)
        finished_match = self.create_match(
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            home_score=2,
            away_score=1,
        )
        match_admin = MatchAdmin(Match, django_admin.site)

        self.assertEqual(match_admin.voting_status(open_match), "Open")
        self.assertEqual(match_admin.voting_status(finished_match), "Locked")

    def test_match_admin_flags_finished_knockout_missing_qualified_team(self):
        match = self.create_match(
            home_team="France",
            away_team="Germany",
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            home_score=1,
            away_score=1,
            stage=Match.STAGE_ROUND_OF_16,
        )
        match_admin = MatchAdmin(Match, django_admin.site)

        self.assertEqual(
            match_admin.qualification_status(match),
            "Needs qualified team",
        )

    def test_matches_page_renders_collapse_controls(self):
        self.create_match(kickoff_delta_hours=24)

        self.login_as_aryan()

        response = self.client.get(reverse("matches"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "matches-v2-card is-collapsed")
        self.assertContains(response, "matches-v2-collapse-toggle")
        self.assertContains(response, "Expand Argentina vs Brazil")

    def test_matches_page_defaults_to_open_filter_without_all_tab(self):
        self.create_match(kickoff_delta_hours=24)

        self.login_as_aryan()

        response = self.client.get(reverse("matches"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Open Now")
        self.assertContains(response, 'data-filter="open"')
        self.assertNotContains(response, 'data-filter="all"')

    def test_collapsed_match_summary_includes_essential_match_details(self):
        self.create_match(kickoff_delta_hours=24)

        self.login_as_aryan()

        response = self.client.get(reverse("matches"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "matches-v2-collapsed-summary")
        self.assertContains(response, "Argentina")
        self.assertContains(response, "Brazil")
        self.assertContains(response, "Voting Open")
        self.assertContains(response, "Awaiting Result")

    def test_collapsed_match_summary_shows_finished_user_outcome_indicator(self):
        finished_match = self.create_match(
            home_team="Argentina",
            away_team="Brazil",
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            home_score=2,
            away_score=1,
        )

        Prediction.objects.create(
            user=self.aryan,
            match=finished_match,
            prediction=Prediction.PREDICTION_HOME,
        )

        self.login_as_aryan()

        response = self.client.get(reverse("matches"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "matches-v2-outcome-indicator outcome-win")
        self.assertContains(response, "Your pick was correct")

    def test_logged_in_user_can_access_my_picks(self):
        match = self.create_match(kickoff_delta_hours=24)

        Prediction.objects.create(
            user=self.aryan,
            match=match,
            prediction=Prediction.PREDICTION_HOME,
        )

        self.login_as_aryan()

        response = self.client.get(reverse("my_picks"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Dashboard")
        self.assertContains(response, "My Stats")
        self.assertContains(response, "My Picks")

    def test_navbar_shows_my_dashboard_instead_of_my_picks(self):
        self.login_as_aryan()

        response = self.client.get(reverse("matches"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Dashboard")
        self.assertNotContains(response, ">My Picks</a>", html=False)

    def test_my_picks_defaults_to_my_stats(self):
        self.login_as_aryan()

        response = self.client.get(reverse("my_picks"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Personal Stage Accuracy")
        self.assertContains(response, "User vs Crowd")
        self.assertContains(response, "Pick Style")

    def test_my_picks_history_alias_still_shows_pick_history(self):
        match = self.create_match(kickoff_delta_hours=24)

        Prediction.objects.create(
            user=self.aryan,
            match=match,
            prediction=Prediction.PREDICTION_HOME,
        )

        self.login_as_aryan()

        response = self.client.get(f"{reverse('my_picks')}?tab=history")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your saved picks")
        self.assertContains(response, "Argentina")
        self.assertContains(response, "Argentina flag")
        self.assertContains(response, "Home win")

    def test_my_picks_tab_shows_pick_history(self):
        match = self.create_match(kickoff_delta_hours=24)

        Prediction.objects.create(
            user=self.aryan,
            match=match,
            prediction=Prediction.PREDICTION_HOME,
        )

        self.login_as_aryan()

        response = self.client.get(f"{reverse('my_picks')}?tab=picks")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your saved picks")
        self.assertContains(response, "Argentina")

    def test_user_picks_self_view_shows_open_picks(self):
        open_match = self.create_match(
            home_team="Canada",
            away_team="Mexico",
            kickoff_delta_hours=24,
        )

        Prediction.objects.create(
            user=self.aryan,
            match=open_match,
            prediction=Prediction.PREDICTION_HOME,
        )

        self.login_as_aryan()

        response = self.client.get(
            f"{reverse('user_picks', args=[self.aryan.id])}?tab=picks"
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Canada")
        self.assertContains(response, "my-picks-choice")

    def test_other_user_picks_hides_open_picks(self):
        open_match = self.create_match(
            home_team="Canada",
            away_team="Mexico",
            kickoff_delta_hours=24,
        )

        Prediction.objects.create(
            user=self.friend,
            match=open_match,
            prediction=Prediction.PREDICTION_AWAY,
        )

        self.login_as_aryan()

        response = self.client.get(
            f"{reverse('user_picks', args=[self.friend.id])}?tab=picks"
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Only locked and finished picks are shown for fairness.")
        self.assertNotContains(response, "Canada")
        self.assertNotContains(response, "Mexico")

    def test_other_user_picks_shows_locked_and_finished_picks(self):
        locked_match = self.create_match(
            home_team="France",
            away_team="Germany",
            kickoff_delta_hours=-1,
        )
        finished_match = self.create_match(
            home_team="Argentina",
            away_team="Brazil",
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            home_score=2,
            away_score=1,
        )

        Prediction.objects.create(
            user=self.friend,
            match=locked_match,
            prediction=Prediction.PREDICTION_DRAW,
        )
        Prediction.objects.create(
            user=self.friend,
            match=finished_match,
            prediction=Prediction.PREDICTION_AWAY,
        )

        self.login_as_aryan()

        response = self.client.get(
            f"{reverse('user_picks', args=[self.friend.id])}?tab=picks"
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "friend&#x27;s past picks")
        self.assertContains(response, "France")
        self.assertContains(response, "Argentina")

    def test_other_user_picks_are_read_only(self):
        locked_match = self.create_match(
            home_team="France",
            away_team="Germany",
            kickoff_delta_hours=-1,
        )

        Prediction.objects.create(
            user=self.friend,
            match=locked_match,
            prediction=Prediction.PREDICTION_DRAW,
        )

        self.login_as_aryan()

        response = self.client.get(
            f"{reverse('user_picks', args=[self.friend.id])}?tab=picks"
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Read-only")
        self.assertNotContains(response, "my-picks-choice")
        self.assertNotContains(response, 'name="prediction"')

    def test_anonymous_user_is_redirected_from_my_picks(self):
        response = self.client.get(f"{reverse('my_picks')}?tab=picks")

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_my_picks_only_shows_matches_current_user_has_picked(self):
        picked_match = self.create_match(
            home_team="Argentina",
            away_team="Brazil",
            kickoff_delta_hours=24,
        )
        unpicked_match = self.create_match(
            home_team="France",
            away_team="Germany",
            kickoff_delta_hours=24,
        )

        Prediction.objects.create(
            user=self.aryan,
            match=picked_match,
            prediction=Prediction.PREDICTION_HOME,
        )
        Prediction.objects.create(
            user=self.friend,
            match=unpicked_match,
            prediction=Prediction.PREDICTION_AWAY,
        )

        self.login_as_aryan()

        response = self.client.get(f"{reverse('my_picks')}?tab=picks")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Argentina")
        self.assertNotContains(response, "France")

    def test_open_picked_match_can_be_changed_from_my_picks(self):
        match = self.create_match(kickoff_delta_hours=24)

        Prediction.objects.create(
            user=self.aryan,
            match=match,
            prediction=Prediction.PREDICTION_HOME,
        )

        self.login_as_aryan()

        response = self.client.get(f"{reverse('my_picks')}?tab=picks")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Draw")
        self.assertContains(response, "selected")

        response = self.client.post(
            reverse("submit_prediction", args=[match.id]),
            {
                "prediction": Prediction.PREDICTION_AWAY,
                "next": f"{reverse('my_picks')}?tab=picks",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Dashboard")

        prediction = Prediction.objects.get(user=self.aryan, match=match)

        self.assertEqual(prediction.prediction, Prediction.PREDICTION_AWAY)

    def test_group_match_still_allows_draw_prediction_button(self):
        self.create_match(kickoff_delta_hours=24)

        self.login_as_aryan()

        response = self.client.get(reverse("matches"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your prediction")
        self.assertContains(response, 'value="draw"')
        self.assertContains(response, "Draw")

    def test_knockout_match_hides_draw_prediction_button(self):
        self.create_match(
            home_team="France",
            away_team="Germany",
            kickoff_delta_hours=24,
            stage=Match.STAGE_ROUND_OF_16,
        )

        self.login_as_aryan()

        response = self.client.get(reverse("matches"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Who qualifies?")
        self.assertContains(response, "Selection pending")
        self.assertContains(response, "France")
        self.assertContains(response, "Germany")
        self.assertNotContains(response, "France qualifies")
        self.assertNotContains(response, "Germany qualifies")
        self.assertNotContains(response, 'value="draw"')

    def test_knockout_match_shows_selected_team_in_question_line(self):
        match = self.create_match(
            home_team="France",
            away_team="Germany",
            kickoff_delta_hours=24,
            stage=Match.STAGE_ROUND_OF_16,
        )

        Prediction.objects.create(
            user=self.aryan,
            match=match,
            prediction=Prediction.PREDICTION_AWAY,
        )

        self.login_as_aryan()

        response = self.client.get(reverse("matches"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "You predicted: Germany to qualify for the next round",
        )
        self.assertNotContains(response, "Current pick:")

    def test_knockout_match_rejects_draw_prediction(self):
        match = self.create_match(
            home_team="France",
            away_team="Germany",
            kickoff_delta_hours=24,
            stage=Match.STAGE_ROUND_OF_16,
        )

        self.login_as_aryan()

        response = self.client.post(
            reverse("submit_prediction", args=[match.id]),
            {
                "prediction": Prediction.PREDICTION_DRAW,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Draw is not available for knockout matches. Pick who qualifies.",
        )
        self.assertFalse(
            Prediction.objects.filter(
                user=self.aryan,
                match=match,
            ).exists()
        )

    def test_knockout_match_saves_home_or_away_qualifier_prediction(self):
        match = self.create_match(
            home_team="France",
            away_team="Germany",
            kickoff_delta_hours=24,
            stage=Match.STAGE_ROUND_OF_16,
        )

        self.login_as_aryan()

        response = self.client.post(
            reverse("submit_prediction", args=[match.id]),
            {
                "prediction": Prediction.PREDICTION_AWAY,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        prediction = Prediction.objects.get(user=self.aryan, match=match)
        self.assertEqual(prediction.prediction, Prediction.PREDICTION_AWAY)

    def test_knockout_prediction_scores_against_qualified_team(self):
        match = self.create_match(
            home_team="France",
            away_team="Germany",
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            home_score=1,
            away_score=1,
            stage=Match.STAGE_ROUND_OF_16,
            qualified_team=Match.RESULT_AWAY,
        )

        correct_prediction = Prediction.objects.create(
            user=self.aryan,
            match=match,
            prediction=Prediction.PREDICTION_AWAY,
        )
        incorrect_prediction = Prediction.objects.create(
            user=self.friend,
            match=match,
            prediction=Prediction.PREDICTION_HOME,
        )

        self.assertEqual(match.result, Match.RESULT_DRAW)
        self.assertEqual(match.get_scoring_result(), Match.RESULT_AWAY)
        self.assertEqual(correct_prediction.points_awarded, 3)
        self.assertEqual(incorrect_prediction.points_awarded, 0)

    def test_knockout_finished_match_without_qualified_team_is_unscored(self):
        match = self.create_match(
            home_team="France",
            away_team="Germany",
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            home_score=1,
            away_score=1,
            stage=Match.STAGE_ROUND_OF_16,
        )

        prediction = Prediction.objects.create(
            user=self.aryan,
            match=match,
            prediction=Prediction.PREDICTION_HOME,
        )

        self.assertEqual(match.result, Match.RESULT_DRAW)
        self.assertIsNone(match.get_scoring_result())
        self.assertEqual(prediction.points_awarded, 0)

    def test_qualified_team_choices_do_not_include_draw(self):
        choice_values = [
            value for value, _label in Match._meta.get_field("qualified_team").choices
        ]

        self.assertEqual(choice_values, [Match.RESULT_HOME, Match.RESULT_AWAY])

    def test_group_stage_scoring_still_awards_three_points(self):
        match = self.create_match(
            home_team="Argentina",
            away_team="Brazil",
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            home_score=2,
            away_score=1,
        )

        prediction = Prediction.objects.create(
            user=self.aryan,
            match=match,
            prediction=Prediction.PREDICTION_HOME,
        )

        self.assertEqual(match.get_scoring_result(), Match.RESULT_HOME)
        self.assertEqual(prediction.points_awarded, 3)

    def test_finished_my_picks_show_result_row_highlighting(self):
        correct_match = self.create_match(
            home_team="Argentina",
            away_team="Brazil",
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            home_score=2,
            away_score=1,
        )
        incorrect_match = self.create_match(
            home_team="France",
            away_team="Germany",
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            home_score=0,
            away_score=1,
        )

        Prediction.objects.create(
            user=self.aryan,
            match=correct_match,
            prediction=Prediction.PREDICTION_HOME,
        )
        Prediction.objects.create(
            user=self.aryan,
            match=incorrect_match,
            prediction=Prediction.PREDICTION_HOME,
        )

        self.login_as_aryan()

        response = self.client.get(f"{reverse('my_picks')}?tab=picks")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Home win")
        self.assertContains(response, "Away win")
        self.assertContains(response, "is-result-match")
        self.assertContains(response, "is-result-different")

    def test_compare_picks_tab_is_accessible_to_logged_in_users(self):
        self.login_as_aryan()

        response = self.client.get(f"{reverse('my_picks')}?tab=compare")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Compare Picks")
        self.assertContains(response, "Compare Picks only uses matches where voting is locked or finished.")

    def test_my_picks_shows_player_stats_summary_for_self(self):
        picked_open_match = self.create_match(
            home_team="Canada",
            away_team="Mexico",
            kickoff_delta_hours=24,
        )
        self.create_match(
            home_team="Spain",
            away_team="Portugal",
            kickoff_delta_hours=24,
        )
        correct_match = self.create_match(
            home_team="Argentina",
            away_team="Brazil",
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            home_score=2,
            away_score=1,
        )

        Prediction.objects.create(
            user=self.aryan,
            match=picked_open_match,
            prediction=Prediction.PREDICTION_HOME,
        )
        Prediction.objects.create(
            user=self.aryan,
            match=correct_match,
            prediction=Prediction.PREDICTION_HOME,
        )

        self.login_as_aryan()

        response = self.client.get(reverse("my_picks"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Stats")
        self.assertContains(response, "Personal analytics")
        self.assertContains(response, "Action needed: 1 open pick remaining")
        self.assertContains(response, "Total points")
        self.assertContains(response, "Draw pick rate")
        self.assertContains(response, "3")
        self.assertContains(response, "100%")
        self.assertContains(response, "my-picks-form-dot is-win")
        self.assertNotContains(response, "<span>Open picks</span>", html=False)

    def test_dashboard_renders_personal_stage_accuracy(self):
        group_match = self.create_match(
            home_team="Argentina",
            away_team="Brazil",
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            home_score=2,
            away_score=1,
        )
        knockout_match = self.create_match(
            home_team="France",
            away_team="Germany",
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            home_score=1,
            away_score=1,
            stage=Match.STAGE_ROUND_OF_16,
            qualified_team=Match.RESULT_AWAY,
        )

        Prediction.objects.create(
            user=self.aryan,
            match=group_match,
            prediction=Prediction.PREDICTION_HOME,
        )
        Prediction.objects.create(
            user=self.aryan,
            match=knockout_match,
            prediction=Prediction.PREDICTION_AWAY,
        )

        self.login_as_aryan()

        response = self.client.get(reverse("my_picks"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Personal Stage Accuracy")
        self.assertContains(response, "Group Stage")
        self.assertContains(response, "Round of 16")
        self.assertContains(response, "1/1 correct - 100%")

    def test_dashboard_renders_user_vs_crowd_and_excludes_open_matches(self):
        third_user = User.objects.create_user(
            username="third",
            password="Testpass123!",
        )
        finished_match = self.create_match(
            home_team="Argentina",
            away_team="Brazil",
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            home_score=2,
            away_score=1,
        )
        open_match = self.create_match(
            home_team="Canada",
            away_team="Mexico",
            kickoff_delta_hours=24,
        )

        Prediction.objects.create(
            user=self.aryan,
            match=finished_match,
            prediction=Prediction.PREDICTION_HOME,
        )
        Prediction.objects.create(
            user=self.friend,
            match=finished_match,
            prediction=Prediction.PREDICTION_HOME,
        )
        Prediction.objects.create(
            user=third_user,
            match=finished_match,
            prediction=Prediction.PREDICTION_AWAY,
        )
        Prediction.objects.create(
            user=self.aryan,
            match=open_match,
            prediction=Prediction.PREDICTION_AWAY,
        )
        Prediction.objects.create(
            user=self.friend,
            match=open_match,
            prediction=Prediction.PREDICTION_AWAY,
        )

        predictions = list(
            Prediction.objects.filter(user=self.aryan).select_related("match")
        )
        crowd_stats = build_user_vs_crowd(predictions)

        self.assertEqual(crowd_stats["compared_matches"], 1)
        self.assertEqual(crowd_stats["followed_crowd"], 1)

        self.login_as_aryan()

        response = self.client.get(reverse("my_picks"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User vs Crowd")
        self.assertContains(response, "Followed the crowd")
        self.assertContains(response, "Went against the crowd")
        self.assertContains(response, "Contrarian success rate")

    def test_dashboard_pick_style_renders_ranking_snapshot(self):
        match = self.create_match(
            home_team="Argentina",
            away_team="Brazil",
            kickoff_delta_hours=24,
        )

        Prediction.objects.create(
            user=self.aryan,
            match=match,
            prediction=Prediction.PREDICTION_HOME,
        )

        self.login_as_aryan()

        response = self.client.get(reverse("my_picks"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pick Style")
        self.assertContains(
            response,
            "FIFA/Coca-Cola Men&#x27;s World Ranking",
        )
        self.assertContains(response, "Higher-ranked picks")
        self.assertContains(response, "1 pick - 100%")

    def test_fifa_ranking_snapshot_handles_aliases_and_placeholders(self):
        self.assertEqual(get_team_ranking("Brazil"), 5)
        self.assertEqual(get_team_ranking("United States"), 15)
        self.assertEqual(get_team_ranking("Korea Republic"), 32)
        self.assertTrue(is_placeholder_team_name("1A"))
        self.assertTrue(is_placeholder_team_name("3A/B/C/D/F"))
        self.assertTrue(is_placeholder_team_name("W100"))
        self.assertTrue(is_placeholder_team_name("L101"))
        self.assertIsNone(get_team_ranking("1A"))

    def test_pick_style_skips_placeholder_teams(self):
        placeholder_match = self.create_match(
            home_team="1A",
            away_team="Brazil",
            kickoff_delta_hours=24,
        )
        ranked_match = self.create_match(
            home_team="Argentina",
            away_team="Brazil",
            kickoff_delta_hours=24,
        )

        Prediction.objects.create(
            user=self.aryan,
            match=placeholder_match,
            prediction=Prediction.PREDICTION_AWAY,
        )
        Prediction.objects.create(
            user=self.aryan,
            match=ranked_match,
            prediction=Prediction.PREDICTION_HOME,
        )

        predictions = list(
            Prediction.objects.filter(user=self.aryan).select_related("match")
        )
        pick_style = build_pick_style(predictions)

        self.assertEqual(pick_style["total_picks"], 1)
        self.assertEqual(pick_style["unknown_ranking"], 0)

    def test_public_user_stats_do_not_include_open_picks(self):
        open_match = self.create_match(
            home_team="Canada",
            away_team="Mexico",
            kickoff_delta_hours=24,
        )
        finished_match = self.create_match(
            home_team="France",
            away_team="Germany",
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            home_score=1,
            away_score=0,
        )

        Prediction.objects.create(
            user=self.friend,
            match=open_match,
            prediction=Prediction.PREDICTION_HOME,
        )
        Prediction.objects.create(
            user=self.friend,
            match=finished_match,
            prediction=Prediction.PREDICTION_HOME,
        )

        self.login_as_aryan()

        response = self.client.get(reverse("user_picks", args=[self.friend.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Player profile")
        self.assertContains(response, "Public picks only")
        self.assertContains(response, "France")
        self.assertNotContains(response, "Canada")
        self.assertNotContains(response, "<span>Open picks</span>", html=False)

    def test_compare_picks_does_not_expose_active_open_picks(self):
        open_match = self.create_match(
            home_team="Canada",
            away_team="Mexico",
            kickoff_delta_hours=24,
        )

        Prediction.objects.create(
            user=self.aryan,
            match=open_match,
            prediction=Prediction.PREDICTION_HOME,
        )
        Prediction.objects.create(
            user=self.friend,
            match=open_match,
            prediction=Prediction.PREDICTION_AWAY,
        )

        self.login_as_aryan()

        response = self.client.get(
            f"{reverse('my_picks')}?tab=compare&compare_user_id={self.friend.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Canada")
        self.assertNotContains(response, "Mexico")

    def test_compare_picks_shows_locked_and_finished_shared_predictions(self):
        locked_match = self.create_match(
            home_team="France",
            away_team="Germany",
            kickoff_delta_hours=-1,
        )
        finished_match = self.create_match(
            home_team="Argentina",
            away_team="Brazil",
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            home_score=2,
            away_score=1,
        )

        Prediction.objects.create(
            user=self.aryan,
            match=locked_match,
            prediction=Prediction.PREDICTION_HOME,
        )
        Prediction.objects.create(
            user=self.friend,
            match=locked_match,
            prediction=Prediction.PREDICTION_AWAY,
        )
        Prediction.objects.create(
            user=self.aryan,
            match=finished_match,
            prediction=Prediction.PREDICTION_HOME,
        )
        Prediction.objects.create(
            user=self.friend,
            match=finished_match,
            prediction=Prediction.PREDICTION_AWAY,
        )

        self.login_as_aryan()

        response = self.client.get(
            f"{reverse('my_picks')}?tab=compare&compare_user_id={self.friend.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "France")
        self.assertContains(response, "Argentina")
        self.assertContains(response, "Awaiting result")

    def test_compare_picks_cells_include_correctness_class_hooks(self):
        finished_match = self.create_match(
            home_team="Argentina",
            away_team="Brazil",
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            home_score=2,
            away_score=1,
        )

        Prediction.objects.create(
            user=self.aryan,
            match=finished_match,
            prediction=Prediction.PREDICTION_HOME,
        )
        Prediction.objects.create(
            user=self.friend,
            match=finished_match,
            prediction=Prediction.PREDICTION_AWAY,
        )

        self.login_as_aryan()

        response = self.client.get(
            f"{reverse('my_picks')}?tab=compare&compare_user_id={self.friend.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "compare-pick-cell is-result-match")
        self.assertContains(response, "compare-pick-cell is-result-different")

    def test_compare_picks_summary_counts_locked_and_finished_matches(self):
        shared_correct_match = self.create_match(
            home_team="Argentina",
            away_team="Brazil",
            kickoff_delta_hours=-4,
            status=Match.STATUS_FINISHED,
            home_score=2,
            away_score=1,
        )
        split_result_match = self.create_match(
            home_team="France",
            away_team="Germany",
            kickoff_delta_hours=-3,
            status=Match.STATUS_FINISHED,
            home_score=0,
            away_score=1,
        )
        locked_match = self.create_match(
            home_team="Spain",
            away_team="Portugal",
            kickoff_delta_hours=-1,
        )
        open_match = self.create_match(
            home_team="Canada",
            away_team="Mexico",
            kickoff_delta_hours=24,
        )

        Prediction.objects.create(
            user=self.aryan,
            match=shared_correct_match,
            prediction=Prediction.PREDICTION_HOME,
        )
        Prediction.objects.create(
            user=self.friend,
            match=shared_correct_match,
            prediction=Prediction.PREDICTION_HOME,
        )
        Prediction.objects.create(
            user=self.aryan,
            match=split_result_match,
            prediction=Prediction.PREDICTION_HOME,
        )
        Prediction.objects.create(
            user=self.friend,
            match=split_result_match,
            prediction=Prediction.PREDICTION_AWAY,
        )
        Prediction.objects.create(
            user=self.aryan,
            match=locked_match,
            prediction=Prediction.PREDICTION_DRAW,
        )
        Prediction.objects.create(
            user=self.friend,
            match=locked_match,
            prediction=Prediction.PREDICTION_AWAY,
        )
        Prediction.objects.create(
            user=self.aryan,
            match=open_match,
            prediction=Prediction.PREDICTION_HOME,
        )
        Prediction.objects.create(
            user=self.friend,
            match=open_match,
            prediction=Prediction.PREDICTION_AWAY,
        )

        self.login_as_aryan()

        response = self.client.get(
            f"{reverse('my_picks')}?tab=compare&compare_user_id={self.friend.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Matches compared")
        self.assertContains(response, "Same picks")
        self.assertContains(response, "Different picks")
        self.assertContains(response, "Head-to-head winner")
        self.assertContains(response, "friend")
        self.assertContains(response, "Spain")
        self.assertNotContains(response, "Canada")

    def test_leaderboard_calculates_correct_and_incorrect_predictions(self):
        finished_match = self.create_match(
            home_team="Argentina",
            away_team="Brazil",
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            result=Match.RESULT_HOME,
            home_score=2,
            away_score=1,
        )

        Prediction.objects.create(
            user=self.aryan,
            match=finished_match,
            prediction=Prediction.PREDICTION_AWAY,
        )

        self.login_as_aryan()

        response = self.client.get(reverse("leaderboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Incorrect Picks")
        self.assertContains(response, "0%")

    def test_global_leaderboard_shows_rank_movement_inside_rank_cell(self):
        third_user = User.objects.create_user(
            username="third",
            password="Testpass123!",
        )
        GroupMember.objects.create(
            user=third_user,
            group=self.family,
            role=GroupMember.ROLE_MEMBER,
        )
        base_time = timezone.now().replace(hour=12, minute=0, second=0, microsecond=0)
        previous_match = self.create_match(
            home_team="Argentina",
            away_team="Brazil",
            status=Match.STATUS_FINISHED,
            home_score=2,
            away_score=1,
            kickoff_time=base_time - timedelta(days=2),
        )
        latest_match_one = self.create_match(
            home_team="France",
            away_team="Germany",
            status=Match.STATUS_FINISHED,
            home_score=0,
            away_score=1,
            kickoff_time=base_time - timedelta(days=1),
        )
        latest_match_two = self.create_match(
            home_team="Spain",
            away_team="Portugal",
            status=Match.STATUS_FINISHED,
            home_score=0,
            away_score=1,
            kickoff_time=base_time - timedelta(days=1) + timedelta(hours=1),
        )

        Prediction.objects.create(
            user=self.aryan,
            match=previous_match,
            prediction=Prediction.PREDICTION_HOME,
        )
        Prediction.objects.create(
            user=self.friend,
            match=previous_match,
            prediction=Prediction.PREDICTION_AWAY,
        )
        Prediction.objects.create(
            user=self.aryan,
            match=latest_match_one,
            prediction=Prediction.PREDICTION_HOME,
        )
        Prediction.objects.create(
            user=self.friend,
            match=latest_match_one,
            prediction=Prediction.PREDICTION_AWAY,
        )
        Prediction.objects.create(
            user=self.aryan,
            match=latest_match_two,
            prediction=Prediction.PREDICTION_HOME,
        )
        Prediction.objects.create(
            user=self.friend,
            match=latest_match_two,
            prediction=Prediction.PREDICTION_AWAY,
        )

        self.login_as_aryan()

        response = self.client.get(reverse("leaderboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "rank-movement movement-up")
        self.assertContains(response, "&uarr; 1", html=False)
        self.assertContains(response, "rank-movement movement-down")
        self.assertContains(response, "&darr; 1", html=False)
        self.assertContains(response, "rank-movement movement-neutral")
        self.assertNotContains(response, "<th>Movement</th>", html=False)

    def test_league_leaderboard_shows_rank_movement(self):
        GroupMember.objects.create(
            user=self.friend,
            group=self.family,
            role=GroupMember.ROLE_MEMBER,
        )
        base_time = timezone.now().replace(hour=12, minute=0, second=0, microsecond=0)
        previous_match = self.create_match(
            home_team="Argentina",
            away_team="Brazil",
            status=Match.STATUS_FINISHED,
            home_score=2,
            away_score=1,
            kickoff_time=base_time - timedelta(days=2),
        )
        latest_match_one = self.create_match(
            home_team="France",
            away_team="Germany",
            status=Match.STATUS_FINISHED,
            home_score=0,
            away_score=1,
            kickoff_time=base_time - timedelta(days=1),
        )
        latest_match_two = self.create_match(
            home_team="Spain",
            away_team="Portugal",
            status=Match.STATUS_FINISHED,
            home_score=0,
            away_score=1,
            kickoff_time=base_time - timedelta(days=1) + timedelta(hours=1),
        )

        for match, aryan_pick, friend_pick in [
            (previous_match, Prediction.PREDICTION_HOME, Prediction.PREDICTION_AWAY),
            (latest_match_one, Prediction.PREDICTION_HOME, Prediction.PREDICTION_AWAY),
            (latest_match_two, Prediction.PREDICTION_HOME, Prediction.PREDICTION_AWAY),
        ]:
            Prediction.objects.create(
                user=self.aryan,
                match=match,
                prediction=aryan_pick,
            )
            Prediction.objects.create(
                user=self.friend,
                match=match,
                prediction=friend_pick,
            )

        self.login_as_aryan()

        response = self.client.get(reverse("league_detail", args=[self.family.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "rank-movement movement-up")
        self.assertContains(response, "rank-movement movement-down")

    def test_staff_user_can_see_sync_results_button_on_matches_page(self):
        self.login_as_staff()

        response = self.client.get(reverse("matches"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sync Results")
        self.assertContains(response, "Sync latest fixtures and results")

    def test_non_staff_user_cannot_see_sync_results_button_on_matches_page(self):
        self.login_as_aryan()

        response = self.client.get(reverse("matches"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Sync Results")
        self.assertNotContains(response, "Sync latest fixtures and results")

    @patch("predictions.views.call_command")
    def test_staff_user_can_trigger_sync_results_command(self, mocked_call_command):
        self.login_as_staff()

        def write_import_output(*args, **kwargs):
            stdout = kwargs["stdout"]
            stdout.write("Starting OpenFootball World Cup import...\n")
            stdout.write("Source URL: https://example.com/worldcup.json\n")
            stdout.write("OpenFootball import completed.\n")
            stdout.write("Created: 1\n")
            stdout.write("Updated: 2\n")
            stdout.write("Skipped: 3\n")

        mocked_call_command.side_effect = write_import_output

        response = self.client.post(
            reverse("sync_latest_results"),
            {
                "next": reverse("matches"),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        mocked_call_command.assert_called_once()
        self.assertEqual(
            mocked_call_command.call_args.args[0],
            "import_openfootball_worldcup",
        )
        self.assertContains(
            response,
            "Sync complete. Fixtures and results are up to date.",
        )
        self.assertNotContains(response, "Starting OpenFootball World Cup import")
        self.assertNotContains(response, "Source URL")
        self.assertNotContains(response, "Created:")
        self.assertNotContains(response, "Updated:")
        self.assertNotContains(response, "Skipped:")

    @patch("predictions.views.call_command")
    def test_non_staff_user_cannot_trigger_sync_results_command(
        self,
        mocked_call_command,
    ):
        self.login_as_aryan()

        response = self.client.post(
            reverse("sync_latest_results"),
            {
                "next": reverse("matches"),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        mocked_call_command.assert_not_called()
        self.assertContains(response, "Only staff users can sync fixtures and results.")

    def test_homepage_uses_restored_matchpick_branding(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "MatchPick")
        self.assertContains(response, "Predict once. Compete everywhere.")
        self.assertContains(response, "MP")
        self.assertContains(response, "New in MatchPick")
        self.assertContains(response, "View My Picks")
        self.assertContains(response, reverse("my_picks"))
        self.assertContains(response, "View Matches")
        self.assertContains(response, reverse("matches"))

    def test_insights_page_requires_login(self):
        response = self.client.get(reverse("insights"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_insights_page_loads_for_logged_in_user(self):
        self.login_as_aryan()

        response = self.client.get(reverse("insights"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Insights")
        self.assertContains(response, "Trends unlock after kickoff")
        self.assertContains(response, "Points Progression")
        self.assertContains(response, "Rank Race")
        self.assertContains(response, "Crowd Accuracy by Stage")
        self.assertContains(response, "Recent Form Board")

    def test_insights_progression_uses_daily_snapshots(self):
        base_time = timezone.now() - timedelta(days=3)
        day_one_first = self.create_match(
            kickoff_time=base_time,
            status=Match.STATUS_FINISHED,
            home_score=2,
            away_score=1,
        )
        day_one_second = self.create_match(
            home_team="France",
            away_team="Germany",
            kickoff_time=base_time + timedelta(hours=3),
            status=Match.STATUS_FINISHED,
            home_score=1,
            away_score=0,
        )
        day_two = self.create_match(
            home_team="Canada",
            away_team="Mexico",
            kickoff_time=base_time + timedelta(days=1),
            status=Match.STATUS_FINISHED,
            home_score=0,
            away_score=1,
        )

        for match in [day_one_first, day_one_second, day_two]:
            Prediction.objects.create(
                user=self.aryan,
                match=match,
                prediction=Prediction.PREDICTION_HOME,
            )

        self.login_as_aryan()

        response = self.client.get(reverse("insights"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["insights_timeline_snapshot_count"], 2)
        self.assertContains(response, 'data-point-count="2"')

    def test_insights_x_axis_labels_use_clean_calendar_intervals(self):
        base_time = timezone.now() - timedelta(days=20)

        for index in range(18):
            match = self.create_match(
                kickoff_time=base_time + timedelta(days=index),
                status=Match.STATUS_FINISHED,
                home_score=2,
                away_score=1,
            )
            Prediction.objects.create(
                user=self.aryan,
                match=match,
                prediction=Prediction.PREDICTION_HOME,
            )

        self.login_as_aryan()

        response = self.client.get(reverse("insights"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["insights_points_chart"]["point_count"], 18)
        point_x_labels = response.context["insights_points_chart"]["x_labels"]
        rank_x_labels = response.context["insights_rank_chart"]["x_labels"]
        expected_offsets = [0, 3, 6, 9, 12, 15, 17]

        self.assertEqual(len(point_x_labels), 7)
        self.assertEqual(len(rank_x_labels), 7)
        self.assertEqual(
            [label["day_offset"] for label in point_x_labels],
            expected_offsets,
        )
        self.assertEqual(
            [label["day_offset"] for label in rank_x_labels],
            expected_offsets,
        )
        self.assertTrue(
            point_x_labels[1]["x"] - point_x_labels[0]["x"]
            > point_x_labels[-1]["x"] - point_x_labels[-2]["x"]
        )

    def test_insights_points_y_axis_labels_show_clean_scale(self):
        for index in range(4):
            match = self.create_match(
                home_team=f"Home {index}",
                away_team=f"Away {index}",
                kickoff_delta_hours=-2,
                status=Match.STATUS_FINISHED,
                home_score=2,
                away_score=1,
            )
            Prediction.objects.create(
                user=self.aryan,
                match=match,
                prediction=Prediction.PREDICTION_HOME,
            )

        self.login_as_aryan()

        response = self.client.get(reverse("insights"))

        point_y_labels = [
            label["label"]
            for label in response.context["insights_points_chart"]["y_labels"]
        ]
        self.assertEqual(point_y_labels, ["12", "6", "0"])
        self.assertContains(response, "12")
        self.assertContains(response, "6")

    def test_insights_rank_y_axis_labels_show_two_user_ranks(self):
        match = self.create_match(
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            home_score=2,
            away_score=1,
        )
        Prediction.objects.create(
            user=self.aryan,
            match=match,
            prediction=Prediction.PREDICTION_HOME,
        )
        Prediction.objects.create(
            user=self.friend,
            match=match,
            prediction=Prediction.PREDICTION_AWAY,
        )

        self.login_as_aryan()

        response = self.client.get(reverse("insights"))

        rank_y_labels = [
            label["label"]
            for label in response.context["insights_rank_chart"]["y_labels"]
        ]
        self.assertEqual(rank_y_labels, ["#1", "#2"])
        self.assertContains(response, "#1")
        self.assertContains(response, "#2")

    def test_insights_progression_uses_group_and_knockout_scoring(self):
        group_match = self.create_match(
            home_team="Argentina",
            away_team="Brazil",
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            home_score=2,
            away_score=1,
        )
        knockout_match = self.create_match(
            home_team="France",
            away_team="Germany",
            kickoff_delta_hours=-1,
            status=Match.STATUS_FINISHED,
            home_score=1,
            away_score=1,
            stage=Match.STAGE_ROUND_OF_16,
            qualified_team=Match.RESULT_AWAY,
        )

        Prediction.objects.create(
            user=self.aryan,
            match=group_match,
            prediction=Prediction.PREDICTION_HOME,
        )
        Prediction.objects.create(
            user=self.aryan,
            match=knockout_match,
            prediction=Prediction.PREDICTION_AWAY,
        )

        self.login_as_aryan()

        response = self.client.get(reverse("insights"))

        self.assertEqual(response.status_code, 200)
        aryan_series = next(
            series
            for series in response.context["insights_points_chart"]["series"]
            if series["username"] == "aryan"
        )
        self.assertEqual(aryan_series["latest_value"], 6)
        self.assertContains(response, "Round of 16")
        self.assertContains(response, "100%")

    def test_insights_excludes_active_open_picks(self):
        finished_match = self.create_match(
            home_team="Argentina",
            away_team="Brazil",
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            home_score=2,
            away_score=1,
        )
        open_match = self.create_match(
            home_team="Canada",
            away_team="Mexico",
            kickoff_delta_hours=24,
        )

        Prediction.objects.create(
            user=self.aryan,
            match=finished_match,
            prediction=Prediction.PREDICTION_HOME,
        )
        Prediction.objects.create(
            user=self.aryan,
            match=open_match,
            prediction=Prediction.PREDICTION_AWAY,
        )

        self.login_as_aryan()

        response = self.client.get(reverse("insights"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Argentina")
        self.assertNotContains(response, "Canada")
        self.assertNotContains(response, "Mexico")

    def test_insights_display_rule_includes_all_users_when_competition_is_small(self):
        finished_match = self.create_match(
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            home_score=2,
            away_score=1,
        )

        Prediction.objects.create(
            user=self.aryan,
            match=finished_match,
            prediction=Prediction.PREDICTION_HOME,
        )
        Prediction.objects.create(
            user=self.friend,
            match=finished_match,
            prediction=Prediction.PREDICTION_AWAY,
        )

        self.login_as_aryan()

        response = self.client.get(reverse("insights"))

        usernames = [
            series["username"]
            for series in response.context["insights_points_chart"]["series"]
        ]
        self.assertEqual(usernames, ["aryan", "friend"])

    def test_insights_display_rule_limits_large_competitions_but_keeps_current_user(self):
        finished_match = self.create_match(
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            home_score=2,
            away_score=1,
        )
        top_users = []

        for index in range(1, 16):
            user = User.objects.create_user(
                username=f"player{index:02d}",
                password="Testpass123!",
            )
            GroupMember.objects.create(
                user=user,
                group=self.family,
                role=GroupMember.ROLE_MEMBER,
            )

            if index <= 5:
                top_users.append(user)
                Prediction.objects.create(
                    user=user,
                    match=finished_match,
                    prediction=Prediction.PREDICTION_HOME,
                )

        Prediction.objects.create(
            user=self.aryan,
            match=finished_match,
            prediction=Prediction.PREDICTION_AWAY,
        )

        self.login_as_aryan()

        response = self.client.get(reverse("insights"))

        usernames = [
            series["username"]
            for series in response.context["insights_points_chart"]["series"]
        ]
        self.assertEqual(len(usernames), 6)
        self.assertIn("aryan", usernames)
        self.assertIn("player01", usernames)
        self.assertNotIn("player15", usernames)

    def test_insights_crowd_accuracy_handles_tied_crowd_picks(self):
        match = self.create_match(
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            home_score=2,
            away_score=1,
        )

        Prediction.objects.create(
            user=self.aryan,
            match=match,
            prediction=Prediction.PREDICTION_HOME,
        )
        Prediction.objects.create(
            user=self.friend,
            match=match,
            prediction=Prediction.PREDICTION_AWAY,
        )

        self.login_as_aryan()

        response = self.client.get(reverse("insights"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["crowd_accuracy_by_stage"]["rows"], [])
        self.assertEqual(
            response.context["crowd_accuracy_by_stage"]["split_crowd_matches"],
            1,
        )
        self.assertContains(response, "1 split-crowd match skipped")

    def test_match_card_hides_prediction_trends_before_kickoff(self):
        match = self.create_match(kickoff_delta_hours=24)

        Prediction.objects.create(
            user=self.aryan,
            match=match,
            prediction=Prediction.PREDICTION_HOME,
        )

        self.login_as_aryan()

        response = self.client.get(reverse("matches"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Argentina win")
        self.assertContains(response, "Draw")
        self.assertContains(response, "Brazil win")
        self.assertNotContains(
            response,
            "Prediction trends will appear after voting closes for this match.",
        )
        self.assertNotContains(
            response,
            "Your choice is saved once and used across all of your leagues.",
        )
        self.assertNotContains(response, "Voting split after lock")

    def test_match_card_shows_prediction_trends_after_kickoff(self):
        match = self.create_match(kickoff_delta_hours=-1)

        Prediction.objects.create(
            user=self.aryan,
            match=match,
            prediction=Prediction.PREDICTION_HOME,
        )

        Prediction.objects.create(
            user=self.friend,
            match=match,
            prediction=Prediction.PREDICTION_AWAY,
        )

        self.login_as_aryan()

        response = self.client.get(reverse("matches"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Voting split after lock")
        self.assertContains(response, "Argentina")
        self.assertContains(response, "Brazil")
        self.assertContains(response, "Argentina flag")
        self.assertContains(response, "Brazil flag")
        self.assertContains(response, "50%")

    def test_insights_page_shows_locked_match_voting_split(self):
        match = self.create_match(
            home_team="Australia",
            away_team="Turkey",
            kickoff_delta_hours=-1,
        )

        Prediction.objects.create(
            user=self.aryan,
            match=match,
            prediction=Prediction.PREDICTION_HOME,
        )

        Prediction.objects.create(
            user=self.friend,
            match=match,
            prediction=Prediction.PREDICTION_HOME,
        )

        self.login_as_aryan()

        response = self.client.get(reverse("insights"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Australia")
        self.assertContains(response, "Turkey")
        self.assertContains(response, "Australia flag")
        self.assertContains(response, "Turkey flag")
        self.assertContains(response, "Most Backed Team")
        self.assertContains(response, "Australia")
        self.assertContains(response, "100%")
        self.assertContains(response, "2 picks")

    def test_global_leaderboard_card_shows_tied_fewest_missed_players(self):
        third_user = User.objects.create_user(
            username="third",
            password="Testpass123!",
        )

        GroupMember.objects.create(
            user=third_user,
            group=self.family,
            role=GroupMember.ROLE_MEMBER,
        )

        finished_match = self.create_match(
            home_team="Argentina",
            away_team="Brazil",
            kickoff_delta_hours=-2,
            status=Match.STATUS_FINISHED,
            result=Match.RESULT_HOME,
            home_score=2,
            away_score=1,
        )

        Prediction.objects.create(
            user=self.aryan,
            match=finished_match,
            prediction=Prediction.PREDICTION_HOME,
        )

        Prediction.objects.create(
            user=self.friend,
            match=finished_match,
            prediction=Prediction.PREDICTION_AWAY,
        )

        Prediction.objects.create(
            user=third_user,
            match=finished_match,
            prediction=Prediction.PREDICTION_AWAY,
        )

        self.login_as_aryan()

        response = self.client.get(reverse("leaderboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fewest Missed Picks")
        self.assertContains(response, "aryan, friend, third")
        self.assertContains(response, "3 players tied")

    def test_match_model_displays_team_flags(self):
        match = self.create_match(
            home_team="Australia",
            away_team="Turkey",
            kickoff_delta_hours=24,
        )

        self.assertEqual(match.home_team_flag, "🇦🇺")
        self.assertEqual(match.away_team_flag, "🇹🇷")
        self.assertEqual(match.home_team_flag_url, "https://flagcdn.com/w40/au.png")
        self.assertEqual(match.away_team_flag_url, "https://flagcdn.com/w40/tr.png")
        self.assertEqual(match.home_team_with_flag, "🇦🇺 Australia")
        self.assertEqual(match.away_team_with_flag, "🇹🇷 Turkey")
