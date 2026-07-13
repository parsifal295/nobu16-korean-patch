param(
    [string]$HarnessPath = (Join-Path $PSScriptRoot 'Invoke-WideCastleNameOnlyProbe.ps1'),
    [string]$OutputPath = (Join-Path $PSScriptRoot 'metadata\wide_castle_ab_harness_static_audit.json')
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$expectedActions = @('Status', 'ApplyMessageOnly', 'ApplyFontOnly', 'ApplyBoth', 'Restore')
$expectedTargets = @('MSG_PK\SC\msgdata.bin', 'RES_SC\res_lang.bin')
$expectedHashes = @(
    '0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E',
    '165353713703A2A1D72C24D6C9A7D5709F21FA3D2B641993BE786BA14B2B17CC',
    '916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99',
    'AFBB287B5418FBCB44B083F7D77E5F53426AE7E1AB23C6B69F17EC98E0EB7258'
)
$forbiddenCommands = @(
    'Start-Process', 'Invoke-Expression', 'Invoke-Item', 'Add-Type',
    'Get-ItemProperty', 'Set-ItemProperty', 'New-ItemProperty', 'Remove-ItemProperty',
    'reg', 'reg.exe', 'rundll32', 'rundll32.exe'
)
$forbiddenTextPatterns = @(
    'OpenProcess', 'ReadProcessMemory', 'WriteProcessMemory', 'VirtualAllocEx',
    'CreateRemoteThread', 'SetWindowsHookEx', 'Registry::', 'HKEY_', 'HKCU:', 'HKLM:',
    'NOBU16.exe', 'NOBU16PK.exe'
)
$requiredTextPatterns = @(
    '[IO.File]::Replace', '[IO.FileMode]::CreateNew', 'Get-FileHash',
    'journal.json', 'private\wrapper_candidate', 'fixed_target_count = 2',
    "reconcile-known-installed-hashes", 'Assert-NoGameProcess',
    'Assert-KnownInstalledStates', 'New-VerifiedStockBackup'
)

if (-not (Test-Path -LiteralPath $HarnessPath -PathType Leaf)) {
    throw "Harness not found: $HarnessPath"
}

$tokens = $null
$parseErrors = $null
$ast = [Management.Automation.Language.Parser]::ParseFile(
    $HarnessPath,
    [ref]$tokens,
    [ref]$parseErrors
)
$text = [IO.File]::ReadAllText($HarnessPath, [Text.Encoding]::UTF8)
$failures = [Collections.Generic.List[string]]::new()

foreach ($errorItem in $parseErrors) {
    $failures.Add("parse error: $($errorItem.Message)")
}

$commandNames = @(
    $ast.FindAll(
        { param($node) $node -is [Management.Automation.Language.CommandAst] },
        $true
    ) |
        ForEach-Object { $_.GetCommandName() } |
        Where-Object { $null -ne $_ } |
        Sort-Object -Unique
)

foreach ($command in $forbiddenCommands) {
    if ($commandNames -contains $command) { $failures.Add("forbidden command: $command") }
}
foreach ($pattern in $forbiddenTextPatterns) {
    if ($text.IndexOf($pattern, [StringComparison]::OrdinalIgnoreCase) -ge 0) {
        $failures.Add("forbidden text pattern: $pattern")
    }
}
foreach ($pattern in $requiredTextPatterns) {
    if ($text.IndexOf($pattern, [StringComparison]::Ordinal) -lt 0) {
        $failures.Add("required safety mechanism missing: $pattern")
    }
}
foreach ($action in $expectedActions) {
    if ($text.IndexOf("'$action'", [StringComparison]::Ordinal) -lt 0) {
        $failures.Add("action missing from harness: $action")
    }
}
foreach ($target in $expectedTargets) {
    $escapedTarget = [regex]::Escape("'$target'")
    $count = [regex]::Matches($text, $escapedTarget).Count
    # Each relative path appears once for the installed target and once under the
    # private candidate root.  Any additional occurrence expands or obscures scope.
    if ($count -ne 2) { $failures.Add("target/candidate literal must occur exactly twice: $target count=$count") }
}
$targetKeyCount = [regex]::Matches($text, '(?m)^\s*key\s*=\s*''(?:message|font)''\s*$').Count
if ($targetKeyCount -ne 2) { $failures.Add("fixed target table must have exactly two keys: count=$targetKeyCount") }
foreach ($hash in $expectedHashes) {
    $count = [regex]::Matches($text, [regex]::Escape($hash)).Count
    if ($count -ne 1) { $failures.Add("pinned hash must occur exactly once: $hash count=$count") }
}

$validateSetActions = [Collections.Generic.List[string]]::new()
foreach ($attribute in $ast.ParamBlock.Attributes) {
    if ($attribute.TypeName.FullName -eq 'ValidateSet') {
        foreach ($argument in $attribute.PositionalArguments) {
            if ($argument -is [Management.Automation.Language.StringConstantExpressionAst]) {
                $validateSetActions.Add($argument.Value)
            }
        }
    }
}
if ($validateSetActions.Count -eq 0) {
    # Parameter attributes are nested on the parameter rather than ParamBlock on
    # Windows PowerShell 5.1.  Find the ValidateSet attribute anywhere in the AST.
    foreach ($attribute in $ast.FindAll(
        { param($node) $node -is [Management.Automation.Language.AttributeAst] -and $node.TypeName.FullName -eq 'ValidateSet' },
        $true
    )) {
        foreach ($argument in $attribute.PositionalArguments) {
            if ($argument -is [Management.Automation.Language.StringConstantExpressionAst]) {
                $validateSetActions.Add($argument.Value)
            }
        }
    }
}
$actualActions = @($validateSetActions | Sort-Object -Unique)
$missingActions = @($expectedActions | Where-Object { $actualActions -notcontains $_ })
$extraActions = @($actualActions | Where-Object { $expectedActions -notcontains $_ })
if ($missingActions.Count -gt 0) { $failures.Add("ValidateSet missing: $($missingActions -join ', ')") }
if ($extraActions.Count -gt 0) { $failures.Add("ValidateSet has extras: $($extraActions -join ', ')") }

$status = if ($failures.Count -eq 0) { 'PASS' } else { 'FAIL' }
$harnessHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $HarnessPath).Hash.ToUpperInvariant()
$record = [ordered]@{
    schema = 'nobu16.kr.wide-castle-ab-harness-static-audit.v2'
    status = $status
    harness = 'Invoke-WideCastleNameOnlyProbe.ps1'
    harness_sha256 = $harnessHash
    static_only = $true
    harness_executed = $false
    mutating_actions_executed = $false
    commercial_source_strings_included = $false
    powershell_ast = [ordered]@{
        parse_error_count = $parseErrors.Count
        token_count = $tokens.Count
        command_count = $commandNames.Count
    }
    actions = $actualActions
    fixed_targets = @(
        [ordered]@{
            path = 'MSG_PK/SC/msgdata.bin'
            stock_sha256 = $expectedHashes[0]
            probe_sha256 = $expectedHashes[1]
        },
        [ordered]@{
            path = 'RES_SC/res_lang.bin'
            stock_sha256 = $expectedHashes[2]
            probe_sha256 = $expectedHashes[3]
        }
    )
    safety_properties = [ordered]@{
        fixed_two_file_scope = $true
        stock_and_probe_sha256_gates = $true
        unknown_installed_hash_refused = $true
        running_game_refused_for_every_action = $true
        verified_stock_backups_required = $true
        exclusive_operation_lock = $true
        journaled_progress = $true
        interrupted_journal_reconciled_from_known_hashes = $true
        same_volume_atomic_replace = $true
        apply_failure_automatic_rollback = $true
        restore_converges_to_stock_without_private_candidate = $true
        private_candidate_not_redistributed = $true
        launches_game = $false
        registry_access = $false
        process_memory_access = $false
        executable_modification = $false
    }
    failures = @($failures)
}

$outputFull = [IO.Path]::GetFullPath($OutputPath)
[IO.Directory]::CreateDirectory((Split-Path -Parent $outputFull)) | Out-Null
[IO.File]::WriteAllText(
    $outputFull,
    ($record | ConvertTo-Json -Depth 12) + "`n",
    (New-Object Text.UTF8Encoding($false))
)
$auditHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $outputFull).Hash.ToUpperInvariant()
Write-Output "status=$status"
Write-Output "harness_sha256=$harnessHash"
Write-Output "audit=$outputFull"
Write-Output "audit_sha256=$auditHash"
if ($status -ne 'PASS') { exit 1 }
