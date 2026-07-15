#!/usr/bin/env python3
"""Build proved native-JP and SC-container-mirror PK msggame candidates."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
MSGGAME_ROOT = REPO_ROOT / "workstreams" / "msggame"
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path[:0] = [str(MSGGAME_ROOT), str(TOOLS_ROOT)]

import build_common_message_overlay as common  # noqa: E402
import msggame_format as msggame  # noqa: E402
from nobu16_lz4 import decompress_wrapper  # noqa: E402


SOURCE_RESOURCE = "MSG_PK/SC/msggame.bin"
TARGET_RESOURCE = "MSG_PK/JP/msggame.bin"
RECIPE_SCHEMA = "nobu16.kr.msggame-jp-native-transfer-recipe.v1"
RECIPE_ID = "msggame_pk_jp_native_transfer_v1_8310.v1"
RECIPE_NAME = "msggame_ko_pk_jp_native_transfer_v1_8310.v1.json"
MIRROR_RECIPE_SCHEMA = "nobu16.kr.msggame-jp-sc-container-mirror-recipe.v1"
MIRROR_RECIPE_ID = "msggame_pk_jp_sc_container_mirror_v1_11722.v1"
MIRROR_RECIPE_NAME = "msggame_ko_pk_jp_sc_container_mirror_v1_11722.v1.json"
EVIDENCE_NAME = "msggame_pk_jp_transfer_v1_evidence.v1.json"
REVIEW_NAME = "msggame_pk_jp_transfer_v1_blocked_review.v1.json"
VALIDATION_NAME = "msggame_pk_jp_transfer_v1_validation.v1.json"
README_PATH = WORKSTREAM_ROOT / "README_KO.md"
RUNTIME_VALIDATION_STATE = "not_run_game_runtime_unverified"
NATIVE_STAGE_RELATIVE = Path("native") / "MSG_PK" / "JP" / "msggame.bin"
MIRROR_STAGE_RELATIVE = Path("mirror") / "MSG_PK" / "JP" / "msggame.bin"

B06_RELATIVE = (
    "workstreams/msggame_pk_ui_priority_b06/public/"
    "msggame_ko_pk_ui_priority_b06_300.v1.json"
)
B07_RELATIVE = (
    "workstreams/msggame_pk_ui_priority_b07/public/"
    "msggame_ko_pk_ui_priority_b07_300.v1.json"
)
PREFIX_PATTERN_COUNT = 33
PREFIX_PATTERNS_SHA256 = "91EAF864168DAD3E05417F0FFB8E723ABEDD0761739AB40EEE1525C16893DDB2"
INPUT_OVERLAY_COUNT = 34
INPUT_ENTRY_COUNT = 11_722
INPUT_MANIFEST_SHA256 = "60023DC59C47AC10305B38388E5D32D55014A863A990227353A2DD11CF7EB9D4"
INPUT_COORDINATES_SHA256 = "82882CCE6B645BFDEE802AF5E4EDD47CD074C453E346AC64EAF4B8F6601A66FB"
DIRECT_COUNT = 7_449
DIRECT_COORDINATES_SHA256 = "E6B21D5756293B196CD357FCB82C9F75B38C43991B0768BF525D90FCEAE29240"
REMAPPED_COUNT = 861
REMAPPED_COORDINATES_SHA256 = "66E6E02661861013BB41A46A73724CB50D78B2016C765453AA464792E1AD0EE3"
TRANSFERABLE_COUNT = 8_310
BLOCKED_COUNT = 3_412
TRANSFERABLE_COORDINATES_SHA256 = "AD26C5443C149AD596543AB70AC4F3C535AD817476C46E8FE5F08ABA6005CAF7"
BLOCKED_COORDINATES_SHA256 = "DA224ACB393C3075ABF41A6AFC7F882665135C596D9285A46F5DBBF00FC7572F"
MIRROR_COUNT = INPUT_ENTRY_COUNT
MIRROR_CHANGED_COUNT = 11_717
EXPECTED_NATIVE_PACKED_SIZE = 1_651_697
EXPECTED_NATIVE_PACKED_SHA256 = "0E10975D7A08C1BD445D7FCFFF5C2FAEC5D16C3F1BC3CDBD440677873B6EE146"
EXPECTED_NATIVE_RAW_SIZE = 1_645_220
EXPECTED_NATIVE_RAW_SHA256 = "67560598716AD90BCA0ED1BC05E262143D526720905F08475989D44EA48443EE"
EXPECTED_MIRROR_PACKED_SIZE = 1_269_018
EXPECTED_MIRROR_PACKED_SHA256 = "D5365A49945582D1F82BF5137CA898EC9EBE270B5F8B90513497E6ADC68E9AD9"
EXPECTED_MIRROR_RAW_SIZE = 1_264_036
EXPECTED_MIRROR_RAW_SHA256 = "D1EB3749C835BDEB6C5AA252452F15C83E5E0E57AB6E7636EBBB54401691A04A"

DEFAULT_SC = (
    GAME_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "pk-full-messages-seoulhangang-v1"
    / "originals"
    / "MSG_PK"
    / "SC"
    / "msggame.bin"
)
DEFAULT_JP = GAME_ROOT / "MSG_PK" / "JP" / "msggame.bin"
DEFAULT_TC = GAME_ROOT / "MSG_PK" / "TC" / "msggame.bin"
DEFAULT_EN = GAME_ROOT / "MSG_PK" / "EN" / "msggame.bin"
DEFAULT_PROGRESS = REPO_ROOT / "data" / "public" / "translation_progress.v0.1.json"

SOURCE_PINS = {
    "SC": {
        "packed_size": 529_419,
        "packed_sha256": "BD7B33FCC7495B855B0828C7FE4E5F7ADB2DE656A9B12E20259750F94EE665D6",
        "raw_size": 1_077_200,
        "raw_sha256": "1958B2B801D37186D478284EA0E29CA96D8DA2BC087D6BEB74A4139EF01C11CE",
        "record_count": 21_581,
        "literal_count": 25_598,
    },
    "JP": {
        "packed_size": 709_290,
        "packed_sha256": "0FB9EA3B4817D208C65F587AF1F57A5BB82106367314801A13C9A534ECC47CD8",
        "raw_size": 1_571_384,
        "raw_sha256": "F00C897353C3C0084BFBFC5ED781C467945C82708F28A6D57BA0CC2710976D57",
        "record_count": 21_581,
        "literal_count": 29_149,
    },
    "TC": {
        "packed_size": 535_098,
        "packed_sha256": "73278A4CF06F007E729C37FC6E6409FD77A5A246DB0408CF2879082E88FB0B5D",
        "raw_size": 1_120_204,
        "raw_sha256": "989D3FD487344C4DAED73C1D13704488F77A0E6B036E491FBB588C1FFFF58AF4",
        "record_count": 21_581,
        "literal_count": 26_064,
    },
    "EN": {
        "packed_size": 714_037,
        "packed_sha256": "14D9A20ECB35F35C91D14947921CF09F5EAF960F8FA4D70F703F2366DB1D13AF",
        "raw_size": 2_169_852,
        "raw_sha256": "03A1D07A4FFB460F393A47A047EFF596BBCE6BAADAE22EB00B3686E8AF96D39E",
        "record_count": 21_581,
        "literal_count": 25_169,
    },
}

U32_MAX = 0xFFFFFFFF
MAX_LITERAL_UTF16_BYTES = U32_MAX - 0xFF
STRUCTURE_PLACEHOLDER = b"\x07\x07\x01<TRANSFER-LITERAL>\x07\x07\x02"
CJK_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")
KANA_RE = re.compile(r"[\u3040-\u30FF\u31F0-\u31FF]")
HANGUL_RE = re.compile(r"[\uAC00-\uD7A3]")
RECIPE_ROOT_KEYS = {
    "schema",
    "recipe_id",
    "resource",
    "base_language",
    "entry_count",
    "distribution_policy",
    "stock_jp",
    "input_overlay_catalog",
    "adapter_policy",
    "entries",
}
RECIPE_ENTRY_KEYS = {
    "block_id",
    "record_id",
    "literal_id",
    "source_sc_coordinate",
    "mapping_method",
    "source_jp_utf16le_sha256",
    "jp_record_structure_sha256",
    "jp_record_literal_count",
    "ko",
}
MIRROR_RECIPE_ROOT_KEYS = {
    "schema",
    "recipe_id",
    "resource",
    "base_container_language",
    "entry_count",
    "distribution_policy",
    "stock_sc",
    "stock_jp_target_guard",
    "input_overlay_catalog",
    "container_policy",
    "expected_candidate",
}
NATIVE_ADAPTER_POLICY = {
    "coordinate_must_exist_in_jp": True,
    "direct_requires_sc_jp_record_structure_match": True,
    "remap_requires_same_record_equal_literal_cardinality_and_ordinal": True,
    "remap_preserves_jp_native_record_structure": True,
    "remap_uses_sc_jp_tc_en_hashed_context_anchors": True,
    "jp_control_layout_invariants_must_match_ko": True,
    "utf16_and_u32_capacity_must_pass": True,
    "blocked_entries_are_never_applied": True,
}
MIRROR_CONTAINER_POLICY = {
    "official_pk_msggame_container_format_shared_by_sc_and_jp": True,
    "build_complete_sc_container_then_place_at_jp_resource_path": True,
    "preserve_sc_record_directory_and_literal_coordinates": True,
    "overlay_source_hashes_and_control_layout_must_match_sc": True,
    "jp_installed_resource_is_only_a_pinned_target_guard": True,
}


class TransferError(ValueError):
    """Raised whenever the JP transfer cannot be proved safe."""


def strict_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise TransferError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text(encoding="utf-8-sig"), object_pairs_hook=strict_object
    )
    if not isinstance(value, dict):
        raise TransferError(f"JSON root must be an object: {path}")
    return value


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def write_json(path: Path, value: Any) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {
        "path": path.relative_to(path.parents[1]).as_posix()
        if path.parent.name in {"public", "evidence", "review"}
        else path.name,
        "size": len(blob),
        "sha256": sha256(blob),
    }


def require_exact_bool_policy(
    actual: Any, expected: Mapping[str, bool], label: str
) -> None:
    if not isinstance(actual, dict) or set(actual) != set(expected):
        actual_keys = set(actual) if isinstance(actual, dict) else set()
        raise TransferError(
            f"{label} keys changed: {sorted(actual_keys ^ set(expected))}"
        )
    for key, expected_value in expected.items():
        value = actual[key]
        if type(value) is not bool or value is not expected_value:
            raise TransferError(f"{label}.{key} must be exactly {expected_value!r}")


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def validate_private_staging_root(staging_root: Path) -> tuple[Path, Path, Path]:
    """Validate an isolated root and return its two fixed candidate paths."""
    raw = Path(staging_root)
    if not raw.is_absolute():
        raise TransferError("private staging root must be an explicit absolute directory")
    if raw.suffix.lower() in {".bin", ".exe", ".dll"}:
        raise TransferError("private staging root cannot be a binary or executable path")
    game_root = GAME_ROOT.resolve()
    repo_root = REPO_ROOT.resolve()
    lexical_root = Path(os.path.abspath(raw))
    if _is_within(lexical_root, game_root) or _is_within(lexical_root, repo_root):
        raise TransferError("private staging root must stay outside GAME_ROOT and the repository")
    if raw.exists() and raw.is_symlink():
        raise TransferError("private staging root cannot be a symlink")
    root = raw.resolve()
    if root.parent == root:
        raise TransferError("filesystem root cannot be used as a private staging root")
    if _is_within(root, game_root) or _is_within(root, repo_root):
        raise TransferError("private staging root must stay outside GAME_ROOT and the repository")
    if root.exists() and not root.is_dir():
        raise TransferError("private staging root must be a directory, not a file")
    root.mkdir(parents=True, exist_ok=True)
    root = root.resolve()
    if _is_within(root, game_root) or _is_within(root, repo_root):
        raise TransferError("resolved private staging root entered a protected tree")

    native = (root / NATIVE_STAGE_RELATIVE).resolve()
    mirror = (root / MIRROR_STAGE_RELATIVE).resolve()
    try:
        native_relative = native.relative_to(root)
        mirror_relative = mirror.relative_to(root)
    except ValueError as exc:
        raise TransferError("private candidate destination escaped the staging root") from exc
    if native_relative != NATIVE_STAGE_RELATIVE:
        raise TransferError("native staging destination escaped or changed its exact layout")
    if mirror_relative != MIRROR_STAGE_RELATIVE:
        raise TransferError("mirror staging destination escaped or changed its exact layout")

    allowed_directories = {
        Path("native"),
        Path("native") / "MSG_PK",
        Path("native") / "MSG_PK" / "JP",
        Path("mirror"),
        Path("mirror") / "MSG_PK",
        Path("mirror") / "MSG_PK" / "JP",
    }
    allowed_files = {NATIVE_STAGE_RELATIVE, MIRROR_STAGE_RELATIVE}
    for item in root.rglob("*"):
        if item.is_symlink():
            raise TransferError("symlinks are forbidden in the private staging tree")
        relative = item.relative_to(root)
        if item.is_dir():
            if relative not in allowed_directories:
                raise TransferError(f"unexpected directory in private staging root: {relative}")
        elif relative not in allowed_files:
            raise TransferError(f"unexpected file in private staging root: {relative}")
    for destination in (native, mirror):
        if destination.exists() and not destination.is_file():
            raise TransferError("exact private candidate destination is not a regular file")
    return root, native, mirror


def write_private_candidates(
    staging_root: Path | None, native_blob: bytes, mirror_blob: bytes
) -> dict[str, Any]:
    if staging_root is None:
        return {
            "written": False,
            "exact_layout": False,
            "native_written": False,
            "mirror_written": False,
        }
    root, native_path, mirror_path = validate_private_staging_root(staging_root)
    for destination, blob in ((native_path, native_blob), (mirror_path, mirror_blob)):
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(blob)
        if destination.read_bytes() != blob:
            raise TransferError("private staged candidate write verification failed")
    checked_root, checked_native, checked_mirror = validate_private_staging_root(root)
    if (checked_root, checked_native, checked_mirror) != (root, native_path, mirror_path):
        raise TransferError("private staging layout changed after candidate writes")
    return {
        "written": True,
        "exact_layout": True,
        "native_written": True,
        "mirror_written": True,
    }


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256(text.encode("utf-16-le"))


def canonical_hash(value: Any) -> str:
    return sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    )


def script_counts(text: str) -> dict[str, int]:
    return {
        "cjk_unified_count": len(CJK_RE.findall(text)),
        "kana_count": len(KANA_RE.findall(text)),
    }


def assert_source_free(paths: Iterable[Path]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for path in paths:
        counts = script_counts(path.read_text(encoding="utf-8"))
        result[path.name] = counts
        if counts != {"cjk_unified_count": 0, "kana_count": 0}:
            raise TransferError(f"commercial source script leaked into artifact: {path}")
    return result


def literal_map(archive: Any) -> dict[tuple[int, int, int], Any]:
    return {
        (literal.block_id, literal.record_id, literal.literal_id): literal
        for literal in msggame.iter_literals(archive)
    }


def record_map(archive: Any) -> dict[tuple[int, int], Any]:
    return {
        (record.block_id, record.record_id): record
        for block in archive.blocks
        for record in block.records
    }


def load_source(path: Path, label: str) -> dict[str, Any]:
    packed = path.read_bytes()
    pin = SOURCE_PINS[label]
    if len(packed) != pin["packed_size"] or sha256(packed) != pin["packed_sha256"]:
        raise TransferError(f"{label} packed source pin changed")
    _header, raw = decompress_wrapper(packed)
    if len(raw) != pin["raw_size"] or sha256(raw) != pin["raw_sha256"]:
        raise TransferError(f"{label} raw source pin changed")
    parsed = msggame.parse_packed_msggame(packed)
    literals = literal_map(parsed.archive)
    if parsed.archive.record_count != pin["record_count"]:
        raise TransferError(f"{label} record count changed")
    if len(literals) != pin["literal_count"]:
        raise TransferError(f"{label} literal count changed")
    return {
        "path": path,
        "packed": packed,
        "raw": raw,
        "archive": parsed.archive,
        "literals": literals,
        "records": record_map(parsed.archive),
    }


def record_structure_blob(record: Any) -> bytes:
    output = bytearray()
    cursor = 0
    for literal in msggame.parse_record_literals(record):
        output.extend(record.data[cursor : literal.marker_offset])
        output.extend(STRUCTURE_PLACEHOLDER)
        cursor = literal.marker_end
    output.extend(record.data[cursor:])
    return bytes(output)


def record_structure_hash(record: Any) -> str:
    return sha256(record_structure_blob(record))


def record_literal_hashes(record: Any) -> list[str]:
    return [text_hash(literal.text) for literal in msggame.parse_record_literals(record)]


def record_context_hashes(
    source: dict[str, Any], coordinate: tuple[int, int, int]
) -> dict[str, Any]:
    """Return source-free same-record and adjacent-record anchors."""
    block_id, record_id, literal_id = coordinate
    current = source["records"][(block_id, record_id)]
    anchors: dict[str, Any] = {
        "record_literal_count": len(msggame.parse_record_literals(current)),
        "record_literal_hashes_sha256": canonical_hash(record_literal_hashes(current)),
        "ordinal_literal_hash": (
            text_hash(source["literals"][(block_id, record_id, literal_id)].text)
            if (block_id, record_id, literal_id) in source["literals"]
            else None
        ),
    }
    block = source["archive"].blocks[block_id]
    for label, neighbor_id in (("previous_record", record_id - 1), ("next_record", record_id + 1)):
        if not 0 <= neighbor_id < len(block.records):
            anchors[label] = None
            continue
        neighbor = source["records"][(block_id, neighbor_id)]
        anchors[label] = {
            "record_id": neighbor_id,
            "record_structure_sha256": record_structure_hash(neighbor),
            "literal_hashes_sha256": canonical_hash(record_literal_hashes(neighbor)),
        }
    return anchors


def multilingual_remap_evidence(
    coordinate: tuple[int, int, int],
    sources: Mapping[str, dict[str, Any]],
) -> dict[str, Any]:
    sc_record = sources["SC"]["records"][coordinate[:2]]
    jp_record = sources["JP"]["records"][coordinate[:2]]
    sc_count = len(msggame.parse_record_literals(sc_record))
    jp_count = len(msggame.parse_record_literals(jp_record))
    if sc_count != jp_count or not 0 <= coordinate[2] < jp_count:
        raise TransferError(f"remap is not a unique equal-cardinality ordinal: {coordinate}")
    return {
        "method": "same_record_equal_cardinality_ordinal_marker_offset_remap",
        "confidence": "exact_unique",
        "source_sc_coordinate": list(coordinate),
        "target_jp_coordinate": list(coordinate),
        "candidate_target_count": 1,
        "record_directory_coordinate_equal": True,
        "sc_jp_literal_cardinality_equal": True,
        "ordinal_preserved": True,
        "record_structure_intentionally_language_native": True,
        "context": {
            language: record_context_hashes(source, coordinate)
            for language, source in sorted(sources.items())
        },
    }


def validate_multilingual_record_directories(
    sources: Mapping[str, dict[str, Any]],
) -> dict[str, Any]:
    shapes = {
        language: [len(block.records) for block in source["archive"].blocks]
        for language, source in sources.items()
    }
    if len({tuple(shape) for shape in shapes.values()}) != 1:
        raise TransferError("PK SC/JP/TC/EN record directory shapes are not aligned")
    coordinate_sets = {
        language: set(source["records"])
        for language, source in sources.items()
    }
    if len({frozenset(values) for values in coordinate_sets.values()}) != 1:
        raise TransferError("PK SC/JP/TC/EN record coordinates are not aligned")
    coordinates = next(iter(coordinate_sets.values()))
    block_record_counts = next(iter(shapes.values()))
    return {
        "languages": sorted(sources),
        "block_count_each": len(block_record_counts),
        "record_count_each": len(coordinates),
        "block_record_counts": block_record_counts,
        "record_coordinates_sha256": canonical_hash(
            [list(value) for value in sorted(coordinates)]
        ),
        "record_directory_coordinates_equal": True,
    }


def _require_int(entry: Mapping[str, Any], key: str) -> int:
    value = entry.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise TransferError(f"entry {key} must be a non-negative integer")
    return value


def validate_utf16_capacity(
    replacement: str,
    *,
    coordinate: tuple[int, int, int] | None = None,
    limit: int = MAX_LITERAL_UTF16_BYTES,
) -> bytes:
    label = coordinate if coordinate is not None else "test-value"
    if not isinstance(replacement, str):
        raise TransferError(f"replacement must be a string at {label}")
    try:
        encoded = replacement.encode("utf-16-le")
    except UnicodeEncodeError as exc:
        raise TransferError(f"replacement is not valid UTF-16 at {label}") from exc
    if len(encoded) > limit:
        raise TransferError(
            f"replacement exceeds UTF-16 literal capacity at {label}: {len(encoded)} > {limit}"
        )
    if msggame.LITERAL_START in encoded or msggame.LITERAL_END in encoded:
        raise TransferError(f"replacement collides with a literal marker at {label}")
    return encoded


def capacity_manifest(
    archive: Any, replacements: Mapping[tuple[int, int, int], str]
) -> dict[str, int]:
    rebuilt_records = msggame.literal_record_replacements(archive, replacements)
    max_record_size = 0
    max_block_size = 0
    raw_offset = (4 + len(archive.blocks) * 8 + 3) & ~3
    for block in archive.blocks:
        block_size = 4 + len(block.records) * 4
        for record in block.records:
            record_blob = rebuilt_records.get((record.block_id, record.record_id), record.data)
            record_size = len(record_blob)
            if record_size > U32_MAX:
                raise TransferError(
                    f"rebuilt record exceeds u32 capacity: {(record.block_id, record.record_id)}"
                )
            max_record_size = max(max_record_size, record_size)
            block_size += record_size
        if block_size > U32_MAX:
            raise TransferError(f"rebuilt block exceeds u32 capacity: {block.block_id}")
        max_block_size = max(max_block_size, block_size)
        if raw_offset > U32_MAX or raw_offset + block_size > U32_MAX:
            raise TransferError(f"rebuilt raw offset exceeds u32 capacity: {block.block_id}")
        raw_offset = (raw_offset + block_size + 3) & ~3
    if raw_offset > U32_MAX:
        raise TransferError("rebuilt raw msggame exceeds u32 capacity")
    return {
        "replacement_count": len(replacements),
        "max_rebuilt_record_size": max_record_size,
        "max_rebuilt_block_size": max_block_size,
        "predicted_raw_size": raw_offset,
    }


def _progress_prefix(progress_path: Path) -> list[str]:
    progress = read_json(progress_path)
    resources = progress.get("resources")
    matches = [item for item in resources if item.get("path") == SOURCE_RESOURCE] if isinstance(resources, list) else []
    if len(matches) != 1:
        raise TransferError("progress must contain exactly one PK/SC msggame resource")
    patterns = matches[0].get("overlay_globs")
    if not isinstance(patterns, list) or not all(isinstance(value, str) for value in patterns):
        raise TransferError("PK/SC msggame overlay list is invalid")
    if patterns.count(B06_RELATIVE) != 1:
        raise TransferError("B06 boundary must be registered exactly once")
    prefix = patterns[: patterns.index(B06_RELATIVE) + 1]
    if len(prefix) != PREFIX_PATTERN_COUNT:
        raise TransferError("B06 prefix pattern count changed")
    if canonical_hash(prefix) != PREFIX_PATTERNS_SHA256:
        raise TransferError("B06 prefix pattern order changed")
    return prefix


def collect_overlay_inputs(progress_path: Path) -> dict[str, Any]:
    relative_paths = _progress_prefix(progress_path) + [B07_RELATIVE]
    if len(relative_paths) != INPUT_OVERLAY_COUNT or len(set(relative_paths)) != len(relative_paths):
        raise TransferError("cumulative overlay path set changed")
    inputs: list[dict[str, Any]] = []
    entries: list[dict[str, Any]] = []
    coordinates: set[tuple[int, int, int]] = set()
    for relative in relative_paths:
        matches = sorted(REPO_ROOT.glob(relative))
        if len(matches) != 1:
            raise TransferError(f"overlay path {relative!r} resolved to {len(matches)} files")
        path = matches[0]
        if path.relative_to(REPO_ROOT).as_posix() != relative:
            raise TransferError(f"overlay must use its exact logical path: {relative}")
        blob = path.read_bytes()
        payload = read_json(path)
        if payload.get("resource") != SOURCE_RESOURCE:
            raise TransferError(f"overlay resource changed: {relative}")
        policy = payload.get("distribution_policy")
        if (
            not isinstance(policy, dict)
            or policy.get("contains_commercial_source_text") is not False
            or policy.get("contains_complete_game_resource") is not False
            or script_counts(path.read_text(encoding="utf-8"))
            != {"cjk_unified_count": 0, "kana_count": 0}
        ):
            raise TransferError(f"input overlay is not source-free: {relative}")
        values = payload.get("entries")
        if not isinstance(values, list):
            raise TransferError(f"overlay entries are invalid: {relative}")
        if payload.get("entry_count") not in (None, len(values)):
            raise TransferError(f"overlay entry_count changed: {relative}")
        overlay_hash = sha256(blob)
        for entry in values:
            if not isinstance(entry, dict):
                raise TransferError(f"overlay entry is invalid: {relative}")
            coordinate = (
                _require_int(entry, "block_id"),
                _require_int(entry, "record_id"),
                _require_int(entry, "literal_id"),
            )
            if coordinate in coordinates:
                raise TransferError(f"cumulative overlays overlap at {coordinate}")
            source_hash = entry.get("source_sc_utf16le_sha256")
            replacement = entry.get("ko")
            if not isinstance(source_hash, str) or re.fullmatch(r"[0-9A-F]{64}", source_hash) is None:
                raise TransferError(f"invalid SC source hash at {coordinate}: {relative}")
            if not isinstance(replacement, str):
                raise TransferError(f"invalid Korean replacement at {coordinate}: {relative}")
            if script_counts(replacement) != {"cjk_unified_count": 0, "kana_count": 0}:
                raise TransferError(f"source script in Korean replacement at {coordinate}: {relative}")
            coordinates.add(coordinate)
            entries.append(
                {
                    "coordinate": coordinate,
                    "source_sc_hash": source_hash,
                    "ko": replacement,
                    "origin_path": relative,
                    "origin_sha256": overlay_hash,
                }
            )
        inputs.append({"path": relative, "size": len(blob), "sha256": overlay_hash})
    if len(entries) != INPUT_ENTRY_COUNT or len(coordinates) != INPUT_ENTRY_COUNT:
        raise TransferError("cumulative overlay entry count changed")
    if canonical_hash(inputs) != INPUT_MANIFEST_SHA256:
        raise TransferError("cumulative overlay input manifest changed")
    if canonical_hash([list(value) for value in sorted(coordinates)]) != INPUT_COORDINATES_SHA256:
        raise TransferError("cumulative overlay coordinate set changed")
    return {
        "paths": relative_paths,
        "inputs": inputs,
        "entries": entries,
        "coordinates": coordinates,
    }


def classify_entries(
    source_sc: dict[str, Any],
    target_jp: dict[str, Any],
    context_tc: dict[str, Any],
    context_en: dict[str, Any],
    catalog: dict[str, Any],
) -> dict[str, Any]:
    multilingual_sources = {
        "SC": source_sc,
        "JP": target_jp,
        "TC": context_tc,
        "EN": context_en,
    }
    directory_alignment = validate_multilingual_record_directories(multilingual_sources)
    direct: list[dict[str, Any]] = []
    remapped: list[dict[str, Any]] = []
    transferable: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    nonexclusive_reasons: collections.Counter[str] = collections.Counter()
    primary_reasons: collections.Counter[str] = collections.Counter()
    mismatch_keys: collections.Counter[str] = collections.Counter()
    block_transferable: collections.Counter[int] = collections.Counter()
    block_blocked: collections.Counter[int] = collections.Counter()
    origin_counts: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    max_utf16_bytes = 0

    for item in catalog["entries"]:
        coordinate = item["coordinate"]
        sc_literal = source_sc["literals"].get(coordinate)
        if sc_literal is None or text_hash(sc_literal.text) != item["source_sc_hash"]:
            raise TransferError(f"SC source hash mismatch at {coordinate}")
        jp_literal = target_jp["literals"].get(coordinate)
        reasons: list[str] = []
        detail: dict[str, Any] = {
            "block_id": coordinate[0],
            "record_id": coordinate[1],
            "literal_id": coordinate[2],
            "origin_overlay_path": item["origin_path"],
            "origin_overlay_sha256": item["origin_sha256"],
            "source_sc_utf16le_sha256": item["source_sc_hash"],
            "ko_utf16le_sha256": text_hash(item["ko"]),
        }
        if jp_literal is None:
            reasons.append("jp_coordinate_missing")
            detail.update(
                {
                    "source_jp_utf16le_sha256": None,
                    "sc_record_literal_count": None,
                    "jp_record_literal_count": None,
                    "sc_record_structure_sha256": None,
                    "jp_record_structure_sha256": None,
                    "jp_invariant_mismatch_keys": [],
                    "ko_utf16le_size": len(item["ko"].encode("utf-16-le")),
                }
            )
        else:
            record_key = coordinate[:2]
            sc_record = source_sc["records"][record_key]
            jp_record = target_jp["records"][record_key]
            sc_literal_count = len(msggame.parse_record_literals(sc_record))
            jp_literal_count = len(msggame.parse_record_literals(jp_record))
            sc_structure = record_structure_hash(sc_record)
            jp_structure = record_structure_hash(jp_record)
            if sc_literal_count != jp_literal_count:
                reasons.append("record_literal_count_mismatch")
            if sc_structure != jp_structure:
                reasons.append("record_skeleton_mismatch")
            invariant_mismatches = common.invariant_mismatches(jp_literal.text, item["ko"])
            keys = sorted({value.split(":", 1)[0] for value in invariant_mismatches})
            if keys:
                reasons.append("jp_invariant_mismatch")
                mismatch_keys.update(keys)
            try:
                encoded = validate_utf16_capacity(item["ko"], coordinate=coordinate)
            except TransferError as exc:
                encoded = b""
                message = str(exc)
                if "capacity" in message:
                    reasons.append("utf16_literal_capacity_exceeded")
                elif "marker" in message:
                    reasons.append("reserved_marker_collision")
                else:
                    reasons.append("utf16_encode_failure")
            max_utf16_bytes = max(max_utf16_bytes, len(encoded))
            detail.update(
                {
                    "source_jp_utf16le_sha256": text_hash(jp_literal.text),
                    "sc_record_literal_count": sc_literal_count,
                    "jp_record_literal_count": jp_literal_count,
                    "sc_record_structure_sha256": sc_structure,
                    "jp_record_structure_sha256": jp_structure,
                    "jp_invariant_mismatch_keys": keys,
                    "ko_utf16le_size": len(encoded),
                }
            )

        reasons = list(dict.fromkeys(reasons))
        if reasons == ["record_skeleton_mismatch"]:
            remap = multilingual_remap_evidence(
                coordinate,
                multilingual_sources,
            )
            recipe_entry = {
                "block_id": coordinate[0],
                "record_id": coordinate[1],
                "literal_id": coordinate[2],
                "source_sc_coordinate": list(coordinate),
                "mapping_method": remap["method"],
                "source_jp_utf16le_sha256": detail["source_jp_utf16le_sha256"],
                "jp_record_structure_sha256": detail["jp_record_structure_sha256"],
                "jp_record_literal_count": detail["jp_record_literal_count"],
                "ko": item["ko"],
            }
            detail.update(
                {
                    "status": "remapped",
                    "mapping": remap,
                    "jp_invariants_exact": True,
                    "utf16_capacity_ok": True,
                }
            )
            wrapped = {"recipe_entry": recipe_entry, "evidence": detail}
            remapped.append(wrapped)
            transferable.append(wrapped)
            block_transferable[coordinate[0]] += 1
            origin_counts[item["origin_path"]]["remapped"] += 1
            continue

        if reasons:
            detail.update(
                {
                    "status": "blocked",
                    "primary_reason": reasons[0],
                    "reasons": reasons,
                    "human_adapter_required": True,
                }
            )
            blocked.append(detail)
            nonexclusive_reasons.update(reasons)
            primary_reasons[reasons[0]] += 1
            block_blocked[coordinate[0]] += 1
            origin_counts[item["origin_path"]]["blocked"] += 1
            continue

        recipe_entry = {
            "block_id": coordinate[0],
            "record_id": coordinate[1],
            "literal_id": coordinate[2],
            "source_sc_coordinate": list(coordinate),
            "mapping_method": "direct_coordinate_equal_record_structure",
            "source_jp_utf16le_sha256": detail["source_jp_utf16le_sha256"],
            "jp_record_structure_sha256": detail["jp_record_structure_sha256"],
            "jp_record_literal_count": detail["jp_record_literal_count"],
            "ko": item["ko"],
        }
        detail.update(
            {
                "status": "transferable",
                "record_structure_equal": True,
                "jp_invariants_exact": True,
                "utf16_capacity_ok": True,
            }
        )
        wrapped = {"recipe_entry": recipe_entry, "evidence": detail}
        direct.append(wrapped)
        transferable.append(wrapped)
        block_transferable[coordinate[0]] += 1
        origin_counts[item["origin_path"]]["transferable"] += 1

    transferable_coordinates = {
        (
            item["recipe_entry"]["block_id"],
            item["recipe_entry"]["record_id"],
            item["recipe_entry"]["literal_id"],
        )
        for item in transferable
    }
    blocked_coordinates = {
        (item["block_id"], item["record_id"], item["literal_id"])
        for item in blocked
    }
    direct_coordinates = {
        tuple(item["recipe_entry"]["source_sc_coordinate"]) for item in direct
    }
    remapped_coordinates = {
        tuple(item["recipe_entry"]["source_sc_coordinate"]) for item in remapped
    }
    if len(direct) != DIRECT_COUNT or len(remapped) != REMAPPED_COUNT:
        raise TransferError(
            f"native transfer stages changed: direct={len(direct)}, remapped={len(remapped)}"
        )
    if len(transferable) != TRANSFERABLE_COUNT or len(blocked) != BLOCKED_COUNT:
        raise TransferError(
            f"compatibility counts changed: transferable={len(transferable)}, blocked={len(blocked)}"
        )
    if transferable_coordinates & blocked_coordinates:
        raise TransferError("transferable and blocked coordinates overlap")
    if transferable_coordinates | blocked_coordinates != catalog["coordinates"]:
        raise TransferError("compatibility classification does not cover the cumulative catalog")
    if direct_coordinates & remapped_coordinates:
        raise TransferError("direct and remapped source coordinates overlap")
    if canonical_hash([list(value) for value in sorted(direct_coordinates)]) != DIRECT_COORDINATES_SHA256:
        raise TransferError("direct coordinate set changed")
    if canonical_hash([list(value) for value in sorted(remapped_coordinates)]) != REMAPPED_COORDINATES_SHA256:
        raise TransferError("remapped coordinate set changed")
    if (
        canonical_hash([list(value) for value in sorted(transferable_coordinates)])
        != TRANSFERABLE_COORDINATES_SHA256
    ):
        raise TransferError("transferable coordinate set changed")
    if (
        canonical_hash([list(value) for value in sorted(blocked_coordinates)])
        != BLOCKED_COORDINATES_SHA256
    ):
        raise TransferError("blocked coordinate set changed")
    return {
        "direct": direct,
        "remapped": remapped,
        "transferable": transferable,
        "blocked": blocked,
        "transferable_coordinates": transferable_coordinates,
        "blocked_coordinates": blocked_coordinates,
        "nonexclusive_reasons": dict(sorted(nonexclusive_reasons.items())),
        "primary_reasons": dict(sorted(primary_reasons.items())),
        "invariant_mismatch_keys": dict(sorted(mismatch_keys.items())),
        "block_transferable": dict(sorted(block_transferable.items())),
        "block_blocked": dict(sorted(block_blocked.items())),
        "origin_counts": {
            path: dict(sorted(counts.items())) for path, counts in sorted(origin_counts.items())
        },
        "max_utf16_bytes": max_utf16_bytes,
        "multilingual_record_directory_alignment": directory_alignment,
    }


def _validate_recipe_root(recipe: dict[str, Any]) -> list[dict[str, Any]]:
    if set(recipe) != RECIPE_ROOT_KEYS:
        raise TransferError(f"recipe root keys changed: {sorted(set(recipe) ^ RECIPE_ROOT_KEYS)}")
    if recipe.get("schema") != RECIPE_SCHEMA:
        raise TransferError("unsupported JP transfer recipe schema")
    if recipe.get("recipe_id") != RECIPE_ID:
        raise TransferError("JP transfer recipe id changed")
    if recipe.get("resource") != TARGET_RESOURCE or recipe.get("base_language") != "JP":
        raise TransferError("JP transfer recipe target changed")
    policy = recipe.get("distribution_policy")
    if policy != {
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }:
        raise TransferError("JP transfer recipe distribution policy changed")
    require_exact_bool_policy(
        recipe.get("adapter_policy"), NATIVE_ADAPTER_POLICY, "adapter_policy"
    )
    entries = recipe.get("entries")
    if not isinstance(entries, list) or recipe.get("entry_count") != len(entries):
        raise TransferError("JP transfer recipe entries are invalid")
    return entries


def apply_recipe_blob(packed_jp: bytes, recipe: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    entries = _validate_recipe_root(recipe)
    stock = recipe.get("stock_jp")
    if not isinstance(stock, dict):
        raise TransferError("stock_jp must be an object")
    if stock.get("packed_size") != len(packed_jp) or stock.get("packed_sha256") != sha256(packed_jp):
        raise TransferError("packed JP source pin mismatch")
    parsed = msggame.parse_packed_msggame(packed_jp)
    _header, raw = decompress_wrapper(packed_jp)
    literals = literal_map(parsed.archive)
    records = record_map(parsed.archive)
    expected_stock = {
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
        "record_count": parsed.archive.record_count,
        "literal_slot_count": len(literals),
    }
    for key, expected in expected_stock.items():
        if stock.get(key) != expected:
            raise TransferError(f"stock_jp {key} mismatch")

    replacements: dict[tuple[int, int, int], str] = {}
    mapping_counts: collections.Counter[str] = collections.Counter()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or set(entry) != RECIPE_ENTRY_KEYS:
            raise TransferError(f"recipe entry shape changed at index {index}")
        coordinate = (
            _require_int(entry, "block_id"),
            _require_int(entry, "record_id"),
            _require_int(entry, "literal_id"),
        )
        source_coordinate = entry.get("source_sc_coordinate")
        if (
            not isinstance(source_coordinate, list)
            or len(source_coordinate) != 3
            or any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in source_coordinate)
        ):
            raise TransferError(f"invalid SC source coordinate at recipe index {index}")
        if tuple(source_coordinate) != coordinate:
            raise TransferError(f"unsupported cross-ordinal JP remap at recipe index {index}")
        method = entry.get("mapping_method")
        if method not in {
            "direct_coordinate_equal_record_structure",
            "same_record_equal_cardinality_ordinal_marker_offset_remap",
        }:
            raise TransferError(f"unsupported mapping method at recipe index {index}")
        if coordinate in replacements:
            raise TransferError(f"duplicate JP recipe coordinate: {coordinate}")
        source = literals.get(coordinate)
        if source is None:
            raise TransferError(f"JP literal coordinate does not exist: {coordinate}")
        if entry.get("source_jp_utf16le_sha256") != text_hash(source.text):
            raise TransferError(f"JP source text hash mismatch at {coordinate}")
        record = records[coordinate[:2]]
        if entry.get("jp_record_literal_count") != len(msggame.parse_record_literals(record)):
            raise TransferError(f"JP record literal count mismatch at {coordinate}")
        if entry.get("jp_record_structure_sha256") != record_structure_hash(record):
            raise TransferError(f"JP record structure mismatch at {coordinate}")
        replacement = entry.get("ko")
        validate_utf16_capacity(replacement, coordinate=coordinate)
        if common.invariant_mismatches(source.text, replacement):
            raise TransferError(f"JP control/layout invariant mismatch at {coordinate}")
        if script_counts(replacement) != {"cjk_unified_count": 0, "kana_count": 0}:
            raise TransferError(f"source script in JP recipe replacement at {coordinate}")
        replacements[coordinate] = replacement
        mapping_counts[method] += 1

    if len(replacements) != TRANSFERABLE_COUNT:
        raise TransferError(f"JP recipe transfer count changed: {len(replacements)}")
    if mapping_counts != {
        "direct_coordinate_equal_record_structure": DIRECT_COUNT,
        "same_record_equal_cardinality_ordinal_marker_offset_remap": REMAPPED_COUNT,
    }:
        raise TransferError(f"JP recipe mapping partition changed: {dict(mapping_counts)}")
    capacity = capacity_manifest(parsed.archive, replacements)
    rebuilt = msggame.rebuild_packed_with_literals(packed_jp, replacements)
    verified = msggame.parse_packed_msggame(rebuilt)
    verified_literals = literal_map(verified.archive)
    if set(verified_literals) != set(literals):
        raise TransferError("JP candidate changed literal coordinates")
    for coordinate, source in literals.items():
        expected = replacements.get(coordinate, source.text)
        if verified_literals[coordinate].text != expected:
            raise TransferError(f"JP candidate literal verification failed at {coordinate}")
    _new_header, new_raw = decompress_wrapper(rebuilt)
    if (
        len(rebuilt) != EXPECTED_NATIVE_PACKED_SIZE
        or sha256(rebuilt) != EXPECTED_NATIVE_PACKED_SHA256
        or len(new_raw) != EXPECTED_NATIVE_RAW_SIZE
        or sha256(new_raw) != EXPECTED_NATIVE_RAW_SHA256
    ):
        raise TransferError("native JP candidate digest changed")
    manifest = {
        "schema": "nobu16.kr.msggame-jp-transfer-build-manifest.v1",
        "recipe_id": recipe["recipe_id"],
        "resource": TARGET_RESOURCE,
        "entry_count": len(replacements),
        "mapping_counts": dict(sorted(mapping_counts.items())),
        "source": {
            "packed_size": len(packed_jp),
            "packed_sha256": sha256(packed_jp),
            "raw_size": len(raw),
            "raw_sha256": sha256(raw),
        },
        "candidate": {
            "packed_size": len(rebuilt),
            "packed_sha256": sha256(rebuilt),
            "raw_size": len(new_raw),
            "raw_sha256": sha256(new_raw),
        },
        "capacity": capacity,
        "checks": {
            "jp_source_hashes_exact": True,
            "jp_record_structure_exact": True,
            "source_to_target_mapping_partition_exact": True,
            "jp_control_layout_invariants_exact": True,
            "utf16_and_u32_capacity_exact": True,
            "literal_coordinates_preserved": True,
            "non_recipe_literals_preserved": True,
            "rebuilt_literals_match_recipe": True,
        },
        "installed_game_file_written": False,
    }
    return rebuilt, manifest


def _recipe(target_jp: dict[str, Any], catalog: dict[str, Any], classified: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": RECIPE_SCHEMA,
        "recipe_id": RECIPE_ID,
        "resource": TARGET_RESOURCE,
        "base_language": "JP",
        "entry_count": TRANSFERABLE_COUNT,
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_jp": {
            "packed_size": len(target_jp["packed"]),
            "packed_sha256": sha256(target_jp["packed"]),
            "raw_size": len(target_jp["raw"]),
            "raw_sha256": sha256(target_jp["raw"]),
            "record_count": target_jp["archive"].record_count,
            "literal_slot_count": len(target_jp["literals"]),
        },
        "input_overlay_catalog": {
            "source_resource": SOURCE_RESOURCE,
            "overlay_count": INPUT_OVERLAY_COUNT,
            "entry_count": INPUT_ENTRY_COUNT,
            "input_manifest_sha256": INPUT_MANIFEST_SHA256,
            "coordinates_sha256": INPUT_COORDINATES_SHA256,
        },
        "adapter_policy": dict(NATIVE_ADAPTER_POLICY),
        "entries": [item["recipe_entry"] for item in classified["transferable"]],
    }


def _mirror_recipe(
    source_sc: dict[str, Any], target_jp: dict[str, Any], catalog: dict[str, Any]
) -> dict[str, Any]:
    return {
        "schema": MIRROR_RECIPE_SCHEMA,
        "recipe_id": MIRROR_RECIPE_ID,
        "resource": TARGET_RESOURCE,
        "base_container_language": "SC",
        "entry_count": MIRROR_COUNT,
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "packed_size": len(source_sc["packed"]),
            "packed_sha256": sha256(source_sc["packed"]),
            "raw_size": len(source_sc["raw"]),
            "raw_sha256": sha256(source_sc["raw"]),
            "record_count": source_sc["archive"].record_count,
            "literal_slot_count": len(source_sc["literals"]),
        },
        "stock_jp_target_guard": {
            "packed_size": len(target_jp["packed"]),
            "packed_sha256": sha256(target_jp["packed"]),
            "raw_size": len(target_jp["raw"]),
            "raw_sha256": sha256(target_jp["raw"]),
            "record_count": target_jp["archive"].record_count,
        },
        "input_overlay_catalog": {
            "source_resource": SOURCE_RESOURCE,
            "overlay_count": INPUT_OVERLAY_COUNT,
            "entry_count": INPUT_ENTRY_COUNT,
            "input_manifest_sha256": INPUT_MANIFEST_SHA256,
            "coordinates_sha256": INPUT_COORDINATES_SHA256,
            "inputs": catalog["inputs"],
        },
        "container_policy": dict(MIRROR_CONTAINER_POLICY),
        "expected_candidate": {
            "packed_size": EXPECTED_MIRROR_PACKED_SIZE,
            "packed_sha256": EXPECTED_MIRROR_PACKED_SHA256,
            "raw_size": EXPECTED_MIRROR_RAW_SIZE,
            "raw_sha256": EXPECTED_MIRROR_RAW_SHA256,
            "record_count": SOURCE_PINS["SC"]["record_count"],
            "literal_slot_count": SOURCE_PINS["SC"]["literal_count"],
        },
    }


def apply_mirror_recipe_blob(
    packed_sc: bytes,
    packed_jp_guard: bytes,
    catalog: dict[str, Any],
    recipe: dict[str, Any],
) -> tuple[bytes, dict[str, Any]]:
    if set(recipe) != MIRROR_RECIPE_ROOT_KEYS:
        raise TransferError(
            f"mirror recipe root keys changed: {sorted(set(recipe) ^ MIRROR_RECIPE_ROOT_KEYS)}"
        )
    if (
        recipe.get("schema") != MIRROR_RECIPE_SCHEMA
        or recipe.get("recipe_id") != MIRROR_RECIPE_ID
        or recipe.get("resource") != TARGET_RESOURCE
        or recipe.get("base_container_language") != "SC"
        or recipe.get("entry_count") != MIRROR_COUNT
    ):
        raise TransferError("mirror recipe identity changed")
    if recipe.get("distribution_policy") != {
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }:
        raise TransferError("mirror recipe distribution policy changed")
    require_exact_bool_policy(
        recipe.get("container_policy"), MIRROR_CONTAINER_POLICY, "container_policy"
    )
    stock_sc = recipe.get("stock_sc")
    stock_jp = recipe.get("stock_jp_target_guard")
    if not isinstance(stock_sc, dict) or not isinstance(stock_jp, dict):
        raise TransferError("mirror stock guards are invalid")
    if stock_sc.get("packed_size") != len(packed_sc) or stock_sc.get("packed_sha256") != sha256(packed_sc):
        raise TransferError("mirror SC stock pin mismatch")
    if stock_jp.get("packed_size") != len(packed_jp_guard) or stock_jp.get("packed_sha256") != sha256(packed_jp_guard):
        raise TransferError("mirror JP target guard mismatch")
    parsed_sc = msggame.parse_packed_msggame(packed_sc)
    parsed_jp = msggame.parse_packed_msggame(packed_jp_guard)
    _sc_header, raw_sc = decompress_wrapper(packed_sc)
    _jp_header, raw_jp = decompress_wrapper(packed_jp_guard)
    sc_literals = literal_map(parsed_sc.archive)
    for stock, raw, archive, literals in (
        (stock_sc, raw_sc, parsed_sc.archive, sc_literals),
        (stock_jp, raw_jp, parsed_jp.archive, literal_map(parsed_jp.archive)),
    ):
        expected = {
            "raw_size": len(raw),
            "raw_sha256": sha256(raw),
            "record_count": archive.record_count,
        }
        if "literal_slot_count" in stock:
            expected["literal_slot_count"] = len(literals)
        for key, value in expected.items():
            if stock.get(key) != value:
                raise TransferError(f"mirror stock {key} mismatch")
    overlay_catalog = recipe.get("input_overlay_catalog")
    if not isinstance(overlay_catalog, dict):
        raise TransferError("mirror overlay catalog is invalid")
    expected_overlay = {
        "source_resource": SOURCE_RESOURCE,
        "overlay_count": INPUT_OVERLAY_COUNT,
        "entry_count": INPUT_ENTRY_COUNT,
        "input_manifest_sha256": INPUT_MANIFEST_SHA256,
        "coordinates_sha256": INPUT_COORDINATES_SHA256,
        "inputs": catalog["inputs"],
    }
    if overlay_catalog != expected_overlay:
        raise TransferError("mirror overlay catalog changed")

    replacements: dict[tuple[int, int, int], str] = {}
    for item in catalog["entries"]:
        coordinate = item["coordinate"]
        source = sc_literals.get(coordinate)
        if source is None or text_hash(source.text) != item["source_sc_hash"]:
            raise TransferError(f"mirror SC source hash mismatch at {coordinate}")
        replacement = item["ko"]
        validate_utf16_capacity(replacement, coordinate=coordinate)
        if common.invariant_mismatches(source.text, replacement):
            raise TransferError(f"mirror SC control/layout invariant mismatch at {coordinate}")
        if script_counts(replacement) != {"cjk_unified_count": 0, "kana_count": 0}:
            raise TransferError(f"source script in mirror replacement at {coordinate}")
        if coordinate in replacements:
            raise TransferError(f"duplicate mirror coordinate: {coordinate}")
        replacements[coordinate] = replacement
    if len(replacements) != MIRROR_COUNT or set(replacements) != catalog["coordinates"]:
        raise TransferError("mirror replacement coverage changed")

    capacity = capacity_manifest(parsed_sc.archive, replacements)
    rebuilt = msggame.rebuild_packed_with_literals(packed_sc, replacements)
    verified = msggame.parse_packed_msggame(rebuilt)
    _candidate_header, candidate_raw = decompress_wrapper(rebuilt)
    if msggame.rebuild_raw_msggame(verified.archive) != candidate_raw:
        raise TransferError("mirror candidate raw parse/rebuild is not byte-exact")
    verified_literals = literal_map(verified.archive)
    if verified.archive.record_count != SOURCE_PINS["SC"]["record_count"]:
        raise TransferError("mirror candidate record count changed")
    if set(verified_literals) != set(sc_literals):
        raise TransferError("mirror candidate changed SC literal coordinates")
    changed = 0
    for coordinate, source in sc_literals.items():
        expected_text = replacements.get(coordinate, source.text)
        if verified_literals[coordinate].text != expected_text:
            raise TransferError(f"mirror candidate literal verification failed at {coordinate}")
        changed += int(expected_text != source.text)
    if changed != MIRROR_CHANGED_COUNT:
        raise TransferError(f"mirror changed-literal count changed: {changed}")
    expected_candidate = recipe.get("expected_candidate")
    actual_candidate = {
        "packed_size": len(rebuilt),
        "packed_sha256": sha256(rebuilt),
        "raw_size": len(candidate_raw),
        "raw_sha256": sha256(candidate_raw),
        "record_count": verified.archive.record_count,
        "literal_slot_count": len(verified_literals),
    }
    if expected_candidate != actual_candidate:
        raise TransferError("mirror candidate digest or structure changed")
    return rebuilt, {
        "schema": "nobu16.kr.msggame-jp-sc-container-mirror-build-manifest.v1",
        "recipe_id": MIRROR_RECIPE_ID,
        "resource": TARGET_RESOURCE,
        "entry_count": len(replacements),
        "changed_literal_count": changed,
        "source_sc": {
            "packed_size": len(packed_sc),
            "packed_sha256": sha256(packed_sc),
            "raw_size": len(raw_sc),
            "raw_sha256": sha256(raw_sc),
        },
        "jp_target_guard": {
            "packed_size": len(packed_jp_guard),
            "packed_sha256": sha256(packed_jp_guard),
            "raw_size": len(raw_jp),
            "raw_sha256": sha256(raw_jp),
        },
        "candidate": actual_candidate,
        "capacity": capacity,
        "checks": {
            "all_11722_overlay_coordinates_applied": True,
            "all_sc_source_hashes_exact": True,
            "all_sc_control_layout_invariants_exact": True,
            "sc_container_record_count_preserved": True,
            "sc_literal_coordinates_preserved": True,
            "non_overlay_literals_preserved": True,
            "packed_candidate_parse_verified": True,
            "raw_parse_rebuild_byte_exact": True,
            "jp_stock_target_guard_exact": True,
        },
        "installed_game_file_written": False,
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    source_sc_path = args.pk_sc.resolve()
    target_jp_path = args.pk_jp.resolve()
    context_tc_path = args.pk_tc.resolve()
    context_en_path = args.pk_en.resolve()
    progress_path = args.progress.resolve()
    before = {
        str(path): sha256(path.read_bytes())
        for path in (
            source_sc_path,
            target_jp_path,
            context_tc_path,
            context_en_path,
            progress_path,
            README_PATH,
        )
    }
    catalog = collect_overlay_inputs(progress_path)
    for item in catalog["inputs"]:
        path = REPO_ROOT / item["path"]
        before[str(path)] = sha256(path.read_bytes())
    source_sc = load_source(source_sc_path, "SC")
    target_jp = load_source(target_jp_path, "JP")
    context_tc = load_source(context_tc_path, "TC")
    context_en = load_source(context_en_path, "EN")
    classified = classify_entries(source_sc, target_jp, context_tc, context_en, catalog)
    recipe = _recipe(target_jp, catalog, classified)
    candidate, candidate_manifest = apply_recipe_blob(target_jp["packed"], recipe)
    mirror_recipe = _mirror_recipe(source_sc, target_jp, catalog)
    mirror_candidate, mirror_manifest = apply_mirror_recipe_blob(
        source_sc["packed"], target_jp["packed"], catalog, mirror_recipe
    )

    out_root = args.out_root.resolve()
    recipe_path = out_root / "public" / RECIPE_NAME
    mirror_recipe_path = out_root / "public" / MIRROR_RECIPE_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    validation_path = out_root / VALIDATION_NAME
    recipe_artifact = write_json(recipe_path, recipe)
    mirror_recipe_artifact = write_json(mirror_recipe_path, mirror_recipe)
    readme_blob = README_PATH.read_bytes()
    readme_artifact = {
        "path": README_PATH.name,
        "size": len(readme_blob),
        "sha256": sha256(readme_blob),
    }

    evidence = {
        "schema": "nobu16.kr.msggame-pk-jp-transfer-evidence.v1",
        "recipe_id": RECIPE_ID,
        "source_free": True,
        "source_resource": SOURCE_RESOURCE,
        "target_resource": TARGET_RESOURCE,
        "stock_pins": {language: SOURCE_PINS[language] for language in ("SC", "JP", "TC", "EN")},
        "input_overlays": catalog["inputs"],
        "input_manifest_sha256": INPUT_MANIFEST_SHA256,
        "input_coordinate_count": INPUT_ENTRY_COUNT,
        "input_coordinates_sha256": INPUT_COORDINATES_SHA256,
        "multilingual_record_directory_alignment": classified[
            "multilingual_record_directory_alignment"
        ],
        "compatibility": {
            "direct_count": DIRECT_COUNT,
            "remapped_count": REMAPPED_COUNT,
            "transferable_count": TRANSFERABLE_COUNT,
            "blocked_count": BLOCKED_COUNT,
            "direct_coordinates_sha256": DIRECT_COORDINATES_SHA256,
            "remapped_coordinates_sha256": REMAPPED_COORDINATES_SHA256,
            "transferable_coordinates_sha256": TRANSFERABLE_COORDINATES_SHA256,
            "blocked_coordinates_sha256": BLOCKED_COORDINATES_SHA256,
            "primary_reason_counts": classified["primary_reasons"],
            "nonexclusive_reason_counts": classified["nonexclusive_reasons"],
            "jp_invariant_mismatch_key_counts": classified["invariant_mismatch_keys"],
            "transferable_by_block": classified["block_transferable"],
            "blocked_by_block": classified["block_blocked"],
            "counts_by_origin": classified["origin_counts"],
            "ui_b05_b07": {
                "input": 900,
                "direct": 144,
                "remapped": 35,
                "native_total": 179,
                "native_blocked": 721,
                "sc_container_mirror": 900,
            },
        },
        "capacity": {
            "max_selected_literal_utf16_bytes": classified["max_utf16_bytes"],
            **candidate_manifest["capacity"],
        },
        "native_candidate_ab": {
            "A_stock_jp": candidate_manifest["source"],
            "B_memory_built_candidate": candidate_manifest["candidate"],
            "candidate_written_to_game": False,
        },
        "mirror_candidate_ab": {
            "A_stock_jp_target_guard": mirror_manifest["jp_target_guard"],
            "A_stock_sc_container": mirror_manifest["source_sc"],
            "B_memory_built_sc_container_at_jp_target": mirror_manifest["candidate"],
            "overlay_entry_count": MIRROR_COUNT,
            "changed_literal_count": mirror_manifest["changed_literal_count"],
            "checks": mirror_manifest["checks"],
            "candidate_written_to_game": False,
        },
        "recipe_artifacts": {
            "native": recipe_artifact,
            "sc_container_mirror": mirror_recipe_artifact,
        },
        "entry_count": TRANSFERABLE_COUNT,
        "entries": [item["evidence"] for item in classified["transferable"]],
        "contains_commercial_source_text": False,
    }
    evidence_artifact = write_json(evidence_path, evidence)

    review = {
        "schema": "nobu16.kr.msggame-pk-jp-transfer-blocked-review.v1",
        "recipe_id": RECIPE_ID,
        "quality_state": "fail_closed_blocked_entries_require_jp_specific_human_adapter",
        "selected_count": TRANSFERABLE_COUNT,
        "blocked_count": BLOCKED_COUNT,
        "direct_count": DIRECT_COUNT,
        "remapped_count": REMAPPED_COUNT,
        "mirror_route_preserves_all_input_entries": True,
        "primary_reason_counts": classified["primary_reasons"],
        "nonexclusive_reason_counts": classified["nonexclusive_reasons"],
        "entries": classified["blocked"],
        "contains_commercial_source_text": False,
    }
    review_artifact = write_json(review_path, review)
    source_free_scan = assert_source_free(
        (recipe_path, mirror_recipe_path, evidence_path, review_path, README_PATH)
    )

    staging = write_private_candidates(
        args.private_staging_root, candidate, mirror_candidate
    )

    after = {path: sha256(Path(path).read_bytes()) for path in before}
    if before != after:
        raise TransferError("read-only input changed during JP transfer build")
    validation = {
        "schema": "nobu16.kr.msggame-pk-jp-transfer-validation.v1",
        "recipe_id": RECIPE_ID,
        "passed": True,
        "runtime_validation": {
            "state": RUNTIME_VALIDATION_STATE,
            "installed_game_candidate_application_run": False,
            "game_process_launch_run": False,
            "screen_capture_verification_run": False,
            "release_ready": False,
        },
        "counts": {
            "input": INPUT_ENTRY_COUNT,
            "direct": DIRECT_COUNT,
            "remapped": REMAPPED_COUNT,
            "transferable": TRANSFERABLE_COUNT,
            "blocked": BLOCKED_COUNT,
            "classified_total": TRANSFERABLE_COUNT + BLOCKED_COUNT,
            "mirror_preserved": MIRROR_COUNT,
            "mirror_changed": MIRROR_CHANGED_COUNT,
            "ui_b05_b07_input": 900,
            "ui_b05_b07_native": 179,
            "ui_b05_b07_mirror": 900,
        },
        "coordinate_sets": {
            "input_sha256": INPUT_COORDINATES_SHA256,
            "direct_sha256": DIRECT_COORDINATES_SHA256,
            "remapped_sha256": REMAPPED_COORDINATES_SHA256,
            "transferable_sha256": TRANSFERABLE_COORDINATES_SHA256,
            "blocked_sha256": BLOCKED_COORDINATES_SHA256,
            "transferable_blocked_disjoint": True,
            "classification_covers_input": True,
        },
        "proofs": {
            "all_input_overlays_source_free_and_pinned": True,
            "all_sc_source_hashes_exact": True,
            "all_sc_jp_tc_en_private_sources_pinned": True,
            "direct_and_remapped_partition_exact": True,
            "remapped_entries_have_unique_same_record_equal_cardinality_ordinal_targets": True,
            "remapped_entries_include_source_free_four_language_context_anchors": True,
            "jp_coordinate_existence_fail_closed": True,
            "jp_record_literal_count_fail_closed": True,
            "jp_record_nonliteral_structure_fail_closed": True,
            "jp_control_layout_invariants_fail_closed": True,
            "utf16_literal_record_block_and_raw_capacity_fail_closed": True,
            "blocked_entries_not_applied": True,
            "jp_literal_coordinates_preserved": True,
            "jp_non_recipe_literals_preserved": True,
            "recipe_replacements_verified_after_rebuild": True,
            "mirror_all_11722_overlay_coordinates_applied": True,
            "mirror_sc_container_record_count_and_literal_coordinates_preserved": True,
            "mirror_non_overlay_literals_preserved": True,
            "mirror_packed_parse_and_raw_roundtrip_verified": True,
            "mirror_jp_target_stock_guard_exact": True,
        },
        "native_candidate_ab": {
            "A_stock_jp": candidate_manifest["source"],
            "B_candidate": candidate_manifest["candidate"],
            "checks": candidate_manifest["checks"],
            "installed_game_file_written": False,
            "private_candidate_written": staging["native_written"],
            "private_candidate_path_recorded": False,
        },
        "mirror_candidate_ab": {
            "A_stock_jp_target_guard": mirror_manifest["jp_target_guard"],
            "A_stock_sc_container": mirror_manifest["source_sc"],
            "B_candidate": mirror_manifest["candidate"],
            "checks": mirror_manifest["checks"],
            "installed_game_file_written": False,
            "private_candidate_written": staging["mirror_written"],
            "private_candidate_path_recorded": False,
        },
        "private_staging": {
            "written": staging["written"],
            "exact_layout": staging["exact_layout"],
            "native_relative_path": NATIVE_STAGE_RELATIVE.as_posix(),
            "mirror_relative_path": MIRROR_STAGE_RELATIVE.as_posix(),
            "arbitrary_absolute_file_output_supported": False,
            "game_root_output_allowed": False,
        },
        "source_free_scan": source_free_scan,
        "artifacts": {
            "recipe": recipe_artifact,
            "mirror_recipe": mirror_recipe_artifact,
            "evidence": evidence_artifact,
            "review": review_artifact,
            "readme": readme_artifact,
        },
        "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
        "safety": {
            "installed_game_files_modified": False,
            "source_sc_modified": False,
            "source_jp_modified": False,
            "source_tc_modified": False,
            "source_en_modified": False,
            "shared_progress_modified": False,
            "shared_readme_modified": False,
            "runtime_game_validation_run": False,
            "release_ready": False,
            "executable_modified": False,
            "dll_injection": False,
            "process_memory_access": False,
            "registry_modified": False,
        },
    }
    validation_artifact = write_json(validation_path, validation)
    assert_source_free((validation_path,))
    return {
        "input_count": INPUT_ENTRY_COUNT,
        "direct_count": DIRECT_COUNT,
        "remapped_count": REMAPPED_COUNT,
        "transferable_count": TRANSFERABLE_COUNT,
        "blocked_count": BLOCKED_COUNT,
        "mirror_count": MIRROR_COUNT,
        "mirror_changed_count": MIRROR_CHANGED_COUNT,
        "recipe_sha256": recipe_artifact["sha256"],
        "candidate_packed_sha256": candidate_manifest["candidate"]["packed_sha256"],
        "candidate_packed_size": candidate_manifest["candidate"]["packed_size"],
        "mirror_recipe_sha256": mirror_recipe_artifact["sha256"],
        "mirror_candidate_packed_sha256": mirror_manifest["candidate"]["packed_sha256"],
        "mirror_candidate_packed_size": mirror_manifest["candidate"]["packed_size"],
        "private_candidate_written": staging["native_written"],
        "private_mirror_candidate_written": staging["mirror_written"],
        "artifacts": {
            "recipe": recipe_artifact,
            "mirror_recipe": mirror_recipe_artifact,
            "evidence": evidence_artifact,
            "review": review_artifact,
            "validation": validation_artifact,
        },
    }


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--pk-sc", type=Path, default=DEFAULT_SC)
    value.add_argument("--pk-jp", type=Path, default=DEFAULT_JP)
    value.add_argument("--pk-tc", type=Path, default=DEFAULT_TC)
    value.add_argument("--pk-en", type=Path, default=DEFAULT_EN)
    value.add_argument("--progress", type=Path, default=DEFAULT_PROGRESS)
    value.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    value.add_argument("--private-staging-root", type=Path)
    return value


def main() -> int:
    print(json.dumps(build(parser().parse_args()), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
