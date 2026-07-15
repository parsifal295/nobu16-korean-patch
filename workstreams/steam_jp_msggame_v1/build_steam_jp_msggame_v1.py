#!/usr/bin/env python3
"""Build a Steam-1.1.7-native JP ``msggame.bin`` without touching the game.

The target archive is always rebuilt from the exact Steam JP stock resource.
Public overlays may contain only JP source hashes and Korean replacements.  A
candidate is accepted only when every block/record/literal coordinate and all
non-literal record bytes remain structurally identical to stock.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO_ROOT = SCRIPT.parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
MSGGAME_ROOT = REPO_ROOT / "workstreams" / "msggame"
sys.path[:0] = [str(TOOLS_ROOT), str(MSGGAME_ROOT)]

import build_common_message_overlay as common  # noqa: E402
import msggame_format as msggame  # noqa: E402
from nobu16_lz4 import decompress_wrapper  # noqa: E402


GAME_ROOT = Path(r"F:/SteamLibrary/steamapps/common/NOBU16")
RESOURCE = "MSG_PK/JP/msggame.bin"
DEFAULT_STOCK = GAME_ROOT / Path(RESOURCE)
OVERLAY_SCHEMA = "nobu16.kr.msggame-jp-literal-overlay.v1"
MANIFEST_SCHEMA = "nobu16.kr.steam-jp-msggame-build.v1"
RUNTIME_VERSION = "1.1.7"
STEAM_BUILD_ID = 18_823_764

STOCK_PIN = {
    "packed_size": 721_304,
    "packed_sha256": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "raw_size": 1_599_324,
    "raw_sha256": "F052DA62C584C024C1EAF67A706253525421E6068976657DF6A6C07EFCA5D4E8",
    "block_count": 18,
    "record_count": 21_751,
    "literal_count": 29_524,
    "semantic_target_count": 28_272,
}

DEFAULT_OVERLAYS = (
    {
        "path": REPO_ROOT
        / "workstreams"
        / "msggame_pk_jp_native_wave06"
        / "public"
        / "msggame_ko_pk_jp_native_steam_prior_rebased_9386.v1.json",
        "sha256": "9F2E8498E45899E55D8AF8221434DBB35D1D2660C96F43E678C0A065D059D974",
        "entry_count": 9_386,
    },
    {
        "path": REPO_ROOT
        / "workstreams"
        / "msggame_pk_jp_native_wave06"
        / "public"
        / "msggame_ko_pk_jp_native_steam_switch_v13_exact_14825.v1.json",
        "sha256": "40C2DCCCDBA0F0FCFD99063531C116F82006E7DFE078F67F930F5EBEDB328045",
        "entry_count": 14_825,
    },
)

EXPECTED_FOUNDATION = 24_211
EXPECTED_REMAINING = 4_061
CJK_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")
KANA_RE = re.compile(r"[\u3040-\u30FF\u31F0-\u31FF]")


class BuildError(ValueError):
    """A stock, overlay, structure, or output safety contract failed."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256(text.encode("utf-16-le"))


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def strict_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    folded: set[str] = set()
    for key, value in pairs:
        normalized = key.casefold()
        if normalized in folded:
            raise BuildError(f"duplicate or case-colliding JSON key: {key!r}")
        folded.add(normalized)
        result[key] = value
    return result


