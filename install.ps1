#
# Dataify Skills - Universal Installer (Windows PowerShell)
#
# Usage:
#   irm https://raw.githubusercontent.com/dataify-server/skills/main/install.ps1 | iex
#   .\install.ps1
#   .\install.ps1 -Target claude-code
#   .\install.ps1 -Target codex
#   .\install.ps1 -Target openclaw
#   .\install.ps1 -Target all
#   .\install.ps1 -Target claude-code -Skills "serp-google-search,scraper-amazon-product"
#   .\install.ps1 -Token YOUR_TOKEN
#   .\install.ps1 -Uninstall -Target claude-code
#

param(
    [string]$Target = "",
    [string]$Skills = "",
    [string]$Token = "",
    [switch]$Uninstall,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

# ── Config ──
$RepoUrl = "https://github.com/dataify-server/skills.git"
$InstallDir = if ($env:DATAIFY_SKILLS_DIR) { $env:DATAIFY_SKILLS_DIR } else { "$env:USERPROFILE\.dataify\skills" }
$DashboardUrl = "https://dashboard.dataify.com?utm_source=installer"
$SkillPrefix = "dataify-"

# ── Helpers ──
function Write-Info    { param([string]$Msg) Write-Host "[INFO] $Msg" -ForegroundColor Blue }
function Write-Ok      { param([string]$Msg) Write-Host "[OK] $Msg" -ForegroundColor Green }
function Write-Warn    { param([string]$Msg) Write-Host "[WARN] $Msg" -ForegroundColor Yellow }
function Write-Err     { param([string]$Msg) Write-Host "[ERROR] $Msg" -ForegroundColor Red; exit 1 }

if ($Help) {
    Write-Host @"
Usage: .\install.ps1 [OPTIONS]

Options:
  -Target TARGET      Target tool: claude-code, codex, openclaw, all (default: auto-detect)
  -Skills SKILLS      Comma-separated skill names to install (default: all)
  -Token TOKEN        Dataify API token (optional, can set later)
  -Uninstall          Remove installed skills from target tool
  -Help               Show this help message

Examples:
  .\install.ps1                                    # Interactive, auto-detect tools
  .\install.ps1 -Target claude-code                # Install to Claude Code only
  .\install.ps1 -Target all                        # Install to all detected tools
  .\install.ps1 -Uninstall -Target claude-code     # Remove from Claude Code
"@
    exit 0
}

# ── Banner ──
Write-Host ""
Write-Host "+===========================================+" -ForegroundColor Blue
Write-Host "|      Dataify Skills Installer              |" -ForegroundColor Blue
Write-Host "|  63+ Skills . 3 Tools . Cross-Platform     |" -ForegroundColor Blue
Write-Host "+===========================================+" -ForegroundColor Blue
Write-Host ""

# ── Tool paths ──
function Get-ClaudeCodeSkillsDir { return "$env:USERPROFILE\.claude\skills" }
function Get-OpenClawSkillsDir   { return "$env:USERPROFILE\.openclaw\skills" }
function Get-CodexDir            { return "$env:USERPROFILE\.codex" }

# ── Detect tools ──
function Get-DetectedTools {
    $found = @()
    if ((Get-Command "claude" -ErrorAction SilentlyContinue) -or (Test-Path "$env:USERPROFILE\.claude")) {
        $found += "claude-code"
    }
    if ((Get-Command "codex" -ErrorAction SilentlyContinue) -or (Test-Path "$env:USERPROFILE\.codex")) {
        $found += "codex"
    }
    if ((Get-Command "openclaw" -ErrorAction SilentlyContinue) -or (Test-Path "$env:USERPROFILE\.openclaw")) {
        $found += "openclaw"
    }
    return $found
}

# ── Get skill directories ──
function Get-SkillDirs {
    $skillsRoot = "$InstallDir\skills"
    if ($Skills -ne "") {
        $names = $Skills -split "," | ForEach-Object { $_.Trim() }
        foreach ($name in $names) {
            $dir = "$skillsRoot\$name"
            if ((Test-Path $dir) -and (Test-Path "$dir\SKILL.md")) {
                $dir
            } else {
                Write-Warn "Skill not found: $name"
            }
        }
    } else {
        Get-ChildItem -Path $skillsRoot -Recurse -Filter "SKILL.md" -Depth 2 -ErrorAction SilentlyContinue |
            ForEach-Object { $_.Directory.FullName }
    }
}

# ── Uninstall functions ──
function Uninstall-Symlinks {
    param([string]$ToolName, [string]$TargetDir)
    $count = 0
    if (Test-Path $TargetDir) {
        Get-ChildItem -Path $TargetDir -Filter "${SkillPrefix}*" -ErrorAction SilentlyContinue | Where-Object {
            $_.Attributes -band [System.IO.FileAttributes]::ReparsePoint
        } | ForEach-Object {
            Remove-Item $_.FullName -Force
            $count++
        }
    }
    Write-Ok "${ToolName}: removed $count skills from $TargetDir"
}

function Uninstall-Codex {
    $agentsFile = "$(Get-CodexDir)\AGENTS.md"
    if (Test-Path $agentsFile) {
        $content = Get-Content $agentsFile -Raw
        if ($content -match "<!-- DATAIFY_SKILLS_START -->") {
            $content = $content -replace "(?s)<!-- DATAIFY_SKILLS_START -->.*?<!-- DATAIFY_SKILLS_END -->\r?\n?", ""
            if ($content.Trim() -eq "") {
                Remove-Item $agentsFile -Force
            } else {
                Set-Content -Path $agentsFile -Value $content -NoNewline
            }
            Write-Ok "Codex: removed Dataify section from $agentsFile"
        } else {
            Write-Info "Codex: no Dataify section found in $agentsFile"
        }
    } else {
        Write-Info "Codex: no AGENTS.md found"
    }
}

if ($Uninstall) {
    if ($Target -eq "") { Write-Err "Please specify -Target for uninstall (claude-code, codex, openclaw, all)" }
    switch ($Target) {
        "claude-code" { Uninstall-Symlinks "Claude Code" (Get-ClaudeCodeSkillsDir) }
        "codex"       { Uninstall-Codex }
        "openclaw"    { Uninstall-Symlinks "OpenClaw" (Get-OpenClawSkillsDir) }
        "all" {
            Uninstall-Symlinks "Claude Code" (Get-ClaudeCodeSkillsDir)
            Uninstall-Codex
            Uninstall-Symlinks "OpenClaw" (Get-OpenClawSkillsDir)
        }
        default { Write-Err "Unknown target: $Target" }
    }
    Write-Host ""
    Write-Ok "Uninstall complete."
    exit 0
}

# ── Phase 1: Clone or update ──
Write-Info "Phase 1: Downloading skills..."

if (-not (Get-Command "git" -ErrorAction SilentlyContinue)) {
    Write-Err "git is not installed. Please install git first."
}

if (Test-Path "$InstallDir\.git") {
    Write-Info "Existing installation found, updating..."
    Push-Location $InstallDir
    try {
        git pull --ff-only origin main 2>$null
        Write-Ok "Updated successfully"
    } catch {
        Write-Warn "Could not auto-update. Using existing version."
    }
    Pop-Location
} else {
    Write-Info "Cloning to $InstallDir ..."
    $parentDir = Split-Path $InstallDir -Parent
    if (-not (Test-Path $parentDir)) { New-Item -ItemType Directory -Path $parentDir -Force | Out-Null }
    git clone $RepoUrl $InstallDir 2>$null
    if ($LASTEXITCODE -ne 0) { Write-Err "Failed to clone repository. Check your network connection." }
    Write-Ok "Cloned successfully"
}

$SkillCount = (Get-ChildItem -Path "$InstallDir\skills" -Recurse -Filter "SKILL.md" -Depth 2 -ErrorAction SilentlyContinue).Count
Write-Ok "Found $SkillCount skills"
Write-Host ""

# ── Phase 2: Install ──
Write-Info "Phase 2: Installing skills to tools..."

function Install-Symlinks {
    param([string]$ToolName, [string]$TargetDir)
    $count = 0
    if (-not (Test-Path $TargetDir)) { New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null }

    foreach ($skillDir in (Get-SkillDirs)) {
        $skillName = Split-Path $skillDir -Leaf
        # Avoid double prefix (e.g., dataify-dataify-web-unlocker)
        $linkName = if ($skillName.StartsWith($SkillPrefix)) { $skillName } else { "${SkillPrefix}${skillName}" }
        $linkPath = "$TargetDir\$linkName"

        # Remove existing junction/symlink
        if (Test-Path $linkPath) {
            $item = Get-Item $linkPath -Force
            if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
                Remove-Item $linkPath -Force
            } else {
                Write-Warn "${ToolName}: $linkName already exists (not a symlink), skipping"
                continue
            }
        }

        # Create directory junction (works without admin on Windows)
        cmd /c mklink /J "$linkPath" "$skillDir" >$null 2>&1
        if ($LASTEXITCODE -eq 0) {
            $count++
        } else {
            # Fallback: try symbolic link (requires admin or developer mode)
            try {
                New-Item -ItemType SymbolicLink -Path $linkPath -Target $skillDir -ErrorAction Stop | Out-Null
                $count++
            } catch {
                Write-Warn "${ToolName}: failed to link $skillName (try running as Administrator)"
            }
        }
    }
    Write-Ok "${ToolName}: $count skills linked -> $TargetDir"
}

