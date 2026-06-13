# Stage 16 — README and Portfolio Documentation

## Goal

The goal of this stage was to improve the public presentation of the MatchPick project by adding GitHub and portfolio documentation.

## Actions Completed

* Created a professional `README.md`.
* Added project overview and purpose.
* Documented the main features.
* Documented the technology stack.
* Documented the security and privacy design choices.
* Added local setup instructions.
* Added testing instructions.
* Added deployment information.
* Added fixture import command notes.
* Added project status and future improvements.
* Created `docs/project_summary.md`.
* Checked that GitHub displays the project files correctly.
* Removed evidence screenshots from the public GitHub repository while keeping them locally.

## Design Decision

I added a detailed README because GitHub is often the first place someone will inspect the project. The README explains what the app does, how it works, how it was deployed, and what security/privacy decisions were made.

I also created a separate project summary document because it gives a cleaner portfolio-style explanation of the project without requiring someone to read the full source code.

Evidence screenshots were removed from GitHub because they are mainly useful for personal records and portfolio/report preparation, not for the public source code repository.

## Security and Privacy Notes

The README explains that production secrets are handled through environment variables and are not committed to GitHub.

The public repository should not contain `.env`, local SQLite database files, virtual environment files, collected static files, or real credentials.

The documentation also explains the data-minimisation design: Version 1 uses username, hashed password, group membership, and prediction data only.

## Evidence Captured

* `82_readme_added_to_github.png`
* `83_project_summary_document_created.png`
* `84_public_repo_cleaned_no_evidence_folder.png`

## Reflection

This stage improved the professional presentation of MatchPick. The project is now easier for others to understand from GitHub and is more suitable for use as a portfolio project.
