# script_writer.ps1 - interactive request builder for ScriptEngine script writing
#
# Interactive: run without parameters, press the menu numbers to edit fields,
# Enter (or 'f') to fetch context from ScriptEngine and save the request.
#   powershell -ExecutionPolicy Bypass -File script_writer.ps1
#
# Headless (for the AI assistant or scripting): pass every field as a switch.
#   powershell -ExecutionPolicy Bypass -File script_writer.ps1 `
#     -Headless -Topic "Shibuya Incident" -Series jjk -Words 3000 -Intro $true
#
# Writes: scripts output/current_request.json (previous copy -> .prev.json)

[CmdletBinding()]
param(
    [switch]$Headless,
    [string]$Topic = "",
    [string]$Series = "",
    [string]$Question = "",
    [int]$Words = 0,
    # A string, not a [bool]. PowerShell's -File passes every argument as a
    # string, so the documented `-Intro $true` failed with "Cannot convert value
    # System.String to type System.Boolean" and the headless path could not be
    # run the way STARTME.md and README.md both describe.
    [string]$Intro = "true",
    [int]$Budget = 0,
    [ValidateSet("auto", "narrative", "roster", "qa")]
    [string]$Mode = "",
    [string]$BaseUrl = "http://127.0.0.1:8000"
)

$ErrorActionPreference = "Stop"
$ScriptDir = $PSScriptRoot
if (-not $ScriptDir) { $ScriptDir = (Get-Location).Path }
$OutDir = Join-Path $ScriptDir "scripts output"
$RequestFile = Join-Path $OutDir "current_request.json"
$PrevFile = Join-Path $OutDir "current_request.prev.json"

function New-DefaultSettings {
    @{
        topic        = "Shibuya Incident"
        series       = "jjk"
        question     = "Shibuya Incident"
        words        = 3000
        intro        = $true
        budget       = 24000
        # auto reads the topic: "Every Rank of Curse" is a set and comes back as
        # a roster, anything else comes back as a narrative.
        mode         = "auto"
        base_url     = "http://127.0.0.1:8000"
    }
}

function Get-AutoBudget([int]$words) {
    $b = $words * 8
    if ($b -lt 6000) { $b = 6000 }
    if ($b -gt 60000) { $b = 60000 }
    return $b
}

function Read-Value([string]$prompt, [string]$current) {
    $raw = Read-Host "$prompt [$current]"
    if ([string]::IsNullOrWhiteSpace($raw)) { return $current }
    return $raw.Trim()
}

function Read-Int([string]$prompt, [int]$current) {
    $raw = Read-Host "$prompt [$current]"
    if ([string]::IsNullOrWhiteSpace($raw)) { return $current }
    $n = 0
    if ([int]::TryParse($raw, [ref]$n)) { return $n }
    Write-Host "Not a number, keeping $current." -ForegroundColor Yellow
    return $current
}

function ConvertTo-Bool([string]$raw, [bool]$fallback) {
    if ([string]::IsNullOrWhiteSpace($raw)) { return $fallback }
    if ($raw -match "^(true|yes|y|1|on)$") { return $true }
    if ($raw -match "^(false|no|n|0|off)$") { return $false }
    return $fallback
}

function Read-YesNo([string]$prompt, [bool]$current) {
    $raw = Read-Host "$prompt [y/n, default $current]"
    if ([string]::IsNullOrWhiteSpace($raw)) { return $current }
    if ($raw -match "^(y|yes)$") { return $true }
    if ($raw -match "^(n|no)$") { return $false }
    Write-Host "Type y or n, keeping $current." -ForegroundColor Yellow
    return $current
}

function Show-Menu([hashtable]$s) {
    $introTxt = if ($s.intro) { "yes" } else { "no" }
    $budgetTxt = if ($s.budget -eq 0) { "auto" } else { "$($s.budget) tokens" }
    Write-Host ""
    Write-Host "=== ScriptEngine script request ===" -ForegroundColor Cyan
    Write-Host (" 1. Script topic     : {0}" -f $s.topic)
    Write-Host (" 2. Series           : {0}" -f $s.series)
    Write-Host (" 3. Question (query) : {0}" -f $s.question)
    Write-Host (" 4. Target length    : {0} words" -f $s.words)
    Write-Host (" 5. Intro            : {0}" -f $introTxt)
    Write-Host (" 6. Context budget   : {0}" -f $budgetTxt)
    Write-Host (" 7. Mode             : {0}" -f $s.mode)
    Write-Host (" 8. API              : {0}" -f $s.base_url)
    Write-Host "----------------------------------------" -ForegroundColor DarkGray
    Write-Host " f/Enter : fetch context & save request" -ForegroundColor Green
    Write-Host " l       : load previous request" -ForegroundColor Green
    Write-Host " q       : quit" -ForegroundColor Green
}

function Save-Request([hashtable]$s, $bundle) {
    if (-not (Test-Path -LiteralPath $OutDir)) {
        New-Item -ItemType Directory -Path $OutDir | Out-Null
    }
    if (Test-Path -LiteralPath $RequestFile) {
        Copy-Item -LiteralPath $RequestFile -Destination $PrevFile -Force
    }
    $record = @{
        topic         = $s.topic
        series        = $s.series
        question      = $s.question
        words         = $s.words
        intro         = $s.intro
        token_budget  = $s.budget
        base_url      = $s.base_url
        mode          = $s.mode
        resolved_mode = $bundle.mode
        subject       = $bundle.subject
        fetched_at    = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        tokens_used   = $bundle.tokens_used
        beats_count   = @($bundle.beats).Count
        members_count = @($bundle.members | Where-Object { $_ }).Count
        facts_count   = @($bundle.facts).Count
        prompt        = $bundle.prompt
        facts         = $bundle.facts
    }
    $json = $record | ConvertTo-Json -Depth 10
    # No byte-order mark. [System.Text.Encoding]::UTF8 emits one, and Python's
    # json.load() then fails on this file with "Unexpected UTF-8 BOM", which
    # broke every Python consumer of the request the writer works from.
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($RequestFile, $json, $utf8NoBom)
    return $json.Length
}

