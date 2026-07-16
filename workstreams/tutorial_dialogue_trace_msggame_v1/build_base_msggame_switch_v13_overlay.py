#!/usr/bin/env python3
"""Build a source-free Steam JP base-msggame Korean overlay from Switch v1.3.

The running PK game still resolves shared map tutorial and advisor dialogue from
``MSG/JP/msggame.bin``.  That base resource was absent from the old 12-path
Steam candidate, which only carried the PK counterpart.  This builder proves
the Steam 1.1.7 base JP and the pinned Switch v1.3 resource have identical
literal coordinates, transfers only safe coordinate-exact Korean literals,
and never writes an installed game file.

The tracked public overlay deliberately contains Korean replacements plus
Steam-JP source hashes only: no original game prose and no complete resource.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any, Iterable


sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
TOOLS = REPO / "tools"
MSGGAME_TOOLS = REPO / "workstreams" / "msggame"
sys.path[:0] = [str(TOOLS), str(MSGGAME_TOOLS)]

import build_common_message_overlay as common  # noqa: E402
import msggame_format as msggame  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper_greedy  # noqa: E402


RESOURCE = "MSG/JP/msggame.bin"
SWITCH_MEMBER = "NobunagaShinsei_KR/romfs/MSG/JP/msggame.bin"
SCHEMA = "nobu16.kr.base-msggame-jp-switch-v13-exact-overlay.v1"
VALIDATION_SCHEMA = "nobu16.kr.base-msggame-jp-switch-v13-exact-validation.v1"
RUNTIME_VERSION = "1.1.7"
STEAM_BUILD_ID = 18_823_764

DEFAULT_GAME_ROOT = Path(r"F:/SteamLibrary/steamapps/common/NOBU16")
DEFAULT_SWITCH_ZIP = (
    REPO
    / "tmp"
    / "third_party_switch_v13"
    / "NobunagaShinsei_KoreanPatch_v1.3.zip"
)
OVERLAY_PATH = HERE / "public" / "msggame_ko_base_jp_switch_v13_exact_22924.v1.json"
VALIDATION_PATH = HERE / "validation.v1.json"

BASE_PIN = {
    "packed_size": 610_163,
    "packed_sha256": "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    "raw_size": 1_337_548,
    "raw_sha256": "353010B59A3E04BFE5541162229C1CFCAD181EF0E75FCC9B6DE2043BFC515F38",
    "block_count": 18,
    "record_count": 19_152,
    "literal_count": 24_262,
}
SWITCH_ZIP_PIN = {
    "size": 72_977_145,
    "sha256": "F4D2563C1B32DB450165C8CCF61C6947DEA904233581036E179AFA1D6A918CC4",
}
SWITCH_TEXT_PIN = {
    "packed_size": 487_964,
    "packed_sha256": "89CC6412B8548CA5CCADB6A2AB406D0EC4ED3ABCEBB8B703C4E324C0EAAB2F67",
    "raw_size": 1_498_434,
    "raw_sha256": "759C32FD7EFAABF70C6B82C45E21AB090D6B80CF88827247370AED9F163D6501",
    "block_count": 18,
    "record_count": 19_152,
    "literal_count": 24_262,
}
EXPECTED_ELIGIBLE_COUNT = 22_924
EXPECTED_COORDINATE_SHA256 = "4AD107EEC33B1DB759B2546F59C65566E94EFBE0AB24C5F1C89BBE36D25AD803"
EXPECTED_ENTRY_CONTRACT_SHA256 = "8BBBD9AD28AEB38F5E9DAD2E7E2ABF18957FB178376BE61BD6C2C8D07B07A0B2"
EXPECTED_NORMALIZED_STRUCTURE_SHA256 = "06DE8E4A0007E21C1479589C94D259ADD6A8A8E5BF91D5C0CC3BE92EA8BC019D"
EXPECTED_CANDIDATE = {
    "packed_size": 647_418,
    "packed_sha256": "72A81DABBDD5BC596356CF4F457B2235E439B2D27BD2FB00546842606531CE44",
    "raw_size": 1_490_068,
    "raw_sha256": "CAA61791F205A1FD3F3DB8FBEB479F2C6551104B7884AF663D4F23FF19542A93",
}

# This coordinate is the map-advisor tutorial line shown in the report.  Only
# hashes are retained for the JP source; Korean is intentionally sourced from
# the Switch-authorized Korean patch during model generation.
TUTORIAL_ANCHOR = (13, 217, 0)
TUTORIAL_ANCHOR_SOURCE_HASH = "279D8D1246B6C655F8E6FEC0DA1CAA7848AAA1E0EB58C1AA13370EBF5E84BC5B"
TUTORIAL_ANCHOR_KO_HASH = "0EA8FAF9225A94AF8A10296E06FC1AF873806B8C5CE10C53A2997836A7B42067"

CJK_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")
KANA_RE = re.compile(r"[\u3040-\u30FF\u31F0-\u31FF]")
HANGUL_RE = re.compile(r"[\uAC00-\uD7A3]")


class BaseMsgGameSwitchError(ValueError):
    """A source pin, transfer invariant, or public contract diverged."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256(text.encode("utf-16-le"))


