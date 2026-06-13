# Stage 4 — Admin Panel Setup

## Goal

The goal of this stage was to configure Django's admin panel so that the MatchPick data can be managed through a secure organiser interface.

## Actions Completed

- Registered the MatchPick models in `predictions/admin.py`.
- Added admin list displays for competition groups, group members, matches and predictions.
- Added search and filter options to make admin management easier.
- Added inline group membership management inside competition groups.
- Created a Django superuser account.
- Logged into the Django admin panel.
- Confirmed that the MatchPick models appear in the admin interface.
- Created a test competition group.
- Added a test group member.
- Created a test match.
- Created a test prediction.
- Entered a match result and confirmed that points were updated correctly.

## Design Decision

I used Django's built-in admin panel as the first organiser interface because it provides a secure and functional way to manage the application without building a custom admin dashboard immediately. This allows the core data workflow to be tested early.

I also added a points recalculation step to the match admin save process. This is needed because predictions are usually submitted before the match result is known. When the organiser enters the result later, existing predictions must be recalculated so the leaderboard can use accurate points.

## Security and Privacy Notes

The admin panel is protected by Django authentication and should only be accessible to trusted organiser accounts. Normal users should not be given staff or superuser access.

No email address was required when creating the local admin account. This supports the app's data-minimisation approach because the competition does not need email addresses to function in Version 1.

## Evidence Captured

- `09_admin_models_registered.png`
- `10_admin_competition_group_created.png`
- `11_admin_match_created.png`
- `12_admin_prediction_created.png`
- `13_admin_scoring_test_success.png`

## Reflection

This stage made the application manageable through Django's admin interface. The organiser can now create groups, add matches, manage group members and enter results. Testing a prediction and then entering a result confirmed that the core scoring logic works at database/admin level before building the user-facing screens.

## Minor Fix

After reviewing the Django admin panel, I noticed that Django automatically displayed the plural form of `Match` as `Matchs`. I corrected this by adding `verbose_name = "Match"` and `verbose_name_plural = "Matches"` to the `Match` model's Meta class. This improved the professionalism and readability of the admin interface.