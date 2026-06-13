# Stage 5 — Basic Pages and Navigation

## Goal

The goal of this stage was to create the first user-facing pages for the MatchPick web application and replace Django's default homepage with a custom MatchPick homepage.

## Actions Completed

- Created template folders inside the `predictions` app.
- Created static folders for app-specific CSS.
- Created a reusable `base.html` template.
- Created a custom homepage template.
- Created a placeholder matches page.
- Created a placeholder leaderboard page.
- Added a navigation bar linking to Home, Matches, Leaderboard and Admin.
- Created basic CSS styling for the website.
- Added view functions in `predictions/views.py`.
- Created `predictions/urls.py` to define app-level URL routes.
- Updated `config/urls.py` to include the prediction app routes.
- Confirmed that the root URL now loads the MatchPick homepage.
- Confirmed that `/matches/`, `/leaderboard/` and `/admin/` work correctly.

## Design Decision

I created a reusable base template so that common layout elements such as the navigation bar, page container and footer do not need to be repeated across every page. This makes the project easier to maintain because future layout changes can be made in one file.

I also created placeholder pages for matches and leaderboard before connecting them to real data. This allows the navigation and page structure to be tested before adding more complex database queries, forms and user authentication.

## Security and Privacy Notes

The homepage includes a privacy-focused message explaining that Version 1 of the app only needs a username, password, group membership and match predictions. This supports the project's data-minimisation approach.

The admin panel remains separate at `/admin/`, which keeps organiser management separate from normal user-facing pages.

## Evidence Captured

- `15_matchpick_homepage.png`
- `16_matches_page_placeholder.png`
- `17_leaderboard_page_placeholder.png`
- `18_admin_still_working_after_routes.png`

## Reflection

This stage changed the project from a backend/admin-only Django system into the beginning of a real user-facing web application. The homepage, matches page and leaderboard page now provide a clear structure for future features. Creating the navigation early also makes it easier to test user flow as the app develops.