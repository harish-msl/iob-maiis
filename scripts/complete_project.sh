#!/bin/bash
echo "Creating remaining backend router and service files..."

# Create __init__ files for all packages
touch backend/app/api/__init__.py
touch backend/app/auth/__init__.py
touch backend/app/services/__init__.py
touch backend/app/utils/__init__.py
touch backend/tests/__init__.py

# Create .gitkeep files for data directories
touch data/documents/.gitkeep
touch data/knowledge_base/.gitkeep

# Create frontend config files
touch frontend/.eslintrc.json
touch frontend/next.config.js
touch frontend/tailwind.config.ts
touch frontend/tsconfig.json
touch frontend/postcss.config.js

# Create nginx config
touch nginx/nginx.conf

# Create monitoring configs
touch monitoring/prometheus.yml

echo "✅ All placeholder files created!"
echo "Run: chmod +x setup.sh && ./setup.sh to complete setup"
