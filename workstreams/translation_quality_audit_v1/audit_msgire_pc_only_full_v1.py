#!/usr/bin/env python3
"""Perform a PC-only quality audit over all 122 ``msgire`` entries.

The audit compares the pristine PC Japanese table with the installed Korean
table and PC EN/SC/TC context.  It creates a private proposal only for an
unambiguous source-to-target error, retains already active builder proposals
without duplicating them, and emits a separate hold artifact for terminology
whose Korean wording cannot be safely settled from this evidence alone.

No Switch Korean or historical Korean data is read.  The script writes only
private JSONL evidence below ``tmp`` and never writes a Steam game resource.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Mapping


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
BUILDER = REPO / "workstreams" / "translation_quality_corrections_v1" / "build_translation_quality_corrections_v1.py"
DEFAULT_AUDIT_OUTPUT = AUDIT_ROOT / "semantic" / "msgire_pc_only_full_audit.v1.jsonl"
DEFAULT_CANDIDATE_OUTPUT = AUDIT_ROOT / "semantic" / "msgire_pc_only_quality_addendum.v1.jsonl"
DEFAULT_HOLD_OUTPUT = AUDIT_ROOT / "semantic" / "msgire_pc_only_ambiguous_holds.v1.jsonl"

PATHS = {
    "jp": PRISTINE_ROOT / "MSG_PK" / "JP" / "msgire.bin",
    "ko": STEAM / "MSG_PK" / "JP" / "msgire.bin",
    "en": STEAM / "MSG_PK" / "EN" / "msgire.bin",
    "sc": STEAM / "MSG_PK" / "SC" / "msgire.bin",
    "tc": STEAM / "MSG_PK" / "TC" / "msgire.bin",
}
STRDATA_PATHS = {
    "jp": PRISTINE_ROOT / "MSG" / "JP" / "strdata.bin",
    "ko": STEAM / "MSG" / "JP" / "strdata.bin",
}

EXPECTED_FILE_SHA256 = {
    "jp": "0AFBFE11A380A9C98FB3B368092A05B39ABB6F80C4B0723AD3B6DB55C2559C5D",
    "ko": "C4977A74B98605AB350BE761C67CCF879AEE7565104F8D7FD2B725FDD5806D84",
    "en": "F56ADC564ACBB046B76BC2976C6D2479A9A37B134AF8F8B620E2D65BD7D04035",
    "sc": "FEE2CBE52D688B6E67D751AB468C4A19D8A44A2142C6D9E723F69D340D263548",
    "tc": "D18217453963AF0B4A79548995EBBC5FA73B372870BA0C9F1E5E7557DCB50865",
}
EXPECTED_STRDATA_FILE_SHA256 = {
    "jp": "FF172741A7ADC0F8C9E903A4BB3F4482639CE5AB80EA44C8CC458C300940DEE0",
    "ko": "D518A91E36B9A59EAD0B5ED1FDD067941E4BF72E43AFCB19C296C8AD77C8C128",
}

ENTRY_COUNT = 122
INITIAL_ACTIVE_IDS = {17, 19, 20, 22, 23, 24, 37, 79, 104, 111}
NEW_CANDIDATE_IDS = {112}

# These are terms where the PC source establishes the subject but not a
# uniquely preferable Korean editorial treatment.  They remain distinct from
# normal reviewed-retained rows so a later terminology pass can revisit them
# without rereading the whole 122-entry table.
AMBIGUOUS_HOLDS = {
    13: "historical sobriquet and tea-utensil title require a deliberate Korean title style",
    53: "armor school and historical armor-name terminology need a resource-wide convention",
    59: "botanical and helmet-ornament wording needs a confirmed Korean term preference",
    61: "court-headwear term for the ceremonial streamer is not fixed by PC references",
    62: "historic marriage-gift relation (hikidemono) is context-sensitive in Korean",
    65: "Buddhist divine-name sentence has multiple equally plausible Korean restructurings",
    69: "named hereditary banner and armor terms need same-resource label evidence",
    70: "the white-character component of the horse name requires its visible item-label treatment",
    72: "horse-name and coat-color treatment require proper-name policy rather than automatic prose rewrite",
    81: "collective tea-utensil category is a title-like historical designation",
    82: "tea-kettle mouth-shape term is technical and needs glossary-level terminology review",
    84: "the exact historical room term should be settled with item/context labels before prose change",
    86: "early breech-loading artillery vocabulary is technical and not safely normalized from PC text alone",
    87: "dōmaru is a historical armor-class term with no uniquely safe Korean rendering in this sentence",
    90: "good-luck/omen idiom is semantically close but editorially ambiguous",
    92: "book-title term Tao has reading/title-policy implications",
    108: "specific horse-coat term requires a proper-name/coat-color terminology convention",
    110: "specific horse-coat term requires a proper-name/coat-color terminology convention",
    116: "tea-aesthetic mounting term needs a glossary decision rather than an isolated wording change",
    117: "paired-artwork title distinction requires external label evidence before changing prose",
}

SOURCE_HALF_PROFILE = "\u534a\u8eab\u306b\u69cb\u3048\u305f\u5e03\u888b\u304c\u5de6\u624b\u3067\u8179\u3092\u3055\u3059\u3063\u3066\u3044\u308b"
CURRENT_BARE_UPPER_BODY = "\ubc18\uc2e0\uc744 \ub4dc\ub7ec\ub0b8 \ud3ec\ub300\ud654\uc0c1\uc774"
PROPOSED_HALF_PROFILE = "\ubab8\uc744 \ubc18\ucbe4 \ub3cc\ub9b0 \ud3ec\ub300\ud654\uc0c1\uc774"
STRDATA_HALF_PROFILE = "\ubab8\uc744 \ubc18\ucbe4 \ub3cc\ub9b0 \ud3ec\ub300"
STRDATA_SAME_DESCRIPTION = (3, 112)

RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
PRIVATE_USE_RE = re.compile(r"[\ue000-\uf8ff]")
KANA_OR_HAN_RE = re.compile(
    r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")

sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "workstreams" / "strdata"))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402
from strdata_format import coordinate_texts, parse_raw_strdata  # noqa: E402


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


def load_strdata(path: Path) -> dict[tuple[int, int], str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return coordinate_texts(parse_raw_strdata(raw))


def format_profile(value: str) -> dict[str, Any]:
    return {
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": PRINTF_RE.findall(value),
        "escape_tags": ESC_RE.findall(value),
        "line_breaks": re.findall(r"\r\n|\n|\r", value),
        "outer_ascii_whitespace": [
            value[: len(value) - len(value.lstrip(" \t"))],
            value[len(value.rstrip(" \t")) :],
        ],
        "private_use": [f"U+{ord(character):04X}" for character in PRIVATE_USE_RE.findall(value)],
        "fullwidth_percent_count": value.count("\uff05"),
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


def deterministic_jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)


def active_builder_ids() -> set[int]:
    """Read the current msgire builder inputs without invoking a build/write."""
    if not BUILDER.is_file():
        raise ValueError(f"translation-quality builder is absent: {BUILDER}")
    for dependency in (REPO / "tools", REPO / "workstreams" / "strdata", REPO / "workstreams" / "msggame"):
        dependency_text = str(dependency)
        if dependency_text not in sys.path:
            sys.path.insert(0, dependency_text)
    module_name = "_msgire_pc_only_audit_builder"
    module_spec = importlib.util.spec_from_file_location(module_name, BUILDER)
    if module_spec is None or module_spec.loader is None:
        raise ValueError(f"unable to load builder: {BUILDER}")
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_name] = module
    module_spec.loader.exec_module(module)
    try:
        spec = next(resource for resource in module.SPECS if resource.name == "msgire")
        rows = module.read_proposals(spec)
    finally:
        sys.modules.pop(module_name, None)
    result: set[int] = set()
    for row in rows:
        try:
            identifier = int(row["coordinate"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("msgire builder returned a nonnumeric coordinate") from exc
        if identifier in result:
            raise ValueError(f"duplicate active msgire coordinate: {identifier}")
        result.add(identifier)
    return result


def candidate_for_112(
    source: str,
    current: str,
    file_hashes: Mapping[str, str],
    references: Mapping[str, str],
    strdata_source: str,
    strdata_current: str,
    strdata_file_hashes: Mapping[str, str],
) -> dict[str, Any]:
    if SOURCE_HALF_PROFILE not in source:
        raise ValueError("msgire:112 pristine source no longer has the half-profile predicate")
    if current.count(CURRENT_BARE_UPPER_BODY) != 1:
        raise ValueError("msgire:112 Korean source no longer has exactly one unsupported bare-body phrase")
    if strdata_source != source or STRDATA_HALF_PROFILE not in strdata_current:
        raise ValueError("PC strdata no longer supplies the same-source half-profile Korean evidence")
    proposed = current.replace(CURRENT_BARE_UPPER_BODY, PROPOSED_HALF_PROFILE)
    before_profile = format_profile(current)
    after_profile = format_profile(proposed)
    source_profile = format_profile(source)
    if before_profile != after_profile or source_profile != after_profile:
        raise ValueError("msgire:112 replacement changes a protected text-format field")
    if KANA_OR_HAN_RE.search(proposed) or not HANGUL_RE.search(proposed) or "\0" in proposed or "\ufffd" in proposed:
        raise ValueError("msgire:112 replacement fails Korean-text safety checks")
    return {
        "id": 112,
        "ko": current,
        "proposed_ko": proposed,
        "current_hash": text_hash(current),
        "source_text": source,
        "source_text_hash": text_hash(source),
        "live_ko_file_sha256": file_hashes["ko"],
        "pristine_jp_file_sha256": file_hashes["jp"],
        "reference_contexts": dict(references),
        "issue_type": "half_profile_pose_mistranslated_as_bare_upper_body",
        "rationale": (
            "Pristine PC Japanese describes Hotei in a half-profile/sideways pose "
            "(\u534a\u8eab\u306b\u69cb\u3048\u305f), not as exposing his upper body. "
            "The Korean replacement restores the pose while retaining the painting name and every protected format field."
        ),
        "pc_reference_use": "EN/SC/TC recorded as context only; JP predicate is the translation authority for this correction",
        "pc_cross_resource_evidence": {
            "strdata_same_source_coordinate": "3:112",
            "strdata_pristine_jp_file_sha256": strdata_file_hashes["jp"],
            "strdata_current_ko_file_sha256": strdata_file_hashes["ko"],
            "established_korean_half_profile_phrase": STRDATA_HALF_PROFILE,
            "switch_korean_translation_used": False,
        },
        "format_validation": {
            "current_to_proposed": "runtime_printf_escape_newline_outer_whitespace_private_use_and_percent_match",
            "pristine_jp_to_proposed": "runtime_printf_escape_newline_outer_whitespace_private_use_and_percent_match",
            "all_required_checks_pass": True,
        },
        "switch_korean_translation_used": False,
        "historic_korean_translation_used": False,
        "game_files_written": False,
    }


def build_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    file_hashes = {language: file_hash(path) for language, path in PATHS.items()}
    if file_hashes != EXPECTED_FILE_SHA256:
        raise ValueError("PC msgire file baseline changed; rebase the audit before reuse")
    tables = {language: load_table(path) for language, path in PATHS.items()}
    if any(len(table) != ENTRY_COUNT for table in tables.values()):
        raise ValueError("PC msgire table cardinality differs from 122")
    strdata_file_hashes = {language: file_hash(path) for language, path in STRDATA_PATHS.items()}
    if strdata_file_hashes != EXPECTED_STRDATA_FILE_SHA256:
        raise ValueError("PC strdata cross-resource baseline changed; rebase msgire:112 evidence before reuse")
    strdata_tables = {language: load_strdata(path) for language, path in STRDATA_PATHS.items()}
    if STRDATA_SAME_DESCRIPTION not in strdata_tables["jp"] or STRDATA_SAME_DESCRIPTION not in strdata_tables["ko"]:
        raise ValueError("PC strdata same-source coordinate is absent")

    active_ids = active_builder_ids()
    permitted_active_sets = (INITIAL_ACTIVE_IDS, INITIAL_ACTIVE_IDS | NEW_CANDIDATE_IDS)
    if active_ids not in permitted_active_sets:
        raise ValueError("active msgire candidate set changed outside the PC-only audit partition")
    new_candidate_already_active = NEW_CANDIDATE_IDS.issubset(active_ids)
    if set(AMBIGUOUS_HOLDS).intersection(active_ids | NEW_CANDIDATE_IDS):
        raise ValueError("ambiguous hold partition overlaps a proposal coordinate")

    candidate_rows = [
        candidate_for_112(
            tables["jp"][112],
            tables["ko"][112],
            file_hashes,
            {language.upper(): tables[language][112] for language in ("en", "sc", "tc")},
            strdata_tables["jp"][STRDATA_SAME_DESCRIPTION],
            strdata_tables["ko"][STRDATA_SAME_DESCRIPTION],
            strdata_file_hashes,
        )
    ]
    candidates_by_id = {row["id"]: row for row in candidate_rows}
    audit_rows: list[dict[str, Any]] = []
    hold_rows: list[dict[str, Any]] = []
    for identifier in range(ENTRY_COUNT):
        source = tables["jp"][identifier]
        current = tables["ko"][identifier]
        references = {language.upper(): tables[language][identifier] for language in ("en", "sc", "tc")}
        if identifier in INITIAL_ACTIVE_IDS:
            disposition = "active_existing_candidate"
            detail = "already present in current msgire builder inputs; independently excluded from duplicate proposal"
        elif identifier in candidates_by_id:
            disposition = "active_new_candidate" if new_candidate_already_active else "candidate_high_confidence"
            detail = candidates_by_id[identifier]["issue_type"]
        elif identifier in AMBIGUOUS_HOLDS:
            disposition = "hold_ambiguous_name_or_term"
            detail = AMBIGUOUS_HOLDS[identifier]
        else:
            disposition = "retained_after_pc_comparison"
            detail = "no high-confidence meaning, proper-name, quantity, or effect error found from PC-only evidence"
        row = {
            "schema": "nobu16.kr.msgire-pc-only-full-audit.v1",
            "resource": "msgire",
            "id": identifier,
            "disposition": disposition,
            "disposition_detail": detail,
            "source_jp": source,
            "source_jp_utf16le_sha256": text_hash(source),
            "current_ko": current,
            "current_ko_utf16le_sha256": text_hash(current),
            "reference_contexts": references,
            "source_file_sha256": file_hashes["jp"],
            "current_file_sha256": file_hashes["ko"],
            "reference_file_sha256": {language.upper(): file_hashes[language] for language in ("en", "sc", "tc")},
            "audit_scope": {
                "pristine_pc_japanese": True,
                "current_pc_korean": True,
                "pc_en_sc_tc_references": True,
                "switch_korean_read": False,
                "historic_korean_read": False,
                "steam_game_resource_written": False,
            },
        }
        audit_rows.append(row)
        if disposition == "hold_ambiguous_name_or_term":
            hold_rows.append(row)

    summary = {
        "schema": "nobu16.kr.msgire-pc-only-full-audit-summary.v1",
        "entry_count": len(audit_rows),
        "active_builder_candidate_count": len(active_ids),
        "new_candidate_already_active": new_candidate_already_active,
        "new_high_confidence_candidate_count": len(candidate_rows),
        "ambiguous_hold_count": len(hold_rows),
        "disposition_counts": dict(sorted(Counter(row["disposition"] for row in audit_rows).items())),
        "switch_korean_translation_used": False,
        "historic_korean_translation_used": False,
        "game_files_written": False,
    }
    return audit_rows, candidate_rows, hold_rows, summary


def validate_rows(
    audit_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    hold_rows: list[dict[str, Any]],
    summary: Mapping[str, Any],
) -> None:
    if len(audit_rows) != ENTRY_COUNT or {row["id"] for row in audit_rows} != set(range(ENTRY_COUNT)):
        raise ValueError("full msgire audit does not cover every 0..121 coordinate exactly once")
    expected_dispositions = {
        "active_existing_candidate": len(INITIAL_ACTIVE_IDS),
        "hold_ambiguous_name_or_term": len(AMBIGUOUS_HOLDS),
        "retained_after_pc_comparison": ENTRY_COUNT - len(INITIAL_ACTIVE_IDS) - len(NEW_CANDIDATE_IDS) - len(AMBIGUOUS_HOLDS),
        "candidate_high_confidence" if not summary["new_candidate_already_active"] else "active_new_candidate": len(NEW_CANDIDATE_IDS),
    }
    if Counter(row["disposition"] for row in audit_rows) != Counter(expected_dispositions):
        raise ValueError("msgire audit disposition counts differ from reviewed partition")
    if {row["id"] for row in candidate_rows} != NEW_CANDIDATE_IDS:
        raise ValueError("high-confidence msgire candidate set differs from reviewed set")
    if {row["id"] for row in hold_rows} != set(AMBIGUOUS_HOLDS):
        raise ValueError("ambiguous msgire hold set differs from reviewed set")
    if any(row.get("id") in INITIAL_ACTIVE_IDS for row in candidate_rows):
        raise ValueError("new candidate duplicates existing active msgire proposal")
    candidate = candidate_rows[0]
    if candidate["ko"] == candidate["proposed_ko"] or text_hash(candidate["ko"]) != candidate["current_hash"]:
        raise ValueError("msgire candidate text/hash gate is invalid")
    if format_profile(candidate["ko"]) != format_profile(candidate["proposed_ko"]):
        raise ValueError("msgire candidate format profile differs")
    if KANA_OR_HAN_RE.search(candidate["proposed_ko"]) or not HANGUL_RE.search(candidate["proposed_ko"]):
        raise ValueError("msgire candidate retains Japanese/CJK text or lacks Korean text")
    for row in audit_rows:
        scope = row["audit_scope"]
        if scope["switch_korean_read"] or scope["historic_korean_read"] or scope["steam_game_resource_written"]:
            raise ValueError("audit scope must remain PC-only and read-only")
    if summary.get("entry_count") != ENTRY_COUNT or summary.get("new_high_confidence_candidate_count") != 1:
        raise ValueError("msgire audit summary is inconsistent")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-output", type=Path, default=DEFAULT_AUDIT_OUTPUT)
    parser.add_argument("--candidate-output", type=Path, default=DEFAULT_CANDIDATE_OUTPUT)
    parser.add_argument("--hold-output", type=Path, default=DEFAULT_HOLD_OUTPUT)
    parser.add_argument("--write", action="store_true", help="write private PC-only audit, candidate, and hold JSONL files")
    parser.add_argument("--validate", action="store_true", help="validate generated data and any existing deterministic outputs")
    args = parser.parse_args()

    outputs = {
        "audit": safe_under(args.audit_output, AUDIT_ROOT),
        "candidate": safe_under(args.candidate_output, AUDIT_ROOT),
        "hold": safe_under(args.hold_output, AUDIT_ROOT),
    }
    audit_rows, candidate_rows, hold_rows, summary = build_rows()
    validate_rows(audit_rows, candidate_rows, hold_rows, summary)
    payloads = {
        "audit": deterministic_jsonl(audit_rows),
        "candidate": deterministic_jsonl(candidate_rows),
        "hold": deterministic_jsonl(hold_rows),
    }
    if args.write:
        for key in ("audit", "candidate", "hold"):
            atomic_write(outputs[key], payloads[key])
    if args.validate:
        for key in ("audit", "candidate", "hold"):
            if outputs[key].exists() and outputs[key].read_text(encoding="utf-8") != payloads[key]:
                raise ValueError(f"existing {key} output differs from deterministic PC-only evidence")
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True))


if __name__ == "__main__":
    main()
