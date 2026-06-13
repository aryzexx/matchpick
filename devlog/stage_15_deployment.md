# Stage 15 — Deployment

## Goal

The goal of this stage was to deploy MatchPick online so that it can be accessed through a public web link.

## Actions Completed

- Initialised a Git repository locally.
- Created a GitHub repository for the MatchPick source code.
- Pushed the project code to GitHub.
- Created a hosted PostgreSQL database using Neon.
- Created a Render web service connected to the GitHub repository.
- Added deployment environment variables including `SECRET_KEY`, `DEBUG`, `DATABASE_URL`, `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`.
- Deployed the Django app using Render.
- Ran deployment build steps including dependency installation, static file collection and database migrations.
- Created a production superuser.
- Logged into the production Django admin panel.
- Created a production competition group and invite code.
- Imported fixture data on the deployed app.
- Tested registration on the deployed app.
- Tested matches, predictions and leaderboard pages online.
- Checked that secrets and local database files were not exposed in the GitHub repository.

## Design Decision

I deployed the app using a managed web hosting platform and a hosted PostgreSQL database rather than trying to run the app from my own laptop. This makes the application accessible through a real URL and better reflects how web applications are deployed professionally.

I used environment variables for sensitive production configuration. This avoids hardcoding secrets, database credentials or deployment-specific hostnames in the source code.

The local SQLite database was not deployed. Production uses PostgreSQL, which is more appropriate for hosted deployment.

## Security and Privacy Notes

The production `SECRET_KEY` and `DATABASE_URL` are stored as environment variables rather than being committed to GitHub.

The GitHub repository should not contain `.env`, `.venv`, `db.sqlite3` or any real credentials.

The app still follows the data-minimisation approach. Registration requires only username, password and invite code.

## Evidence Captured

- `65_git_version_check.png`
- `66_initial_git_commit_success.png`
- `67_github_repo_pushed.png`
- `68_neon_database_created.png`
- `69_render_deploy_success.png`
- `70_live_homepage_deployed.png`
- `71_production_superuser_created.png`
- `72_production_admin_login_success.png`
- `73_production_group_created.png`
- `74_production_fixture_import_success.png`
- `75_production_imported_matches_visible.png`
- `76_production_user_registration_success.png`
- `77_production_matches_page.png`
- `78_production_prediction_submit_success.png`
- `79_production_leaderboard_page.png`
- `80_github_no_secrets_check.png`

## Reflection

This stage moved MatchPick from a local development project to a deployed web application. The app can now be accessed through a live URL, making it usable by real users and suitable for portfolio demonstration. Deployment also introduced important production concerns such as environment variables, hosted databases, static files and secret management.


## Minor UX Improvement — Smooth Prediction Submission

During live testing, I noticed that submitting a prediction caused the matches page to refresh and move position. This was functional but annoying for users because they would need to scroll again after each prediction.

I improved this by changing prediction submission to use JavaScript fetch requests. The backend now returns a JSON response for JavaScript submissions, while still keeping normal form submission as a fallback. This allows the selected prediction button and current prediction text to update immediately without refreshing the page.

This made the live app feel smoother and more suitable for real user testing.