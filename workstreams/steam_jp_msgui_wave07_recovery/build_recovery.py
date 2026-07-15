#!/usr/bin/env python3
"""Build the source-free Steam JP msgui withheld-entry recovery supplement."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO_ROOT = SCRIPT.parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


RESOURCE = "MSG_PK/JP/msgui.bin"
RUNTIME_VERSION = "1.1.7"
INPUT_AUDIT = REPO_ROOT / "workstreams" / "steam_jp_msgui_v1" / "remap_audit.v1.json"
FOUNDATION_OVERLAY = (
    REPO_ROOT
    / "workstreams"
    / "steam_jp_msgui_v1"
    / "public"
    / "msgui_ko_pk_jp_steam_native_v1.json"
)
DECISIONS = WORKSTREAM / "recovery_decisions.ko.jsonl"
PUBLIC_OVERLAY = (
    WORKSTREAM
    / "public"
    / "msgui_ko_pk_jp_steam_wave07_recovery_343.v1.json"
)
EXCLUSIONS = WORKSTREAM / "exclusions.v1.json"
REVIEW = WORKSTREAM / "review" / "review_evidence.v1.json"
VALIDATION = WORKSTREAM / "validation.v1.json"

DEFAULT_JP_STOCK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
    r"\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals"
    r"\MSG_PK\JP\msgui.bin"
)
DEFAULT_CONTEXT_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK")

AUDIT_SHA256 = "B9E65B6360AAA48F097873D218052A8A1D74CDB6FE462BD79963A17D414A397E"
FOUNDATION_SHA256 = "1581C52901FE536AF45F4FD6225E8D94795FDA883798947B6610D5CF86E09424"
WITHHELD_COUNT = 344
WITHHELD_COORDINATE_SHA256 = "040FC071EA485FDA3FBC5443F1253BDE6A351B3BFFC6F4ED5AB69A3823C916E4"
FOUNDATION_COUNT = 3_693
FOUNDATION_COORDINATE_SHA256 = "E1FFD90081D66D47E695E98AD1CE5BBA2EBADB6A5FE33EF7EA3CE1B5F7D0AF6F"
RECOVERED_COUNT = 343
EXCLUDED_COUNT = 1

PRIVATE_SPECS = {
    "JP": {
        "packed_size": 64_976,
        "packed_sha256": "9775D4B7253828899F7EF0DF2E88AB28121ACB260E1381F3D706C6A1065D504A",
        "raw_size": 105_864,
        "raw_sha256": "F79AE8B004AAE73F5F67ED0F858AAD74083649040F69A317E48212F74761095C",
        "string_count": 5_100,
    },
    "SC": {
        "packed_size": 63_366,
        "packed_sha256": "B21196467A5A2E08A4019D4CEC4A474A64C6F0CD577FA3D068F2130F95CF2C0C",
        "raw_size": 89_932,
        "raw_sha256": "289F913C7454ECD9C9DEAF8A621C8F6965985E5A4358CC8458E687CB6EE8318B",
        "string_count": 5_100,
    },
    "EN": {
        "packed_size": 89_180,
        "packed_sha256": "B993412D73889B58B68C8998446AF65E1C7CD02066FEAF483E3F44E3EB0602D5",
        "raw_size": 234_636,
        "raw_sha256": "FA8A335E81A90D82959008593F4659CB7A52C9D9375D52D2577FA69AF49AC850",
        "string_count": 5_100,
    },
    "TC": {
        "packed_size": 63_241,
        "packed_sha256": "FA4351F8303DFDAA240441C5BDF8B42DD4F7603E56E6DBAB8CB4DC0594C007D5",
        "raw_size": 90_124,
        "raw_sha256": "6843283064A953895405923696FFEF26F184F55ED0A2F6BFFB26ED7876770A1A",
        "string_count": 5_100,
    },
}

OVERLAY_SCHEMA = "nobu16.kr.steam-jp-msgui-supplement.v1"
EXCLUSIONS_SCHEMA = "nobu16.kr.steam-jp-msgui-exclusions.v1"
REVIEW_SCHEMA = "nobu16.kr.steam-jp-msgui-recovery-review.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-msgui-recovery-validation.v1"
SOURCE_SCRIPT_RE = re.compile(
    r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)
PRINTF_RE = re.compile(
    r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?"
    r"(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
LINE_BREAK_RE = re.compile(r"\r\n|\n|\r")
NON_SEMANTIC_CATEGORIES = frozenset(
    ("Cc", "Cf", "Cs", "Mn", "Me", "Zl", "Zp", "Zs", "Cn")
)
INVARIANT_KEYS = (
    "printf",
    "unknown_percent_count",
    "leading_whitespace",
    "trailing_whitespace",
    "esc",
    "controls",
    "line_breaks",
    "pua",
)


class BuildError(ValueError):
    """Raised when a frozen recovery contract differs."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256(text.encode("utf-16-le"))


