#!/usr/bin/env python3
"""Audit every PC ``msgstf`` credits-table entry without Switch evidence.

The authority for this review is the declared pristine PC Japanese table.  The
installed PC Korean table is the target; PC EN/SC/TC are recorded only as
context.  The three generated JSONL files are private because they contain
source-paired commercial text.  This helper does not read a Switch Korean
resource, a historical Korean backup, or write a Steam game resource.

``msgstf`` is a 20-slot credits table, with eight populated entries and twelve
intentional empty slots.  The high-confidence fixes below repair credit
headings where a *person/role* was translated as an activity, or where the
source's production/modeling scope was replaced by a materially different
label.  Project-role wording that cannot be settled from PC text alone is
kept in the separate hold output rather than rewritten speculatively.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
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
DEFAULT_AUDIT_OUTPUT = AUDIT_ROOT / "semantic" / "msgstf_pc_only_full_audit.v1.jsonl"
DEFAULT_CANDIDATE_OUTPUT = AUDIT_ROOT / "semantic" / "msgstf_pc_only_quality_addendum.v1.jsonl"
DEFAULT_HOLD_OUTPUT = AUDIT_ROOT / "semantic" / "msgstf_pc_only_ambiguous_holds.v1.jsonl"
GENERIC_BUILDER = REPO / "workstreams" / "translation_quality_corrections_v1" / "build_translation_quality_corrections_v1.py"

PATHS = {
    "jp": PRISTINE_ROOT / "MSG_PK" / "JP" / "msgstf.bin",
    "ko": STEAM / "MSG_PK" / "JP" / "msgstf.bin",
    "en": STEAM / "MSG_PK" / "EN" / "msgstf.bin",
    "sc": STEAM / "MSG_PK" / "SC" / "msgstf.bin",
    "tc": STEAM / "MSG_PK" / "TC" / "msgstf.bin",
}

EXPECTED_FILE_SHA256 = {
    "jp": "01EEB0B1B4879B6C70E9D7564F9D2FBD93E7B537CF8C614A58EEA82A83785A29",
    "ko": "B90BB9C18C92626A3E9B0F9A2620FEFAAD9A51A2E67C95B8514CC4E4F4A5C607",
    "en": "75F665B1400560EB1A91DF6F2334B4AC93B9F003C036CFCF62DCEF2CC30AE0B5",
    "sc": "B0B61DD26272AA0E64179C7C6495F23C8BA083942E84F1B9F4A3405725AC74CA",
    "tc": "4213547ACF0174C099A93E758403CCF944BFCC5225B41488B642E567C677343F",
}

# Keeping source text itself out of this tracked helper avoids duplicating
# commercial Japanese text outside the private audit artifacts.  A per-entry
# source hash, together with the pristine-file hash above, rejects a rebase.
EXPECTED_SOURCE_TEXT_SHA256 = {
    0: "A74F1E6DA39AF4EB9470134DFB41BBD53D3051B270E8D3B606A3DAF9872F815A",
    1: "1754361C8A8EFF383E7ECC664311EA8A342BB957487F292ECB6FE1DDB1723EAC",
    2: "62839FEA907CC4B4C2788AD6D4DF5CB15071771DBE8DCC78848735371D85AB4A",
    3: "CC6D3563AFEBD84A4FF55E56F638DECADED6001791B8A3DB709F3238F3D790F2",
    4: "932E2800C6650855D422DA6F09646620546F1ADAD6E0B84C9B4AA31EC03D8D27",
    5: "DF1FC37E37CA7F1B6411222C309ED038FD30B6C6F8C7B6FF0B3ECD39A0FC4235",
    6: "0FB84E801791CEF7DA4499C11F122AB64C7FA15756CC2C7751C442571684CAD9",
    7: "79957621468C56F980CEAC5729723E04DE905A4B3FC902B350024CE7603CCD33",
}

ENTRY_COUNT = 20
POPULATED_IDS = set(range(8))
EMPTY_IDS = set(range(8, ENTRY_COUNT))
NEW_CANDIDATE_IDS = {0, 1, 2, 3}

RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
KANA_OR_HAN_RE = re.compile(
    r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")

sys.path.insert(0, str(REPO / "tools"))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


def u(value: str) -> str:
    """Decode an ASCII-only Unicode-escape literal deterministically."""
    return value.encode("ascii").decode("unicode_escape")


# The current-PC phrases are deliberately encoded as ASCII escapes so this
# source remains safe to execute from a legacy PowerShell code page.  The
# order matters only where a shorter phrase occurs inside a longer heading.
REPLACEMENTS: dict[int, tuple[tuple[str, str], ...]] = {
    0: (
        (
            u(r"\ub3c4\uad6c \ubc0f \ub77c\uc774\ube0c\ub7ec\ub9ac \ud504\ub85c\uadf8\ub798\ubc0d"),
            u(r"\ub3c4\uad6c \ubc0f \ub77c\uc774\ube0c\ub7ec\ub9ac \ud504\ub85c\uadf8\ub798\uba38"),
        ),
        (
            u(r"\uc778\uacf5\uc9c0\ub2a5 \ud504\ub85c\uadf8\ub798\ubc0d"),
            u(r"\uc778\uacf5\uc9c0\ub2a5 \ud504\ub85c\uadf8\ub798\uba38"),
        ),
        (u(r"\uac8c\uc784 \uae30\ud68d"), u(r"\uac8c\uc784 \uae30\ud68d\uc790")),
        (u(r"\ud504\ub85c\uadf8\ub798\ubc0d"), u(r"\ud504\ub85c\uadf8\ub798\uba38")),
    ),
    1: (
        (u(r"\uc5bc\uad74 \ubaa8\uc158 \uc5f0\uae30"), u(r"\ud398\uc774\uc15c \uc561\ud130")),
        (u(r"\ubaa8\uc158 \uc5f0\uae30"), u(r"\ubaa8\uc158 \uc561\ud130")),
    ),
    2: (
        (u(r"\uce90\ub9ad\ud130 \uc544\ud2b8"), u(r"\uce90\ub9ad\ud130 \ubaa8\ub378\ub9c1")),
        (u(r"\ud658\uacbd \uc544\ud2b8"), u(r"\ud658\uacbd \ubaa8\ub378\ub9c1")),
        (u(r"\uc774\ucc28\uc6d0 \uc815\uc9c0\ud654\uba74 \ub514\uc790\uc778"), u(r"2D \uc560\ub2c8\uba54\uc774\uc158")),
    ),
    3: (
        (u(r"\uc601\uc0c1 \ub514\uc790\uc778"), u(r"\uc601\uc0c1 \uc81c\uc791")),
        (u(r"\uc2dc\uac01 \ud488\uc9c8 \uad00\ub9ac"), u(r"\ucef4\ud4e8\ud130 \uadf8\ub798\ud53d \ud488\uc9c8 \uad00\ub9ac")),
    ),
}

ISSUE_TYPES = {
    0: "credit_role_nouns_mistranslated_as_activities",
    1: "credit_actor_roles_mistranslated_as_acting_activity",
    2: "credit_modeling_and_animation_scope_mistranslated",
    3: "credit_production_and_cg_scope_mistranslated",
}

ISSUE_RATIONALES = {
    0: (
        "The Korean credits headings name planning/programming activities while the "
        "pristine PC Japanese headings label the credited people.  The replacement "
        "restores role nouns without changing any credit line layout."
    ),
    1: (
        "The source labels actor roles, but the Korean headings label an acting "
        "activity.  The replacement restores the credited actor-role categories."
    ),
    2: (
        "The source distinguishes character/stage modeling and 2D animation.  The "
        "current Korean broadens modeling into art and replaces animation with still "
        "screen design; the replacement restores those source scopes."
    ),
    3: (
        "The source uses production and CG-quality-management categories.  The "
        "current Korean changes them to design and generic visual quality; the "
        "replacement restores the stated production and CG scope."
    ),
}

# These two issues are visible in the same credits entry as high-confidence
# corrections, but cannot be resolved safely without a project-wide production
# role glossary.  They intentionally do not block the independent fixes.
AMBIGUOUS_HOLDS = (
    {
        "id": 2,
        "hold_key": "action_design_credit_role_style",
        "reason": (
            "The pristine PC Japanese action-design heading and the current Korean "
            "animation-art heading are not equivalent, but the uniquely appropriate "
            "Korean production-role title needs a project-wide credit convention."
        ),
    },
    {
        "id": 2,
        "hold_key": "event_production_credit_role_style",
        "reason": (
            "The pristine PC Japanese event-production heading is narrower/different "
            "from the current Korean cinematics label; do not normalize it without "
            "the project-specific production-role glossary."
        ),
    },
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


def format_profile(value: str) -> dict[str, Any]:
    esc_offsets = {offset for match in ESC_RE.finditer(value) for offset in range(match.start(), match.end())}
    return {
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": PRINTF_RE.findall(value),
        "escape_tags": ESC_RE.findall(value),
        "line_breaks": re.findall(r"\r\n|\n|\r", value),
        "leading_whitespace": value[: len(value) - len(value.lstrip())],
        "trailing_whitespace": value[len(value.rstrip()) :],
        "private_use": [f"U+{ord(character):04X}" for character in value if 0xE000 <= ord(character) <= 0xF8FF],
        "controls": [
            f"U+{ord(character):04X}"
            for index, character in enumerate(value)
            if unicodedata.category(character) == "Cc" and character not in ("\r", "\n") and index not in esc_offsets
        ],
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


def replace_exactly_once(value: str, before: str, after: str, identifier: int) -> str:
    if value.count(before) != 1:
        raise ValueError(f"msgstf:{identifier}: expected one current-PC occurrence for a reviewed heading")
    if before == after:
        raise ValueError(f"msgstf:{identifier}: ineffective heading replacement")
    return value.replace(before, after, 1)


def candidate_for(
    identifier: int,
    source: str,
    current: str,
    file_hashes: Mapping[str, str],
    references: Mapping[str, str],
) -> dict[str, Any]:
    if text_hash(source) != EXPECTED_SOURCE_TEXT_SHA256[identifier]:
        raise ValueError(f"msgstf:{identifier}: pristine PC Japanese source changed")
    proposed = current
    for before, after in REPLACEMENTS[identifier]:
        proposed = replace_exactly_once(proposed, before, after, identifier)
    if proposed == current:
        raise ValueError(f"msgstf:{identifier}: no effective Korean correction")
    before_profile = format_profile(current)
    after_profile = format_profile(proposed)
    if before_profile != after_profile:
        raise ValueError(f"msgstf:{identifier}: correction changes a protected format field")
    if KANA_OR_HAN_RE.search(proposed) or not HANGUL_RE.search(proposed) or "\0" in proposed or "\ufffd" in proposed:
        raise ValueError(f"msgstf:{identifier}: correction fails Korean-text safety checks")
    return {
        "resource": "msgstf",
        "id": identifier,
        "ko": current,
        "proposed_ko": proposed,
        "current_hash": text_hash(current),
        "source_text": source,
        "source_text_hash": text_hash(source),
        "live_ko_file_sha256": file_hashes["ko"],
        "pristine_jp_file_sha256": file_hashes["jp"],
        "reference_contexts": dict(references),
        "issue_type": ISSUE_TYPES[identifier],
        "rationale": ISSUE_RATIONALES[identifier],
        "pc_reference_use": "EN/SC/TC recorded as context only; pristine PC Japanese is the translation authority",
        "format_validation": {
            "current_to_proposed": "runtime_printf_escape_newline_outer_whitespace_private_use_controls_and_percent_match",
            "all_required_checks_pass": True,
        },
        "switch_korean_translation_used": False,
        "historic_korean_translation_used": False,
        "game_files_written": False,
    }


def generic_builder_has_msgstf_resource() -> bool:
    """Report the integration requirement without importing mutable proposals."""
    if not GENERIC_BUILDER.is_file():
        return False
    source = GENERIC_BUILDER.read_text(encoding="utf-8")
    return bool(re.search(r'ResourceSpec\(\s*"msgstf"', source))


def build_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    file_hashes = {language: file_hash(path) for language, path in PATHS.items()}
    if file_hashes != EXPECTED_FILE_SHA256:
        raise ValueError("PC msgstf baseline changed; rebase the PC-only audit before reuse")
    tables = {language: load_table(path) for language, path in PATHS.items()}
    if any(len(table) != ENTRY_COUNT for table in tables.values()):
        raise ValueError("PC msgstf table cardinality differs from 20")
    if any(tables[language][identifier] for language in tables for identifier in EMPTY_IDS):
        raise ValueError("msgstf expected-empty slots are no longer empty")
    if {identifier for identifier in POPULATED_IDS if not tables["jp"][identifier]} != set():
        raise ValueError("msgstf populated pristine-PC slots changed")
    if {identifier for identifier in POPULATED_IDS if text_hash(tables["jp"][identifier]) != EXPECTED_SOURCE_TEXT_SHA256[identifier]}:
        raise ValueError("msgstf pristine-PC populated-slot hashes changed")

    candidates_by_id = {
        identifier: candidate_for(
            identifier,
            tables["jp"][identifier],
            tables["ko"][identifier],
            file_hashes,
            {language.upper(): tables[language][identifier] for language in ("en", "sc", "tc")},
        )
        for identifier in sorted(NEW_CANDIDATE_IDS)
    }
    audit_rows: list[dict[str, Any]] = []
    for identifier in range(ENTRY_COUNT):
        if identifier in candidates_by_id:
            disposition = "candidate_high_confidence"
            detail = candidates_by_id[identifier]["issue_type"]
        elif identifier in EMPTY_IDS:
            disposition = "retained_intentional_empty_slot"
            detail = "empty in pristine PC JP and every current PC language"
        else:
            disposition = "retained_after_pc_comparison"
            detail = "no high-confidence meaning, role, proper-name, quantity, or terminology error found from PC-only evidence"
        audit_rows.append(
            {
                "schema": "nobu16.kr.msgstf-pc-only-full-audit.v1",
                "resource": "msgstf",
                "id": identifier,
                "disposition": disposition,
                "disposition_detail": detail,
                "source_jp": tables["jp"][identifier],
                "source_jp_utf16le_sha256": text_hash(tables["jp"][identifier]),
                "current_ko": tables["ko"][identifier],
                "current_ko_utf16le_sha256": text_hash(tables["ko"][identifier]),
                "reference_contexts": {language.upper(): tables[language][identifier] for language in ("en", "sc", "tc")},
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
        )

    hold_rows: list[dict[str, Any]] = []
    for hold in AMBIGUOUS_HOLDS:
        identifier = hold["id"]
        hold_rows.append(
            {
                "schema": "nobu16.kr.msgstf-pc-only-ambiguous-hold.v1",
                "resource": "msgstf",
                "id": identifier,
                "hold_key": hold["hold_key"],
                "reason": hold["reason"],
                "source_jp": tables["jp"][identifier],
                "source_jp_utf16le_sha256": text_hash(tables["jp"][identifier]),
                "current_ko": tables["ko"][identifier],
                "current_ko_utf16le_sha256": text_hash(tables["ko"][identifier]),
                "reference_contexts": {language.upper(): tables[language][identifier] for language in ("en", "sc", "tc")},
                "source_file_sha256": file_hashes["jp"],
                "current_file_sha256": file_hashes["ko"],
                "audit_scope": {
                    "switch_korean_read": False,
                    "historic_korean_read": False,
                    "steam_game_resource_written": False,
                },
            }
        )

    summary = {
        "schema": "nobu16.kr.msgstf-pc-only-full-audit-summary.v1",
        "entry_count": len(audit_rows),
        "populated_entry_count": len(POPULATED_IDS),
        "intentional_empty_entry_count": len(EMPTY_IDS),
        "new_high_confidence_candidate_count": len(candidates_by_id),
        "ambiguous_hold_count": len(hold_rows),
        "disposition_counts": dict(sorted(Counter(row["disposition"] for row in audit_rows).items())),
        "generic_translation_quality_builder_has_msgstf_resource": generic_builder_has_msgstf_resource(),
        "integration_requirement": (
            "add a common-table msgstf ResourceSpec and this private candidate JSONL to "
            "translation_quality_corrections_v1 before the candidates can be frozen"
        ),
        "switch_korean_translation_used": False,
        "historic_korean_translation_used": False,
        "game_files_written": False,
    }
    return audit_rows, [candidates_by_id[identifier] for identifier in sorted(candidates_by_id)], hold_rows, summary


def validate_rows(
    audit_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    hold_rows: list[dict[str, Any]],
    summary: Mapping[str, Any],
) -> None:
    if len(audit_rows) != ENTRY_COUNT or {row["id"] for row in audit_rows} != set(range(ENTRY_COUNT)):
        raise ValueError("full msgstf audit does not cover every 0..19 coordinate exactly once")
    if {row["id"] for row in candidate_rows} != NEW_CANDIDATE_IDS:
        raise ValueError("high-confidence msgstf candidate set differs from reviewed set")
    if len(hold_rows) != len(AMBIGUOUS_HOLDS) or {(row["id"], row["hold_key"]) for row in hold_rows} != {
        (row["id"], row["hold_key"]) for row in AMBIGUOUS_HOLDS
    }:
        raise ValueError("msgstf ambiguous hold partition differs from reviewed set")
    expected = Counter(
        {
            "candidate_high_confidence": len(NEW_CANDIDATE_IDS),
            "retained_after_pc_comparison": len(POPULATED_IDS - NEW_CANDIDATE_IDS),
            "retained_intentional_empty_slot": len(EMPTY_IDS),
        }
    )
    if Counter(row["disposition"] for row in audit_rows) != expected:
        raise ValueError("msgstf audit disposition counts differ from reviewed partition")
    for row in candidate_rows:
        if row["ko"] == row["proposed_ko"] or text_hash(row["ko"]) != row["current_hash"]:
            raise ValueError(f"msgstf:{row['id']}: candidate text/hash gate is invalid")
        if format_profile(row["ko"]) != format_profile(row["proposed_ko"]):
            raise ValueError(f"msgstf:{row['id']}: candidate format profile differs")
        if KANA_OR_HAN_RE.search(row["proposed_ko"]) or not HANGUL_RE.search(row["proposed_ko"]):
            raise ValueError(f"msgstf:{row['id']}: candidate Korean safety check fails")
        if row["switch_korean_translation_used"] or row["historic_korean_translation_used"] or row["game_files_written"]:
            raise ValueError(f"msgstf:{row['id']}: candidate audit scope is not PC-only/read-only")
    for row in audit_rows:
        scope = row["audit_scope"]
        if scope["switch_korean_read"] or scope["historic_korean_read"] or scope["steam_game_resource_written"]:
            raise ValueError("msgstf audit scope must remain PC-only and read-only")
    if summary.get("entry_count") != ENTRY_COUNT or summary.get("new_high_confidence_candidate_count") != len(NEW_CANDIDATE_IDS):
        raise ValueError("msgstf audit summary is inconsistent")


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
    summary = dict(summary)
    summary["payload_sha256"] = {key: hashlib.sha256(payload.encode("utf-8")).hexdigest().upper() for key, payload in payloads.items()}
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True))


if __name__ == "__main__":
    main()
