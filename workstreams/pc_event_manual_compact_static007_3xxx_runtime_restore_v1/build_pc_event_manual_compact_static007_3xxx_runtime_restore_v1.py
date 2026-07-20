#!/usr/bin/env python3
"""Build the final private Static Patch 007 runtime-token event candidate.

The build consumes only the latest 607-row private Korean candidate as its
binary input.  It applies two already-audited Korean proposals: 17 held rows
from the 3442--3611 review and 26 held rows from the 3xxx review.  Every row
is checked against the batch07 artifact baseline, the latest strict input,
direct PC contexts, protected controls, strict-table full-name substitution,
and the Static Patch 007 four-line layout.  The sole output is private under
this workstream's tmp root; Steam, Git, release, and network actions do not
exist in this program.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_ROOT = TMP_ROOT / "candidate-final"
RESOURCE = Path("MSG_PK") / "JP" / "msgev.bin"
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.pc-event-manual-compact-static007-3xxx-runtime-restore.v1"
LATEST_WORKSTREAM = "pc_event_manual_compact_static007_3900_11008_restore_v1"
LATEST_ROOT = REPO / "tmp" / LATEST_WORKSTREAM / "candidate-final"
LATEST_EVENT = LATEST_ROOT / RESOURCE
LATEST_AUDIT = LATEST_ROOT / "audit.v1.json"
LATEST_MANIFEST = LATEST_ROOT / "candidate_manifest.v1.json"
EXPECTED_LATEST_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "2DFE8833BC6153E3EF76701EC8A823CA21AAAFF561090BD06957A0426CC07871",
    "raw_size": 1_042_232,
    "sha256": "A5F09D0E36A044D895C41BEA56ADC6809A9768BF2D3AFE79B1793E8BCC4B1867",
    "size": 1_046_345,
}

BATCH07_WORKSTREAM = "pc_event_manual_compact_static007_batch07_v1"
BATCH07_ROOT = REPO / "tmp" / BATCH07_WORKSTREAM / "candidate-final"
BATCH07_EVENT = BATCH07_ROOT / RESOURCE
BATCH07_AUDIT = BATCH07_ROOT / "audit.v1.json"
BATCH07_MANIFEST = BATCH07_ROOT / "candidate_manifest.v1.json"
EXPECTED_BATCH07_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "85C48E864CC06831EB8F31C713703E0E3715848EE049A36B4F53CEB757F186E3",
    "raw_size": 1_020_156,
    "sha256": "5B84334A51829A8D981F4BE5E161D73803894D29F7FA1D91AC40090671CB347D",
    "size": 1_024_182,
}

BATCH07_BUILDER = (
    REPO
    / "workstreams"
    / BATCH07_WORKSTREAM
    / "build_pc_event_manual_compact_static007_batch07_v1.py"
)
RUNTIME_3XXX_REPORT = (
    REPO
    / "workstreams"
    / "pc_event_3xxx_runtime_review_v1"
    / "public"
    / "pc_event_3xxx_runtime_review.v1.json"
)
RUNTIME_3442_REPORT = (
    REPO
    / "workstreams"
    / "manual_compact_runtime_3442_3611_review_v1"
    / "public"
    / "manual_compact_runtime_3442_3611_review.v1.json"
)

EXPECTED_RUNTIME_3442_IDS = (
    3_442,
    3_443,
    3_444,
    3_448,
    3_455,
    3_456,
    3_459,
    3_499,
    3_519,
    3_520,
    3_524,
    3_526,
    3_548,
    3_565,
    3_576,
    3_579,
    3_611,
)
EXPECTED_RUNTIME_3XXX_IDS = (
    3_692,
    3_694,
    3_703,
    3_713,
    3_715,
    3_734,
    3_736,
    3_765,
    3_766,
    3_767,
    3_783,
    3_789,
    3_795,
    3_798,
    3_806,
    3_810,
    3_815,
    3_818,
    3_859,
    3_860,
    3_861,
    3_862,
    3_865,
    3_875,
    3_876,
    3_877,
)
EXPECTED_TARGET_IDS = tuple(sorted(EXPECTED_RUNTIME_3442_IDS + EXPECTED_RUNTIME_3XXX_IDS))
QUALITY_CORRECTION_IDS = (3_524, 3_579, 3_713, 3_767, 3_789)
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "920373F9AFA47959C291025A3D3230B4064261997090AFC01A1EE57F61153FFB",
    "raw_size": 1_043_920,
    "sha256": "CFF60029741A596F40EA19DF9F05A8FEC53E240EF09C750B732D052195A04D35",
    "size": 1_048_039,
}

RAW_G1N_LIMIT = 1_440
EFFECTIVE_LIMIT = 912
MAX_LINES = 4
RUNTIME_RE = re.compile(r"\[([A-Za-z]+)(\d+)\]")
LINEBREAK_RE = re.compile(r"\r\n|\r|\n")


@dataclass(frozen=True)
class ArtifactSpec:
    name: str
    path: Path
    sha256: str
    schema: str
    rows_key: str
    baseline_key: str
    target_key: str
    expected_ids: tuple[int, ...]
    family: str


@dataclass(frozen=True)
class Proposal:
    entry_id: int
    artifact: ArtifactSpec
    source_row: Mapping[str, Any]
    baseline_ko: str
    target_ko: str


@dataclass(frozen=True)
class Bundle:
    event: bytes
    profile: Mapping[str, Any]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


ARTIFACT_SPECS = (
    ArtifactSpec(
        name="manual_compact_runtime_3442_3611_review_v1",
        path=RUNTIME_3442_REPORT,
        sha256="45A08D14DDED7DF0AE86D68ECEF78B050EF681D3ED35CF9404DF422F02A4A938",
        schema="nobu16.kr.manual-compact-runtime-3442-3611-review.v1",
        rows_key="entries",
        baseline_key="current_ko_at_batch07_strict_baseline",
        target_key="proposed_ko",
        expected_ids=EXPECTED_RUNTIME_3442_IDS,
        family="runtime_3442_3611",
    ),
    ArtifactSpec(
        name="pc_event_3xxx_runtime_review_v1",
        path=RUNTIME_3XXX_REPORT,
        sha256="414EDDB6B8920DD14C78681E295A12ACF21E5CAD44E947A3123207775FABD1F5",
        schema="nobu16.kr.pc-event-3xxx-runtime-review.v1",
        rows_key="rows",
        baseline_key="strict_batch07_current_ko",
        target_key="target_ko",
        expected_ids=EXPECTED_RUNTIME_3XXX_IDS,
        family="runtime_3xxx",
    ),
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


batch07 = load_module("pc_event_runtime_restore_batch07", BATCH07_BUILDER)
base = batch07.base


class RuntimeRestoreError(RuntimeError):
    """Raised when a strict input, evidence artifact, or output drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeRestoreError(message)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def relative(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def file_record(path: Path) -> Mapping[str, Any]:
    payload = path.read_bytes()
    return {"relative_path": relative(path), "sha256": sha256(payload), "size": len(payload)}


def event_profile(packed: bytes, raw: bytes) -> Mapping[str, Any]:
    return {
        "raw_sha256": sha256(raw),
        "raw_size": len(raw),
        "sha256": sha256(packed),
        "size": len(packed),
    }


def normalized_lines(value: str) -> list[str]:
    return LINEBREAK_RE.sub("\n", value).split("\n")


def ids_hash(ids: Sequence[int]) -> str:
    return sha256(",".join(str(entry_id) for entry_id in ids).encode("ascii"))


def load_json(path: Path) -> Mapping[str, Any]:
    require(path.is_file(), f"JSON artifact missing: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON artifact root is not an object: {path}")
    return value


def candidate_files(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}


def load_pinned_candidate(
    *,
    name: str,
    root: Path,
    event_path: Path,
    audit_path: Path,
    manifest_path: Path,
    expected_profile: Mapping[str, Any],
) -> tuple[Any, tuple[str, ...], bytes, Mapping[str, Any], Mapping[str, Any]]:
    resolved_root = root.resolve(strict=True)
    require(resolved_root.is_relative_to((REPO / "tmp").resolve()), f"{name}: candidate escapes tmp")
    expected_files = {RESOURCE.as_posix(), "audit.v1.json", "candidate_manifest.v1.json"}
    require(candidate_files(resolved_root) == expected_files, f"{name}: candidate file scope drift")
    packed = event_path.read_bytes()
    header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    require(rebuild_message_table(table, table.texts) == raw, f"{name}: message table round-trip drift")
    profile = event_profile(packed, raw)
    require(profile == expected_profile, f"{name}: pinned packed/raw profile drift")
    audit = load_json(audit_path)
    manifest = load_json(manifest_path)
    require(audit.get("candidate_only") is True, f"{name}: audit is not private")
    require(manifest.get("candidate_only") is True, f"{name}: manifest is not private")
    require(manifest.get("output") == profile, f"{name}: manifest output profile drift")
    require(audit.get("output_event_profile") == profile, f"{name}: audit output profile drift")
    require(len(table.texts) == 17_916, f"{name}: string topology drift")
    record = {
        "workstream": name,
        "candidate_relative": relative(root),
        "event_relative": relative(event_path),
        "event_profile": profile,
        "audit": file_record(audit_path),
        "candidate_manifest": file_record(manifest_path),
    }
    return header, tuple(table.texts), raw, profile, record


def substitute_strict_names(value: str, strict_texts: Sequence[str]) -> tuple[str, list[Mapping[str, Any]]]:
    reservations: list[Mapping[str, Any]] = []

    def replacement(match: re.Match[str]) -> str:
        token = match.group(0)
        name_id = int(match.group(2))
        require(0 <= name_id < len(strict_texts), f"runtime name ID out of range: {token}")
        name = strict_texts[name_id]
        require("\n" not in name and "\r" not in name and "\x00" not in name, f"bad strict name: {token}")
        name_metrics = list(base.line_metrics(name))
        require(len(name_metrics) == 1, f"strict name unexpectedly wraps: {token}")
        reservations.append(
            {
                "token": token,
                "token_prefix": match.group(1),
                "strict_name_id": name_id,
                "strict_korean_name": name,
                "strict_korean_name_utf16le_sha256": text_hash(name),
                "strict_korean_name_raw_g1n_width_px": name_metrics[0]["raw_g1n_width_px"],
                "strict_korean_name_effective_width_px": name_metrics[0]["effective_width_px"],
                "runtime_proven": False,
                "reservation_policy": "Reserve the complete strict Korean name at the numeric token ID; token-prefix behavior is not inferred.",
            }
        )
        return name

    return RUNTIME_RE.sub(replacement, value), reservations


def measured_layout(value: str, strict_texts: Sequence[str], entry_id: int) -> tuple[str, list[Mapping[str, Any]], list[Mapping[str, Any]]]:
    rendered, reservations = substitute_strict_names(value, strict_texts)
    metrics = list(base.line_metrics(rendered))
    require(1 <= len(metrics) <= MAX_LINES, f"{entry_id}: rendered line count outside 1..4")
    require(all(line["raw_g1n_width_px"] <= RAW_G1N_LIMIT for line in metrics), f"{entry_id}: raw width overflow")
    require(all(line["effective_width_px"] <= EFFECTIVE_LIMIT for line in metrics), f"{entry_id}: effective width overflow")
    require(all(line["passes_static_patch_007"] for line in metrics), f"{entry_id}: Static Patch 007 failure")
    return rendered, reservations, metrics


def assert_source_layout(spec: ArtifactSpec, source: Mapping[str, Any], target: str, metrics: Sequence[Mapping[str, Any]]) -> None:
    entry_id = int(source["entry_id"])
    if spec.family == "runtime_3xxx":
        require(source.get("line_count") == len(metrics), f"{entry_id}: 3xxx source line-count drift")
        require(source.get("all_static_patch_007_lines_pass") is True, f"{entry_id}: 3xxx source layout failed")
        source_lines = source.get("displayed_lines")
        require(isinstance(source_lines, list) and len(source_lines) == len(metrics), f"{entry_id}: 3xxx source lines missing")
        for expected, actual in zip(source_lines, metrics):
            for key in (
                "line_number",
                "display_string",
                "raw_g1n_width_px",
                "effective_width_px",
                "full_width_character_count",
                "half_width_character_count",
                "passes_static_patch_007",
            ):
                require(expected.get(key) == actual.get(key), f"{entry_id}: 3xxx source metric drift: {key}")
        require(source.get("japanese_source_line_breaks_used") is False, f"{entry_id}: Japanese LF source reused")
        require(source.get("korean_sentence_shortened_or_deleted") is False, f"{entry_id}: Korean sentence shortened")
        return

    layout = source.get("layout")
    require(isinstance(layout, dict), f"{entry_id}: 3442 source layout missing")
    require(layout.get("line_count") == len(metrics), f"{entry_id}: 3442 source line-count drift")
    require(layout.get("all_lines_pass_static_patch_007") is True, f"{entry_id}: 3442 source layout failed")
    source_lines = layout.get("lines")
    target_lines = normalized_lines(target)
    require(isinstance(source_lines, list) and len(source_lines) == len(metrics), f"{entry_id}: 3442 source lines missing")
    require(len(target_lines) == len(metrics), f"{entry_id}: target line split drift")
    for expected, encoded, actual in zip(source_lines, target_lines, metrics):
        require(expected.get("encoded_string") == encoded, f"{entry_id}: 3442 encoded source line drift")
        for key in (
            "line_number",
            "raw_g1n_width_px",
            "effective_width_px",
            "full_width_character_count",
            "half_width_character_count",
        ):
            require(expected.get(key) == actual.get(key), f"{entry_id}: 3442 source metric drift: {key}")
        require(expected.get("exceeds_912px") is False, f"{entry_id}: 3442 source marks overflow")
        require(expected.get("runtime_display_proven") is False, f"{entry_id}: runtime proof unexpectedly claimed")
        source_reservations = expected.get("runtime_reservations")
        require(isinstance(source_reservations, list), f"{entry_id}: 3442 source reservation list missing")
        require(all(item.get("runtime_proven") is False for item in source_reservations), f"{entry_id}: source runtime proof unexpectedly claimed")
    policy = source.get("review_policy")
    require(isinstance(policy, dict), f"{entry_id}: 3442 review policy missing")
    require(policy.get("japanese_source_linebreaks_used_as_layout_authority") is False, f"{entry_id}: Japanese LF source reused")
    require(policy.get("sentence_shortening_or_deletion_allowed") is False, f"{entry_id}: Korean sentence shortening enabled")


def source_direct_text(source: Mapping[str, Any], spec: ArtifactSpec, language: str) -> str:
    if spec.family == "runtime_3xxx":
        value = source.get(f"direct_pc_{language}")
    else:
        values = source.get("direct_pc_sources")
        require(isinstance(values, dict), f"{source.get('entry_id')}: 3442 direct contexts missing")
        value = values.get(language)
    require(isinstance(value, str), f"{source.get('entry_id')}: direct {language} text missing")
    return value


def validate_artifact_metadata(spec: ArtifactSpec, payload: Mapping[str, Any]) -> None:
    require(payload.get("schema") == spec.schema, f"{spec.name}: schema drift")
    if spec.family == "runtime_3xxx":
        coverage = payload.get("coverage")
        summary = payload.get("summary")
        source_policy = payload.get("source_policy")
        require(isinstance(coverage, dict) and coverage.get("manual_source_complete_runtime_target_ids") == list(spec.expected_ids), f"{spec.name}: coverage drift")
        require(coverage.get("source_meaning_correction_ids") == [3713, 3767, 3789], f"{spec.name}: quality-correction coverage drift")
        require(isinstance(summary, dict) and summary.get("all_26_targets_ready_for_followup_candidate") is True, f"{spec.name}: summary drift")
        require(isinstance(source_policy, dict), f"{spec.name}: source policy missing")
        require(source_policy.get("japanese_source_line_breaks_used") is False, f"{spec.name}: Japanese LF policy drift")
        require(source_policy.get("korean_sentence_shortened_or_deleted") is False, f"{spec.name}: Korean shortening policy drift")
    else:
        counts = payload.get("counts")
        safety = payload.get("safety")
        scope = payload.get("scope")
        require(isinstance(counts, dict) and counts.get("all_rows_within_912px") is True, f"{spec.name}: width summary drift")
        require(isinstance(counts, dict) and counts.get("all_rows_within_four_lines") is True, f"{spec.name}: line summary drift")
        require(isinstance(safety, dict) and safety.get("candidate_binary_written") is False, f"{spec.name}: review no longer read-only")
        require(isinstance(scope, dict) and scope.get("target_ids") == list(spec.expected_ids), f"{spec.name}: scope drift")
        require(scope.get("quality_correction_ids") == [3524, 3579], f"{spec.name}: quality-correction scope drift")


def load_proposals(
    *,
    latest_texts: Sequence[str],
    batch07_texts: Sequence[str],
    direct: Mapping[str, Any],
) -> tuple[tuple[Proposal, ...], Mapping[str, Any]]:
    proposals: list[Proposal] = []
    records: dict[str, Any] = {}
    seen: set[int] = set()
    for spec in ARTIFACT_SPECS:
        require(spec.path.is_file(), f"{spec.name}: report missing")
        payload_bytes = spec.path.read_bytes()
        require(sha256(payload_bytes) == spec.sha256, f"{spec.name}: pinned report hash drift")
        payload = load_json(spec.path)
        validate_artifact_metadata(spec, payload)
        source_rows = payload.get(spec.rows_key)
        require(isinstance(source_rows, list), f"{spec.name}: rows missing")
        ids = tuple(row.get("entry_id") for row in source_rows if isinstance(row, dict))
        require(ids == spec.expected_ids, f"{spec.name}: proposal ID order/scope drift")
        for source in source_rows:
            require(isinstance(source, dict), f"{spec.name}: non-object source row")
            entry_id = source.get("entry_id")
            require(isinstance(entry_id, int), f"{spec.name}: entry ID missing")
            require(entry_id not in seen, f"duplicate proposal ID: {entry_id}")
            seen.add(entry_id)
            baseline = source.get(spec.baseline_key)
            target = source.get(spec.target_key)
            require(isinstance(baseline, str) and isinstance(target, str), f"{spec.name}:{entry_id}: proposal text missing")
            require("\x00" not in target, f"{spec.name}:{entry_id}: embedded terminator")
            base.assert_no_break_inside_tag(target)
            require(batch07_texts[entry_id] == baseline, f"{spec.name}:{entry_id}: artifact/batch07 baseline mismatch")
            require(latest_texts[entry_id] == baseline, f"{spec.name}:{entry_id}: artifact/latest strict baseline mismatch")
            require(target != baseline, f"{spec.name}:{entry_id}: proposal is not a real restoration")
            baseline_signature = base.control_signature(baseline)
            target_signature = base.control_signature(target)
            jp_signature = base.control_signature(direct["jp"].texts[entry_id])
            require(baseline_signature == target_signature == jp_signature, f"{spec.name}:{entry_id}: KO/JP control or token drift")
            require(target_signature["runtime_tokens"], f"{spec.name}:{entry_id}: runtime token absent")
            for language in ("jp", "en", "sc", "tc"):
                require(
                    source_direct_text(source, spec, language) == direct[language].texts[entry_id],
                    f"{spec.name}:{entry_id}: direct {language} context drift",
                )
            if spec.family == "runtime_3xxx":
                require(source.get("strict_batch07_current_ko_utf16le_sha256") == text_hash(baseline), f"{entry_id}: 3xxx baseline hash drift")
                require(source.get("target_ko_utf16le_sha256") == text_hash(target), f"{entry_id}: 3xxx target hash drift")
                require(source.get("target_control_signature") == target_signature, f"{entry_id}: 3xxx target signature drift")
                source_reservations = source.get("runtime_token_reservations")
                require(isinstance(source_reservations, list) and source_reservations, f"{entry_id}: 3xxx reservations missing")
            else:
                hashes = source.get("text_sha256_utf16le")
                signatures = source.get("control_signature")
                require(isinstance(hashes, dict) and hashes.get("current_ko") == text_hash(baseline), f"{entry_id}: 3442 baseline hash drift")
                require(isinstance(hashes, dict) and hashes.get("proposed_ko") == text_hash(target), f"{entry_id}: 3442 target hash drift")
                require(isinstance(signatures, dict), f"{entry_id}: 3442 signatures missing")
                proposed_signature = signatures.get("proposed")
                require(isinstance(proposed_signature, dict), f"{entry_id}: 3442 proposed signature missing")
                require(proposed_signature.get("runtime_tokens") == target_signature["runtime_tokens"], f"{entry_id}: 3442 token signature drift")
                require(proposed_signature.get("esc_tags") == target_signature["esc_tokens"], f"{entry_id}: 3442 tag signature drift")
            _rendered, _reservations, metrics = measured_layout(target, latest_texts, entry_id)
            assert_source_layout(spec, source, target, metrics)
            proposals.append(Proposal(entry_id, spec, source, baseline, target))
        records[spec.name] = {
            "artifact": file_record(spec.path),
            "schema": spec.schema,
            "entry_ids": list(spec.expected_ids),
            "entry_ids_sha256": ids_hash(spec.expected_ids),
            "batch07_artifact_baseline_equals_latest_strict_for_all_ids": True,
            "runtime_proven": False,
        }
    proposals.sort(key=lambda proposal: proposal.entry_id)
    require(tuple(proposal.entry_id for proposal in proposals) == EXPECTED_TARGET_IDS, "combined proposal coverage drift")
    require(set(QUALITY_CORRECTION_IDS).issubset(EXPECTED_TARGET_IDS), "quality-correction ID scope drift")
    return tuple(proposals), records


def build_bundle(*, require_output_profile: bool) -> Bundle:
    latest_header, latest_texts, latest_raw, latest_profile, latest_record = load_pinned_candidate(
        name=LATEST_WORKSTREAM,
        root=LATEST_ROOT,
        event_path=LATEST_EVENT,
        audit_path=LATEST_AUDIT,
        manifest_path=LATEST_MANIFEST,
        expected_profile=EXPECTED_LATEST_PROFILE,
    )
    _batch07_header, batch07_texts, _batch07_raw, batch07_profile, batch07_record = load_pinned_candidate(
        name=BATCH07_WORKSTREAM,
        root=BATCH07_ROOT,
        event_path=BATCH07_EVENT,
        audit_path=BATCH07_AUDIT,
        manifest_path=BATCH07_MANIFEST,
        expected_profile=EXPECTED_BATCH07_PROFILE,
    )
    direct, _direct_profiles = base.load_direct_contexts()
    require(all(len(table.texts) == len(latest_texts) for table in direct.values()), "direct context topology drift")
    proposals, artifacts = load_proposals(latest_texts=latest_texts, batch07_texts=batch07_texts, direct=direct)

    target_texts = list(latest_texts)
    for proposal in proposals:
        target_texts[proposal.entry_id] = proposal.target_ko
    raw = rebuild_message_table(parse_message_table(latest_raw), target_texts)
    event = recompress_wrapper(raw, latest_header)
    output_profile = event_profile(event, raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "output profile is not pinned")
        require(output_profile == EXPECTED_OUTPUT_PROFILE, "deterministic output profile drift")
    _after_header, after_raw = decompress_wrapper(event)
    after = parse_message_table(after_raw).texts
    require(tuple(after) == tuple(target_texts), "rebuilt text table drift")
    actual_changed_ids = [
        entry_id
        for entry_id, (before, after_text) in enumerate(zip(latest_texts, target_texts))
        if before != after_text
    ]
    require(actual_changed_ids == list(EXPECTED_TARGET_IDS), "candidate changed-ID scope drift")

    audit_rows: list[Mapping[str, Any]] = []
    for proposal in proposals:
        entry_id = proposal.entry_id
        rendered, reservations, metrics = measured_layout(proposal.target_ko, latest_texts, entry_id)
        source = proposal.source_row
        audit_rows.append(
            {
                "entry_id": entry_id,
                "proposal_artifact": proposal.artifact.name,
                "proposal_artifact_relative": relative(proposal.artifact.path),
                "proposal_artifact_sha256": proposal.artifact.sha256,
                "strict_batch07_artifact_baseline_ko": proposal.baseline_ko,
                "strict_latest_input_ko": latest_texts[entry_id],
                "target_ko": proposal.target_ko,
                "strict_batch07_artifact_baseline_utf16le_sha256": text_hash(proposal.baseline_ko),
                "strict_latest_input_utf16le_sha256": text_hash(latest_texts[entry_id]),
                "target_ko_utf16le_sha256": text_hash(proposal.target_ko),
                "artifact_baseline_equals_latest_strict": True,
                "direct_pc_jp": direct["jp"].texts[entry_id],
                "direct_pc_en": direct["en"].texts[entry_id],
                "direct_pc_sc": direct["sc"].texts[entry_id],
                "direct_pc_tc": direct["tc"].texts[entry_id],
                "target_control_signature": base.control_signature(proposal.target_ko),
                "direct_pc_control_signatures": {
                    language: base.control_signature(direct[language].texts[entry_id])
                    for language in ("jp", "en", "sc", "tc")
                },
                "runtime_tokens": base.control_signature(proposal.target_ko)["runtime_tokens"],
                "runtime_name_reservations": reservations,
                "rendered_display_template": rendered,
                "displayed_lines": metrics,
                "line_count": len(metrics),
                "all_static_patch_007_lines_pass": True,
                "runtime_proven": False,
                "runtime_hold_excluded": False,
                "runtime_resolution_status": "RESOLVED_WITH_CONSERVATIVE_STRICT_NAME_RESERVATION",
                "runtime_resolution_limit": "No live token-prefix rendering claim is made; runtime_proven remains false while the complete strict Korean same-ID name is reserved.",
                "japanese_source_line_breaks_used": False,
                "korean_sentence_shortened_or_deleted": False,
                "quality_correction": entry_id in QUALITY_CORRECTION_IDS,
                "source_review_status": source.get("review_status", source.get("route_status")),
            }
        )

    unresolved_runtime_hold_ids: list[int] = []
    runtime_proven_false_ids = [row["entry_id"] for row in audit_rows if row["runtime_proven"] is False]
    require(runtime_proven_false_ids == list(EXPECTED_TARGET_IDS), "runtime_proven=false accounting drift")
    require(all(row["runtime_hold_excluded"] is False for row in audit_rows), "unresolved runtime hold remains in audit")
    require(all(row["all_static_patch_007_lines_pass"] for row in audit_rows), "audit layout aggregation drift")
    require(all(1 <= row["line_count"] <= MAX_LINES for row in audit_rows), "audit line-count aggregation drift")
    require(all(row["korean_sentence_shortened_or_deleted"] is False for row in audit_rows), "sentence shortening remains in audit")

    audit: Mapping[str, Any] = {
        "schema": SCHEMA + ".audit",
        "candidate_only": True,
        "resource": RESOURCE.as_posix(),
        "strict_input": latest_record,
        "batch07_artifact_baseline": batch07_record,
        "proposal_artifacts": artifacts,
        "static_patch_007_layout": {
            "runtime_font_px": 30,
            "runtime_usable_line_width_px": EFFECTIVE_LIMIT,
            "max_lines": MAX_LINES,
            "raw_g1n_full_width_px": 48,
            "raw_g1n_half_width_px": 24,
            "raw_g1n_pass_limit_px": RAW_G1N_LIMIT,
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "effective_width_pass_limit_px": EFFECTIVE_LIMIT,
            "runtime_name_reservation": "Substitute the complete strict Korean table name at each runtime token numeric ID before measuring each displayed line.",
        },
        "coverage": {
            "proposal_row_count": len(proposals),
            "proposal_row_ids": list(EXPECTED_TARGET_IDS),
            "proposal_row_ids_sha256": ids_hash(EXPECTED_TARGET_IDS),
            "changed_row_count": len(actual_changed_ids),
            "changed_row_ids": actual_changed_ids,
            "changed_row_ids_sha256": ids_hash(actual_changed_ids),
            "all_artifact_baselines_equal_latest_strict": True,
            "all_rows_static_patch_007_pass": True,
            "all_rows_four_or_fewer_lines": True,
            "unresolved_runtime_hold_ids": unresolved_runtime_hold_ids,
            "unresolved_runtime_hold_count": len(unresolved_runtime_hold_ids),
            "runtime_proven_false_ids": runtime_proven_false_ids,
            "runtime_proven_false_count": len(runtime_proven_false_ids),
            "quality_correction_ids": list(QUALITY_CORRECTION_IDS),
            "quality_correction_count": len(QUALITY_CORRECTION_IDS),
            "all_rows_sentence_shortened_or_deleted_false": True,
        },
        "output_event_profile": output_profile,
        "rows": audit_rows,
        "source_policy": {
            "only_korean_binary_build_input_is_latest_607_row_candidate": True,
            "batch07_binary_is_read_only_artifact_baseline_evidence": True,
            "proposal_artifacts_are_source_audited": True,
            "japanese_source_line_breaks_not_reused": True,
            "sentence_shortening_or_deletion_allowed": False,
            "runtime_prefix_semantics_inferred": False,
            "runtime_proven_preserved_false": True,
            "candidate_binary_written_to_steam": False,
            "git_operation_performed": False,
            "release_published": False,
            "network_operation_performed": False,
        },
    }
    manifest: Mapping[str, Any] = {
        "schema": SCHEMA + ".manifest",
        "candidate_only": True,
        "candidate_output_must_be_under": relative(TMP_ROOT),
        "resource": RESOURCE.as_posix(),
        "strict_input": latest_record,
        "batch07_artifact_baseline": batch07_record,
        "proposal_artifacts": artifacts,
        "applied_row_ids": list(EXPECTED_TARGET_IDS),
        "quality_correction_ids": list(QUALITY_CORRECTION_IDS),
        "output": output_profile,
        "unresolved_runtime_hold_ids": unresolved_runtime_hold_ids,
        "runtime_proven_false_ids": runtime_proven_false_ids,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
        "network_operation_performed": False,
    }
    return Bundle(event=event, profile=output_profile, audit=audit, manifest=manifest)


def require_private(path: Path) -> Path:
    resolved = path.resolve()
    root = TMP_ROOT.resolve()
    require(resolved.is_relative_to(root), f"candidate path escapes private tmp root: {resolved}")
    return resolved


def write_candidate(bundle: Bundle) -> Path:
    root = require_private(CANDIDATE_ROOT)
    if root.exists():
        shutil.rmtree(root)
    (root / RESOURCE).parent.mkdir(parents=True, exist_ok=True)
    (root / RESOURCE).write_bytes(bundle.event)
    (root / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
    (root / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
    return root


def verify_private_candidate() -> Mapping[str, Any]:
    bundle = build_bundle(require_output_profile=True)
    root = require_private(CANDIDATE_ROOT)
    require(root.is_dir(), f"candidate missing: {root}")
    expected_files = {RESOURCE.as_posix(), "audit.v1.json", "candidate_manifest.v1.json"}
    require(candidate_files(root) == expected_files, "candidate file scope drift")
    require((root / RESOURCE).read_bytes() == bundle.event, "candidate event differs from deterministic build")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "candidate manifest differs")
    return {
        "status": "PASS",
        "candidate_root": relative(root),
        "event_profile": bundle.profile,
        "applied_row_count": len(EXPECTED_TARGET_IDS),
        "applied_row_ids": list(EXPECTED_TARGET_IDS),
        "unresolved_runtime_hold_count": 0,
        "runtime_proven_false_count": len(EXPECTED_TARGET_IDS),
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
        "network_operation_performed": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "README_KO.md",
        WORKSTREAM / "build_pc_event_manual_compact_static007_3xxx_runtime_restore_v1.py",
        WORKSTREAM / "test_pc_event_manual_compact_static007_3xxx_runtime_restore_v1.py",
    ):
        require(path.is_file(), f"authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        print(json.dumps(build_bundle(require_output_profile=False).profile, ensure_ascii=False, sort_keys=True))
        return 0
    if command == "build":
        source_whitespace_check()
        require(EXPECTED_OUTPUT_PROFILE is not None, "output profile is not pinned")
        print(relative(write_candidate(build_bundle(require_output_profile=True))))
        return 0
    if command == "verify-private":
        source_whitespace_check()
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, sort_keys=True))
        return 0
    bundle = build_bundle(require_output_profile=True)
    print(
        json.dumps(
            {
                "applied_row_ids": bundle.audit["coverage"]["changed_row_ids"],
                "event_profile": bundle.profile,
                "runtime_proven_false_ids": bundle.audit["coverage"]["runtime_proven_false_ids"],
                "unresolved_runtime_hold_ids": bundle.audit["coverage"]["unresolved_runtime_hold_ids"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeRestoreError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