def load_json(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=strict_object,
            parse_constant=lambda value: (_ for _ in ()).throw(
                BuildError(f"invalid JSON constant: {value}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BuildError(f"invalid strict UTF-8 JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise BuildError(f"JSON root must be an object: {path}")
    return value, raw


def literal_map(archive: msggame.MsgGameArchive) -> dict[tuple[int, int, int], Any]:
    return {
        (literal.block_id, literal.record_id, literal.literal_id): literal
        for literal in msggame.iter_literals(archive)
    }


def coordinate_hash(coordinates: Iterable[tuple[int, int, int]]) -> str:
    payload = "".join(
        f"{block}:{record}:{literal}\n"
        for block, record, literal in sorted(coordinates)
    ).encode("ascii")
    return sha256(payload)


def has_source_script(text: str) -> bool:
    return bool(CJK_RE.search(text) or KANA_RE.search(text))


def normalized_structure_raw(archive: msggame.MsgGameArchive) -> bytes:
    """Remove only proved literal text, retaining every marker and bytecode byte."""
    replacements = {
        (literal.block_id, literal.record_id, literal.literal_id): ""
        for literal in msggame.iter_literals(archive)
    }
    return msggame.rebuild_raw_with_literals(archive, replacements)


def stock_context(packed: bytes) -> dict[str, Any]:
    if len(packed) != STOCK_PIN["packed_size"] or sha256(packed) != STOCK_PIN["packed_sha256"]:
        raise BuildError("Steam 1.1.7 JP msggame packed pin mismatch")
    header, raw = decompress_wrapper(packed)
    if len(raw) != STOCK_PIN["raw_size"] or sha256(raw) != STOCK_PIN["raw_sha256"]:
        raise BuildError("Steam 1.1.7 JP msggame raw pin mismatch")
    parsed = msggame.parse_packed_msggame(packed)
    literals = literal_map(parsed.archive)
    actual = {
        "block_count": len(parsed.archive.blocks),
        "record_count": parsed.archive.record_count,
        "literal_count": len(literals),
        "semantic_target_count": sum(
            has_source_script(literal.text) for literal in literals.values()
        ),
    }
    for key, expected in STOCK_PIN.items():
        if key in actual and actual[key] != expected:
            raise BuildError(f"Steam stock {key} mismatch: {actual[key]} != {expected}")
    if msggame.rebuild_raw_msggame(parsed.archive) != raw:
        raise BuildError("Steam stock raw parse/rebuild is not byte exact")
    return {
        "packed": packed,
        "header": header,
        "raw": raw,
        "parsed": parsed,
        "literals": literals,
        "coordinate_sha256": coordinate_hash(literals),
        "normalized_structure_sha256": sha256(normalized_structure_raw(parsed.archive)),
    }


def _reject_sc_keys(value: Any, location: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            folded = key.casefold()
            if (
                folded == "sc"
                or folded.startswith("sc_")
                or folded.endswith("_sc")
                or "_sc_" in folded
                or folded.startswith("source_sc")
                or folded.startswith("stock_sc")
            ):
                raise BuildError(f"SC source field is forbidden at {location}.{key}")
            _reject_sc_keys(child, f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_sc_keys(child, f"{location}[{index}]")


def load_overlay(
    path: Path,
    expected_sha256: str | None,
    expected_entry_count: int | None,
    stock: dict[str, Any],
) -> tuple[dict[tuple[int, int, int], str], dict[str, Any]]:
    value, raw = load_json(path)
    digest = sha256(raw)
    if expected_sha256 is not None and digest != expected_sha256:
        raise BuildError(f"overlay file pin mismatch: {path}")
    _reject_sc_keys(value)
    if value.get("schema") != OVERLAY_SCHEMA:
        raise BuildError(f"unsupported overlay schema: {path}")
    if value.get("resource") != RESOURCE or value.get("base_language") != "JP":
        raise BuildError(f"overlay is not Steam JP msggame: {path}")
    policy = value.get("distribution_policy")
    if (
        not isinstance(policy, dict)
        or policy.get("contains_commercial_source_text") is not False
        or policy.get("contains_complete_game_resource") is not False
    ):
        raise BuildError(f"overlay is not declared source-free: {path}")
    stock_jp = value.get("stock_jp")
    expected_stock = {
        "packed_size": STOCK_PIN["packed_size"],
        "packed_sha256": STOCK_PIN["packed_sha256"],
        "raw_size": STOCK_PIN["raw_size"],
        "raw_sha256": STOCK_PIN["raw_sha256"],
        "record_count": STOCK_PIN["record_count"],
        "literal_count": STOCK_PIN["literal_count"],
    }
    if stock_jp != expected_stock:
        raise BuildError(f"overlay Steam JP stock contract mismatch: {path}")
    entries = value.get("entries")
    if not isinstance(entries, list) or value.get("entry_count") != len(entries):
        raise BuildError(f"overlay entry array/count mismatch: {path}")
    if expected_entry_count is not None and len(entries) != expected_entry_count:
        raise BuildError(f"overlay expected entry count mismatch: {path}")

    replacements: dict[tuple[int, int, int], str] = {}
    allowed = {
        "block_id",
        "record_id",
        "literal_id",
        "source_jp_utf16le_sha256",
        "ko",
    }
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or set(entry) != allowed:
            raise BuildError(f"overlay entry {index} has unexpected fields: {path}")
        coordinate_values = (entry["block_id"], entry["record_id"], entry["literal_id"])
        if any(isinstance(item, bool) or not isinstance(item, int) or item < 0 for item in coordinate_values):
            raise BuildError(f"invalid coordinate at entry {index}: {path}")
        coordinate = tuple(coordinate_values)
        if coordinate in replacements:
            raise BuildError(f"duplicate coordinate {coordinate}: {path}")
        source_literal = stock["literals"].get(coordinate)
        if source_literal is None:
            raise BuildError(f"coordinate absent from Steam stock {coordinate}: {path}")
        source = source_literal.text
        if entry["source_jp_utf16le_sha256"] != text_hash(source):
            raise BuildError(f"JP source hash mismatch at {coordinate}: {path}")
        korean = entry["ko"]
        if not isinstance(korean, str) or has_source_script(korean):
            raise BuildError(f"source script leaked at {coordinate}: {path}")
        mismatches = common.invariant_mismatches(source, korean)
        if mismatches:
            raise BuildError(f"JP invariant mismatch at {coordinate}: {mismatches}")
        replacements[coordinate] = korean
    return replacements, {
        "overlay_id": value.get("overlay_id"),
        "path": path.resolve().relative_to(REPO_ROOT.resolve()).as_posix(),
        "sha256": digest,
        "entry_count": len(replacements),
    }


def build_blob(
    stock_packed: bytes,
    overlay_specs: Sequence[tuple[Path, str | None, int | None]],
    *,
    expected_foundation: int = EXPECTED_FOUNDATION,
    expected_remaining: int = EXPECTED_REMAINING,
) -> tuple[bytes, dict[str, Any]]:
    stock = stock_context(stock_packed)
    replacements: dict[tuple[int, int, int], str] = {}
    overlay_rows: list[dict[str, Any]] = []
    for path, expected_hash, expected_count in overlay_specs:
        current, row = load_overlay(path, expected_hash, expected_count, stock)
        overlap = set(replacements) & set(current)
        if overlap:
            raise BuildError(f"overlays overlap at {sorted(overlap)[:3]}")
        replacements.update(current)
        overlay_rows.append(row)
    if len(replacements) != expected_foundation:
        raise BuildError(
            f"foundation entry count changed: {len(replacements)} != {expected_foundation}"
        )

    candidate = msggame.rebuild_packed_with_literals(stock_packed, replacements)
    candidate_header, candidate_raw = decompress_wrapper(candidate)
    candidate_parsed = msggame.parse_packed_msggame(candidate)
    candidate_literals = literal_map(candidate_parsed.archive)
    if set(candidate_literals) != set(stock["literals"]):
        raise BuildError("candidate literal coordinate set differs from Steam stock")
    if len(candidate_parsed.archive.blocks) != STOCK_PIN["block_count"]:
        raise BuildError("candidate block count changed")
    if candidate_parsed.archive.record_count != STOCK_PIN["record_count"]:
        raise BuildError("candidate record count changed")
    source_block_counts = [len(block.records) for block in stock["parsed"].archive.blocks]
    target_block_counts = [len(block.records) for block in candidate_parsed.archive.blocks]
    if target_block_counts != source_block_counts:
        raise BuildError("candidate per-block record counts changed")
    if candidate_header.prefix != stock["header"].prefix:
        raise BuildError("candidate wrapper prefix changed")
    target_structure = sha256(normalized_structure_raw(candidate_parsed.archive))
    if target_structure != stock["normalized_structure_sha256"]:
        raise BuildError("candidate non-literal structure differs from Steam stock")

    for coordinate, source_literal in stock["literals"].items():
        expected = replacements.get(coordinate, source_literal.text)
        if candidate_literals[coordinate].text != expected:
            raise BuildError(f"candidate literal mismatch at {coordinate}")
    remaining_source_script = sum(
        has_source_script(literal.text) for literal in candidate_literals.values()
    )
    if remaining_source_script != expected_remaining:
        raise BuildError(
            f"remaining JP semantic count changed: {remaining_source_script} != {expected_remaining}"
        )

    manifest = {
        "schema": MANIFEST_SCHEMA,
        "runtime": {
            "distribution": "Steam",
            "pk_version": RUNTIME_VERSION,
            "steam_build_id": STEAM_BUILD_ID,
            "language_route": "JP",
        },
        "resource": RESOURCE,
        "source": {
            **{key: STOCK_PIN[key] for key in ("packed_size", "packed_sha256", "raw_size", "raw_sha256")},
            "block_count": STOCK_PIN["block_count"],
            "record_count": STOCK_PIN["record_count"],
            "literal_count": STOCK_PIN["literal_count"],
            "coordinate_sha256": stock["coordinate_sha256"],
            "normalized_structure_sha256": stock["normalized_structure_sha256"],
        },
        "overlays": overlay_rows,
        "translation": {
            "applied_entry_count": len(replacements),
            "semantic_target_count": STOCK_PIN["semantic_target_count"],
            "remaining_jp_semantic_count": remaining_source_script,
        },
        "target": {
            "packed_size": len(candidate),
            "packed_sha256": sha256(candidate),
            "raw_size": len(candidate_raw),
            "raw_sha256": sha256(candidate_raw),
            "block_count": len(candidate_parsed.archive.blocks),
            "record_count": candidate_parsed.archive.record_count,
            "literal_count": len(candidate_literals),
            "coordinate_sha256": coordinate_hash(candidate_literals),
            "normalized_structure_sha256": target_structure,
        },
        "checks": {
            "steam_stock_hash_gate": "PASS",
            "jp_source_hash_gate": "PASS",
            "sc_container_used": False,
            "overlay_coordinates_disjoint": True,
            "wrapper_prefix_preserved": True,
            "block_record_counts_preserved": True,
            "literal_coordinate_set_preserved": True,
            "non_literal_structure_preserved": True,
            "unchanged_literals_preserved": True,
            "replacement_literals_verified": True,
            "deterministic_rebuild": True,
            "installed_game_file_written": False,
        },
    }
    return candidate, manifest


def validate_output_root(path: Path) -> Path:
    resolved = path.resolve()
    tmp_root = (REPO_ROOT / "tmp").resolve()
    if resolved == tmp_root or tmp_root not in resolved.parents:
        raise BuildError(f"output must be a child of repository tmp: {resolved}")
    if resolved.exists() and any(resolved.iterdir()):
        raise BuildError(f"output must be absent or empty: {resolved}")
    return resolved


def default_overlay_specs() -> list[tuple[Path, str, int]]:
    return [
        (row["path"], row["sha256"], row["entry_count"])
        for row in DEFAULT_OVERLAYS
    ]


def command_build(args: argparse.Namespace) -> int:
    stock_path = args.stock.resolve()
    before = stock_path.read_bytes()
    overlays = (
        [(path.resolve(), None, None) for path in args.overlay]
        if args.overlay
        else default_overlay_specs()
    )
    with tempfile.TemporaryDirectory(prefix="steam_jp_msggame_ab_", dir=REPO_ROOT / "tmp"):
        first, first_manifest = build_blob(before, overlays)
        second, second_manifest = build_blob(before, overlays)
    if first != second or canonical_json(first_manifest) != canonical_json(second_manifest):
        raise BuildError("A/B rebuild is not deterministic")
    if stock_path.read_bytes() != before:
        raise BuildError("Steam stock changed during offline build")

    output_root = validate_output_root(args.output_root)
    candidate_path = output_root / "private" / "candidate" / Path(RESOURCE)
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.write_bytes(first)
    manifest_path = output_root / "build_manifest.json"
    manifest_path.write_bytes(canonical_json(first_manifest))
    print(f"candidate={candidate_path}")
    print(f"candidate_sha256={sha256(first)}")
    print(f"applied_entries={first_manifest['translation']['applied_entry_count']}")
    print(f"remaining_jp_semantic={first_manifest['translation']['remaining_jp_semantic_count']}")
    print("steam_stock_written=False")
    return 0


def command_verify(args: argparse.Namespace) -> int:
    stock = stock_context(args.stock.read_bytes())
    candidate = args.candidate.read_bytes()
    parsed = msggame.parse_packed_msggame(candidate)
    candidate_literals = literal_map(parsed.archive)
    if set(candidate_literals) != set(stock["literals"]):
        raise BuildError("candidate coordinate set mismatch")
    target_structure = sha256(normalized_structure_raw(parsed.archive))
    if target_structure != stock["normalized_structure_sha256"]:
        raise BuildError("candidate non-literal structure mismatch")
    print(f"candidate_sha256={sha256(candidate)}")
    print(f"records={parsed.archive.record_count}")
    print(f"literals={len(candidate_literals)}")
    print("steam_1_1_7_structure=PASS")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build")
    build.add_argument("--stock", type=Path, default=DEFAULT_STOCK)
    build.add_argument("--overlay", type=Path, action="append")
    build.add_argument(
        "--output-root",
        type=Path,
        default=REPO_ROOT / "tmp" / "steam_jp_msggame_v1_candidate",
    )
    build.set_defaults(handler=command_build)
    verify = sub.add_parser("verify")
    verify.add_argument("--stock", type=Path, default=DEFAULT_STOCK)
    verify.add_argument("--candidate", type=Path, required=True)
    verify.set_defaults(handler=command_verify)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.handler(args))
    except (BuildError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
