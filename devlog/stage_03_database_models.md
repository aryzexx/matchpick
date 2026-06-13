# Stage 3 — Database Models

## Goal

The goal of this stage was to create the core database structure for the MatchPick application.

## Actions Completed

- Created the `CompetitionGroup` model to store private prediction groups.
- Created the `GroupMember` model to connect users to groups.
- Created the `Match` model to store football fixtures, kickoff times, match stages and results.
- Created the `Prediction` model to store user predictions and awarded points.
- Added basic point calculation logic where a correct prediction is worth 3 points and an incorrect prediction is worth 0 points.
- Ran Django's system check.
- Created the initial migration file using `makemigrations`.
- Applied the migration using `migrate`.
- Confirmed that the `predictions` migration was applied successfully.

## Design Decision

I decided to separate the data into four main models: groups, group members, matches and predictions. This structure reflects the main workflow of the app: a user joins a private group, views matches, submits predictions and earns points after results are entered.

I used `CompetitionGroup` instead of simply naming the model `Group` because Django already has a built-in authentication group model. Using a more specific name avoids confusion and makes the code clearer.

I also decided not to store unnecessary personal data. Version 1 of the app only needs a username, password and group invite code. Email addresses, phone numbers, full names, dates of birth, locations and profile photos are not required for the competition to work, so they will not be collected through the app.

## Security and Privacy Notes

The app uses Django's built-in authentication system, which means passwords are handled using Django's password hashing mechanism rather than being stored as plaintext.

The database models focus only on data needed for the prediction competition. This supports data minimisation and reduces unnecessary privacy risk.

## Evidence Captured

- `05_models_code.png`
- `06_makemigrations_success.png`
- `07_migrate_success.png`
- `08_predictions_migration_applied.png`

## Reflection

This stage turned the app from a blank Django project into a structured prediction system. The database now has the foundations needed for private groups, fixtures, user predictions and scoring. Creating the models before the user interface helps keep the application organised and easier to expand later.