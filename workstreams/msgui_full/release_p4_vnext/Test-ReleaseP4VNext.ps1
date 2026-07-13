[CmdletBinding()]
param(
    [string]$PackageRoot,
    [string]$EvidenceOutput
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$KrPatchRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$GameRoot = Split-Path -Parent $KrPatchRoot
if (-not $PackageRoot) {
    $PackageRoot = Join-Path $KrPatchRoot 'releases\msgui_p4_file_only_v0.3-dev_2026-07-13'
}
if (-not $EvidenceOutput) {
    $EvidenceOutput = Join-Path $KrPatchRoot 'reports\release_p4_vnext_offline_validation_2026-07-13.json'
}
$PackageRoot = [IO.Path]::GetFullPath($PackageRoot)
$EvidenceOutput = [IO.Path]::GetFullPath($EvidenceOutput)
$Installer = Join-Path $PackageRoot 'tools\Invoke-FileOnlyPatch.ps1'
$StockMessage = Join-Path $GameRoot 'MSG_PK\SC\msgui.bin'
$StockFont = Join-Path $GameRoot 'RES_SC\res_lang.bin'
$TargetMessageSource = Join-Path $KrPatchRoot 'workstreams\msgui_full\build_p4_0401_1100\private\message_recipe_repro\recipe_rebuilt_1.msgui.bin'
$TargetFontSource = Join-Path $KrPatchRoot 'workstreams\msgui_full\font_v4\build\private\candidate\res_lang.SC.font-v4.bin'
$PowerShellExe = 'C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe'

$StockMessageHash = 'C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82'
$TargetMessageHash = '5E4B26FC465F4F0F4C046462714E7B677D7B479FDA6023086EF7F9A8817E6984'
$TargetMessageSize = 87274L
$StockFontHash = '916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99'
$TargetFontHash = '3BC57379D9AF95E83A77C96C1EE2D104AAF4A8BEA1733EA33FC3D1BCF056D1A9'
$TargetFontSize = 180350761L

function Get-Sha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToUpperInvariant()
}

function Assert-Hash([string]$Path, [string]$Expected, [string]$Label) {
    $actual = Get-Sha256 $Path
    if ($actual -ne $Expected) {
        throw "$Label hash mismatch: $actual"
    }
}

function Assert-Size([string]$Path, [int64]$Expected, [string]$Label) {
    $actual = [int64](Get-Item -LiteralPath $Path).Length
    if ($actual -ne $Expected) {
        throw "$Label size mismatch: $actual"
    }
}

function Write-Json([string]$Path, $Value, [int]$Depth = 20) {
    $json = (($Value | ConvertTo-Json -Depth $Depth) -replace "`r`n", "`n") + "`n"
    [IO.File]::WriteAllText($Path, $json, $Utf8NoBom)
}

function Invoke-Package([string]$Root, [string]$Action, [string]$FixtureRoot, [bool]$AllowDevelopment) {
    $script = Join-Path $Root 'tools\Invoke-FileOnlyPatch.ps1'
    $arguments = @('-NoLogo', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $script, '-Action', $Action)
    if ($FixtureRoot) { $arguments += @('-GameRoot', $FixtureRoot) }
    if ($AllowDevelopment) { $arguments += '-AllowDevelopmentMilestone' }
    $previousPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $output = & $PowerShellExe @arguments 2>&1 | Out-String
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousPreference
    }
    return [pscustomobject]@{ exit_code = $exitCode; output = $output }
}

function Invoke-StandaloneAudit([string]$Root, [string]$ZipPath = $null) {
    $arguments = @(
        '-NoLogo', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
        (Join-Path $PSScriptRoot 'Audit-ReleaseP4VNext.ps1'), '-PackageRoot', $Root
    )
    if ($ZipPath) { $arguments += @('-ZipPath', $ZipPath) }
    $previousPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $output = & $PowerShellExe @arguments 2>&1 | Out-String
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousPreference
    }
    return [pscustomobject]@{ exit_code = $exitCode; output = $output }
}