function Fetch-And-Save([hashtable]$s) {
    if ($s.budget -eq 0) { $s.budget = Get-AutoBudget $s.words }
    $payload = @{
        series       = $s.series
        query        = $s.question
        mode         = $s.mode
        token_budget = $s.budget
        top_k        = 12
        # The engine serves the house style, voice and annotation rules with the
        # context, and states the length and intro choice inside them.
        words        = $s.words
        intro        = $s.intro
        as_prompt    = $true
    } | ConvertTo-Json
    Write-Host ("Fetching /context for '{0}' ({1}, {2}, budget {3})..." -f $s.question, $s.series, $s.mode, $s.budget)
    try {
        $bundle = Invoke-RestMethod -Method Post -Uri ($s.base_url + "/context") `
            -ContentType "application/json" -Body $payload -TimeoutSec 300
    } catch {
        Write-Host "Could not reach ScriptEngine at $($s.base_url)." -ForegroundColor Red
        Write-Host "Start it with: python start_scriptengine.py  (repo root)" -ForegroundColor Yellow
        Write-Host ("  detail: " + $_.Exception.Message)
        return $false
    }
    $bytes = Save-Request $s $bundle
    Write-Host ("Saved {0} bytes to {1}" -f $bytes, $RequestFile) -ForegroundColor Green
    Write-Host ("mode: {0} | subject: {1}" -f $bundle.mode, $bundle.subject)
    Write-Host ("tokens_used: {0} | beats: {1} | members: {2} | facts: {3} | prompt chars: {4}" -f `
        $bundle.tokens_used, @($bundle.beats | Where-Object { $_ }).Count, `
        @($bundle.members | Where-Object { $_ }).Count, `
        @($bundle.facts | Where-Object { $_ }).Count, $bundle.prompt.Length)
    return $true
}

function Load-Previous([hashtable]$s) {
    if (-not (Test-Path -LiteralPath $RequestFile)) {
        Write-Host "No previous request file." -ForegroundColor Yellow
        return $s
    }
    $prev = Get-Content -LiteralPath $RequestFile -Raw | ConvertFrom-Json
    $s.topic    = $prev.topic
    $s.series   = $prev.series
    $s.question = $prev.question
    $s.words    = [int]$prev.words
    $s.intro    = [bool]$prev.intro
    $s.budget   = [int]$prev.token_budget
    if ($prev.mode)     { $s.mode = $prev.mode }
    if ($prev.base_url) { $s.base_url = $prev.base_url }
    Write-Host "Loaded previous request settings." -ForegroundColor Green
    return $s
}

# ---------------------------------------------------------------- headless
if ($Headless) {
    $s = New-DefaultSettings
    if ($Topic)    { $s.topic = $Topic }
    if ($Series)   { $s.series = $Series }
    if ($Question) { $s.question = $Question }
    else           { $s.question = $s.topic }
    if ($Words -gt 0) { $s.words = $Words }
    if ($Mode)        { $s.mode = $Mode }
    $s.intro = ConvertTo-Bool $Intro $true
    if ($Budget -gt 0) { $s.budget = $Budget }
    else            { $s.budget = Get-AutoBudget $s.words }
    if (-not $s.question) {
        Write-Host "Headless mode needs -Topic (or -Question)." -ForegroundColor Red
        exit 1
    }
    if (Fetch-And-Save $s) { exit 0 } else { exit 1 }
}

# -------------------------------------------------------------- interactive
$s = New-DefaultSettings
if (Test-Path -LiteralPath $RequestFile) {
    $s = Load-Previous $s
}
Write-Host "ScriptEngine script request builder. Press q to quit." -ForegroundColor Cyan

while ($true) {
    Show-Menu $s
    $key = [Console]::ReadKey($true).KeyChar
    switch ($key.ToString().ToLower()) {
        "1" { $s.topic = Read-Value "Script topic" $s.topic }
        "2" { $s.series = Read-Value "Series (jjk/db/csm)" $s.series }
        "3" { $s.question = Read-Value "Question (retrieval query)" $s.question }
        "4" { $s.words = Read-Int "Target length (words)" $s.words }
        "5" { $s.intro = Read-YesNo "Intro" $s.intro }
        "6" { $s.budget = Read-Int "Context budget (0 = auto from words)" $s.budget }
        "7" { $s.mode = Read-Value "Mode (auto/narrative/roster/qa)" $s.mode }
        "8" { $s.base_url = Read-Value "API base URL" $s.base_url }
        "f" { $null = Fetch-And-Save $s }
        "l" { $s = Load-Previous $s }
        "q" { Write-Host "Bye."; exit 0 }
        default {
            if ($key -eq [char]13) { $null = Fetch-And-Save $s }   # Enter
            elseif ($key -ne [char]0 -and -not [string]::IsNullOrWhiteSpace($key)) {
                Write-Host "Unknown key: $key" -ForegroundColor Yellow
            }
        }
    }
}
