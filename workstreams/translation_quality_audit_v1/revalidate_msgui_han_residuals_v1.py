#!/usr/bin/env python3
"""Revalidate the 79 unresolved-Han PC ``msgui`` review coordinates.

The review queue marks 79 live Korean ``msgui`` strings that are still the
same Han/Kanji text as pristine PC Japanese.  Seventy already have entries in
the active ``msgui_ko.jsonl`` input of the PC-only realign builder.  This
script records their exact-source/current gates and format validation instead
of creating duplicate builder inputs.  The remaining nine are Japanese IME
component/status glyphs; PC EN/SC/TC does not establish safe Korean labels, so
they are retained as explicit no-candidate holds.

Only pristine PC Japanese, current PC Korean, and PC EN/SC/TC are read.  It
does not read Switch Korean or historic Korean backups, and it never writes a
Steam game resource.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PRISTINE_ROOT = (
    STEAM
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
)
AUDIT_ROOT = REPO / "tmp" / "translation_quality_audit_v1"
QUEUE = AUDIT_ROOT / "semantic_inventory_v6" / "private_review_queue.jsonl"
ACTIVE_RESIDUALS = AUDIT_ROOT / "proposals" / "msgui_ko.jsonl"
OTHER_REALIGN = AUDIT_ROOT / "semantic" / "msgui_findings.v1.jsonl"
DEFAULT_OUTPUT = AUDIT_ROOT / "semantic" / "msgui_han_residual_revalidation.v1.jsonl"
DEFAULT_HOLD_OUTPUT = AUDIT_ROOT / "semantic" / "msgui_ime_component_holds.v1.jsonl"

PATHS = {
    "jp": PRISTINE_ROOT / "MSG_PK" / "JP" / "msgui.bin",
    "ko": STEAM / "MSG_PK" / "JP" / "msgui.bin",
    "en": STEAM / "MSG_PK" / "EN" / "msgui.bin",
    "sc": STEAM / "MSG_PK" / "SC" / "msgui.bin",
    "tc": STEAM / "MSG_PK" / "TC" / "msgui.bin",
}

# These bind the audit to the installed PC baseline and the already reviewed
# builder input.  A changed baseline must be explicitly re-reviewed rather
# than silently reusing this evidence.
EXPECTED_FILE_SHA256 = {
    "jp": "9775D4B7253828899F7EF0DF2E88AB28121ACB260E1381F3D706C6A1065D504A",
    "ko": "470FAD81852C6D80D2E1A0390F89A5590529ACE0BE5192DC1C1C58F70178D0DB",
    "en": "B993412D73889B58B68C8998446AF65E1C7CD02066FEAF483E3F44E3EB0602D5",
    "sc": "B21196467A5A2E08A4019D4CEC4A474A64C6F0CD577FA3D068F2130F95CF2C0C",
    "tc": "FA4351F8303DFDAA240441C5BDF8B42DD4F7603E56E6DBAB8CB4DC0594C007D5",
}
EXPECTED_ACTIVE_RESIDUAL_SHA256 = "E21CA23A3F83E1AE0303264450AEC5B4A28049BDDB2C984B5A5C283D52A2E75A"
EXPECTED_OTHER_REALIGN_SHA256 = "9DC3FAC2BDF42306569557AE9A41E148999D4841DFD1D0B952601A86EF535E7B"

ALL_RESIDUAL_IDS = {
    191, 192, 193, 194, 196, 197, 198, 199, 200, 201, 203, 206, 207, 208, 209,
    1921, 1923, 1924, 1927, 1928, 1929, 1930, 1931, 1932,
    2665, 2666, 2667, 2668, 2669, 2670, 2671, 2672, 2673, 2674, 2675, 2676,
    2677, 2678, 2679, 2680, 2681, 2683, 2685, 2686,
    2749, 2750, 2751, 2752, 2753, 2754, 2755, 2756, 2757, 2758, 2761, 2764,
    2765, 2767, 2768, 2772, 2773, 2775, 2778, 2779, 2780, 2782, 2784, 2785,
    2786, 2787, 2788, 2789, 2790, 2791, 2792, 2793, 2794, 2796, 2797,
}
IME_HOLD_IDS = {1921, 1923, 1924, 1927, 1928, 1929, 1930, 1931, 1932}
EXISTING_CANDIDATE_IDS = ALL_RESIDUAL_IDS - IME_HOLD_IDS
EXPECTED_CROSS_ARTIFACT_SAME_VALUE = {2757: "\uba85", 2758: "\uc804\uccb4"}

sys.path.insert(0, str(REPO / "tools"))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
PRIVATE_USE_RE = re.compile(r"[\ue000-\uf8ff]")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
CJK_OR_KANA_RE = re.compile(
    r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff"
    r"\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-16-le")).hexdigest().upper()


def load_table(path: Path) -> tuple[str, ...]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return parse_message_table(raw).texts


def profile(value: str) -> dict[str, object]:
    return {
        "escape_tags": ESC_RE.findall(value),
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf": PRINTF_RE.findall(value),
        "newlines": re.findall(r"\r\n|\n|\r", value),
        "outer_ascii_whitespace": (
            value[: len(value) - len(value.lstrip(" \t"))],
            value[len(value.rstrip(" \t")) :],
        ),
        "private_use": [f"U+{ord(character):04X}" for character in PRIVATE_USE_RE.findall(value)],
        "fullwidth_percent_count": value.count("\uff05"),
        "question_mark_count": value.count("?"),
    }


def profile_match(left: dict[str, object], right: dict[str, object]) -> dict[str, bool]:
    return {
        "escape_tags_match": left["escape_tags"] == right["escape_tags"],
        "runtime_tokens_match": left["runtime_tokens"] == right["runtime_tokens"],
        "printf_match": left["printf"] == right["printf"],
        "newlines_match": left["newlines"] == right["newlines"],
        "outer_ascii_whitespace_match": left["outer_ascii_whitespace"] == right["outer_ascii_whitespace"],
        "private_use_match": left["private_use"] == right["private_use"],
        "fullwidth_percent_count_match": left["fullwidth_percent_count"] == right["fullwidth_percent_count"],
        "question_mark_count_match": left["question_mark_count"] == right["question_mark_count"],
    }


def korean_integrity(value: str) -> dict[str, bool]:
    return {
        "hangul_present": bool(HANGUL_RE.search(value)),
        "no_japanese_or_cjk_residue": not bool(CJK_OR_KANA_RE.search(value)),
        "no_replacement_glyph": "\ufffd" not in value,
        "no_repeated_question_marks": "??" not in value,
    }


def safe_under(path: Path, root: Path) -> Path:
    resolved = path.resolve(strict=False)
    allowed = root.resolve(strict=False)
    if resolved != allowed and allowed not in resolved.parents:
        raise ValueError(f"output must remain below {allowed}: {resolved}")
    return resolved


def atomic_write(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def jsonl_rows(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise ValueError(f"required artifact is absent: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"row is not an object: {path}:{line_number}")
        rows.append(value)
    return rows


def unique_korean_map(path: Path, rows: list[dict[str, Any]]) -> dict[int, str]:
    result: dict[int, str] = {}
    for line_number, row in enumerate(rows, start=1):
        identifier = row.get("id")
        value = row.get("ko")
        if isinstance(identifier, bool) or not isinstance(identifier, int) or not isinstance(value, str) or not value:
            raise ValueError(f"invalid Korean candidate row: {path}:{line_number}")
        if identifier in result:
            raise ValueError(f"duplicate candidate ID: {path}:{identifier}")
        result[identifier] = value
    return result


def queue_rows() -> dict[int, dict[str, Any]]:
    result: dict[int, dict[str, Any]] = {}
    for line_number, row in enumerate(jsonl_rows(QUEUE), start=1):
        if row.get("resource") != "msgui" or "target_han_residual" not in row.get("flags", []):
            continue
        coordinate = row.get("coordinate")
        try:
            identifier = int(coordinate)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid msgui queue coordinate: {QUEUE}:{line_number}") from exc
        if identifier in result:
            raise ValueError(f"duplicate msgui queue coordinate: {identifier}")
        result[identifier] = row
    if set(result) != ALL_RESIDUAL_IDS:
        raise ValueError("msgui Han residual queue differs from the reviewed 79-coordinate set")
    return result


def build_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    file_hashes = {language: file_hash(path) for language, path in PATHS.items()}
    if file_hashes != EXPECTED_FILE_SHA256:
        raise ValueError("PC msgui baseline hash differs; rebase review before reuse")
    tables = {language: load_table(path) for language, path in PATHS.items()}
    if any(len(table) != len(tables["jp"]) for table in tables.values()):
        raise ValueError("PC msgui table cardinalities differ")

    if file_hash(ACTIVE_RESIDUALS) != EXPECTED_ACTIVE_RESIDUAL_SHA256:
        raise ValueError("active msgui residual artifact changed; re-review before reuse")
    if file_hash(OTHER_REALIGN) != EXPECTED_OTHER_REALIGN_SHA256:
        raise ValueError("other msgui realign artifact changed; re-review before reuse")
    active = unique_korean_map(ACTIVE_RESIDUALS, jsonl_rows(ACTIVE_RESIDUALS))
    if set(active) != EXISTING_CANDIDATE_IDS:
        raise ValueError("active msgui residual candidate set differs from reviewed 70-coordinate set")
    other = unique_korean_map(OTHER_REALIGN, jsonl_rows(OTHER_REALIGN))
    overlap = set(active).intersection(other)
    if overlap != set(EXPECTED_CROSS_ARTIFACT_SAME_VALUE):
        raise ValueError("existing msgui realign overlap differs from reviewed safe overlap")
    if {identifier: active[identifier] for identifier in overlap} != EXPECTED_CROSS_ARTIFACT_SAME_VALUE:
        raise ValueError("existing msgui realign overlap has conflicting Korean replacements")
    if {identifier: other[identifier] for identifier in overlap} != EXPECTED_CROSS_ARTIFACT_SAME_VALUE:
        raise ValueError("other msgui realign overlap has conflicting Korean replacements")

    queue = queue_rows()
    evidence: list[dict[str, Any]] = []
    holds: list[dict[str, Any]] = []
    for identifier in sorted(ALL_RESIDUAL_IDS):
        source = tables["jp"][identifier]
        current = tables["ko"][identifier]
        queue_row = queue[identifier]
        if source != current:
            raise ValueError(f"target Han residual is no longer exact at msgui:{identifier}")
        if queue_row.get("jp") != source or queue_row.get("ko") != current:
            raise ValueError(f"review queue text differs from PC tables at msgui:{identifier}")
        if queue_row.get("jp_utf16le_sha256") != text_hash(source) or queue_row.get("ko_utf16le_sha256") != text_hash(current):
            raise ValueError(f"review queue hash differs from PC tables at msgui:{identifier}")
        source_profile = profile(source)
        current_profile = profile(current)
        pc_contexts = {language: tables[language][identifier] for language in ("en", "sc", "tc")}
        queue_contexts = {"EN": pc_contexts["en"], "SC": pc_contexts["sc"], "TC": pc_contexts["tc"]}
        if queue_contexts != queue_row.get("contexts"):
            raise ValueError(f"review queue PC contexts differ from PC tables at msgui:{identifier}")

        common = {
            "resource": "msgui",
            "coordinate": str(identifier),
            "id": identifier,
            "current_ko": current,
            "current_hash": text_hash(current),
            "source_text": source,
            "source_text_hash": text_hash(source),
            "source_file_sha256": file_hashes["ko"],
            "pristine_jp_file_sha256": file_hashes["jp"],
            "reference_file_sha256": {language: file_hashes[language] for language in ("en", "sc", "tc")},
            "pc_target_contexts": pc_contexts,
            "source_gate_validation": "exact_utf16le_hash_match",
            "current_ko_gate_validation": "exact_utf16le_hash_match",
            "switch_korean_translation_used": False,
            "historic_korean_backup_used": False,
            "game_files_written": False,
        }
        if identifier in IME_HOLD_IDS:
            holds.append(
                {
                    **common,
                    "review_status": "hold_no_high_confidence_replacement",
                    "classification": "Japanese_IME_component_or_status_glyph",
                    "reason": "PC EN/SC/TC is blank for these compact IME labels (except a single English 'Single' marker), so it does not establish Korean wording or the runtime layout contract. Existing PC realign review intentionally excluded this component cluster.",
                    "no_candidate_created": True,
                }
            )
            continue

        replacement = active[identifier]
        replacement_profile = profile(replacement)
        source_format = profile_match(source_profile, replacement_profile)
        current_format = profile_match(current_profile, replacement_profile)
        integrity = korean_integrity(replacement)
        if not all(source_format.values()) or not all(current_format.values()) or not all(integrity.values()):
            raise ValueError(f"existing msgui candidate fails format or Korean integrity at {identifier}")
        if replacement == current:
            raise ValueError(f"existing msgui candidate does not replace residual at {identifier}")
        evidence.append(
            {
                **common,
                "issue_type": "untranslated_han_ui_residual_revalidation",
                "existing_candidate_comparison": {
                    "artifact": ACTIVE_RESIDUALS.name,
                    "active_candidate_artifact_sha256": EXPECTED_ACTIVE_RESIDUAL_SHA256,
                    "existing_candidate_ko": replacement,
                    "existing_candidate_hash": text_hash(replacement),
                    "source_coordinate_unchanged_han_residual": True,
                    "other_msgui_realign_overlap": identifier in overlap,
                    "overlap_value_matches": identifier not in overlap or other[identifier] == replacement,
                    "material_replacement_recommendation": None,
                },
                "format_profile": {
                    "pristine_jp": source_profile,
                    "current_ko": current_profile,
                    "existing_candidate": replacement_profile,
                },
                "format_validation": {
                    "existing_to_pristine_jp": source_format,
                    "existing_to_current": current_format,
                    "existing_integrity": integrity,
                    "all_required_checks_pass": True,
                },
                "candidate_integration_policy": "evidence_only_existing_msgui_realign_input_no_duplicate_application",
            }
        )

    if {row["id"] for row in evidence} != EXISTING_CANDIDATE_IDS or {row["id"] for row in holds} != IME_HOLD_IDS:
        raise ValueError("msgui residual partition differs")
    summary = {
        "queue_residual_count": len(ALL_RESIDUAL_IDS),
        "revalidated_existing_realignment_count": len(evidence),
        "ime_component_hold_count": len(holds),
        "existing_candidate_artifact": ACTIVE_RESIDUALS.name,
        "cross_artifact_same_value_overlap_ids": sorted(overlap),
        "pc_baseline_hash_gates": "all_exact_file_hash_match",
        "source_current_hash_gates": "all_exact_utf16le_hash_match",
        "format_validation": "all_existing_candidates_match_pristine_current_runtime_printf_escape_newline_whitespace_profiles",
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
    }
    return evidence, holds, summary


def payload(rows: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--hold-output", type=Path, default=DEFAULT_HOLD_OUTPUT)
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if not args.validate and not args.write:
        parser.error("choose --validate and/or --write")
    try:
        output = safe_under(args.output, AUDIT_ROOT)
        hold_output = safe_under(args.hold_output, AUDIT_ROOT)
        evidence, holds, summary = build_rows()
        if args.write:
            atomic_write(output, payload(evidence))
            atomic_write(hold_output, payload(holds))
            summary = {
                **summary,
                "output": str(output),
                "output_bytes": output.stat().st_size,
                "hold_output": str(hold_output),
                "hold_output_bytes": hold_output.stat().st_size,
                "json_encoding": "ensure_ascii_true_utf8",
            }
    except (OSError, ValueError, json.JSONDecodeError, IndexError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
