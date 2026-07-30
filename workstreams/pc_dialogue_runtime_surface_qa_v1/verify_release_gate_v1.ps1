[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Evidence,

    [Parameter(Mandatory = $true)]
    [string]$BaseDialogueMsggame,

    [Parameter(Mandatory = $true)]
    [string]$PkDialogueMsggame
)

$ErrorActionPreference = 'Stop'
$evidencePath = (Resolve-Path -LiteralPath $Evidence).Path
$basePath = (Resolve-Path -LiteralPath $BaseDialogueMsggame).Path
$pkPath = (Resolve-Path -LiteralPath $PkDialogueMsggame).Path

function Require(
    [bool]$Condition,
    [string]$Message
) {
    if (-not $Condition) {
        throw $Message
    }
}

function Assert-BoundResource(
    [object]$EvidenceObject,
    [string]$RelativePath,
    [string]$CandidatePath,
    [string]$ExpectedResource
) {
    $property = $EvidenceObject.resources.PSObject.Properties[$RelativePath]
    Require ($null -ne $property) "Runtime-surface evidence lacks $RelativePath"
    $resource = $property.Value
    $item = Get-Item -LiteralPath $CandidatePath
    $actualSha256 = (
        Get-FileHash -Algorithm SHA256 -LiteralPath $CandidatePath
    ).Hash
    Require (
        [string]$resource.resource -eq $ExpectedResource
    ) "Runtime-surface resource label mismatch: $RelativePath"
    Require (
        [long]$resource.size -eq [long]$item.Length
    ) "Runtime-surface size binding mismatch: $RelativePath"
    Require (
        [string]$resource.sha256 -eq $actualSha256
    ) "Runtime-surface SHA-256 binding mismatch: $RelativePath"
    Require (
        [long]$resource.issue_count -eq 0
    ) "Runtime-surface resource still has issues: $RelativePath"
    Require (
        [long]$resource.surface_issue_count -eq 0
    ) "Runtime-surface resource has surface issues: $RelativePath"
    Require (
        [long]$resource.terminal_boundary_issue_count -eq 0
    ) "Runtime-surface resource has terminal-boundary issues: $RelativePath"
    Require (
        [long]$resource.structure_issue_count -eq 0
    ) "Runtime-surface resource has structure issues: $RelativePath"
    Require (
        [long]$resource.empirical_width_issue_count -eq 0
    ) "Runtime-surface resource has empirical width issues: $RelativePath"
    Require (
        [long]$resource.empirical_width_issue_coordinate_count -eq 0
    ) "Runtime-surface resource has empirical width coordinates: $RelativePath"
    $expectedStructureMutationCount = if (
        $RelativePath -eq 'MSG_PK/JP/msggame.bin'
    ) { 575 } else { 1659 }
    Require (
        [long]$resource.allowed_structure_mutation_count -eq (
            $expectedStructureMutationCount
        )
    ) "Runtime-surface allowed structure mutation count drifted: $RelativePath"
    Require (
        @($resource.category_counts.PSObject.Properties).Count -eq 0
    ) "Runtime-surface resource has non-empty category counts: $RelativePath"
    Require (
        [long]$resource.record_count -eq [long]$resource.decoded_record_count
    ) "Runtime-surface decoder coverage is incomplete: $RelativePath"

    return [ordered]@{
        relative_path = $RelativePath
        size = [long]$item.Length
        sha256 = $actualSha256
    }
}

$gate = Get-Content -Raw -Encoding UTF8 -LiteralPath $evidencePath |
    ConvertFrom-Json
