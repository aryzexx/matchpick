# Stage 7 — API-Ready Match Model

## Goal

The goal of this stage was to upgrade the Match model so that the application can support future fixture and result imports from a free external data source.

## Actions Completed

- Added external source tracking to the Match model.
- Added an external match ID field.
- Added a match status field with scheduled, finished, postponed and cancelled options.
- Added home score and away score fields.
- Added a last synced timestamp field.
- Added score display logic.
- Added automatic result calculation from final scores.
- Updated the admin match interface to show fixture details, score/result fields and external import tracking.
- Created and applied a database migration.
- Confirmed the migration was applied successfully.
- Tested automatic result calculation from a home win score.
- Tested automatic result calculation from a draw score.

## Design Decision

I decided to abandon live score tracking for Version 1 because reliable live-score data is usually paid or heavily rate-limited. Instead, the app will focus on free fixture/result import where possible, with manual admin fallback.

The Match model was upgraded before building the voting and leaderboard screens so that the database structure is ready for future fixture/result import. This avoids building the next stages on a model that would need major changes later.

I also decided to keep manual admin correction available. This is important because free external data may be delayed, incomplete or temporarily unavailable. The organiser should always be able to manually add or correct match information.

## Security and Privacy Notes

This stage did not add any new user personal data. The new fields only relate to football fixtures, scores and external data tracking.

Keeping fixture/result data separate from user prediction data helps maintain a clean structure. User accounts and predictions remain stored inside the application, while external data is only used to update match information.

## Evidence Captured

- `24_match_model_import_fields_migration_created.png`
- `25_match_model_import_fields_migration_applied.png`
- `26_stage7_migrations_confirmed.png`
- `27_admin_match_import_fields_visible.png`
- `28_score_to_result_calculation_test.png`
- `29_draw_result_calculation_test.png`

## Reflection

This stage prepared MatchPick for future automation without making the app dependent on a paid API. The app can still work manually through the admin panel, but the database now contains the fields needed to import fixtures and final results later. This improves the long-term design while keeping the Version 1 scope realistic.