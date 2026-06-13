# Stage 10 — Real Leaderboard Calculation

## Goal

The goal of this stage was to replace the placeholder leaderboard with a real leaderboard calculated from group members, predictions and match results.

## Actions Completed

- Updated the leaderboard view to identify the current user's primary competition group.
- Retrieved all members of the user's competition group.
- Calculated each member's total points from saved predictions.
- Calculated predictions made, scored predictions, correct predictions, missed finished matches and accuracy percentage.
- Sorted the leaderboard by total points, correct predictions and username.
- Added rank numbers to leaderboard rows.
- Updated the leaderboard template to display real group standings.
- Highlighted the current user's row.
- Added summary cards for members, finished matches, predictions made and highest points.
- Tested the leaderboard using saved predictions and finished match results.

## Design Decision

I calculated the leaderboard in the Django view rather than storing a separate leaderboard table. This keeps the database simpler because points already exist inside Prediction records. The leaderboard can be recalculated whenever the page is loaded.

For Version 1, the app uses the user's first competition group as their active group. This keeps the user flow simple for a private family/friends competition where most users are expected to belong to one group. A future version could add a group selector for users who join multiple competitions.

I included missed finished matches and accuracy percentage to make the leaderboard more informative than just total points.

## Security and Privacy Notes

The leaderboard page requires login. Users can only see the leaderboard for their own competition group.

The leaderboard displays usernames only. It does not display email addresses, phone numbers, full names, locations or other unnecessary personal data.

## Evidence Captured

- `40_real_leaderboard_page.png`
- `41_leaderboard_current_user_highlighted.png`
- `42_leaderboard_points_after_result.png`
- `43_leaderboard_multiple_users.png`

## Reflection

This stage completed the main competition loop: users can join a group, view matches, submit predictions and see a leaderboard based on points. This makes MatchPick function as a real private football prediction app, even before automated fixture/result import is added.