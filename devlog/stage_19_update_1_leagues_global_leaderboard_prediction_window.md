# Stage 19 — Update 1: Leagues, Global Leaderboard, and Prediction Window

## Goal

The goal of this stage was to improve MatchPick after live testing showed that the original league and leaderboard behaviour was too limited for real use.

The update focused on making the application more realistic for users who want to compete in multiple private leagues while still keeping prediction rules fair and simple.

## Issue Found

During real testing, I found that a user may need to belong to more than one league. For example, I wanted to be part of both a family league and a friends league.

The earlier design showed only one leaderboard for the user’s first league. This meant that users who belonged to multiple leagues could not easily view each league separately.

I also identified a second issue with predictions. The app showed all fixtures, including future knockout-stage fixtures where the teams had not yet been confirmed. This meant users could make predictions too far in advance, including on matches where the final participants were unknown.

## Design Decision: One Prediction Across All Leagues

I decided that users should not be able to make different predictions for the same match in different leagues.

The correct rule is:

**One user + one match = one prediction.**

This means that if a user predicts one result for a match, that same prediction counts in every league they belong to.

Leagues control who appears in each leaderboard, but they do not change the user’s prediction choice.

This keeps the app fair because a user cannot predict one outcome in a family league and a different outcome in a friends league.

## Design Decision: League Page Instead of Separate Join Page

Instead of creating a separate join-league page, I created a main Leagues page.

The Leagues page allows users to:

* See all leagues they currently belong to.
* Join another league using a league code.
* Click into an individual league page.
* View that league’s leaderboard only.

This made more sense than a standalone join page because league joining and league navigation are part of the same user flow.

## Design Decision: Global Leaderboard

I changed the existing leaderboard page into a global leaderboard.

The global leaderboard shows all users on the app who belong to at least one league. This gives the app a wider competition view while still allowing private league leaderboards to exist separately.

For privacy, the global leaderboard is only visible to logged-in users. Logged-out visitors are redirected to the login page.

## Design Decision: Prediction Window

I decided not to allow predictions for all fixtures immediately because many future knockout matches may not have confirmed teams.

I also decided not to restrict predictions to only tomorrow’s matches because that would be too strict and could make the app annoying to use.

The final rule chosen was:

* Predictions open 48 hours before kickoff.
* Predictions lock at kickoff.
* Matches with unconfirmed teams stay locked.
* Matches that are not scheduled stay locked.

This gives users enough time to predict upcoming matches while preventing unrealistic early predictions.

## Actions Completed

* Added a Leagues page.
* Added the ability for logged-in users to join another league using a league code.
* Added individual league pages.
* Changed the existing leaderboard page into a global leaderboard.
* Made the global leaderboard visible only to logged-in users.
* Added league-specific leaderboard views under each league page.
* Preserved the rule that users make one prediction per match.
* Synced each prediction across all leagues the user belongs to.
* Added prediction window logic.
* Locked voting for matches more than 48 hours away.
* Locked voting for matches where teams are not confirmed.
* Kept voting locked after kickoff.
* Added clearer messages explaining why voting is locked.
* Updated the navigation bar to include Matches, Leagues, and Global Leaderboard.
* Updated automated tests for the new behaviour.

## Files Updated

* `predictions/forms.py`
* `predictions/views.py`
* `predictions/urls.py`
* `predictions/tests.py`
* `predictions/templates/predictions/base.html`
* `predictions/templates/predictions/matches.html`
* `predictions/templates/predictions/leaderboard.html`
* `predictions/templates/predictions/leagues.html`
* `predictions/templates/predictions/league_detail.html`

## Testing Completed

I ran the Django system check successfully:

```text
python manage.py check
```

I also ran the automated tests successfully:

```text
python manage.py test predictions
```

The tests covered:

* Joining a second league after account creation.
* Preventing duplicate league memberships.
* Syncing one prediction across all user leagues.
* Blocking predictions more than 48 hours before kickoff.
* Blocking predictions for placeholder teams.
* Showing the global leaderboard to logged-in users.
* Redirecting logged-out users away from the global leaderboard.
* Showing only league members on individual league pages.
* Preventing users from viewing leagues they are not members of.
* Ensuring global and league leaderboards use the same prediction points.

## Manual Testing Completed

I manually checked that:

* The Matches page loads.
* Future matches outside the prediction window are locked.
* Placeholder fixtures are locked.
* The Leagues page loads.
* Existing leagues are shown.
* Users can join another league using a valid league code.
* Users can click into individual league pages.
* Individual league pages show only that league’s leaderboard.
* The Global Leaderboard shows all app users.
* Logged-out users cannot access the Global Leaderboard.
* Predictions still submit smoothly without a full page refresh.

## Security and Privacy Notes

* The global leaderboard is visible only to logged-in users.
* Users can only view league pages for leagues they are members of.
* Joining a league requires a valid league code.
* Duplicate league memberships are prevented.
* No additional personal data was collected.
* Users still only need a username, password, and league code.
* Predictions are synced across leagues without exposing private league codes.

## Reflection

This update made MatchPick feel much more like a real product.

The original app worked as a portfolio prototype, but this stage improved the actual user experience. Users can now belong to multiple leagues, join new leagues after registration, view private league leaderboards, and compare themselves globally.

The prediction rules are also fairer because users cannot vote too far ahead on unconfirmed fixtures. The app now supports the realistic flow of a World Cup prediction game while keeping the rules simple: predict once, compete everywhere.
