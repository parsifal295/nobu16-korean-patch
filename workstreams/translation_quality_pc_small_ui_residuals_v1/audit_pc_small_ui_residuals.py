#!/usr/bin/env python3
"""PC-only residual audit for small UI/message resources.

This audit deliberately reads only five direct PC source families:

* pristine PC JP from the file-only transaction backup (where available),
* the current Steam JP-route Korean target,
* current Steam EN, SC, and TC sibling resources.

It never reads a Switch repository, historic Korean payload, a generic overlay,
or ``F:\\Games\\NOBU16\\MSG_PK\\SC``.  A correction is emitted only when a
suspect current Korean row has an exact same-resource PC-JP source twin with
one unique, already-present Korean rendering.  This makes the result a
same-resource canonical-anchor repair rather than a newly inferred translation.

Private candidates contain commercial strings and are written beneath ``tmp``.
The workstream validation report deliberately contains hashes, counts, IDs, and
format proofs only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_ROOT = PROJECT_ROOT / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


SCHEMA = "nobu16.kr.translation-quality.pc-small-ui-residuals.v1"
VALIDATION_SCHEMA = "nobu16.kr.translation-quality.pc-small-ui-residuals.validation.v1"
WORKSTREAM = PROJECT_ROOT / "workstreams" / "translation_quality_pc_small_ui_residuals_v1"
PRIVATE_OUTPUT = PROJECT_ROOT / "tmp" / "translation_quality_pc_small_ui_residuals_v1" / "private_candidates.v1.jsonl"
VALIDATION_OUTPUT = WORKSTREAM / "validation.v1.json"

STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
BACKUP_JP_ROOT = STEAM_ROOT / "KR_PATCH_BACKUP" / "file_only_transaction" / "steam-jp-1.1.7-v0.6.0" / "originals" / "MSG_PK" / "JP"
STEAM_MSG_PK = STEAM_ROOT / "MSG_PK"

RESOURCES = ("msgui", "msgbre", "msgire", "msgstf", "msgstf_ce")
LANGUAGES = ("JP", "EN", "SC", "TC")
PRINTF_RE = re.compile(r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
ASCII_WORD_RE = re.compile(r"[A-Za-z]{4,}")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff\uff66-\uff9f]")
HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")


class AuditError(ValueError):
    pass


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256_bytes(text.encode("utf-16le"))


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def write_json(path: Path, value: Any) -> None:
    atomic_write(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    atomic_write(
        path,
        b"".join(
            json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"
            for row in rows
        ),
    )


def load_table(path: Path) -> tuple[str, list[str]]:
    if not path.is_file():
        raise AuditError(f"missing approved PC source: {path}")
    packed = path.read_bytes()
    _, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    return sha256_bytes(packed), list(table.texts)


def profile(text: str) -> dict[str, Any]:
    esc_spans = {
        position
        for match in ESC_RE.finditer(text)
        for position in range(match.start(), match.end())
    }
    controls = [
        f"U+{ord(char):04X}"
        for index, char in enumerate(text)
        if ord(char) < 0x20 and char not in ("\n", "\r", "\t") and index not in esc_spans
    ]
    return {
        "printf": [match.group(0) for match in PRINTF_RE.finditer(text)],
        "esc": ESC_RE.findall(text),
        "pua": [f"U+{ord(char):04X}" for char in text if 0xE000 <= ord(char) <= 0xF8FF],
        "other_controls": controls,
        "line_feed_count": text.count("\n"),
        "carriage_return_count": text.count("\r"),
        "tab_count": text.count("\t"),
        "leading_whitespace": bool(text[:1] and text[:1].isspace()),
        "trailing_whitespace": bool(text[-1:] and text[-1:].isspace()),
    }


def semantic_text(text: str) -> bool:
    return any(
        not char.isspace()
        and unicodedata.category(char) not in {"Cc", "Cf", "Cs", "Mn", "Me", "Zl", "Zp", "Zs", "Cn"}
        for char in text
    )


def suspicion_reasons(text: str) -> list[str]:
    """Return conservative residue signals; a canonical anchor is still required."""

    reasons: list[str] = []
    if "\ufffd" in text:
        reasons.append("replacement_character")
    if JAPANESE_RE.search(text):
        reasons.append("japanese_script")
    if HAN_RE.search(text) and not HANGUL_RE.search(text):
        reasons.append("han_only_without_hangul")
    ascii_words = ASCII_WORD_RE.findall(text)
    if ascii_words and not HANGUL_RE.search(text):
        reasons.append("ascii_word_without_hangul")
    return reasons


def current_ko_path(resource: str) -> Path:
    # The active Steam patch routes Korean text through the JP directory.
    return STEAM_MSG_PK / "JP" / f"{resource}.bin"


def pristine_jp_path(resource: str) -> tuple[Path, str]:
    candidate = BACKUP_JP_ROOT / f"{resource}.bin"
    if candidate.is_file():
        return candidate, "file_only_transaction_backup"
    if resource == "msgstf_ce":
        # This packed resource is still Japanese-only in the active Steam path;
        # no separate pristine copy exists in the named transaction backup.
        return STEAM_MSG_PK / "JP" / f"{resource}.bin", "active_steam_jp_japanese_only"
    raise AuditError(f"no pristine PC JP source for {resource}")


def build_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    resource_reports: dict[str, Any] = {}

    for resource in RESOURCES:
        jp_path, jp_origin = pristine_jp_path(resource)
        jp_file_hash, jp = load_table(jp_path)
        ko_path = current_ko_path(resource)
        ko_file_hash, ko = load_table(ko_path)
        reference: dict[str, list[str]] = {}
        reference_hashes: dict[str, str] = {}
        for language in ("EN", "SC", "TC"):
            source_hash, texts = load_table(STEAM_MSG_PK / language / f"{resource}.bin")
            reference[language] = texts
            reference_hashes[language] = source_hash
        lengths = {"JP": len(jp), "KO": len(ko), **{language: len(reference[language]) for language in reference}}
        if len(set(lengths.values())) != 1:
            raise AuditError(f"{resource} source table count mismatch: {lengths}")

        # Exact PC-JP twins may only act as an anchor if all usable current KO
        # twins agree on one semantic Korean rendering.  This blocks context
        # variants from becoming automatic translation memory.  EN/SC/TC must
        # also match at the target and anchor IDs: JP alone can share a short
        # token while the other PC language tables reveal a different slot.
        jp_to_anchor_ids: dict[str, list[int]] = defaultdict(list)
        for entry_id, (jp_text, ko_text) in enumerate(zip(jp, ko, strict=True)):
            if semantic_text(ko_text) and HANGUL_RE.search(ko_text) and not suspicion_reasons(ko_text):
                jp_to_anchor_ids[jp_text].append(entry_id)

        suspect_count = 0
        anchored_count = 0
        rejected_profile_count = 0
        rejected_ambiguity_count = 0
        rejected_cross_language_anchor_count = 0
        hold_without_canonical_anchor_count = 0
        candidates_before_sort: list[dict[str, Any]] = []
        for entry_id, (jp_text, ko_text) in enumerate(zip(jp, ko, strict=True)):
            reasons = suspicion_reasons(ko_text)
            if not reasons:
                continue
            suspect_count += 1
            anchor_ids = jp_to_anchor_ids.get(jp_text, [])
            if not anchor_ids:
                hold_without_canonical_anchor_count += 1
                continue
            anchor_ids = [
                anchor_id
                for anchor_id in anchor_ids
                if all(
                    reference[language][entry_id] == reference[language][anchor_id]
                    for language in ("EN", "SC", "TC")
                )
            ]
            if not anchor_ids:
                rejected_cross_language_anchor_count += 1
                continue
            variants = {ko[anchor_id] for anchor_id in anchor_ids}
            if len(variants) != 1:
                if variants:
                    rejected_ambiguity_count += 1
                continue
            proposed = next(iter(variants))
            anchor_ids = [anchor_id for anchor_id in anchor_ids if ko[anchor_id] == proposed]
            target_profile = profile(ko_text)
            proposed_profile = profile(proposed)
            if target_profile != proposed_profile:
                rejected_profile_count += 1
                continue
            anchored_count += 1
            candidates_before_sort.append(
                {
                    "schema": SCHEMA,
                    "resource": resource,
                    "id": entry_id,
                    "reason": sorted(reasons),
                    "anchor": {
                        "resource": resource,
                        "id": min(anchor_ids),
                        "same_pristine_pc_jp_utf16le_sha256": text_hash(jp_text),
                        "same_jp_text": True,
                        "same_steam_en_sc_tc_text": True,
                        "unique_current_korean_rendering": True,
                        "candidate_anchor_count": len(anchor_ids),
                    },
                    "pc_source_file_sha256": {
                        "pristine_jp": jp_file_hash,
                        "current_steam_ko": ko_file_hash,
                        "steam_en": reference_hashes["EN"],
                        "steam_sc": reference_hashes["SC"],
                        "steam_tc": reference_hashes["TC"],
                    },
                    "pc_source_text_utf16le_sha256": {
                        "pristine_jp": text_hash(jp_text),
                        "current_ko": text_hash(ko_text),
                        "steam_en": text_hash(reference["EN"][entry_id]),
                        "steam_sc": text_hash(reference["SC"][entry_id]),
                        "steam_tc": text_hash(reference["TC"][entry_id]),
                    },
                    "pc_anchor_text_utf16le_sha256": {
                        "pristine_jp": text_hash(jp[min(anchor_ids)]),
                        "current_ko": text_hash(ko[min(anchor_ids)]),
                        "steam_en": text_hash(reference["EN"][min(anchor_ids)]),
                        "steam_sc": text_hash(reference["SC"][min(anchor_ids)]),
                        "steam_tc": text_hash(reference["TC"][min(anchor_ids)]),
                    },
                    "current_ko": ko_text,
                    "proposed_ko": proposed,
                    "current_ko_utf16le_sha256": text_hash(ko_text),
                    "proposed_ko_utf16le_sha256": text_hash(proposed),
                    "format_profile": {
                        "current_ko": target_profile,
                        "proposed_ko": proposed_profile,
                        "exactly_preserved": True,
                    },
                }
            )

        resource_reports[resource] = {
            "count": len(jp),
            "pristine_jp_source": {
                "path": str(jp_path),
                "origin": jp_origin,
                "packed_sha256": jp_file_hash,
            },
            "current_steam_ko_source": {
                "path": str(ko_path),
                "packed_sha256": ko_file_hash,
            },
            "steam_reference_sources": {
                language: {
                    "path": str(STEAM_MSG_PK / language / f"{resource}.bin"),
                    "packed_sha256": reference_hashes[language],
                }
                for language in ("EN", "SC", "TC")
            },
            "suspect_row_count": suspect_count,
            "same_resource_exact_anchor_candidate_count": anchored_count,
            "hold_without_canonical_anchor_count": hold_without_canonical_anchor_count,
            "rejected_cross_language_anchor_count": rejected_cross_language_anchor_count,
            "rejected_ambiguous_anchor_count": rejected_ambiguity_count,
            "rejected_format_profile_count": rejected_profile_count,
        }
        rows.extend(candidates_before_sort)

    rows.sort(key=lambda row: (RESOURCES.index(str(row["resource"])), int(row["id"])))
    if len({(row["resource"], row["id"]) for row in rows}) != len(rows):
        raise AuditError("duplicate candidate coordinate")
    return rows, resource_reports


def source_free_validation(rows: list[dict[str, Any]], resource_reports: dict[str, Any]) -> dict[str, Any]:
    candidate_ids: dict[str, list[int]] = {resource: [] for resource in RESOURCES}
    candidate_hashes: dict[str, list[dict[str, Any]]] = {resource: [] for resource in RESOURCES}
    for row in rows:
        resource = str(row["resource"])
        candidate_ids[resource].append(int(row["id"]))
        candidate_hashes[resource].append(
            {
                "id": int(row["id"]),
                "anchor_id": int(row["anchor"]["id"]),
                "current_ko_utf16le_sha256": row["current_ko_utf16le_sha256"],
                "proposed_ko_utf16le_sha256": row["proposed_ko_utf16le_sha256"],
                "pristine_jp_utf16le_sha256": row["pc_source_text_utf16le_sha256"]["pristine_jp"],
                "anchor_pc_jp_utf16le_sha256": row["pc_anchor_text_utf16le_sha256"]["pristine_jp"],
                "anchor_steam_en_sc_tc_text_exact_match": bool(row["anchor"]["same_steam_en_sc_tc_text"]),
                "format_profile_exactly_preserved": bool(row["format_profile"]["exactly_preserved"]),
            }
        )
    private_payload = b"".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"
        for row in rows
    )
    return {
        "schema": VALIDATION_SCHEMA,
        "audit_scope": {
            "resources": list(RESOURCES),
            "expected_entry_counts": {
                "msgui": 5100,
                "msgbre": 3000,
                "msgire": 122,
                "msgstf": 20,
                "msgstf_ce": 20,
            },
            "total_entry_count": sum(report["count"] for report in resource_reports.values()),
        },
        "source_policy": {
            "allowed": [
                "pristine PC JP direct file",
                "current Steam JP-route Korean direct file",
                "current Steam PC EN direct file",
                "current Steam PC SC direct file",
                "current Steam PC TC direct file",
            ],
            "excluded": [
                "Switch / Switch repository",
                "historic Korean payload",
                "generic overlay",
                "I:/Workspaces/NOBU16-Korean/private-inputs/legacy-pc-root/MSG_PK/SC",
            ],
            "source_content_in_validation": False,
        },
        "resource_reports": resource_reports,
        "candidate_count": len(rows),
        "candidate_ids": candidate_ids,
        "candidate_hash_proofs": candidate_hashes,
        "private_candidate_file": {
            "path": str(PRIVATE_OUTPUT),
            "sha256": sha256_bytes(private_payload),
            "contains_commercial_text": bool(rows),
            "public_distribution_eligible": False,
        },
        "validation": {
            "all_expected_resource_counts_match": {
                resource: resource_reports[resource]["count"] == expected
                for resource, expected in {
                    "msgui": 5100,
                    "msgbre": 3000,
                    "msgire": 122,
                    "msgstf": 20,
                    "msgstf_ce": 20,
                }.items()
            },
            "candidate_coordinates_unique": True,
            "same_resource_exact_pc_jp_anchor_required": True,
            "anchor_steam_en_sc_tc_text_exact_match_required": True,
            "unique_current_korean_anchor_required": True,
            "candidate_format_profiles_exactly_preserved": all(
                bool(row["format_profile"]["exactly_preserved"]) for row in rows
            ),
            "installed_game_files_modified": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write private candidates and source-free validation")
    parser.add_argument("--validate", action="store_true", help="recompute and verify deterministic audit results")
    args = parser.parse_args()
    if not args.write and not args.validate:
        parser.error("at least one of --write or --validate is required")

    rows, reports = build_rows()
    validation = source_free_validation(rows, reports)
    expected_counts = validation["audit_scope"]["expected_entry_counts"]
    if validation["audit_scope"]["total_entry_count"] != sum(expected_counts.values()):
        raise AuditError("total coverage does not match required scope")
    if not all(validation["validation"]["all_expected_resource_counts_match"].values()):
        raise AuditError("one or more source tables do not match required scope")

    if args.write:
        write_jsonl(PRIVATE_OUTPUT, rows)
        write_json(VALIDATION_OUTPUT, validation)
    if args.validate:
        if not PRIVATE_OUTPUT.is_file() or not VALIDATION_OUTPUT.is_file():
            raise AuditError("--validate requires prior --write outputs")
        expected_private = b"".join(
            json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"
            for row in rows
        )
        if PRIVATE_OUTPUT.read_bytes() != expected_private:
            raise AuditError("private candidate output is stale or non-deterministic")
        expected_validation = (json.dumps(validation, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        if VALIDATION_OUTPUT.read_bytes() != expected_validation:
            raise AuditError("source-free validation output is stale or non-deterministic")

    print(f"coverage={validation['audit_scope']['total_entry_count']}")
    print(f"candidates={len(rows)}")
    print(f"private_candidates={PRIVATE_OUTPUT}")
    print(f"validation={VALIDATION_OUTPUT}")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
