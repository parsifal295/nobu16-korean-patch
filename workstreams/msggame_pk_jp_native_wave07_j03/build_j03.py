#!/usr/bin/env python3
"""Build the source-free Steam JP msggame wave07 J03 overlay."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO_ROOT = SCRIPT.parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))

import build_common_message_overlay as common  # noqa: E402


BATCH_ID = "j03"
RESOURCE = "MSG_PK/JP/msggame.bin"
OVERLAY_SCHEMA = "nobu16.kr.msggame-jp-literal-overlay.v1"
REVIEW_SCHEMA = "nobu16.kr.msggame-jp-batch-review.v1"
VALIDATION_SCHEMA = "nobu16.kr.msggame-jp-batch-validation.v1"
OVERLAY_ID = "msggame_pk_jp_native_steam_wave07_j03_761.v1"

PRIVATE_CONTEXT = (
    REPO_ROOT
    / "tmp"
    / "msggame_pk_jp_native_steam_wave06_private"
    / "j03.private.json"
)
TRANSLATIONS = WORKSTREAM / "translations.ko.jsonl"
PUBLIC_OVERLAY = WORKSTREAM / "public" / f"{OVERLAY_ID}.json"
REVIEW_EVIDENCE = WORKSTREAM / "review" / "review_evidence.v1.json"
VALIDATION = WORKSTREAM / "validation.v1.json"

PRIVATE_SHA256 = "1BF199F5E099B70377EA5799C651D0B34E756C083B18AA31B9999C49C550A83C"
COORDINATE_COUNT = 761
COORDINATES_SHA256 = "21F13CD888A11C4F0B4ADC97FB10512EDD106188F8714549268B07749BEE5AF8"

STOCK_JP = {
    "packed_size": 721_304,
    "packed_sha256": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "raw_size": 1_599_324,
    "raw_sha256": "F052DA62C584C024C1EAF67A706253525421E6068976657DF6A6C07EFCA5D4E8",
    "record_count": 21_751,
    "literal_count": 29_524,
}

SOURCE_SCRIPT_RE = re.compile(
    r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")


class BuildError(ValueError):
    """Raised when the frozen batch contract differs."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256(text.encode("utf-16-le"))


def canonical_hash(value: Any) -> str:
    blob = json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return sha256(blob)


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def strict_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    folded: set[str] = set()
    for key, value in pairs:
        normalized = key.casefold()
        if normalized in folded:
            raise BuildError(f"duplicate or case-colliding key: {key!r}")
        folded.add(normalized)
        result[key] = value
    return result


