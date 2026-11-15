# Links this repository into Dota 2 as the custom game addon "legion_td".
# Creates directory junctions (no admin rights needed):
#   <Dota>\game\dota_addons\legion_td     -> <repo>\game\dota_addons\legion_td
#   <Dota>\content\dota_addons\legion_td  -> <repo>\content\dota_addons\legion_td
# Usage: double-click install.bat, or: powershell -File install.ps1 [-DotaPath "D:\...\dota 2 beta"]

param([string]$DotaPath = "")

$ErrorActionPreference = "Stop"
$AddonName = "legion_td"
$RepoRoot = Split-Path -Parent $PSScriptRoot

function Find-Dota {
    $candidates = @()
    foreach ($key in @("HKCU:\Software\Valve\Steam", "HKLM:\SOFTWARE\WOW6432Node\Valve\Steam")) {
        try {
            $p = Get-ItemProperty -Path $key -ErrorAction Stop
            foreach ($v in @($p.SteamPath, $p.InstallPath)) { if ($v) { $candidates += $v } }
        } catch {}
    }
    $libs = @()
    foreach ($steam in $candidates) {
        $steam = $steam -replace "/", "\"
        $libs += $steam
        $vdf = Join-Path $steam "steamapps\libraryfolders.vdf"
        if (Test-Path $vdf) {
            foreach ($m in [regex]::Matches((Get-Content $vdf -Raw), '"path"\s+"([^"]+)"')) {
                $libs += ($m.Groups[1].Value -replace "\\\\", "\")
            }
        }
    }
    $libs += "C:\Program Files (x86)\Steam"
    foreach ($lib in ($libs | Select-Object -Unique)) {
        $d = Join-Path $lib "steamapps\common\dota 2 beta"
        if (Test-Path (Join-Path $d "game\dota")) { return $d }
    }
    return $null
}

function Link-Folder([string]$Source, [string]$Target) {
    if (-not (Test-Path $Source)) { throw "Source folder not found: $Source" }
    $parent = Split-Path -Parent $Target
    if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent | Out-Null }

    if (Test-Path $Target) {
        $item = Get-Item $Target -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            # Old link: remove only the link, never the files it points to.
            cmd /c rmdir "$Target" | Out-Null
        } else {
            $backup = "$Target" + "_backup_" + (Get-Date -Format "yyyyMMdd_HHmmss")
            Write-Host "Real folder exists, moving it to $backup" -ForegroundColor Yellow
            Rename-Item -Path $Target -NewName (Split-Path -Leaf $backup)
        }
    }
    New-Item -ItemType Junction -Path $Target -Value $Source | Out-Null
    Write-Host "OK  $Target  ->  $Source" -ForegroundColor Green
}

if (-not $DotaPath) { $DotaPath = Find-Dota }
if (-not $DotaPath) {
    $DotaPath = Read-Host "Dota 2 not found. Paste the path to the 'dota 2 beta' folder"
}
if (-not (Test-Path (Join-Path $DotaPath "game\dota"))) {
    throw "This does not look like a Dota 2 folder: $DotaPath"
}
Write-Host "Dota 2: $DotaPath"
Write-Host "Repo:   $RepoRoot"

Link-Folder (Join-Path $RepoRoot "game\dota_addons\$AddonName")    (Join-Path $DotaPath "game\dota_addons\$AddonName")
Link-Folder (Join-Path $RepoRoot "content\dota_addons\$AddonName") (Join-Path $DotaPath "content\dota_addons\$AddonName")

Set-Content -Path (Join-Path $PSScriptRoot "dota_path.txt") -Value $DotaPath -Encoding ASCII
Write-Host ""
Write-Host "Done. Now run tools\launch.bat" -ForegroundColor Green
