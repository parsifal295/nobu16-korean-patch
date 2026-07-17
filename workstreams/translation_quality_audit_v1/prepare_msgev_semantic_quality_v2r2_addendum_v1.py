#!/usr/bin/env python3
"""Build the PC-only MS GEV 9337 semantic-quality addendum.

The committed generator reads the pristine PC Japanese source and the current
PC Korean/EN/SC/TC tables only.  It never defines or opens a Switch path.
Its sole write target is the private JSONL artifact below ``tmp``; it does
not write any game resource.  The candidate is rejected if its coordinate
already appears in any other MS GEV review artifact in that private folder.
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
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
TMP_ROOT = REPO / "tmp"
SEMANTIC_ROOT = TMP_ROOT / "translation_quality_audit_v1" / "semantic"
OUTPUT = SEMANTIC_ROOT / "msgev_semantic_quality_v2r2_addendum.jsonl"
ENTRY_ID = 9337
REVIEW_BATCH = "msgev_semantic_quality_v2r2_addendum"

PC_PATHS = {
    "jp": (
        STEAM_ROOT
        / "KR_PATCH_BACKUP"
        / "file_only_transaction"
        / "steam-jp-1.1.7-v0.6.0"
        / "originals"
        / "MSG_PK"
        / "JP"
        / "msgev.bin"
    ),
    "ko": STEAM_ROOT / "MSG_PK" / "JP" / "msgev.bin",
    "en": STEAM_ROOT / "MSG_PK" / "EN" / "msgev.bin",
    "sc": STEAM_ROOT / "MSG_PK" / "SC" / "msgev.bin",
    "tc": STEAM_ROOT / "MSG_PK" / "TC" / "msgev.bin",
}
EXPECTED_FILE_HASHES = {
    "jp": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
    "ko": "B8B3B1C5A635419E590DB866C240A1B6609799E0FEA0E69F86D6208F27E5C52B",
    "en": "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E",
    "sc": "7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA",
    "tc": "89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6",
}
LAYOUT_SCRIPT = (
    REPO
    / "workstreams"
    / "steam_jp_msgev_full_layout_v2"
    / "build_steam_jp_msgev_full_layout_v2.py"
)

PROPOSED_KO = (
    "또 \x1bCA오다\x1bCZ와 같은 \x1bCA시바\x1bCZ 가신 출신인 \x1bCC에치젠\x1bCZ\n"
    "다이묘 \x1bCA아사쿠라 요시카게\x1bCZ는 \x1bCA요시아키\x1bCZ의\n"
    "곁자리를 빼앗긴 탓에 더 적대한다…"
)

ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
MALFORMED_RUNTIME_RE = re.compile(r"\[\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")
KANA_OR_HAN_RE = re.compile(
    r"[\u3041-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)


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
        if len(table) != 17916:
            raise ValueError(f"{name} coordinate count differs: {len(table)}")
        tables[name] = table
        hashes[name] = packed_hash
    return tables, hashes


@lru_cache(maxsize=1)
def layout_runtime() -> tuple[Any, Any, dict[str, int], dict[str, Any]]:
    spec = importlib.util.spec_from_file_location(
        "msgev_semantic_quality_v2r2_addendum_layout", LAYOUT_SCRIPT
    )
    if spec is None or spec.loader is None:
        raise ValueError("cannot load current MS GEV layout verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    advance, font = module.current_font(STEAM_ROOT)
    reservations, _excluded, _document = module.load_reservations()
    return module, advance, reservations, font


def profile(value: str) -> dict[str, Any]:
    escape_offsets = {
        offset
        for match in ESC_RE.finditer(value)
        for offset in range(match.start(), match.end())
    }
    return {
        "escape_tags": ESC_RE.findall(value),
        "runtime_tokens": RUNTIME_RE.findall(value),
        "malformed_runtime_open_count": len(MALFORMED_RUNTIME_RE.findall(value)),
        "printf": PRINTF_RE.findall(value),
        "newlines": LINEBREAK_RE.findall(value),
        "leading_ascii_whitespace": value[: len(value) - len(value.lstrip(" \t\r\n"))],
        "trailing_ascii_whitespace": value[len(value.rstrip(" \t\r\n")) :],
        "question_marks": value.count("?"),
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
    candidate = profile(after)
    protected = (
        "escape_tags",
        "runtime_tokens",
        "malformed_runtime_open_count",
        "printf",
        "newlines",
        "leading_ascii_whitespace",
        "trailing_ascii_whitespace",
        "question_marks",
        "non_esc_controls",
        "private_use",
    )
    mismatches = [key for key in protected if current[key] != candidate[key]]
    if mismatches:
        raise ValueError("format profile mismatch: " + ",".join(mismatches))
    if "\x00" in after or "\ufffd" in after:
        raise ValueError("unsafe NUL or replacement glyph")
    if KANA_OR_HAN_RE.search(after):
        raise ValueError("candidate retains CJK or Kana")
    hard_line_count = len(LINEBREAK_RE.split(after))
    if hard_line_count > 3:
        raise ValueError("candidate exceeds the three-line manual-break budget")
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
            "candidate": hard_line_count,
            "max": 3,
            "within_budget": True,
        },
        "source_hash_encoding": "utf-16le-sha256",
    }


def event_layout_validation(before: str, after: str) -> dict[str, Any]:
    module, advance, reservations, font = layout_runtime()
    actual, reserved = module.target_width_pairs(after, advance, reservations)
    current_tokens = RUNTIME_RE.findall(before)
    candidate_tokens = RUNTIME_RE.findall(after)
    candidate_line_count = len(LINEBREAK_RE.split(after))
    source_line_count = len(LINEBREAK_RE.split(before))
    if current_tokens != candidate_tokens:
        raise ValueError("runtime tokens differ in MS GEV candidate")
    if (
        candidate_line_count != source_line_count
        or candidate_line_count > 3
        or len(actual) != candidate_line_count
        or len(reserved) != candidate_line_count
        or any(width > 912 for width in actual)
        or any(width > 912 for width in reserved)
    ):
        raise ValueError("MS GEV candidate exceeds the current event layout budget")
    return {
        "font": font,
        "linebreak": {
            "actual_widths_px": actual,
            "allowed_delta": [],
            "candidate_line_count": candidate_line_count,
            "max_line_px": 912,
            "reserved_widths_px": reserved,
            "source_line_count": source_line_count,
            "within_three_line_budget": True,
        },
        "runtime_tokens": {
            "candidate": candidate_tokens,
            "current": current_tokens,
            "expected": current_tokens,
            "matches_expected": True,
        },
    }


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"review row is not an object: {path}:{number}")
        rows.append(row)
    return rows


def prior_msgev_coordinates() -> tuple[list[str], set[int]]:
    """Read local review metadata and reject a coordinate already reviewed."""

    artifact_names: list[str] = []
    coordinates: set[int] = set()
    for artifact in sorted(SEMANTIC_ROOT.glob("*.jsonl")):
        if artifact == OUTPUT:
            continue
        rows = load_jsonl(artifact)
        msgev_rows = [
            row
            for row in rows
            if row.get("audit_scope") == "msgev_all_17916_coordinates"
        ]
        if not msgev_rows:
            continue
        identifiers = [row.get("id") for row in msgev_rows]
        if not all(isinstance(identifier, int) for identifier in identifiers):
            raise ValueError(f"MS GEV artifact has a non-integer coordinate: {artifact.name}")
        ids = [int(identifier) for identifier in identifiers]
        if len(ids) != len(set(ids)):
            raise ValueError(f"duplicate coordinates inside {artifact.name}")
        artifact_names.append(artifact.name)
        coordinates.update(ids)
    return artifact_names, coordinates


def verify_pc_semantic_evidence(tables: dict[str, tuple[str, ...]]) -> None:
    """Pin the PC-only source evidence before emitting the paraphrase."""

    jp = tables["jp"][ENTRY_ID]
    en = tables["en"][ENTRY_ID]
    sc = tables["sc"][ENTRY_ID]
    tc = tables["tc"][ENTRY_ID]
    if not all(term in jp for term in ("神輿", "嫉視", "ことさら敵対")):
        raise ValueError("pristine PC Japanese source no longer contains expected evidence")
    if "furious" not in en.lower() or "taken from him" not in en.lower():
        raise ValueError("PC English corroboration no longer contains the lost-position relation")
    if "嫉妒" not in sc or "妒恨" not in tc:
        raise ValueError("PC Chinese corroboration no longer contains the jealousy relation")


def build() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    tables, hashes = load_inputs()
    prior_artifacts, prior_ids = prior_msgev_coordinates()
    if ENTRY_ID in prior_ids:
        raise ValueError(f"coordinate {ENTRY_ID} already exists in a prior MS GEV artifact")
    verify_pc_semantic_evidence(tables)

    source = tables["jp"][ENTRY_ID]
    current = tables["ko"][ENTRY_ID]
    formatting = format_validation(current, PROPOSED_KO)
    layout = event_layout_validation(current, PROPOSED_KO)
    rows = [
        {
            "allowed_format_delta": [],
            "audit_scope": "msgev_all_17916_coordinates",
            "confidence": "high",
            "current_hash": text_hash(current),
            "duplicate_coordinate_check": {
                "candidate_id": ENTRY_ID,
                "candidate_id_in_prior_artifacts": False,
                "prior_coordinate_union_count": len(prior_ids),
                "scanned_msgev_artifacts": prior_artifacts,
            },
            "format_validation": formatting,
            "id": ENTRY_ID,
            "issue_type": "political_figurehead_position_relation_loss",
            "jp_source": source,
            "jp_source_hash": text_hash(source),
            "ko": current,
            "pc_semantic_evidence": {
                "jp_terms": ["神輿", "嫉視", "ことさら敵対"],
                "pc_en_lost_position_relation": True,
                "pc_sc_jealousy_relation": True,
                "pc_tc_jealousy_relation": True,
            },
            "proposed_ko": PROPOSED_KO,
            "rationale": (
                "The current Korean says Yoshiaki himself was taken in resentment. "
                "Pristine PC JP presents Yoshikage's loss of the Yoshiaki political "
                "figurehead/position; PC EN corroborates the lost place at Yoshiaki's "
                "side, and PC SC/TC corroborate the jealousy and heightened hostility."
            ),
            "reference_basis": ["pristine_pc_jp", "pc_en", "pc_sc", "pc_tc"],
            "reference_file_sha256": {
                "en": hashes["en"],
                "sc": hashes["sc"],
                "tc": hashes["tc"],
            },
            "review_batch": REVIEW_BATCH,
            "source_file_sha256": hashes["jp"],
            "steam_ko_file_sha256": hashes["ko"],
            "switch_korean_translation_used": False,
            "validation": layout,
        }
    ]
    summary = {
        "candidate_count": len(rows),
        "candidate_id": ENTRY_ID,
        "game_files_written": False,
        "output": str(OUTPUT),
        "prior_coordinate_union_count": len(prior_ids),
        "prior_msgev_artifacts": prior_artifacts,
        "switch_korean_translation_used": False,
    }
    return rows, summary


def canonical_jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(
        json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    )


def safe_under_tmp(path: Path) -> Path:
    root = TMP_ROOT.resolve()
    resolved = path.resolve(strict=False)
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"output escapes tmp: {resolved}")
    return resolved


def atomic_write(path: Path, payload: str) -> None:
    path = safe_under_tmp(path)
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


def validate_existing_artifact(rows: list[dict[str, Any]]) -> str:
    if not OUTPUT.is_file():
        return "absent"
    existing = load_jsonl(OUTPUT)
    if canonical_jsonl(existing) != canonical_jsonl(rows):
        raise ValueError("existing addendum artifact differs from the generator")
    return "exact"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    rows, summary = build()
    if args.write:
        atomic_write(OUTPUT, canonical_jsonl(rows))
    artifact_match = validate_existing_artifact(rows)
    print(
        json.dumps(
            {**summary, "artifact_generator_match": artifact_match},
            ensure_ascii=True,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