Require (
    [string]$gate.schema -eq (
        'nobu16.kr.pc-dialogue-runtime-surface-final-candidate-gate.v1'
    )
) 'Unexpected runtime-surface evidence schema'
Require ([string]$gate.status -eq 'PASS') 'Runtime-surface evidence is not PASS'
Require (
    [string]$gate.release_target -eq '0.15.0'
) 'Runtime-surface release target drifted'
Require (
    [string]$gate.runtime_completion -eq 'PASS'
) 'Runtime completion is not PASS'
Require (
    $gate.runtime_completion_allowed -eq $true
) 'Runtime completion is not allowed'
Require ([long]$gate.issue_count -eq 0) 'Runtime-surface issue count is not zero'
Require (
    @($gate.issues | Where-Object { $null -ne $_ }).Count -eq 0
) 'Runtime-surface PASS evidence unexpectedly carries issues'
Require (
    $gate.source_or_translation_bodies_omitted -eq $true
) 'Runtime-surface evidence is not source-free'
Require (
    $gate.steam_write_performed -eq $false
) 'Runtime-surface evidence reports a Steam write'
Require (
    [string]$gate.audit_contract.schema -eq (
        'nobu16.kr.pc-dialogue-runtime-surface-audit.v1'
    )
) 'Runtime-surface audit contract schema drifted'
$auditEnginePath = Join-Path $PSScriptRoot 'audit_runtime_surface_v1.py'
Require (
    Test-Path -LiteralPath $auditEnginePath -PathType Leaf
) "Runtime-surface audit engine is absent: $auditEnginePath"
$auditEngineSha256 = (
    Get-FileHash -Algorithm SHA256 -LiteralPath $auditEnginePath
).Hash
Require (
    [string]$gate.audit_contract.engine_sha256 -eq $auditEngineSha256
) 'Runtime-surface audit engine binding mismatch'
$selectorContractPath = Join-Path (
    $PSScriptRoot
) 'ghidra_selector_domain_contract.v1.json'
Require (
    Test-Path -LiteralPath $selectorContractPath -PathType Leaf
) "Selector-domain contract is absent: $selectorContractPath"
$selectorContract = Get-Content -Raw -Encoding UTF8 `
    -LiteralPath $selectorContractPath | ConvertFrom-Json
$selectorContractSha256 = (
    Get-FileHash -Algorithm SHA256 -LiteralPath $selectorContractPath
).Hash
Require (
    [string]$selectorContract.schema -eq (
        'nobu16.kr.pc-dialogue-ghidra-selector-domain-contract.v1'
    )
) 'Unexpected selector-domain contract schema'
Require (
    [string]$gate.audit_contract.selector_domain_contract.schema -eq (
        [string]$selectorContract.schema
    )
) 'Runtime-surface selector-domain schema binding mismatch'
Require (
    [string]$gate.audit_contract.selector_domain_contract.sha256 -eq (
        $selectorContractSha256
    )
) 'Runtime-surface selector-domain hash binding mismatch'
$terminalDetectorPath = Join-Path (
    $PSScriptRoot
) 'terminal_boundary_detector_v1.py'
Require (
    Test-Path -LiteralPath $terminalDetectorPath -PathType Leaf
) "Terminal-boundary detector is absent: $terminalDetectorPath"
$terminalDetectorSha256 = (
    Get-FileHash -Algorithm SHA256 -LiteralPath $terminalDetectorPath
).Hash
Require (
    [string]$gate.audit_contract.terminal_boundary_detector.schema -eq (
        'nobu16.kr.pc-dialogue-terminal-boundary-detector.v1'
    )
) 'Unexpected terminal-boundary detector schema'
Require (
    [string]$gate.audit_contract.terminal_boundary_detector.engine_sha256 -eq (
        $terminalDetectorSha256
    )
) 'Runtime-surface terminal-boundary detector binding mismatch'
Require (
    (
        $gate.audit_contract.terminal_boundary_detector.
            completed_prefix_before_terminal_suffix_forbidden
    ) -eq $true
) 'Runtime-surface gate weakens terminal-boundary rejection'
$structureAuditPath = Join-Path (
    $PSScriptRoot
) 'audit_candidate_structure_v1.py'
Require (
    Test-Path -LiteralPath $structureAuditPath -PathType Leaf
) "Candidate-structure audit is absent: $structureAuditPath"
$structureAuditSha256 = (
    Get-FileHash -Algorithm SHA256 -LiteralPath $structureAuditPath
).Hash
Require (
    [string]$gate.audit_contract.candidate_structure.schema -eq (
        'nobu16.kr.pc-dialogue-candidate-structure-audit.v1'
    )
) 'Unexpected candidate-structure audit schema'
Require (
    [string]$gate.audit_contract.candidate_structure.engine_sha256 -eq (
        $structureAuditSha256
    )
) 'Candidate-structure audit engine binding mismatch'
Require (
    [string]$gate.audit_contract.candidate_structure.report_status -eq 'PASS'
) 'Candidate-structure audit is not PASS'
Require (
    [long]$gate.audit_contract.candidate_structure.report_issue_count -eq 0
) 'Candidate-structure issue count is not zero'
Require (
    $gate.audit_contract.candidate_structure.
        only_reviewed_pk_call_retargets_allowed -eq $true
) 'Candidate-structure audit weakens the reviewed-retarget contract'
Require (
    [long]$gate.audit_contract.candidate_structure.
        base_reviewed_component_mutation_count -eq 1659
) 'Base reviewed structure mutation count drifted'
Require (
    [long]$gate.audit_contract.candidate_structure.
        pk_reviewed_operation_count -eq 569
) 'PK reviewed control-retarget operation count drifted'
Require (
    [string]$gate.audit_contract.candidate_structure.
        pk_reviewed_operation_sha256 -eq (
            'FEBBBBFF456009C2B09C1D8294B4D18F5724A0D710BD718A6162D1A89245B9C7'
        )
) 'PK reviewed control-retarget operation digest drifted'
Require (
    [long]$gate.audit_contract.candidate_structure.
        pk_reviewed_component_mutation_count -eq 575
) 'PK reviewed control-retarget component count drifted'
Require (
    [string]$gate.audit_contract.candidate_structure.
        pk_reviewed_component_contract_sha256 -eq (
            'EBF693AA53CBFA7CA3EA39FD53965706E3B9D384582C6DFC76B53794AF7CC2DE'
        )
) 'PK reviewed control-retarget component digest drifted'
Require (
    $gate.audit_contract.candidate_structure.
        pk_exact_coordinate_component_before_after_hash_bound -eq $true
) 'PK reviewed control-retarget exact component binding is absent'

$empiricalWidthAuditPath = Join-Path (
    $PSScriptRoot
) 'audit_empirical_block_width_policy_v1.py'
Require (
    Test-Path -LiteralPath $empiricalWidthAuditPath -PathType Leaf
) "Candidate empirical width audit is absent: $empiricalWidthAuditPath"
$empiricalWidthAuditSha256 = (
    Get-FileHash -Algorithm SHA256 -LiteralPath $empiricalWidthAuditPath
).Hash
Require (
    [string]$gate.audit_contract.candidate_empirical_block_width.schema -eq (
        'nobu16.kr.msggame-empirical-block-width-policy-audit.v1'
    )
) 'Unexpected candidate empirical width audit schema'
Require (
    [string]$gate.audit_contract.candidate_empirical_block_width.
        engine_sha256 -eq $empiricalWidthAuditSha256
) 'Candidate empirical width audit engine binding mismatch'
Require (
    [string]$gate.audit_contract.candidate_empirical_block_width.
        report_status -eq 'PASS'
) 'Candidate empirical width audit is not PASS'
Require (
    [long]$gate.audit_contract.candidate_empirical_block_width.
        report_issue_count -eq 0
) 'Candidate empirical width issue count is not zero'
Require (
    $gate.audit_contract.candidate_empirical_block_width.
        event_dialogue_912px_gate_applied -eq $false
) 'Candidate empirical width audit incorrectly applies event 912px'
Require (
    $gate.audit_contract.candidate_empirical_block_width.
        final_global_plus_24px_gate_applied -eq $false
) 'Candidate empirical width audit still applies global +24px'
Require (
    $gate.audit_contract.candidate_empirical_block_width.
        candidate_line_must_fit_predecessor_same_block_max -eq $true
) 'Candidate empirical width line-max invariant drifted'
Require (
    $gate.audit_contract.candidate_empirical_block_width.
        candidate_line_count_must_fit_predecessor_same_block_max -eq $true
) 'Candidate empirical width line-count invariant drifted'
Require (
    $gate.audit_contract.candidate_empirical_block_width.
        base_and_pk_required -eq $true
) 'Candidate empirical width audit does not bind Base and PK'

$stageWidthAuditPath = Join-Path (
    $PSScriptRoot
) 'audit_candidate_relative_width_v1.py'
Require (
    Test-Path -LiteralPath $stageWidthAuditPath -PathType Leaf
) "Stage relative-width audit is absent: $stageWidthAuditPath"
$stageWidthAuditSha256 = (
    Get-FileHash -Algorithm SHA256 -LiteralPath $stageWidthAuditPath
).Hash
Require (
    [string]$gate.audit_contract.base_stage_relative_width.schema -eq (
        'nobu16.kr.base-remediation-stage-relative-width.v1'
    )
) 'Unexpected Base stage relative-width schema'
Require (
    [string]$gate.audit_contract.base_stage_relative_width.engine_sha256 -eq (
        $stageWidthAuditSha256
    )
) 'Base stage relative-width engine binding mismatch'
Require (
    [string]$gate.audit_contract.base_stage_relative_width.report_status -eq (
        'PASS'
    )
) 'Base surface/post-call stage relative-width audit is not PASS'
Require (
    [long]$gate.audit_contract.base_stage_relative_width.
        report_issue_count -eq 0
) 'Base surface/post-call stage relative-width issue count is not zero'
Require (
    [long]$gate.audit_contract.base_stage_relative_width.
        surface_and_post_call_maximum_line_growth_px -eq 24
) 'Base surface/post-call +24px limit drifted'
Require (
    $gate.audit_contract.base_stage_relative_width.
        call_semantic_rebuild_excluded_from_plus_24_gate -eq $true
) 'Base semantic call rebuild is not isolated from the +24px stage gate'

$callSemanticPath = Join-Path (
    (Split-Path -Parent $PSScriptRoot)
) 'pc_dialogue_runtime_surface_remediation_v1\base_call_assembly_remediation_v1.py'
Require (
    Test-Path -LiteralPath $callSemanticPath -PathType Leaf
) "Base call-semantic engine is absent: $callSemanticPath"
$callSemanticSha256 = (
    Get-FileHash -Algorithm SHA256 -LiteralPath $callSemanticPath
).Hash
$callSemantic = $gate.audit_contract.base_call_semantic_rebuild
Require (
    [string]$callSemantic.schema -eq (
        'nobu16.kr.base-call-assembly-remediation.v1'
    )
) 'Unexpected Base call-semantic contract schema'
Require (
    [string]$callSemantic.engine_sha256 -eq $callSemanticSha256
) 'Base call-semantic engine binding mismatch'
Require (
    [string]$callSemantic.report_status -eq 'PASS'
) 'Base call-semantic contract is not PASS'
Require (
    [long]$callSemantic.report_issue_count -eq 0
) 'Base call-semantic contract issue count is not zero'
Require (
    [long]$callSemantic.literal_before_after_hash_contract.entry_count -eq (
        [long]$callSemantic.literal_replacement_count
    )
) 'Base call-semantic literal hash contract is incomplete'
Require (
    [string]$callSemantic.literal_before_after_hash_contract.entry_sha256 -match (
        '^[0-9A-F]{64}$'
    )
) 'Base call-semantic literal hash digest is invalid'
Require (
    $callSemantic.literal_before_after_hash_contract.
        source_or_translation_bodies_omitted -eq $true
) 'Base call-semantic literal hash contract is not source-free'
Require (
    $gate.audit_contract.base_and_pk_required -eq $true
) 'Runtime-surface evidence does not require both resources'
Require (
    $gate.audit_contract.issue_count_must_be_zero -eq $true
) 'Runtime-surface evidence weakens the zero-issue invariant'
Require (
    $gate.audit_contract.binary_hash_binding_required -eq $true
) 'Runtime-surface evidence does not require hash binding'

$ghidra = $gate.audit_contract.ghidra_contract
Require (
    $ghidra.literal_and_dynamic_output_are_verbatim -eq $true
) 'Runtime-surface evidence lost the verbatim-output contract'
Require (
    $ghidra.automatic_space_inserted -eq $false
) 'Runtime-surface evidence claims automatic spacing'
Require (
    $ghidra.automatic_punctuation_inserted -eq $false
) 'Runtime-surface evidence claims automatic punctuation'
Require (
    $ghidra.opcode_0143_calls_record -eq $true
) 'Runtime-surface evidence lost the call-record contract'

$resourceProperties = @($gate.resources.PSObject.Properties)
Require (
    $resourceProperties.Count -eq 2
) 'Runtime-surface evidence must bind exactly two resources'
Require (
    @($gate.category_counts.PSObject.Properties).Count -eq 0
) 'Runtime-surface PASS evidence has non-empty category counts'
$bound = @(
    Assert-BoundResource `
        -EvidenceObject $gate `
        -RelativePath 'MSG/JP/msggame.bin' `
        -CandidatePath $basePath `
        -ExpectedResource 'base_msggame'
    Assert-BoundResource `
        -EvidenceObject $gate `
        -RelativePath 'MSG_PK/JP/msggame.bin' `
        -CandidatePath $pkPath `
        -ExpectedResource 'pk_msggame'
)

[ordered]@{
    status = 'PASS'
    schema = [string]$gate.schema
    evidence_sha256 = (
        Get-FileHash -Algorithm SHA256 -LiteralPath $evidencePath
    ).Hash
    resources = $bound
} | ConvertTo-Json -Compress -Depth 6
