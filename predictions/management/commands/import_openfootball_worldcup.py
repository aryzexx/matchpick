import json
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone as django_timezone

from predictions.models import Match


OPENFOOTBALL_WORLD_CUP_2026_URL = (
    "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"
)


class Command(BaseCommand):
    help = "Import World Cup 2026 fixtures/results from OpenFootball worldcup.json."

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            default=OPENFOOTBALL_WORLD_CUP_2026_URL,
            help="URL for the OpenFootball World Cup JSON file.",
        )

        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Optional number of matches to import. Useful for testing.",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview what would be imported without saving changes.",
        )

    def handle(self, *args, **options):
        url = options["url"]
        limit = options["limit"]
        dry_run = options["dry_run"]

        self.stdout.write(self.style.NOTICE("Starting OpenFootball World Cup import..."))
        self.stdout.write(f"Source URL: {url}")

        data = self.fetch_json(url)
        matches = data.get("matches", [])

        if not matches:
            raise CommandError("No matches were found in the source JSON.")

        if limit is not None:
            matches = matches[:limit]

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for index, source_match in enumerate(matches, start=1):
            parsed_match = self.parse_source_match(source_match, index)

            if parsed_match is None:
                skipped_count += 1
                continue

            if dry_run:
                self.stdout.write(
                    "[DRY RUN] "
                    f"{parsed_match['home_team']} vs {parsed_match['away_team']} "
                    f"at {parsed_match['kickoff_time']} "
                    f"status={parsed_match['status']}"
                )
                continue

            existing_match = Match.objects.filter(
                external_source=parsed_match["external_source"],
                external_match_id=parsed_match["external_match_id"],
            ).first()

            if existing_match:
                for field_name, field_value in parsed_match.items():
                    if (
                        field_name == "qualified_team"
                        and field_value is None
                        and existing_match.qualified_team
                    ):
                        continue

                    setattr(existing_match, field_name, field_value)

                existing_match.save()
                self.recalculate_predictions(existing_match)
                updated_count += 1
            else:
                new_match = Match.objects.create(**parsed_match)
                self.recalculate_predictions(new_match)
                created_count += 1

        self.stdout.write(self.style.SUCCESS("OpenFootball import completed."))

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run only. No database changes were made."))

        self.stdout.write(f"Created: {created_count}")
        self.stdout.write(f"Updated: {updated_count}")
        self.stdout.write(f"Skipped: {skipped_count}")

    def fetch_json(self, url):
        """
        Downloads and parses JSON from the provided URL.
        """

        try:
            with urlopen(url, timeout=20) as response:
                raw_data = response.read().decode("utf-8")
        except HTTPError as error:
            raise CommandError(f"HTTP error while downloading source data: {error}") from error
        except URLError as error:
            raise CommandError(f"Network error while downloading source data: {error}") from error
        except TimeoutError as error:
            raise CommandError("The request timed out while downloading source data.") from error

        try:
            return json.loads(raw_data)
        except json.JSONDecodeError as error:
            raise CommandError(f"Could not parse JSON source data: {error}") from error

    def parse_source_match(self, source_match, index):
        """
        Converts one OpenFootball match object into fields for the Match model.
        """

        home_team = source_match.get("team1")
        away_team = source_match.get("team2")
        match_date = source_match.get("date")
        match_time = source_match.get("time", "")

        if not home_team or not away_team or not match_date:
            self.stdout.write(
                self.style.WARNING(
                    f"Skipping match {index}: missing team or date data."
                )
            )
            return None

        kickoff_time = self.parse_kickoff_time(match_date, match_time)
        stage = self.map_stage(source_match)

        score_data = source_match.get("score", {})
        full_time_score = score_data.get("ft")

        home_score = None
        away_score = None
        status = Match.STATUS_SCHEDULED

        if (
            isinstance(full_time_score, list)
            and len(full_time_score) == 2
            and full_time_score[0] is not None
            and full_time_score[1] is not None
        ):
            home_score = int(full_time_score[0])
            away_score = int(full_time_score[1])
            status = Match.STATUS_FINISHED

        external_match_id = self.build_external_match_id(source_match, index)

        parsed_match = {
            "external_source": "openfootball",
            "external_match_id": external_match_id,
            "home_team": home_team,
            "away_team": away_team,
            "kickoff_time": kickoff_time,
            "stage": stage,
            "status": status,
            "home_score": home_score,
            "away_score": away_score,
            "last_synced_at": django_timezone.now(),
        }

        if status == Match.STATUS_FINISHED:
            temporary_match = Match(**parsed_match)
            calculated_result = temporary_match.calculate_result_from_score()
            parsed_match["result"] = calculated_result

            if (
                temporary_match.is_knockout
                and calculated_result in {Match.RESULT_HOME, Match.RESULT_AWAY}
            ):
                parsed_match["qualified_team"] = calculated_result
            else:
                parsed_match["qualified_team"] = None
        else:
            parsed_match["result"] = None
            parsed_match["qualified_team"] = None

        return parsed_match

    def parse_kickoff_time(self, match_date, match_time):
        """
        Parses OpenFootball date/time into a timezone-aware datetime.

        Examples from the source may look like:
        - date: 2026-06-11
        - time: 13:00 UTC-6
        """

        time_parts = match_time.split()

        if time_parts:
            clock_time = time_parts[0]
        else:
            clock_time = "00:00"

        naive_datetime = datetime.strptime(
            f"{match_date} {clock_time}",
            "%Y-%m-%d %H:%M",
        )

        offset = timezone.utc

        for part in time_parts[1:]:
            if part.startswith("UTC"):
                offset = self.parse_utc_offset(part)
                break

        aware_datetime = naive_datetime.replace(tzinfo=offset)

        return aware_datetime

    def parse_utc_offset(self, value):
        """
        Converts strings such as UTC-6, UTC+2, UTC-4 into a timezone object.
        """

        if value == "UTC":
            return timezone.utc

        raw_offset = value.replace("UTC", "")

        if not raw_offset:
            return timezone.utc

        sign = 1

        if raw_offset.startswith("-"):
            sign = -1
            raw_offset = raw_offset[1:]
        elif raw_offset.startswith("+"):
            raw_offset = raw_offset[1:]

        try:
            hours = int(raw_offset)
        except ValueError:
            return timezone.utc

        return timezone(sign * timedelta(hours=hours))

    def map_stage(self, source_match):
        """
        Maps OpenFootball round/group information to the Match model stage choices.
        """

        round_name = source_match.get("round", "").lower()
        group_name = source_match.get("group", "")

        if group_name:
            return Match.STAGE_GROUP

        if "round of 32" in round_name:
            return Match.STAGE_ROUND_OF_32

        if "round of 16" in round_name:
            return Match.STAGE_ROUND_OF_16

        if "quarter" in round_name:
            return Match.STAGE_QUARTER_FINAL

        if "semi" in round_name:
            return Match.STAGE_SEMI_FINAL

        if "third" in round_name:
            return Match.STAGE_THIRD_PLACE

        if "final" in round_name:
            return Match.STAGE_FINAL

        return Match.STAGE_GROUP

    def build_external_match_id(self, source_match, index):
        """
        Builds a stable-enough external ID from the OpenFootball data.

        OpenFootball does not provide a numeric fixture ID in the same way a paid API
        might. This ID prevents duplicates when the command is run more than once.
        """

        date_value = source_match.get("date", "unknown-date")
        team1 = source_match.get("team1", "team1").lower().replace(" ", "-")
        team2 = source_match.get("team2", "team2").lower().replace(" ", "-")

        return f"wc2026-{index:03d}-{date_value}-{team1}-vs-{team2}"

    def recalculate_predictions(self, match):
        """
        Recalculates prediction points for this match after fixture/result updates.
        """

        for prediction in match.predictions.all():
            prediction.points_awarded = prediction.calculate_points()
            prediction.save()
