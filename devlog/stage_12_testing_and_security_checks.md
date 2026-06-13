# Stage 12 — Testing and Security Checks

## Goal

The goal of this stage was to test the core MatchPick workflow and confirm that the main security and privacy rules are working as intended.

## Actions Completed

- Added automated tests in `predictions/tests.py`.
- Tested password hashing.
- Tested invalid invite-code rejection.
- Tested valid invite-code registration and group membership creation.
- Tested that matches and leaderboard pages require login.
- Tested that normal users do not see the admin link.
- Tested that staff/admin users can see the admin link.
- Tested prediction creation before kickoff.
- Tested prediction updates before kickoff.
- Tested that predictions are rejected after voting is locked.
- Tested that users without a group cannot submit predictions.
- Tested match result calculation from final scores.
- Tested correct and incorrect prediction points.
- Tested leaderboard display using real group members and prediction points.
- Created a manual testing and security checklist.
- Ran manual browser checks on the main pages.
- Ran Django's deployment-style check to identify production security settings that must be reviewed before deployment.

## Design Decision

I added automated tests before further polishing or deployment because the core workflow is now large enough that manual testing alone would be unreliable. Automated tests make it easier to confirm that future changes do not break registration, prediction voting, locking rules or leaderboard behaviour.

I also created a manual checklist because some behaviours are easier to confirm visually, such as page layout, navigation visibility and user-facing messages.

## Security and Privacy Notes

The tests confirm that passwords are not stored as plaintext. Django's authentication system stores password hashes and verifies passwords using `check_password`.

The app continues to follow data minimisation. Version 1 registration requires only a username, password and invite code. It does not require email addresses, phone numbers, full names, dates of birth, locations or profile photos.

Protected pages require login, and prediction submission checks both authentication and group membership.

The deployment check produced expected warnings because the app is still running in local development mode. These warnings will need to be addressed before public deployment.

## Evidence Captured

- `49_django_system_check_success.png`
- `50_automated_tests_passed.png`
- `51_manual_browser_check_matches.png`
- `52_manual_browser_check_leaderboard.png`
- `53_deployment_check_warnings_local_dev.png`

## Reflection

This stage improved confidence in the application by testing the main user journey and security controls. The automated test suite confirms that the core private competition workflow works correctly. The manual checklist provides additional evidence that the app has been reviewed from a user and security perspective.