#!/usr/bin/env python3
"""Build the private Wave 101 Kanto event quality candidate.

Only the fifteen static-high-confidence proposal rows from the reviewed Kanto
audit are applied.  The input is the pinned Wave 100 private candidate; direct
PC JP/EN/SC/TC resources are read-only validation evidence.  Output is limited
to this workstream's private ``tmp`` candidate and never touches Steam, Git,
release, or network state.
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
RESOURCE = Path("MSG_PK") / "JP" / "msgev.bin"
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.pc-event-kanto-quality-wave101.v1"
ROW_COUNT = 17_916
APPLIED_IDS = (3489, 3490, 3491, 3493, 3497, 3500, 3502, 3505, 3506, 3508, 3510, 3514, 3516, 3522, 3526)
RUNTIME_RESERVATION_IDS = (3514, 3522, 3526)

STRICT_WORKSTREAM = "pc_event_ending_regions_quality_wave100_v1"
STRICT_ROOT = REPO / "tmp" / STRICT_WORKSTREAM / "candidate-final"
STRICT_EVENT = STRICT_ROOT / RESOURCE
STRICT_AUDIT = STRICT_ROOT / "audit.v1.json"
STRICT_MANIFEST = STRICT_ROOT / "candidate_manifest.v1.json"
EXPECTED_STRICT_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "F7DB831E850F191CC6320E54BF878DCC8B7F3DC4F5D51AD66379D64617F553ED",
    "raw_size": 1_043_924,
    "sha256": "245043679E4A7A75628519829C1B16372A8FD085A1CC7F0F4EE97F52BB66BA60",
    "size": 1_048_043,
}
EXPECTED_STRICT_AUDIT_SHA256 = "8753762BDD868EBFBBDDA4E0D806D165B95462AC855C8FE683E6E1BE01741C30"
EXPECTED_STRICT_MANIFEST_SHA256 = "78989313D5A44A562173618F2F44C77368BBF55A3F6CC3B26BA10AE4338FE931"

KANTO_AUDIT_WORKSTREAM = REPO / "workstreams" / "pc_event_kanto_audit_v1"
KANTO_AUDIT_SCRIPT = KANTO_AUDIT_WORKSTREAM / "build_pc_event_kanto_audit_v1.py"
KANTO_AUDIT_REPORT = KANTO_AUDIT_WORKSTREAM / "public" / "pc_event_kanto_audit.v1.json"
EXPECTED_KANTO_AUDIT_SCRIPT_SHA256 = "29BB347949223FC9038B7CF4EC5F3F2FEE48C8A4F2CC04E657F3A26E2E83E37D"
EXPECTED_KANTO_AUDIT_REPORT_SHA256 = "B14AD40DFB766044EAA1DF26FFD8F784CD86B26EB18E03B0F41F6E66E1A0A5B0"

STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
SOURCES: Mapping[str, tuple[Path, Mapping[str, Any]]] = {
    "jp": (
        STEAM_ROOT
        / "KR_PATCH_BACKUP"
        / "file_only_transaction"
        / "steam-jp-1.1.7-v0.6.0"
        / "originals"
        / "MSG_PK"
        / "JP"
        / "msgev.bin",
        {
            "raw_sha256": "07D7512BE0235753FC7BB0C7C548B61F471D9CDED01379E63B8AF8EAE013813E",
            "raw_size": 894_800,
            "sha256": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
            "size": 562_226,
        },
    ),
    "en": (
        STEAM_ROOT / "MSG_PK" / "EN" / "msgev.bin",
        {
            "raw_sha256": "6A1F3891412EBFF5AC3188F498C9951431154192D69E82B7ABB6F25AA934D911",
            "raw_size": 1_878_836,
            "sha256": "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E",
            "size": 762_196,
        },
    ),
    "sc": (
        STEAM_ROOT / "MSG_PK" / "SC" / "msgev.bin",
        {
            "raw_sha256": "3ACE267E6B9774D8C940C9D7940F168B61744ADDF7C082F2CB1EA7E9BBD82B5E",
            "raw_size": 754_708,
            "sha256": "7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA",
            "size": 522_177,
        },
    ),
    "tc": (
        STEAM_ROOT / "MSG_PK" / "TC" / "msgev.bin",
        {
            "raw_sha256": "42DC893AA9FF9D3E7B75FBCFFBEFD7C3DFC338CAB71E942C081BDC52C9024BF6",
            "raw_size": 744_212,
            "sha256": "89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6",
            "size": 524_909,
        },
    ),
}

# Deterministic output from the pinned W100 input and the 15 audited proposal
# rows.  Keeping this exact pin prevents accidental proposal/source drift.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "507F8FB7CF75D327F8CC88725E17BE3DA1084C4BD96237B9F1A1E8CE5F9D3B41",
    "raw_size": 1_043_960,
    "sha256": "96DBB584AE96157E3B7013CAF86A4876CDB0B87EFF66433CB9236206996C2D91",
    "size": 1_048_079,
}


class Wave101Error(RuntimeError):
    """Raised when strict input, audit provenance, or candidate output drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave101Error(message)


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


