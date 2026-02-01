#!/bin/bash
# GitHub Setup Script for TaloraV2

echo "==================================================================="
echo "TaloraV2 - GitHub Repository Setup"
echo "==================================================================="
echo ""

# Step 1: Create GitHub repository
echo "STEP 1: Create GitHub Repository"
echo "-------------------------------------------------------------------"
echo "Go to: https://github.com/new"
echo ""
echo "Repository settings:"
echo "  - Name: TaloraV2"
echo "  - Description: AI-Powered Job Matching Platform - 2000+ jobs/day"
echo "  - Visibility: PRIVATE"
echo "  - Do NOT initialize with README (we have one)"
echo ""
read -p "Press Enter after creating the repository on GitHub..."

# Step 2: Connect and push
echo ""
echo "STEP 2: Connect Local Repository to GitHub"
echo "-------------------------------------------------------------------"

REPO_URL="https://github.com/theravikumar/TaloraV2.git"

echo "Adding remote origin: $REPO_URL"
git remote add origin $REPO_URL

echo ""
echo "Pushing to GitHub..."
git push -u origin main

echo ""
echo "==================================================================="
echo "SUCCESS! Repository pushed to GitHub"
echo "==================================================================="
echo ""
echo "View your repository at:"
echo "https://github.com/theravikumar/TaloraV2"
echo ""
echo "NEXT STEPS:"
echo "1. Add team members: Settings → Collaborators → Add people"
echo "2. Set up GitHub Issues for task tracking"
echo "3. Share with teammates - they can clone with:"
echo "   git clone https://github.com/theravikumar/TaloraV2.git"
echo ""