function Install-Codex {
    $codexDir = Get-CodexDir
    $agentsFile = "$codexDir\AGENTS.md"

    if (-not (Test-Path $codexDir)) { New-Item -ItemType Directory -Path $codexDir -Force | Out-Null }

    $lines = @()
    $lines += "<!-- DATAIFY_SKILLS_START -->"
    $lines += "# Dataify Skills"
    $lines += ""
    $lines += "You have access to Dataify data collection skills for web scraping, search, and structured data extraction."
    $lines += ""
    $lines += "**Setup:** Set ``DATAIFY_API_TOKEN`` environment variable before using any skill."
    $lines += "Get your token at: https://dashboard.dataify.com"
    $lines += ""
    $lines += "## Available Skills"
    $lines += ""
    $lines += "| Skill | Description | Script |"
    $lines += "|-------|-------------|--------|"

    foreach ($skillDir in (Get-SkillDirs)) {
        $skillName = Split-Path $skillDir -Leaf
        $description = $skillName

        # Extract description from SKILL.md frontmatter (handles BOM and quoted values)
        $skillMd = "$skillDir\SKILL.md"
        if (Test-Path $skillMd) {
            $content = Get-Content $skillMd -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
            if ($content -match '(?m)^\s*description:\s*"?(.+?)"?\s*$') {
                $description = $Matches[1].Trim().Trim('"')
                if ($description.Length -gt 80) { $description = $description.Substring(0, 77) + "..." }
            }
        }

        # Find main script
        $mainScript = ""
        $scriptsDir = "$skillDir\scripts"
        if (Test-Path $scriptsDir) {
            $scripts = Get-ChildItem -Path $scriptsDir -Filter "*.py" -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -ne "preview_params.py" }
            if ($scripts) {
                $mainScript = $scripts[0].FullName
            } else {
                $fallback = Get-ChildItem -Path $scriptsDir -Filter "*.py" -ErrorAction SilentlyContinue
                if ($fallback) { $mainScript = $fallback[0].FullName }
            }
        }

        if ($mainScript) {
            $lines += "| $skillName | $description | ``python3 $mainScript`` |"
        } else {
            $lines += "| $skillName | $description | See SKILL.md |"
        }
    }

    $lines += ""
    $lines += "## Usage"
    $lines += ""
    $lines += "For detailed instructions on any skill, read its SKILL.md:"
    $lines += '```'
    $lines += "cat $InstallDir\skills\<skill-name>\SKILL.md"
    $lines += '```'
    $lines += "<!-- DATAIFY_SKILLS_END -->"

    $newContent = $lines -join "`n"

    if (Test-Path $agentsFile) {
        $existing = Get-Content $agentsFile -Raw
        if ($existing -match "<!-- DATAIFY_SKILLS_START -->") {
            $existing = $existing -replace "(?s)<!-- DATAIFY_SKILLS_START -->.*?<!-- DATAIFY_SKILLS_END -->", ""
        }
        $finalContent = $existing.TrimEnd() + "`n`n" + $newContent + "`n"
        Set-Content -Path $agentsFile -Value $finalContent -NoNewline
        Write-Ok "Codex: updated $agentsFile"
    } else {
        Set-Content -Path $agentsFile -Value ($newContent + "`n") -NoNewline
        Write-Ok "Codex: created $agentsFile"
    }
}

