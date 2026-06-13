# Stage 14 — Deployment Preparation

## Goal

The goal of this stage was to prepare MatchPick for deployment while also cleaning up the user-facing matches page.

## Actions Completed

- Removed the `Source` field from the user-facing matches page.
- Kept external source tracking in the database/admin for fixture import management.
- Installed deployment-related packages: Gunicorn, WhiteNoise, dj-database-url and psycopg.
- Updated Django settings to support environment variables.
- Added `DATABASE_URL` support for PostgreSQL deployment.
- Added WhiteNoise middleware and static file storage settings.
- Added `STATIC_ROOT` for collected static files.
- Created `.env.example` to document required deployment environment variables.
- Created `.gitignore` to avoid committing virtual environments, local databases and secrets.
- Created `build.sh` for deployment build steps.
- Ran Django checks.
- Re-ran automated tests.
- Ran `collectstatic` successfully.

## Design Decision

I removed `Source` from the user-facing matches page because normal users do not need to know whether a match was manually entered or imported. This information is still useful for the organiser, so it remains available in the admin panel and database.

I prepared the project for a free deployment path using a hosted Django web service and an external PostgreSQL database. The app now reads sensitive deployment settings from environment variables rather than hardcoding them in the project.

WhiteNoise was added so static files can be served correctly in deployment.

## Security and Privacy Notes

Sensitive values such as `SECRET_KEY` and `DATABASE_URL` are now expected to come from environment variables in deployment.

The `.gitignore` file prevents local databases, virtual environments and `.env` files from being committed.

This stage did not add any new personal data. The app still follows the data-minimisation approach: username, hashed password, invite-code group membership and prediction data only.

## Evidence Captured

- `61_source_removed_from_matches_page.png`
- `62_deployment_settings_check_success.png`
- `63_collectstatic_success.png`
- `64_tests_after_deployment_prep_passed.png`

## Reflection

This stage made the project more deployment-ready and improved the user interface by removing unnecessary technical information from the matches page. The app now separates organiser/admin metadata from normal user-facing information more clearly.