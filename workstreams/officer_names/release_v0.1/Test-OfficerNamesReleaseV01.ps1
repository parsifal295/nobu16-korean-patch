[CmdletBinding()]
param([string]$EvidenceOutput)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ReleaseRoot = $PSScriptRoot
$KrPatchRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $ReleaseRoot))
$SharedGuard = Join-Path $KrPatchRoot 'workstreams\msgui_full\release_p4_vnext\template\tools\JsonKeyGuard.cs'
$AtomicModule = Join-Path $ReleaseRoot 'template\tools\AtomicFileSet.ps1'
$SafetyModule = Join-Path $ReleaseRoot 'template\tools\FileOnlySafety.ps1'
$BuildScript = Join-Path $ReleaseRoot 'Build-OfficerNamesReleaseV01.ps1'
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
if ([string]::IsNullOrWhiteSpace($EvidenceOutput)) {
    $EvidenceOutput = Join-Path $KrPatchRoot 'tmp\officer_names_release_v01_test_result.json'
}
$EvidenceOutput = [System.IO.Path]::GetFullPath($EvidenceOutput)

if (-not ('N16KrFileOnly.JsonKeyGuard' -as [type])) { Add-Type -Path $SharedGuard }
. $AtomicModule
. $SafetyModule

function Write-Bytes([string]$Path, [string]$Text) {
    [System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($Path)) | Out-Null
    [System.IO.File]::WriteAllBytes($Path, [Text.Encoding]::UTF8.GetBytes($Text))
}

function Get-Hash([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToUpperInvariant()
}

function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
}

function Assert-Throws([scriptblock]$Action, [string]$Label) {
    $threw = $false
    try { & $Action } catch { $threw = $true }
    if (-not $threw) { throw "$Label did not fail closed." }
}

function New-TestItems(
    [string[]]$Paths,
    [string[]]$BeforeHashes,
    [string[]]$AfterHashes,
    [string[]]$StagePaths
) {
    $ids = @('msgui', 'msgdata', 'msgev', 'font')
    $items = @()
    for ($index = 0; $index -lt 4; $index++) {
        $items += [pscustomobject]@{
            Id = $ids[$index]
            Destination = $Paths[$index]
            Staged = $StagePaths[$index]
            Rollback = Join-Path ([System.IO.Path]::GetDirectoryName($Paths[$index])) (
                '.' + [System.IO.Path]::GetFileName($Paths[$index]) + '.krpatch.rollback.' + [Guid]::NewGuid().ToString('N'))
            BeforeSha256 = $BeforeHashes[$index]
            AfterSha256 = $AfterHashes[$index]
        }
    }
    return @($items)
}

function New-Stages([string[]]$Paths, [string[]]$Texts, [string]$Tag) {
    $result = @()
    for ($index = 0; $index -lt 4; $index++) {
        $stage = Join-Path ([System.IO.Path]::GetDirectoryName($Paths[$index])) (
            '.' + [System.IO.Path]::GetFileName($Paths[$index]) + '.krpatch.' + $Tag + '.' + [Guid]::NewGuid().ToString('N'))
        Write-Bytes $stage $Texts[$index]
        $result += $stage
    }
    return @($result)
}

function Assert-Vector([string[]]$Paths, [string[]]$ExpectedHashes, [string]$Label) {
    for ($index = 0; $index -lt 4; $index++) {
        $actual = Get-Hash $Paths[$index]
        if ($actual -ne $ExpectedHashes[$index]) {
            throw "$Label mismatch at index ${index}: $actual, expected $($ExpectedHashes[$index])"
        }
    }
}

$tempParent = Join-Path $KrPatchRoot 'tmp\officer_names_release_v01_tests'
[System.IO.Directory]::CreateDirectory($tempParent) | Out-Null
$testRoot = Join-Path $tempParent ([Guid]::NewGuid().ToString('N'))
$fixture = Join-Path $testRoot 'game'
$journal = Join-Path $testRoot 'transaction.json'
$checks = [ordered]@{
    synthetic_fixture_only = $false
    apply_four_file_commit = $false
    restore_four_file_commit = $false
    apply_failure_rolls_back_all_four = $false
    restore_failure_rolls_back_all_four = $false
    failure_injection_boundaries_enforced = $false
    interrupted_partial_transaction_recovers = $false
    predecessor_composite_failure_restores_input = $false
    restore_known_mixed_vector_to_stock = $false
    arbitrary_hash_vector_rejected = $false
    font_artifact_pin_set_enforced = $false
    path_traversal_rejected = $false
    case_colliding_inventory_rejected = $false
    duplicate_json_key_rejected = $false
    reparse_point_rejected = $false
    nested_transaction_temporary_rejected = $false
    incomplete_inputs_fail_before_output = $false
    candidate_without_attestations_fails_before_output = $false
    production_installer_has_no_forbidden_access_calls = $false
}

