#!/usr/bin/env python3
"""Read-only audit of the Steam JP PK msgstf_ce credits resource.

The module inspects the four language variants in a Steam 1.1.7 installation,
their message-table shape, and limited static route evidence.  It emits only
source-free hashes, counts, IDs, and conclusions.  It does not translate,
rebuild, copy, or write any game resource; no candidate or release artifact is
created by this workstream.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
TOOLS = REPO / "tools"
sys.path.insert(0, str(TOOLS))

from build_common_message_overlay import invariant_mismatches  # noqa: E402
from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


DEFAULT_STEAM_ROOT = Path(r"F:/SteamLibrary/steamapps/common/NOBU16")
LANGUAGES = ("JP", "EN", "SC", "TC")
RESOURCE_TEMPLATE = "MSG_PK/{language}/msgstf_ce.bin"
V5_VERIFICATION_PATH = REPO / "workstreams" / "steam_jp_117_candidate_v5" / "verification.v5.json"
AUDIT_PATH = HERE / "audit.v1.json"

SCHEMA = "nobu16.kr.steam-jp-msgstf-ce-credits-audit.v1"
EXPECTED_VERSION = "1.1.7"
EXPECTED_STRING_COUNT = 20
EXPECTED_NONEMPTY_IDS = tuple(range(8))
EXPECTED_EMPTY_IDS = tuple(range(8, 20))

# The punctuation U+30FB is not treated as a lexical source-script character.
CJK_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")
KANA_LETTER_RE = re.compile(
    r"[\u3041-\u3096\u309D-\u309F\u30A1-\u30FA\u30FD-\u30FF\u31F0-\u31FF]"
)
HANGUL_RE = re.compile(r"[\uAC00-\uD7A3]")
LATIN_RE = re.compile(r"[A-Za-z]")


class CreditsAuditError(ValueError):
    """Raised when a pinned audit input or source-free model diverges."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def strict_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CreditsAuditError(f"cannot read JSON: {path}") from exc
    if not isinstance(value, dict):
        raise CreditsAuditError(f"JSON root is not an object: {path}")
    return value


def path_spec(path: Path) -> dict[str, Any]:
    blob = path.read_bytes()
    return {"size": len(blob), "sha256": sha256(blob)}


def vector_sha256(values: Iterable[int]) -> str:
    return sha256("".join(f"{value}\n" for value in values).encode("ascii"))


def text_hash(text: str) -> str:
    return sha256(text.encode("utf-16-le"))


def source_script_count(text: str) -> int:
    return len(CJK_RE.findall(text)) + len(KANA_LETTER_RE.findall(text))


def has_lexical_source_script(text: str) -> bool:
    return source_script_count(text) > 0


def assert_source_free(value: Any, label: str) -> None:
    serialized = canonical_json_bytes(value).decode("utf-8")
    if has_lexical_source_script(serialized):
        raise CreditsAuditError(f"source script leaked into public artifact: {label}")


def resource_path(steam_root: Path, language: str) -> Path:
    if language not in LANGUAGES:
        raise CreditsAuditError(f"unknown language: {language}")
    return steam_root / Path(RESOURCE_TEMPLATE.format(language=language))


def mismatch_summary(source: str, target: str) -> list[str]:
    """Return only invariant category names, never source/target content."""
    return sorted({item.split(":", 1)[0] for item in invariant_mismatches(source, target)})


def load_variant(steam_root: Path, language: str) -> dict[str, Any]:
    path = resource_path(steam_root, language)
    packed = path.read_bytes()
    wrapper, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    if rebuild_message_table(table, table.texts) != raw:
        raise CreditsAuditError(f"message table parse/rebuild differs: {language}")
    if table.string_count != EXPECTED_STRING_COUNT:
        raise CreditsAuditError(f"unexpected string count for {language}: {table.string_count}")

    nonempty_ids = [entry_id for entry_id, text in enumerate(table.texts) if text]
    empty_ids = [entry_id for entry_id, text in enumerate(table.texts) if not text]
    if tuple(nonempty_ids) != EXPECTED_NONEMPTY_IDS or tuple(empty_ids) != EXPECTED_EMPTY_IDS:
        raise CreditsAuditError(f"credits page slot domain differs: {language}")

    rows: list[dict[str, Any]] = []
    for entry_id, text in enumerate(table.texts):
        rows.append(
            {
                "id": entry_id,
                "character_count": len(text),
                "line_break_count": text.count("\n"),
                "utf16le_sha256": text_hash(text),
                "has_hangul": HANGUL_RE.search(text) is not None,
                "has_lexical_source_script": has_lexical_source_script(text),
                "has_latin": LATIN_RE.search(text) is not None,
            }
        )
    if any(row["line_break_count"] == 0 for row in rows[:8]):
        raise CreditsAuditError(f"nonempty credits page lost multiline layout: {language}")

    layout = {
        "block_offset": table.block_offset,
        "table_offset": table.table_offset,
        "table_size": table.table_size,
        "string_start": table.string_start,
        "logical_size": table.logical_size,
        "logical_end": table.logical_end,
        "offset_vector_sha256": sha256(
            "".join(f"{offset}\n" for offset in table.string_offsets).encode("ascii")
        ),
    }
    return {
        "language": language,
        "resource": RESOURCE_TEMPLATE.format(language=language),
        "packed": {"size": len(packed), "sha256": sha256(packed)},
        "raw": {"size": len(raw), "sha256": sha256(raw)},
        "container": "raw-lz4-single-message-table",
        "wrapper_prefix_sha256": sha256(wrapper.prefix),
        "string_count": table.string_count,
        "nonempty_ids": nonempty_ids,
        "empty_ids": empty_ids,
        "nonempty_ids_sha256": vector_sha256(nonempty_ids),
        "empty_ids_sha256": vector_sha256(empty_ids),
        "nonempty_multiline_page_count": sum(row["line_break_count"] > 0 for row in rows[:8]),
        "script_summary": {
            "nonempty_rows_with_hangul": sum(row["has_hangul"] for row in rows[:8]),
            "nonempty_rows_with_lexical_source_script": sum(
                row["has_lexical_source_script"] for row in rows[:8]
            ),
            "nonempty_rows_with_latin": sum(row["has_latin"] for row in rows[:8]),
        },
        "layout": layout,
        "entry_metadata": rows,
        "_texts": table.texts,
    }


