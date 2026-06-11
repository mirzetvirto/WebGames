#!/usr/bin/env bash
set -euo pipefail

# Usage: ./create_and_push.sh <github_repo_url>
# Example: ./create_and_push.sh https://github.com/tu-usuario/tu-repo.git

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <github_repo_url>"
  exit 1
fi

REPO_URL="$1"

# Ensure git is installed
if ! command -v git >/dev/null 2>&1; then
  echo "git not found. Please install git first." >&2
  exit 2
fi

# Initialize git repo if needed
if [ ! -d .git ]; then
  git init
  git add .
  git commit -m "Initial commit - Flask game launcher"
else
  echo "Git repo already initialized." 
fi

# Add remote and push
if git remote | grep -q '^origin$'; then
  echo "Remote 'origin' already exists. Updating URL." 
  git remote set-url origin "$REPO_URL"
else
  git remote add origin "$REPO_URL"
fi

# Create main branch and push
git branch -M main || true
git push -u origin main

echo "Pushed to $REPO_URL"
