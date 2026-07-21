#!/usr/bin/env python3
"""Build the private Wave100 ending-region event quality candidate.

Only the six static, source-backed proposals accepted in the ending-region
audit are applied to the strict W98 Korean candidate.  This builder writes a
candidate below ``tmp`` only; it never writes the Steam installation, Git,
release, or network state.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
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


SCHEMA = "nobu16.kr.pc-event-ending-regions-quality-wave100.v1"
ROW_COUNT = 17_916
STRICT_WORKSTREAM = "pc_event_gifu_quality_wave98_v1"
STRICT_ROOT = REPO / "tmp" / STRICT_WORKSTREAM / "candidate-final"
STRICT_EVENT = STRICT_ROOT / RESOURCE
STRICT_AUDIT = STRICT_ROOT / "audit.v1.json"
STRICT_MANIFEST = STRICT_ROOT / "candidate_manifest.v1.json"
EXPECTED_STRICT_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "D0FAB9C303F8F456184DCDD89AC929C675D6528080F8C29E419E1249BD9B7408",
    "raw_size": 1_043_932,
    "sha256": "62C7F55506DB59A43761DDCE07FB5DA4175AD0AC4B68C03507B37AD52E2AEBD3",
    "size": 1_048_051,
}

AUDIT_REPORT = REPO / "workstreams" / "pc_event_ending_regions_audit_v1" / "public" / "pc_event_ending_regions_audit.v1.json"
AUDIT_REPORT_EXPECTED_SHA256 = "4425E976A1FDBD524ABD0C9A2B3C8613DBA43AA26F65867FF54A38B3A6CB6A68"
AUDIT_SCHEMA = "nobu16.kr.pc-event-ending-regions-audit.v1"
TARGET_IDS = (3_331, 3_413, 3_446, 3_475, 3_477, 3_479)

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

METRICS_HELPER_PATH = (
    REPO
    / "workstreams"
    / "pc_event_manual_compact_static007_batch01_v1"
    / "build_pc_event_manual_compact_static007_batch01_v1.py"
)

EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "F7DB831E850F191CC6320E54BF878DCC8B7F3DC4F5D51AD66379D64617F553ED",
    "raw_size": 1_043_924,
    "sha256": "245043679E4A7A75628519829C1B16372A8FD085A1CC7F0F4EE97F52BB66BA60",
    "size": 1_048_043,
}


class Wave100Error(RuntimeError):
    """Raised when source evidence, layout, or private-candidate scope drifts."""


@dataclass(frozen=True)
class LoadedTable:
    packed: bytes
    raw: bytes
    header: Any
    texts: tuple[str, ...]
    profile: Mapping[str, Any]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave100Error(message)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError:
        return str(path)


def file_record(path: Path) -> Mapping[str, Any]:
    blob = path.read_bytes()
    return {"relative_path": relative(path), "sha256": sha256(blob), "size": len(blob)}


def profile(packed: bytes, raw: bytes) -> Mapping[str, Any]:
    return {
        "raw_sha256": sha256(raw),
        "raw_size": len(raw),
        "sha256": sha256(packed),
        "size": len(packed),
    }


def candidate_files(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}


def load_table(path: Path, expected: Mapping[str, Any], label: str) -> LoadedTable:
    require(path.is_file(), f"{label}: file missing: {path}")
    packed = path.read_bytes()
    header, raw = decompress_wrapper(packed)
    parsed = parse_message_table(raw)
    texts = tuple(parsed.texts)
    require(len(texts) == ROW_COUNT, f"{label}: row count drift: {len(texts)}")
    require(rebuild_message_table(parsed, texts) == raw, f"{label}: message-table round-trip drift")
    measured = profile(packed, raw)
    require(measured == expected, f"{label}: packed/raw profile drift")
    return LoadedTable(packed=packed, raw=raw, header=header, texts=texts, profile=measured)


def load_module(name: str, path: Path) -> Any:
    require(path.is_file(), f"metrics helper missing: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import metrics helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


metrics = load_module("pc_event_ending_regions_wave100_metrics", METRICS_HELPER_PATH)


def ids_hash(ids: Sequence[int]) -> str:
    return sha256(",".join(str(entry_id) for entry_id in ids).encode("ascii"))


def layout_record(value: str) -> Mapping[str, Any]:
    lines = list(metrics.line_metrics(value))
    require(1 <= len(lines) <= 4, f"line count outside 1..4: {len(lines)}")
    require(all(line["passes_static_patch_007"] for line in lines), "line fails Static Patch 007")
    return {
        "line_count": len(lines),
        "lines": lines,
        "max_raw_g1n_width_px": max(line["raw_g1n_width_px"] for line in lines),
        "max_effective_width_px": max(line["effective_width_px"] for line in lines),
        "over_912px": any(line["over_effective_912px"] for line in lines),
        "all_static_patch_007_lines_pass": all(line["passes_static_patch_007"] for line in lines),
    }


def load_strict_input() -> tuple[LoadedTable, Mapping[str, Any]]:
    root = STRICT_ROOT.resolve(strict=True)
    private_tmp = (REPO / "tmp").resolve()
    require(root.is_relative_to(private_tmp), "strict input escapes private tmp")
    expected_files = {RESOURCE.as_posix(), "audit.v1.json", "candidate_manifest.v1.json"}
    require(candidate_files(root) == expected_files, "strict input candidate file scope drift")
    table = load_table(STRICT_EVENT, EXPECTED_STRICT_PROFILE, "W98 strict Korean input")
    audit = json.loads(STRICT_AUDIT.read_text(encoding="utf-8"))
    manifest = json.loads(STRICT_MANIFEST.read_text(encoding="utf-8"))
    require(audit.get("candidate_only") is True, "strict input audit is not private")
    require(manifest.get("candidate_only") is True, "strict input manifest is not private")
    require(audit.get("output_event_profile") == table.profile, "strict input audit profile drift")
    require(manifest.get("output") == table.profile, "strict input manifest profile drift")
    return table, {
        "workstream": STRICT_WORKSTREAM,
        "candidate_relative": relative(root),
        "event_relative": relative(STRICT_EVENT),
        "event_profile": table.profile,
        "audit": file_record(STRICT_AUDIT),
        "candidate_manifest": file_record(STRICT_MANIFEST),
    }


def load_audit_targets() -> tuple[Mapping[int, Mapping[str, Any]], Mapping[str, Any]]:
    require(AUDIT_REPORT.is_file(), f"ending-region audit report missing: {AUDIT_REPORT}")
    blob = AUDIT_REPORT.read_bytes()
    require(sha256(blob) == AUDIT_REPORT_EXPECTED_SHA256, "ending-region audit report hash drift")
    report = json.loads(blob.decode("utf-8"))
    require(report.get("schema") == AUDIT_SCHEMA, "ending-region audit schema drift")
    scope = report.get("scope")
    require(isinstance(scope, Mapping), "ending-region audit scope missing")
    require(scope.get("strict_input_rebased_to") == "pc_event_gifu_quality_wave98_v1/candidate-final", "audit is not W98-rebased")
    require(scope.get("w98_target_rows_identical_to_pre_w98") is True, "audit target-range rebase proof missing")
    require(scope.get("start_id") == 3309 and scope.get("end_id") == 3484, "ending-region audit scope drift")
    entries = report.get("entries")
    require(isinstance(entries, list), "ending-region audit entries missing")
    by_id = {entry.get("entry_id"): entry for entry in entries if isinstance(entry, Mapping)}
    targets: dict[int, Mapping[str, Any]] = {}
    for entry_id in TARGET_IDS:
        entry = by_id.get(entry_id)
        require(isinstance(entry, Mapping), f"audit row missing: {entry_id}")
        require(entry.get("classification") == "static_high_confidence_correction", f"audit row not high confidence: {entry_id}")
        correction = entry.get("correction")
        require(isinstance(correction, Mapping), f"audit correction missing: {entry_id}")
        proposed = correction.get("proposed_ko")
        current = entry.get("current_ko")
        require(isinstance(proposed, str) and proposed, f"audit proposed Korean missing: {entry_id}")
        require(isinstance(current, str) and current, f"audit baseline Korean missing: {entry_id}")
        require(correction.get("control_signature_preserved") is True, f"audit control preservation missing: {entry_id}")
        require(correction.get("sentence_shortened_or_deleted") is False, f"audit shortening flag drift: {entry_id}")
        require(correction.get("japanese_linebreaks_copied") is False, f"audit JP-LF flag drift: {entry_id}")
        require(correction.get("tag_internal_linebreak_inserted") is False, f"audit tag-LF flag drift: {entry_id}")
        proposed_layout = correction.get("proposed_layout")
        require(isinstance(proposed_layout, Mapping), f"audit layout missing: {entry_id}")
        require(proposed_layout.get("all_lines_pass_static_patch_007") is True, f"audit layout failed: {entry_id}")
        require(proposed_layout.get("line_count") in (1, 2, 3, 4), f"audit line count drift: {entry_id}")
        sources = correction.get("direct_pc_sources_for_meaning_review")
        require(isinstance(sources, Mapping) and set(sources) == {"jp", "en", "sc", "tc"}, f"audit source evidence drift: {entry_id}")
        targets[entry_id] = {
            "baseline_ko": current,
            "target_ko": proposed,
            "rationale": entry.get("review_judgement"),
            "semantic_obligations": correction.get("semantic_obligations_preserved"),
            "audit_direct_sources": sources,
        }
    require(tuple(targets) == TARGET_IDS, "audit target order/scope drift")
    return targets, file_record(AUDIT_REPORT)


def load_direct_sources() -> tuple[Mapping[str, LoadedTable], Mapping[str, Any]]:
    tables: dict[str, LoadedTable] = {}
    records: dict[str, Any] = {}
    for language, (path, expected) in SOURCES.items():
        resolved = path.resolve(strict=True)
        require("switch" not in {part.casefold() for part in resolved.parts}, f"non-PC source forbidden: {resolved}")
        table = load_table(resolved, expected, f"direct PC {language.upper()} source")
        tables[language] = table
        records[language] = {"path": str(resolved), "profile": table.profile}
    require(tuple(sorted(tables)) == ("en", "jp", "sc", "tc"), "direct PC source set drift")
    return tables, records


def validate_target(target: str, baseline: str, entry_id: int) -> Mapping[str, Any]:
    require("\x00" not in target, f"{entry_id}: embedded terminator")
    metrics.assert_no_break_inside_tag(baseline)
    metrics.assert_no_break_inside_tag(target)
    before = metrics.control_signature(baseline)
    after = metrics.control_signature(target)
    require(before == after, f"{entry_id}: control/tag/token signature drift")
    require(not after["runtime_tokens"], f"{entry_id}: unexpected runtime token")
    require(not after["printf_tokens"], f"{entry_id}: unexpected printf token")
    require(after["unknown_percent_count"] == 0, f"{entry_id}: unknown percent token")
    require(not after["other_controls"], f"{entry_id}: unexpected control code")
    return layout_record(target)


def build_bundle(require_output_profile: bool) -> tuple[bytes, Mapping[str, Any], Mapping[str, Any], Mapping[str, Any]]:
    strict, strict_record = load_strict_input()
    targets, audit_report_record = load_audit_targets()
    sources, source_records = load_direct_sources()
    require(all(len(source.texts) == len(strict.texts) for source in sources.values()), "direct source topology drift")

    texts = list(strict.texts)
    rows: list[Mapping[str, Any]] = []
    for entry_id in TARGET_IDS:
        audit_target = targets[entry_id]
        baseline = str(audit_target["baseline_ko"])
        target = str(audit_target["target_ko"])
        require(strict.texts[entry_id] == baseline, f"{entry_id}: strict W98 Korean baseline drift")
        target_layout = validate_target(target, baseline, entry_id)
        audit_source_texts = audit_target["audit_direct_sources"]
        require(isinstance(audit_source_texts, Mapping), f"{entry_id}: audit source map invalid")
        direct_sources = {language: source.texts[entry_id] for language, source in sources.items()}
        require(direct_sources == audit_source_texts, f"{entry_id}: direct PC source evidence drift from audit")
        require(metrics.control_signature(baseline) == metrics.control_signature(direct_sources["jp"]), f"{entry_id}: strict KO/JP signature drift")
        texts[entry_id] = target
        rows.append(
            {
                "entry_id": entry_id,
                "changed": True,
                "strict_w98_ko": baseline,
                "target_ko": target,
                "strict_w98_ko_utf16le_sha256": text_hash(baseline),
                "target_ko_utf16le_sha256": text_hash(target),
                "direct_pc_sources": direct_sources,
                "direct_pc_source_utf16le_sha256": {
                    language: text_hash(value) for language, value in direct_sources.items()
                },
                "strict_and_target_control_signature": metrics.control_signature(target),
                "rationale_from_ending_region_audit": audit_target["rationale"],
                "semantic_obligations_preserved": audit_target["semantic_obligations"],
                "korean_sentence_shortened_or_deleted": False,
                "japanese_source_line_breaks_reused": False,
                "tag_internal_line_break_inserted": False,
                **target_layout,
            }
        )

    changed_ids = [entry_id for entry_id, (before, after) in enumerate(zip(strict.texts, texts)) if before != after]
    require(changed_ids == list(TARGET_IDS), f"changed-row scope drift: {changed_ids}")
    require(all(not row["over_912px"] for row in rows), "target layout exceeds 912px")
    require(all(row["line_count"] <= 4 for row in rows), "target layout exceeds four lines")
    require(all(not row["korean_sentence_shortened_or_deleted"] for row in rows), "shortening flag drift")

    raw = rebuild_message_table(parse_message_table(strict.raw), tuple(texts))
    event = recompress_wrapper(raw, strict.header)
    output_profile = profile(event, raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "output profile is not pinned")
        require(output_profile == EXPECTED_OUTPUT_PROFILE, "deterministic output profile drift")

    audit: Mapping[str, Any] = {
        "schema": SCHEMA + ".audit",
        "candidate_only": True,
        "resource": RESOURCE.as_posix(),
        "strict_input": strict_record,
        "source_ending_region_audit": audit_report_record,
        "direct_pc_source_resources": source_records,
        "static_patch_007_layout": {
            "runtime_font_px": 30,
            "runtime_usable_line_width_px": 912,
            "max_lines": 4,
            "raw_g1n_full_width_px": 48,
            "raw_g1n_half_width_px": 24,
            "raw_g1n_pass_limit_px": 1_440,
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "effective_width_pass_limit_px": 912,
        },
        "coverage": {
            "applied_row_ids": list(TARGET_IDS),
            "applied_row_count": len(TARGET_IDS),
            "applied_row_ids_sha256": ids_hash(TARGET_IDS),
            "all_rows_static_patch_007_pass": True,
            "all_rows_four_or_fewer_lines": True,
            "all_rows_sentence_shortened_or_deleted_false": True,
            "unresolved_runtime_hold_ids": [],
        },
        "output_event_profile": output_profile,
        "rows": rows,
        "policy": {
            "audit_report_proposed_ko_used_without_reauthoring": True,
            "direct_pc_jp_en_sc_tc_used_as_read_only_evidence": True,
            "japanese_source_line_breaks_not_reused": True,
            "sentence_shortening_or_deletion_allowed": False,
            "tag_internal_line_break_allowed": False,
            "steam_game_resource_written": False,
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
        "strict_input": strict_record,
        "source_ending_region_audit": audit_report_record,
        "applied_row_ids": list(TARGET_IDS),
        "output": output_profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
        "network_operation_performed": False,
    }
    return event, output_profile, audit, manifest


def require_private_candidate_root() -> Path:
    root = CANDIDATE_ROOT.resolve()
    tmp_root = TMP_ROOT.resolve()
    require(root.parent == tmp_root, f"candidate root is not direct child of private tmp root: {root}")
    require(root.is_relative_to((REPO / "tmp").resolve()), f"candidate root escapes tmp: {root}")
    return root


def write_candidate(event: bytes, audit: Mapping[str, Any], manifest: Mapping[str, Any]) -> Path:
    root = require_private_candidate_root()
    if root.exists():
        shutil.rmtree(root)
    (root / RESOURCE).parent.mkdir(parents=True, exist_ok=True)
    (root / RESOURCE).write_bytes(event)
    (root / "audit.v1.json").write_bytes(canonical_json(audit))
    (root / "candidate_manifest.v1.json").write_bytes(canonical_json(manifest))
    return root


def verify_private_candidate() -> Mapping[str, Any]:
    event, output_profile, audit, manifest = build_bundle(require_output_profile=True)
    root = require_private_candidate_root()
    require(root.is_dir(), "private candidate missing")
    expected_files = {RESOURCE.as_posix(), "audit.v1.json", "candidate_manifest.v1.json"}
    require(candidate_files(root) == expected_files, "private candidate file scope drift")
    require((root / RESOURCE).read_bytes() == event, "private event differs from deterministic build")
    require((root / "audit.v1.json").read_bytes() == canonical_json(audit), "private audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(manifest), "private manifest differs")
    return {
        "status": "PASS",
        "candidate_root": relative(root),
        "event_profile": output_profile,
        "applied_row_count": len(TARGET_IDS),
        "applied_row_ids": list(TARGET_IDS),
        "unresolved_runtime_hold_count": 0,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
        "network_operation_performed": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "README_KO.md",
        SCRIPT,
        WORKSTREAM / "test_pc_event_ending_regions_quality_wave100_v1.py",
    ):
        require(path.is_file(), f"authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"trailing whitespace: {path.name}:{number}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify-private", "summary"))
    command = parser.parse_args(argv).command
    if command == "profile":
        _event, output_profile, _audit, _manifest = build_bundle(require_output_profile=False)
        print(json.dumps(output_profile, ensure_ascii=False, sort_keys=True))
        return 0
    if command == "build":
        source_whitespace_check()
        require(EXPECTED_OUTPUT_PROFILE is not None, "output profile is not pinned")
        event, _output_profile, audit, manifest = build_bundle(require_output_profile=True)
        print(relative(write_candidate(event, audit, manifest)))
        return 0
    if command == "verify-private":
        source_whitespace_check()
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, sort_keys=True))
        return 0
    _event, output_profile, audit, _manifest = build_bundle(require_output_profile=True)
    print(
        json.dumps(
            {
                "event_profile": output_profile,
                "applied_row_ids": audit["coverage"]["applied_row_ids"],
                "unresolved_runtime_hold_ids": audit["coverage"]["unresolved_runtime_hold_ids"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Wave100Error, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
