# update_igm_bundle.ps1 - Install only modules from igm_bundle_modules.txt not yet in the database
# Run from workspace root: .\igm_tools\igm_bundle_of_standard_apps\update_igm_bundle.ps1
# No venv activation needed.

$WorkspaceRoot = (Get-Item $PSScriptRoot).Parent.Parent.FullName
$Python        = Join-Path $WorkspaceRoot ".venv\Scripts\python.exe"
$OdooBin       = Join-Path $WorkspaceRoot "odoo-bin"
$Conf          = Join-Path $WorkspaceRoot "odoo_local.conf"
$ModuleFile    = Join-Path $PSScriptRoot  "igm_bundle_modules.txt"

function Get-ConfValue($key) {
    $line = Select-String "^\s*$key\s*=\s*(.+)" $Conf | Select-Object -First 1
    if ($line) { return $line.Matches[0].Groups[1].Value.Trim() }
    return $null
}

$DbHost = Get-ConfValue 'db_host'
$DbPort = Get-ConfValue 'db_port'
$DbUser = Get-ConfValue 'db_user'
$DbPass = Get-ConfValue 'db_password'
$DbName = Get-ConfValue 'db_name'

$Modules = Get-Content $ModuleFile |
    Where-Object { $_ -notmatch '^\s*#' -and $_ -match '\S' } |
    ForEach-Object { ($_ -split '\s+')[0].Trim() } |
    Where-Object { $_ -ne '' }

$psqlCmd = Get-Command psql -ErrorAction SilentlyContinue
$psql = if ($psqlCmd) { $psqlCmd.Source } else { $null }
if (-not $psql) {
    $psql = Get-ChildItem "C:\Program Files\PostgreSQL" -Filter psql.exe -Recurse -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending | Select-Object -First 1 -ExpandProperty FullName
}
if (-not $psql) {
    Write-Host "psql not found. Add PostgreSQL bin to PATH or install PostgreSQL." -ForegroundColor Red
    exit 1
}

$env:PGPASSWORD = $DbPass
$Installed = & $psql -h $DbHost -p $DbPort -U $DbUser -d $DbName -t -A -c "SELECT name FROM ir_module_module WHERE state = 'installed';"
$env:PGPASSWORD = $null

if (-not $Installed) {
    Write-Host "Could not query the database. Is the DB initialised?" -ForegroundColor Red
    exit 1
}

$ToInstall = $Modules | Where-Object { $Installed -notcontains $_ }

Write-Host ""
Write-Host "Igm Bundle - Gap Installer" -ForegroundColor Cyan
Write-Host "-----------------------------" -ForegroundColor Cyan
Write-Host "Database  : $DbName"
Write-Host "Bundle    : $($Modules.Count) modules total"
Write-Host "Installed : $($Modules.Count - $ToInstall.Count)"
Write-Host "To install: $($ToInstall.Count)"
Write-Host ""

if ($ToInstall.Count -eq 0) {
    Write-Host "Nothing to do - all bundle modules are already installed." -ForegroundColor Green
    exit 0
}

Write-Host "Queued:" -ForegroundColor Yellow
$ToInstall | ForEach-Object { Write-Host "  - $_" }
Write-Host ""

$ModuleArg = $ToInstall -join ","

& $Python $OdooBin -c $Conf --init $ModuleArg --without-demo=all --stop-after-init

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Gap install completed successfully." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Install finished with errors (exit code $LASTEXITCODE)." -ForegroundColor Red
    Write-Host "Check the log above, fix the issue, then re-run." -ForegroundColor Yellow
}
