# Stage 2 — Django Project Setup

## Goal

The goal of this stage was to create the initial Django project structure and confirm that the web application can run locally in a browser.

## Actions Completed

- Removed the unused placeholder `app` folder.
- Created a Django project called `config`.
- Confirmed that `manage.py` was created in the root project folder.
- Started the Django development server.
- Opened the local web application at `http://127.0.0.1:8000/`.
- Confirmed that the Django installation page loaded successfully.
- Created a Django app called `predictions`.
- Registered the `predictions` app inside `config/settings.py`.

## Design Decision

I used `config` as the Django project folder because it separates project-level settings from the main application features. I used `predictions` as the main app name because the core purpose of MatchPick is to allow users to predict football match outcomes.

This separation makes the project easier to maintain because global settings are stored in one place, while app-specific features such as matches, groups, predictions and leaderboards will be developed inside the `predictions` app.

## Evidence Captured

- `04_django_first_server.png`

## Reflection

This stage confirmed that the basic Django project is working locally. Running the server successfully provides a foundation for building the rest of the MatchPick application in controlled stages.