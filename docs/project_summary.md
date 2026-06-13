# MatchPick Project Summary

## Overview

MatchPick is a private football prediction web application built using Django. It allows users to join an invite-only group, submit match predictions, and compete on a leaderboard.

The project was developed as a portfolio application to demonstrate full-stack web development, secure authentication, database design, automated testing, deployment, and privacy-aware design.

## Problem

Football prediction games are often either too public, too complex, or require unnecessary personal information. For a small family/friends competition, users need a simple and private way to predict matches and track rankings.

MatchPick solves this by providing a lightweight invite-only prediction platform.

## Solution

The application allows an organiser to create a competition group and invite code. Users register using the invite code, view fixtures, submit predictions before kickoff, and track their ranking on a leaderboard.

The organiser can manage matches, results, users, groups, and predictions through the Django admin panel.

## Main Features

* Invite-code registration
* Username/password login
* Private competition groups
* Match display
* Prediction voting
* Voting lock after kickoff
* Score/result tracking
* Automatic prediction points
* Leaderboard ranking
* Admin management
* Fixture/result import command
* Live deployment

## Technical Implementation

The backend was built with Django. The app uses Django models for groups, group memberships, matches, and predictions.

The application uses SQLite locally and PostgreSQL in production. Neon is used for the hosted PostgreSQL database, while Render hosts the deployed Django web service.

Static files are handled with WhiteNoise in production. Gunicorn is used as the production application server.

## Security and Privacy

The application was designed using data minimisation. Version 1 does not require email addresses, phone numbers, full names, dates of birth, locations, or profile photos.

Authentication uses Django’s built-in user system, meaning passwords are hashed rather than stored in plaintext.

Sensitive production settings are stored in environment variables rather than being committed to GitHub.

Protected pages require login, and prediction submission also checks group membership.

## Testing

Automated tests were written for the core workflow, including:

* Invite-code registration
* Password hashing
* Protected page access
* Prediction submission
* Prediction updates
* Voting lock rules
* Points calculation
* Leaderboard display

Manual browser testing was also performed locally and on the deployed version.

## Deployment

The application was deployed using:

* GitHub for code hosting
* Render for web app hosting
* Neon for PostgreSQL database hosting
* Gunicorn for application serving
* WhiteNoise for static file serving

The deployed version was tested using a production admin account, production competition group, production test user, fixture import, prediction submission, and leaderboard access.

## Key Design Decisions

### Username and invite code instead of email

The app does not require email in Version 1 because the competition is private and invite-only. This reduces unnecessary personal data collection.

### Django admin retained for organiser control

The Django admin panel provides a reliable organiser interface without needing to build a custom admin dashboard in Version 1.

### Manual fallback retained for results

Fixture/result import was added, but manual admin correction remains available because free football data sources may be incomplete or delayed.

### Smooth prediction submission

Prediction voting was improved with JavaScript fetch requests so users can submit predictions without the page refreshing or jumping position.

## Current Limitations

* Users can only use their first competition group as the active group.
* No password reset flow is included because email is not collected.
* No exact score prediction feature yet.
* No live score updates.
* Admin functions are still handled through Django admin rather than a custom organiser dashboard.

## Future Improvements

Future versions could add:

* Multiple group support
* Exact score prediction
* Group switcher
* User profile/settings page
* Optional email/password reset flow
* More advanced scoring
* Country flags
* Custom organiser dashboard
* Better mobile navigation
* Scheduled fixture/result import

## Reflection

MatchPick shows a complete project lifecycle: planning, implementation, testing, deployment, and refinement. It demonstrates practical Django development and thoughtful design decisions around privacy, usability, and maintainability.
