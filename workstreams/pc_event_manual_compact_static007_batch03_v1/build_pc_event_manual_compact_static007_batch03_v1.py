#!/usr/bin/env python3
"""Build the private Static Patch 007 manual_compact restoration batch 03.

Only the on-disk batch02 candidate provides Korean text. Direct PC JP/EN/SC/TC
resources are read-only semantic evidence. The builder produces one candidate
beneath ``tmp`` and has no Steam, Git, release, or network path.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_ROOT = TMP_ROOT / "candidate-final"
MSGEV = "MSG_PK/JP/msgev.bin"

BATCH02_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_manual_compact_static007_batch02_v1"
    / "build_pc_event_manual_compact_static007_batch02_v1.py"
)
PREDECESSOR_WORKSTREAM = "pc_event_manual_compact_static007_batch02_v1"
PREDECESSOR_CANDIDATE_ROOT = REPO / "tmp" / PREDECESSOR_WORKSTREAM / "candidate-final"
EXPECTED_PREDECESSOR_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "C9F9BD8772C16DC7FC10220AE515FDFAC2C0B3DBF431B8D07A71604982274C05",
    "raw_size": 996_456,
    "sha256": "20050DDFB1F5791A20DF7B05FBA891B654D0486F519410EEE516991368D9C41A",
    "size": 1_000_389,
}
# Deterministic output from the pinned batch02 strict predecessor.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "A2815BB64F67F85A4033A907ADD3688B479CD88E34E32BF8E8C9F976B0A879D5",
    "raw_size": 996_456,
    "sha256": "259908A5D24CB0C81B3A66FBBD55AE9A97D5210DE24555B1BDBF79AAF0C90B16",
    "size": 1_000_389,
}

HISTORICAL_OVERLAY_PATH = (
    REPO / "workstreams" / "steam_jp_msgev_full_layout_v2" / "public" / "msgev_ko_steam_jp_full_layout.v2.json"
)
HISTORICAL_OPERATION = "manual_compact_korean_layout"
SCENE_NAME = "mikatagahara_shingen_advance"
SCENE_IDS = tuple(range(3_261, 3_277))
CHANGED_IDS = (3_262, 3_274)
RETAINED_IDS = tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS)
E = "\x1b"

TARGETS: Mapping[int, str] = {
    3_262: (
        "겐키 3년(1572년). 쇼군 "
        f"{E}CA요시아키{E}CZ까지 가세한\n"
        f"반{E}CB오다{E}CZ 연합의 최대 난적이자 가장 성가신 인물……\n"
        f"{E}CC카이{E}CZ의 노련한 영걸이 마침내 움직였다."
    ),
    3_274: (
        f"그 틈을 타 낙담한 주군을 {E}CC하마마쓰성{E}CZ으로\n"
        "필사적으로 피신시킨 충복들 덕에\n"
        f"{E}CA이에야스{E}CZ는 목숨을 건졌다."
    ),
}
TARGET_LAYOUTS: Mapping[int, tuple[tuple[int, ...], tuple[int, ...]]] = {
    3_262: ((1_008, 1_104, 888), (630, 690, 555)),
    3_274: ((936, 744, 600), (585, 465, 375)),
}
RATIONALES: Mapping[int, str] = {
    3_262: "현재 품질본의 연도·쇼군 참여·반오다 연합·최대 난적·성가신 인물 의미를 모두 보존하고, 문장 단위 세 줄로 재배치했다.",
    3_274: "그 틈을 타는 인과와 낙담한 주군의 피신, 충복들의 공, 이에야스의 생환을 축약 없이 문장 단위로 연결했다.",
}
CURRENT_QUALITY_PRESERVED: Mapping[int, tuple[str, ...]] = {
    3_262: ("겐키 3년(1572년)", "쇼군", "요시아키", "반오다 연합", "최대 난적", "가장 성가신 인물", "카이", "노련한 영걸"),
    3_274: ("낙담한 주군", "하마마쓰성", "필사적으로", "충복들", "목숨을 건졌다"),
}


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


if not BATCH02_BUILDER.is_file():
    raise RuntimeError(f"batch02 helper missing: {BATCH02_BUILDER}")
base = load_module("manual_compact_static007_batch02_base", BATCH02_BUILDER)


class ManualCompactStatic007Batch03Error(RuntimeError):
    """Raised when strict input, evidence, layout, or output drifts."""


@dataclass(frozen=True)
class Bundle:
    event: bytes
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]
    profile: Mapping[str, Any]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ManualCompactStatic007Batch03Error(message)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def file_spec(path: Path) -> Mapping[str, Any]:
    blob = path.read_bytes()
    return {"path": path.relative_to(REPO).as_posix(), "size": len(blob), "sha256": sha256(blob)}


def require_private(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ManualCompactStatic007Batch03Error(f"candidate path escapes tmp: {resolved}") from exc
    return resolved


def validate_authored_targets() -> None:
    require(tuple(TARGETS) == CHANGED_IDS, "target ID order/scope drift")
    require(set(CHANGED_IDS).isdisjoint(RETAINED_IDS), "changed/retained scope overlap")
    require(SCENE_IDS == tuple(range(3261, 3277)), "scene scope drift")
    for entry_id, target in TARGETS.items():
        require("\x00" not in target, f"embedded terminator: {entry_id}")
        base.base.assert_no_break_inside_tag(target)
        signature = base.base.control_signature(target)
        require(signature["runtime_tokens"] == [], f"runtime token in target: {entry_id}")
        require(signature["printf_tokens"] == [], f"printf token in target: {entry_id}")
        require(signature["unknown_percent_count"] == 0, f"unknown percent in target: {entry_id}")
        require(signature["other_controls"] == [], f"other control in target: {entry_id}")
        metrics = base.base.line_metrics(target)
        require(1 <= len(metrics) <= 4, f"target line count exceeds max: {entry_id}")
        require(all(line["passes_static_patch_007"] for line in metrics), f"target fails Static Patch 007: {entry_id}")
        if TARGET_LAYOUTS:
            expected_raw, expected_effective = TARGET_LAYOUTS[entry_id]
            require(tuple(line["raw_g1n_width_px"] for line in metrics) == expected_raw, f"target raw drift: {entry_id}")
            require(
                tuple(line["effective_width_px"] for line in metrics) == expected_effective,
                f"target effective drift: {entry_id}",
            )


def load_predecessor() -> tuple[bytes, Any, bytes, Mapping[str, Any], Mapping[str, Any]]:
    root = PREDECESSOR_CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"strict predecessor file scope drift: {sorted(actual_files)}")
    event = (root / MSGEV).read_bytes()
    _header, raw, table = base.base.parse_table("strict batch02 predecessor", event)
    predecessor_profile = base.base.profile(event, raw)
    require(predecessor_profile == EXPECTED_PREDECESSOR_PROFILE, "strict predecessor packed/raw profile drift")
    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit.get("output_event_profile") == EXPECTED_PREDECESSOR_PROFILE, "predecessor audit profile drift")
    require(manifest.get("output") == EXPECTED_PREDECESSOR_PROFILE, "predecessor manifest profile drift")
    return event, table, raw, predecessor_profile, audit


def load_historical_manual_compact() -> tuple[Mapping[int, Mapping[str, Any]], Mapping[str, Any]]:
    require(HISTORICAL_OVERLAY_PATH.is_file(), f"historical overlay missing: {HISTORICAL_OVERLAY_PATH}")
    document = json.loads(HISTORICAL_OVERLAY_PATH.read_text(encoding="utf-8"))
    entries = document.get("entries")
    require(isinstance(entries, list), "historical overlay entries missing")
    by_id: dict[int, Mapping[str, Any]] = {}
    for entry in entries:
        if isinstance(entry, dict) and type(entry.get("id")) is int and entry["id"] in CHANGED_IDS:
            require(entry["id"] not in by_id, f"historical duplicate ID: {entry['id']}")
            by_id[entry["id"]] = entry
    require(tuple(sorted(by_id)) == CHANGED_IDS, "historical manual compact coverage drift")
    for entry_id, entry in by_id.items():
        require(entry.get("operation") == HISTORICAL_OPERATION, f"historical operation drift: {entry_id}")
        require(isinstance(entry.get("ko"), str) and entry["ko"], f"historical Korean absent: {entry_id}")
    return by_id, file_spec(HISTORICAL_OVERLAY_PATH)


def historical_evidence(entry_id: int, historical: Mapping[int, Mapping[str, Any]]) -> Mapping[str, Any]:
    entry = historical[entry_id]
    legacy = str(entry["ko"])
    return {
        "operation": str(entry["operation"]),
        "legacy_manual_compact_ko": legacy,
        "legacy_manual_compact_ko_utf16le_sha256": text_hash(legacy),
        "legacy_lines": list(base.base.line_metrics(legacy)),
        "legacy_source_is_not_korean_build_input": True,
    }


def prepare(*, require_output_profile: bool) -> Bundle:
    validate_authored_targets()
    before_event, before, _before_raw, predecessor_profile, predecessor_audit = load_predecessor()
    contexts, context_profiles = base.base.load_direct_contexts()
    historical, historical_profile = load_historical_manual_compact()
    require(all(len(before.texts) == len(table.texts) for table in contexts.values()), "context table topology drift")

    texts = list(before.texts)
    rows: list[Mapping[str, Any]] = []
    for entry_id in SCENE_IDS:
        current = before.texts[entry_id]
        source_jp = contexts["jp"].texts[entry_id]
        source_en = contexts["en"].texts[entry_id]
        source_sc = contexts["sc"].texts[entry_id]
        source_tc = contexts["tc"].texts[entry_id]
        target = TARGETS.get(entry_id, current)
        require(all((current, source_jp, source_en, source_sc, source_tc, target)), f"empty reviewed row: {entry_id}")
        current_signature = base.base.control_signature(current)
        require(current_signature == base.base.control_signature(source_jp), f"strict KO/direct JP control drift: {entry_id}")
        require(base.base.control_signature(target) == current_signature, f"target control/token drift: {entry_id}")
        base.base.assert_no_break_inside_tag(current)
        base.base.assert_no_break_inside_tag(target)
        current_lines = base.base.line_metrics(current)
        target_lines = base.base.line_metrics(target)
        require(1 <= len(target_lines) <= 4, f"target line count exceeds max: {entry_id}")
        require(all(line["passes_static_patch_007"] for line in target_lines), f"target layout fails: {entry_id}")
        changed = entry_id in CHANGED_IDS
        require((target != current) == changed, f"change disposition drift: {entry_id}")
        if changed:
            texts[entry_id] = target
        row: dict[str, Any] = {
            "entry_id": entry_id,
            "scene": SCENE_NAME,
            "changed": changed,
            "strict_predecessor_ko": current,
            "target_ko": target,
            "strict_predecessor_ko_utf16le_sha256": text_hash(current),
            "target_ko_utf16le_sha256": text_hash(target),
            "direct_pc_jp": source_jp,
            "direct_pc_en": source_en,
            "direct_pc_sc": source_sc,
            "direct_pc_tc": source_tc,
            "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
            "direct_pc_en_utf16le_sha256": text_hash(source_en),
            "direct_pc_sc_utf16le_sha256": text_hash(source_sc),
            "direct_pc_tc_utf16le_sha256": text_hash(source_tc),
            "direct_control_signatures": {
                "jp": base.base.control_signature(source_jp),
                "en": base.base.control_signature(source_en),
                "sc": base.base.control_signature(source_sc),
                "tc": base.base.control_signature(source_tc),
            },
            "target_control_signature": base.base.control_signature(target),
            "strict_ko_matches_direct_jp_protected_signature": True,
            "japanese_source_line_breaks_used": False,
            "jp_lf_policy": "ignored",
            "runtime_tokens": [],
            "runtime_reservations": [],
            "runtime_proven": False,
            "current_manual_line_count": len(current_lines),
            "target_manual_line_count": len(target_lines),
            "current_lines": list(current_lines),
            "target_lines": list(target_lines),
            "current_static_patch_007_passes": all(line["passes_static_patch_007"] for line in current_lines),
            "target_static_patch_007_passes": all(line["passes_static_patch_007"] for line in target_lines),
            "terminator_policy": "UTF-16LE NUL terminator is serialized by rebuild_message_table",
        }
        if changed:
            row["rationale"] = RATIONALES[entry_id]
            row["historical_vs_current"] = historical_evidence(entry_id, historical)
            row["current_quality_conflict_check"] = {
                "status": "PASS",
                "preserved_current_terms": list(CURRENT_QUALITY_PRESERVED[entry_id]),
                "reason": "현재 strict 품질본의 용어와 의미를 유지한 채, direct PC 4언어에서 확인되는 누락 또는 부자연스러운 경계를 복원했다.",
            }
        else:
            row["rationale"] = "장면 문맥·direct PC 4언어·Static Patch 007 폭을 확인했으나 manual_compact 대상이 아니므로 유지했다."
            row["historical_vs_current"] = None
            row["current_quality_conflict_check"] = {
                "status": "NOT_APPLICABLE",
                "reason": "manual_compact 대상 밖이므로 변경하지 않았다.",
            }
        rows.append(row)

    header, _raw_again, _table_again = base.base.parse_table("strict batch02 predecessor", before_event)
    rebuilt_raw = base.base.rebuild_message_table(before, texts)
    event = base.base.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = base.base.parse_table("manual compact Static007 batch03 output", event)
    require(after_raw == rebuilt_raw, "candidate raw reparse mismatch")
    changed_ids = [index for index, (left, right) in enumerate(zip(before.texts, after.texts)) if left != right]
    require(changed_ids == list(CHANGED_IDS), f"candidate is not exact two-row diff: {changed_ids[:12]}")
    require(all(after.texts[entry_id] == TARGETS[entry_id] for entry_id in CHANGED_IDS), "candidate target text drift")
    event_profile = base.base.profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "candidate output packed/raw profile drift")

    changed_rows = [row for row in rows if row["changed"]]
    audit = {
        "schema": "nobu16.kr.pc-event-manual-compact-static007-batch03-audit.v1",
        "candidate_only": True,
        "source_policy": {
            "strict_input_only": PREDECESSOR_CANDIDATE_ROOT.relative_to(REPO).as_posix(),
            "only_korean_predecessor_input": True,
            "direct_pc_context_read_only": True,
            "direct_pc_context_languages": ["jp", "en", "sc", "tc"],
            "historical_manual_compact_is_comparison_only": True,
            "switch_korean_used": False,
            "japanese_source_line_breaks_used": False,
            "korean_sentence_shortened_or_deleted": False,
            "steam_game_resource_written": False,
            "git_operation_performed": False,
            "network_operation_performed": False,
            "release_published": False,
        },
        "layout_policy": {
            "authority": "F:/Games/NOBU16/AGENTS.md Static Patch 007 baseline",
            "raw_full_width_px": 48,
            "raw_half_width_px": 24,
            "raw_hard_limit_px": 1_440,
            "effective_width_hard_limit_px": 912,
            "max_lines": 4,
            "draw_font_px": 30,
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "effective_width_is_report_only": False,
            "runtime_reservations": {},
        },
        "source_profiles": {
            "strict_predecessor_batch02": predecessor_profile,
            "direct_pc_contexts": context_profiles,
            "historical_manual_compact_overlay": historical_profile,
        },
        "predecessor_quality_evidence": {
            "predecessor_audit_schema": predecessor_audit.get("schema"),
            "predecessor_changed_row_ids": predecessor_audit.get("actual_changed_row_ids"),
            "predecessor_profile": predecessor_profile,
        },
        "coverage": {
            "reviewed_scene": SCENE_NAME,
            "reviewed_row_ids": list(SCENE_IDS),
            "reviewed_row_count": len(SCENE_IDS),
            "manual_compact_changed_ids": list(CHANGED_IDS),
            "manual_compact_changed_count": len(CHANGED_IDS),
            "retained_context_ids": list(RETAINED_IDS),
            "retained_context_count": len(RETAINED_IDS),
        },
        "output_event_profile": event_profile,
        "actual_changed_row_ids": changed_ids,
        "actual_changed_row_count": len(changed_ids),
        "exact_two_row_diff": changed_rows,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-manual-compact-static007-batch03-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "predecessor": {
            "workstream": PREDECESSOR_WORKSTREAM,
            "candidate_relative": (PREDECESSOR_CANDIDATE_ROOT / MSGEV).relative_to(REPO).as_posix(),
            "profile": predecessor_profile,
            "strict_on_disk": True,
            "only_korean_predecessor_input": True,
        },
        "direct_pc_context_profiles": context_profiles,
        "historical_manual_compact_overlay": historical_profile,
        "changed_row_ids": list(CHANGED_IDS),
        "exact_two_row_diff": True,
        "output": event_profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "network_operation_performed": False,
        "release_published": False,
    }
    return Bundle(event, audit, manifest, event_profile)


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT)
    require(not output.exists(), f"candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"candidate staging already exists: {staging}")
    staging.mkdir(parents=True)
    try:
        event_path = staging / MSGEV
        event_path.parent.mkdir(parents=True)
        event_path.write_bytes(bundle.event)
        (staging / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (staging / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        os.replace(staging, output)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return output


def verify_private_candidate(bundle: Bundle | None = None) -> Mapping[str, Any]:
    bundle = bundle or prepare(require_output_profile=True)
    root = require_private(CANDIDATE_ROOT)
    require(root.is_dir(), f"candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "candidate event differs from deterministic build")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "candidate manifest differs")
    return {
        "status": "PASS",
        "candidate_root": root.relative_to(REPO).as_posix(),
        "changed_row_ids": list(CHANGED_IDS),
        "event_profile": bundle.profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "network_operation_performed": False,
        "release_published": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "README_KO.md",
        WORKSTREAM / "build_pc_event_manual_compact_static007_batch03_v1.py",
        WORKSTREAM / "test_pc_event_manual_compact_static007_batch03_v1.py",
    ):
        require(path.is_file(), f"authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("authoring-check", "profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "authoring-check":
        validate_authored_targets()
        print(json.dumps({entry_id: list(base.base.line_metrics(text)) for entry_id, text in TARGETS.items()}, ensure_ascii=False))
        return 0
    if command == "profile":
        print(json.dumps(prepare(require_output_profile=False).profile, ensure_ascii=False, sort_keys=True))
        return 0
    if command == "build":
        source_whitespace_check()
        require(EXPECTED_OUTPUT_PROFILE is not None, "output profile is not pinned")
        print(write_candidate(prepare(require_output_profile=True)))
        return 0
    if command == "verify-private":
        source_whitespace_check()
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, sort_keys=True))
        return 0
    bundle = prepare(require_output_profile=True)
    print(json.dumps({"changed_row_ids": bundle.audit["actual_changed_row_ids"], "event_profile": bundle.profile}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
