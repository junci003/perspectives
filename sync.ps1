# sync.ps1 - copy locally distilled skills into this repo
#
# Usage: run in repo root   .\sync.ps1
#  1. scans %USERPROFILE%\.workbuddy\skills\ for every *-perspective directory
#  2. adds the tool-type skills listed in $ExtraSkills (they do not match *-perspective)
#  3. copies them over this repo. Never deletes directories that exist here but not locally.
#
# NOTE: messages are ASCII on purpose. PowerShell 5.1 reads BOM-less .ps1 as ANSI,
# so non-ASCII string literals come out garbled on this machine.

$ErrorActionPreference = 'Stop'

# tool-type skills, listed by name (not *-perspective)
$ExtraSkills = @(
    'zh-humanizer',
    'ui-humanizer',
    'github-skill-teardown',
    'clawhub-publish',
    'codex-archive-to-obsidian',
    'openclaw-codex-reinstall'
)

$src = Join-Path $env:USERPROFILE '.workbuddy\skills'
$dst = $PSScriptRoot

if (-not (Test-Path $src)) {
    Write-Error "skills directory not found: $src"
    exit 1
}

$names = @()
$names += (Get-ChildItem $src -Directory -Filter '*-perspective').Name
$names += $ExtraSkills
$names = $names | Sort-Object -Unique

$count = 0
foreach ($name in $names) {
    $full = Join-Path $src $name
    if (-not (Test-Path $full)) {
        Write-Host "[skip] not on this machine: $name"
        continue
    }
    $target = Join-Path $dst $name
    New-Item -ItemType Directory -Force -Path $target | Out-Null
    Copy-Item (Join-Path $full '*') -Destination $target -Recurse -Force
    Write-Host "[ok]   $name"
    $count++
}

Write-Host ''
Write-Host "synced $count skill(s). next:"
Write-Host '  git add -A'
Write-Host '  git commit -m "sync skills"'
Write-Host '  git push'
