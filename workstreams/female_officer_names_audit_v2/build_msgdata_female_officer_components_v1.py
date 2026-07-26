#!/usr/bin/env python3
"""Legacy 11-component trial builder; intentionally blocked after scope audit.

This workstream is intentionally fail-closed against the observed active JP
baseline.  It never writes to the supplied game root: ``build`` emits a
candidate only below an explicit output root outside the game root.

The full historical-name impact audit added complete competing-name exclusion
checks for the ambiguous source tokens.  This v1 entry point is retained solely
as a fail-closed source of hashed component baselines for v2; use
``build_msgdata_female_officer_components_v2_safe.py`` for a candidate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


RESOURCE = Path("MSG_PK") / "JP" / "msgdata.bin"
OVERLAY_PATH = HERE / "public" / "msgdata_female_officer_component_fix.v1.json"
SCHEMA = "nobu16.kr.female-officer-component-fix.v1"
REPORT_SCHEMA = "nobu16.kr.female-officer-component-fix-build-report.v1"
V1_DEPLOYMENT_BLOCK_REASON = (
    "v1 is superseded by v2-safe and lacks the final full-scope guards; "
    "build_msgdata_female_officer_components_v2_safe.py is required"
)

BASELINE = {
    "packed_size": 481_948,
    "packed_sha256": "6E2B883004545B2DD7D28360AFEED7D3BFDFEF2BF45E8333FD95CD0A49E95C70",
    "raw_size": 480_040,
    "raw_sha256": "EED37E2756D34130F169D85D3EC9185AE92E4C221E925A48483CC47510CEE4E9",
    "string_count": 29_218,
}

# Every row is an identifier-like name component.  The original component
# text is represented only by its UTF-16LE hash; all visible strings below are
# project-authored Korean replacements.
PATCHES: tuple[dict[str, Any], ...] = (
    {
        "id": 287,
        "baseline_ko_utf16le_sha256": "F24FD7273D612A108C8AB1450EE571957B46FC5A7DD5781A4D7C4965B8D374E2",
        "ko": "네",
        "ko_utf16le_sha256": "707CFA320F0B2E284385156B037F337344FE287AAFA64202EEF2BCCBAC199D93",
        "affected_msgev_ids": [1582],
    },
    {
        "id": 376,
        "baseline_ko_utf16le_sha256": "B8091B8C1584CEB3B0A0492E8BF99FC08BB6CC676A2A805FB57E87C1114127E4",
        "ko": "요시",
        "ko_utf16le_sha256": "D05822E47E5998740711B8BAD8BFDBF23712CCF8164E25010FD87229F2E19838",
        "affected_msgev_ids": [2147],
    },
    {
        "id": 386,
        "baseline_ko_utf16le_sha256": "128652858A1E6B0A8AEF0918EDB320B0912AB8FD486C29DBFD8A18CAB3940281",
        "ko": "메고",
        "ko_utf16le_sha256": "E327248059AF4DBB3CDB0FE0C44C1702682FC693EAA9440F6CD62C8D138187A2",
        "affected_msgev_ids": [2007],
    },
    {
        "id": 434,
        "baseline_ko_utf16le_sha256": "993E5B201B13CCFC26D9A242047DFF5913DC4ED0A95FC50B7DA89CA0BDF2AC39",
        "ko": "오바이",
        "ko_utf16le_sha256": "352EA4927CA0C62A23C33B5A7D18DCA43127CD8E7D85B733F16B81EC6FDF50E4",
        "affected_msgev_ids": [410],
    },
    {
        "id": 773,
        "baseline_ko_utf16le_sha256": "D8E1DE8F5C1845EAB6330C2313C26FBAA888B31D087DCAD0B11E20D2DEF2975C",
        "ko": "조케이",
        "ko_utf16le_sha256": "4AC42C00EAD9A22A3FE5EF21F9D49FBCA80693326943A6B22D311E1F7A94DD05",
        "affected_msgev_ids": [1094],
    },
    {
        "id": 791,
        "baseline_ko_utf16le_sha256": "55F1F060DA5B169B076D26FA96E7011107F93BB4131A13743ED7988BFE1587FE",
        "ko": "후유",
        "ko_utf16le_sha256": "4A20022A912C8F13FB52AAE5DDEACC11E662C311539700B859612C266D8F80A3",
        "affected_msgev_ids": [1724],
    },
    {
        "id": 2081,
        "baseline_ko_utf16le_sha256": "7802879BF88695FF3E8C74BE36A97B57358A62A5F72EA6E8E1EC736BAB2A2BFA",
        "ko": "초",
        "ko_utf16le_sha256": "DC07BF37B1D20AB6CADBEF0D9C0B960A523889713F67A8F999759ECF11DD6839",
        "affected_msgev_ids": [715],
    },
    {
        "id": 2082,
        "baseline_ko_utf16le_sha256": "63BBEA1544AB415C24C491D3A4C63E7A2271E6E5CB14F2463697D471F9D82987",
        "ko": "히메",
        "ko_utf16le_sha256": "8824478D09577F64755EFF640D0392C1DD491F970CAD67C6FACC01ADEDA74F37",
        "affected_msgev_ids": [719, 1157, 1170, 1171, 1390, 1391, 1724, 1861, 2007, 2147],
    },
    {
        "id": 2083,
        "baseline_ko_utf16le_sha256": "20539974F0B90DB7F8B073DD783893E5AFFF7D0963D241DF173F73DCD6678F55",
        "ko": "이치",
        "ko_utf16le_sha256": "CBB95FC20E22E2A00375BE3E0F078575E22007AF2787AF4E74FBAABA69E2AADD",
        "affected_msgev_ids": [404],
    },
    {
        "id": 2087,
        "baseline_ko_utf16le_sha256": "7EC967F953CAF45217910952660B7618356914D8B158C2A530BD64E89B8B0B6E",
        "ko": "큐",
        "ko_utf16le_sha256": "9E1162334348838C9273520FC204A3FC7BE856E6BB6933468F9BDFD2292E52FB",
        "affected_msgev_ids": [1969],
    },
    {
        "id": 6708,
        "baseline_ko_utf16le_sha256": "7802879BF88695FF3E8C74BE36A97B57358A62A5F72EA6E8E1EC736BAB2A2BFA",
        "ko": "초",
        "ko_utf16le_sha256": "DC07BF37B1D20AB6CADBEF0D9C0B960A523889713F67A8F999759ECF11DD6839",
        "affected_msgev_ids": [715],
    },
)

# Static component reconstructions for the rows whose two-part form is exact
# in the active table.  These are validation anchors, not a full claim that
# every historical officer record has been reverse-serialized.
COMPOSITION_CHECKS: tuple[tuple[int, tuple[int, int], str], ...] = (
    (1582, (287, 287), "\ub124\ub124"),
    (404, (62, 2083), "\uc624\uc774\uce58"),
    (410, (434, 2080), "\uc624\ubc14\uc774\uc778"),
    (715, (472, 2081), "\uae30\ucd08"),
    (715, (472, 6708), "\uae30\ucd08"),
    (719, (116, 2082), "\uae30\ucfe0\ud788\uba54"),
    (1094, (773, 2080), "\uc870\ucf00\uc774\uc778"),
    (1157, (204, 2082), "\uc2a4\uc640 \ud788\uba54"),
    (1170, (674, 2082), "\uc138\ub098 \ud788\uba54"),
    (1171, (206, 2082), "\uc13c \ud788\uba54"),
    (1390, (804, 2082), "\ub3c4\ucfe0\ud788\uba54"),
    (1391, (808, 2082), "\ub3c4\ucfe0\ud788\uba54"),
    (1724, (791, 2082), "\ud6c4\uc720\ud788\uba54"),
    (1861, (328, 2082), "\ub9c8\uc4f0\ud788\uba54"),
    (1969, (898, 2087), "\ubb18\ud050"),
    (2007, (386, 2082), "\uba54\uace0\ud788\uba54"),
    # ID 376 is the current active table's semantic component "의" (義),
    # rather than the phonetic direct-name rendering "요시" in msgev.  This
    # anchor intentionally proves only the requested common suffix change.
    (2147, (376, 2082), "\uc694\uc2dc\ud788\uba54"),
)


class ComponentFixError(ValueError):
    """Raised when the input or tracked source-free contract differs."""


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256_bytes(text.encode("utf-16le"))


def pretty_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def expected_overlay() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "overlay_id": "msgdata-female-officer-component-fix.v1",
        "resource": RESOURCE.as_posix(),
        "base_language": "JP",
        "active_baseline": BASELINE,
        "entry_count": len(PATCHES),
        "entries": list(PATCHES),
        "static_evidence": {
            "name_combiner": "FUN_1405F40D0",
            "text_resolver": "FUN_1409F9BE0",
            "component_id_upper_bound_inclusive": "0x22DB",
            "female_msgev_ids_covered": [
                404, 410, 715, 719, 1094, 1157, 1170, 1171, 1390, 1391, 1582,
                1724, 1861, 1969, 2007, 2147,
            ],
        },
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
            "installed_game_files_modified": False,
        },
    }


def load_overlay() -> dict[str, Any]:
    try:
        value = json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ComponentFixError(f"cannot read component overlay: {exc}") from exc
    expected = expected_overlay()
    if value != expected:
        raise ComponentFixError("tracked component overlay differs from the fail-closed model")
    return value


def parse_pinned_input(game_root: Path) -> tuple[Path, bytes, bytes, tuple[str, ...]]:
    source = (game_root / RESOURCE).resolve()
    packed = source.read_bytes()
    if len(packed) != BASELINE["packed_size"] or sha256_bytes(packed) != BASELINE["packed_sha256"]:
        raise ComponentFixError("active JP msgdata packed baseline differs")
    header, raw = decompress_wrapper(packed)
    if len(raw) != BASELINE["raw_size"] or sha256_bytes(raw) != BASELINE["raw_sha256"]:
        raise ComponentFixError("active JP msgdata raw baseline differs")
    table = parse_message_table(raw)
    if table.string_count != BASELINE["string_count"]:
        raise ComponentFixError("active JP msgdata string-count baseline differs")
    if rebuild_message_table(table, table.texts) != raw:
        raise ComponentFixError("active JP msgdata parse/rebuild is not byte-identical")
    if header.prefix != packed[:8]:
        raise ComponentFixError("raw-LZ4 wrapper prefix invariant differs")
    return source, packed, raw, table.texts


def build_candidate(game_root: Path) -> tuple[bytes, dict[str, Any]]:
    raise ComponentFixError(V1_DEPLOYMENT_BLOCK_REASON)


def _legacy_unsafe_build_candidate_for_audit_only(game_root: Path) -> tuple[bytes, dict[str, Any]]:
    overlay = load_overlay()
    source, packed, raw, texts = parse_pinned_input(game_root)
    if texts[62] + texts[2083] != "오시장":
        raise ComponentFixError("active Oichi component reconstruction no longer matches the observed defect")
    updated = list(texts)
    changed_ids: list[int] = []
    for entry in overlay["entries"]:
        entry_id = entry["id"]
        if not isinstance(entry_id, int) or not 0 <= entry_id < len(updated):
            raise ComponentFixError("component entry ID is outside msgdata")
        if text_hash(updated[entry_id]) != entry["baseline_ko_utf16le_sha256"]:
            raise ComponentFixError(f"component baseline text differs at id {entry_id}")
        replacement = entry["ko"]
        if not isinstance(replacement, str) or not replacement or "\0" in replacement:
            raise ComponentFixError(f"component replacement is invalid at id {entry_id}")
        if text_hash(replacement) != entry["ko_utf16le_sha256"]:
            raise ComponentFixError(f"component replacement hash differs at id {entry_id}")
        updated[entry_id] = replacement
        changed_ids.append(entry_id)
    if changed_ids != [entry["id"] for entry in PATCHES]:
        raise ComponentFixError("component change set is not the exact expected ID sequence")
    if any(texts[i] != updated[i] for i in range(len(texts)) if i not in set(changed_ids)):
        raise ComponentFixError("a non-target msgdata row changed in memory")
    recompositions: list[dict[str, Any]] = []
    for msgev_id, component_ids, expected_korean in COMPOSITION_CHECKS:
        first, second = component_ids
        if not all(0 <= component_id <= 0x22DB for component_id in component_ids):
            raise ComponentFixError(f"component ID range differs for msgev id {msgev_id}")
        actual = updated[first] + updated[second]
        if actual != expected_korean:
            raise ComponentFixError(f"component reconstruction differs for msgev id {msgev_id}")
        recompositions.append(
            {
                "msgev_id": msgev_id,
                "component_ids": list(component_ids),
                "ko": actual,
            }
        )

    table = parse_message_table(raw)
    rebuilt_raw = rebuild_message_table(table, updated)
    rebuilt_table = parse_message_table(rebuilt_raw)
    if rebuilt_table.texts != tuple(updated):
        raise ComponentFixError("rebuilt msgdata table did not round-trip")
    candidate = recompress_wrapper(rebuilt_raw, packed)
    candidate_header, candidate_raw = decompress_wrapper(candidate)
    if candidate_raw != rebuilt_raw or candidate_header.prefix != packed[:8]:
        raise ComponentFixError("candidate raw-LZ4 wrapper verification failed")

    source_after = source.read_bytes()
    if source_after != packed:
        raise ComponentFixError("input changed while the candidate was being built")
    report = {
        "schema": REPORT_SCHEMA,
        "resource": RESOURCE.as_posix(),
        "source": BASELINE,
        "candidate": {
            "packed_size": len(candidate),
            "packed_sha256": sha256_bytes(candidate),
            "raw_size": len(rebuilt_raw),
            "raw_sha256": sha256_bytes(rebuilt_raw),
            "string_count": rebuilt_table.string_count,
        },
        "changed": [
            {
                "id": entry["id"],
                "ko": entry["ko"],
                "ko_utf16le_sha256": entry["ko_utf16le_sha256"],
                "affected_msgev_ids": entry["affected_msgev_ids"],
            }
            for entry in PATCHES
        ],
        "static_component_recompositions": recompositions,
        "verification": {
            "source_parse_rebuild_byte_identical": True,
            "non_target_texts_preserved": True,
            "candidate_parse_roundtrip": True,
            "wrapper_prefix_preserved": True,
            "input_unchanged_during_build": True,
            "observed_oichi_component_defect_reconstructed": True,
            "installed_game_files_modified": False,
        },
    }
    return candidate, report


def atomic_write(path: Path, blob: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(blob)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def ensure_output_is_safe(game_root: Path, output_root: Path) -> None:
    try:
        output_root.resolve().relative_to(game_root.resolve())
    except ValueError:
        return
    raise ComponentFixError("output root must be outside the supplied game root")


def cmd_verify(args: argparse.Namespace) -> int:
    _candidate, report = build_candidate(args.game_root.resolve())
    print(f"resource={RESOURCE.as_posix()}")
    print(f"changed={len(report['changed'])}")
    print("result=PASS")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    game_root = args.game_root.resolve()
    output_root = args.output_root.resolve()
    ensure_output_is_safe(game_root, output_root)
    candidate, report = build_candidate(game_root)
    output = output_root / RESOURCE
    report_path = output_root / "component_fix.build-report.v1.json"
    atomic_write(output, candidate)
    atomic_write(report_path, pretty_json(report))
    print(f"output={output}")
    print(f"report={report_path}")
    print(f"changed={len(report['changed'])}")
    print("installed_game_files_modified=False")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    verify = commands.add_parser("verify", help="validate the pinned input and build in memory")
    verify.add_argument("--game-root", type=Path, required=True)
    verify.set_defaults(func=cmd_verify)
    build = commands.add_parser("build", help="write a candidate only outside the game root")
    build.add_argument("--game-root", type=Path, required=True)
    build.add_argument("--output-root", type=Path, required=True)
    build.set_defaults(func=cmd_build)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError, ComponentFixError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