def canonical_hash(value: Any) -> str:
    return sha256(
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    )


def pretty_bytes(value: Any) -> bytes:
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


def decode_json(blob: bytes, label: str) -> Any:
    try:
        return json.loads(blob.decode("utf-8-sig"), object_pairs_hook=strict_object)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise BuildError(f"invalid UTF-8 JSON in {label}: {exc}") from exc


def has_semantic_text(text: str) -> bool:
    consumed = {
        index
        for match in ESC_RE.finditer(text)
        for index in range(match.start(), match.end())
    }
    return any(
        index not in consumed
        and not char.isspace()
        and unicodedata.category(char) not in NON_SEMANTIC_CATEGORIES
        for index, char in enumerate(text)
    )


def message_invariants(text: str) -> dict[str, Any]:
    printf_matches = list(PRINTF_RE.finditer(text))
    consumed_percent = {
        index
        for match in printf_matches
        for index in range(match.start(), match.end())
        if text[index] == "%"
    }
    escape_matches = list(ESC_RE.finditer(text))
    consumed_escape = {
        index
        for match in escape_matches
        for index in range(match.start(), match.end())
    }
    return {
        "printf": [match.group(0) for match in printf_matches],
        "unknown_percent_count": sum(
            1
            for index, char in enumerate(text)
            if char == "%" and index not in consumed_percent
        ),
        "leading_whitespace": text[: len(text) - len(text.lstrip())],
        "trailing_whitespace": text[len(text.rstrip()) :],
        "esc": [match.group(0) for match in escape_matches],
        "controls": [
            f"U+{ord(char):04X}"
            for index, char in enumerate(text)
            if unicodedata.category(char) == "Cc"
            and char not in ("\r", "\n")
            and index not in consumed_escape
        ],
        "line_breaks": LINE_BREAK_RE.findall(text),
        "pua": [
            f"U+{ord(char):04X}"
            for char in text
            if 0xE000 <= ord(char) <= 0xF8FF
        ],
    }


def mismatch_keys(source: str, replacement: str) -> list[str]:
    before = message_invariants(source)
    after = message_invariants(replacement)
    return [key for key in INVARIANT_KEYS if before[key] != after[key]]


def load_table(path: Path, language: str) -> tuple[tuple[str, ...], dict[str, Any]]:
    spec = PRIVATE_SPECS[language]
    packed = path.read_bytes()
    if len(packed) != spec["packed_size"] or sha256(packed) != spec["packed_sha256"]:
        raise BuildError(f"{language} private packed context pin mismatch")
    _header, raw = decompress_wrapper(packed)
    if len(raw) != spec["raw_size"] or sha256(raw) != spec["raw_sha256"]:
        raise BuildError(f"{language} private raw context pin mismatch")
    table = parse_message_table(raw)
    if table.string_count != spec["string_count"]:
        raise BuildError(f"{language} private context string count mismatch")
    if rebuild_message_table(table, table.texts) != raw:
        raise BuildError(f"{language} private context round-trip mismatch")
    return table.texts, dict(spec)


