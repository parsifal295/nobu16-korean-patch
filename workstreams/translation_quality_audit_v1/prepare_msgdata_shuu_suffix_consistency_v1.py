#!/usr/bin/env python3
"""Audit and prepare safe PC-only ``○○衆`` suffix-consistency candidates.

Only the pristine PC Japanese source and the current PC JP/EN/SC/TC tables
are loaded.  Switch resources and historic Korean backups are neither defined
nor opened.  Existing private artifacts are consulted only for their outer
coordinate IDs so a duplicate proposal is never emitted.
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


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
TMP_ROOT = REPO / "tmp"
SEMANTIC_ROOT = TMP_ROOT / "translation_quality_audit_v1" / "semantic"
PROPOSAL_ROOT = TMP_ROOT / "translation_quality_audit_v1" / "proposals"
CANDIDATE_ARTIFACT = SEMANTIC_ROOT / "msgdata_shuu_suffix_consistency_candidates.v1.jsonl"
HOLD_ARTIFACT = SEMANTIC_ROOT / "msgdata_shuu_suffix_consistency_holds.v1.jsonl"

PC_PATHS = {
    "jp": (
        STEAM_ROOT
        / "KR_PATCH_BACKUP"
        / "file_only_transaction"
        / "steam-jp-1.1.7-v0.6.0"
        / "originals"
        / "MSG_PK"
        / "JP"
        / "msgdata.bin"
    ),
    "ko": STEAM_ROOT / "MSG_PK" / "JP" / "msgdata.bin",
    "en": STEAM_ROOT / "MSG_PK" / "EN" / "msgdata.bin",
    "sc": STEAM_ROOT / "MSG_PK" / "SC" / "msgdata.bin",
    "tc": STEAM_ROOT / "MSG_PK" / "TC" / "msgdata.bin",
}
EXPECTED_FILE_HASHES = {
    "jp": "13498FBFFF6D33F0BFB0915B6F365F076FE8E78046EE411BB8478235C86C2C9E",
    "ko": "7EAA33BC80C021A028660DF1A7934886591A1DA36DB7BC53146749C3A4AEF040",
    "en": "BDE25DFD7265C5B6E765F2FA2A8F800E171C6C2B23FB8A66F05AE239BF71E033",
    "sc": "A3A0260B74191D4676C43403B587BB4EC676A7D96E56725844F24C8107B1604E",
    "tc": "E266A9C43AAE09BEEA739812AD8E3E8DDDBC4710EF5A81E174A9D215D6B03676",
}

# Keep the source/target suffixes codepoint-defined so the classification is
# independent of the shell code page used to run this helper.
JP_SHUU = chr(0x8846)
KO_JUNG = chr(0xC911)
KO_SHUU = chr(0xC288)
TERM_RE = re.compile(r"([\u3400-\u9fff\u3005\u30f6]+" + JP_SHUU + r")")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")
KANA_OR_HAN_RE = re.compile(
    r"[\u3041-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)

EXPECTED_CANDIDATE_GROUP_COUNT = 142
EXPECTED_CANDIDATE_ID_COUNT = 144
EXPECTED_HOLD_COUNT = 28


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def load_table(path: Path) -> tuple[str, tuple[str, ...]]:
    sys.path.insert(0, str(REPO / "tools"))
    from nobu16_lz4 import decompress_wrapper
    from nobu16_msg_table import parse_message_table

    packed = path.read_bytes()
    _header, raw = decompress_wrapper(packed)
    return sha256_bytes(packed), parse_message_table(raw).texts


def load_inputs() -> tuple[dict[str, tuple[str, ...]], dict[str, str]]:
    tables: dict[str, tuple[str, ...]] = {}
    hashes: dict[str, str] = {}
    for name, path in PC_PATHS.items():
        packed_hash, table = load_table(path)
        if packed_hash != EXPECTED_FILE_HASHES[name]:
            raise ValueError(f"{name} packed SHA-256 differs: {packed_hash}")
        if len(table) != 29218:
            raise ValueError(f"{name} coordinate count differs: {len(table)}")
        tables[name] = table
        hashes[name] = packed_hash
    return tables, hashes


def profile(value: str) -> dict[str, Any]:
    escape_offsets = {
        offset
        for match in ESC_RE.finditer(value)
        for offset in range(match.start(), match.end())
    }
    return {
        "escape_tags": ESC_RE.findall(value),
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf": PRINTF_RE.findall(value),
        "newlines": LINEBREAK_RE.findall(value),
        "outer_ascii_whitespace": [
            value[: len(value) - len(value.lstrip(" \t\r\n"))],
            value[len(value.rstrip(" \t\r\n")) :],
        ],
        "question_mark_count": value.count("?"),
        "non_esc_controls": [
            f"U+{ord(char):04X}"
            for offset, char in enumerate(value)
            if unicodedata.category(char) == "Cc"
            and char not in ("\r", "\n")
            and offset not in escape_offsets
        ],
        "private_use": [f"U+{ord(char):04X}" for char in value if 0xE000 <= ord(char) <= 0xF8FF],
    }


def format_validation(before: str, after: str) -> dict[str, Any]:
    current = profile(before)
    proposed = profile(after)
    required = (
        "escape_tags",
        "runtime_tokens",
        "printf",
        "newlines",
        "outer_ascii_whitespace",
        "question_mark_count",
        "non_esc_controls",
        "private_use",
    )
    mismatches = [key for key in required if current[key] != proposed[key]]
    if mismatches:
        raise ValueError("format profile mismatch: " + ",".join(mismatches))
    if "\x00" in after or "\ufffd" in after:
        raise ValueError("unsafe NUL or replacement glyph")
    if KANA_OR_HAN_RE.search(after):
        raise ValueError("candidate retains Japanese/CJK residue")
    return {
        "escape_tags": "match",
        "runtime_tokens": "match",
        "printf": "match",
        "newlines": "match",
        "outer_ascii_whitespace": "match",
        "question_marks": "unchanged",
        "non_esc_controls": "match",
        "private_use": "match",
        "hard_line_count": {
            "current": len(LINEBREAK_RE.split(before)),
            "candidate": len(LINEBREAK_RE.split(after)),
            "max": 3,
            "within_budget": len(LINEBREAK_RE.split(after)) <= 3,
        },
        "source_hash_encoding": "utf-16le-sha256",
    }


def active_artifact_ids() -> tuple[list[str], set[int]]:
    """Read only outer coordinate IDs from active msgdata artifacts.

    Prior Korean strings are deliberately not used as linguistic evidence.  The
    artifact scan exists solely to prevent coordinate overlap.
    """

    names: list[str] = []
    identifiers: set[int] = set()
    paths = [*sorted(PROPOSAL_ROOT.glob("msgdata*.jsonl")), *sorted(SEMANTIC_ROOT.glob("msgdata*.jsonl"))]
    excluded = {CANDIDATE_ARTIFACT.resolve(), HOLD_ARTIFACT.resolve()}
    for path in paths:
        if path.resolve() in excluded:
            continue
        per_file: set[int] = set()
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            identifier = row.get("id")
            # Summary/hold rows can deliberately describe a range rather than
            # propose one coordinate.  They do not create an overlap target.
            if not isinstance(identifier, int):
                continue
            if identifier in per_file:
                raise ValueError(f"duplicate id in active artifact: {path.name}:{identifier}")
            per_file.add(identifier)
        names.append(path.name)
        identifiers.update(per_file)
    return names, identifiers


def source_term_groups(jp_table: tuple[str, ...]) -> dict[str, list[int]]:
    groups: dict[str, list[int]] = defaultdict(list)
    for identifier, source in enumerate(jp_table):
        for term in set(TERM_RE.findall(source)):
            groups[term].append(identifier)
    return dict(groups)


def compact_pc_context(tables: dict[str, tuple[str, ...]], identifier: int) -> dict[str, str]:
    return {language: tables[language][identifier] for language in ("en", "sc", "tc")}


def hold_reason_text(reason: str) -> str:
    messages = {
        "reading_prefix_diverges": (
            "The exact Japanese label has both -중 and -슈 forms, but the stem "
            "reading differs too; changing only the suffix would silently choose a "
            "reading without enough evidence."
        ),
        "pc_reference_context_diverges": (
            "At least one PC EN/SC/TC counterpart differs across the otherwise same "
            "Japanese label, so a cross-role normalization is not high confidence."
        ),
        "not_standalone_label": (
            "The matched token is embedded in a longer source string/name, so it is "
            "not a safe duplicate UI-label pair."
        ),
        "multiple_or_asymmetric_prefixes": (
            "More than one Korean reading stem participates in the pair, so a single "
            "suffix normalization would conflate unresolved readings."
        ),
        "existing_active_artifact_overlap": (
            "At least one coordinate is already proposed by an active msgdata artifact."
        ),
    }
    return messages[reason]


def build() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    tables, hashes = load_inputs()
    artifact_names, active_ids = active_artifact_ids()
    candidates: list[dict[str, Any]] = []
    holds: list[dict[str, Any]] = []
    candidate_group_count = 0

    for term, ids in sorted(source_term_groups(tables["jp"]).items()):
        middle_ids: dict[str, list[int]] = defaultdict(list)
        shuu_ids: dict[str, list[int]] = defaultdict(list)
        for identifier in ids:
            current = tables["ko"][identifier]
            if current.endswith(KO_JUNG):
                middle_ids[current[: -len(KO_JUNG)]].append(identifier)
            if current.endswith(KO_SHUU):
                shuu_ids[current[: -len(KO_SHUU)]].append(identifier)

        # Only groups that visibly mix the target suffixes need a decision.
        if not middle_ids or not shuu_ids:
            continue
        if any(tables["jp"][identifier] != term for identifier in ids):
            reason = "not_standalone_label"
        else:
            common_stems = sorted(set(middle_ids).intersection(shuu_ids))
            if not common_stems:
                reason = "reading_prefix_diverges"
            elif set(middle_ids) != set(shuu_ids) or len(common_stems) != 1:
                reason = "multiple_or_asymmetric_prefixes"
            elif any(
                any(tables[language][identifier] != tables[language][ids[0]] for language in ("jp", "en", "sc", "tc"))
                for identifier in ids
            ):
                reason = "pc_reference_context_diverges"
            else:
                stem = common_stems[0]
                change_ids = sorted(shuu_ids[stem])
                overlap = sorted(set(change_ids).intersection(active_ids))
                if overlap:
                    reason = "existing_active_artifact_overlap"
                else:
                    canonical = stem + KO_JUNG
                    source_context = compact_pc_context(tables, ids[0])
                    canonical_ids = sorted(middle_ids[stem])
                    for identifier in change_ids:
                        current = tables["ko"][identifier]
                        validation = format_validation(current, canonical)
                        candidates.append(
                            {
                                "allowed_format_delta": [],
                                "audit_scope": "msgdata_all_29218_coordinates",
                                "canonical_jung_coordinates": canonical_ids,
                                "confidence": "high",
                                "current_hash": text_hash(current),
                                "duplicate_coordinate_check": {
                                    "active_artifact_coordinate_union_count": len(active_ids),
                                    "candidate_id_in_active_artifacts": False,
                                    "scanned_active_artifacts": artifact_names,
                                },
                                "format_validation": validation,
                                "historic_korean_backup_used": False,
                                "id": identifier,
                                "issue_type": "duplicate_shuu_suffix_inconsistency",
                                "jp_source": term,
                                "jp_source_hash": text_hash(term),
                                "ko": current,
                                "pc_reference_contexts": source_context,
                                "proposed_ko": canonical,
                                "rationale": (
                                    "The exact standalone PC-JP label is duplicated with an "
                                    "identical Korean stem ending in -중 and -슈. PC EN renders "
                                    "the group as Tribe and PC SC/TC retain 衆/眾; this coordinate "
                                    "therefore changes only the inconsistent Japanese-reading suffix."
                                ),
                                "reference_basis": ["pristine_pc_jp", "pc_en", "pc_sc", "pc_tc"],
                                "reference_file_sha256": {
                                    "en": hashes["en"],
                                    "sc": hashes["sc"],
                                    "tc": hashes["tc"],
                                },
                                "review_batch": "msgdata_shuu_suffix_consistency_v1",
                                "source_file_sha256": hashes["jp"],
                                "steam_ko_file_sha256": hashes["ko"],
                                "switch_korean_translation_used": False,
                            }
                        )
                    candidate_group_count += 1
                    continue

        holds.append(
            {
                "audit_scope": "msgdata_all_29218_coordinates",
                "current_ko_by_coordinate": {str(identifier): tables["ko"][identifier] for identifier in sorted(ids)},
                "hold_reason": reason,
                "id": sorted(ids),
                "jp_source_term": term,
                "pc_reference_contexts_by_coordinate": {
                    str(identifier): compact_pc_context(tables, identifier) for identifier in sorted(ids)
                },
                "rationale": hold_reason_text(reason),
                "reference_basis": ["pristine_pc_jp", "pc_en", "pc_sc", "pc_tc"],
                "reference_file_sha256": {"en": hashes["en"], "sc": hashes["sc"], "tc": hashes["tc"]},
                "source_file_sha256": hashes["jp"],
                "steam_ko_file_sha256": hashes["ko"],
                "status": "hold",
                "switch_korean_translation_used": False,
            }
        )

    candidates.sort(key=lambda row: int(row["id"]))
    holds.sort(key=lambda row: (str(row["hold_reason"]), str(row["jp_source_term"])))
    if candidate_group_count != EXPECTED_CANDIDATE_GROUP_COUNT:
        raise ValueError(f"candidate group count drift: {candidate_group_count}")
    if len(candidates) != EXPECTED_CANDIDATE_ID_COUNT:
        raise ValueError(f"candidate ID count drift: {len(candidates)}")
    if len(holds) != EXPECTED_HOLD_COUNT:
        raise ValueError(f"hold count drift: {len(holds)}")
    if len({int(row["id"]) for row in candidates}) != len(candidates):
        raise ValueError("duplicate candidate IDs")

    summary = {
        "active_artifact_coordinate_union_count": len(active_ids),
        "active_artifacts": artifact_names,
        "candidate_group_count": candidate_group_count,
        "candidate_id_count": len(candidates),
        "game_files_written": False,
        "hold_count": len(holds),
        "hold_reason_counts": dict(sorted(Counter(str(row["hold_reason"]) for row in holds).items())),
        "historic_korean_backup_used": False,
        "resource": "MSG_PK/JP/msgdata.bin",
        "switch_korean_translation_used": False,
    }
    return candidates, holds, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=("candidates", "holds", "summary"), required=True)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    if args.offset < 0 or args.limit is not None and args.limit < 0:
        raise ValueError("offset and limit must be non-negative")
    candidates, holds, summary = build()
    if args.kind == "summary":
        print("@@SUMMARY@@" + json.dumps(summary, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
        return 0
    print("@@JSONL@@")
    rows = candidates if args.kind == "candidates" else holds
    rows = rows[args.offset : None if args.limit is None else args.offset + args.limit]
    for row in rows:
        print(json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