def pretty_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def strict_json(path: Path) -> tuple[dict[str, Any], bytes]:
    blob = path.read_bytes()
    try:
        value = json.loads(blob.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BaseMsgGameSwitchError(f"invalid UTF-8 JSON: {path}") from exc
    if not isinstance(value, dict):
        raise BaseMsgGameSwitchError(f"JSON root is not an object: {path}")
    return value, blob


def literal_map(archive: msggame.MsgGameArchive) -> dict[tuple[int, int, int], Any]:
    return {
        (literal.block_id, literal.record_id, literal.literal_id): literal
        for literal in msggame.iter_literals(archive)
    }


def coordinate_hash(coordinates: Iterable[tuple[int, int, int]]) -> str:
    return sha256(
        "".join(f"{block}:{record}:{literal}\n" for block, record, literal in sorted(coordinates)).encode(
            "ascii"
        )
    )


def entry_contract_hash(
    entries: Iterable[dict[str, Any]],
) -> str:
    digest = hashlib.sha256()
    for entry in sorted(
        entries,
        key=lambda value: (value["block_id"], value["record_id"], value["literal_id"]),
    ):
        digest.update(
            f"{entry['block_id']}:{entry['record_id']}:{entry['literal_id']}:".encode("ascii")
        )
        digest.update(str(entry["source_jp_utf16le_sha256"]).encode("ascii"))
        digest.update(b":")
        digest.update(str(entry["ko_utf16le_sha256"]).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest().upper()


def has_japanese_script(text: str) -> bool:
    return CJK_RE.search(text) is not None or KANA_RE.search(text) is not None


def normalized_structure_raw(archive: msggame.MsgGameArchive) -> bytes:
    return msggame.rebuild_raw_with_literals(
        archive,
        {
            (literal.block_id, literal.record_id, literal.literal_id): ""
            for literal in msggame.iter_literals(archive)
        },
    )


def _require_pin(observed: dict[str, Any], expected: dict[str, Any], label: str) -> None:
    if observed != expected:
        raise BaseMsgGameSwitchError(f"{label} pin differs: {observed!r}")


def load_base(game_root: Path) -> dict[str, Any]:
    path = game_root / Path(RESOURCE)
    packed = path.read_bytes()
    if len(packed) != BASE_PIN["packed_size"] or sha256(packed) != BASE_PIN["packed_sha256"]:
        raise BaseMsgGameSwitchError("Steam 1.1.7 base msggame packed pin mismatch")
    header, raw = decompress_wrapper(packed)
    if len(raw) != BASE_PIN["raw_size"] or sha256(raw) != BASE_PIN["raw_sha256"]:
        raise BaseMsgGameSwitchError("Steam 1.1.7 base msggame raw pin mismatch")
    parsed = msggame.parse_packed_msggame(packed)
    literals = literal_map(parsed.archive)
    observed = {
        "block_count": len(parsed.archive.blocks),
        "record_count": parsed.archive.record_count,
        "literal_count": len(literals),
    }
    _require_pin(observed, {key: BASE_PIN[key] for key in observed}, "base msggame structure")
    if msggame.rebuild_raw_msggame(parsed.archive) != raw:
        raise BaseMsgGameSwitchError("base msggame raw parse/rebuild is not byte exact")
    if sha256(normalized_structure_raw(parsed.archive)) != EXPECTED_NORMALIZED_STRUCTURE_SHA256:
        raise BaseMsgGameSwitchError("base msggame normalized structure pin differs")
    return {
        "path": path,
        "packed": packed,
        "header": header,
        "raw": raw,
        "archive": parsed.archive,
        "literals": literals,
    }


def load_switch(switch_zip: Path) -> dict[str, Any]:
    zip_blob = switch_zip.read_bytes()
    _require_pin(
        {"size": len(zip_blob), "sha256": sha256(zip_blob)},
        SWITCH_ZIP_PIN,
        "Switch v1.3 ZIP",
    )
    with zipfile.ZipFile(switch_zip) as archive:
        try:
            packed = archive.read(SWITCH_MEMBER)
        except KeyError as exc:
            raise BaseMsgGameSwitchError("Switch v1.3 base msggame member is missing") from exc
    if (
        len(packed) != SWITCH_TEXT_PIN["packed_size"]
        or sha256(packed) != SWITCH_TEXT_PIN["packed_sha256"]
    ):
        raise BaseMsgGameSwitchError("Switch v1.3 base msggame packed pin mismatch")
    _header, raw = decompress_wrapper(packed)
    if len(raw) != SWITCH_TEXT_PIN["raw_size"] or sha256(raw) != SWITCH_TEXT_PIN["raw_sha256"]:
        raise BaseMsgGameSwitchError("Switch v1.3 base msggame raw pin mismatch")
    parsed = msggame.parse_raw_msggame(raw + b"\0" * ((-len(raw)) % 4))
    literals = literal_map(parsed)
    observed = {
        "block_count": len(parsed.blocks),
        "record_count": parsed.record_count,
        "literal_count": len(literals),
    }
    _require_pin(observed, {key: SWITCH_TEXT_PIN[key] for key in observed}, "Switch msggame structure")
    return {"packed": packed, "raw": raw, "archive": parsed, "literals": literals}


def eligible_coordinates(base: dict[str, Any], switch: dict[str, Any]) -> list[tuple[int, int, int]]:
    base_literals = base["literals"]
    switch_literals = switch["literals"]
    if set(base_literals) != set(switch_literals):
        raise BaseMsgGameSwitchError("Steam base and Switch v1.3 literal coordinate sets differ")
    result: list[tuple[int, int, int]] = []
    for coordinate in sorted(base_literals):
        source = base_literals[coordinate].text
        korean = switch_literals[coordinate].text
        if not has_japanese_script(source):
            continue
        if HANGUL_RE.search(korean) is None:
            continue
        if has_japanese_script(korean):
            continue
        if common.invariant_mismatches(source, korean):
            continue
        result.append(coordinate)
    if len(result) != EXPECTED_ELIGIBLE_COUNT:
        raise BaseMsgGameSwitchError(f"eligible literal count changed: {len(result)}")
    if coordinate_hash(result) != EXPECTED_COORDINATE_SHA256:
        raise BaseMsgGameSwitchError("eligible literal coordinate hash changed")
    if TUTORIAL_ANCHOR not in result:
        raise BaseMsgGameSwitchError("map tutorial anchor was not eligible")
    return result


def expected_overlay(base: dict[str, Any], switch: dict[str, Any]) -> dict[str, Any]:
    coordinates = eligible_coordinates(base, switch)
    entries = [
        {
            "block_id": coordinate[0],
            "record_id": coordinate[1],
            "literal_id": coordinate[2],
            "source_jp_utf16le_sha256": text_hash(base["literals"][coordinate].text),
            "ko": switch["literals"][coordinate].text,
            "ko_utf16le_sha256": text_hash(switch["literals"][coordinate].text),
        }
        for coordinate in coordinates
    ]
    if entry_contract_hash(entries) != EXPECTED_ENTRY_CONTRACT_SHA256:
        raise BaseMsgGameSwitchError("eligible literal entry contract hash changed")
    tutorial = next(
        entry
        for entry in entries
        if (entry["block_id"], entry["record_id"], entry["literal_id"]) == TUTORIAL_ANCHOR
    )
    if (
        tutorial["source_jp_utf16le_sha256"] != TUTORIAL_ANCHOR_SOURCE_HASH
        or tutorial["ko_utf16le_sha256"] != TUTORIAL_ANCHOR_KO_HASH
    ):
        raise BaseMsgGameSwitchError("map tutorial anchor hash differs")
    return {
        "schema": SCHEMA,
        "overlay_id": "msggame_ko_base_jp_switch_v13_exact_22924.v1",
        "resource": RESOURCE,
        "base_language": "JP",
        "runtime": {"steam_build_id": STEAM_BUILD_ID, "version": RUNTIME_VERSION},
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_jp": dict(BASE_PIN),
        "switch_v13": {
            "author": "snake7594",
            "asset_sha256": SWITCH_ZIP_PIN["sha256"],
            "member": SWITCH_MEMBER,
            "release_tag": "v1.3",
            "text": dict(SWITCH_TEXT_PIN),
        },
        "selection": {
            "base_japanese_literal_count": sum(
                has_japanese_script(literal.text) for literal in base["literals"].values()
            ),
            "coordinate_exact": True,
            "requires_hangul": True,
            "switch_japanese_script_rejected": True,
            "format_invariants_required": True,
        },
        "entry_count": len(entries),
        "entry_coordinate_sha256": coordinate_hash(coordinates),
        "entry_contract_sha256": entry_contract_hash(entries),
        "entries": entries,
    }


def load_overlay(base: dict[str, Any], switch: dict[str, Any]) -> tuple[dict[str, Any], bytes]:
    value, blob = strict_json(OVERLAY_PATH)
    expected = expected_overlay(base, switch)
    if value != expected:
        raise BaseMsgGameSwitchError("tracked base-msggame overlay differs from its pinned model")
    return value, blob


def build_blob(
    game_root: Path = DEFAULT_GAME_ROOT,
    switch_zip: Path = DEFAULT_SWITCH_ZIP,
) -> tuple[bytes, dict[str, Any]]:
    """Return the complete base-msggame candidate in memory; never writes Steam."""
    base = load_base(game_root)
    switch = load_switch(switch_zip)
    overlay, overlay_blob = load_overlay(base, switch)
    replacements: dict[tuple[int, int, int], str] = {}
    for entry in overlay["entries"]:
        coordinate = (int(entry["block_id"]), int(entry["record_id"]), int(entry["literal_id"]))
        if coordinate in replacements or coordinate not in base["literals"]:
            raise BaseMsgGameSwitchError(f"invalid overlay coordinate: {coordinate}")
        source = base["literals"][coordinate].text
        korean = str(entry["ko"])
        if text_hash(source) != entry["source_jp_utf16le_sha256"]:
            raise BaseMsgGameSwitchError(f"source hash mismatch at {coordinate}")
        if text_hash(korean) != entry["ko_utf16le_sha256"]:
            raise BaseMsgGameSwitchError(f"Korean hash mismatch at {coordinate}")
        if not has_japanese_script(source) or HANGUL_RE.search(korean) is None:
            raise BaseMsgGameSwitchError(f"selection predicate differs at {coordinate}")
        if has_japanese_script(korean) or common.invariant_mismatches(source, korean):
            raise BaseMsgGameSwitchError(f"transfer invariant differs at {coordinate}")
        replacements[coordinate] = korean
    if sorted(replacements) != eligible_coordinates(base, switch):
        raise BaseMsgGameSwitchError("overlay coordinate domain differs from selection")

    raw = msggame.rebuild_raw_with_literals(base["archive"], replacements)
    candidate = recompress_wrapper_greedy(raw, base["header"])
    _header, roundtrip = decompress_wrapper(candidate)
    if roundtrip != raw or candidate[:8] != base["packed"][:8]:
        raise BaseMsgGameSwitchError("greedy wrapper round-trip or prefix differs")
    parsed_candidate = msggame.parse_packed_msggame(candidate)
    candidate_literals = literal_map(parsed_candidate.archive)
    if set(candidate_literals) != set(base["literals"]):
        raise BaseMsgGameSwitchError("candidate literal coordinate set differs")
    changed = {
        coordinate
        for coordinate in base["literals"]
        if base["literals"][coordinate].text != candidate_literals[coordinate].text
    }
    if changed != set(replacements):
        raise BaseMsgGameSwitchError("candidate changed a non-selected literal")
    if any(candidate_literals[key].text != value for key, value in replacements.items()):
        raise BaseMsgGameSwitchError("candidate Korean literal differs")
    normalized_base = normalized_structure_raw(base["archive"])
    normalized_candidate = normalized_structure_raw(parsed_candidate.archive)
    if normalized_base != normalized_candidate:
        raise BaseMsgGameSwitchError("candidate changed opaque bytecode or structure")
    candidate_spec = {
        "packed_size": len(candidate),
        "packed_sha256": sha256(candidate),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
    }
    if candidate_spec != EXPECTED_CANDIDATE:
        raise BaseMsgGameSwitchError(f"candidate pin differs: {candidate_spec!r}")
    return candidate, {
        "resource": RESOURCE,
        "entry_count": len(replacements),
        "entry_coordinate_sha256": coordinate_hash(replacements),
        "entry_contract_sha256": overlay["entry_contract_sha256"],
        "stock": dict(BASE_PIN),
        "candidate": candidate_spec,
        "overlay": {"size": len(overlay_blob), "sha256": sha256(overlay_blob)},
        "normalized_structure_sha256": sha256(normalized_base),
        "non_selected_literals_preserved": True,
        "wrapper_prefix_preserved": True,
        "compression": "raw-lz4-greedy",
        "map_tutorial_anchor": {
            "coordinate": list(TUTORIAL_ANCHOR),
            "source_jp_utf16le_sha256": TUTORIAL_ANCHOR_SOURCE_HASH,
            "ko_utf16le_sha256": TUTORIAL_ANCHOR_KO_HASH,
        },
        "sc_binary_used": False,
    }


def validation_model(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": VALIDATION_SCHEMA,
        "status": "PASS",
        "resource": RESOURCE,
        "runtime": {"steam_build_id": STEAM_BUILD_ID, "version": RUNTIME_VERSION},
        "translation": {
            "eligible_switch_v13_exact_literals": EXPECTED_ELIGIBLE_COUNT,
            "map_tutorial_anchor_coordinate": list(TUTORIAL_ANCHOR),
            "map_tutorial_anchor_included": True,
        },
        "expected": {
            "stock": metrics["stock"],
            "candidate": metrics["candidate"],
            "overlay": metrics["overlay"],
        },
        "proofs": {
            "base_switch_coordinate_sets_equal": True,
            "entry_coordinate_sha256": metrics["entry_coordinate_sha256"],
            "entry_contract_sha256": metrics["entry_contract_sha256"],
            "normalized_structure_sha256": metrics["normalized_structure_sha256"],
            "non_selected_literals_preserved": metrics["non_selected_literals_preserved"],
            "wrapper_prefix_preserved": metrics["wrapper_prefix_preserved"],
            "deterministic_ab_equal": True,
        },
        "safety": {
            "complete_candidate_binary_tracked": False,
            "installed_game_files_modified": False,
            "sc_binary_used": False,
            "source_text_embedded": False,
        },
    }


def generate(
    game_root: Path = DEFAULT_GAME_ROOT,
    switch_zip: Path = DEFAULT_SWITCH_ZIP,
) -> dict[str, Any]:
    """Mechanically generate only the source-free overlay and validation JSON."""
    base = load_base(game_root)
    switch = load_switch(switch_zip)
    OVERLAY_PATH.parent.mkdir(parents=True, exist_ok=True)
    OVERLAY_PATH.write_bytes(pretty_bytes(expected_overlay(base, switch)))
    first, metrics = build_blob(game_root, switch_zip)
    second, second_metrics = build_blob(game_root, switch_zip)
    if first != second or metrics != second_metrics:
        raise BaseMsgGameSwitchError("deterministic A/B candidate differs")
    VALIDATION_PATH.write_bytes(pretty_bytes(validation_model(metrics)))
    return {"status": "GENERATED", **metrics, "deterministic_ab_equal": True}


def verify(
    game_root: Path = DEFAULT_GAME_ROOT,
    switch_zip: Path = DEFAULT_SWITCH_ZIP,
) -> dict[str, Any]:
    first, metrics = build_blob(game_root, switch_zip)
    second, second_metrics = build_blob(game_root, switch_zip)
    if first != second or metrics != second_metrics:
        raise BaseMsgGameSwitchError("deterministic A/B candidate differs")
    validation, _validation_blob = strict_json(VALIDATION_PATH)
    if validation != validation_model(metrics):
        raise BaseMsgGameSwitchError("tracked validation differs from model")
    return {"status": "PASS", **metrics, "deterministic_ab_equal": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("generate", "verify"))
    parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME_ROOT)
    parser.add_argument("--switch-zip", type=Path, default=DEFAULT_SWITCH_ZIP)
    args = parser.parse_args()
    result = (
        generate(args.game_root, args.switch_zip)
        if args.command == "generate"
        else verify(args.game_root, args.switch_zip)
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
