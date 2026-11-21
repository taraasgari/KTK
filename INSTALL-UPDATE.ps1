param(
  [Parameter(Mandatory=$true)][string]$ProjectPath,
  [switch]$RunServer
)

$ErrorActionPreference = 'Stop'
$ProjectPath = [System.IO.Path]::GetFullPath($ProjectPath)
$packageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$imageSource = Join-Path $packageRoot 'KTK\static\images\ktk-hero-product-v13.webp'
$imageTarget = Join-Path $ProjectPath 'static\images\ktk-hero-product-v13.webp'
$cssPath = Join-Path $ProjectPath 'static\css\katika-storefront.css'
$templatePath = Join-Path $ProjectPath 'templates\base.html'
$manage = Join-Path $ProjectPath 'manage.py'

foreach ($path in @($imageSource, $cssPath, $templatePath, $manage)) {
  if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Required file missing: $path" }
}

$utf8 = New-Object System.Text.UTF8Encoding($false)
$css = [System.IO.File]::ReadAllText($cssPath)
$template = [System.IO.File]::ReadAllText($templatePath)
$oldImage = '../images/katika-hero-product.webp'
$newImage = '../images/ktk-hero-product-v13.webp?v=13'
$oldLink = 'href="{% static ''css/katika-storefront.css'' %}"'
$newLink = 'href="{% static ''css/katika-storefront.css'' %}?v=13"'

# Validate before making any changes. Keeping other files and user settings untouched.
if (-not $css.Contains($oldImage) -and -not $css.Contains($newImage)) {
  throw 'Could not locate the homepage default image reference in CSS. No files changed.'
}
if (-not $template.Contains($oldLink) -and -not $template.Contains($newLink)) {
  throw 'Could not locate the storefront CSS link in templates/base.html. No files changed.'
}

$backupRoot = Join-Path (Split-Path -Parent $ProjectPath) ('KTK-v13-changed-files-backup-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Force -Path (Join-Path $backupRoot 'static\css') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $backupRoot 'templates') | Out-Null
Copy-Item -LiteralPath $cssPath -Destination (Join-Path $backupRoot 'static\css\katika-storefront.css')
Copy-Item -LiteralPath $templatePath -Destination (Join-Path $backupRoot 'templates\base.html')

Copy-Item -LiteralPath $imageSource -Destination $imageTarget -Force
[System.IO.File]::WriteAllText($cssPath, $css.Replace($oldImage, $newImage), $utf8)
[System.IO.File]::WriteAllText($templatePath, $template.Replace($oldLink, $newLink), $utf8)

Write-Host "V13 installed. Backups of changed files: $backupRoot"
Write-Host 'Database, .env, .venv, media and original image have not been modified.'

$python = Join-Path $ProjectPath '.venv\Scripts\python.exe'
if (Test-Path -LiteralPath $python -PathType Leaf) {
  Push-Location $ProjectPath
  try {
    & $python manage.py check
    if ($LASTEXITCODE -ne 0) { throw "Django check failed with exit code $LASTEXITCODE" }
    Write-Host 'Django check passed.'
    if ($RunServer) { & $python manage.py runserver }
  }
  finally { Pop-Location }
}
else {
  Write-Warning 'No .venv\Scripts\python.exe found; Django check was not run. The image and CSS patch was installed.'
}