def load_audit() -> tuple[dict[int, dict[str, Any]], bytes]:
    blob = INPUT_AUDIT.read_bytes()
    if sha256(blob) != AUDIT_SHA256:
        raise BuildError("v1 withheld audit pin mismatch")
    value = decode_json(blob, "v1 withheld audit")
    result = value.get("result") if isinstance(value, dict) else None
    if not isinstance(result, dict):
        raise BuildError("v1 withheld audit result is missing")
    if (
        result.get("unmapped_entry_count") != WITHHELD_COUNT
        or result.get("unmapped_coordinate_sha256") != WITHHELD_COORDINATE_SHA256
        or result.get("mapped_entry_count") != FOUNDATION_COUNT
        or result.get("mapped_coordinate_sha256") != FOUNDATION_COORDINATE_SHA256
    ):
        raise BuildError("v1 withheld audit count or partition pin mismatch")
    reasons = result.get("reason_dictionary")
    rows = result.get("unmapped_entries")
    if not isinstance(reasons, list) or not isinstance(rows, list) or len(rows) != WITHHELD_COUNT:
        raise BuildError("v1 withheld audit rows are malformed")
    output: dict[int, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, list) or len(row) != 4:
            raise BuildError("v1 withheld audit row is malformed")
        entry_id, reason_indexes, source_hash, prior_ko_hash = row
        if (
            isinstance(entry_id, bool)
            or not isinstance(entry_id, int)
            or entry_id < 0
            or entry_id in output
            or not isinstance(reason_indexes, list)
            or not isinstance(source_hash, str)
            or not isinstance(prior_ko_hash, str)
        ):
            raise BuildError("v1 withheld audit row values are malformed")
        try:
            decoded_reasons = [reasons[index] for index in reason_indexes]
        except (IndexError, TypeError) as exc:
            raise BuildError("v1 withheld audit reason index is invalid") from exc
        output[entry_id] = {
            "source_jp_utf16le_sha256": source_hash,
            "original_mismatch_reasons": decoded_reasons,
            "prior_ko_utf16le_sha256": prior_ko_hash,
        }
    if canonical_hash(sorted(output)) != WITHHELD_COORDINATE_SHA256:
        raise BuildError("v1 withheld audit ID hash mismatch")
    return output, blob


def load_foundation_ids() -> tuple[set[int], bytes]:
    blob = FOUNDATION_OVERLAY.read_bytes()
    if sha256(blob) != FOUNDATION_SHA256:
        raise BuildError("v1 foundation overlay pin mismatch")
    value = decode_json(blob, "v1 foundation overlay")
    entries = value.get("entries") if isinstance(value, dict) else None
    if not isinstance(entries, list) or value.get("entry_count") != FOUNDATION_COUNT:
        raise BuildError("v1 foundation overlay count mismatch")
    ids: list[int] = []
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {
            "id",
            "source_jp_utf16le_sha256",
            "ko",
        }:
            raise BuildError("v1 foundation overlay entry shape mismatch")
        ids.append(entry["id"])
    if ids != sorted(set(ids)) or canonical_hash(ids) != FOUNDATION_COORDINATE_SHA256:
        raise BuildError("v1 foundation overlay ID partition mismatch")
    return set(ids), blob


