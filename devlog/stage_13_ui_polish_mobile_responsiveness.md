# Stage 13 — UI Polish and Mobile Responsiveness

## Goal

The goal of this stage was to improve the visual quality and mobile responsiveness of the MatchPick application.

## Actions Completed

- Improved the navigation bar with a stronger MatchPick brand identity.
- Updated the homepage with a more polished hero section.
- Improved the login and registration page layout.
- Improved card-based styling across the matches page.
- Improved leaderboard table styling and summary cards.
- Added responsive layout rules for smaller screens.
- Checked the application in desktop view.
- Checked the application in mobile browser view.
- Re-ran automated tests after the UI changes.

## Design Decision

I focused on making the app look suitable for a portfolio project while keeping the design simple and maintainable. I used reusable card, button and layout styling so that the app feels consistent across homepage, authentication pages, matches and leaderboard.

I also prioritised mobile responsiveness because family and friends are likely to use the app from phones rather than desktop computers.

## Security and Privacy Notes

This stage did not add any new personal data or change the authentication workflow. The privacy-focused design remains the same: Version 1 requires only username, password, invite code, group membership and match predictions.

The automated tests were re-run after the UI changes to confirm that visual changes did not break core functionality.

## Evidence Captured

- `54_polished_homepage_desktop.png`
- `55_polished_matches_desktop.png`
- `56_polished_leaderboard_desktop.png`
- `57_mobile_homepage_view.png`
- `58_mobile_matches_view.png`
- `59_mobile_leaderboard_view.png`
- `60_tests_after_ui_polish_passed.png`

## Reflection

This stage improved the usability and presentation quality of MatchPick. The app now looks more professional and works better on smaller screens, making it more realistic for actual family/friend use and stronger as a portfolio project.

## Minor Fix — Login/Register Template Mix-up

During Stage 13 UI polish, the login page temporarily displayed the registration layout. This was caused by a template/view mismatch during file replacement. I fixed the issue by replacing the authentication views, URL routes, login template and registration template with verified versions. After testing, `/login/` showed only username and password fields, while `/register/` showed username, password, confirm password and invite code fields.