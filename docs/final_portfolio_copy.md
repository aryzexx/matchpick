# MatchPick — Final Portfolio Copy

## One-Line Project Description

MatchPick is a deployed Django web application for running private football prediction competitions with invite-code registration, match predictions, automatic scoring, and group leaderboards.

## Short Portfolio Description

MatchPick is a full-stack Django web application that allows users to join a private football prediction group using an invite code, submit match predictions before kickoff, and compete on a leaderboard.

The project demonstrates backend development, database modelling, authentication, testing, deployment, and privacy-aware design. It was deployed using Render for the web service and Neon PostgreSQL for the production database.

## Longer Portfolio Description

MatchPick is a private football prediction competition web app built with Django. The app allows users to register with a username, password, and invite code, then submit predictions for scheduled football matches. Predictions are locked after kickoff, results can be managed by the organiser, and the leaderboard automatically ranks users based on prediction points.

The project was designed with data minimisation in mind. Version 1 does not require email addresses, phone numbers, full names, dates of birth, locations, or profile photos. It uses Django’s built-in authentication system, CSRF protection, login-required pages, and environment variables for production secrets.

The application includes a deployed production version, a PostgreSQL production database, automated tests, GitHub documentation, fixture import functionality, and a smoother JavaScript-based prediction submission flow that avoids unnecessary page refreshes.

## CV Bullet Points

* Built and deployed MatchPick, a full-stack Django football prediction web app with invite-code registration, match prediction voting, automatic scoring, and group leaderboard functionality.
* Designed Django models for competition groups, group members, matches, and predictions, including voting lock rules and points calculation.
* Implemented authentication using Django’s built-in user system, including password hashing, login-required pages, CSRF-protected forms, and role-aware admin access.
* Applied privacy-by-design principles by avoiding unnecessary personal data collection such as email addresses, phone numbers, full names, dates of birth, locations, and profile photos.
* Added automated tests covering registration, invite-code validation, protected pages, prediction submission, voting locks, scoring, and leaderboard display.
* Deployed the application using Render, Neon PostgreSQL, Gunicorn, WhiteNoise, GitHub, and environment-variable based production configuration.
* Improved user experience by implementing smooth prediction submission using JavaScript fetch requests, allowing prediction updates without full page refreshes.

## LinkedIn Project Post

I recently built and deployed MatchPick, a private football prediction competition web app using Django.

The idea was to create a simple invite-only platform where family or friends can join a private group, predict match outcomes before kickoff, and compete on a leaderboard.

Some of the main features include:

* Invite-code registration
* Username/password authentication
* Match prediction voting
* Voting lock after kickoff
* Automatic points calculation
* Group leaderboard
* Django admin organiser controls
* Fixture/result import command
* Smooth prediction submission without page refresh
* Deployment using Render and Neon PostgreSQL

A key focus of the project was privacy-aware design. Version 1 only requires a username, password, invite code, group membership, and prediction data. It does not require email addresses, phone numbers, full names, dates of birth, locations, or profile photos.

This project helped me practise Django models, authentication, database relationships, testing, deployment, environment variables, PostgreSQL, static files, and production debugging.

Live app: [add live link]
GitHub: [add GitHub link]

## Interview Explanation

MatchPick is a private football prediction app I built with Django. The core problem was that many prediction platforms are too public or collect more personal information than necessary. I wanted to build a lightweight private alternative for family and friends.

Users join using an invite code, submit predictions before kickoff, and are ranked on a leaderboard after results are entered. The organiser can manage groups, matches, results, users, and predictions through Django admin.

Technically, the project uses Django models for groups, memberships, matches, and predictions. Predictions are linked to a user, group, and match, and points are calculated based on the final result. I also added automated tests for the main workflow and deployed the app using Render and Neon PostgreSQL.

One issue I fixed during development was that prediction submission originally refreshed the page and moved the user away from the match they were voting on. I improved this using JavaScript fetch requests and JSON responses so predictions update smoothly without a full page reload.

The project demonstrates backend development, authentication, database modelling, testing, deployment, and privacy-aware design.

## GitHub Repository Description

Private football prediction competition web app built with Django, PostgreSQL, invite-code registration, prediction voting, automatic scoring, leaderboard ranking, automated tests, and Render/Neon deployment.

## Portfolio Card Text

**MatchPick**
A deployed Django web app for private football prediction competitions. Users join with an invite code, predict match outcomes, and compete on a leaderboard. Built with Django, PostgreSQL, JavaScript, Render, Neon, Gunicorn, and WhiteNoise.

## Skills Demonstrated

* Django web development
* Python backend development
* Database modelling
* User authentication
* Access control
* CSRF-protected forms
* JavaScript fetch requests
* PostgreSQL deployment
* Static file handling
* Automated testing
* Git and GitHub
* Render deployment
* Neon database setup
* Privacy-aware design
* Debugging production issues
* Technical documentation