def load_decisions() -> tuple[dict[int, dict[str, Any]], bytes]:
    blob = DECISIONS.read_bytes()
    try:
        lines = blob.decode("utf-8-sig").splitlines()
    except UnicodeError as exc:
        raise BuildError("recovery decisions are not UTF-8") from exc
    output: dict[int, dict[str, Any]] = {}
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            raise BuildError(f"blank recovery decision line: {line_number}")
        row = decode_json(line.encode("utf-8"), f"decision line {line_number}")
        if not isinstance(row, dict):
            raise BuildError(f"decision line {line_number} must be an object")
        entry_id = row.get("id")
        status = row.get("status")
        if (
            isinstance(entry_id, bool)
            or not isinstance(entry_id, int)
            or entry_id < 0
            or entry_id in output
        ):
            raise BuildError(f"invalid or duplicate decision ID: {entry_id!r}")
        if status == "recovered":
            if set(row) != {"id", "status", "ko"}:
                raise BuildError(f"recovered decision fields differ at ID {entry_id}")
            korean = row["ko"]
            if (
                not isinstance(korean, str)
                or not has_semantic_text(korean)
                or SOURCE_SCRIPT_RE.search(korean)
                or "\0" in korean
                or "\ufffd" in korean
            ):
                raise BuildError(f"unsafe recovered Korean at ID {entry_id}")
        elif status == "excluded":
            if set(row) != {"id", "status", "reason"}:
                raise BuildError(f"excluded decision fields differ at ID {entry_id}")
            if row["reason"] != "jp_slot_nonsemantic_whitespace_only":
                raise BuildError(f"unsupported exclusion reason at ID {entry_id}")
        else:
            raise BuildError(f"unknown decision status at ID {entry_id}")
        output[entry_id] = row
    if len(output) != WITHHELD_COUNT:
        raise BuildError("recovery decision count mismatch")
    return output, blob


def source_free(blob: bytes, label: str) -> None:
    text = blob.decode("utf-8")
    if SOURCE_SCRIPT_RE.search(text):
        raise BuildError(f"publisher source script leaked into {label}")
    for forbidden in ('"jp":', '"sc":', '"tc":', '"en":', '"source_text":'):
        if forbidden in text:
            raise BuildError(f"publisher source field leaked into {label}")


def artifact(path: Path, blob: bytes) -> dict[str, Any]:
    return {
        "path": path.relative_to(REPO_ROOT).as_posix(),
        "size": len(blob),
        "sha256": sha256(blob),
    }