try {
    $relativePaths = @(
        'MSG_PK\SC\msgui.bin',
        'MSG_PK\SC\msgdata.bin',
        'MSG_PK\SC\msgev.bin',
        'RES_SC\res_lang.bin'
    )
    [string[]]$paths = @($relativePaths | ForEach-Object { Join-Path $fixture $_ })
    [string[]]$stockTexts = @('stock-msgui-v1', 'stock-msgdata-v1', 'stock-msgev-v1', 'stock-font-v1')
    [string[]]$targetTexts = @('target-msgui-v1', 'target-msgdata-v1', 'target-msgev-v1', 'target-font-v1')
    for ($index = 0; $index -lt 4; $index++) { Write-Bytes $paths[$index] $stockTexts[$index] }
    [string[]]$stockHashes = @($paths | ForEach-Object { Get-Hash $_ })
    $targetHashFiles = New-Stages $paths $targetTexts 'hash'
    [string[]]$targetHashes = @($targetHashFiles | ForEach-Object { Get-Hash $_ })
    Remove-AtomicTemporary $targetHashFiles
    $checks.synthetic_fixture_only = $true

    $applyStages = New-Stages $paths $targetTexts 'apply'
    $applyItems = New-TestItems $paths $stockHashes $targetHashes $applyStages
    [void](Invoke-AtomicFileSetTransaction $applyItems $journal 'apply')
    Assert-Vector $paths $targetHashes 'apply commit'
    Remove-AtomicTemporary @($journal)
    $checks.apply_four_file_commit = $true

    $restoreStages = New-Stages $paths $stockTexts 'restore'
    $restoreItems = New-TestItems $paths $targetHashes $stockHashes $restoreStages
    [void](Invoke-AtomicFileSetTransaction $restoreItems $journal 'restore')
    Assert-Vector $paths $stockHashes 'restore commit'
    Remove-AtomicTemporary @($journal)
    $checks.restore_four_file_commit = $true

    foreach ($failureCount in 0..3) {
        $failedApplyStages = New-Stages $paths $targetTexts "failed-apply-$failureCount"
        $failedApplyItems = New-TestItems $paths $stockHashes $targetHashes $failedApplyStages
        Assert-Throws {
            Invoke-AtomicFileSetTransaction $failedApplyItems $journal 'apply' `
                -FailureAfterReplaceCount $failureCount
        } "injected apply after $failureCount"
        Assert-Vector $paths $stockHashes "failed apply rollback after $failureCount"
        Remove-AtomicTemporary @($journal)
    }
    $checks.apply_failure_rolls_back_all_four = $true

    $applyAgainStages = New-Stages $paths $targetTexts 'apply-again'
    $applyAgainItems = New-TestItems $paths $stockHashes $targetHashes $applyAgainStages
    [void](Invoke-AtomicFileSetTransaction $applyAgainItems $journal 'apply')
    Remove-AtomicTemporary @($journal)
    foreach ($failureCount in 0..3) {
        $failedRestoreStages = New-Stages $paths $stockTexts "failed-restore-$failureCount"
        $failedRestoreItems = New-TestItems $paths $targetHashes $stockHashes $failedRestoreStages
        Assert-Throws {
            Invoke-AtomicFileSetTransaction $failedRestoreItems $journal 'restore' `
                -FailureAfterReplaceCount $failureCount
        } "injected restore after $failureCount"
        Assert-Vector $paths $targetHashes "failed restore rollback after $failureCount"
        Remove-AtomicTemporary @($journal)
    }
    $checks.restore_failure_rolls_back_all_four = $true
    $rangeProbeStages = New-Stages $paths $stockTexts 'failure-range-probe'
    $rangeProbeItems = New-TestItems $paths $targetHashes $stockHashes $rangeProbeStages
    Assert-Throws {
        Invoke-AtomicFileSetTransaction $rangeProbeItems $journal 'restore' -FailureAfterReplaceCount 4
    } 'out-of-range failure injection count'
    Remove-AtomicTemporary $rangeProbeStages
    Remove-AtomicTemporary @($journal)
    $checks.failure_injection_boundaries_enforced = $true

    $recoveryStages = New-Stages $paths $stockTexts 'recovery-unused'
    $recoveryItems = New-TestItems $paths $targetHashes $stockHashes $recoveryStages
    $recoveryJournal = New-AtomicJournalValue $recoveryItems 'restore'
    for ($index = 0; $index -lt 2; $index++) {
        [System.IO.File]::Replace(
            [string]$recoveryItems[$index].Staged,
            [string]$recoveryItems[$index].Destination,
            [string]$recoveryItems[$index].Rollback,
            $true)
    }
    $recoveryJournal.status = 'replacing'
    $recoveryJournal.replaced_count = 2
    Write-AtomicJournal $journal $recoveryJournal
    [void](Recover-AtomicFileSetTransaction $recoveryJournal $recoveryItems $journal)
    Assert-Vector $paths $targetHashes 'interrupted restore recovery'
    Remove-AtomicTemporary @($journal)
    $checks.interrupted_partial_transaction_recovers = $true

    [string[]]$predecessorTexts = @('target-msgui-v1', 'probe-msgdata-v1', 'probe-msgev-v1', 'font-v4-v1')
    for ($index = 0; $index -lt 4; $index++) { Write-Bytes $paths[$index] $predecessorTexts[$index] }
    [string[]]$predecessorHashes = @($paths | ForEach-Object { Get-Hash $_ })
    $normalizeStages = New-Stages $paths $stockTexts 'normalize'
    $normalizeItems = New-TestItems $paths $predecessorHashes $stockHashes $normalizeStages
    [void](Invoke-AtomicFileSetTransaction $normalizeItems $journal 'normalize-stock')
    Remove-AtomicTemporary @($journal)
    $compositeApplyStages = New-Stages $paths $targetTexts 'composite-apply'
    $compositeApplyItems = New-TestItems $paths $stockHashes $targetHashes $compositeApplyStages
    Assert-Throws { Invoke-AtomicFileSetTransaction $compositeApplyItems $journal 'apply' -FailureAfterReplaceCount 2 } 'composite final apply'
    Assert-Vector $paths $stockHashes 'composite failed apply stock rollback'
    Remove-AtomicTemporary @($journal)
    $inputRollbackStages = New-Stages $paths $predecessorTexts 'input-rollback'
    $inputRollbackItems = New-TestItems $paths $stockHashes $predecessorHashes $inputRollbackStages
    [void](Invoke-AtomicFileSetTransaction $inputRollbackItems $journal 'rollback-input')
    Assert-Vector $paths $predecessorHashes 'composite input rollback'
    Remove-AtomicTemporary @($journal)
    $checks.predecessor_composite_failure_restores_input = $true

    $knownVectors = @(
        [pscustomobject]@{ id = 'stock'; hashes = @($stockHashes) },
        [pscustomobject]@{ id = 'final'; hashes = @($targetHashes) },
        [pscustomobject]@{ id = 'officer_probe_v0.1_on_msgui_full_font_v4'; hashes = @($predecessorHashes) }
    )
    $knownRestoreId = Assert-KnownHashVector $predecessorHashes $knownVectors 'synthetic restore input'
    Assert-True ($knownRestoreId -eq 'officer_probe_v0.1_on_msgui_full_font_v4') 'Known predecessor vector resolved to the wrong id.'
    $knownRestoreStages = New-Stages $paths $stockTexts 'known-restore'
    $knownRestoreItems = New-TestItems $paths $predecessorHashes $stockHashes $knownRestoreStages
    [void](Invoke-AtomicFileSetTransaction $knownRestoreItems $journal 'restore')
    Assert-Vector $paths $stockHashes 'known predecessor restore'
    Remove-AtomicTemporary @($journal)
    $checks.restore_known_mixed_vector_to_stock = $true

    [string[]]$arbitraryMixedHashes = @($stockHashes)
    $arbitraryMixedHashes[0] = $targetHashes[0]
    Assert-Throws {
        Assert-KnownHashVector $arbitraryMixedHashes $knownVectors 'synthetic arbitrary mixed vector'
    } 'arbitrary mixed hash vector'
    $checks.arbitrary_hash_vector_rejected = $true

    $fontArtifactRoot = Join-Path $testRoot 'font_artifacts'
    [string[]]$fontArtifactPaths = @(
        'licenses/OFL-NotoSansKR.txt',
        'licenses/OFL-NotoSerifKR.txt',
        'metrics/glyphs.jsonl',
        'payload/glyph_pixels_entry_6.pixels',
        'payload/glyph_pixels_entry_7.pixels'
    )
    $fontArtifactPins = @()
    for ($index = 0; $index -lt $fontArtifactPaths.Count; $index++) {
        $artifactPath = Join-Path $fontArtifactRoot ($fontArtifactPaths[$index].Replace('/', '\'))
        Write-Bytes $artifactPath "synthetic-font-artifact-$index"
        $fontArtifactPins += [pscustomobject]@{
            path = $fontArtifactPaths[$index]
            size = [int64](Get-Item -LiteralPath $artifactPath).Length
            sha256 = Get-Hash $artifactPath
        }
    }
    Assert-PinnedArtifactSet $fontArtifactPins $fontArtifactPaths $fontArtifactRoot 'synthetic font artifact pins'
    Assert-ExactOrdinaryFileSet $fontArtifactRoot $fontArtifactPaths 'synthetic font artifact tree'
    $extraFontArtifact = Join-Path $fontArtifactRoot 'payload\unreviewed.pixels'
    Write-Bytes $extraFontArtifact 'unreviewed-font-artifact'
    Assert-Throws {
        Assert-ExactOrdinaryFileSet $fontArtifactRoot $fontArtifactPaths 'synthetic font artifact tree with extra file'
    } 'unreviewed font artifact absorption'
    [System.IO.File]::Delete($extraFontArtifact)
    Write-Bytes (Join-Path $fontArtifactRoot 'metrics\glyphs.jsonl') 'tampered-metrics'
    Assert-Throws {
        Assert-PinnedArtifactSet $fontArtifactPins $fontArtifactPaths $fontArtifactRoot 'tampered synthetic font artifact pins'
    } 'tampered font artifact pin set'
    $checks.font_artifact_pin_set_enforced = $true

    Assert-Throws { Resolve-FileOnlyChild $fixture '../escape.bin' 'traversal probe' } 'path traversal'
    $checks.path_traversal_rejected = $true
    Assert-Throws { Assert-UniqueCanonicalPaths @('A/File.json', 'a/file.json') 'case probe' } 'case collision'
    $checks.case_colliding_inventory_rejected = $true

    $badJson = Join-Path $testRoot 'duplicate.json'
    [System.IO.File]::WriteAllText($badJson, '{"resource":1,"resource":2}', $Utf8NoBom)
    Assert-Throws { Read-StrictFileOnlyJson $badJson } 'duplicate JSON key'
    $checks.duplicate_json_key_rejected = $true

    $realDirectory = Join-Path $testRoot 'real_directory'
    $junction = Join-Path $testRoot 'junction_directory'
    [System.IO.Directory]::CreateDirectory($realDirectory) | Out-Null
    New-Item -ItemType Junction -Path $junction -Target $realDirectory | Out-Null
    Assert-Throws { Assert-OrdinaryExistingPath $junction 'junction probe' } 'reparse point'
    $checks.reparse_point_rejected = $true

    $nestedTemporaryParent = Join-Path ([System.IO.Path]::GetDirectoryName($paths[0])) 'nested_transaction_path'
    [System.IO.Directory]::CreateDirectory($nestedTemporaryParent) | Out-Null
    $nestedStage = Join-Path $nestedTemporaryParent (
        '.' + [System.IO.Path]::GetFileName($paths[0]) + '.krpatch.stage.' + [Guid]::NewGuid().ToString('N'))
    Write-Bytes $nestedStage $targetTexts[0]
    $nestedStages = New-Stages $paths $targetTexts 'nested-path-probe'
    $nestedStages[0] = $nestedStage
    $nestedItems = New-TestItems $paths $stockHashes $targetHashes $nestedStages
    Assert-Throws { Assert-AtomicItemSet $nestedItems } 'nested transaction temporary path'
    Remove-AtomicTemporary $nestedStages
    $checks.nested_transaction_temporary_rejected = $true

    $missingRoot = Join-Path $testRoot 'missing_inputs'
    $unexpectedOutput = Join-Path $KrPatchRoot 'releases\officer_names_v01_should_not_exist_test'
    if (Test-Path -LiteralPath $unexpectedOutput) {
        throw "Test output path unexpectedly exists before fail-closed test: $unexpectedOutput"
    }
    Assert-Throws {
        & $BuildScript -MsguiRecipe (Join-Path $missingRoot 'msgui.json') `
            -MsgdataRecipe (Join-Path $missingRoot 'msgdata.json') `
            -MsgevRecipe (Join-Path $missingRoot 'msgev.json') `
            -FontPublicRoot (Join-Path $missingRoot 'font') `
            -OutputRoot $unexpectedOutput
    } 'incomplete release inputs'
    Assert-True (-not (Test-Path -LiteralPath $unexpectedOutput)) 'Fail-closed build created an output directory.'
    $checks.incomplete_inputs_fail_before_output = $true

    $unexpectedCandidateOutput = Join-Path $KrPatchRoot 'releases\officer_names_v01_candidate_should_not_exist_test'
    if (Test-Path -LiteralPath $unexpectedCandidateOutput) {
        throw "Candidate test output path unexpectedly exists before fail-closed test: $unexpectedCandidateOutput"
    }
    Assert-Throws {
        & $BuildScript -Mode ReleaseCandidate `
            -CandidatePinsPath (Join-Path $missingRoot 'candidate_pins.json') `
            -RecipeE2EAttestation (Join-Path $missingRoot 'four_resource_recipe_e2e.json') `
            -RuntimeQaAttestation (Join-Path $missingRoot 'runtime_qa.json') `
            -OutputRoot $unexpectedCandidateOutput
    } 'release candidate without attestations'
    Assert-True (-not (Test-Path -LiteralPath $unexpectedCandidateOutput)) 'Attestation-less candidate build created an output directory.'
    $checks.candidate_without_attestations_fails_before_output = $true

    $productionText = [System.IO.File]::ReadAllText((Join-Path $ReleaseRoot 'template\tools\Invoke-OfficerNamesFileOnlyPatch.ps1'))
    foreach ($forbidden in @('Get-Process', 'Start-Process', 'OpenProcess(', 'ReadProcessMemory', 'WriteProcessMemory', 'Microsoft.Win32.Registry')) {
        if ($productionText.IndexOf($forbidden, [StringComparison]::OrdinalIgnoreCase) -ge 0) {
            throw "Production installer contains a forbidden access call: $forbidden"
        }
    }
    $checks.production_installer_has_no_forbidden_access_calls = $true

    $evidence = [ordered]@{
        schema = 'nobu16.officer-names-release-skeleton-test.v1'
        tested_utc = [DateTime]::UtcNow.ToString('o')
        fixture_root = $testRoot
        installed_game_accessed = $false
        checks = $checks
    }
    [System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($EvidenceOutput)) | Out-Null
    [System.IO.File]::WriteAllText($EvidenceOutput, (ConvertTo-Json $evidence -Depth 8) + "`n", $Utf8NoBom)
    Write-Host "Officer-name v0.1 release skeleton tests: OK"
    Write-Host "evidence=$EvidenceOutput"
}
finally {
    if (Test-Path -LiteralPath $testRoot -PathType Container) {
        $fullTestRoot = [System.IO.Path]::GetFullPath($testRoot)
        $safePrefix = [System.IO.Path]::GetFullPath($tempParent).TrimEnd('\') + '\'
        if ($fullTestRoot.StartsWith($safePrefix, [StringComparison]::OrdinalIgnoreCase)) {
            $testJunction = Join-Path $fullTestRoot 'junction_directory'
            if (Test-Path -LiteralPath $testJunction) {
                $junctionItem = Get-Item -LiteralPath $testJunction -Force
                if (($junctionItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                    Remove-Item -LiteralPath $testJunction -Force
                }
            }
            [System.IO.Directory]::Delete($fullTestRoot, $true)
        }
    }
    if ((Test-Path -LiteralPath $tempParent -PathType Container) -and
        @(Get-ChildItem -LiteralPath $tempParent -Force).Count -eq 0) {
        [System.IO.Directory]::Delete($tempParent, $false)
    }
}
