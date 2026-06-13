# Stage 6 — Authentication and Invite-Code Joining

## Goal

The goal of this stage was to add user registration, login, logout and invite-code joining to the MatchPick application.

## Actions Completed

- Created a custom registration form in `predictions/forms.py`.
- Configured the registration form to collect only username, password and invite code.
- Added validation to check whether the invite code belongs to an existing competition group.
- Created a registration view.
- Created a login view using Django's authentication system.
- Created a logout view using a POST request.
- Protected the matches and leaderboard pages so only logged-in users can access them.
- Added authentication routes for registration, login and logout.
- Added login-related settings to `config/settings.py`.
- Created registration and login templates.
- Updated the navigation bar to show different options depending on whether the user is logged in.
- Tested invalid invite-code rejection.
- Tested valid account creation using an invite code.
- Confirmed that a new group membership was created automatically.
- Tested logout.
- Tested login.

## Design Decision

I decided to keep registration minimal by collecting only a username, password and invite code. This supports the app's data-minimisation approach because email addresses, phone numbers, full names, dates of birth, locations and profile photos are not required for the competition to work.

I also decided that users should only be able to access matches and leaderboards after logging in. This keeps the prediction competition private and prevents public visitors from viewing group-related pages.

Invite-code joining was added so that a user can automatically join the correct private competition group during registration. This creates a smoother user flow because the organiser does not need to manually add every user through the admin panel.

## Security and Privacy Notes

Passwords are handled through Django's built-in authentication system rather than being stored manually. The registration form does not collect email addresses or other unnecessary personal information.

The logout action uses a POST request instead of a simple GET link. This is a safer design because logging out changes the user's session state.

The login view checks that redirect URLs are safe before redirecting users after login. This reduces the risk of unsafe redirect behaviour.

## Evidence Captured

- `19_invalid_invite_code_rejected.png`
- `20_registration_valid_invite_success.png`
- `21_logout_success.png`
- `22_login_success.png`
- `23_group_membership_created_from_invite.png`

## Reflection

This stage changed MatchPick from a public prototype into a private user-based application. Users can now create accounts, join groups using invite codes and access protected pages. This is a major step because the app now supports the core private competition model needed for family and friends.