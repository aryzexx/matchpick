# Stage 21 — Update 3: Prediction Refactor and Voting Insights

## Goal

The goal of this update was to improve the prediction system so the database better matched the app’s rule of one prediction per user and match. I also added voting trend insights that become visible only after voting has locked.

This update was needed because the previous database design still stored predictions against a specific group, even though the app had already been changed so that one prediction should count across all leagues.

## Issue Found

During admin testing, I noticed that if a user belonged to two leagues, the same prediction was stored twice in the database.

For example, if one user predicted Saudi Arabia vs Uruguay while belonging to two leagues, Django admin showed two prediction rows:

* User + Family League + Match
* User + Second League + Match

This was not ideal because the product rule is:

**One user + one match = one prediction.**

The league should decide which leaderboard the user appears in, but it should not decide how many times the prediction is stored.

## Database Design Decision

I refactored the `Prediction` model so that predictions are no longer tied to a group.

The old design was:

```text
Prediction = user + group + match + prediction
```

The new design is:

```text
Prediction = user + match + prediction
```

This is cleaner because one prediction now automatically counts in every league the user belongs to.

## Migration and Data Cleanup

Because existing data already contained duplicate predictions, I created a migration that cleaned the data before removing the group field.

The migration:

* Found predictions with the same user and match.
* Kept the most recently updated prediction.
* Deleted older duplicate rows.
* Removed the group field from `Prediction`.
* Changed the unique rule to `user + match`.

This prevented duplicate prediction rows from remaining after the model refactor.

## Admin Improvement

The Prediction admin page was updated so it no longer asks for a group.

The admin now focuses on:

* User
* Match
* Prediction
* Points awarded
* Submitted time

This makes manual admin review much easier and avoids confusion when adding or checking predictions.

## Voting Trend Design Decision

I added voting trend percentages, but only after voting has locked.

This decision was made for fairness. If percentages were shown before kickoff, users could copy the majority choice instead of making their own prediction.

The final rule is:

* Before kickoff, voting trends are hidden.
* After kickoff, voting is locked and trends become visible.
* After full-time, trends remain visible alongside the result.

This means users can see how people voted without that information influencing active predictions.

## Insights Page

I added a new Insights page.

The page shows prediction analytics after matches are locked, including:

* Locked matches with picks.
* Total locked picks.
* Most backed team.
* Biggest favourite.
* Most predicted draw.
* Recently locked voting splits.

This makes the app more engaging because users can see voting behaviour across the competition, not just the leaderboard.

## Match Card Improvements

Match cards now show voting trend percentages after voting has locked.

For example, after kickoff a match can show:

* Team A win percentage
* Draw percentage
* Team B win percentage
* Total number of picks

Before kickoff, the match card explains that trends are hidden until voting closes.

## Files Updated

* `predictions/models.py`
* `predictions/admin.py`
* `predictions/views.py`
* `predictions/urls.py`
* `predictions/tests.py`
* `predictions/templates/predictions/base.html`
* `predictions/templates/predictions/matches.html`
* `predictions/templates/predictions/insights.html`
* `predictions/static/predictions/styles.css`
* `predictions/migrations/0004_refactor_prediction_one_per_user_match.py`

## Testing Completed

I ran the Django system check:

```text
python manage.py check
```

The system check passed.

I ran the prediction app tests:

```text
python manage.py test predictions
```

The tests passed.

The tests covered:

* One prediction being stored once even if the user belongs to multiple leagues.
* Updating an existing prediction instead of creating a duplicate row.
* Blocking predictions outside the allowed window.
* Blocking placeholder fixtures.
* Global leaderboard login protection.
* League access control.
* Leaderboard clarity columns.
* Admin result sync access control.
* Insights page login protection.
* Insights page loading for logged-in users.
* Hiding prediction trends before kickoff.
* Showing prediction trends after kickoff.
* Showing locked match voting splits on the Insights page.

## Manual Testing Completed

I manually checked that:

* The migration ran successfully.
* The `group` field was removed from the Prediction model.
* The unique rule is now `user + match`.
* Duplicate predictions were cleaned.
* The Prediction admin page no longer requires a group.
* The Insights page loads.
* The Insights link appears in the navbar.
* Voting percentages appear only after voting has locked.
* Matches, leagues, leaderboards, and prediction submission still work.

## Reflection

This update improved the internal quality of MatchPick as well as the user-facing experience.

The database now matches the actual product rule, which makes the app cleaner and easier to maintain. Removing the group field from predictions also prevents unnecessary duplicate rows and simplifies Django admin.

The new Insights page adds a more engaging analytics layer while still protecting prediction fairness. Users can now see how others voted after voting has locked, without influencing live predictions.
