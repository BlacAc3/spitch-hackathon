#!/bin/bash
echo "BUILD START"

# Ensure pip is installed and up to date
python3.9 -m ensurepip --upgrade

# Install requirements, use --no-cache-dir to avoid caching issues in vercel
python3.9 -m pip install --no-cache-dir -r requirements.txt

# Collect static files
python3.9 manage.py collectstatic --noinput --clear

echo "BUILD END"