def load_table(path: Path, expected: Mapping[str, Any], label: str) -> tuple[bytes, Any, bytes, tuple[str, ...], dict[str, Any]]:
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
    require(KANTO_AUDIT_SCRIPT.is_file(), f"Kanto audit script missing: {KANTO_AUDIT_SCRIPT}")
    require(digest(KANTO_AUDIT_SCRIPT.read_bytes()) == EXPECTED_KANTO_AUDIT_SCRIPT_SHA256, "Kanto audit script hash drift")
    spec = importlib.util.spec_from_file_location("pc_event_kanto_audit_wave101_helper", KANTO_AUDIT_SCRIPT)
    require(spec is not None and spec.loader is not None, "cannot load Kanto audit helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_strict_input() -> tuple[bytes, Any, bytes, tuple[str, ...], dict[str, Any], dict[str, Any]]:
    root = STRICT_ROOT.resolve(strict=True)
    require(root.is_relative_to((REPO / "tmp").resolve()), "strict input escapes private tmp")
    expected_files = {RESOURCE.as_posix(), "audit.v1.json", "candidate_manifest.v1.json"}
    require(candidate_files(root) == expected_files, "strict input candidate scope drift")
    packed, header, raw, texts, packed_profile = load_table(STRICT_EVENT, EXPECTED_STRICT_PROFILE, "Wave 100 strict input")
    audit_record = file_record(STRICT_AUDIT)
    manifest_record = file_record(STRICT_MANIFEST)
    require(audit_record["sha256"] == EXPECTED_STRICT_AUDIT_SHA256, "Wave 100 audit hash drift")
    require(manifest_record["sha256"] == EXPECTED_STRICT_MANIFEST_SHA256, "Wave 100 manifest hash drift")
    audit = json.loads(STRICT_AUDIT.read_text(encoding="utf-8"))
    manifest = json.loads(STRICT_MANIFEST.read_text(encoding="utf-8"))
    require(audit.get("candidate_only") is True, "Wave 100 audit is not private")
    require(manifest.get("candidate_only") is True, "Wave 100 manifest is not private")
    require(audit.get("output_event_profile") == packed_profile, "Wave 100 audit profile drift")
    require(manifest.get("output") == packed_profile, "Wave 100 manifest profile drift")
    return packed, header, raw, texts, packed_profile, {"audit": audit_record, "candidate_manifest": manifest_record}


def load_kanto_report(audit_helper: Any, strict_texts: tuple[str, ...], strict_profile: Mapping[str, Any]) -> tuple[dict[str, Any], dict[int, Mapping[str, Any]]]:
    require(KANTO_AUDIT_REPORT.is_file(), f"Kanto audit report missing: {KANTO_AUDIT_REPORT}")
    require(digest(KANTO_AUDIT_REPORT.read_bytes()) == EXPECTED_KANTO_AUDIT_REPORT_SHA256, "Kanto audit report hash drift")
    report = json.loads(KANTO_AUDIT_REPORT.read_text(encoding="utf-8"))
    require(report.get("schema") == "nobu16.kr.pc-event-kanto-audit.v1", "Kanto audit schema drift")
    scope = report.get("scope")
    coverage = report.get("coverage")
    entries = report.get("entries")
    require(isinstance(scope, Mapping) and isinstance(coverage, Mapping) and isinstance(entries, list), "Kanto audit structure drift")
    require(scope.get("resource") == RESOURCE.as_posix(), "Kanto audit resource drift")
    require(scope.get("target_ids") == list(range(3485, 3527)), "Kanto audit scope drift")
    require(scope.get("wave100_rebase_range_identical_to_wave98") is True, "Kanto audit W100 rebase guard missing")
    source_profile = report.get("sources", {}).get("strict_korean_input", {})
    require(isinstance(source_profile, Mapping), "Kanto audit strict profile missing")
    require(source_profile.get("packed_sha256") == strict_profile["sha256"], "Kanto audit strict packed hash drift")
    require(source_profile.get("raw_sha256") == strict_profile["raw_sha256"], "Kanto audit strict raw hash drift")
    require(coverage.get("static_high_confidence_ids") == list(APPLIED_IDS), "Kanto audit applied scope drift")
    require(coverage.get("static_high_confidence_count") == len(APPLIED_IDS), "Kanto audit count drift")
    require(coverage.get("runtime_reservation_proposal_ids") == list(RUNTIME_RESERVATION_IDS), "Kanto runtime proposal scope drift")
    require(coverage.get("runtime_or_ui_hold_ids") == [], "unresolved Kanto runtime/UI holds")
    by_id = {entry.get("entry_id"): entry for entry in entries if isinstance(entry, Mapping)}
    require(len(by_id) == 42 and all(entry_id in by_id for entry_id in range(3485, 3527)), "Kanto audit row topology drift")
    for entry_id in APPLIED_IDS:
        entry = by_id[entry_id]
        require(entry.get("review_status") == "static_high_confidence", f"{entry_id}: audit status drift")
        require(entry.get("changed_in_this_audit") is True, f"{entry_id}: audit change flag drift")
        current = entry.get("current_ko")
        target = entry.get("proposed_ko")
        require(isinstance(current, str) and isinstance(target, str), f"{entry_id}: audit Korean text missing")
        require(current == strict_texts[entry_id], f"{entry_id}: audit current Korean no longer matches W100")
        require(current != target, f"{entry_id}: audit target is unchanged")
        hashes = entry.get("text_sha256_utf16le")
        require(isinstance(hashes, Mapping), f"{entry_id}: audit text hash record missing")
        require(hashes.get("current_ko") == text_hash(current), f"{entry_id}: audit current hash drift")
        require(hashes.get("proposed_ko") == text_hash(target), f"{entry_id}: audit proposal hash drift")
        audit_helper.assert_colour_layout(target, entry_id)
        require(audit_helper.control_signature(target) == audit_helper.control_signature(current), f"{entry_id}: audit protected signature drift")
        expected_layout = entry.get("proposed_layout")
        require(isinstance(expected_layout, Mapping), f"{entry_id}: audit proposed layout missing")
        actual_layout = audit_helper.layout_record(entry_id, target, strict_texts, audit_helper.read_reservations())
        require(actual_layout == expected_layout, f"{entry_id}: audit Static007 layout drift")
        policy = entry.get("review_policy")
        require(isinstance(policy, Mapping) and policy.get("sentence_shortened_or_deleted") is False, f"{entry_id}: shortening policy drift")
    return report, by_id


def load_sources() -> dict[str, tuple[tuple[str, ...], dict[str, Any]]]:
    loaded: dict[str, tuple[tuple[str, ...], dict[str, Any]]] = {}
    for language, (path, expected) in SOURCES.items():
        _packed, _header, _raw, texts, measured = load_table(path, expected, f"direct PC {language.upper()}")
        loaded[language] = (texts, measured)
    return loaded


def build_bundle(require_output_profile: bool) -> tuple[bytes, dict[str, Any], dict[str, Any]]:
    audit_helper = load_audit_module()
    _strict_packed, header, raw, strict_texts, strict_profile, strict_records = load_strict_input()
    report, by_id = load_kanto_report(audit_helper, strict_texts, strict_profile)
    sources = load_sources()
    require(all(len(texts) == len(strict_texts) for texts, _profile in sources.values()), "direct source topology drift")

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
        direct_sources = {language: texts[entry_id] for language, (texts, _profile) in sources.items()}
        require(baseline_signature == audit_helper.control_signature(direct_sources["jp"]), f"{entry_id}: direct JP protected signature drift")
        for language, value in direct_sources.items():
            expected_value = audit_entry["direct_pc_sources"].get(language)
            require(value == expected_value, f"{entry_id}: direct PC {language.upper()} source drift from audit")
        layout = audit_helper.layout_record(entry_id, target, strict_texts, audit_helper.read_reservations())
        require(layout == audit_entry["proposed_layout"], f"{entry_id}: proposal layout differs from approved audit")
        require(layout["line_count"] <= 4, f"{entry_id}: line count exceeds four")
        require(layout["all_lines_pass_static_patch_007"] is True, f"{entry_id}: Static007 layout failure")
        runtime_tokens = target_signature["runtime_tokens"]
        if entry_id in RUNTIME_RESERVATION_IDS:
            require(runtime_tokens, f"{entry_id}: expected runtime token absent")
            for line in layout["lines"]:
                for reservation in line["runtime_reservations"]:
                    require(reservation["runtime_proven"] is False, f"{entry_id}: runtime proof overstated")
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
                "direct_pc_sources": direct_sources,
                "direct_pc_source_utf16le_sha256": {language: text_hash(value) for language, value in direct_sources.items()},
                "control_signature": {
                    "baseline": baseline_signature,
                    "proposed": target_signature,
                    "direct_pc_jp": audit_helper.control_signature(direct_sources["jp"]),
                },
                "layout": layout,
                "runtime_token_policy": {
                    "runtime_tokens": runtime_tokens,
                    "runtime_proven": False,
                    "prefix_semantics_inferred": False,
                    "strict_full_name_reservation_preserved_from_kanto_audit": entry_id in RUNTIME_RESERVATION_IDS,
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
        "source_kanto_audit": {
            "report": file_record(KANTO_AUDIT_REPORT),
            "builder": file_record(KANTO_AUDIT_SCRIPT),
            "proposal_rows_used_without_reauthoring": list(APPLIED_IDS),
            "wave100_rebase_range_identical_to_wave98": report["scope"]["wave100_rebase_range_identical_to_wave98"],
        },
        "direct_pc_source_resources": {
            language: {
                "path": str(SOURCES[language][0]),
                "profile": source_profile,
            }
            for language, (_texts, source_profile) in sources.items()
        },
        "static_patch_007_layout": {
            "runtime_font_px": 30,
            "runtime_line_spacing_setting": 8,
            "runtime_usable_line_width_px": 912,
            "max_lines": 4,
            "raw_g1n_full_width_advance_px": 48,
            "raw_g1n_half_width_advance_px": 24,
            "raw_g1n_pass_limit_px": 1440,
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "effective_width_pass_limit_px": 912,
            "runtime_token_reservation": "Use the audit's strict full-name reservation; runtime prefix semantics are not inferred and runtime_proven remains false.",
        },
        "coverage": {
            "audited_scope_ids": report["scope"]["target_ids"],
            "applied_row_ids": list(APPLIED_IDS),
            "applied_row_count": len(APPLIED_IDS),
            "runtime_reservation_ids": list(RUNTIME_RESERVATION_IDS),
            "all_rows_static_patch_007_pass": True,
            "all_rows_four_or_fewer_lines": True,
            "all_rows_sentence_shortened_or_deleted_false": True,
            "unresolved_runtime_hold_ids": [],
        },
        "output_event_profile": event_profile,
        "rows": rows,
        "policy": {
            "audit_report_proposed_ko_used_without_reauthoring": True,
            "direct_pc_jp_en_sc_tc_used_as_read_only_evidence": True,
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
    manifest = {
        "schema": SCHEMA + ".manifest",
        "candidate_only": True,
        "candidate_output_must_be_under": relative(TMP_ROOT),
        "resource": RESOURCE.as_posix(),
        "strict_input": audit["strict_input"],
        "source_kanto_audit": audit["source_kanto_audit"],
        "applied_row_ids": list(APPLIED_IDS),
        "output": event_profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
        "network_operation_performed": False,
    }
    return event, audit, manifest


def require_private(path: Path) -> Path:
    resolved = path.resolve()
    root = TMP_ROOT.resolve()
    require(resolved.is_relative_to(root), f"candidate path escapes private tmp root: {resolved}")
    return resolved


def write_candidate(event: bytes, audit: Mapping[str, Any], manifest: Mapping[str, Any]) -> Path:
    root = require_private(CANDIDATE_ROOT)
    if root.exists():
        shutil.rmtree(root)
    (root / RESOURCE).parent.mkdir(parents=True, exist_ok=True)
    (root / RESOURCE).write_bytes(event)
    (root / "audit.v1.json").write_bytes(canonical_json(audit))
    (root / "candidate_manifest.v1.json").write_bytes(canonical_json(manifest))
    return root


def verify_private_candidate() -> dict[str, Any]:
    event, audit, manifest = build_bundle(require_output_profile=True)
    root = require_private(CANDIDATE_ROOT)
    require(root.is_dir(), "private candidate missing")
    expected_files = {RESOURCE.as_posix(), "audit.v1.json", "candidate_manifest.v1.json"}
    require(candidate_files(root) == expected_files, "private candidate file scope drift")
    require((root / RESOURCE).read_bytes() == event, "private event differs from deterministic build")
    require((root / "audit.v1.json").read_bytes() == canonical_json(audit), "private audit differs from deterministic build")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(manifest), "private manifest differs from deterministic build")
    return {
        "status": "PASS",
        "candidate_root": relative(root),
        "event_profile": audit["output_event_profile"],
        "applied_row_count": len(APPLIED_IDS),
        "applied_row_ids": list(APPLIED_IDS),
        "runtime_reservation_ids": list(RUNTIME_RESERVATION_IDS),
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
        "network_operation_performed": False,
    }


def source_whitespace_check() -> None:
    for path in (SCRIPT, WORKSTREAM / "README_KO.md", WORKSTREAM / "test_pc_event_kanto_quality_wave101_v1.py"):
        require(path.is_file(), f"authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    source_whitespace_check()
    if command == "profile":
        _event, audit, _manifest = build_bundle(require_output_profile=False)
        print(json.dumps(audit["output_event_profile"], ensure_ascii=False, sort_keys=True))
        return 0
    if command == "build":
        require(EXPECTED_OUTPUT_PROFILE is not None, "output profile has not been pinned")
        event, audit, manifest = build_bundle(require_output_profile=True)
        print(relative(write_candidate(event, audit, manifest)))
        return 0
    if command == "verify-private":
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, sort_keys=True))
        return 0
    _event, audit, _manifest = build_bundle(require_output_profile=True)
    print(
        json.dumps(
            {
                "strict_input": audit["strict_input"]["event_profile"],
                "output": audit["output_event_profile"],
                "applied_row_ids": audit["coverage"]["applied_row_ids"],
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
    except (Wave101Error, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
