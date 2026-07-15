#!/usr/bin/env python3
"""Recover source-free PK msggame Korean entries from the Switch v1.3 text.

This batch is deliberately narrower than a human translation pass.  It only
publishes entries whose Switch Korean meaning can be aligned through an exact
PC base-JP/PK-JP UTF-16LE hash and then transformed into the pristine PK/SC
format with a mechanically proved rule.  Unresolved line redistribution and
two remaining ideographic annotations stay in the review index.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
MSGGAME_ROOT = REPO_ROOT / "workstreams" / "msggame"
V11_ROOT = REPO_ROOT / "workstreams" / "switch_msggame_v11"
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path[:0] = [str(MSGGAME_ROOT), str(V11_ROOT), str(TOOLS_ROOT)]

import build_switch_msggame_v11 as prior  # noqa: E402
import build_translation_batch1 as msggame_translation  # noqa: E402
from build_common_message_overlay import invariant_mismatches, message_invariants  # noqa: E402
from build_literal_overlay import OVERLAY_SCHEMA, apply_overlay_blob  # noqa: E402
from msggame_format import (  # noqa: E402
    iter_literals,
    parse_packed_msggame,
    parse_raw_msggame,
    rebuild_raw_msggame,
    sha256,
)
from nobu16_lz4 import decompress_wrapper  # noqa: E402


BATCH_ID = "switch_v13_pk_msggame_invariant_recovery_580.v1"
RESOURCE = "MSG_PK/SC/msggame.bin"
OVERLAY_NAME = "msggame_ko_switch_v13_invariant_recovery_580.v1.json"
EVIDENCE_NAME = "switch_v13_pk_msggame_invariant_recovery_evidence.v1.json"
REVIEW_NAME = "switch_v13_pk_msggame_invariant_recovery_review.v1.json"
VALIDATION_NAME = "switch_v13_pk_msggame_invariant_recovery_validation.v1.json"

SWITCH_MEMBER = "NobunagaShinsei_KR/romfs/MSG/JP/msggame.bin"
DEFAULT_V13_ZIP = REPO_ROOT / "tmp" / "third_party_switch_v13" / "NobunagaShinsei_KoreanPatch_v1.3.zip"
DEFAULT_V11_ZIP = REPO_ROOT / "tmp" / "third_party_switch_v11" / "NobunagaShinsei_KoreanPatch_v1.1.zip"
DEFAULT_PK_SC = (
    GAME_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "pk-full-messages-seoulhangang-v1"
    / "originals"
    / "MSG_PK"
    / "SC"
    / "msggame.bin"
)
DEFAULT_PROGRESS = REPO_ROOT / "data" / "public" / "translation_progress.v0.1.json"
DEFAULT_TARGET_CATALOG = REPO_ROOT / "data" / "public" / "translation_target_keys.v0.1.json"
SELF_RELATIVE = (WORKSTREAM_ROOT / "public" / OVERLAY_NAME).relative_to(REPO_ROOT).as_posix()
PREDECESSOR_BOUNDARY_RELATIVE = (
    V11_ROOT / "public" / "msggame_ko_switch_v11_exact_source_hash.v0.1.json"
).relative_to(REPO_ROOT).as_posix()
PREDECESSOR_PATHS_PIN = "7511C7F69132C4C99865FA7CE5533BB13CC633B9CCD8FCBA06645557FE3E6492"
SELF_COORDINATES_PIN = "C3272DBF2B18A63394BED427619D70E04C40D65B5874067EE0D9C68D67C25901"
SELF_OVERLAY_SHA256 = "9EF7210B5AA5F6842494EA75D79874AC009A9452855E4EC0FE79744284C6E61C"

V13_ZIP_PIN = {
    "size": 72_977_145,
    "sha256": "F4D2563C1B32DB450165C8CCF61C6947DEA904233581036E179AFA1D6A918CC4",
}
V11_ZIP_PIN = {
    "size": 73_040_529,
    "sha256": "931E7C5BDECD724E44987D722E71A12161448A1A583DFFB4A569A4FA58EC46F6",
}
SWITCH_TEXT_PIN = {
    "packed_size": 487_964,
    "packed_sha256": "89CC6412B8548CA5CCADB6A2AB406D0EC4ED3ABCEBB8B703C4E324C0EAAB2F67",
    "raw_size": 0x16DD42,
    "raw_sha256": "759C32FD7EFAABF70C6B82C45E21AB090D6B80CF88827247370AED9F163D6501",
    "padded_raw_size": 0x16DD44,
    "padded_raw_sha256": "63C95026686EC3BBFAED37700209B3440DE6BBAE52925D2C723DBFD64FB34523",
}

EXPECTED = {
    "existing_coordinate_union": 9_318,
    "target_coordinate_count": 16_482,
    "review_pool": 2_459,
    "invariant_mismatch_pool": 2_306,
    "forbidden_script_pool": 153,
    "edge_template": 407,
    "pc_pua_map": 15,
    "public_whitespace_variant": 7,
    "bullet_normalization": 151,
    "selected": 580,
    "excluded": 1_879,
    "unresolved_invariant_mismatch": 1_877,
    "unresolved_ideographic_annotation": 2,
}

# Switch controller-symbol codepoints are compatibility characters used as
# glyph selectors by the Switch font.  The PC SC path uses the corresponding
# private-use icons.  The mapping is proved by the pinned controller-help rows.
SWITCH_TO_PC_PUA = {
    0x334D: 0xE007,
    0x339D: 0xE015,
    0x3323: 0xE010,
    0x3351: 0xE00C,
    0x330D: 0xE00E,
    0x3326: 0xE00F,
    0x3357: 0xE00D,
    0x32A4: 0xE018,
    0x3239: 0xE01F,
    0x3318: 0xE008,
    0x3322: 0xE006,
    0x3327: 0xE009,
    0x3349: 0xE004,
    0x3314: 0xE005,
    0x332B: 0xE011,
    0x3336: 0xE00B,
    0x3303: 0xE00A,
}

OPEN_DELIMITERS = frozenset("[<{\u3008\u300a\u300c\u300e\u3010\u3014\uff3b\uff5b\u201c\u2018")
CLOSE_DELIMITERS = frozenset("]>}\u3009\u300b\u300d\u300f\u3011\u3015\uff3d\uff5d\u201d\u2019")
CJK_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")
KANA_RE = re.compile(r"[\u3040-\u30FF\u31F0-\u31FF]")


class RecoveryError(ValueError):
    """Raised when a recovery proof or pinned input changes."""


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-16-le")).hexdigest().upper()


def canonical_hash(value: Any) -> str:
    blob = json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return sha256(blob)


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {"path": path.relative_to(path.parents[1]).as_posix(), "size": len(blob), "sha256": sha256(blob)}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RecoveryError(f"JSON root is not an object: {path}")
    return value


def literal_map(archive: Any) -> dict[tuple[int, int, int], Any]:
    return {(item.block_id, item.record_id, item.literal_id): item for item in iter_literals(archive)}


def delimiter_roles(text: str) -> tuple[str, ...]:
    return tuple(
        "open" if character in OPEN_DELIMITERS else "close"
        for character in text
        if character in OPEN_DELIMITERS or character in CLOSE_DELIMITERS
    )


def delimiter_glyph_hash(text: str) -> str:
    glyphs = "".join(
        character
        for character in text
        if character in OPEN_DELIMITERS or character in CLOSE_DELIMITERS
    )
    return text_hash(glyphs)


def script_counts(text: str) -> dict[str, int]:
    return {"cjk_unified_count": len(CJK_RE.findall(text)), "kana_count": len(KANA_RE.findall(text))}


def mismatch_keys(source: str, replacement: str) -> tuple[str, ...]:
    return tuple(item.split(":", 1)[0] for item in invariant_mismatches(source, replacement))


def edge_template(source: str, replacement: str) -> str:
    """Use only the pristine SC leading/trailing whitespace template."""

    source_inv = message_invariants(source)
    replacement_inv = message_invariants(replacement)
    core = replacement[len(replacement_inv["leading_whitespace"]) :]
    trailing = replacement_inv["trailing_whitespace"]
    if trailing:
        core = core[: -len(trailing)]
    return source_inv["leading_whitespace"] + core + source_inv["trailing_whitespace"]


def semantic_whitespace_key(text: str) -> str:
    return " ".join(text.split())


def replace_switch_icons(text: str) -> str:
    return "".join(chr(SWITCH_TO_PC_PUA.get(ord(character), ord(character))) for character in text)


def source_structure(text: str) -> dict[str, Any]:
    invariant = message_invariants(text)
    return {
        "printf_tokens": invariant["printf"],
        "unknown_percent_count": invariant["unknown_percent_count"],
        "escape_sequences": invariant["esc"],
        "control_codepoints": invariant["controls"],
        "line_breaks": invariant["line_breaks"],
        "private_use_codepoints": invariant["pua"],
        "leading_whitespace_sha256": text_hash(invariant["leading_whitespace"]),
        "trailing_whitespace_sha256": text_hash(invariant["trailing_whitespace"]),
        "delimiter_roles": list(delimiter_roles(text)),
        "delimiter_glyphs_sha256": delimiter_glyph_hash(text),
    }


def load_switch(zip_path: Path, zip_pin: dict[str, Any]) -> dict[str, Any]:
    zip_blob = zip_path.read_bytes()
    actual_zip = {"size": len(zip_blob), "sha256": sha256(zip_blob)}
    if actual_zip != zip_pin:
        raise RecoveryError(f"Switch ZIP pin mismatch: {actual_zip!r}")
    with zipfile.ZipFile(zip_path) as archive:
        matches = [item for item in archive.infolist() if item.filename == SWITCH_MEMBER]
        if len(matches) != 1:
            raise RecoveryError(f"Switch msggame member count is {len(matches)}, expected 1")
        packed = archive.read(matches[0])
    _header, raw = decompress_wrapper(packed)
    padded = raw + b"\0\0"
    actual_text = {
        "packed_size": len(packed),
        "packed_sha256": sha256(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
        "padded_raw_size": len(padded),
        "padded_raw_sha256": sha256(padded),
    }
    if actual_text != SWITCH_TEXT_PIN:
        raise RecoveryError(f"Switch msggame pin mismatch: {actual_text!r}")
    archive = parse_raw_msggame(padded)
    if rebuild_raw_msggame(archive) != padded:
        raise RecoveryError("Switch msggame padded parse/rebuild is not byte-identical")
    if zip_path.read_bytes() != zip_blob:
        raise RecoveryError("Switch ZIP changed during read-only load")
    return {"packed": packed, "raw": raw, "padded": padded, "archive": archive}


def load_target_catalog(path: Path) -> dict[str, Any]:
    catalog = read_json(path)
    resources = catalog.get("resources")
    if not isinstance(resources, list):
        raise RecoveryError("target catalog resources is not an array")
    matches = [item for item in resources if item.get("path") == RESOURCE]
    if len(matches) != 1:
        raise RecoveryError("target catalog must contain exactly one PK msggame resource")
    item = matches[0]
    coordinates = {tuple(value) for value in item.get("target_coordinates", [])}
    if len(coordinates) != EXPECTED["target_coordinate_count"]:
        raise RecoveryError("target coordinate count changed")
    if item.get("target_keys_sha256") != "60D7053C25D2AEA8D565A22BC7AFA7C18F233698EFB0975B54996665A02931AF":
        raise RecoveryError("target coordinate catalog hash changed")
    if canonical_hash(sorted([list(value) for value in coordinates])) != item["target_keys_sha256"]:
        raise RecoveryError("target coordinate payload does not match its hash")
    return {"coordinates": coordinates, "hash": item["target_keys_sha256"]}


def _load_overlay_coordinates(path: Path) -> tuple[dict[str, Any], set[tuple[int, int, int]]]:
    overlay = read_json(path)
    if overlay.get("resource") != RESOURCE or not isinstance(overlay.get("entries"), list):
        raise RecoveryError(f"invalid existing msggame overlay: {path}")
    coordinates: set[tuple[int, int, int]] = set()
    for entry in overlay["entries"]:
        coordinate = (entry.get("block_id"), entry.get("record_id"), entry.get("literal_id"))
        if not all(type(value) is int for value in coordinate):
            raise RecoveryError(f"invalid existing coordinate: {path}")
        if coordinate in coordinates:
            raise RecoveryError(f"duplicate coordinate in msggame overlay: {path}")
        ko = entry.get("ko")
        if not isinstance(ko, str):
            raise RecoveryError(f"existing overlay has invalid Korean text: {path}")
        coordinates.add(coordinate)
    if overlay.get("entry_count") not in (None, len(coordinates)):
        raise RecoveryError(f"entry_count mismatch in msggame overlay: {path}")
    return overlay, coordinates


def collect_overlay_history(
    progress_path: Path,
    *,
    target_catalog_path: Path,
    predecessor_boundary_relative: str,
    predecessor_paths_pin: str,
    predecessor_coordinate_count: int,
    self_relative: str,
    self_batch_id: str,
    self_coordinate_count: int,
    self_coordinates_pin: str,
    self_overlay_sha256: str,
    collect_variants: bool = False,
) -> dict[str, Any]:
    """Pin historical predecessors and only validate later registrations.

    Appending a source-free, target-only, disjoint successor must never feed a
    historical batch's selection.  The successor still has to pass the public
    overlay contract so a bad registration cannot be silently ignored.
    """

    progress = read_json(progress_path)
    resources = progress.get("resources")
    matches = [item for item in resources if item.get("path") == RESOURCE] if isinstance(resources, list) else []
    if len(matches) != 1:
        raise RecoveryError("progress must contain exactly one PK msggame resource")
    patterns = matches[0].get("overlay_globs")
    if not isinstance(patterns, list) or not all(isinstance(item, str) for item in patterns):
        raise RecoveryError("PK msggame overlay_globs is invalid")
    if patterns.count(predecessor_boundary_relative) != 1:
        raise RecoveryError("pinned predecessor boundary must be registered exactly once")
    self_count = patterns.count(self_relative)
    if self_count not in (0, 1):
        raise RecoveryError("self overlay must be absent or registered exactly once")

    marker = patterns.index(predecessor_boundary_relative)
    predecessor_patterns = patterns[: marker + 1]
    if canonical_hash(predecessor_patterns) != predecessor_paths_pin:
        raise RecoveryError("pinned predecessor overlay prefix changed")

    resolved: list[tuple[str, str, Path]] = []
    for pattern in patterns:
        found = sorted(REPO_ROOT.glob(pattern))
        if len(found) != 1:
            raise RecoveryError(f"progress pattern {pattern!r} resolved to {len(found)} files")
        path = found[0]
        logical = path.relative_to(REPO_ROOT).as_posix()
        if logical == self_relative and pattern != self_relative:
            raise RecoveryError("self overlay must use its exact logical path")
        resolved.append((pattern, logical, path))

    target_coordinates = load_target_catalog(target_catalog_path)["coordinates"]
    self_path = REPO_ROOT / self_relative
    self_overlay, self_coordinates = _load_overlay_coordinates(self_path)
    if self_overlay.get("overlay_id") != self_batch_id:
        raise RecoveryError("checked self overlay_id changed")
    if len(self_coordinates) != self_coordinate_count:
        raise RecoveryError("checked self coordinate count changed")
    if canonical_hash(sorted([list(value) for value in self_coordinates])) != self_coordinates_pin:
        raise RecoveryError("checked self coordinate set changed")
    if sha256(self_path.read_bytes()) != self_overlay_sha256:
        raise RecoveryError("checked self overlay SHA-256 changed")
    if not self_coordinates <= target_coordinates:
        raise RecoveryError("checked self overlay escaped the exact target catalog")
    self_policy = self_overlay.get("distribution_policy")
    if (
        not isinstance(self_policy, dict)
        or self_policy.get("contains_commercial_source_text") is not False
        or self_policy.get("contains_complete_game_resource") is not False
        or script_counts(self_path.read_text(encoding="utf-8"))
        != {"cjk_unified_count": 0, "kana_count": 0}
    ):
        raise RecoveryError("checked self overlay is not source-free")

    predecessor_coordinates: set[tuple[int, int, int]] = set()
    predecessor_inputs: list[dict[str, Any]] = []
    variants: dict[str, dict[str, set[tuple[str, tuple[int, int, int]]]]] = defaultdict(
        lambda: defaultdict(set)
    )
    for _pattern, logical, path in resolved[: marker + 1]:
        overlay, coordinates = _load_overlay_coordinates(path)
        overlap = predecessor_coordinates & coordinates
        if overlap:
            raise RecoveryError(f"pinned predecessor overlays overlap at {min(overlap)}")
        predecessor_coordinates.update(coordinates)
        predecessor_inputs.append(
            {"path": logical, "size": path.stat().st_size, "sha256": sha256(path.read_bytes())}
        )
        if collect_variants:
            for entry in overlay["entries"]:
                coordinate = (entry["block_id"], entry["record_id"], entry["literal_id"])
                ko = entry["ko"]
                variants[semantic_whitespace_key(ko)][ko].add((logical, coordinate))
    if len(predecessor_coordinates) != predecessor_coordinate_count:
        raise RecoveryError(f"pinned predecessor coordinate union changed: {len(predecessor_coordinates)}")
    if predecessor_coordinates & self_coordinates:
        raise RecoveryError("checked self overlay overlaps a pinned predecessor")

    successor_coordinates: set[tuple[int, int, int]] = set()
    successor_paths: list[str] = []
    for pattern, logical, path in resolved[marker + 1 :]:
        if logical == self_relative:
            continue
        if pattern != logical:
            raise RecoveryError("successor overlays must use exact logical paths")
        overlay, coordinates = _load_overlay_coordinates(path)
        policy = overlay.get("distribution_policy")
        if (
            not isinstance(policy, dict)
            or policy.get("contains_commercial_source_text") is not False
            or policy.get("contains_complete_game_resource") is not False
            or script_counts(path.read_text(encoding="utf-8"))
            != {"cjk_unified_count": 0, "kana_count": 0}
        ):
            raise RecoveryError(f"successor overlay is not source-free: {logical}")
        outside_target = coordinates - target_coordinates
        if outside_target:
            raise RecoveryError(f"successor overlay escaped the target catalog at {min(outside_target)}: {logical}")
        overlap = coordinates & self_coordinates
        if overlap:
            raise RecoveryError(f"successor overlay overlaps this batch at {min(overlap)}: {logical}")
        overlap = coordinates & predecessor_coordinates
        if overlap:
            raise RecoveryError(f"successor overlay overlaps a pinned predecessor at {min(overlap)}: {logical}")
        overlap = coordinates & successor_coordinates
        if overlap:
            raise RecoveryError(f"successor overlays overlap at {min(overlap)}: {logical}")
        successor_coordinates.update(coordinates)
        successor_paths.append(logical)

    return {
        "predecessor_coordinates": predecessor_coordinates,
        "predecessor_paths": predecessor_patterns,
        "predecessor_inputs": predecessor_inputs,
        "predecessor_normalized_sha256": canonical_hash(predecessor_inputs),
        "variants": variants,
        "self_registration_count": self_count,
        "successor_coordinates": successor_coordinates,
        "successor_paths": successor_paths,
        "all_coordinates": predecessor_coordinates | successor_coordinates,
    }


def collect_existing(
    progress_path: Path, target_catalog_path: Path = DEFAULT_TARGET_CATALOG
) -> dict[str, Any]:
    history = collect_overlay_history(
        progress_path,
        target_catalog_path=target_catalog_path,
        predecessor_boundary_relative=PREDECESSOR_BOUNDARY_RELATIVE,
        predecessor_paths_pin=PREDECESSOR_PATHS_PIN,
        predecessor_coordinate_count=EXPECTED["existing_coordinate_union"],
        self_relative=SELF_RELATIVE,
        self_batch_id=BATCH_ID,
        self_coordinate_count=EXPECTED["selected"],
        self_coordinates_pin=SELF_COORDINATES_PIN,
        self_overlay_sha256=SELF_OVERLAY_SHA256,
        collect_variants=True,
    )
    resolved_paths = history["predecessor_paths"]
    return {
        "coordinates": history["predecessor_coordinates"],
        "variants": history["variants"],
        "resolved_paths": resolved_paths,
        "self_registration_count": history["self_registration_count"],
        "normalized_input_hash": canonical_hash(resolved_paths),
        "successor_coordinates": history["successor_coordinates"],
        "successor_paths": history["successor_paths"],
    }


def is_exact_replacement(source: str, replacement: str) -> bool:
    return (
        not invariant_mismatches(source, replacement)
        and script_counts(replacement) == {"cjk_unified_count": 0, "kana_count": 0}
        and prior.has_hangul_syllable(replacement)
    )


def choose_recovery(
    *, source: str, switch_ko: str, existing_variants: dict[str, dict[str, set[Any]]]
) -> tuple[str, str, list[dict[str, Any]]] | None:
    """Return one proved replacement using disjoint, ordered selection rules."""

    original_mismatches = mismatch_keys(source, switch_ko)
    if original_mismatches:
        edge = edge_template(source, switch_ko)
        if (
            is_exact_replacement(source, edge)
            and msggame_translation.bracket_sequence(source)
            == msggame_translation.bracket_sequence(edge)
        ):
            return "edge_template", edge, []

        pua = edge_template(source, replace_switch_icons(switch_ko))
        if (
            "pua" in original_mismatches
            and is_exact_replacement(source, pua)
            and msggame_translation.bracket_sequence(source)
            == msggame_translation.bracket_sequence(pua)
        ):
            return "pc_pua_map", pua, []

        matching_variants: list[tuple[str, set[Any]]] = []
        for value, origins in existing_variants.get(semantic_whitespace_key(switch_ko), {}).items():
            if (
                is_exact_replacement(source, value)
                and msggame_translation.bracket_sequence(source)
                == msggame_translation.bracket_sequence(value)
            ):
                matching_variants.append((value, origins))
        if len(matching_variants) == 1:
            value, origins = matching_variants[0]
            references = [
                {"overlay_path": path, "coordinate": list(coordinate)}
                for path, coordinate in sorted(origins)
            ]
            return "public_whitespace_variant", value, references
        return None

    forbidden = script_counts(switch_ko)
    script_codepoints = {
        ord(character)
        for character in switch_ko
        if CJK_RE.fullmatch(character) or KANA_RE.fullmatch(character)
    }
    if forbidden["cjk_unified_count"] == 0 and script_codepoints == {0x30FB}:
        replacement = switch_ko.replace(chr(0x30FB), chr(0x00B7))
        if (
            is_exact_replacement(source, replacement)
            and delimiter_roles(source) == delimiter_roles(replacement)
        ):
            return "bullet_normalization", replacement, []
    return None


def assert_source_free(paths: Iterable[Path]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for path in paths:
        counts = script_counts(path.read_text(encoding="utf-8"))
        result[path.name] = counts
        if counts != {"cjk_unified_count": 0, "kana_count": 0}:
            raise RecoveryError(f"source script leaked into artifact: {path}")
    return result


def build(args: argparse.Namespace) -> dict[str, Any]:
    v13_path = args.switch_v13_zip.resolve()
    v11_path = args.switch_v11_zip.resolve()
    base_jp_path = args.base_jp.resolve()
    pk_jp_path = args.pk_jp.resolve()
    pk_sc_path = args.pk_sc.resolve()
    progress_path = args.progress.resolve()
    target_catalog_path = args.target_catalog.resolve()
    input_paths = (v13_path, v11_path, base_jp_path, pk_jp_path, pk_sc_path, progress_path, target_catalog_path)
    before = {str(path): sha256(path.read_bytes()) for path in input_paths}

    v13 = load_switch(v13_path, V13_ZIP_PIN)
    v11 = load_switch(v11_path, V11_ZIP_PIN)
    if v13["packed"] != v11["packed"] or v13["raw"] != v11["raw"]:
        raise RecoveryError("Switch v1.3 msggame text differs from pinned v1.1")
    base_jp = prior.load_standard_source(base_jp_path, "base_jp")
    pk_jp = prior.load_standard_source(pk_jp_path, "pk_jp")
    pk_sc = prior.load_standard_source(pk_sc_path, "pk_sc")
    target_catalog = load_target_catalog(target_catalog_path)
    existing = collect_existing(progress_path, target_catalog_path)

    base_literals = literal_map(base_jp["archive"])
    switch_literals = literal_map(v13["archive"])
    pk_jp_literals = literal_map(pk_jp["archive"])
    pk_sc_literals = literal_map(pk_sc["archive"])
    switch_values, occurrences = prior.build_switch_value_map(
        base_literals,
        switch_literals,
        prior.record_map(base_jp["archive"]),
        prior.record_map(v13["archive"]),
    )

    counters: Counter[str] = Counter()
    selected: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    for coordinate in sorted(pk_jp_literals):
        pk_jp_literal = pk_jp_literals[coordinate]
        pk_sc_literal = pk_sc_literals.get(coordinate)
        if pk_sc_literal is None or coordinate not in target_catalog["coordinates"]:
            continue
        source_hash = text_hash(pk_jp_literal.text)
        values = switch_values.get(source_hash)
        if values is None or len(values) != 1:
            continue
        switch_ko = next(iter(values))
        if (
            switch_ko == pk_jp_literal.text
            or not prior.has_semantic_text(switch_ko)
            or not prior.has_hangul_syllable(switch_ko)
            or not prior.is_visible_translation_candidate(pk_sc_literal.text)
            or coordinate in existing["coordinates"]
        ):
            continue

        mismatches = mismatch_keys(pk_sc_literal.text, switch_ko)
        forbidden = script_counts(switch_ko)
        if mismatches:
            counters["invariant_mismatch_pool"] += 1
        elif forbidden != {"cjk_unified_count": 0, "kana_count": 0}:
            counters["forbidden_script_pool"] += 1
        else:
            continue
        counters["review_pool"] += 1

        recovery = choose_recovery(
            source=pk_sc_literal.text,
            switch_ko=switch_ko,
            existing_variants=existing["variants"],
        )
        if recovery is None:
            reason = (
                "unresolved_invariant_mismatch"
                if mismatches
                else "unresolved_ideographic_annotation"
            )
            counters[reason] += 1
            exclusions.append(
                {
                    "block_id": coordinate[0],
                    "record_id": coordinate[1],
                    "literal_id": coordinate[2],
                    "status": "excluded",
                    "reason": reason,
                    "human_review_required": True,
                    "pk_jp_utf16le_sha256": source_hash,
                    "pk_sc_utf16le_sha256": text_hash(pk_sc_literal.text),
                    "switch_ko_utf16le_sha256": text_hash(switch_ko),
                    "invariant_mismatch_keys": list(mismatches),
                    "forbidden_script_counts": forbidden,
                    "delimiter_roles_equal": delimiter_roles(pk_sc_literal.text) == delimiter_roles(switch_ko),
                }
            )
            continue

        mode, replacement, references = recovery
        counters[mode] += 1
        selected.append(
            {
                "coordinate": coordinate,
                "mode": mode,
                "replacement": replacement,
                "pk_jp_hash": source_hash,
                "pk_sc_hash": text_hash(pk_sc_literal.text),
                "switch_ko_hash": text_hash(switch_ko),
                "replacement_hash": text_hash(replacement),
                "source_occurrences": occurrences[source_hash],
                "source_structure": source_structure(pk_sc_literal.text),
                "replacement_structure": source_structure(replacement),
                "references": references,
            }
        )

    actual = {
        "existing_coordinate_union": len(existing["coordinates"]),
        "target_coordinate_count": len(target_catalog["coordinates"]),
        "review_pool": counters["review_pool"],
        "invariant_mismatch_pool": counters["invariant_mismatch_pool"],
        "forbidden_script_pool": counters["forbidden_script_pool"],
        "edge_template": counters["edge_template"],
        "pc_pua_map": counters["pc_pua_map"],
        "public_whitespace_variant": counters["public_whitespace_variant"],
        "bullet_normalization": counters["bullet_normalization"],
        "selected": len(selected),
        "excluded": len(exclusions),
        "unresolved_invariant_mismatch": counters["unresolved_invariant_mismatch"],
        "unresolved_ideographic_annotation": counters["unresolved_ideographic_annotation"],
    }
    if actual != EXPECTED:
        raise RecoveryError(f"selection changed: expected {EXPECTED!r}, got {actual!r}")

    selected_coordinates = [item["coordinate"] for item in selected]
    excluded_coordinates = [
        (item["block_id"], item["record_id"], item["literal_id"]) for item in exclusions
    ]
    if len(selected_coordinates) != len(set(selected_coordinates)):
        raise RecoveryError("selected coordinates are not unique")
    if set(selected_coordinates) & existing["coordinates"]:
        raise RecoveryError("selected coordinates overlap an existing overlay")
    if not set(selected_coordinates) <= target_catalog["coordinates"]:
        raise RecoveryError("selected coordinates escape the exact target catalog")
    if set(selected_coordinates) & set(excluded_coordinates):
        raise RecoveryError("selected and excluded coordinates overlap")
    if any(
        item["source_structure"]["delimiter_roles"]
        != item["replacement_structure"]["delimiter_roles"]
        for item in selected
    ):
        raise RecoveryError("selected replacement changed the delimiter role sequence")

    class_coordinates = {
        mode: sorted([list(item["coordinate"]) for item in selected if item["mode"] == mode])
        for mode in ("edge_template", "pc_pua_map", "public_whitespace_variant", "bullet_normalization")
    }
    class_manifest = {
        mode: {"count": len(values), "coordinates_sha256": canonical_hash(values)}
        for mode, values in class_coordinates.items()
    }

    overlay_entries = [
        {
            "block_id": item["coordinate"][0],
            "record_id": item["coordinate"][1],
            "literal_id": item["coordinate"][2],
            "source_sc_utf16le_sha256": item["pk_sc_hash"],
            "ko": item["replacement"],
        }
        for item in selected
    ]
    overlay = {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "defaults": {"status": "translated"},
        "entry_count": len(overlay_entries),
        "distribution_policy": {"contains_commercial_source_text": False, "contains_complete_game_resource": False},
        "migration_provenance": {
            "kind": "third_party_switch_v13_invariant_recovery",
            "author": "snake7594",
            "repository_url": "https://github.com/snake7594/nobunaga-shinsei-korean-patch",
            "release_tag": "v1.3",
            "asset_sha256": V13_ZIP_PIN["sha256"],
            "v13_text_identical_to_v11": True,
            "source_text_embedded": False,
        },
        "stock_sc": {
            "packed_size": len(pk_sc["packed"]),
            "packed_sha256": sha256(pk_sc["packed"]),
            "raw_size": len(pk_sc["raw"]),
            "raw_sha256": sha256(pk_sc["raw"]),
            "record_count": pk_sc["archive"].record_count,
            "literal_slot_count": len(pk_sc_literals),
        },
        "entries": overlay_entries,
    }

    evidence_entries = [
        {
            "block_id": item["coordinate"][0],
            "record_id": item["coordinate"][1],
            "literal_id": item["coordinate"][2],
            "selection_class": item["mode"],
            "pk_jp_utf16le_sha256": item["pk_jp_hash"],
            "pk_sc_utf16le_sha256": item["pk_sc_hash"],
            "switch_ko_utf16le_sha256": item["switch_ko_hash"],
            "replacement_utf16le_sha256": item["replacement_hash"],
            "source_occurrence_count": item["source_occurrences"],
            "pk_sc_structure": item["source_structure"],
            "replacement_structure": item["replacement_structure"],
            "invariants_exact_after_recovery": True,
            "delimiter_role_sequence_equal": item["source_structure"]["delimiter_roles"] == item["replacement_structure"]["delimiter_roles"],
            "public_variant_references": item["references"],
        }
        for item in selected
    ]
    evidence = {
        "schema": "nobu16.kr.switch-msggame-v13-invariant-recovery-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "source_free": True,
        "provenance": {
            "repository_url": "https://github.com/snake7594/nobunaga-shinsei-korean-patch",
            "v13_zip_sha256": V13_ZIP_PIN["sha256"],
            "v11_zip_sha256": V11_ZIP_PIN["sha256"],
            "v13_v11_msggame_byte_identical": True,
            "msggame_packed_sha256": SWITCH_TEXT_PIN["packed_sha256"],
        },
        "target_catalog": {
            "path": target_catalog_path.relative_to(REPO_ROOT).as_posix(),
            "coordinate_count": len(target_catalog["coordinates"]),
            "coordinates_sha256": target_catalog["hash"],
            "selected_is_subset": True,
        },
        "existing_overlay_exclusion": {
            "coordinate_union": len(existing["coordinates"]),
            "resolved_paths": existing["resolved_paths"],
            "normalized_input_sha256": existing["normalized_input_hash"],
            "self_path": SELF_RELATIVE,
            "self_registration_states_supported": [0, 1],
            "self_excluded_before_selection": True,
        },
        "selection": actual,
        "selection_classes": class_manifest,
        "selected_coordinates_sha256": canonical_hash(sorted([list(value) for value in selected_coordinates])),
        "excluded_coordinates_sha256": canonical_hash(sorted([list(value) for value in excluded_coordinates])),
        "entry_count": len(evidence_entries),
        "entries": evidence_entries,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.switch-msggame-v13-invariant-recovery-review.v1",
        "batch_id": BATCH_ID,
        "quality_state": "proved_subset_translated_unresolved_pool_excluded",
        "selected_count": len(selected),
        "excluded_count": len(exclusions),
        "entries": [
            {
                "block_id": item["coordinate"][0],
                "record_id": item["coordinate"][1],
                "literal_id": item["coordinate"][2],
                "status": "translated",
                "selection_class": item["mode"],
                "automated_proof": True,
                "human_review_required": True,
                "runtime_reviewed": False,
            }
            for item in selected
        ] + exclusions,
        "contains_commercial_source_text": False,
    }

    out_root = args.out_root.resolve()
    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    artifacts = {
        "overlay": write_json(overlay_path, overlay),
        "evidence": write_json(evidence_path, evidence),
        "review": write_json(review_path, review),
    }
    source_free_scan = assert_source_free((overlay_path, evidence_path, review_path))

    rebuilt, binary_manifest = apply_overlay_blob(pk_sc["packed"], overlay)
    parsed = parse_packed_msggame(rebuilt)
    rebuilt_literals = literal_map(parsed.archive)
    if set(rebuilt_literals) != set(pk_sc_literals):
        raise RecoveryError("offline reconstruction changed literal coordinates")
    for item in selected:
        if rebuilt_literals[item["coordinate"]].text != item["replacement"]:
            raise RecoveryError(f"offline replacement mismatch at {item['coordinate']}")

    after = {str(path): sha256(path.read_bytes()) for path in input_paths}
    if before != after:
        raise RecoveryError("read-only input changed during build")
    validation = {
        "schema": "nobu16.kr.switch-msggame-v13-invariant-recovery-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "selection": actual,
        "selection_classes": class_manifest,
        "coordinate_sets": {
            "selected_sha256": evidence["selected_coordinates_sha256"],
            "excluded_sha256": evidence["excluded_coordinates_sha256"],
            "selected_excluded_disjoint": True,
            "selected_existing_disjoint": True,
            "selected_target_subset": True,
        },
        "proofs": {
            "exact_pk_jp_to_base_jp_utf16le_hash_alignment": True,
            "unique_switch_ko_value_set_required": True,
            "all_replacements_preserve_pk_sc_invariants": True,
            "all_replacements_preserve_delimiter_role_sequence": True,
            "bullet_normalization_only_u30fb_to_u00b7": True,
            "pc_pua_map_pinned": True,
            "unresolved_internal_line_redistribution_not_transferred": True,
            "v13_msggame_byte_identical_to_v11": True,
            "self_registration_states_supported": [0, 1],
            "self_registration_does_not_feed_selection": True,
            "later_overlay_registration_does_not_feed_selection": True,
            "later_overlays_source_free_target_only_and_disjoint": True,
        },
        "offline_binary_validation": {
            "entry_count": binary_manifest["entry_count"],
            "target_packed_size": len(rebuilt),
            "target_packed_sha256": sha256(rebuilt),
            "literal_coordinates_preserved": True,
            "installed_game_file_written": False,
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
        "safety": {
            "installed_game_files_modified": False,
            "executable_modified": False,
            "dll_injection": False,
            "process_memory_access": False,
            "registry_modified": False,
            "root_progress_modified": False,
            "root_readme_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    validation_artifact = write_json(validation_path, validation)
    return {
        "entry_count": len(selected),
        "excluded_count": len(exclusions),
        "selection": actual,
        "target_packed_sha256": sha256(rebuilt),
        "artifacts": {**artifacts, "validation": validation_artifact},
        "self_registration_count": existing["self_registration_count"],
    }


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--switch-v13-zip", type=Path, default=DEFAULT_V13_ZIP)
    value.add_argument("--switch-v11-zip", type=Path, default=DEFAULT_V11_ZIP)
    value.add_argument("--base-jp", type=Path, default=GAME_ROOT / "MSG" / "JP" / "msggame.bin")
    value.add_argument("--pk-jp", type=Path, default=GAME_ROOT / "MSG_PK" / "JP" / "msggame.bin")
    value.add_argument("--pk-sc", type=Path, default=DEFAULT_PK_SC)
    value.add_argument("--progress", type=Path, default=DEFAULT_PROGRESS)
    value.add_argument("--target-catalog", type=Path, default=DEFAULT_TARGET_CATALOG)
    value.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return value


def main() -> int:
    result = build(parser().parse_args())
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