def build_values(
    jp_stock: Path = DEFAULT_JP_STOCK,
    context_root: Path = DEFAULT_CONTEXT_ROOT,
) -> dict[str, tuple[Any, bytes]]:
    audit, audit_blob = load_audit()
    foundation_ids, foundation_blob = load_foundation_ids()
    decisions, decisions_blob = load_decisions()
    if set(audit) != set(decisions):
        raise BuildError("recovery decisions do not cover exactly the withheld partition")
    if foundation_ids & set(decisions):
        raise BuildError("recovery supplement overlaps the v1 foundation overlay")

    context_paths = {
        "JP": jp_stock,
        "SC": context_root / "SC" / "msgui.bin",
        "EN": context_root / "EN" / "msgui.bin",
        "TC": context_root / "TC" / "msgui.bin",
    }
    tables: dict[str, tuple[str, ...]] = {}
    context_specs: dict[str, dict[str, Any]] = {}
    for language, path in context_paths.items():
        tables[language], context_specs[language] = load_table(path, language)

    recovered: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    review_entries: list[dict[str, Any]] = []
    mismatch_reason_counts: Counter[str] = Counter()
    invariant_profile_counts: Counter[str] = Counter()
    for entry_id in sorted(decisions):
        source = tables["JP"][entry_id]
        audit_row = audit[entry_id]
        source_digest = text_hash(source)
        if source_digest != audit_row["source_jp_utf16le_sha256"]:
            raise BuildError(f"current JP source hash differs from audit at ID {entry_id}")
        mismatch_reason_counts.update(audit_row["original_mismatch_reasons"])
        decision = decisions[entry_id]
        if decision["status"] == "excluded":
            if has_semantic_text(source):
                raise BuildError(f"excluded JP slot is not nonsemantic at ID {entry_id}")
            exclusion = {
                "id": entry_id,
                "source_jp_utf16le_sha256": source_digest,
                "reason": decision["reason"],
                "original_mismatch_reasons": audit_row["original_mismatch_reasons"],
            }
            excluded.append(exclusion)
            review_entries.append(
                {
                    "id": entry_id,
                    "source_jp_utf16le_sha256": source_digest,
                    "status": "excluded",
                    "reason": decision["reason"],
                }
            )
            continue

        korean = decision["ko"]
        failures = mismatch_keys(source, korean)
        if failures:
            raise BuildError(f"JP invariant mismatch at ID {entry_id}: {failures}")
        for key, value in message_invariants(source).items():
            if value not in ([], "", 0):
                invariant_profile_counts[key] += 1
        recovered.append(
            {
                "id": entry_id,
                "source_jp_utf16le_sha256": source_digest,
                "ko": korean,
            }
        )
        available_context = [
            language
            for language in ("JP", "EN", "SC", "TC")
            if has_semantic_text(tables[language][entry_id])
        ]
        review_entries.append(
            {
                "id": entry_id,
                "source_jp_utf16le_sha256": source_digest,
                "status": "recovered",
                "invariant_status": "PASS",
                "semantic_context_review_status": "PASS",
                "available_context_languages": available_context,
            }
        )

    if len(recovered) != RECOVERED_COUNT or len(excluded) != EXCLUDED_COUNT:
        raise BuildError("recovered/excluded decision counts differ")
    recovered_ids = [row["id"] for row in recovered]
    excluded_ids = [row["id"] for row in excluded]
    no_op_count = sum(tables["JP"][row["id"]] == row["ko"] for row in recovered)
    effective_change_count = len(recovered) - no_op_count

    overlay = {
        "schema": OVERLAY_SCHEMA,
        "supplement_id": "steam_jp_msgui_wave07_recovery_343.v1",
        "resource": RESOURCE,
        "base_language": "JP",
        "runtime_version": RUNTIME_VERSION,
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_jp": context_specs["JP"],
        "foundation": {
            "sha256": sha256(foundation_blob),
            "entry_count": FOUNDATION_COUNT,
            "coordinate_sha256": FOUNDATION_COORDINATE_SHA256,
        },
        "withheld_input": {
            "audit_sha256": sha256(audit_blob),
            "entry_count": WITHHELD_COUNT,
            "coordinate_sha256": WITHHELD_COORDINATE_SHA256,
        },
        "semantic_review": {
            "private_context_languages": ["JP", "EN", "SC", "TC"],
            "publisher_source_text_embedded": False,
            "slot_context_reviewed": True,
            "runtime_screen_reviewed": False,
        },
        "entry_count": len(recovered),
        "effective_change_count": effective_change_count,
        "no_op_count": no_op_count,
        "coordinate_sha256": canonical_hash(recovered_ids),
        "excluded_entry_count": len(excluded),
        "entries": recovered,
    }
    overlay_blob = pretty_bytes(overlay)

    exclusions = {
        "schema": EXCLUSIONS_SCHEMA,
        "resource": RESOURCE,
        "base_language": "JP",
        "source_free": True,
        "withheld_entry_count": WITHHELD_COUNT,
        "recovered_entry_count": len(recovered),
        "effective_change_count": effective_change_count,
        "no_op_count": no_op_count,
        "excluded_entry_count": len(excluded),
        "excluded_coordinate_sha256": canonical_hash(excluded_ids),
        "entries": excluded,
    }
    exclusions_blob = pretty_bytes(exclusions)

    review = {
        "schema": REVIEW_SCHEMA,
        "resource": RESOURCE,
        "base_language": "JP",
        "source_free": True,
        "private_context_pins": context_specs,
        "coordinate_count": WITHHELD_COUNT,
        "coordinate_sha256": WITHHELD_COORDINATE_SHA256,
        "status_counts": {"recovered": len(recovered), "excluded": len(excluded)},
        "invariant_status_counts": {"PASS": len(recovered)},
        "semantic_context_review_status_counts": {"PASS": len(recovered)},
        "runtime_screen_reviewed": False,
        "entries": review_entries,
    }
    review_blob = pretty_bytes(review)

    validation = {
        "schema": VALIDATION_SCHEMA,
        "resource": RESOURCE,
        "base_language": "JP",
        "runtime_version": RUNTIME_VERSION,
        "status": "PASS",
        "withheld_entry_count": WITHHELD_COUNT,
        "recovered_entry_count": len(recovered),
        "effective_change_count": effective_change_count,
        "no_op_count": no_op_count,
        "excluded_entry_count": len(excluded),
        "recovered_coordinate_sha256": canonical_hash(recovered_ids),
        "excluded_coordinate_sha256": canonical_hash(excluded_ids),
        "original_mismatch_reason_counts": dict(sorted(mismatch_reason_counts.items())),
        "recovered_invariant_profile_nonempty_counts": dict(
            sorted(invariant_profile_counts.items())
        ),
        "checks": {
            "v1_audit_pin_exact": sha256(audit_blob) == AUDIT_SHA256,
            "v1_foundation_pin_exact": sha256(foundation_blob) == FOUNDATION_SHA256,
            "private_context_pins_exact": True,
            "withheld_partition_exact": set(audit) == set(decisions),
            "foundation_disjoint": not bool(foundation_ids & set(decisions)),
            "jp_source_hashes_exact": True,
            "all_recovered_invariants_exact": True,
            "all_recovered_slots_semantically_reviewed": True,
            "all_exclusions_explicit": True,
            "public_entry_shape_exact": all(
                set(row) == {"id", "source_jp_utf16le_sha256", "ko"}
                for row in recovered
            ),
            "publisher_source_text_absent": True,
        },
        "artifacts": [
            artifact(DECISIONS, decisions_blob),
            artifact(PUBLIC_OVERLAY, overlay_blob),
            artifact(EXCLUSIONS, exclusions_blob),
            artifact(REVIEW, review_blob),
        ],
    }
    validation_blob = pretty_bytes(validation)

    values = {
        "overlay": (overlay, overlay_blob),
        "exclusions": (exclusions, exclusions_blob),
        "review": (review, review_blob),
        "validation": (validation, validation_blob),
    }
    source_free(decisions_blob, "recovery decisions")
    for name, (_value, blob) in values.items():
        source_free(blob, name)
    return values