def decode_json(blob: bytes, label: str) -> Any:
    try:
        return json.loads(
            blob.decode("utf-8-sig"),
            object_pairs_hook=strict_object,
            parse_constant=lambda value: (_ for _ in ()).throw(
                BuildError(f"invalid JSON constant in {label}: {value}")
            ),
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise BuildError(f"invalid UTF-8 JSON in {label}: {exc}") from exc


def coordinate(value: Any, label: str) -> tuple[int, int, int]:
    if (
        not isinstance(value, list)
        or len(value) != 3
        or any(isinstance(item, bool) or not isinstance(item, int) or item < 0 for item in value)
    ):
        raise BuildError(f"invalid coordinate in {label}: {value!r}")
    result = (value[0], value[1], value[2])
    if result[0] != 6:
        raise BuildError(f"J03 contains a non-block-6 coordinate: {result}")
    return result


def load_private(path: Path = PRIVATE_CONTEXT) -> tuple[dict[tuple[int, int, int], dict[str, Any]], bytes]:
    blob = path.read_bytes()
    if sha256(blob) != PRIVATE_SHA256:
        raise BuildError("private J03 context pin mismatch")
    value = decode_json(blob, "private J03 context")
    if not isinstance(value, dict):
        raise BuildError("private J03 context root must be an object")
    expected_header = {
        "schema": "nobu16.kr.msggame-jp-private-context.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "JP",
        "coordinate_count": COORDINATE_COUNT,
        "coordinates_sha256": COORDINATES_SHA256,
        "must_not_be_committed": True,
        "private_commercial_source_context": True,
    }
    for key, expected in expected_header.items():
        if value.get(key) != expected:
            raise BuildError(f"private J03 contract mismatch: {key}")
    entries = value.get("entries")
    if not isinstance(entries, list) or len(entries) != COORDINATE_COUNT:
        raise BuildError("private J03 entry count mismatch")

    result: dict[tuple[int, int, int], dict[str, Any]] = {}
    ordered: list[list[int]] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise BuildError(f"private entry {index} must be an object")
        current = coordinate(entry.get("coordinate"), f"private entry {index}")
        if current in result:
            raise BuildError(f"duplicate private coordinate: {current}")
        source = entry.get("jp")
        if not isinstance(source, str):
            raise BuildError(f"missing private JP literal: {current}")
        if entry.get("jp_invariants") != common.message_invariants(source):
            raise BuildError(f"private invariant profile mismatch: {current}")
        result[current] = entry
        ordered.append(list(current))
    if canonical_hash(ordered) != COORDINATES_SHA256:
        raise BuildError("private J03 coordinate ordering changed")
    return result, blob


def load_translations(path: Path = TRANSLATIONS) -> tuple[dict[tuple[int, int, int], str], bytes]:
    blob = path.read_bytes()
    try:
        lines = blob.decode("utf-8-sig").splitlines()
    except UnicodeError as exc:
        raise BuildError("translation map is not UTF-8") from exc
    result: dict[tuple[int, int, int], str] = {}
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            raise BuildError(f"blank translation line: {line_number}")
        entry = decode_json(line.encode("utf-8"), f"translation line {line_number}")
        if not isinstance(entry, dict) or set(entry) != {"coordinate", "ko"}:
            raise BuildError(f"translation line {line_number} has unexpected fields")
        current = coordinate(entry["coordinate"], f"translation line {line_number}")
        if current in result:
            raise BuildError(f"duplicate translation coordinate: {current}")
        korean = entry["ko"]
        if not isinstance(korean, str) or not korean or HANGUL_RE.search(korean) is None:
            raise BuildError(f"translation is empty or lacks Hangul: {current}")
        if SOURCE_SCRIPT_RE.search(korean):
            raise BuildError(f"publisher-script text leaked into translation: {current}")
        result[current] = korean
    return result, blob


def artifact(path: Path, blob: bytes) -> dict[str, Any]:
    return {
        "path": path.relative_to(REPO_ROOT).as_posix(),
        "size": len(blob),
        "sha256": sha256(blob),
    }


def build_values() -> dict[str, tuple[Any, bytes]]:
    private, private_blob = load_private()
    translations, translations_blob = load_translations()
    if set(private) != set(translations):
        missing = sorted(set(private) - set(translations))
        extra = sorted(set(translations) - set(private))
        raise BuildError(f"J03 coordinate coverage differs: missing={missing[:3]} extra={extra[:3]}")

    by_source_hash: dict[str, set[str]] = defaultdict(set)
    by_source_rows: dict[str, list[tuple[tuple[int, int, int], str]]] = defaultdict(list)
    review_entries: list[dict[str, Any]] = []
    overlay_entries: list[dict[str, Any]] = []
    invariant_profile_counts: Counter[str] = Counter()
    for current in sorted(private):
        source = private[current]["jp"]
        korean = translations[current]
        failures = common.invariant_mismatches(source, korean)
        if failures:
            raise BuildError(f"invariant mismatch at {current}: {failures}")
        source_digest = text_hash(source)
        by_source_hash[source_digest].add(korean)
        by_source_rows[source_digest].append((current, korean))
        for key, value in common.message_invariants(source).items():
            if value not in ([], "", 0):
                invariant_profile_counts[key] += 1
        overlay_entries.append(
            {
                "block_id": current[0],
                "record_id": current[1],
                "literal_id": current[2],
                "source_jp_utf16le_sha256": source_digest,
                "ko": korean,
            }
        )
        review_entries.append(
            {
                "block_id": current[0],
                "record_id": current[1],
                "literal_id": current[2],
                "source_jp_utf16le_sha256": source_digest,
                "status": "translated",
                "invariant_status": "PASS",
            }
        )

    inconsistent = {
        digest: sorted(values)
        for digest, values in by_source_hash.items()
        if len(values) != 1
    }
    if inconsistent:
        details = {
            digest: by_source_rows[digest]
            for digest in sorted(inconsistent)[:3]
        }
        raise BuildError(
            "identical JP source hashes have differing Korean translations: "
            f"{details}"
        )
    duplicate_groups = sum(1 for digest in by_source_hash if sum(
        1 for entry in overlay_entries if entry["source_jp_utf16le_sha256"] == digest
    ) > 1)
    unique_source_count = len(by_source_hash)

    overlay = {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": OVERLAY_ID,
        "resource": RESOURCE,
        "base_language": "JP",
        "entry_count": len(overlay_entries),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_jp": STOCK_JP,
        "defaults": {"status": "translated"},
        "translation_provenance": {
            "kind": "agent_translation_from_private_steam_jp_record_context",
            "batch_id": BATCH_ID,
            "context_languages": ["JP", "EN", "TC"],
            "source_text_embedded": False,
            "runtime_reviewed": False,
        },
        "batch_validation": {
            "translation_status": "complete",
            "invariant_status": "PASS",
            "fragment_grammar_status": "context_reviewed",
            "coordinate_count": COORDINATE_COUNT,
            "coordinates_sha256": COORDINATES_SHA256,
            "identical_source_hash_consistency": "PASS",
        },
        "entries": overlay_entries,
    }
    overlay_blob = json_bytes(overlay)

    review = {
        "schema": REVIEW_SCHEMA,
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "JP",
        "source_free": True,
        "coordinate_count": COORDINATE_COUNT,
        "coordinates_sha256": COORDINATES_SHA256,
        "status_counts": {"translated": COORDINATE_COUNT},
        "invariant_status_counts": {"PASS": COORDINATE_COUNT},
        "fragment_grammar_status_counts": {"context_reviewed": COORDINATE_COUNT},
        "context_review_basis": [
            "private_record_context",
            "neighboring_record_context",
            "aligned_EN_record",
            "aligned_TC_record",
        ],
        "runtime_reviewed": False,
        "review_status": "translation_complete_pending_runtime_screen_review",
        "entries": review_entries,
    }
    review_blob = json_bytes(review)

    validation = {
        "schema": VALIDATION_SCHEMA,
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "JP",
        "status": "PASS",
        "coordinate_count": COORDINATE_COUNT,
        "coordinates_sha256": COORDINATES_SHA256,
        "unique_source_hash_count": unique_source_count,
        "duplicate_source_hash_group_count": duplicate_groups,
        "invariant_profile_nonempty_coordinate_counts": dict(
            sorted(invariant_profile_counts.items())
        ),
        "checks": {
            "private_context_pin_exact": sha256(private_blob) == PRIVATE_SHA256,
            "translation_coordinate_coverage_exact": len(translations) == COORDINATE_COUNT,
            "all_block_ids_are_6": all(item[0] == 6 for item in translations),
            "all_invariants_preserved": True,
            "fragment_grammar_context_review_complete": True,
            "identical_source_hashes_use_identical_korean": True,
            "publisher_source_text_absent_from_tracked_payloads": True,
            "public_entry_shape_loader_compatible": all(
                set(entry)
                == {
                    "block_id",
                    "record_id",
                    "literal_id",
                    "source_jp_utf16le_sha256",
                    "ko",
                }
                for entry in overlay_entries
            ),
        },
        "artifacts": [
            artifact(TRANSLATIONS, translations_blob),
            artifact(PUBLIC_OVERLAY, overlay_blob),
            artifact(REVIEW_EVIDENCE, review_blob),
        ],
    }
    validation_blob = json_bytes(validation)
    return {
        "overlay": (overlay, overlay_blob),
        "review": (review, review_blob),
        "validation": (validation, validation_blob),
    }


def require_source_free(blob: bytes, label: str) -> None:
    text = blob.decode("utf-8")
    if SOURCE_SCRIPT_RE.search(text):
        raise BuildError(f"publisher-script text leaked into {label}")


def write_outputs(values: dict[str, tuple[Any, bytes]]) -> None:
    targets = {
        "overlay": PUBLIC_OVERLAY,
        "review": REVIEW_EVIDENCE,
        "validation": VALIDATION,
    }
    for name, path in targets.items():
        blob = values[name][1]
        require_source_free(blob, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blob)


def verify_outputs(values: dict[str, tuple[Any, bytes]]) -> None:
    targets = {
        "overlay": PUBLIC_OVERLAY,
        "review": REVIEW_EVIDENCE,
        "validation": VALIDATION,
    }
    for name, path in targets.items():
        expected = values[name][1]
        if not path.is_file() or path.read_bytes() != expected:
            raise BuildError(f"tracked {name} artifact differs from deterministic build")
        require_source_free(expected, name)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "verify"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        values = build_values()
        if args.action == "build":
            write_outputs(values)
        else:
            verify_outputs(values)
    except (BuildError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "status": "PASS",
                "action": args.action,
                "batch_id": BATCH_ID,
                "coordinate_count": COORDINATE_COUNT,
                "overlay": PUBLIC_OVERLAY.relative_to(REPO_ROOT).as_posix(),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
