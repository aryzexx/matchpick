# Stage 9 — Prediction Voting

## Goal

The goal of this stage was to allow authenticated users to submit and update match predictions before kickoff.

## Actions Completed

- Added a prediction submission view.
- Added a prediction URL route for each match.
- Updated the matches view so each match displays the current user's prediction if one exists.
- Added prediction buttons for home win, draw and away win.
- Allowed users to update predictions before kickoff.
- Locked prediction voting after kickoff or when a match is not scheduled.
- Displayed saved predictions on the matches page.
- Confirmed that predictions are stored in the admin panel.

## Design Decision

I added prediction voting directly to the matches page because this creates a simple user flow. Users can view fixtures and vote in the same place rather than needing to open a separate match detail page.

I used the existing Match `is_voting_open` property to control whether prediction buttons should appear. This keeps the voting rule consistent: users can only vote before kickoff while the match is scheduled.

For Version 1, the app uses the user's first competition group when saving predictions. This is suitable for the initial private competition use case where most users belong to one group. A future version could add a group selector if users join multiple competitions.

## Security and Privacy Notes

Prediction submission requires login. The prediction view also checks that the user belongs to a competition group before allowing a vote to be saved.

The form uses Django's CSRF protection because prediction submission changes data in the database.

Users cannot submit or update predictions after voting is locked.

## Evidence Captured

- `35_prediction_buttons_visible.png`
- `36_prediction_submitted_success.png`
- `37_prediction_update_success.png`
- `38_locked_match_no_voting_buttons.png`
- `39_prediction_visible_in_admin.png`

## Reflection

This stage added the core interaction of the MatchPick app. Users can now vote on match outcomes and update their choice before kickoff. This makes the app usable as a private prediction competition, even before the leaderboard is fully implemented.