# ── Target selection ──
function Run-Install {
    param([string[]]$Targets)
    foreach ($t in $Targets) {
        switch ($t) {
            "claude-code" { Install-Symlinks "Claude Code" (Get-ClaudeCodeSkillsDir) }
            "codex"       { Install-Codex }
            "openclaw"    { Install-Symlinks "OpenClaw" (Get-OpenClawSkillsDir) }
            default       { Write-Warn "Unknown target: $t" }
        }
    }
}

if ($Target -ne "") {
    if ($Target -eq "all") {
        Run-Install @("claude-code", "codex", "openclaw")
    } else {
        Run-Install @($Target)
    }
} else {
    $detected = Get-DetectedTools

    if ($detected.Count -eq 0) {
        Write-Host "  No tools auto-detected. Select target:" -ForegroundColor White
        Write-Host ""
        Write-Host "  1) Claude Code" -ForegroundColor Cyan
        Write-Host "  2) Codex (OpenAI)" -ForegroundColor Cyan
        Write-Host "  3) OpenClaw" -ForegroundColor Cyan
        Write-Host "  4) All" -ForegroundColor Cyan
        Write-Host ""
        $choice = Read-Host "  Choose [1-4]"
        switch ($choice) {
            "1" { Run-Install @("claude-code") }
            "2" { Run-Install @("codex") }
            "3" { Run-Install @("openclaw") }
            "4" { Run-Install @("claude-code", "codex", "openclaw") }
            default { Run-Install @("claude-code", "codex", "openclaw") }
        }
    } else {
        Write-Host "  Detected tools:"
        foreach ($t in $detected) {
            Write-Host "    + $t" -ForegroundColor Green
        }
        Write-Host ""
        $confirm = Read-Host "  Install to all detected tools? [Y/n]"
        if ($confirm -eq "n" -or $confirm -eq "N") {
            Write-Host ""
            Write-Host "  1) Claude Code" -ForegroundColor Cyan
            Write-Host "  2) Codex (OpenAI)" -ForegroundColor Cyan
            Write-Host "  3) OpenClaw" -ForegroundColor Cyan
            Write-Host "  4) All" -ForegroundColor Cyan
            Write-Host ""
            $choice = Read-Host "  Choose [1-4]"
            switch ($choice) {
                "1" { Run-Install @("claude-code") }
                "2" { Run-Install @("codex") }
                "3" { Run-Install @("openclaw") }
                "4" { Run-Install @("claude-code", "codex", "openclaw") }
                default { Run-Install $detected }
            }
        } else {
            Run-Install $detected
        }
    }
}

