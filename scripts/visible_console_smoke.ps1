$ErrorActionPreference = "Stop"

$env:CLOAK_SCRAPLING_CONSOLE = "1"
$env:CLOAK_SCRAPLING_CONSOLE_HOLD = "1"

Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    python scripts\cli_smoke.py
}
finally {
    Pop-Location
}
