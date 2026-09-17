# Run this after dropping this week's PDFs into reports/ (adding, removing,
# or overwriting any of them). One command does everything: regenerates
# index.html and PDF titles, then commits and pushes.
#
#   .\publish.ps1
#
# If nothing actually changed, the commit step is skipped automatically.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

python update_site.py

git add reports/ index.html

git diff --cached --quiet
$hasChanges = ($LASTEXITCODE -ne 0)
if ($hasChanges) {
    $message = "reports update " + (Get-Date -Format "yyyy-MM-dd")
    git commit -m $message
    git push
    Write-Host "`nPublished: $message"
} else {
    Write-Host "`nNo changes to publish."
}