function Copy-Package([string]$Destination) {
    [IO.Directory]::CreateDirectory($Destination) | Out-Null
    foreach ($item in @(Get-ChildItem -LiteralPath $PackageRoot -Force)) {
        Copy-Item -LiteralPath $item.FullName -Destination $Destination -Recurse -Force
    }
}

function Update-ManifestFile([string]$Root, [string]$Relative, [bool]$Add) {
    $manifestPath = Join-Path $Root 'release_manifest.json'
    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $native = $Relative.Replace('/', '\')
    $path = Join-Path $Root $native
    $spec = [pscustomobject]@{
        path = $Relative.Replace('\', '/')
        size = [int64](Get-Item -LiteralPath $path).Length
        sha256 = Get-Sha256 $path
    }
    if ($Add) {
        $manifest.files = @($manifest.files) + $spec
    }
    else {
        $found = $false
        $updated = @()
        foreach ($file in @($manifest.files)) {
            if ([string]$file.path -eq $spec.path) {
                $updated += $spec
                $found = $true
            }
            else { $updated += $file }
        }
        if (-not $found) { throw "Manifest file was not found for update: $Relative" }
        $manifest.files = $updated
    }
    Write-Json $manifestPath $manifest 30
}

function Insert-AfterFirst([string]$Text, [string]$Needle, [string]$Insertion) {
    $index = $Text.IndexOf($Needle, [StringComparison]::Ordinal)
    if ($index -lt 0) { throw "JSON fixture needle was not found: $Needle" }
    return $Text.Insert($index + $Needle.Length, "`n" + $Insertion)
}

foreach ($path in @($PackageRoot, $Installer, $StockMessage, $StockFont, $TargetMessageSource, $TargetFontSource)) {
    if (-not (Test-Path -LiteralPath $path)) { throw "Required test input is missing: $path" }
}
if (@(Get-Process -Name NOBU16,NOBU16PK,NOBU16PK_EN,NOBU16_Launcher -ErrorAction SilentlyContinue).Count -ne 0) {
    throw 'Close the game and launcher before the offline release test'
}
Assert-Hash $StockMessage $StockMessageHash 'installed stock message before tests'
Assert-Hash $StockFont $StockFontHash 'installed stock font before tests'
Assert-Size $TargetMessageSource $TargetMessageSize 'canonical P4 target message'
Assert-Hash $TargetMessageSource $TargetMessageHash 'canonical P4 target message'
Assert-Size $TargetFontSource $TargetFontSize 'canonical Font-v4 target archive'
Assert-Hash $TargetFontSource $TargetFontHash 'canonical Font-v4 target archive'
$installedMessageBefore = Get-Sha256 $StockMessage
$installedFontBefore = Get-Sha256 $StockFont

$tempParent = [IO.Path]::GetFullPath((Join-Path $KrPatchRoot 'tmp\release_p4_vnext_tests'))
[IO.Directory]::CreateDirectory($tempParent) | Out-Null
$testRoot = Join-Path $tempParent ([Guid]::NewGuid().ToString('N'))
[IO.Directory]::CreateDirectory($testRoot) | Out-Null
$fixture = Join-Path $testRoot 'game'
$fixtureMessage = Join-Path $fixture 'MSG_PK\SC\msgui.bin'
$fixtureFont = Join-Path $fixture 'RES_SC\res_lang.bin'
$helper = $null

$checks = [ordered]@{
    verify_passed = $false
    apply_passed = $false
    restore_passed = $false
    bad_stock_rejected = $false
    mixed_state_recovered = $false
    running_process_refused = $false
    package_tamper_rejected = $false
    json_duplicate_keys_rejected = $false
    build_duplicate_keys_rejected = $false
    audit_duplicate_keys_rejected = $false
    untrusted_installer_not_executed = $false
    installed_game_files_unchanged = $false
    development_gate_refused = $false
    castle_name_runtime_gate_refused = $false
}

try {
    [IO.Directory]::CreateDirectory((Split-Path -Parent $fixtureMessage)) | Out-Null
    [IO.Directory]::CreateDirectory((Split-Path -Parent $fixtureFont)) | Out-Null
    Copy-Item -LiteralPath $StockMessage -Destination $fixtureMessage
    Copy-Item -LiteralPath $StockFont -Destination $fixtureFont

    $verify = Invoke-Package $PackageRoot 'Verify' $null $false
    if ($verify.exit_code -ne 0) { throw "Package Verify failed: $($verify.output)" }
    $checks.verify_passed = $true

    $developmentGate = Invoke-Package $PackageRoot 'Apply' $fixture $false
    if ($developmentGate.exit_code -eq 0) { throw 'Development apply gate did not refuse an unvalidated package' }
    Assert-Hash $fixtureMessage $StockMessageHash 'development-gate message'
    Assert-Hash $fixtureFont $StockFontHash 'development-gate font'
    $checks.development_gate_refused = $true

    $apply = Invoke-Package $PackageRoot 'Apply' $fixture $true
    if ($apply.exit_code -ne 0) { throw "Isolated Apply failed: $($apply.output)" }
    Assert-Hash $fixtureMessage $TargetMessageHash 'isolated apply message'
    Assert-Hash $fixtureFont $TargetFontHash 'isolated apply font'
    Assert-Size $fixtureMessage $TargetMessageSize 'isolated apply message'
    Assert-Size $fixtureFont $TargetFontSize 'isolated apply font'
    $backupRoot = Join-Path $fixture 'KR_PATCH_BACKUP\msgui_p4_font_v4_v0_3'
    Assert-Hash (Join-Path $backupRoot 'message_sc.stock.bak') $StockMessageHash 'message backup'
    Assert-Hash (Join-Path $backupRoot 'font_sc.stock.bak') $StockFontHash 'font backup'
    $state = Get-Content -LiteralPath (Join-Path $backupRoot 'install_state.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($state.status -ne 'applied') { throw 'Apply transaction journal did not reach applied' }
    $checks.apply_passed = $true

    $restore = Invoke-Package $PackageRoot 'Restore' $fixture $true
    if ($restore.exit_code -ne 0) { throw "Isolated Restore failed: $($restore.output)" }
    Assert-Hash $fixtureMessage $StockMessageHash 'isolated restore message'
    Assert-Hash $fixtureFont $StockFontHash 'isolated restore font'
    $checks.restore_passed = $true

    [byte[]]$bad = [IO.File]::ReadAllBytes($fixtureMessage)
    $bad[$bad.Length - 1] = $bad[$bad.Length - 1] -bxor 1
    [IO.File]::WriteAllBytes($fixtureMessage, $bad)
    $badHash = Get-Sha256 $fixtureMessage
    $badApply = Invoke-Package $PackageRoot 'Apply' $fixture $true
    if ($badApply.exit_code -eq 0) { throw 'Bad-stock Apply unexpectedly succeeded' }
    Assert-Hash $fixtureMessage $badHash 'bad-stock message preservation'
    Assert-Hash $fixtureFont $StockFontHash 'bad-stock font preservation'
    $checks.bad_stock_rejected = $true
    Copy-Item -LiteralPath $StockMessage -Destination $fixtureMessage -Force

    $mixedApply = Invoke-Package $PackageRoot 'Apply' $fixture $true
    if ($mixedApply.exit_code -ne 0) { throw "Mixed-state setup Apply failed: $($mixedApply.output)" }
    Copy-Item -LiteralPath $StockMessage -Destination $fixtureMessage -Force
    Assert-Hash $fixtureMessage $StockMessageHash 'mixed message setup'
    Assert-Hash $fixtureFont $TargetFontHash 'mixed font setup'
    $mixedRestore = Invoke-Package $PackageRoot 'Restore' $fixture $true
    if ($mixedRestore.exit_code -ne 0) { throw "Mixed-state recovery failed: $($mixedRestore.output)" }
    Assert-Hash $fixtureMessage $StockMessageHash 'mixed recovery message'
    Assert-Hash $fixtureFont $StockFontHash 'mixed recovery font'
    $state = Get-Content -LiteralPath (Join-Path $backupRoot 'install_state.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($state.status -ne 'recovered_stock') { throw "Unexpected mixed recovery journal status: $($state.status)" }
    $checks.mixed_state_recovered = $true

    $helperDir = Join-Path $testRoot 'process_helper'
    [IO.Directory]::CreateDirectory($helperDir) | Out-Null
    $helperExe = Join-Path $helperDir 'NOBU16PK.exe'
    Copy-Item -LiteralPath $PowerShellExe -Destination $helperExe
    $helper = Start-Process -FilePath $helperExe -ArgumentList @(
        '-NoLogo', '-NoProfile', '-Command', 'Start-Sleep -Seconds 60'
    ) -WindowStyle Hidden -PassThru
    Start-Sleep -Milliseconds 500
    $helperProcess = Get-Process -Id $helper.Id -ErrorAction Stop
    if ($helperProcess.ProcessName -ne 'NOBU16PK') {
        throw "Helper process name did not match the game gate: $($helperProcess.ProcessName)"
    }
    $processApply = Invoke-Package $PackageRoot 'Apply' $fixture $true
    if ($processApply.exit_code -eq 0) { throw 'Running-process Apply unexpectedly succeeded' }
    Assert-Hash $fixtureMessage $StockMessageHash 'running-process message preservation'
    Assert-Hash $fixtureFont $StockFontHash 'running-process font preservation'
    $checks.running_process_refused = $true
    Stop-Process -Id $helper.Id -Force
    $helper.WaitForExit()
    $helper = $null

    $tamperResults = @()

    $renamedRoot = Join-Path $testRoot 'tamper_complete_p4_resource_at_allowed_path'
    Copy-Package $renamedRoot
    $leakPath = Join-Path $renamedRoot 'components\message\msgui_sc.recipe.json'
    Copy-Item -LiteralPath $TargetMessageSource -Destination $leakPath
    Update-ManifestFile $renamedRoot 'components/message/msgui_sc.recipe.json' $false
    $tamperResults += (Invoke-Package $renamedRoot 'Verify' $null $false).exit_code -ne 0

    $jsonRoot = Join-Path $testRoot 'tamper_json_base64'
    Copy-Package $jsonRoot
    $recipePath = Join-Path $jsonRoot 'components\message\msgui_sc.recipe.json'
    $recipe = Get-Content -LiteralPath $recipePath -Raw -Encoding UTF8 | ConvertFrom-Json
    $blob = [Convert]::ToBase64String([IO.File]::ReadAllBytes($TargetMessageSource))
    $recipe | Add-Member -NotePropertyName 'forbidden_complete_resource_base64' -NotePropertyValue $blob
    Write-Json $recipePath $recipe 30
    Update-ManifestFile $jsonRoot 'components/message/msgui_sc.recipe.json' $false
    $tamperResults += (Invoke-Package $jsonRoot 'Verify' $null $false).exit_code -ne 0

    $zipRoot = Join-Path $testRoot 'tamper_nested_zip'
    Copy-Package $zipRoot
    $nestedZip = Join-Path $zipRoot 'components\message\hidden.zip'
    Compress-Archive -LiteralPath $TargetMessageSource -DestinationPath $nestedZip
    Update-ManifestFile $zipRoot 'components/message/hidden.zip' $true
    $tamperResults += (Invoke-Package $zipRoot 'Verify' $null $false).exit_code -ne 0

    Add-Type -AssemblyName System.IO.Compression
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $hostileZipPath = Join-Path $testRoot 'tamper_zip_traversal.zip'
    $zipStream = [IO.File]::Open(
        $hostileZipPath,
        [IO.FileMode]::CreateNew,
        [IO.FileAccess]::ReadWrite,
        [IO.FileShare]::None
    )
    $zipArchive = $null
    try {
        $zipArchive = [IO.Compression.ZipArchive]::new(
            $zipStream,
            [IO.Compression.ZipArchiveMode]::Create,
            $false
        )
        $packagePrefix = [IO.Path]::GetFileName($PackageRoot) + '/'
        $hostileEntry = $zipArchive.CreateEntry($packagePrefix + '../escape.txt')
        $entryStream = $hostileEntry.Open()
        try {
            [byte[]]$entryBytes = [Text.Encoding]::UTF8.GetBytes('hostile traversal probe')
            $entryStream.Write($entryBytes, 0, $entryBytes.Length)
        }
        finally {
            $entryStream.Dispose()
        }
    }
    finally {
        if ($null -ne $zipArchive) { $zipArchive.Dispose() }
        $zipStream.Dispose()
    }
    $tamperResults += (Invoke-StandaloneAudit $PackageRoot $hostileZipPath).exit_code -ne 0

    $duplicateRoot = Join-Path $testRoot 'tamper_duplicate_manifest_key'
    Copy-Package $duplicateRoot
    $duplicateManifest = Join-Path $duplicateRoot 'release_manifest.json'
    $raw = [IO.File]::ReadAllText($duplicateManifest, [Text.Encoding]::UTF8)
    $raw = Insert-AfterFirst $raw '"release_eligible":  false,' '    "release_eligible":  false,'
    [IO.File]::WriteAllText($duplicateManifest, $raw, $Utf8NoBom)
    $duplicateVerifyRejected = (Invoke-Package $duplicateRoot 'Verify' $null $false).exit_code -ne 0
    $duplicateAuditRejected = (Invoke-StandaloneAudit $duplicateRoot).exit_code -ne 0
    $tamperResults += ($duplicateVerifyRejected -and $duplicateAuditRejected)
    $checks.audit_duplicate_keys_rejected = $duplicateAuditRejected

    $nestedDuplicateRoot = Join-Path $testRoot 'tamper_nested_duplicate_evidence_key'
    Copy-Package $nestedDuplicateRoot
    $duplicateEvidence = Join-Path $nestedDuplicateRoot 'VALIDATION_EVIDENCE.json'
    $raw = [IO.File]::ReadAllText($duplicateEvidence, [Text.Encoding]::UTF8)
    $raw = Insert-AfterFirst $raw '"passed":  false,' '                    "passed":  false,'
    [IO.File]::WriteAllText($duplicateEvidence, $raw, $Utf8NoBom)
    Update-ManifestFile $nestedDuplicateRoot 'VALIDATION_EVIDENCE.json' $false
    $tamperResults += (Invoke-Package $nestedDuplicateRoot 'Verify' $null $false).exit_code -ne 0

    $escapedDuplicateRoot = Join-Path $testRoot 'tamper_escaped_duplicate_manifest_key'
    Copy-Package $escapedDuplicateRoot
    $escapedManifest = Join-Path $escapedDuplicateRoot 'release_manifest.json'
    $raw = [IO.File]::ReadAllText($escapedManifest, [Text.Encoding]::UTF8)
    $raw = Insert-AfterFirst $raw '"release_eligible":  false,' '    "releas\u0065_eligible":  false,'
    [IO.File]::WriteAllText($escapedManifest, $raw, $Utf8NoBom)
    $tamperResults += (Invoke-Package $escapedDuplicateRoot 'Verify' $null $false).exit_code -ne 0

    $caseDuplicateRoot = Join-Path $testRoot 'tamper_case_collision_manifest_key'
    Copy-Package $caseDuplicateRoot
    $caseManifest = Join-Path $caseDuplicateRoot 'release_manifest.json'
    $raw = [IO.File]::ReadAllText($caseManifest, [Text.Encoding]::UTF8)
    $raw = Insert-AfterFirst $raw '"release_eligible":  false,' '    "Release_eligible":  false,'
    [IO.File]::WriteAllText($caseManifest, $raw, $Utf8NoBom)
    $tamperResults += (Invoke-Package $caseDuplicateRoot 'Verify' $null $false).exit_code -ne 0

    $markerRoot = Join-Path $testRoot 'tamper_installer_marker'
    Copy-Package $markerRoot
    $markerPath = Join-Path $testRoot 'packaged_installer_was_executed.marker'
    $markerInstaller = Join-Path $markerRoot 'tools\Invoke-FileOnlyPatch.ps1'
    $raw = [IO.File]::ReadAllText($markerInstaller, [Text.Encoding]::UTF8)
    $escapedMarkerPath = $markerPath.Replace("'", "''")
    $markerCode = "[IO.File]::WriteAllText('$escapedMarkerPath', 'executed')"
    $raw = Insert-AfterFirst $raw 'Set-StrictMode -Version Latest' $markerCode
    [IO.File]::WriteAllText($markerInstaller, $raw, $Utf8NoBom)
    Update-ManifestFile $markerRoot 'tools/Invoke-FileOnlyPatch.ps1' $false
    $previousPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $auditOutput = & $PowerShellExe -NoLogo -NoProfile -ExecutionPolicy Bypass -File `
            (Join-Path $PSScriptRoot 'Audit-ReleaseP4VNext.ps1') -PackageRoot $markerRoot 2>&1 | Out-String
        $auditExit = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousPreference
    }
    $markerRejected = $auditExit -ne 0 -and -not (Test-Path -LiteralPath $markerPath)
    $tamperResults += $markerRejected

    if (@($tamperResults | Where-Object { $_ -ne $true }).Count -ne 0 -or $tamperResults.Count -ne 9) {
        throw 'One or more public-package leak regression fixtures were accepted'
    }
    $checks.package_tamper_rejected = $true
    $checks.json_duplicate_keys_rejected = $true
    $checks.untrusted_installer_not_executed = $true

    $builderProbeEvidence = Join-Path $testRoot 'builder_duplicate_evidence.json'
    $builderProbe = [ordered]@{
        schema = 'nobu16.file-only-offline-validation.v2'
        passed = $true
        validated_utc = [DateTime]::UtcNow.ToString('o')
        checks = $checks
        artifacts = [ordered]@{
            message_stock_sha256 = $StockMessageHash
            message_target_sha256 = $TargetMessageHash
            font_stock_sha256 = $StockFontHash
            font_target_sha256 = $TargetFontHash
            powershell_version = [string]$PSVersionTable.PSVersion
        }
    }
    Write-Json $builderProbeEvidence $builderProbe 20
    $raw = [IO.File]::ReadAllText($builderProbeEvidence, [Text.Encoding]::UTF8)
    $raw = Insert-AfterFirst $raw '"passed":  true,' '    "passed":  true,'
    [IO.File]::WriteAllText($builderProbeEvidence, $raw, $Utf8NoBom)
    $builderProbeOutput = Join-Path $KrPatchRoot ('releases\.p4_vnext_json_guard_probe_' + [Guid]::NewGuid().ToString('N'))
    $previousPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $builderOutput = & $PowerShellExe -NoLogo -NoProfile -ExecutionPolicy Bypass -File `
            (Join-Path $PSScriptRoot 'Build-ReleaseP4VNext.ps1') -OutputRoot $builderProbeOutput `
            -OfflineEvidencePath $builderProbeEvidence 2>&1 | Out-String
        $builderExit = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousPreference
    }
    $checks.build_duplicate_keys_rejected = $builderExit -ne 0
    if (Test-Path -LiteralPath $builderProbeOutput -PathType Container) {
        $probeFull = [IO.Path]::GetFullPath($builderProbeOutput)
        $releasePrefix = ([IO.Path]::GetFullPath((Join-Path $KrPatchRoot 'releases'))).TrimEnd('\') + '\'
        if (-not $probeFull.StartsWith($releasePrefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw 'Builder duplicate-key probe escaped the releases directory'
        }
        Remove-Item -LiteralPath $probeFull -Recurse -Force
    }
    if (-not $checks.build_duplicate_keys_rejected) {
        throw 'Builder accepted duplicate JSON keys before ConvertFrom-Json'
    }

    Assert-Hash $StockMessage $installedMessageBefore 'installed message before castle-name gate probe'
    Assert-Hash $StockFont $installedFontBefore 'installed font before castle-name gate probe'
    $checks.installed_game_files_unchanged = $true

    $runtimeGateOfflineEvidence = Join-Path $testRoot 'castle_gate_offline_evidence.json'
    $runtimeGateOffline = [ordered]@{
        schema = 'nobu16.file-only-offline-validation.v2'
        passed = $true
        validated_utc = [DateTime]::UtcNow.ToString('o')
        checks = $checks
        artifacts = [ordered]@{
            message_stock_sha256 = $StockMessageHash
            message_target_sha256 = $TargetMessageHash
            font_stock_sha256 = $StockFontHash
            font_target_sha256 = $TargetFontHash
            powershell_version = [string]$PSVersionTable.PSVersion
        }
    }
    Write-Json $runtimeGateOfflineEvidence $runtimeGateOffline 20
    $runtimeGateEvidence = Join-Path $testRoot 'castle_gate_runtime_evidence.json'
    $runtimeGate = [ordered]@{
        schema = 'nobu16.file-only-runtime-validation.v2'
        passed = $true
        artifacts = [ordered]@{
            message_target_sha256 = $TargetMessageHash
            font_target_sha256 = $TargetFontHash
            validated_utc = [DateTime]::UtcNow.ToString('o')
        }
        checks = [ordered]@{
            boot_completed = $true
            korean_ui_visible = $true
            castle_name_horizontal = $false
            missing_glyphs_checked = $true
            clipping_checked = $true
            normal_exit = $true
            stock_restored_after_qa = $true
        }
        screens = @()
        scope = [ordered]@{ observed_labels = @(); untested_areas = @() }
    }
    Write-Json $runtimeGateEvidence $runtimeGate 20
    $runtimeGateOutput = Join-Path $KrPatchRoot `
        ('releases\.p4_vnext_castle_gate_probe_' + [Guid]::NewGuid().ToString('N'))
    $previousPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $runtimeGateText = & $PowerShellExe -NoLogo -NoProfile -ExecutionPolicy Bypass -File `
            (Join-Path $PSScriptRoot 'Build-ReleaseP4VNext.ps1') -OutputRoot $runtimeGateOutput `
            -OfflineEvidencePath $runtimeGateOfflineEvidence `
            -RuntimeEvidencePath $runtimeGateEvidence 2>&1 | Out-String
        $runtimeGateExit = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousPreference
    }
    if ($runtimeGateExit -eq 0 -or
        -not $runtimeGateText.Contains('castle_name_horizontal') -or
        (Test-Path -LiteralPath $runtimeGateOutput)) {
        throw 'Builder accepted runtime evidence while castle names remain vertical'
    }
    $checks.castle_name_runtime_gate_refused = $true

    Assert-Hash $StockMessage $installedMessageBefore 'installed message after tests'
    Assert-Hash $StockFont $installedFontBefore 'installed font after tests'
    $checks.installed_game_files_unchanged = $true

    $evidence = [ordered]@{
        schema = 'nobu16.file-only-offline-validation.v2'
        passed = $true
        validated_utc = [DateTime]::UtcNow.ToString('o')
        checks = $checks
        artifacts = [ordered]@{
            message_stock_sha256 = $StockMessageHash
            message_target_sha256 = $TargetMessageHash
            font_stock_sha256 = $StockFontHash
            font_target_sha256 = $TargetFontHash
            powershell_version = [string]$PSVersionTable.PSVersion
        }
        leak_regressions = @(
            'complete P4 msgui substituted into an allowlisted recipe path rejected',
            'complete P4 msgui embedded as ignored base64 JSON field rejected',
            'unlisted hostile nested ZIP containing complete P4 msgui rejected',
            'hostile ZIP traversal member rejected by the standalone audit',
            'direct duplicate manifest key rejected before ConvertFrom-Json',
            'nested duplicate evidence key rejected before ConvertFrom-Json',
            'escaped-equivalent manifest key rejected before ConvertFrom-Json',
            'OrdinalIgnoreCase manifest key collision rejected before ConvertFrom-Json',
            'standalone audit rejected a modified installer before marker code executed',
            'builder rejected duplicate evidence keys before ConvertFrom-Json'
        )
    }
    [IO.Directory]::CreateDirectory((Split-Path -Parent $EvidenceOutput)) | Out-Null
    Write-Json $EvidenceOutput $evidence 20
}
finally {
    if ($null -ne $helper) {
        try { Stop-Process -Id $helper.Id -Force -ErrorAction SilentlyContinue } catch { }
    }
    $testRootFull = [IO.Path]::GetFullPath($testRoot)
    $tempPrefix = $tempParent.TrimEnd('\') + '\'
    if ($testRootFull.StartsWith($tempPrefix, [StringComparison]::OrdinalIgnoreCase) -and
        (Test-Path -LiteralPath $testRootFull -PathType Container)) {
        Remove-Item -LiteralPath $testRootFull -Recurse -Force
    }
}

Get-Content -LiteralPath $EvidenceOutput -Raw -Encoding UTF8 | ConvertFrom-Json
