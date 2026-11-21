# KTK — Fullscreen brand intro V8 (patch for V7)

Changes only the homepage brand intro:

- Shows the supplied KATIKA splash artwork edge-to-edge with `object-fit: cover`.
- Disables the underlying page's scrollbars while the splash is visible.
- Holds the intro for exactly 3 seconds (including a 300ms fade-out).
- Restores scrolling when the splash disappears.
- Keeps the original once-per-tab behavior from V7.
- Keeps the mobile splash image and all multilingual/theme behavior untouched.

Install on the current project after V7. Extract the ZIP into a **separate** folder, open PowerShell inside it, then run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\INSTALL-UPDATE.ps1 -ProjectPath "C:\Users\Tara\Desktop\KTK"
```

The script creates a full backup and overwrites only `templates/base.html`, `static/css/katika-brand-intro.css` and `static/js/katika-brand-intro.js`. Existing `.env`, `.venv`, database and `media` remain intact. It runs `manage.py check` and starts `runserver` only when the check passes. No migration is necessary.

Because the splash is shown once per tab, open the site in a new tab to see it again, or run `sessionStorage.removeItem('ktk-brand-intro-seen')` in the browser console and refresh.