# ── Save token if provided ──
if ($Token -ne "") {
    [System.Environment]::SetEnvironmentVariable("DATAIFY_API_TOKEN", $Token, "User")
    Write-Ok "Token saved to user environment variables"
}

# Set DATAIFY_SKILLS_DIR
$existingDir = [System.Environment]::GetEnvironmentVariable("DATAIFY_SKILLS_DIR", "User")
if (-not $existingDir) {
    [System.Environment]::SetEnvironmentVariable("DATAIFY_SKILLS_DIR", $InstallDir, "User")
}

# ── Phase 3: Done ──
Write-Host ""
Write-Host "+===========================================+" -ForegroundColor Green
Write-Host "|       Installation Complete!               |" -ForegroundColor Green
Write-Host "+===========================================+" -ForegroundColor Green
Write-Host ""
Write-Host "  Skills directory: $InstallDir" -ForegroundColor Blue
Write-Host "  Total skills:     $SkillCount" -ForegroundColor Blue
Write-Host ""
Write-Host "  Usage:" -ForegroundColor White
Write-Host "    Claude Code  /dataify-serp-google-search" -ForegroundColor Cyan
Write-Host "    OpenClaw     /dataify-serp-google-search" -ForegroundColor Cyan
Write-Host "    Codex        Skills auto-loaded from ~/.codex/AGENTS.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "  To use skills, set your API token:" -ForegroundColor White
Write-Host "    `$env:DATAIFY_API_TOKEN = 'your-token'" -ForegroundColor Yellow
Write-Host "    Get one at: $DashboardUrl" -ForegroundColor Blue
Write-Host ""
Write-Host "  Other commands:" -ForegroundColor White
Write-Host "    Update:    .\install.ps1" -ForegroundColor Cyan
Write-Host "    Uninstall: .\install.ps1 -Uninstall -Target all" -ForegroundColor Cyan
Write-Host "    MCP setup: bash setup-mcp.sh" -ForegroundColor Cyan
Write-Host ""
