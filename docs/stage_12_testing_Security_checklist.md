# Stage 12 — Testing and Security Checklist

## Purpose

This checklist records the manual and automated testing carried out for the MatchPick application.

The aim is to confirm that the main app workflow works correctly and that the most important security and privacy rules are being enforced.

---

## Automated Tests

Automated tests were added in:

`predictions/tests.py`

The test suite checks:

- Passwords are hashed and not stored as plaintext.
- Invalid invite codes are rejected.
- Valid invite codes create a user and group membership.
- Email is not required during registration.
- Logged-out users cannot access the matches page.
- Logged-out users cannot access the leaderboard page.
- Normal users do not see the admin link.
- Staff/admin users can see the admin link.
- Users can submit predictions before kickoff.
- Users can update predictions before kickoff.
- Users cannot vote after voting is locked.
- Users without a group cannot vote.
- Finished match results are calculated from scores.
- Correct predictions receive 3 points.
- Incorrect predictions receive 0 points.
- The leaderboard displays real group members and points.

Command used:

`python manage.py test predictions`

Expected result:

`OK`

---

## Manual Test 1 — Registration with Invalid Invite Code

### Steps

1. Open the registration page.
2. Enter a new username.
3. Enter a valid password.
4. Enter an invalid invite code.
5. Submit the form.

### Expected Result

The account should not be created.

The app should display an invite-code error.

### Result

Pass / Fail:

Notes:

---

## Manual Test 2 — Registration with Valid Invite Code

### Steps

1. Open the registration page.
2. Enter a new username.
3. Enter a valid password.
4. Enter the correct invite code.
5. Submit the form.

### Expected Result

The account should be created.

The user should be added to the matching competition group.

The user should be redirected to the matches page.

### Result

Pass / Fail:

Notes:

---

## Manual Test 3 — Login Required for Matches Page

### Steps

1. Log out.
2. Try opening `/matches/`.

### Expected Result

The app should redirect to the login page.

### Result

Pass / Fail:

Notes:

---

## Manual Test 4 — Login Required for Leaderboard Page

### Steps

1. Log out.
2. Try opening `/leaderboard/`.

### Expected Result

The app should redirect to the login page.

### Result

Pass / Fail:

Notes:

---

## Manual Test 5 — Prediction Submission Before Kickoff

### Steps

1. Log in as a normal user.
2. Open the matches page.
3. Find a scheduled match where voting is open.
4. Click a prediction option.

### Expected Result

The prediction should save successfully.

The selected prediction should be shown on the matches page.

The prediction should appear in the Django admin panel.

### Result

Pass / Fail:

Notes:

---

## Manual Test 6 — Prediction Update Before Kickoff

### Steps

1. Log in as a normal user.
2. Submit one prediction for a scheduled match.
3. Submit a different prediction for the same match.

### Expected Result

The prediction should update.

The app should not create duplicate prediction rows for the same user, group and match.

### Result

Pass / Fail:

Notes:

---

## Manual Test 7 — Voting Locked After Kickoff

### Steps

1. Use admin to set a match kickoff time in the past or set the match as finished.
2. Log in as a normal user.
3. Open the matches page.

### Expected Result

Prediction buttons should not appear for that match.

The page should show that voting is locked.

### Result

Pass / Fail:

Notes:

---

## Manual Test 8 — Result and Points Calculation

### Steps

1. Create or use a scheduled match.
2. Submit a prediction as a normal user.
3. Use admin to mark the match as finished.
4. Enter final scores.
5. Save the match.
6. Check the prediction and leaderboard.

### Expected Result

The match result should be calculated from the score.

A correct prediction should receive 3 points.

An incorrect prediction should receive 0 points.

The leaderboard should update.

### Result

Pass / Fail:

Notes:

---

## Manual Test 9 — Admin Link Visibility

### Steps

1. Log in as a normal user.
2. Check the navigation bar.
3. Log in as an admin/staff user.
4. Check the navigation bar again.

### Expected Result

Normal users should not see the admin link.

Admin/staff users should see the admin link.

### Result

Pass / Fail:

Notes:

---

## Manual Test 10 — Data Minimisation Check

### Data Collected in Version 1

- Username
- Hashed password
- Group membership
- Match predictions
- Points/results

### Data Not Collected in Version 1

- Email address
- Phone number
- Full legal name
- Date of birth
- Location
- Profile photo

### Expected Result

The registration process should only require username, password and invite code.

### Result

Pass / Fail:

Notes:

---

## Security Notes

- Passwords are handled using Django's built-in authentication system.
- Passwords are stored as hashes, not plaintext.
- CSRF protection is used on forms that change data.
- Prediction submission requires login.
- Matches and leaderboard pages require login.
- Normal users cannot access the Django admin panel.
- The app does not collect unnecessary personal data in Version 1.
- Invite codes restrict registration to known private groups.

---

## Limitations

- Version 1 uses the user's first competition group as the active group.
- Version 1 does not yet include a group switcher.
- Version 1 does not include live score updates.
- Version 1 relies on manual result correction if free imported data is incomplete or delayed.
- Version 1 does not include password reset because email addresses are not collected.

---

## Reflection

Testing confirmed that the core MatchPick workflow works: users can register with an invite code, log in, view matches, submit predictions and see leaderboard results.

The security checks confirmed that the app follows a data-minimisation approach and uses Django's built-in authentication features instead of handling passwords manually.
