#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -e .env ]; then cp .env.example .env; fi
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py migrate
printf '%s\n' 'Create an owner: .venv/bin/python manage.py createsuperuser' 'Bootstrap: .venv/bin/python manage.py bootstrap_store --name KTK --owner YOUR_USERNAME' 'Run: .venv/bin/python manage.py runserver'
