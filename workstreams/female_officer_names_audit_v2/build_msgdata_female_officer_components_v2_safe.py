#!/usr/bin/env python3
"""Build the statically scoped safe subset of female-officer name components.

Version 1's 11-component trial set is intentionally *not* the deployable
entry point because it lacks the final full-scope guards.  This version
carries forward the eleven entries that are either
directly scope-validated or have an observed record anchor plus complete,
alternate component decompositions for every apparent competing name.

The command never writes to ``--game-root``.  A candidate is written only
beneath an explicit output root outside the installation.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Sequence


HERE = Path(__file__).resolve().parent


def load_v1() -> Any:
    path = HERE / "build_msgdata_female_officer_components_v1.py"
    spec = importlib.util.spec_from_file_location("female_component_build_v1", path)
    if spec is None or spec.loader is None:
        raise ComponentFixError("cannot load the pinned component baseline helpers")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_component_audit() -> Any:
    path = HERE / "audit_female_officer_component_combinations.py"
    spec = importlib.util.spec_from_file_location("female_component_audit", path)
    if spec is None or spec.loader is None:
        raise ComponentFixError("cannot load component static-audit helpers")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V1 = load_v1()
COMPONENT_AUDIT = load_component_audit()
RESOURCE = V1.RESOURCE
BASELINE = V1.BASELINE
SCHEMA = "nobu16.kr.female-officer-component-fix.v2-safe"
REPORT_SCHEMA = "nobu16.kr.female-officer-component-fix-build-report.v2-safe"

# 386 (메고) and 2083 (이치) are safe within the officer-name domain after
# resolving every apparent source-token competitor to a complete alternate
# pair that excludes the target ID.  No audited component remains blocked.
SAFE_COMPONENT_IDS: tuple[int, ...] = (287, 376, 386, 434, 773, 791, 2081, 2082, 2083, 2087, 6708)
BLOCKED_COMPONENT_IDS: tuple[int, ...] = ()

# For each allowed component, all historical source-token occurrences must
# already contain its replacement in the authoritative direct Korean name.
# These are exact counts from the full 0..2206 static audit and make widening
# or accidental source-table drift fail closed.
EXPECTED_HISTORICAL_NAME_SCOPE: dict[int, int] = {
    287: 1,
    376: 125,
    386: 7,
    434: 1,
    773: 1,
    791: 7,
    2081: 1,
    2082: 10,
    2083: 5,
    2087: 1,
    6708: 1,
}

OICHI_COMPONENT_ID = 2083
OICHI_OBSERVED_COMPONENT_PAIR = (62, 2083)
OICHI_ALTERNATE_COMPONENT_PAIRS: dict[int, tuple[tuple[int, int], ...]] = {
    241: ((573, 1661), (573, 7764)),
    252: ((572, 2371),),
    1371: ((596, 2016),),
    1372: ((596, 2447),),
}
MEGO_COMPONENT_ID = 386
MEGO_TARGET_MSGEV_ID = 2007
MEGO_TARGET_COMPONENT_PAIR = (386, 2082)
MEGO_ALTERNATE_COMPONENT_PAIRS: dict[int, tuple[tuple[int, int], ...]] = {
    0: ((387, 2223),),
    1: ((387, 1947),),
    151: ((394, 1031), (394, 7997), (3008, 1031), (3008, 7997)),
    729: ((879, 2706),),
    730: ((879, 957), (879, 7387)),
    732: ((879, 1841),),
}


class ComponentFixError(ValueError):
    """Raised when static scope or binary invariants differ."""


def load_patches() -> tuple[dict[str, Any], ...]:
    # V1's tracked overlay itself remains fail-closed against the active game
    # baseline; use it only as the signed source of individual entries.
    overlay = V1.load_overlay()
    by_id = {entry["id"]: entry for entry in overlay["entries"]}
    if set(by_id) != set(SAFE_COMPONENT_IDS + BLOCKED_COMPONENT_IDS):
        raise ComponentFixError("the audited v1 component universe differs")
    patches = tuple(by_id[component_id] for component_id in SAFE_COMPONENT_IDS)
    if tuple(entry["id"] for entry in patches) != SAFE_COMPONENT_IDS:
        raise ComponentFixError("safe component order differs")
    return patches


def read_static_name_tables(game_root: Path) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    sc_msgev, _ = COMPONENT_AUDIT.read_table(game_root / "MSG_PK" / "SC" / "msgev.bin")
    jp_msgev, _ = COMPONENT_AUDIT.read_table(game_root / "MSG_PK" / "JP" / "msgev.bin")
    sc_msgdata, _ = COMPONENT_AUDIT.read_table(game_root / "MSG_PK" / "SC" / "msgdata.bin")
    jp_msgdata, _ = COMPONENT_AUDIT.read_table(game_root / "MSG_PK" / "JP" / "msgdata.bin")
    if len(sc_msgev) != COMPONENT_AUDIT.EXPECTED_MSGEV_COUNT:
        raise ComponentFixError("SC msgev string count differs")
    if len(jp_msgev) != COMPONENT_AUDIT.EXPECTED_MSGEV_COUNT:
        raise ComponentFixError("JP msgev string count differs")
    if len(sc_msgdata) != COMPONENT_AUDIT.EXPECTED_MSGDATA_COUNT:
        raise ComponentFixError("SC msgdata string count differs")
    if len(jp_msgdata) != COMPONENT_AUDIT.EXPECTED_MSGDATA_COUNT:
        raise ComponentFixError("JP msgdata string count differs")
    return sc_msgev, jp_msgev, sc_msgdata, jp_msgdata


def validate_historical_name_scope(
    game_root: Path, patches: Sequence[dict[str, Any]]
) -> list[dict[str, Any]]:
    sc_msgev, jp_msgev, sc_msgdata, jp_msgdata = read_static_name_tables(game_root)
    source_index = COMPONENT_AUDIT.component_index(sc_msgdata)
    checks: list[dict[str, Any]] = []
    for patch in patches:
        component_id = patch["id"]
        source_token = sc_msgdata[component_id]
        if not source_token:
            raise ComponentFixError(f"component {component_id} has an empty SC token")
        matched_ids = [
            msgev_id
            for msgev_id in range(COMPONENT_AUDIT.HISTORICAL_OFFICER_MAX_ID + 1)
            if source_token in sc_msgev[msgev_id]
        ]
        if len(matched_ids) != EXPECTED_HISTORICAL_NAME_SCOPE[component_id]:
            raise ComponentFixError(f"historical token scope differs at component {component_id}")
        if component_id == MEGO_COMPONENT_ID:
            if matched_ids != [0, 1, 151, 729, 730, 732, 2007]:
                raise ComponentFixError("Megohime token scope IDs differ")
            target_pairs = COMPONENT_AUDIT.exact_pairs(sc_msgev[MEGO_TARGET_MSGEV_ID], source_index)
            if tuple(target_pairs) != (MEGO_TARGET_COMPONENT_PAIR,):
                raise ComponentFixError("Megohime target component pair differs")
            for msgev_id, expected_pairs in MEGO_ALTERNATE_COMPONENT_PAIRS.items():
                pairs = COMPONENT_AUDIT.exact_pairs(sc_msgev[msgev_id], source_index)
                if tuple(pairs) != expected_pairs or any(MEGO_COMPONENT_ID in pair for pair in pairs):
                    raise ComponentFixError(f"Megohime alternate component proof differs at msgev id {msgev_id}")
                if not any(jp_msgdata[left] + jp_msgdata[right] == jp_msgev[msgev_id] for left, right in pairs):
                    raise ComponentFixError(f"Megohime alternate component rendering differs at msgev id {msgev_id}")
            checks.append(
                {
                    "component_id": component_id,
                    "historical_officer_source_token_scope_count": len(matched_ids),
                    "validation_mode": "megohime_target_pair_plus_alternate_component_exclusion",
                    "all_competing_historical_names_use_exact_pairs_without_386": True,
                    "source_text_stored": False,
                    "historical_msgev_ids_stored": False,
                }
            )
            continue
        if component_id == OICHI_COMPONENT_ID:
            if matched_ids != [241, 252, 404, 1371, 1372]:
                raise ComponentFixError("Oichi token scope IDs differ")
            for msgev_id, expected_pairs in OICHI_ALTERNATE_COMPONENT_PAIRS.items():
                pairs = COMPONENT_AUDIT.exact_pairs(sc_msgev[msgev_id], source_index)
                if tuple(pairs) != expected_pairs or any(OICHI_COMPONENT_ID in pair for pair in pairs):
                    raise ComponentFixError(f"Oichi alternate component proof differs at msgev id {msgev_id}")
                if not any(jp_msgdata[left] + jp_msgdata[right] == jp_msgev[msgev_id] for left, right in pairs):
                    raise ComponentFixError(f"Oichi alternate component rendering differs at msgev id {msgev_id}")
            checks.append(
                {
                    "component_id": component_id,
                    "historical_officer_source_token_scope_count": len(matched_ids),
                    "validation_mode": "observed_oichi_anchor_plus_alternate_component_exclusion",
                    "all_competing_historical_names_use_exact_pairs_without_2083": True,
                    "source_text_stored": False,
                    "historical_msgev_ids_stored": False,
                }
            )
            continue
        conflicts = [msgev_id for msgev_id in matched_ids if patch["ko"] not in jp_msgev[msgev_id]]
        if conflicts:
            raise ComponentFixError(
                f"historical direct-name conflict at component {component_id}: {conflicts}"
            )
        checks.append(
            {
                "component_id": component_id,
                "historical_officer_source_token_scope_count": len(matched_ids),
                "validation_mode": "all_historical_direct_names_contain_replacement",
                "all_direct_korean_names_contain_replacement": True,
                "source_text_stored": False,
                "historical_msgev_ids_stored": False,
            }
        )
    return checks


def build_candidate(game_root: Path) -> tuple[bytes, dict[str, Any]]:
    patches = load_patches()
    _source, packed, raw, texts = V1.parse_pinned_input(game_root)
    scope_checks = validate_historical_name_scope(game_root, patches)
    updated = list(texts)
    for patch in patches:
        component_id = patch["id"]
        if V1.text_hash(updated[component_id]) != patch["baseline_ko_utf16le_sha256"]:
            raise ComponentFixError(f"component baseline text differs at id {component_id}")
        if V1.text_hash(patch["ko"]) != patch["ko_utf16le_sha256"]:
            raise ComponentFixError(f"replacement hash differs at id {component_id}")
        updated[component_id] = patch["ko"]
    changed_ids = [patch["id"] for patch in patches]
    if any(texts[index] != updated[index] for index in range(len(texts)) if index not in set(changed_ids)):
        raise ComponentFixError("a non-target msgdata row changed in memory")
    if texts[OICHI_OBSERVED_COMPONENT_PAIR[0]] + texts[OICHI_OBSERVED_COMPONENT_PAIR[1]] != "오시장":
        raise ComponentFixError("observed Oichi defect reconstruction differs")
    if updated[OICHI_OBSERVED_COMPONENT_PAIR[0]] + updated[OICHI_OBSERVED_COMPONENT_PAIR[1]] != "오이치":
        raise ComponentFixError("targeted Oichi reconstruction differs")
    if updated[MEGO_TARGET_COMPONENT_PAIR[0]] + updated[MEGO_TARGET_COMPONENT_PAIR[1]] != "메고히메":
        raise ComponentFixError("targeted Megohime reconstruction differs")

    source_table = V1.parse_message_table(raw)
    rebuilt_raw = V1.rebuild_message_table(source_table, updated)
    rebuilt_table = V1.parse_message_table(rebuilt_raw)
    if rebuilt_table.texts != tuple(updated):
        raise ComponentFixError("rebuilt msgdata table did not round-trip")
    candidate = V1.recompress_wrapper(rebuilt_raw, packed)
    header, candidate_raw = V1.decompress_wrapper(candidate)
    if candidate_raw != rebuilt_raw or header.prefix != packed[:8]:
        raise ComponentFixError("candidate wrapper verification failed")
    if (_source.read_bytes()) != packed:
        raise ComponentFixError("input changed while the candidate was being built")

    report = {
        "schema": REPORT_SCHEMA,
        "resource": RESOURCE.as_posix(),
        "source": BASELINE,
        "candidate": {
            "packed_size": len(candidate),
            "packed_sha256": V1.sha256_bytes(candidate),
            "raw_size": len(rebuilt_raw),
            "raw_sha256": V1.sha256_bytes(rebuilt_raw),
            "string_count": rebuilt_table.string_count,
        },
        "changed_component_ids": changed_ids,
        "blocked_component_ids": list(BLOCKED_COMPONENT_IDS),
        "historical_name_scope_checks": scope_checks,
        "verification": {
            "source_parse_rebuild_byte_identical": True,
            "non_target_texts_preserved": True,
            "candidate_parse_roundtrip": True,
            "wrapper_prefix_preserved": True,
            "input_unchanged_during_build": True,
            "installed_game_files_modified": False,
        },
    }
    return candidate, report


def cmd_verify(args: argparse.Namespace) -> int:
    _candidate, report = build_candidate(args.game_root.resolve())
    print(f"resource={RESOURCE.as_posix()}")
    print("changed=" + str(len(report["changed_component_ids"])))
    print("blocked=" + json.dumps(report["blocked_component_ids"]))
    print("result=PASS")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    game_root = args.game_root.resolve()
    output_root = args.output_root.resolve()
    V1.ensure_output_is_safe(game_root, output_root)
    candidate, report = build_candidate(game_root)
    output = output_root / RESOURCE
    report_path = output_root / "component_fix.build-report.v2-safe.json"
    V1.atomic_write(output, candidate)
    V1.atomic_write(report_path, V1.pretty_json(report))
    print(f"output={output}")
    print(f"report={report_path}")
    print("changed=" + str(len(report["changed_component_ids"])))
    print("installed_game_files_modified=False")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--game-root", type=Path, required=True)
    verify.set_defaults(func=cmd_verify)
    build = commands.add_parser("build")
    build.add_argument("--game-root", type=Path, required=True)
    build.add_argument("--output-root", type=Path, required=True)
    build.set_defaults(func=cmd_build)
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError, ComponentFixError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
