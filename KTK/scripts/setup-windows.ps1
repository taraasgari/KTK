$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
py -3.12 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe manage.py migrate
Write-Host 'Ready: .\.venv\Scripts\python.exe manage.py createsuperuser'
Write-Host 'Then:  .\.venv\Scripts\python.exe manage.py bootstrap_store --name KTK --owner YOUR_USERNAME'
Write-Host 'Then:  .\.venv\Scripts\python.exe manage.py runserver'
