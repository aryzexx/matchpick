# Stage 8 — Real Matches from the Database

## Goal

The goal of this stage was to replace the placeholder matches page with a real database-driven matches page.

## Actions Completed

- Updated the matches view to query Match records from the database.
- Passed match data and match counts into the matches template.
- Updated the matches page template to display real fixture information.
- Displayed match team names, kickoff time, stage, status, score, result and data source.
- Added a friendly empty state for when no matches exist.
- Added a group access section showing the user's competition group membership.
- Added styling for match cards, status labels, voting labels and summary cards.
- Updated the navigation bar so the admin link is only visible to staff/admin users.
- Tested the matches page as an admin user.
- Tested the matches page as a normal user.

## Design Decision

I replaced the placeholder matches page with a database-driven page before adding prediction voting. This keeps the development process controlled because users need to be able to view real matches before they can vote on them.

I also decided to display the match source as either manual entry or an external source. This supports the future fixture/result import feature while still keeping manual admin entry available as a fallback.

The admin link was hidden from normal users to make the interface cleaner and to separate organiser functionality from normal user functionality.

## Security and Privacy Notes

The matches page remains protected by login, so only authenticated users can view the fixture list.

Normal users do not see the admin link. The admin panel is still protected by Django's staff/superuser permissions.

This stage did not add any new personal data. The new page displays fixture and group access information only.

## Evidence Captured

- `30_real_matches_from_database.png`
- `31_match_status_and_score_display.png`
- `32_normal_user_no_admin_link.png`
- `33_admin_user_admin_link_visible.png`

## Reflection

This stage made the application feel more like a real prediction app because the matches page now displays actual data from the database. This creates the foundation for the next stage, where users will be able to submit predictions for these matches.

## Minor Fix — Matches Page Styling

During testing, the matches page displayed the correct database content but did not initially appear with the intended card-based styling. The homepage and leaderboard styling worked correctly, so I isolated the issue to the matches template/CSS behaviour. I fixed this by replacing the matches template with a self-contained styled version, then confirmed that the matches page displayed summary cards, group access, match cards, status labels and score/result/source sections correctly.