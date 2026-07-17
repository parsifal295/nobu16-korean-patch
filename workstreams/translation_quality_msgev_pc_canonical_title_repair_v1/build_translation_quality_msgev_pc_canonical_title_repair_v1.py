#!/usr/bin/env python3
"""Read-only proof builder for the PC-only msgev canonical-title repairs.

The Japanese title key at each candidate coordinate is phonetic; its reviewed
canonical Japanese title is at a different coordinate in the same pristine PC
resource.  The replacement is copied exactly from that canonical title's
current Steam-PC Korean anchor.  No Switch or older Korean payload is read.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


WORKSPACE = Path(__file__).resolve().parents[2]
STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PRISTINE_JP = (
    STEAM_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)
CURRENT_PC_KO = STEAM_ROOT / "MSG_PK" / "JP" / "msgev.bin"
PC_REFERENCE_FILES = {
    "en": STEAM_ROOT / "MSG_PK" / "EN" / "msgev.bin",
    "sc": STEAM_ROOT / "MSG_PK" / "SC" / "msgev.bin",
    "tc": STEAM_ROOT / "MSG_PK" / "TC" / "msgev.bin",
}

EXPECTED_FILE_SHA256 = {
    "pristine_jp": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
    "current_ko": "B8B3B1C5A635419E590DB866C240A1B6609799E0FEA0E69F86D6208F27E5C52B",
    "en": "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E",
    "sc": "7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA",
    "tc": "89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6",
}
EXPECTED_STRING_COUNT = 17916
SUPERSEDED_TEMPORARY_ID = 14638


def _expected_anchor_map() -> dict[int, int]:
    mapping: dict[int, int] = {}

    def add_range(first: int, last: int, anchor_first: int) -> None:
        for entry_id in range(first, last + 1):
            mapping[entry_id] = anchor_first + entry_id - first

    add_range(14550, 14558, 13751)
    add_range(14559, 14563, 13760)
    add_range(14566, 14570, 13767)
    add_range(14573, 14578, 13774)
    add_range(14580, 14583, 13781)
    add_range(14584, 14595, 13785)
    mapping[14597] = 13798
    mapping[14598] = 13799
    add_range(14600, 14603, 13801)
    add_range(14604, 14606, 13805)
    add_range(14630, 14637, 13831)
    add_range(14638, 14641, 13839)
    if len(mapping) != 62 or mapping[14638] != 13839:
        raise AssertionError("canonical title map construction drifted")
    return mapping


def _load_module(module_name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


LZ4 = _load_module("nobu16_lz4_for_canonical_title_repair", WORKSPACE / "tools" / "nobu16_lz4.py")
MSG = _load_module(
    "nobu16_msg_table_for_canonical_title_repair", WORKSPACE / "tools" / "nobu16_msg_table.py"
)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def _sha256_text(value: str) -> str:
    return _sha256_bytes(value.encode("utf-16le"))


def _table(path: Path) -> Any:
    _header, raw = LZ4.decompress_wrapper(path.read_bytes())
    return MSG.parse_message_table(raw)


def _contains_hangul(value: str) -> bool:
    return any("\uac00" <= char <= "\ud7a3" for char in value)


def _protected_signature(value: str) -> tuple[tuple[str, ...], ...]:
    return (
        tuple(re.findall(r"\x1bC.", value)),
        tuple(re.findall(r"<[^>]*>", value)),
        tuple(re.findall(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]", value)),
        tuple(re.findall(r"\[[A-Za-z]+\d+\]", value)),
    )


def _private_candidates() -> list[dict[str, object]]:
    path = Path(__file__).with_name("private_candidates.v1.jsonl")
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    expected = _expected_anchor_map()
    if len(rows) != len(expected):
        raise AssertionError(f"private candidate count={len(rows)}, expected={len(expected)}")
    seen: set[int] = set()
    for row in rows:
        required = {
            "id",
            "canonical_anchor_id",
            "candidate_jp_utf16le_sha256",
            "current_ko_utf16le_sha256",
            "canonical_jp_utf16le_sha256",
            "translation",
            "translation_utf16le_sha256",
            "proof",
        }
        if set(row) != required:
            raise AssertionError(f"private candidate fields drifted: {sorted(row)}")
        entry_id = row["id"]
        anchor_id = row["canonical_anchor_id"]
        if not isinstance(entry_id, int) or not isinstance(anchor_id, int):
            raise AssertionError("candidate identifiers must be integers")
        if entry_id in seen or expected.get(entry_id) != anchor_id:
            raise AssertionError("private canonical anchor map drifted")
        seen.add(entry_id)
    return rows


def validate() -> dict[str, object]:
    paths = {"pristine_jp": PRISTINE_JP, "current_ko": CURRENT_PC_KO, **PC_REFERENCE_FILES}
    for label, path in paths.items():
        actual = _sha256_bytes(path.read_bytes())
        if actual != EXPECTED_FILE_SHA256[label]:
            raise AssertionError(f"{label} SHA-256 changed: {actual}")

    jp = _table(PRISTINE_JP)
    ko = _table(CURRENT_PC_KO)
    references = {label: _table(path) for label, path in PC_REFERENCE_FILES.items()}
    if jp.string_count != ko.string_count or jp.string_count != EXPECTED_STRING_COUNT:
        raise AssertionError("JP/KO string count mismatch")
    if any(table.string_count != EXPECTED_STRING_COUNT for table in references.values()):
        raise AssertionError("PC EN/SC/TC string count mismatch")

    rows = _private_candidates()
    candidate_ids = {row["id"] for row in rows}
    if SUPERSEDED_TEMPORARY_ID not in candidate_ids:
        raise AssertionError("canonical 14638 supersede candidate is missing")

    proofs: list[dict[str, object]] = []
    for row in rows:
        entry_id = row["id"]
        anchor_id = row["canonical_anchor_id"]
        assert isinstance(entry_id, int) and isinstance(anchor_id, int)
        current = ko.texts[entry_id]
        candidate_jp = jp.texts[entry_id]
        canonical_jp = jp.texts[anchor_id]
        proposal = row["translation"]
        assert isinstance(proposal, str)
        if not re.fullmatch(r"[a-z]+", current):
            raise AssertionError(f"id {entry_id}: expected a lower-case pinyin residual")
        if not any(ord(char) > 127 for char in candidate_jp):
            raise AssertionError(f"id {entry_id}: expected non-ASCII pristine PC JP key")
        if not any(ord(char) > 127 for char in canonical_jp):
            raise AssertionError(f"anchor {anchor_id}: expected non-ASCII canonical PC JP title")
        if proposal != ko.texts[anchor_id] or not _contains_hangul(proposal):
            raise AssertionError(f"id {entry_id}: proposal is not exact current-PC-KO canonical anchor")
        if row["proof"] != "full_canonical_pc_title_anchor":
            raise AssertionError(f"id {entry_id}: proof classification drifted")
        if _sha256_text(candidate_jp) != row["candidate_jp_utf16le_sha256"]:
            raise AssertionError(f"id {entry_id}: pristine JP text hash mismatch")
        if _sha256_text(current) != row["current_ko_utf16le_sha256"]:
            raise AssertionError(f"id {entry_id}: current KO text hash mismatch")
        if _sha256_text(canonical_jp) != row["canonical_jp_utf16le_sha256"]:
            raise AssertionError(f"id {entry_id}: canonical JP text hash mismatch")
        if _sha256_text(proposal) != row["translation_utf16le_sha256"]:
            raise AssertionError(f"id {entry_id}: proposal text hash mismatch")
        if candidate_jp.count("\n") or current.count("\n") or proposal.count("\n"):
            raise AssertionError(f"id {entry_id}: title is not single-line")
        if _protected_signature(current) != _protected_signature(proposal):
            raise AssertionError(f"id {entry_id}: protected token signature changed")
        if any(_protected_signature(current)):
            raise AssertionError(f"id {entry_id}: residual title unexpectedly carries protected tokens")
        source_units = len(candidate_jp.encode("utf-16le")) // 2
        current_units = len(current.encode("utf-16le")) // 2
        proposal_units = len(proposal.encode("utf-16le")) // 2
        if proposal_units > current_units:
            raise AssertionError(f"id {entry_id}: proposal exceeds current title layout budget")
        proofs.append(
            {
                "id": entry_id,
                "canonical_anchor_id": anchor_id,
                "candidate_jp_utf16le_sha256": row["candidate_jp_utf16le_sha256"],
                "current_ko_utf16le_sha256": row["current_ko_utf16le_sha256"],
                "canonical_jp_utf16le_sha256": row["canonical_jp_utf16le_sha256"],
                "proposed_ko_utf16le_sha256": row["translation_utf16le_sha256"],
                "event_layout": {
                    "kind": "single_line_event_title",
                    "candidate_jp_utf16_units": source_units,
                    "current_utf16_units": current_units,
                    "proposal_utf16_units": proposal_units,
                    "proposal_within_current_budget": True,
                    "manual_newline_count": 0,
                    "protected_token_signature": "empty",
                },
            }
        )

    digest = _sha256_bytes(
        json.dumps(proofs, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")
    )
    return {
        "status": "ok",
        "resource": "MSG_PK/JP/msgev.bin",
        "candidate_count": len(proofs),
        "candidate_ids": [proof["id"] for proof in proofs],
        "superseded_temporary_candidate_id": SUPERSEDED_TEMPORARY_ID,
        "pc_reference_string_count": EXPECTED_STRING_COUNT,
        "candidate_proofs_sha256": digest,
        "candidate_proofs": proofs,
        "write_scope": "none",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--proofs", action="store_true", help="emit all source-free hash/layout proofs")
    parser.add_argument("--emit-candidates", action="store_true", help="emit private id/translation/anchor rows")
    args = parser.parse_args()
    result = validate()
    if args.emit_candidates:
        for row in _private_candidates():
            print(
                json.dumps(
                    {
                        "id": row["id"],
                        "translation": row["translation"],
                        "canonical_anchor_id": row["canonical_anchor_id"],
                        "translation_utf16le_sha256": row["translation_utf16le_sha256"],
                    },
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
            )
        return 0
    if not args.proofs:
        result = {key: value for key, value in result.items() if key != "candidate_proofs"}
    print(json.dumps(result, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
