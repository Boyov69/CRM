#!/bin/bash
# setup_git.sh

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: CRM system with Supabase integration"

# Rename branch to main
git branch -M main

# Add remote
git remote add origin https://github.com/Boyov69/CRM.git

# Push (this might ask for credentials)
git push -u origin main
