# MatchPick Demo Script

## Demo Goal

This demo shows how MatchPick works as a private football prediction competition app.

The demo should take approximately 3–5 minutes.

## Before Recording

Open these tabs:

1. Live MatchPick homepage
2. Live MatchPick register page in an InPrivate window
3. Live MatchPick admin page
4. GitHub repository
5. README section on GitHub

Use a test user account, not your real admin password, during the normal user demo.

## Demo Structure

### 1. Introduction

“MatchPick is a private football prediction web application built with Django. It allows users to join an invite-only competition group, submit match predictions before kickoff, and compete on a leaderboard.”

### 2. Problem

“The problem I wanted to solve was that many prediction games are too public, too complicated, or collect unnecessary personal data. For a small family or friends competition, a simpler private app is more appropriate.”

### 3. Registration and Privacy

Show the registration page.

Say:

“Users register with only a username, password, and invite code. Version 1 does not require email addresses, phone numbers, full names, dates of birth, locations, or profile photos. This follows a data-minimisation approach.”

### 4. Invite-Code Access

Show the invite code field.

Say:

“The invite code restricts access to known users. This prevents random users from joining private competition groups.”

### 5. Matches Page

Log in as a test user and open the matches page.

Say:

“After logging in, users can view available fixtures. Each match shows the teams, kickoff time, match status, score/result information, and whether voting is open or locked.”

### 6. Prediction Voting

Scroll to a scheduled match and submit a prediction.

Say:

“Users can choose home win, draw, or away win. Prediction submission now works smoothly without a full page refresh, so the page does not jump around after each vote.”

### 7. Voting Lock

Show a locked/finished match.

Say:

“Voting is locked after kickoff or when a match is no longer scheduled. This prevents users from changing predictions after the match has started or finished.”

### 8. Leaderboard

Open the leaderboard page.

Say:

“The leaderboard ranks group members based on prediction points. A correct prediction is worth 3 points, while incorrect or missed predictions are worth 0 points.”

### 9. Admin Panel

Open the admin panel.

Say:

“The organiser can manage groups, users, matches, results, and predictions through Django admin. This avoids needing to build a custom organiser dashboard in Version 1.”

Do not show or say any passwords.

### 10. Fixture Import

Briefly mention the import command.

Say:

“The app also includes a Django management command for importing fixture and result data from a free football data source. Manual result editing remains available as a fallback.”

### 11. GitHub and Documentation

Show GitHub README.

Say:

“The project is documented on GitHub with setup instructions, testing notes, deployment details, security and privacy decisions, and future improvements.”

### 12. Closing Reflection

Say:

“Overall, MatchPick demonstrates a complete full-stack Django workflow: database modelling, authentication, prediction submission, scoring, leaderboard calculation, testing, deployment, and privacy-aware design.”

## Suggested Evidence Screenshots

Capture these screenshots locally:

* live homepage
* registration page
* matches page
* smooth prediction submission
* leaderboard
* admin panel
* GitHub README
* project summary document
* clean GitHub repository without evidence folder or secrets

## Things Not to Show

Do not show:

* production passwords
* Neon database password
* Render secret values
* `.env` file
* real `DATABASE_URL`
* real `SECRET_KEY`
* admin password entry
