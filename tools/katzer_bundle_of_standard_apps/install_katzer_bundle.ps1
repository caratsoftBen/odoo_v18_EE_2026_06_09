# Katzer Bundle — Install standard apps into the configured Odoo database
# Run from workspace root: .\tools\katzer_bundle_of_standard_apps\install_katzer_bundle.ps1
# No venv activation needed — script uses the venv Python directly.

$WorkspaceRoot = (Get-Item $PSScriptRoot).Parent.Parent.FullName
$Python        = Join-Path $WorkspaceRoot ".venv\Scripts\python.exe"
$OdooBin       = Join-Path $WorkspaceRoot "odoo-bin"
$Conf          = Join-Path $WorkspaceRoot "odoo_local.conf"
$ModuleFile    = Join-Path $PSScriptRoot  "katzer_bundle_modules.txt"

# Parse module list: skip comment lines (#) and blank lines, take first word of each line
$Modules = Get-Content $ModuleFile |
    Where-Object { $_ -notmatch '^\s*#' -and $_ -match '\S' } |
    ForEach-Object { ($_ -split '\s+')[0].Trim() } |
    Where-Object { $_ -ne '' }

$ModuleArg = $Modules -join ","

$DbLine = Select-String 'db_name\s*=' $Conf | Select-Object -First 1
Write-Host ""
Write-Host "Katzer Bundle Installer" -ForegroundColor Cyan
Write-Host "-----------------------" -ForegroundColor Cyan
Write-Host "Workspace : $WorkspaceRoot"
Write-Host "Config    : $Conf"
Write-Host "Database  : $($DbLine.Line.Trim())"
Write-Host "Modules   : $($Modules.Count) queued"
Write-Host ""
Write-Host "Starting Odoo --init. Expected duration: 10-20 minutes." -ForegroundColor Yellow
Write-Host ""

& $Python $OdooBin -c $Conf --init $ModuleArg --without-demo=all --stop-after-init

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Katzer Bundle installed successfully." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Install finished with errors (exit code $LASTEXITCODE)." -ForegroundColor Red
    Write-Host "Check the Odoo log above, fix the issue, then re-run." -ForegroundColor Yellow
    Write-Host "Already-installed modules are automatically skipped on re-run." -ForegroundColor Yellow
}
