#!/usr/bin/env python3
"""Build source-free MSG/SC/ev_strdata officer-name batch1 artifacts.

The installed distribution has SC, JP, and TC copies of ``ev_strdata.bin``
but no EN copy.  TC is therefore the third alignment reference for this
workstream.  Commercial strings are read only in memory and are represented
in distributable artifacts by UTF-16LE SHA-256 values.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))

import build_common_message_overlay as common  # noqa: E402
from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


BATCH_ID = "ev-strdata-officer-names-0000-0149-v0.1"
RESOURCE = "MSG/SC/ev_strdata.bin"
SUPPORTED_RESOURCES = frozenset({RESOURCE})
OVERLAY_NAME = "ev_strdata_ko_officer_names_0000_0149.v0.1.json"
EVIDENCE_NAME = "alignment_evidence.v0.1.json"
REVIEW_NAME = "review_index.v0.1.json"
VALIDATION_NAME = "validation.v0.1.json"
SEED_RELATIVE = Path("data/public/msgev_ko_officer_names_0000_2399.v0.1.json")
SEED_SHA256 = "2625B8261527217EB3592D6B6BD03BE38A666998D32C944D29917FD4598B63BC"
SCOPE_START = 0
SCOPE_END = 149
NEXT_START_ID = 150
STRING_COUNT = 17868
DISPLAY_TARGET_COUNT_SC = 11687
LANGUAGES = ("SC", "JP", "TC")
BRACKET_TOKEN_RE = re.compile(r"\[[A-Za-z0-9_]+\]")
FORBIDDEN_SOURCE_SCRIPT_RE = re.compile(
    r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\u3040-\u30FF]"
)

SOURCE_PINS = {
    "SC": {
        "size": 461651,
        "packed_sha256": "77E87C6FEC67859543FCB4134660A7274A2374F6881B956421B561E61BD7B685",
        "raw_size": 662228,
        "raw_sha256": "482B25ACFBF219E85EF9F9A073745414B3FC97705BABB4FAF4AAC3BB68248DAD",
        "display_nonempty_count": 11687,
    },
    "JP": {
        "size": 496819,
        "packed_sha256": "EADCD167EF9684C7F077694A1A7F68966E34FD2E2EEF9DEFB7817031C3D773EB",
        "raw_size": 789260,
        "raw_sha256": "5FBD960A4870FA4850BD725C58E67BE3A7F191960737C36E4505151FE4B7C528",
        "display_nonempty_count": 13283,
    },
    "TC": {
        "size": 460929,
        "packed_sha256": "9E9346B942CAFA99432D675F6BA74DD04D48F56095F35F46392697011D9CFEF3",
        "raw_size": 650756,
        "raw_sha256": "8918886EC8BB8B58317189F7ABAF48EBC761633CC263F0641ED5213050D1B352",
        "display_nonempty_count": 11687,
    },
}


class EvStrDataError(ValueError):
    """Raised when the pinned source, seed, or public contract differs."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def encode_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def strict_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    return common.strict_object(pairs)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8-sig"), object_pairs_hook=strict_object
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvStrDataError(f"invalid JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise EvStrDataError(f"JSON root must be an object: {path}")
    return value


def file_map(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def generated_file_map(root: Path) -> dict[str, bytes]:
    relative_paths = (
        Path("public") / OVERLAY_NAME,
        Path("evidence") / EVIDENCE_NAME,
        Path("review") / REVIEW_NAME,
        Path(VALIDATION_NAME),
    )
    return {path.as_posix(): (root / path).read_bytes() for path in relative_paths}


def source_free_counts(blob: bytes) -> dict[str, int]:
    text = blob.decode("utf-8")
    return {
        "han_or_kana_count": len(FORBIDDEN_SOURCE_SCRIPT_RE.findall(text)),
        "embedded_nul_count": text.count("\x00"),
    }


def hash_json(value: Any) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def text_structure(text: str) -> dict[str, Any]:
    invariants = common.message_invariants(text)
    bracket_tokens = BRACKET_TOKEN_RE.findall(text)
    return {
        "printf_token_count": len(invariants["printf"]),
        "printf_tokens_sha256": hash_json(invariants["printf"]),
        "unknown_percent_count": invariants["unknown_percent_count"],
        "leading_whitespace_utf16le_sha256": common.text_hash(
            invariants["leading_whitespace"]
        ),
        "trailing_whitespace_utf16le_sha256": common.text_hash(
            invariants["trailing_whitespace"]
        ),
        "escape_token_count": len(invariants["esc"]),
        "escape_tokens_sha256": hash_json(invariants["esc"]),
        "control_codepoints": invariants["controls"],
        "line_breaks_sha256": hash_json(invariants["line_breaks"]),
        "pua_codepoints": invariants["pua"],
        "bracket_placeholder_count": len(bracket_tokens),
        "bracket_placeholders_sha256": hash_json(bracket_tokens),
    }


def replacement_failures(source: str, replacement: str) -> list[str]:
    failures = common.invariant_mismatches(source, replacement)
    source_brackets = BRACKET_TOKEN_RE.findall(source)
    target_brackets = BRACKET_TOKEN_RE.findall(replacement)
    if source_brackets != target_brackets:
        failures.append(
            f"bracket_placeholders: source={source_brackets!r}, ko={target_brackets!r}"
        )
    return failures


def load_sources(game_root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    loaded: dict[str, dict[str, Any]] = {}
    before: dict[str, str] = {}
    for language in LANGUAGES:
        relative = Path("MSG") / language / "ev_strdata.bin"
        path = game_root / relative
        packed = path.read_bytes()
        before[relative.as_posix()] = sha256(packed)
        pin = SOURCE_PINS[language]
        if len(packed) != pin["size"] or sha256(packed) != pin["packed_sha256"]:
            raise EvStrDataError(f"{relative.as_posix()}: packed source pin mismatch")
        _, raw = decompress_wrapper(packed)
        if len(raw) != pin["raw_size"] or sha256(raw) != pin["raw_sha256"]:
            raise EvStrDataError(f"{relative.as_posix()}: raw source pin mismatch")
        table = parse_message_table(raw)
        if table.string_count != STRING_COUNT:
            raise EvStrDataError(
                f"{relative.as_posix()}: strings={table.string_count}, expected={STRING_COUNT}"
            )
        if rebuild_message_table(table, table.texts) != raw:
            raise EvStrDataError(f"{relative.as_posix()}: raw parse/rebuild is not byte-exact")
        display_nonempty = sum(1 for text in table.texts if text.strip())
        if display_nonempty != pin["display_nonempty_count"]:
            raise EvStrDataError(
                f"{relative.as_posix()}: display count={display_nonempty}, "
                f"expected={pin['display_nonempty_count']}"
            )
        loaded[language] = {
            "relative": relative.as_posix(),
            "packed": packed,
            "raw": raw,
            "table": table,
            "display_nonempty_count": display_nonempty,
        }
    return loaded, before


def load_translations(sc_table: Any) -> dict[int, str]:
    seed_path = REPO_ROOT / SEED_RELATIVE
    seed_blob = seed_path.read_bytes()
    if sha256(seed_blob) != SEED_SHA256:
        raise EvStrDataError("pinned officer-name seed overlay changed")
    seed = load_json(seed_path)
    entries = seed.get("entries")
    if not isinstance(entries, list):
        raise EvStrDataError("seed entries must be an array")
    by_id = {
        int(entry["id"]): entry
        for entry in entries
        if isinstance(entry, dict) and "id" in entry
    }
    translations: dict[int, str] = {}
    for entry_id in range(SCOPE_START, SCOPE_END + 1):
        entry = by_id.get(entry_id)
        if entry is None:
            raise EvStrDataError(f"seed has no officer-name entry {entry_id}")
        source = sc_table.texts[entry_id]
        if not source.strip():
            raise EvStrDataError(f"selected SC id {entry_id} is not display text")
        expected_hash = entry.get("source_sc_utf16le_sha256")
        if expected_hash != common.text_hash(source):
            raise EvStrDataError(
                f"id {entry_id}: seed source hash does not match ev_strdata SC"
            )
        replacement = entry.get("ko")
        if not isinstance(replacement, str) or not replacement.strip():
            raise EvStrDataError(f"id {entry_id}: seed Korean name is empty")
        failures = replacement_failures(source, replacement)
        if failures:
            raise EvStrDataError(f"id {entry_id}: invariant mismatch: {failures}")
        translations[entry_id] = replacement
    return translations


def write_json(path: Path, value: Any) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {
        "path": path.relative_to(path.parents[1] if path.parent.name in {"public", "evidence", "review"} else path.parent).as_posix(),
        "size": len(blob),
        "sha256": sha256(blob),
    }


def common_binary_build(game_root: Path, overlay_path: Path) -> dict[str, Any]:
    original_allowlist = common.ALLOWED_RESOURCES
    common.ALLOWED_RESOURCES = original_allowlist | SUPPORTED_RESOURCES
    try:
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr-bin-") as temporary:
            output_root = Path(temporary)
            result = common.build_overlay(game_root, overlay_path, output_root)
            outputs = file_map(output_root)
            return {
                "files": {
                    relative: {"size": len(blob), "sha256": sha256(blob)}
                    for relative, blob in sorted(outputs.items())
                },
                "target_sha256": result["target_sha256"],
                "manifest_sha256": result["manifest_sha256"],
                "recipe_sha256": result["recipe_sha256"],
                "overlay_entries": result["overlay_entries"],
                "operations": result["operations"],
            }
    finally:
        common.ALLOWED_RESOURCES = original_allowlist


def build_once(game_root: Path, out_root: Path) -> dict[str, Any]:
    loaded, before = load_sources(game_root)
    sc_table = loaded["SC"]["table"]
    translations = load_translations(sc_table)
    ids = list(translations)
    if ids != list(range(SCOPE_START, SCOPE_END + 1)):
        raise EvStrDataError("selected ids are not the exact contiguous batch range")

    overlay_entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    failures: list[str] = []
    for entry_id in ids:
        source_sc = sc_table.texts[entry_id]
        replacement = translations[entry_id]
        failures.extend(
            f"id {entry_id}: {failure}"
            for failure in replacement_failures(source_sc, replacement)
        )
        overlay_entries.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": common.text_hash(source_sc),
                "ko": replacement,
            }
        )
        evidence_entries.append(
            {
                "id": entry_id,
                "references": {
                    language: {
                        "utf16le_sha256": common.text_hash(
                            loaded[language]["table"].texts[entry_id]
                        ),
                        "structure": text_structure(
                            loaded[language]["table"].texts[entry_id]
                        ),
                    }
                    for language in LANGUAGES
                },
                "translation_reuse_exact_sc_hash_match": True,
            }
        )
    if failures:
        raise EvStrDataError(f"replacement invariant failures: {failures[:5]}")

    sc_packed = loaded["SC"]["packed"]
    sc_raw = loaded["SC"]["raw"]
    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "entry_count": len(ids),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "size": len(sc_packed),
            "packed_sha256": sha256(sc_packed),
            "raw_size": len(sc_raw),
            "raw_sha256": sha256(sc_raw),
            "string_count": STRING_COUNT,
        },
        "defaults": {"status": "translated"},
        "entries": overlay_entries,
    }
    original_allowlist = common.ALLOWED_RESOURCES
    common.ALLOWED_RESOURCES = original_allowlist | SUPPORTED_RESOURCES
    try:
        common.validate_overlay_shape(overlay)
    finally:
        common.ALLOWED_RESOURCES = original_allowlist

    source_files = {
        language: {
            **SOURCE_PINS[language],
            "relative_path": loaded[language]["relative"],
            "string_count": STRING_COUNT,
        }
        for language in LANGUAGES
    }
    boundary_ids = (SCOPE_START, SCOPE_END, NEXT_START_ID)
    evidence = {
        "schema": "nobu16.kr.ev-strdata-alignment-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": "ev_strdata",
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "next_start_id": NEXT_START_ID,
            "selected_display_entry_count": len(ids),
            "functional_section": "officer_full_name_catalog_initial_batch",
            "boundary_reason": "the initial officer-name section exceeds the 150-entry batch cap",
        },
        "alignment_basis": [
            "same_resource_role",
            "same_17868_string_count",
            "same_numeric_string_ids",
            "selected_ids_nonempty_in_sc_jp_tc",
            "existing_korean_officer_name_reused_only_on_exact_sc_hash_match",
        ],
        "reference_language_note": (
            "The installed MSG tree has no EN ev_strdata.bin; TC is the third "
            "reference alongside SC and JP."
        ),
        "source_files": source_files,
        "translation_seed": {
            "relative_path": SEED_RELATIVE.as_posix(),
            "sha256": SEED_SHA256,
            "commercial_source_text_included": False,
        },
        "boundary_anchors": [
            {
                "id": entry_id,
                "reference_hashes": {
                    language: common.text_hash(
                        loaded[language]["table"].texts[entry_id]
                    )
                    for language in LANGUAGES
                },
            }
            for entry_id in boundary_ids
        ],
        "entry_count": len(ids),
        "entries": evidence_entries,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.ev-strdata-review-index.v1",
        "batch_id": BATCH_ID,
        "quality_state": "project_officer_name_draft_pending_runtime_review",
        "entry_count": len(ids),
        "entries": [
            {
                "id": entry_id,
                "status": "translated",
                "translation_origin": "existing_officer_name_overlay_exact_sc_hash_match",
                "human_review_required": True,
                "runtime_reviewed": False,
                "uncertainty_flags": [],
            }
            for entry_id in ids
        ],
        "contains_commercial_source_text": False,
    }

    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    for path, value in (
        (overlay_path, overlay),
        (evidence_path, evidence),
        (review_path, review),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(encode_json(value))

    source_free_scan = {
        path.relative_to(out_root).as_posix(): source_free_counts(path.read_bytes())
        for path in (overlay_path, evidence_path, review_path)
    }
    if any(
        counts != {"han_or_kana_count": 0, "embedded_nul_count": 0}
        for counts in source_free_scan.values()
    ):
        raise EvStrDataError("public artifact contains source script text or an embedded NUL")

    binary = common_binary_build(game_root, overlay_path)
    after = {
        relative: sha256((game_root / Path(relative)).read_bytes())
        for relative in before
    }
    if before != after:
        raise EvStrDataError("installed game resource changed during the build")

    public_artifacts = {
        path.relative_to(out_root).as_posix(): {
            "size": path.stat().st_size,
            "sha256": sha256(path.read_bytes()),
        }
        for path in (overlay_path, evidence_path, review_path)
    }
    validation = {
        "schema": "nobu16.kr.ev-strdata-generation-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "next_start_id": NEXT_START_ID,
            "selected_display_entry_count": len(ids),
            "selected_ids_sha256": hash_json(ids),
            "total_string_slots": STRING_COUNT,
            "sc_display_translation_target_count": DISPLAY_TARGET_COUNT_SC,
        },
        "source_alignment": {
            "languages": list(LANGUAGES),
            "english_reference_available": False,
            "traditional_chinese_used_as_third_reference": True,
            "string_count_each": STRING_COUNT,
            "selected_reference_hash_count": len(ids) * len(LANGUAGES),
            "selected_ids_nonempty_in_all_references": len(ids),
            "source_files": source_files,
        },
        "translation_reuse": {
            "seed_relative_path": SEED_RELATIVE.as_posix(),
            "seed_sha256": SEED_SHA256,
            "exact_sc_hash_matches": len(ids),
            "mismatches": 0,
        },
        "replacement_invariants": {
            "checked": len(ids),
            "failures": 0,
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "edge_whitespace",
                "esc_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
                "bracket_placeholders_in_order",
            ],
        },
        "raw_format": {
            "lz4_wrapper_decompression": "OK",
            "message_table_parser": "tools/nobu16_msg_table.py",
            "raw_parse_rebuild_byte_exact_languages": list(LANGUAGES),
            "binary_builder_state": "enabled_offline_output_only",
        },
        "offline_binary_build": {
            **binary,
            "installed_target_written": False,
        },
        "source_free_scan": source_free_scan,
        "artifacts": public_artifacts,
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": sha256(SCRIPT_PATH.read_bytes()),
        },
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
        },
        "safety": {
            "installed_game_files_modified": False,
            "font_files_modified": False,
            "installer_modified": False,
            "root_readme_or_progress_modified": False,
            "official_source_text_exposed_in_public_artifacts": False,
            "process_memory_access": False,
            "executable_modified": False,
            "registry_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.write_bytes(encode_json(validation))
    return {
        "entry_count": len(ids),
        "next_start_id": NEXT_START_ID,
        "files": generated_file_map(out_root),
    }


def build_reproducibly(game_root: Path, out_root: Path) -> dict[str, Any]:
    game_root = game_root.resolve()
    out_root = out_root.resolve()
    source_paths = [game_root / "MSG" / language / "ev_strdata.bin" for language in LANGUAGES]
    before = {path.as_posix(): sha256(path.read_bytes()) for path in source_paths}
    with tempfile.TemporaryDirectory(prefix="nobu16-evstr-a-") as first_tmp:
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr-b-") as second_tmp:
            first = build_once(game_root, Path(first_tmp))
            second = build_once(game_root, Path(second_tmp))
            if first["files"] != second["files"]:
                raise EvStrDataError("isolated A/B public artifacts are not byte-identical")
    final = build_once(game_root, out_root)
    if final["files"] != first["files"]:
        raise EvStrDataError("final public artifacts differ from isolated A/B output")
    after = {path.as_posix(): sha256(path.read_bytes()) for path in source_paths}
    if before != after:
        raise EvStrDataError("installed game resource changed across reproducible build")
    return final


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--game-root",
        type=Path,
        default=REPO_ROOT.parent,
        help="NOBU16 install root containing MSG/SC, MSG/JP, and MSG/TC",
    )
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_reproducibly(args.game_root, args.out_root)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={args.out_root.resolve()}")
    print(f"entries={result['entry_count']}")
    print(f"next_start_id={result['next_start_id']}")
    for relative, blob in sorted(result["files"].items()):
        print(f"{relative}_sha256={sha256(blob)}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