def write_outputs(values: Mapping[str, tuple[Any, bytes]]) -> None:
    targets = {
        "overlay": PUBLIC_OVERLAY,
        "exclusions": EXCLUSIONS,
        "review": REVIEW,
        "validation": VALIDATION,
    }
    for name, path in targets.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(values[name][1])


def verify_outputs(values: Mapping[str, tuple[Any, bytes]]) -> None:
    targets = {
        "overlay": PUBLIC_OVERLAY,
        "exclusions": EXCLUSIONS,
        "review": REVIEW,
        "validation": VALIDATION,
    }
    for name, path in targets.items():
        if not path.is_file() or path.read_bytes() != values[name][1]:
            raise BuildError(f"tracked {name} differs from deterministic build")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "verify"))
    parser.add_argument("--jp-stock", type=Path, default=DEFAULT_JP_STOCK)
    parser.add_argument("--context-root", type=Path, default=DEFAULT_CONTEXT_ROOT)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        values = build_values(args.jp_stock, args.context_root)
        if args.action == "build":
            write_outputs(values)
        else:
            verify_outputs(values)
    except (BuildError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "action": args.action,
                "status": "PASS",
                "recovered_entry_count": RECOVERED_COUNT,
                "excluded_entry_count": EXCLUDED_COUNT,
                "overlay": PUBLIC_OVERLAY.relative_to(REPO_ROOT).as_posix(),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
