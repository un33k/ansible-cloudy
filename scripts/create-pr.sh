#!/bin/bash

# Create the pull request
gh pr create \
  --title "feat: Add production security hardening and fix vault variable names" \
  --body-file /tmp/pr-description.md \
  --base main \
  --head churn/ssh \
  --repo un33k/ansible-cloudy

# Alternative: Open PR creation page in browser
# gh pr create --web