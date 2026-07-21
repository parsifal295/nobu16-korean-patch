#!/usr/bin/env python3
"""Build the private Wave 102 Takeda/Hikotsuru event quality candidate.

Only the high-confidence rows from the pinned read-only audit are applied.
The input is the pinned Wave 101 private candidate. Output is limited to this
workstream's private tmp candidate and deterministic audit records; no Steam,
Git, release, or network state is touched.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_ROOT = TMP_ROOT / "candidate-final"
PUBLIC = WORKSTREAM / "public"
PUBLIC_AUDIT = PUBLIC / "pc_event_takeda_hikotsuru_quality_wave102.v1.json"
VALIDATION = WORKSTREAM / "validation.v1.json"
RESOURCE = Path("MSG_PK") / "JP" / "msgev.bin"
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.pc-event-takeda-hikotsuru-quality-wave102.v1"
ROW_COUNT = 17_916
APPLIED_IDS = (
    3529,
    3530,
    3532,
    3533,
    3536,
    3539,
    3540,
    3541,
    3542,
    3546,
    3547,
    3548,
    3550,
    3551,
    3554,
    3555,
    3559,
    3561,
    3563,
    3564,
)
RUNTIME_RESERVATION_IDS = (3548,)

STRICT_WORKSTREAM = "pc_event_kanto_quality_wave101_v1"
STRICT_ROOT = REPO / "tmp" / STRICT_WORKSTREAM / "candidate-final"
STRICT_EVENT = STRICT_ROOT / RESOURCE
STRICT_AUDIT = STRICT_ROOT / "audit.v1.json"
STRICT_MANIFEST = STRICT_ROOT / "candidate_manifest.v1.json"
EXPECTED_STRICT_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "507F8FB7CF75D327F8CC88725E17BE3DA1084C4BD96237B9F1A1E8CE5F9D3B41",
    "raw_size": 1_043_960,
    "sha256": "96DBB584AE96157E3B7013CAF86A4876CDB0B87EFF66433CB9236206996C2D91",
    "size": 1_048_079,
}
EXPECTED_STRICT_AUDIT_SHA256 = "AFEFF861A1DD28C688657A00CB08DFA0C615C933983A3D2723D7428796ABACBC"
EXPECTED_STRICT_MANIFEST_SHA256 = "85C1894EE95C844A6F14B542A127D73768717325139B73D28D791B840536CDAD"

AUDIT_WORKSTREAM = REPO / "workstreams" / "pc_event_takeda_hikotsuru_audit_v1"
AUDIT_SCRIPT = AUDIT_WORKSTREAM / "build_pc_event_takeda_hikotsuru_audit_v1.py"
AUDIT_REPORT = AUDIT_WORKSTREAM / "public" / "pc_event_takeda_hikotsuru_audit.v1.json"
EXPECTED_AUDIT_SCRIPT_SHA256 = "08118E41FF68431EF51649B00A99296161BFF94328A6E77746272B6ABF7F951F"
EXPECTED_AUDIT_REPORT_SHA256 = "1740947E1AD394892166B852FCC47BB416570B41388D0E85E4AE9773DB3AFAA4"

# Deterministic profile from the pinned W101 input and the 20 pinned audit
# proposals. The build and verifier reject any output drift.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "15CC03C20B0E12D4AF2619968CD97C451D5B6A073BB0659000D0E8C6BC645A6B",
    "raw_size": 1_044_196,
    "sha256": "D20E1CC9E1014473DCFCE7C247721FFA912955B0CB6EEA71BB00BD055977FB4E",
    "size": 1_048_316,
}


class Wave102Error(RuntimeError):
    """Raised when strict input, audit provenance, or private output drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave102Error(message)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return digest(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError:
        return str(path)


def file_record(path: Path) -> dict[str, Any]:
    blob = path.read_bytes()
    return {"relative_path": relative(path), "sha256": digest(blob), "size": len(blob)}


def profile(packed: bytes, raw: bytes) -> dict[str, Any]:
    return {
        "raw_sha256": digest(raw),
        "raw_size": len(raw),
        "sha256": digest(packed),
        "size": len(packed),
    }


def candidate_files(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}


def load_table(
    path: Path,
    expected: Mapping[str, Any],
    label: str,
) -> tuple[bytes, Any, bytes, tuple[str, ...], dict[str, Any]]:
    require(path.is_file(), f"{label}: file missing: {path}")
    packed = path.read_bytes()
    header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    require(len(table.texts) == ROW_COUNT, f"{label}: row count drift")
    require(rebuild_message_table(table, table.texts) == raw, f"{label}: message table round-trip drift")
    measured = profile(packed, raw)
    require(measured == expected, f"{label}: packed/raw profile drift")
    return packed, header, raw, tuple(table.texts), measured


def load_audit_module() -> Any:
    require(AUDIT_SCRIPT.is_file(), f"audit builder missing: {AUDIT_SCRIPT}")
    require(digest(AUDIT_SCRIPT.read_bytes()) == EXPECTED_AUDIT_SCRIPT_SHA256, "audit builder hash drift")
    spec = importlib.util.spec_from_file_location("pc_event_takeda_hikotsuru_wave102_helper", AUDIT_SCRIPT)
    require(spec is not None and spec.loader is not None, "cannot load audit helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_strict_input() -> tuple[bytes, Any, bytes, tuple[str, ...], dict[str, Any], dict[str, Any]]:
    root = STRICT_ROOT.resolve(strict=True)
    tmp_root = (REPO / "tmp").resolve()
    require(root.is_relative_to(tmp_root), "strict input escapes private tmp")
    expected_files = {RESOURCE.as_posix(), "audit.v1.json", "candidate_manifest.v1.json"}
    require(candidate_files(root) == expected_files, "strict input candidate scope drift")
    packed, header, raw, texts, packed_profile = load_table(
        STRICT_EVENT,
        EXPECTED_STRICT_PROFILE,
        "Wave 101 strict input",
    )
    audit_record = file_record(STRICT_AUDIT)
    manifest_record = file_record(STRICT_MANIFEST)
    require(audit_record["sha256"] == EXPECTED_STRICT_AUDIT_SHA256, "Wave 101 audit hash drift")
    require(manifest_record["sha256"] == EXPECTED_STRICT_MANIFEST_SHA256, "Wave 101 manifest hash drift")
    audit = json.loads(STRICT_AUDIT.read_text(encoding="utf-8"))
    manifest = json.loads(STRICT_MANIFEST.read_text(encoding="utf-8"))
    require(audit.get("candidate_only") is True, "Wave 101 audit is not private")
    require(manifest.get("candidate_only") is True, "Wave 101 manifest is not private")
    require(audit.get("output_event_profile") == packed_profile, "Wave 101 audit profile drift")
    require(manifest.get("output") == packed_profile, "Wave 101 manifest profile drift")
    return packed, header, raw, texts, packed_profile, {
        "audit": audit_record,
        "candidate_manifest": manifest_record,
    }


def load_pinned_audit(
    audit_helper: Any,
    strict_texts: tuple[str, ...],
    strict_profile: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[int, Mapping[str, Any]]]:
    require(AUDIT_REPORT.is_file(), f"audit report missing: {AUDIT_REPORT}")
    require(digest(AUDIT_REPORT.read_bytes()) == EXPECTED_AUDIT_REPORT_SHA256, "audit report hash drift")
    report = json.loads(AUDIT_REPORT.read_text(encoding="utf-8"))
    require(report.get("schema") == "nobu16.kr.pc-event-takeda-hikotsuru-audit.v1", "audit schema drift")
    scope = report.get("scope")
    coverage = report.get("coverage")
    entries = report.get("entries")
    require(isinstance(scope, Mapping) and isinstance(coverage, Mapping) and isinstance(entries, list), "audit structure drift")
    require(scope.get("resource") == RESOURCE.as_posix(), "audit resource drift")
    require(scope.get("target_ids") == list(range(3527, 3565)), "audit scope drift")
    require(scope.get("strict_input_rebased_from_wave100_to_wave101") is True, "audit W101 rebase guard missing")
    require(scope.get("target_range_identical_between_wave100_and_wave101") is True, "audit non-overlap guard missing")
    source_profile = report.get("sources", {}).get("strict_korean_input", {})
    require(isinstance(source_profile, Mapping), "audit strict profile missing")
    require(source_profile.get("packed_sha256") == strict_profile["sha256"], "audit strict packed hash drift")
    require(source_profile.get("raw_sha256") == strict_profile["raw_sha256"], "audit strict raw hash drift")
    require(coverage.get("static_high_confidence_ids") == list(APPLIED_IDS), "audit applied scope drift")
    require(coverage.get("static_high_confidence_count") == len(APPLIED_IDS), "audit applied count drift")
    require(coverage.get("runtime_reservation_proposal_ids") == list(RUNTIME_RESERVATION_IDS), "audit runtime scope drift")
    require(coverage.get("runtime_or_ui_hold_ids") == [], "audit has unresolved runtime/UI holds")

    by_id = {entry.get("entry_id"): entry for entry in entries if isinstance(entry, Mapping)}
    require(len(by_id) == 38 and all(entry_id in by_id for entry_id in range(3527, 3565)), "audit row topology drift")
    reservations = audit_helper.read_reservations()
    for entry_id in APPLIED_IDS:
        entry = by_id[entry_id]
        require(entry.get("review_status") == "static_high_confidence", f"{entry_id}: audit status drift")
        require(entry.get("changed_in_this_audit") is True, f"{entry_id}: audit change flag drift")
        baseline = entry.get("current_ko")
        target = entry.get("proposed_ko")
        require(isinstance(baseline, str) and isinstance(target, str), f"{entry_id}: audit Korean text missing")
        require(baseline == strict_texts[entry_id], f"{entry_id}: audit baseline does not match Wave 101")
        require(baseline != target, f"{entry_id}: audit target is unchanged")
        hashes = entry.get("text_sha256_utf16le")
        require(isinstance(hashes, Mapping), f"{entry_id}: audit text hash record missing")
        require(hashes.get("current_ko") == text_hash(baseline), f"{entry_id}: audit baseline hash drift")
        require(hashes.get("proposed_ko") == text_hash(target), f"{entry_id}: audit proposal hash drift")
        audit_helper.assert_colour_layout(target, entry_id)
        require(
            audit_helper.control_signature(target) == audit_helper.control_signature(baseline),
            f"{entry_id}: audit protected signature drift",
        )
        expected_layout = entry.get("proposed_layout")
        require(isinstance(expected_layout, Mapping), f"{entry_id}: audit proposed layout missing")
        actual_layout = audit_helper.layout_record(entry_id, target, strict_texts, reservations)
        require(actual_layout == expected_layout, f"{entry_id}: audit Static007 layout drift")
        policy = entry.get("review_policy")
        require(isinstance(policy, Mapping) and policy.get("sentence_shortened_or_deleted") is False, f"{entry_id}: shortening policy drift")
    return report, by_id


def build_bundle(require_output_profile: bool) -> tuple[bytes, dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    audit_helper = load_audit_module()
    _strict_packed, header, raw, strict_texts, strict_profile, strict_records = load_strict_input()
    report, by_id = load_pinned_audit(audit_helper, strict_texts, strict_profile)
    reservations = audit_helper.read_reservations()

    output_texts = list(strict_texts)
    rows: list[dict[str, Any]] = []
    for entry_id in APPLIED_IDS:
        audit_entry = by_id[entry_id]
        baseline = strict_texts[entry_id]
        target = str(audit_entry["proposed_ko"])
        output_texts[entry_id] = target
        baseline_signature = audit_helper.control_signature(baseline)
        target_signature = audit_helper.control_signature(target)
        require(baseline_signature == target_signature, f"{entry_id}: protected signature drift")
        direct_sources = audit_entry.get("direct_pc_sources")
        require(isinstance(direct_sources, Mapping), f"{entry_id}: direct PC source record missing")
        direct_jp = direct_sources.get("jp")
        require(isinstance(direct_jp, str), f"{entry_id}: direct PC JP source missing")
        require(
            baseline_signature == audit_helper.control_signature(direct_jp),
            f"{entry_id}: direct PC JP protected signature drift",
        )
        layout = audit_helper.layout_record(entry_id, target, strict_texts, reservations)
        require(layout == audit_entry["proposed_layout"], f"{entry_id}: proposal layout differs from pinned audit")
        require(layout["line_count"] <= 4, f"{entry_id}: line count exceeds four")
        require(layout["all_lines_pass_static_patch_007"] is True, f"{entry_id}: Static007 layout failure")
        runtime_tokens = target_signature["runtime_tokens"]
        if entry_id in RUNTIME_RESERVATION_IDS:
            require(runtime_tokens == ["[bm1251]"], f"{entry_id}: runtime token scope drift")
            runtime_items = [
                item
                for line in layout["lines"]
                for item in line["runtime_reservations"]
            ]
            require(len(runtime_items) == 1, f"{entry_id}: runtime reservation count drift")
            require(runtime_items[0]["runtime_proven"] is False, f"{entry_id}: runtime proof overstated")
        else:
            require(runtime_tokens == [], f"{entry_id}: unexpected runtime token")
        rows.append(
            {
                "entry_id": entry_id,
                "change_type": audit_entry["change_type"],
                "review_judgement": audit_entry["review_judgement"],
                "source_basis": audit_entry["source_basis"],
                "baseline_ko": baseline,
                "proposed_ko": target,
                "baseline_ko_utf16le_sha256": text_hash(baseline),
                "proposed_ko_utf16le_sha256": text_hash(target),
                "direct_pc_sources": dict(direct_sources),
                "direct_pc_source_utf16le_sha256": {
                    language: text_hash(value)
                    for language, value in direct_sources.items()
                    if isinstance(language, str) and isinstance(value, str)
                },
                "control_signature": {
                    "baseline": baseline_signature,
                    "proposed": target_signature,
                    "direct_pc_jp": audit_helper.control_signature(direct_jp),
                },
                "layout": layout,
                "runtime_token_policy": {
                    "runtime_tokens": runtime_tokens,
                    "runtime_proven": False,
                    "prefix_semantics_inferred": False,
                    "strict_full_name_reservation_preserved_from_pinned_audit": entry_id in RUNTIME_RESERVATION_IDS,
                },
                "korean_sentence_shortened_or_deleted": False,
                "japanese_source_line_breaks_reused": False,
            }
        )

    rebuilt_raw = rebuild_message_table(parse_message_table(raw), tuple(output_texts))
    event = recompress_wrapper(rebuilt_raw, header)
    _candidate_header, reparsed_raw = decompress_wrapper(event)
    reparsed_table = parse_message_table(reparsed_raw)
    require(reparsed_raw == rebuilt_raw, "candidate raw reparse drift")
    require(tuple(reparsed_table.texts) == tuple(output_texts), "candidate text reparse drift")
    changed_ids = [entry_id for entry_id, (before, after) in enumerate(zip(strict_texts, output_texts)) if before != after]
    require(changed_ids == list(APPLIED_IDS), f"candidate diff scope drift: {changed_ids}")
    event_profile = profile(event, rebuilt_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "output profile has not been pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "deterministic candidate output profile drift")

    source_audit = {
        "report": file_record(AUDIT_REPORT),
        "builder": file_record(AUDIT_SCRIPT),
        "proposal_rows_used_without_reauthoring": list(APPLIED_IDS),
        "audit_static_high_confidence_ids": report["coverage"]["static_high_confidence_ids"],
        "audit_runtime_reservation_ids": report["coverage"]["runtime_reservation_proposal_ids"],
        "audit_target_range_identical_between_wave100_and_wave101": report["scope"][
            "target_range_identical_between_wave100_and_wave101"
        ],
    }
    static_patch_007_layout = {
        "runtime_font_px": 30,
        "runtime_line_spacing_setting": 8,
        "runtime_usable_line_width_px": 912,
        "max_lines": 4,
        "raw_g1n_full_width_advance_px": 48,
        "raw_g1n_half_width_advance_px": 24,
        "raw_g1n_pass_limit_px": 1440,
        "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
        "effective_width_pass_limit_px": 912,
        "runtime_token_reservation": "Use the pinned audit's strict full-name reservation; runtime prefix semantics are not inferred and runtime_proven remains false.",
    }
    coverage = {
        "audit_static_high_confidence_ids": list(APPLIED_IDS),
        "applied_row_ids": list(APPLIED_IDS),
        "applied_row_count": len(APPLIED_IDS),
        "outside_w101_changed_row_ids": [],
        "runtime_reservation_ids": list(RUNTIME_RESERVATION_IDS),
        "all_rows_static_patch_007_pass": True,
        "all_rows_four_or_fewer_lines": True,
        "all_rows_sentence_shortened_or_deleted_false": True,
        "unresolved_runtime_hold_ids": [],
    }
    audit = {
        "schema": SCHEMA + ".audit",
        "candidate_only": True,
        "resource": RESOURCE.as_posix(),
        "strict_input": {
            "workstream": STRICT_WORKSTREAM,
            "candidate_relative": relative(STRICT_ROOT),
            "event_relative": relative(STRICT_EVENT),
            "event_profile": strict_profile,
            **strict_records,
        },
        "source_takeda_hikotsuru_audit": source_audit,
        "static_patch_007_layout": static_patch_007_layout,
        "coverage": coverage,
        "output_event_profile": event_profile,
        "rows": rows,
        "policy": {
            "audit_report_proposed_ko_used_without_reauthoring": True,
            "direct_pc_jp_en_sc_tc_evidence_retained_from_pinned_audit": True,
            "switch_translation_used": False,
            "japanese_source_line_breaks_not_reused": True,
            "sentence_shortening_or_deletion_allowed": False,
            "tag_internal_line_break_allowed": False,
            "steam_game_resource_written": False,
            "git_operation_performed": False,
            "release_published": False,
            "network_operation_performed": False,
        },
    }
    public_audit = {
        "schema": SCHEMA + ".public-audit",
        "candidate_only": True,
        "resource": RESOURCE.as_posix(),
        "strict_input": audit["strict_input"],
        "source_takeda_hikotsuru_audit": source_audit,
        "static_patch_007_layout": static_patch_007_layout,
        "coverage": coverage,
        "output_event_profile": event_profile,
        "rows": rows,
        "policy": audit["policy"],
    }
    manifest = {
        "schema": SCHEMA + ".manifest",
        "candidate_only": True,
        "candidate_output_must_be_under": relative(TMP_ROOT),
        "resource": RESOURCE.as_posix(),
        "strict_input": audit["strict_input"],
        "source_takeda_hikotsuru_audit": source_audit,
        "applied_row_ids": list(APPLIED_IDS),
        "output": event_profile,
        "public_audit": {
            "relative_path": relative(PUBLIC_AUDIT),
            "sha256": digest(canonical_json(public_audit)),
        },
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
        "network_operation_performed": False,
    }
    validation = {
        "schema": SCHEMA + ".validation",
        "status": "PASS",
        "strict_input_workstream": STRICT_WORKSTREAM,
        "source_audit_report_sha256": source_audit["report"]["sha256"],
        "applied_row_ids": list(APPLIED_IDS),
        "applied_row_count": len(APPLIED_IDS),
        "outside_w101_changed_row_ids": [],
        "runtime_reservation_ids": list(RUNTIME_RESERVATION_IDS),
        "all_rows_static_patch_007_pass": True,
        "all_rows_four_or_fewer_lines": True,
        "all_rows_sentence_shortened_or_deleted_false": True,
        "output_event_profile": event_profile,
        "candidate_only": True,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
        "network_operation_performed": False,
    }
    return event, audit, manifest, public_audit, validation


def require_private(path: Path) -> Path:
    resolved = path.resolve()
    root = TMP_ROOT.resolve()
    require(resolved.is_relative_to(root), f"candidate path escapes private tmp root: {resolved}")
    return resolved


def write_artifacts(
    event: bytes,
    audit: Mapping[str, Any],
    manifest: Mapping[str, Any],
    public_audit: Mapping[str, Any],
    validation: Mapping[str, Any],
) -> Path:
    root = require_private(CANDIDATE_ROOT)
    if root.exists():
        shutil.rmtree(root)
    (root / RESOURCE).parent.mkdir(parents=True, exist_ok=True)
    (root / RESOURCE).write_bytes(event)
    (root / "audit.v1.json").write_bytes(canonical_json(audit))
    (root / "candidate_manifest.v1.json").write_bytes(canonical_json(manifest))
    PUBLIC.mkdir(parents=True, exist_ok=True)
    PUBLIC_AUDIT.write_bytes(canonical_json(public_audit))
    VALIDATION.write_bytes(canonical_json(validation))
    return root


def verify_private_candidate() -> dict[str, Any]:
    event, audit, manifest, public_audit, validation = build_bundle(require_output_profile=True)
    root = require_private(CANDIDATE_ROOT)
    require(root.is_dir(), "private candidate missing")
    expected_files = {RESOURCE.as_posix(), "audit.v1.json", "candidate_manifest.v1.json"}
    require(candidate_files(root) == expected_files, "private candidate file scope drift")
    require((root / RESOURCE).read_bytes() == event, "private event differs from deterministic build")
    require((root / "audit.v1.json").read_bytes() == canonical_json(audit), "private audit differs from deterministic build")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(manifest), "private manifest differs from deterministic build")
    require(PUBLIC_AUDIT.is_file(), "public audit missing")
    require(PUBLIC_AUDIT.read_bytes() == canonical_json(public_audit), "public audit differs from deterministic build")
    require(VALIDATION.is_file(), "validation missing")
    require(VALIDATION.read_bytes() == canonical_json(validation), "validation differs from deterministic build")
    return {
        "status": "PASS",
        "candidate_root": relative(root),
        "event_profile": audit["output_event_profile"],
        "applied_row_count": len(APPLIED_IDS),
        "applied_row_ids": list(APPLIED_IDS),
        "outside_w101_changed_row_ids": [],
        "runtime_reservation_ids": list(RUNTIME_RESERVATION_IDS),
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
        "network_operation_performed": False,
    }


def source_whitespace_check() -> None:
    for path in (
        SCRIPT,
        WORKSTREAM / "README_KO.md",
        WORKSTREAM / "test_pc_event_takeda_hikotsuru_quality_wave102_v1.py",
    ):
        require(path.is_file(), f"authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-guard"))
    command = parser.parse_args().command
    source_whitespace_check()
    if command == "profile":
        _event, audit, _manifest, _public_audit, _validation = build_bundle(require_output_profile=False)
        print(json.dumps(audit["output_event_profile"], ensure_ascii=False, sort_keys=True))
        return 0
    if command == "build":
        require(EXPECTED_OUTPUT_PROFILE is not None, "output profile has not been pinned")
        event, audit, manifest, public_audit, validation = build_bundle(require_output_profile=True)
        print(relative(write_artifacts(event, audit, manifest, public_audit, validation)))
        return 0
    if command == "verify-private":
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, sort_keys=True))
        return 0
    _event, audit, _manifest, _public_audit, _validation = build_bundle(require_output_profile=True)
    print(
        json.dumps(
            {
                "strict_input": audit["strict_input"]["event_profile"],
                "output": audit["output_event_profile"],
                "applied_row_ids": audit["coverage"]["applied_row_ids"],
                "outside_w101_changed_row_ids": audit["coverage"]["outside_w101_changed_row_ids"],
                "runtime_reservation_ids": audit["coverage"]["runtime_reservation_ids"],
                "candidate_only": audit["candidate_only"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Wave102Error, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
