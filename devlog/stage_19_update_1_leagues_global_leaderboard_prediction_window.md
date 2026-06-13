# Stage 19 — Update 1: Leagues, Global Leaderboard, and Prediction Window

## Goal

The goal of this update was to improve MatchPick after live testing showed that the original leaderboard and league behaviour was too limited for real use.

## Issue Found

The original version assumed that users would only belong to one league. During testing, I identified that a user may need to participate in multiple leagues, such as a family league and a friends league.

I also identified that the original prediction system allowed users to vote too far ahead, including future knockout fixtures where teams had not been confirmed yet.

## Actions Completed

* Added a Leagues page.
* Added the ability for logged-in users to join another league using a league code.
* Added individual league pages.
* Changed the existing leaderboard page into a global leaderboard.
* Made the global leaderboard visible only to logged-in users.
* Added league-specific leaderboard views under each league page.
* Preserved the rule that users make one prediction per match.
* Ensured the same prediction counts in every league the user belongs to.
* Added prediction window logic.
* Locked voting for matches more than 48 hours away.
* Locked voting for matches where teams are not confirmed.
* Kept voting locked after kickoff.
* Updated automated tests for the new behaviour.

## Design Decision

The correct rule is: one user, one match, one prediction.

Leagues should control who appears in each leaderboard, not allow users to make different predictions for the same match.

This keeps the game fair because a user cannot predict one result in a family league and a different result in a friends league.

## Prediction Window Decision

I decided not to allow predictions for all 104 fixtures immediately because many future knockout matches may not have confirmed teams. Allowing predictions too early would make the game feel random and unfair.

I also decided not to restrict predictions to only tomorrow’s matches because that would be too strict and could make users feel forced to check the app every day.

The chosen rule was:

* Predictions open 48 hours before kickoff.
* Predictions lock at kickoff.
* Matches with unconfirmed teams stay locked.

This gives users enough time to predict upcoming matches while preventing unrealistic early predictions.

## Security and Privacy Notes

* The global leaderboard is visible only to logged-in users.
* Users can only view league pages for leagues they are members of.
* Joining a league requires a valid league code.
* Duplicate league memberships are prevented.
* No additional personal data was collected.
* Users still only need a username, password, and league code.

## Reflection

This update made MatchPick more realistic and usable. The app now supports multiple private leagues while keeping prediction rules simple and fair. The global leaderboard adds a wider competition view, while individual league pages keep family and friend groups separate.
