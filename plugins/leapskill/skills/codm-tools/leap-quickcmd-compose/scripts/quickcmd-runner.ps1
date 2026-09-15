#Requires -Version 7
[CmdletBinding(DefaultParameterSetName = 'Run')]
param(
    [Parameter(ParameterSetName = 'List', Mandatory)]
    [switch]$List,

    [Parameter(ParameterSetName = 'List')]
    [switch]$Json,

    [Parameter(ParameterSetName = 'Run', Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string[]]$Commands,

    [Parameter(ParameterSetName = 'Run')]
    [switch]$ContinueOnError,

    [string]$QuickCmdPath = 'H:\MyNote\Obsidian_data\assets\ps\QuickCmd.ps1'
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $QuickCmdPath -PathType Leaf)) {
    throw "QuickCmd source not found: $QuickCmdPath"
}

. $QuickCmdPath

if (-not $script:QuickCmdList) {
    throw "QuickCmd catalog is empty or unavailable after loading: $QuickCmdPath"
}

$catalog = @($script:QuickCmdList | ForEach-Object {
    $parts = $_ -split '\|', 2
    if ($parts.Count -ne 2) {
        throw "Invalid QuickCmd catalog entry: $_"
    }

    [PSCustomObject]@{
        Name = $parts[0].Trim()
        Cmd  = $parts[1].Trim()
    }
})

if ($List) {
    if ($Json) {
        $catalog | ConvertTo-Json -Depth 3
    } else {
        $catalog | Format-Table Name, Cmd -AutoSize
    }
    return
}

$available = @{}
foreach ($entry in $catalog) {
    $available[$entry.Cmd] = $entry
}

$unknown = @($Commands | Where-Object { -not $available.ContainsKey($_) })
if ($unknown.Count -gt 0) {
    throw "Commands are not present in the live QuickCmd catalog: $($unknown -join ', ')"
}

Write-Host "QuickCmd source: $QuickCmdPath" -ForegroundColor DarkGray
Write-Host "Invocation: $($Commands -join ' -> ')" -ForegroundColor Cyan

for ($index = 0; $index -lt $Commands.Count; $index++) {
    $commandName = $Commands[$index]
    $entry = $available[$commandName]
    Write-Host "[$($index + 1)/$($Commands.Count)] $($entry.Name) | $commandName" -ForegroundColor Yellow
    Write-Host ('-' * 60) -ForegroundColor DarkGray

    try {
        & $commandName
        if (-not $?) {
            throw "Command returned an unsuccessful status: $commandName"
        }
    } catch {
        Write-Error "QuickCmd failed: $commandName`n$_"
        if (-not $ContinueOnError) {
            exit 1
        }
    }
}
