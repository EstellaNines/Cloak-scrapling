param(
    [string]$Python = "python",
    [switch]$NoIsolation,
    [switch]$Isolation,
    [switch]$SkipTwineCheck
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path

function Remove-ProjectPath {
    param([string]$RelativePath)

    $target = Join-Path $ProjectRoot $RelativePath
    if (-not (Test-Path -LiteralPath $target)) {
        return
    }

    $resolved = (Resolve-Path -LiteralPath $target).Path
    if (-not $resolved.StartsWith($ProjectRoot, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove outside project root: $resolved"
    }

    Remove-Item -LiteralPath $resolved -Recurse -Force
    Write-Host "[clean] removed $resolved" -ForegroundColor DarkGray
}

function Grant-BuildArtifactAccess {
    param([string]$Path)

    if ($env:OS -ne "Windows_NT") {
        return
    }

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    if (-not (Get-Command icacls -ErrorAction SilentlyContinue)) {
        return
    }

    try {
        $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
        & icacls $Path /grant "${currentUser}:M" /T /C | Out-Null
    }
    catch {
        Write-Warning "Could not update ACLs for ${Path}: $($_.Exception.Message)"
    }
}

Push-Location $ProjectRoot
try {
    Write-Host "[build] project: $ProjectRoot" -ForegroundColor Cyan

    if ($NoIsolation -and $Isolation) {
        throw "Use either -NoIsolation or -Isolation, not both."
    }

    Grant-BuildArtifactAccess -Path (Join-Path $ProjectRoot "dist")
    Remove-ProjectPath "build"
    Remove-ProjectPath "dist"
    Remove-ProjectPath "src\cloak_scrapling.egg-info"

    if ($Isolation) {
        Write-Host "[build] running: $Python -m build" -ForegroundColor Cyan
        & $Python -m build
    }
    else {
        Write-Host "[build] running: $Python -m build --no-isolation" -ForegroundColor Cyan
        & $Python -m build --no-isolation
    }

    if ($LASTEXITCODE -ne 0) {
        throw "build failed with exit code $LASTEXITCODE"
    }

    $dist = Join-Path $ProjectRoot "dist"
    Grant-BuildArtifactAccess -Path $dist

    if (-not $SkipTwineCheck) {
        Write-Host "[check] running: $Python -m twine check dist/*" -ForegroundColor Cyan
        $artifacts = @(Get-ChildItem -LiteralPath $dist -File | ForEach-Object { $_.FullName })
        & $Python -m twine check @artifacts
        if ($LASTEXITCODE -ne 0) {
            throw "twine check failed with exit code $LASTEXITCODE"
        }
    }

    Write-Host "[done] package artifacts:" -ForegroundColor Green
    Get-ChildItem -LiteralPath $dist -File | Select-Object Name, Length | Format-Table -AutoSize
}
finally {
    Pop-Location
}
