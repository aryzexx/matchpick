# MatchPick

MatchPick is a private football prediction web application built with Django. It allows users to join an invite-only competition group, predict football match outcomes before kickoff, and compete on a leaderboard.

The project was designed as a portfolio web application to demonstrate backend development, authentication, database modelling, deployment, testing, and security/privacy-aware design.

## Live Demo

Live app: https://matchpick.onrender.com/
GitHub repository: (https://github.com/aryzexx/matchpick)

## Project Purpose

Many football prediction games are either too public, too complicated, or require unnecessary personal data. MatchPick solves this by providing a simple private prediction competition for family and friends.

Users only need a username, password, and invite code to join. They can then view fixtures, submit predictions, and track rankings in their competition group.

## Core Features

* Invite-code registration
* Username and password login
* Private competition groups
* Match fixture list
* Prediction voting before kickoff
* Voting lock after kickoff or when a match is no longer scheduled
* Score and result tracking
* Automatic prediction scoring
* Group leaderboard
* Admin panel for organiser management
* Fixture/result import command using a free football data source
* Deployed online using Render and Neon PostgreSQL

## Tech Stack

* Python
* Django
* SQLite for local development
* PostgreSQL for production
* Neon for hosted PostgreSQL database
* Render for web app deployment
* Gunicorn as production application server
* WhiteNoise for static files
* HTML, CSS, and JavaScript
* Git and GitHub for version control

## Security and Privacy Design

MatchPick follows a data-minimisation approach.

Version 1 collects only:

* Username
* Hashed password
* Group membership
* Match predictions
* Prediction points

Version 1 does not collect:

* Email address
* Phone number
* Full legal name
* Date of birth
* Location
* Profile photo

Security/privacy measures include:

* Django built-in authentication
* Password hashing using Django’s authentication system
* Login-required protection for matches and leaderboard pages
* Invite-code controlled registration
* CSRF protection on forms
* Admin-only organiser functionality
* Environment variables for production secrets
* `.env`, local database files, virtual environment files, and collected static files excluded from GitHub

## Main User Flow

1. Organiser creates a competition group and invite code.
2. User registers with username, password, and invite code.
3. User views available matches.
4. User submits or updates predictions before kickoff.
5. Organiser/import process records results.
6. Leaderboard updates based on prediction points.

## Scoring

The current scoring model is simple:

* Correct prediction: 3 points
* Incorrect prediction: 0 points
* Missed prediction: 0 points

Predictions are based on the main match outcome:

* Home win
* Draw
* Away win

## Deployment

The application is deployed using:

* Render for the Django web service
* Neon for PostgreSQL database hosting
* Gunicorn for running the Django app
* WhiteNoise for serving static files
* Environment variables for production settings

Production environment variables include:

* `SECRET_KEY`
* `DEBUG`
* `DATABASE_URL`
* `ALLOWED_HOSTS`
* `CSRF_TRUSTED_ORIGINS`

## Local Setup

Clone the repository:

```bash
git clone YOUR_GITHUB_REPO_URL_HERE
cd matchpick
```

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate.bat
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Create a local superuser:

```bash
python manage.py createsuperuser
```

Run the development server:

```bash
python manage.py runserver
```

Open the app locally:

```text
http://127.0.0.1:8000/
```

## Running Tests

Run the automated test suite:

```bash
python manage.py test predictions
```

The tests cover:

* Password hashing
* Invite-code registration
* Protected pages
* Admin link visibility
* Prediction creation
* Prediction updates
* Voting lock rules
* Result calculation
* Points calculation
* Leaderboard display

## Fixture Import

MatchPick includes a Django management command for importing World Cup fixture/result data from a free football data source.

Dry run:

```bash
python manage.py import_openfootball_worldcup --limit 5 --dry-run
```

Import a small test batch:

```bash
python manage.py import_openfootball_worldcup --limit 10
```

Import the full available dataset:

```bash
python manage.py import_openfootball_worldcup
```

Manual admin entry remains available as a fallback if imported data is incomplete or delayed.

## Project Status

Current version: Version 1 deployed prototype.

Completed:

* Registration and login
* Invite-code group joining
* Match display
* Prediction voting
* Smooth no-refresh prediction submission
* Leaderboard calculation
* Fixture/result import command
* Deployment to Render and Neon
* Automated tests
* Basic responsive UI

## Future Improvements

Potential future improvements include:

* Group selector for users in multiple competitions
* More advanced scoring rules
* Exact score predictions
* Group creation from the user interface
* Password reset flow
* Email verification if email is added in a future version
* Better fixture import monitoring
* Country flags and additional fixture metadata
* Improved mobile navigation
* User profile/settings page
* Public landing page separate from authenticated app pages

## Reflection

MatchPick demonstrates a complete full-stack Django workflow: database modelling, authentication, user interaction, admin management, testing, deployment, and privacy-aware design.

The project started as a local Django app and was developed into a deployed web application with a live database and production configuration. It is suitable as a portfolio project because it shows both technical implementation and practical design decision-making.
