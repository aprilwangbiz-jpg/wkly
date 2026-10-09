# Run this after making this week's dated folder in reports/ (e.g.
# reports/10.2.26/) and dropping the PDFs in it. One command does everything:
# regenerates index.html, PDF titles and date stamps, then commits and pushes.
#
#   .\publish.ps1
#
# If nothing changed, the commit is skipped, but it still pushes any earlier
# commit that didn't make it to GitHub (e.g. after a failed push).

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

python update_site.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nupdate_site.py failed (see message above) - nothing published." -ForegroundColor Red
    exit 1
}

git add reports/ index.html

git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    $message = "reports update " + (Get-Date -Format "yyyy-MM-dd")
    git commit -m $message
} else {
    Write-Host "`nNo new report changes to commit."
}

git push
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nPUSH FAILED - the website was NOT updated. Run .\publish.ps1 again." -ForegroundColor Red
    exit 1
}
Write-Host "`nPublished. The website updates within a few minutes (Ctrl+F5 to refresh)." -ForegroundColor Green
