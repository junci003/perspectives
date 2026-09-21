# sync.ps1 — 把本机已蒸馏的视角同步进本仓库
#
# 用法：在本仓库根目录执行  .\sync.ps1
# 作用：扫描 %USERPROFILE%\.workbuddy\skills\ 下所有 *-perspective 目录，
#       覆盖复制到本仓库。不删除仓库里已存在但本机没有的视角。

$ErrorActionPreference = 'Stop'

$src = Join-Path $env:USERPROFILE '.workbuddy\skills'
$dst = $PSScriptRoot

if (-not (Test-Path $src)) {
    Write-Error "找不到 skills 目录：$src"
    exit 1
}

$skills = Get-ChildItem $src -Directory -Filter '*-perspective'
if (-not $skills) {
    Write-Host "没有找到任何 *-perspective 目录。"
    exit 0
}

foreach ($s in $skills) {
    $target = Join-Path $dst $s.Name
    New-Item -ItemType Directory -Force -Path $target | Out-Null
    Copy-Item (Join-Path $s.FullName '*') -Destination $target -Recurse -Force
    Write-Host "已同步：$($s.Name)"
}

Write-Host ''
Write-Host '完成。检查改动后提交：'
Write-Host '  git add -A'
Write-Host '  git commit -m "sync perspectives"'
Write-Host '  git push'
