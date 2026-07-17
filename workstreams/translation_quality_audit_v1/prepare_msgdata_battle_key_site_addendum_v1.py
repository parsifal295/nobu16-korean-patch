#!/usr/bin/env python3
"""Prepare PC-only static ``msgdata`` battlefield key-site corrections.

The Japanese battle-objective term ``\u8981\u6240`` is still rendered as the
generic Korean word ``\uc694\uc18c`` in a small set of visible PK labels and battle
effect descriptions.  For a capturable objective the established Korean term
is ``\uc694\ucda9\uc9c0``.  This helper scans the complete PC table, excludes its
one dummy/unverified record, and emits only the ten direct PC JP/SC/TC-backed
static entries.  It neither reads Switch Korean nor writes a game resource.
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
PRISTINE_JP = (
    STEAM
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / "MSG_PK"
    / "JP"
    / "msgdata.bin"
)
LIVE_KO = STEAM / "MSG_PK" / "JP" / "msgdata.bin"
REFERENCES = {
    language.lower(): STEAM / "MSG_PK" / language / "msgdata.bin"
    for language in ("EN", "SC", "TC")
}
EXPECTED_FILE_SHA256 = {
    "jp": "13498FBFFF6D33F0BFB0915B6F365F076FE8E78046EE411BB8478235C86C2C9E",
    "ko": "7EAA33BC80C021A028660DF1A7934886591A1DA36DB7BC53146749C3A4AEF040",
    "en": "BDE25DFD7265C5B6E765F2FA2A8F800E171C6C2B23FB8A66F05AE239BF71E033",
    "sc": "A3A0260B74191D4676C43403B587BB4EC676A7D96E56725844F24C8107B1604E",
    "tc": "E266A9C43AAE09BEEA739812AD8E3E8DDDBC4710EF5A81E174A9D215D6B03676",
}
AUDIT_ROOT = REPO / "tmp" / "translation_quality_audit_v1"
OUTPUT = AUDIT_ROOT / "semantic" / "msgdata_battle_key_site_addendum.v1.jsonl"

sys.path.insert(0, str(REPO / "tools"))
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


JP_KEY_SITE = "\u8981\u6240"
KO_GENERIC_ELEMENT = "\uc694\uc18c"
KO_BATTLE_KEY_SITE = "\uc694\ucda9\uc9c0"
CHINESE_KEY_SITE_TERMS = ("\u8981\u5730", "\u8981\u6240")

# The full direct PC scan has eleven matches.  15174 is an EN/SC/TC ``dumm``
# placeholder, so it has no trustworthy visible battle-objective meaning and
# remains HOLD rather than being inferred from Japanese alone.
CANDIDATE_IDS = (
    20797,
    20845,
    20847,
    20866,
    20867,
    24952,
    24958,
    24973,
    25019,
    25199,
)
UNVERIFIED_DUMMY_HOLD_IDS = (15174,)

ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
PRIVATE_USE_RE = re.compile(r"[\ue000-\uf8ff]")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def profile(text: str) -> dict[str, object]:
    return {
        "escape_tags": ESC_RE.findall(text),
        "runtime_tokens": RUNTIME_RE.findall(text),
        "printf": PRINTF_RE.findall(text),
        "newlines": re.findall(r"\r\n|\n|\r", text),
        "outer_ascii_whitespace": (
            text[: len(text) - len(text.lstrip(" \t"))],
            text[len(text.rstrip(" \t")) :],
        ),
        "private_use": PRIVATE_USE_RE.findall(text),
        "fullwidth_percent_count": text.count("\uff05"),
        "question_mark_count": text.count("?"),
    }


def _load_table(path: Path) -> tuple[bytes, bytes, Any]:
    packed = path.read_bytes()
    _header, raw = decompress_wrapper(packed)
    return packed, raw, parse_message_table(raw)


def _load_inputs() -> tuple[dict[str, tuple[bytes, bytes, Any]], dict[str, str]]:
    paths = {"jp": PRISTINE_JP, "ko": LIVE_KO, **REFERENCES}
    hashes = {name: sha256_bytes(path.read_bytes()) for name, path in paths.items()}
    if hashes != EXPECTED_FILE_SHA256:
        raise ValueError(f"PC msgdata input file hash drift: {hashes!r}")
    tables = {name: _load_table(path) for name, path in paths.items()}
    counts = {name: table.string_count for name, (_packed, _raw, table) in tables.items()}
    if len(set(counts.values())) != 1:
        raise ValueError(f"PC msgdata table cardinalities differ: {counts!r}")
    for name, (_packed, raw, table) in tables.items():
        if rebuild_message_table(table, table.texts) != raw:
            raise ValueError(f"{name}: unchanged PC msgdata rebuild is not byte-identical")
    return tables, hashes


def _resource_is_msgdata_candidate(path: Path, row: dict[str, object]) -> bool:
    return path.name.startswith("msgdata") or row.get("resource") == "msgdata"


def read_prior_ids() -> set[int]:
    result: set[int] = set()
    for directory in (AUDIT_ROOT / "semantic", AUDIT_ROOT / "proposals"):
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.jsonl")):
            if path.resolve() == OUTPUT.resolve():
                continue
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError(f"invalid review row: {path}:{line_number}")
                if not _resource_is_msgdata_candidate(path, row):
                    continue
                identifier = row.get("id")
                if isinstance(identifier, int):
                    result.add(identifier)
    return result


def _reference_status(text: str) -> str:
    if not text:
        raise ValueError("static candidate has an empty Chinese reference")
    if not any(term in text for term in CHINESE_KEY_SITE_TERMS):
        raise ValueError("PC Chinese reference lacks the named battle key-site context")
    return "named_key_site_visible"


def _validate_full_overlay(
    packed_source: bytes,
    source_table: Any,
    replacements: dict[int, str],
) -> dict[str, object]:
    """Rebuild/repack the complete table and prove only allowlisted IDs change."""
    _header, raw = decompress_wrapper(packed_source)
    table = parse_message_table(raw)
    if table.texts != source_table.texts:
        raise ValueError("full-overlay source table differs from initial parse")
    after_texts = list(table.texts)
    for identifier, proposal in replacements.items():
        after_texts[identifier] = proposal
    rebuilt_raw = rebuild_message_table(table, after_texts)
    reparsed = parse_message_table(rebuilt_raw)
    if reparsed.texts != tuple(after_texts):
        raise ValueError("full-overlay raw rebuild parse verification failed")
    if raw[:8] != rebuilt_raw[:8]:
        raise ValueError("full-overlay changed opaque message-table prefix")
    if raw[12 : table.table_offset] != rebuilt_raw[12 : reparsed.table_offset]:
        raise ValueError("full-overlay changed opaque message-table metadata")
    changed = [
        identifier
        for identifier, (before, after) in enumerate(zip(table.texts, reparsed.texts))
        if before != after
    ]
    expected = sorted(replacements)
    if changed != expected:
        raise ValueError(f"full-overlay changed unexpected msgdata IDs: {changed!r}")
    packed_rebuilt = recompress_wrapper(rebuilt_raw, packed_source)
    _repacked_header, decoded = decompress_wrapper(packed_rebuilt)
    if decoded != rebuilt_raw:
        raise ValueError("full-overlay wrapper round-trip mismatch")
    repacked_table = parse_message_table(decoded)
    if repacked_table.texts != tuple(after_texts):
        raise ValueError("full-overlay repacked parse verification failed")
    return {
        "source_packed_sha256": sha256_bytes(packed_source),
        "rebuilt_raw_sha256": sha256_bytes(rebuilt_raw),
        "rebuilt_packed_sha256": sha256_bytes(packed_rebuilt),
        "changed_ids": changed,
        "unchanged_non_target_texts": True,
        "opaque_table_metadata": "unchanged_except_recalculated_logical_size_and_offsets",
        "wrapper_roundtrip": "pass",
    }


def build_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    candidates = set(CANDIDATE_IDS)
    holds = set(UNVERIFIED_DUMMY_HOLD_IDS)
    if len(candidates) != len(CANDIDATE_IDS) or len(holds) != len(UNVERIFIED_DUMMY_HOLD_IDS):
        raise ValueError("duplicate candidate or hold ID")
    if candidates.intersection(holds):
        raise ValueError("candidate and hold ID partitions overlap")
    prior_overlap = sorted(candidates.intersection(read_prior_ids()))
    if prior_overlap:
        raise ValueError(f"candidate IDs overlap prior msgdata artifacts: {prior_overlap}")

    tables, hashes = _load_inputs()
    texts = {name: table.texts for name, (_packed, _raw, table) in tables.items()}
    full_residuals = {
        identifier
        for identifier, (source, current) in enumerate(zip(texts["jp"], texts["ko"]))
        if JP_KEY_SITE in source and KO_GENERIC_ELEMENT in current
    }
    expected_residuals = candidates.union(holds)
    if full_residuals != expected_residuals:
        raise ValueError(
            "msgdata direct key-site residual inventory drifted: "
            f"missing={sorted(expected_residuals - full_residuals)!r}, "
            f"unexpected={sorted(full_residuals - expected_residuals)!r}"
        )

    rows: list[dict[str, object]] = []
    replacements: dict[int, str] = {}
    for identifier in sorted(candidates):
        source = texts["jp"][identifier]
        current = texts["ko"][identifier]
        if source.count(JP_KEY_SITE) != current.count(KO_GENERIC_ELEMENT):
            raise ValueError(f"{identifier}: source/target key-site occurrence count differs")
        if RUNTIME_RE.search(current) or PRINTF_RE.search(current):
            raise ValueError(f"{identifier}: target must remain a static text-table entry")
        proposal = current.replace(KO_GENERIC_ELEMENT, KO_BATTLE_KEY_SITE)
        if proposal == current:
            raise ValueError(f"{identifier}: no generic Korean element term to replace")
        if profile(current) != profile(proposal):
            raise ValueError(f"{identifier}: format profile changed")
        reference_status = {
            language: _reference_status(texts[language][identifier])
            for language in ("sc", "tc")
        }
        rows.append(
            {
                "id": identifier,
                "ko": current,
                "proposed_ko": proposal,
                "issue_type": "battle_key_site_generic_element_mistranslation",
                "rationale": (
                    "The direct Japanese source names the battlefield objective '\u8981\u6240'. "
                    "PC SC/TC render the same static label/effect as '\u8981\u5730'.  Korean '\uc694\uc18c' "
                    "means a generic element, so use the established battlefield objective term '\uc694\ucda9\uc9c0'."
                ),
                "source_text": source,
                "source_text_hash": sha256_text(source),
                "current_hash": sha256_text(current),
                "proposed_hash": sha256_text(proposal),
                "source_file_sha256": hashes["ko"],
                "native_jp_file_sha256": hashes["jp"],
                "reference_file_sha256": {
                    language: hashes[language]
                    for language in ("en", "sc", "tc")
                },
                "pc_target_contexts": {
                    language: texts[language][identifier]
                    for language in ("en", "sc", "tc")
                },
                "pc_sc_tc_key_site_crosscheck": reference_status,
                "format_profile": {
                    "current_ko": profile(current),
                    "proposed_ko": profile(proposal),
                    "pristine_jp": profile(source),
                },
                "format_validation": {
                    "escape_tags": "match",
                    "runtime_tokens": "match",
                    "printf": "match",
                    "newlines": "match",
                    "outer_ascii_whitespace": "match",
                    "private_use": "match",
                    "fullwidth_percent_count": "match",
                    "question_marks": "unchanged",
                },
            }
        )
        replacements[identifier] = proposal

    overlay = _validate_full_overlay(tables["ko"][0], tables["ko"][2], replacements)
    return rows, {
        "existing_id_overlap": prior_overlap,
        "full_residual_scan": {
            "direct_jp_key_site_to_ko_generic_element_count": len(full_residuals),
            "static_candidate_count": len(candidates),
            "unverified_dummy_hold_count": len(holds),
            "unverified_dummy_hold_ids": sorted(holds),
            "unexpected_residual_ids": [],
        },
        "full_overlay_validation": overlay,
    }


def _atomic_write(path: Path, payload: str) -> None:
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--id", type=int)
    args = parser.parse_args()
    if sum(bool(value) for value in (args.validate, args.write, args.id is not None)) > 1:
        parser.error("choose at most one output mode")

    rows, validation = build_rows()
    if args.id is not None:
        for row in rows:
            if row["id"] == args.id:
                print(json.dumps(row, ensure_ascii=True, separators=(",", ":")))
                return 0
        raise SystemExit("ID not found")
    if args.validate:
        print(
            json.dumps(
                {
                    "row_count": len(rows),
                    "ids": [row["id"] for row in rows],
                    "candidate_contract": "whole_table_rebuild_repack_and_non_target_text_invariance",
                    "source_policy": "stock_pc_jp_plus_live_pc_en_sc_tc_only",
                    "switch_korean_read": False,
                    "json_encoding": "ensure_ascii_true_utf8",
                    **validation,
                },
                ensure_ascii=True,
                sort_keys=True,
            )
        )
        return 0
    if args.write:
        payload = "".join(
            json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n"
            for row in rows
        )
        if any(byte > 0x7F for byte in payload.encode("utf-8")):
            raise ValueError("JSONL payload is not ASCII-only")
        if OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == payload:
            status = "already_current"
        else:
            _atomic_write(OUTPUT, payload)
            status = "written"
        print(
            json.dumps(
                {
                    "output": str(OUTPUT),
                    "row_count": len(rows),
                    "sha256": sha256_bytes(payload.encode("utf-8")),
                    "status": status,
                },
                ensure_ascii=True,
                sort_keys=True,
            )
        )
        return 0
    for row in rows:
        print(json.dumps(row, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
