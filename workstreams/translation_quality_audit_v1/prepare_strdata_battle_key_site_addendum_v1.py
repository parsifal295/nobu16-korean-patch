#!/usr/bin/env python3
"""Prepare PC-only static ``strdata`` battlefield key-site corrections.

The source term ``\u8981\u6240`` denotes a named, capturable battle objective in
these shared labels and effect descriptions.  The Korean word ``\uc694\uc18c``
instead means a generic element; ``\uc694\ucda9\uc9c0`` is the established objective
term.  The complete PC residual scan is partitioned into sixteen direct
JP/SC/TC-backed static entries and one dummy/unverified hold.  No Switch Korean
or historic Korean translation is read, and no game resource is written.
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
    / "MSG"
    / "JP"
    / "strdata.bin"
)
LIVE_KO = STEAM / "MSG" / "JP" / "strdata.bin"
REFERENCES = {
    language.lower(): STEAM / "MSG" / language / "strdata.bin"
    for language in ("SC", "TC")
}
EXPECTED_FILE_SHA256 = {
    "jp": "FF172741A7ADC0F8C9E903A4BB3F4482639CE5AB80EA44C8CC458C300940DEE0",
    "ko": "D518A91E36B9A59EAD0B5ED1FDD067941E4BF72E43AFCB19C296C8AD77C8C128",
    "sc": "93F88D71210B96783749CEB948E0713D7E6552F764F644092B71A5FD0C994B88",
    "tc": "16481F0B4B1E544F8F7C0B1C92210D13592560470AC062847DA32375B77DA861",
}
AUDIT_ROOT = REPO / "tmp" / "translation_quality_audit_v1"
OUTPUT = AUDIT_ROOT / "semantic" / "strdata_battle_key_site_addendum.v1.jsonl"

sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "workstreams" / "strdata"))
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from strdata_format import (  # noqa: E402
    coordinate_texts,
    parse_raw_strdata,
    rebuild_raw_strdata,
)


JP_KEY_SITE = "\u8981\u6240"
KO_GENERIC_ELEMENT = "\uc694\uc18c"
KO_BATTLE_KEY_SITE = "\uc694\ucda9\uc9c0"
CHINESE_KEY_SITE_TERMS = ("\u8981\u5730", "\u8981\u6240")

CANDIDATE_COORDINATES = (
    (0, 20695),
    (0, 20743),
    (0, 20745),
    (0, 20764),
    (0, 20765),
    (0, 24150),
    (0, 24156),
    (0, 24171),
    (0, 24397),
    (1, 568),
    (1, 1143),
    (1, 1144),
    (1, 1242),
    (1, 2054),
    (1, 2235),
    (1, 2984),
)
UNVERIFIED_DUMMY_HOLD_COORDINATES = ((0, 15072),)

ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
PRIVATE_USE_RE = re.compile(r"[\ue000-\uf8ff]")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def coordinate_key(coordinate: tuple[int, int]) -> str:
    return f"{coordinate[0]}:{coordinate[1]}"


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


def _load_archive(path: Path) -> tuple[bytes, bytes, Any]:
    packed = path.read_bytes()
    _header, raw = decompress_wrapper(packed)
    return packed, raw, parse_raw_strdata(raw)


def _load_inputs() -> tuple[dict[str, tuple[bytes, bytes, Any]], dict[str, str]]:
    paths = {"jp": PRISTINE_JP, "ko": LIVE_KO, **REFERENCES}
    hashes = {name: sha256_bytes(path.read_bytes()) for name, path in paths.items()}
    if hashes != EXPECTED_FILE_SHA256:
        raise ValueError(f"PC strdata input file hash drift: {hashes!r}")
    archives = {name: _load_archive(path) for name, path in paths.items()}
    coordinate_sets = {
        name: set(coordinate_texts(archive).keys())
        for name, (_packed, _raw, archive) in archives.items()
    }
    if len({frozenset(value) for value in coordinate_sets.values()}) != 1:
        raise ValueError("PC strdata coordinate sets differ")
    for name, (_packed, raw, archive) in archives.items():
        if rebuild_raw_strdata(archive) != raw:
            raise ValueError(f"{name}: unchanged PC strdata rebuild is not byte-identical")
    return archives, hashes


def _resource_is_strdata_candidate(path: Path, row: dict[str, object]) -> bool:
    return path.name.startswith("strdata") or row.get("resource") == "strdata"


def read_prior_coordinates() -> set[tuple[int, int]]:
    result: set[tuple[int, int]] = set()
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
                if not _resource_is_strdata_candidate(path, row):
                    continue
                block, identifier = row.get("block"), row.get("id")
                if isinstance(block, int) and isinstance(identifier, int):
                    result.add((block, identifier))
    return result


def _reference_status(text: str) -> str:
    if not text:
        raise ValueError("static candidate has an empty Chinese reference")
    if not any(term in text for term in CHINESE_KEY_SITE_TERMS):
        raise ValueError("PC Chinese reference lacks the named battle key-site context")
    return "named_key_site_visible"


def _replacement_sequences(
    archive: Any,
    replacements: dict[tuple[int, int], str],
) -> dict[int, list[str]]:
    result: dict[int, list[str]] = {}
    for block_id, identifier in replacements:
        if block_id not in result:
            result[block_id] = list(archive.blocks[block_id].texts)
        result[block_id][identifier] = replacements[(block_id, identifier)]
    return result


def _validate_full_overlay(
    packed_source: bytes,
    source_archive: Any,
    replacements: dict[tuple[int, int], str],
) -> dict[str, object]:
    """Rebuild/repack the complete archive and prove only allowlisted text changes."""
    _header, raw = decompress_wrapper(packed_source)
    archive = parse_raw_strdata(raw)
    if coordinate_texts(archive) != coordinate_texts(source_archive):
        raise ValueError("full-overlay source archive differs from initial parse")
    rebuilt_raw = rebuild_raw_strdata(archive, _replacement_sequences(archive, replacements))
    rebuilt_archive = parse_raw_strdata(rebuilt_raw)
    before = coordinate_texts(archive)
    after = coordinate_texts(rebuilt_archive)
    changed = sorted(
        coordinate
        for coordinate in before
        if before[coordinate] != after[coordinate]
    )
    expected = sorted(replacements)
    if changed != expected:
        raise ValueError(
            "full-overlay changed unexpected strdata coordinates: "
            f"{[coordinate_key(value) for value in changed]!r}"
        )
    for before_block, after_block in zip(archive.blocks, rebuilt_archive.blocks, strict=True):
        if before_block.inner_header != after_block.inner_header:
            raise ValueError(f"full-overlay changed opaque inner header for block {before_block.block_id}")
    packed_rebuilt = recompress_wrapper(rebuilt_raw, packed_source)
    _repacked_header, decoded = decompress_wrapper(packed_rebuilt)
    if decoded != rebuilt_raw:
        raise ValueError("full-overlay wrapper round-trip mismatch")
    repacked = parse_raw_strdata(decoded)
    if coordinate_texts(repacked) != after:
        raise ValueError("full-overlay repacked parse verification failed")
    return {
        "source_packed_sha256": sha256_bytes(packed_source),
        "rebuilt_raw_sha256": sha256_bytes(rebuilt_raw),
        "rebuilt_packed_sha256": sha256_bytes(packed_rebuilt),
        "changed_coordinates": [coordinate_key(value) for value in changed],
        "unchanged_non_target_texts": True,
        "opaque_inner_headers": "unchanged",
        "wrapper_roundtrip": "pass",
    }


def build_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    candidates = set(CANDIDATE_COORDINATES)
    holds = set(UNVERIFIED_DUMMY_HOLD_COORDINATES)
    if len(candidates) != len(CANDIDATE_COORDINATES) or len(holds) != len(UNVERIFIED_DUMMY_HOLD_COORDINATES):
        raise ValueError("duplicate candidate or hold coordinate")
    if candidates.intersection(holds):
        raise ValueError("candidate and hold coordinate partitions overlap")
    prior_overlap = sorted(candidates.intersection(read_prior_coordinates()))
    if prior_overlap:
        raise ValueError(
            "candidate coordinates overlap prior strdata artifacts: "
            f"{[coordinate_key(value) for value in prior_overlap]!r}"
        )

    archives, hashes = _load_inputs()
    texts = {
        name: coordinate_texts(archive)
        for name, (_packed, _raw, archive) in archives.items()
    }
    full_residuals = {
        coordinate
        for coordinate, source in texts["jp"].items()
        if JP_KEY_SITE in source and KO_GENERIC_ELEMENT in texts["ko"][coordinate]
    }
    expected_residuals = candidates.union(holds)
    if full_residuals != expected_residuals:
        raise ValueError(
            "strdata direct key-site residual inventory drifted: "
            f"missing={[coordinate_key(value) for value in sorted(expected_residuals - full_residuals)]!r}, "
            f"unexpected={[coordinate_key(value) for value in sorted(full_residuals - expected_residuals)]!r}"
        )

    rows: list[dict[str, object]] = []
    replacements: dict[tuple[int, int], str] = {}
    for coordinate in sorted(candidates):
        block, identifier = coordinate
        source = texts["jp"][coordinate]
        current = texts["ko"][coordinate]
        if source.count(JP_KEY_SITE) != current.count(KO_GENERIC_ELEMENT):
            raise ValueError(f"{coordinate_key(coordinate)}: source/target key-site occurrence count differs")
        if RUNTIME_RE.search(current) or PRINTF_RE.search(current):
            raise ValueError(f"{coordinate_key(coordinate)}: target must remain a static text-table entry")
        proposal = current.replace(KO_GENERIC_ELEMENT, KO_BATTLE_KEY_SITE)
        if proposal == current:
            raise ValueError(f"{coordinate_key(coordinate)}: no generic Korean element term to replace")
        if profile(current) != profile(proposal):
            raise ValueError(f"{coordinate_key(coordinate)}: format profile changed")
        reference_status = {
            language: _reference_status(texts[language][coordinate])
            for language in ("sc", "tc")
        }
        rows.append(
            {
                "block": block,
                "id": identifier,
                "ko": current,
                "proposed_ko": proposal,
                "issue_type": "battle_key_site_generic_element_mistranslation",
                "rationale": (
                    "The direct Japanese source names the battlefield objective '\u8981\u6240'. "
                    "PC SC/TC render this static label/effect as '\u8981\u5730' or '\u8981\u6240'.  Korean '\uc694\uc18c' "
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
                    for language in ("sc", "tc")
                },
                "pc_target_contexts": {
                    language: texts[language][coordinate]
                    for language in ("sc", "tc")
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
        replacements[coordinate] = proposal

    overlay = _validate_full_overlay(archives["ko"][0], archives["ko"][2], replacements)
    return rows, {
        "existing_coordinate_overlap": [],
        "full_residual_scan": {
            "direct_jp_key_site_to_ko_generic_element_count": len(full_residuals),
            "static_candidate_count": len(candidates),
            "unverified_dummy_hold_count": len(holds),
            "unverified_dummy_hold_coordinates": [
                coordinate_key(value) for value in sorted(holds)
            ],
            "unexpected_residual_coordinates": [],
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
    parser.add_argument("--coordinate")
    args = parser.parse_args()
    if sum(bool(value) for value in (args.validate, args.write, args.coordinate)) > 1:
        parser.error("choose at most one output mode")

    rows, validation = build_rows()
    if args.coordinate:
        for row in rows:
            if args.coordinate == f"{row['block']}:{row['id']}":
                print(json.dumps(row, ensure_ascii=True, separators=(",", ":")))
                return 0
        raise SystemExit("coordinate not found")
    if args.validate:
        print(
            json.dumps(
                {
                    "row_count": len(rows),
                    "coordinates": [f"{row['block']}:{row['id']}" for row in rows],
                    "candidate_contract": "whole_strdata_rebuild_repack_and_non_target_text_invariance",
                    "source_policy": "stock_pc_jp_plus_live_pc_sc_tc_only",
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
