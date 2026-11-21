# KTK — English-brand-only update (V10)

This update replaces *displayed English* `Katika` and `KATIKA` with `KTK`.

**Preserved:** Persian `کاتیکا`, page structure, all user features, URLs, asset filenames and identifiers, site themes, language selector, pricing, SKU, `.env`, `.venv`, `db.sqlite3`, other database configurations, and `media/`.

Includes updated compiled translation catalogs for all three languages, the default header logo graphic, desktop and mobile splash branding, and an idempotent Django command for previously saved owner-authored English text. Does not edit user-uploaded imagery or images of real products; their preprinted lettering remains as photographed. This avoids altering photographs or customer data without instruction to retouch originals.

## Install on Windows

Extract this ZIP outside your existing KTK folder. In PowerShell in the extracted update folder:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\INSTALL-UPDATE.ps1 -ProjectPath "C:\Users\Tara\Desktop\KTK"
```

The installer creates a complete timestamped backup, copies only entries in `UPDATE-FILES.txt`, checks Django, updates English display brand words in the saved catalog settings, and runs `runserver`.

No database migrations are required. Stop the previous development server before installing. The new translations are already compiled; production deployments should also refresh staticfiles via collectstatic.
