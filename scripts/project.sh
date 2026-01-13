#!/bin/bash

# Script to create FloatChat frontend project structure
# Usage: ./create_project.sh

set -e

echo "Creating FloatChat frontend project structure..."

# Create root directory
mkdir -p floatchat-frontend
cd floatchat-frontend

# Create directory structure
mkdir -p public
mkdir -p src/components
mkdir -p src/pages
mkdir -p src/styles

# Create empty files
touch public/.gitkeep

# Source files
touch src/components/FloatMap.jsx
touch src/components/ProfileViewer.jsx
touch src/components/ChatInterface.jsx
touch src/components/Sidebar.jsx
touch src/components/Header.jsx
touch src/components/FloatCard.jsx

touch src/pages/Dashboard.jsx
touch src/styles/index.css
touch src/App.jsx
touch src/main.jsx

# Configuration files
touch package.json
touch tailwind.config.js
touch vite.config.js
touch index.html

echo "Project structure created successfully!"
echo "Directory structure:"
find . -type f | sort