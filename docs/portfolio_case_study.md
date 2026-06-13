# MatchPick Portfolio Case Study

## Project Title

MatchPick — Private Football Prediction Competition Web App

## Project Type

Full-stack Django web application

## Live Links

Live app: https://matchpick.onrender.com/
GitHub repository: https://github.com/aryzexx/matchpick

## Project Overview

MatchPick is a private football prediction web application built with Django. It allows users to join an invite-only competition group, view football fixtures, submit match predictions before kickoff, and compete on a group leaderboard.

The project was designed as a portfolio application to demonstrate practical backend development, secure authentication, database modelling, testing, deployment, and privacy-aware design.

## Problem

Many football prediction games are either public, overly complex, or require unnecessary personal information such as email addresses, phone numbers, profile details, or social login.

For a small family or friends competition, users need something simpler:

* private access
* quick registration
* match prediction voting
* automatic scoring
* leaderboard ranking
* minimal personal data collection

## Solution

MatchPick solves this by providing an invite-only prediction platform.

Users register using a username, password, and invite code. Once registered, they can view matches, submit predictions, and track their position on the leaderboard.

The organiser can manage groups, matches, results, users, and predictions through the Django admin panel.

## Core Features

* Invite-code registration
* Username and password login
* Private competition groups
* Match fixture list
* Prediction voting before kickoff
* Voting lock after kickoff
* Score and result tracking
* Automatic points calculation
* Leaderboard ranking
* Smooth prediction submission without page refresh
* Django admin organiser controls
* Fixture/result import command using a free football data source
* Deployed production version using Render and Neon PostgreSQL

## Technology Stack

* Python
* Django
* HTML
* CSS
* JavaScript
* SQLite for local development
* PostgreSQL for production
* Neon for hosted PostgreSQL
* Render for web hosting
* Gunicorn for production application serving
* WhiteNoise for static file handling
* Git and GitHub for version control

## Main Data Models

The application uses four main models:

### CompetitionGroup

Stores private competition groups and invite codes.

### GroupMember

Links users to groups and stores their role.

### Match

Stores fixture details, kickoff time, stage, status, scores, results, and external import metadata.

### Prediction

Stores user predictions and awarded points.

## Security and Privacy Design

MatchPick was designed using data minimisation.

Version 1 collects only:

* username
* hashed password
* group membership
* match predictions
* prediction points

Version 1 does not collect:

* email address
* phone number
* full legal name
* date of birth
* location
* profile photo

Security measures include:

* Django built-in authentication
* password hashing through Django
* login-required pages
* invite-code controlled registration
* CSRF protection on forms
* admin-only organiser controls
* environment variables for deployment secrets
* local database and `.env` files excluded from GitHub

## Testing

Automated tests were created for the main workflow. The tests cover:

* password hashing
* invalid invite-code rejection
* valid invite-code registration
* protected matches and leaderboard pages
* admin link visibility
* prediction creation
* prediction updates
* voting lock rules
* result calculation
* correct and incorrect prediction points
* leaderboard display

Manual testing was also carried out locally and on the deployed production app.

## Deployment

The app was deployed online using:

* GitHub for source code
* Render for the Django web service
* Neon for PostgreSQL database hosting
* Gunicorn for running Django in production
* WhiteNoise for serving static files

Production configuration uses environment variables for sensitive settings such as `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`, and `CSRF_TRUSTED_ORIGINS`.

## Key Design Decisions

### 1. Invite-code registration

Invite codes were used to keep the competition private and prevent unknown users from joining.

### 2. No email required in Version 1

Email was not required because the app is designed for a small private group. This reduces unnecessary personal data collection.

### 3. Django admin for organiser controls

Instead of building a custom organiser dashboard in Version 1, Django admin was used for reliable group, user, match, result, and prediction management.

### 4. Manual fallback for results

Fixture import was added, but manual admin editing remains available because free data sources may be incomplete or delayed.

### 5. Smooth prediction submission

Prediction voting was improved using JavaScript fetch requests so users can submit predictions without the page refreshing or jumping position.

## Challenges and Fixes

### Login/register template issue

During UI polishing, the login page temporarily displayed registration fields. This was fixed by checking the authentication views and replacing the login/register templates with verified versions.

### Static files during testing

After adding production static-file handling, local tests initially failed because Django tried to use production manifest static files. This was fixed by using normal static file storage during testing and local development.

### Production admin creation

Render Shell was unavailable on the free plan, so the production superuser was created locally by temporarily connecting the local Django project to the Neon production database.

### Prediction page refresh

Prediction submission originally refreshed the page and moved the user position. This was improved by using JavaScript fetch requests and JSON responses.

### GitHub repository cleanup

Evidence screenshots were removed from the public GitHub repository and kept locally. Sensitive files such as `.env`, `.venv`, `db.sqlite3`, and production secrets were kept out of GitHub.

## Current Limitations

* Users currently use their first competition group as the active group.
* No group switcher is included yet.
* No password reset flow is included because email is not collected.
* No exact score prediction feature yet.
* No live score updates.
* Organiser features are handled through Django admin rather than a custom dashboard.

## Future Improvements

Possible future improvements include:

* multiple group support
* exact score predictions
* custom organiser dashboard
* optional email/password reset flow
* country flags
* user profile/settings page
* more advanced scoring rules
* scheduled fixture/result imports
* better mobile navigation
* improved admin reporting

## Final Reflection

MatchPick demonstrates a complete full-stack Django project lifecycle. The project covers planning, modelling, authentication, user interaction, automated testing, deployment, production database setup, and user experience refinement.

The project is suitable for portfolio use because it shows both technical implementation and practical decision-making around privacy, security, usability, and deployment.
