#!/usr/bin/env python3
"""Build and validate one source-free wave06 PK msggame overlay.

The translation modules contain coordinate-to-Korean mappings only.  The
commercial SC/JP/EN/TC context remains under ``tmp`` and is used solely for
local invariant and source-hash verification.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
PARTITION_PATH = WORKSTREAM_ROOT / "partition.v1.json"
RESOURCE = "MSG_PK/SC/msggame.bin"
OVERLAY_SCHEMA = "nobu16.kr.msggame-literal-overlay.v1"
VALIDATION_SCHEMA = "nobu16.kr.msggame-wave06-batch-validation.v1"
HEX64_RE = re.compile(r"[0-9A-F]{64}\Z")
CJK_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")
KANA_RE = re.compile(r"[\u3040-\u30FF\u31F0-\u31FF]")
HANGUL_RE = re.compile(r"[\uAC00-\uD7A3]")

STOCK_SC = {
    "packed_size": 529_419,
    "packed_sha256": "BD7B33FCC7495B855B0828C7FE4E5F7ADB2DE656A9B12E20259750F94EE665D6",
    "raw_size": 1_077_200,
    "raw_sha256": "1958B2B801D37186D478284EA0E29CA96D8DA2BC087D6BEB74A4139EF01C11CE",
    "record_count": 21_581,
    "literal_slot_count": 25_598,
}


class BatchError(ValueError):
    """Raised when a wave06 translation batch violates its frozen contract."""


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256_bytes(text.encode("utf-16-le"))


def canonical_hash(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    )


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise BatchError(f"JSON root must be an object: {path}")
    return value


def partition_batch(batch: str) -> dict[str, Any]:
    value = read_object(PARTITION_PATH)
    matches = [
        item
        for item in value.get("batches", [])
        if isinstance(item, dict)
        and str(item.get("batch_id", "")).startswith(
            f"msggame_pk_parallel_{batch.lower()}_"
        )
    ]
    if len(matches) != 1:
        raise BatchError(f"partition must contain exactly one {batch} batch")
    item = matches[0]
    coordinates = item.get("coordinates")
    if not isinstance(coordinates, list):
        raise BatchError("partition batch coordinates are invalid")
    if canonical_hash(coordinates) != item.get("coordinates_sha256"):
        raise BatchError("partition coordinate hash changed")
    if len(coordinates) != item.get("coordinate_count"):
        raise BatchError("partition coordinate count changed")
    return item


def discover_context(batch: str) -> Path:
    pattern = f"msggame_pk_parallel_{batch.lower()}_*.private.json"
    matches = sorted((REPO_ROOT / "tmp").glob(f"msggame_pk_parallel_wave06_private_*/{pattern}"))
    if len(matches) != 1:
        raise BatchError(
            f"expected exactly one private {batch} context under repo tmp; got {len(matches)}"
        )
    return matches[0]


def load_context(path: Path, spec: dict[str, Any]) -> dict[tuple[int, int, int], dict[str, Any]]:
    value = read_object(path)
    if value.get("must_not_be_committed") is not True:
        raise BatchError("private context safety marker is missing")
    if value.get("batch_id") != spec["batch_id"]:
        raise BatchError("private context batch id differs from partition")
    if value.get("coordinate_count") != spec["coordinate_count"]:
        raise BatchError("private context coordinate count differs from partition")
    if value.get("coordinates_sha256") != spec["coordinates_sha256"]:
        raise BatchError("private context coordinate hash differs from partition")
    entries = value.get("entries")
    if not isinstance(entries, list):
        raise BatchError("private context entries are invalid")
    result: dict[tuple[int, int, int], dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("coordinate"), list):
            raise BatchError("private context contains an invalid entry")
        coordinate = tuple(entry["coordinate"])
        if len(coordinate) != 3 or not all(type(item) is int for item in coordinate):
            raise BatchError("private context coordinate is invalid")
        if coordinate in result:
            raise BatchError(f"private context duplicates coordinate {coordinate}")
        official = entry.get("official")
        if not isinstance(official, dict) or not isinstance(official.get("SC"), str):
            raise BatchError(f"private context lacks SC source at {coordinate}")
        result[coordinate] = entry
    expected = {tuple(item) for item in spec["coordinates"]}
    if set(result) != expected:
        raise BatchError("private context coordinate set differs from partition")
    return result


def load_module(path: Path, ordinal: int) -> tuple[dict[tuple[int, int, int], str], dict[tuple[int, int, int], str]]:
    module_name = f"_nobu16_wave06_{path.parent.name}_{ordinal}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise BatchError(f"cannot load translation module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    mappings = [
        value
        for name, value in vars(module).items()
        if name.startswith("TRANSLATIONS") and isinstance(value, dict)
    ]
    if len(mappings) != 1:
        raise BatchError(f"{path} must expose exactly one TRANSLATIONS* dict")
    translations = mappings[0]
    statuses = getattr(module, "STATUSES", {})
    if not isinstance(statuses, dict):
        raise BatchError(f"{path} STATUSES must be a dict")
    normalized: dict[tuple[int, int, int], str] = {}
    normalized_statuses: dict[tuple[int, int, int], str] = {}
    for coordinate, ko in translations.items():
        if (
            not isinstance(coordinate, tuple)
            or len(coordinate) != 3
            or not all(type(item) is int for item in coordinate)
            or not isinstance(ko, str)
            or "\0" in ko
        ):
            raise BatchError(f"{path} contains an invalid translation entry")
        normalized[coordinate] = ko
        status = statuses.get(coordinate, "translated")
        if status not in {"translated", "reviewed"}:
            raise BatchError(f"{path} has an invalid status at {coordinate}")
        normalized_statuses[coordinate] = status
    if set(statuses) - set(normalized):
        raise BatchError(f"{path} has status-only coordinates")
    return normalized, normalized_statuses


def load_translations(batch_root: Path) -> tuple[dict[tuple[int, int, int], str], dict[tuple[int, int, int], str], list[Path]]:
    paths = sorted(batch_root.glob("translations_part*.py"))
    if not paths:
        raise BatchError(f"no translation parts found in {batch_root}")
    translations: dict[tuple[int, int, int], str] = {}
    statuses: dict[tuple[int, int, int], str] = {}
    for ordinal, path in enumerate(paths):
        part, part_statuses = load_module(path, ordinal)
        overlap = set(translations) & set(part)
        if overlap:
            raise BatchError(f"translation parts overlap at {min(overlap)}")
        translations.update(part)
        statuses.update(part_statuses)
    return translations, statuses, paths


def invariant_mismatches(source: str, replacement: str) -> list[str]:
    tools_root = REPO_ROOT / "tools"
    if str(tools_root) not in sys.path:
        sys.path.insert(0, str(tools_root))
    from build_common_message_overlay import invariant_mismatches as compare

    return list(compare(source, replacement))


def build(batch: str, context_path: Path | None = None) -> dict[str, Any]:
    batch = batch.lower()
    if re.fullmatch(r"b(?:0[8-9]|1[0-5])", batch) is None:
        raise BatchError("batch must be one of b08 through b15")
    spec = partition_batch(batch)
    context_path = context_path or discover_context(batch)
    context = load_context(context_path.resolve(), spec)
    batch_root = REPO_ROOT / "workstreams" / f"msggame_pk_parallel_{batch}"
    translations, statuses, part_paths = load_translations(batch_root)
    expected = {tuple(item) for item in spec["coordinates"]}
    if set(translations) != expected:
        missing = sorted(expected - set(translations))
        extra = sorted(set(translations) - expected)
        raise BatchError(
            f"{batch} coverage differs: missing={len(missing)} {missing[:3]}, "
            f"extra={len(extra)} {extra[:3]}"
        )

    source_to_ko: dict[str, str] = {}
    reviewed = 0
    semantic = 0
    for coordinate in sorted(translations):
        source = context[coordinate]["official"]["SC"]
        replacement = translations[coordinate]
        mismatches = invariant_mismatches(source, replacement)
        if mismatches:
            raise BatchError(f"invariant mismatch at {coordinate}: {mismatches}")
        if CJK_RE.search(replacement) or KANA_RE.search(replacement):
            raise BatchError(f"source script leaked at {coordinate}")
        source_hash = text_hash(source)
        previous = source_to_ko.setdefault(source_hash, replacement)
        if previous != replacement:
            raise BatchError(f"duplicate source translation differs at {coordinate}")
        if CJK_RE.search(source):
            semantic += 1
            if HANGUL_RE.search(replacement) is None:
                raise BatchError(f"semantic source has no Hangul replacement at {coordinate}")
        if statuses[coordinate] == "reviewed":
            reviewed += 1

    entries = [
        {
            "block_id": coordinate[0],
            "record_id": coordinate[1],
            "literal_id": coordinate[2],
            "source_sc_utf16le_sha256": text_hash(
                context[coordinate]["official"]["SC"]
            ),
            "ko": translations[coordinate],
        }
        for coordinate in sorted(translations)
    ]
    overlay_id = spec["batch_id"]
    overlay = {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": overlay_id,
        "resource": RESOURCE,
        "base_language": "SC",
        "entry_count": len(entries),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": STOCK_SC,
        "defaults": {"status": "translated"},
        "translation_provenance": {
            "context_languages": ["SC", "JP", "EN", "TC"],
            "kind": "parallel_agent_wave06_full_remaining_translation",
            "runtime_reviewed": False,
            "source_text_embedded": False,
        },
        "entries": entries,
    }
    public_root = batch_root / "public"
    overlay_path = public_root / f"msggame_ko_{overlay_id}.json"
    overlay_blob = json_bytes(overlay)
    public_root.mkdir(parents=True, exist_ok=True)
    overlay_path.write_bytes(overlay_blob)

    validation = {
        "schema": VALIDATION_SCHEMA,
        "batch_id": spec["batch_id"],
        "passed": True,
        "coordinate_count": len(entries),
        "coordinates_sha256": spec["coordinates_sha256"],
        "semantic_coordinate_count": semantic,
        "reviewed_coordinate_count": reviewed,
        "unique_source_hash_count": len(source_to_ko),
        "duplicate_source_translation_consistent": True,
        "invariant_mismatch_count": 0,
        "source_script_leak_count": 0,
        "private_context": {
            "committed": False,
            "sha256": sha256_bytes(context_path.read_bytes()),
        },
        "translation_parts": [
            {
                "path": path.name,
                "sha256": sha256_bytes(path.read_bytes()),
            }
            for path in part_paths
        ],
        "overlay": {
            "path": overlay_path.relative_to(batch_root).as_posix(),
            "size": len(overlay_blob),
            "sha256": sha256_bytes(overlay_blob),
        },
    }
    validation_path = batch_root / "validation.v1.json"
    validation_path.write_bytes(json_bytes(validation))
    return {
        "batch": batch,
        "coordinate_count": len(entries),
        "coordinates_sha256": spec["coordinates_sha256"],
        "overlay": str(overlay_path),
        "overlay_sha256": sha256_bytes(overlay_blob),
        "validation": str(validation_path),
    }


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("batch", choices=[f"b{number:02d}" for number in range(8, 16)])
    value.add_argument("--context", type=Path)
    return value


def main() -> int:
    args = parser().parse_args()
    print(json.dumps(build(args.batch, args.context), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
