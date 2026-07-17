param(
    [Parameter(Mandatory = $true)]
    [string]$GameRoot,

    [string]$CandidateRoot
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($CandidateRoot)) {
    $CandidateRoot = Join-Path $PSScriptRoot '..\..\tmp\wheel_system_goal_v1\current_direct_candidates_v5\candidate'
}
$GameRoot = (Resolve-Path -LiteralPath $GameRoot).Path
$CandidateRoot = (Resolve-Path -LiteralPath $CandidateRoot).Path

$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$items = @(
    [PSCustomObject]@{
        Target = Join-Path $GameRoot 'RES_JP\res_lang.bin'
        Candidate = Join-Path $CandidateRoot 'RES_JP\res_lang.bin'
        AllowedOldHashes = @(
            '2AD3B5612D88B0654BED1F3ED9CE5FEF214DABFE8FA312C7A2EBE16A27F7B17A',
            'D47FE86A8458A445A310D3CE28CF59A62608E6CA6854B1AB3313B3C6E3B9CE2B'
        )
        NewHash = '3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7'
    },
    [PSCustomObject]@{
        Target = Join-Path $GameRoot 'RES_JP_PK_PORT\res_lang_pk_port1.bin'
        Candidate = Join-Path $CandidateRoot 'RES_JP_PK_PORT\res_lang_pk_port1.bin'
        AllowedOldHashes = @(
            '8D9E8F7A8E5F0C5F1FA59909C53E9D5BAA9C963D08A2622DDBA60F86D89307D5',
            '18BAD9F1C9D033CD814C4E4DFE846EE01ED2746911DE977AE5F0516C4A460153'
        )
        NewHash = 'F65383C72291D08B71EBA7E2EF504A8C674E7C4678445045868D98FCA5B0730D'
    }
)

if (Get-Process -Name 'NOBU16PK' -ErrorAction SilentlyContinue) {
    throw 'NOBU16PK is still running'
}

foreach ($item in $items) {
    $candidateHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $item.Candidate).Hash
    if ($candidateHash -ne $item.NewHash) {
        throw "Candidate hash differs: $($item.Candidate) $candidateHash"
    }

    $old = (Get-FileHash -Algorithm SHA256 -LiteralPath $item.Target).Hash
    if ($old -eq $item.NewHash) {
        [PSCustomObject]@{
            Target = $item.Target
            LiveSHA256 = $old
            Status = 'already-current'
        } | ConvertTo-Json -Compress
        continue
    }
    if ($old -notin $item.AllowedOldHashes) {
        throw "Live precondition differs: $($item.Target) $old"
    }

    $backup = "$($item.Target).pre-full-system-buttons-$stamp.bak"
    $temp = "$($item.Target).codex-$stamp.tmp"
    if ((Test-Path -LiteralPath $backup) -or (Test-Path -LiteralPath $temp)) {
        throw 'Backup or temporary path already exists'
    }

    Copy-Item -LiteralPath $item.Candidate -Destination $temp
    $tempHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $temp).Hash
    if ($tempHash -ne $item.NewHash) {
        Remove-Item -LiteralPath $temp -Force
        throw "Staged hash differs: $tempHash"
    }

    [System.IO.File]::Replace($temp, $item.Target, $backup, $true)
    $liveHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $item.Target).Hash
    $backupHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $backup).Hash
    if (($liveHash -ne $item.NewHash) -or ($backupHash -ne $old)) {
        throw 'Post-replace verification failed'
    }

    [PSCustomObject]@{
        Target = $item.Target
        LiveSHA256 = $liveHash
        Backup = $backup
        BackupSHA256 = $backupHash
    } | ConvertTo-Json -Compress
}