def public_variant(variant: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in variant.items() if key != "_texts"}


def comparison(jp: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    categories_by_id: dict[str, list[str]] = {}
    same_hash_ids: list[int] = []
    for entry_id, (source, translated) in enumerate(zip(jp["_texts"], target["_texts"], strict=True)):
        categories = mismatch_summary(source, translated)
        if categories:
            categories_by_id[str(entry_id)] = categories
        if text_hash(source) == text_hash(translated):
            same_hash_ids.append(entry_id)
    category_counts = Counter(
        category for categories in categories_by_id.values() for category in categories
    )
    return {
        "target_language": target["language"],
        "same_slot_count": len(jp["_texts"]),
        "same_nonempty_id_vector": jp["nonempty_ids"] == target["nonempty_ids"],
        "same_empty_id_vector": jp["empty_ids"] == target["empty_ids"],
        "same_text_hash_entry_count": len(same_hash_ids),
        "same_text_hash_ids": same_hash_ids,
        "format_mismatch_entry_ids": [int(key) for key in categories_by_id],
        "format_mismatch_categories_by_id": categories_by_id,
        "format_mismatch_category_counts": dict(sorted(category_counts.items())),
    }


def token_present(blob: bytes, token: str) -> dict[str, bool]:
    return {
        "ascii": token.encode("ascii") in blob,
        "utf16le": token.encode("utf-16-le") in blob,
    }


def static_route_evidence(steam_root: Path) -> dict[str, Any]:
    executable = steam_root / "NOBU16PK.exe"
    ending_flow = steam_root / "FLOW_PK" / "ENDING_00.bsf"
    exe_blob = executable.read_bytes()
    flow_blob = ending_flow.read_bytes()
    language_tokens = {
        language: token_present(exe_blob, language) for language in LANGUAGES
    }
    return {
        "executable": {"path": "NOBU16PK.exe", **path_spec(executable)},
        "ending_flow": {"path": "FLOW_PK/ENDING_00.bsf", **path_spec(ending_flow)},
        "generic_message_root_token": token_present(exe_blob, "MSG_PK"),
        "language_tokens_in_executable": language_tokens,
        "exact_msgstf_ce_token_in_executable": token_present(exe_blob, "msgstf_ce.bin"),
        "exact_msgstf_ce_token_in_ending_flow": token_present(flow_blob, "msgstf_ce.bin"),
        "runtime_file_open_trace_completed": False,
        "runtime_file_open_proven": False,
        "evidence_grade": "static_language_route_and_ending_flow_context_only",
        "limitation": "generic_loader_can_construct_resource_names_without_literal_filename",
    }


def candidate_boundary() -> dict[str, Any]:
    verification = strict_json(V5_VERIFICATION_PATH)
    paths = verification.get("candidate_paths")
    if not isinstance(paths, list):
        raise CreditsAuditError("v5 candidate paths are missing")
    resource = RESOURCE_TEMPLATE.format(language="JP")
    return {
        "v5_verification_path": "workstreams/steam_jp_117_candidate_v5/verification.v5.json",
        "v5_candidate_file_count": verification.get("candidate_file_count"),
        "resource_in_v5_candidate_paths": resource in paths,
        "v5_target_paths_sha256": sha256(canonical_json_bytes(paths)),
        "current_candidate_boundary": "omitted",
    }


def model(steam_root: Path = DEFAULT_STEAM_ROOT) -> dict[str, Any]:
    update_ver = (steam_root / "UpdateVer.txt").read_text(encoding="ascii").strip()
    if update_ver != EXPECTED_VERSION:
        raise CreditsAuditError(f"Steam version differs: {update_ver!r}")
    before = {
        language: path_spec(resource_path(steam_root, language)) for language in LANGUAGES
    }
    variants = {language: load_variant(steam_root, language) for language in LANGUAGES}
    after = {
        language: path_spec(resource_path(steam_root, language)) for language in LANGUAGES
    }
    if before != after:
        raise CreditsAuditError("a source resource changed during read-only audit")

    jp = variants["JP"]
    comparisons = {
        language: comparison(jp, variants[language]) for language in ("EN", "SC", "TC")
    }
    sc_tc_raw_identical = variants["SC"]["raw"] == variants["TC"]["raw"]
    sc_tc_text_hashes_identical = all(
        left["utf16le_sha256"] == right["utf16le_sha256"]
        for left, right in zip(
            variants["SC"]["entry_metadata"], variants["TC"]["entry_metadata"], strict=True
        )
    )
    if not sc_tc_raw_identical or not sc_tc_text_hashes_identical:
        raise CreditsAuditError("SC/TC credits payload identity differs from pinned observation")

    if (
        jp["script_summary"]["nonempty_rows_with_lexical_source_script"] != 8
        or jp["script_summary"]["nonempty_rows_with_hangul"] != 0
        or variants["EN"]["script_summary"]["nonempty_rows_with_lexical_source_script"] != 0
        or variants["SC"]["script_summary"]["nonempty_rows_with_lexical_source_script"] != 0
        or variants["TC"]["script_summary"]["nonempty_rows_with_lexical_source_script"] != 0
    ):
        raise CreditsAuditError("language script classification differs")

    routes = static_route_evidence(steam_root)
    if routes["runtime_file_open_proven"]:
        raise CreditsAuditError("unexpected runtime proof state")
    candidate = candidate_boundary()
    if candidate["resource_in_v5_candidate_paths"]:
        raise CreditsAuditError("audit boundary differs: resource is already in v5")

    value = {
        "schema": SCHEMA,
        "status": "STATIC_AUDIT_COMPLETE_RUNTIME_LOAD_UNPROVEN",
        "runtime": {
            "distribution": "Steam",
            "pk_version": update_ver,
            "language_route_under_audit": "JP",
        },
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
            "contains_extracted_binary_payload": False,
            "contains_only_hashes_counts_ids_and_static_conclusions": True,
        },
        "resource_classification": {
            "resource_family": "PK_staff_credits_ending_pages",
            "classification_evidence": "eight_multiline_pages_plus_twelve_empty_slots_in_all_language_variants",
            "credits_content_classification": "strong_static",
            "ending_screen_binding": "static_context_only",
        },
        "language_variants": {language: public_variant(variants[language]) for language in LANGUAGES},
        "cross_language_structure": {
            "all_languages_same_string_count": True,
            "all_languages_same_nonempty_slot_vector": True,
            "all_languages_same_empty_slot_vector": True,
            "sc_tc_raw_payload_identical": sc_tc_raw_identical,
            "sc_tc_text_hash_vectors_identical": sc_tc_text_hashes_identical,
            "jp_to_other_format_comparisons": comparisons,
            "official_sc_tc_korean_translation_source": False,
            "automatic_cross_language_transplant_safe": False,
        },
        "static_runtime_route_evidence": routes,
        "candidate_boundary": candidate,
        "decision": {
            "translation_module_created": False,
            "next_candidate_inclusion": "exclude_pending_runtime_file_open_trace_and_ending_screen_validation",
            "reason_codes": [
                "runtime_file_open_unproven",
                "credits_pages_require_manual_korean_editorial_review",
                "cross_language_format_vectors_not_identical",
                "sc_tc_payload_is_not_a_korean_translation_source",
            ],
            "next_required_evidence": [
                "capture_read_only_file_open_trace_while_triggering_PK_ending_credits",
                "confirm_JP_resource_selection_in_the_ending_screen",
                "after_route_proof_create_manual_Korean_credits_overlay_with_page_level_screen_QA",
            ],
        },
        "safety": {
            "installed_game_files_modified": False,
            "candidate_v5_modified": False,
            "root_readme_modified": False,
            "git_commit_created": False,
            "sc_binary_used_for_translation": False,
            "complete_candidate_binary_written": False,
        },
    }
    assert_source_free(value, "audit model")
    return value


def generate(steam_root: Path = DEFAULT_STEAM_ROOT) -> dict[str, Any]:
    value = model(steam_root)
    AUDIT_PATH.write_bytes(canonical_json_bytes(value))
    return value


def verify(steam_root: Path = DEFAULT_STEAM_ROOT) -> dict[str, Any]:
    value = model(steam_root)
    tracked = strict_json(AUDIT_PATH)
    if tracked != value:
        raise CreditsAuditError("tracked audit differs from the read-only model")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("generate", "verify"))
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    args = parser.parse_args()
    result = generate(args.steam_root) if args.command == "generate" else verify(args.steam_root)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
