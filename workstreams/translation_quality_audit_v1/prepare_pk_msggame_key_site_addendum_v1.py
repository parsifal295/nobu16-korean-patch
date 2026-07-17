#!/usr/bin/env python3
"""Prepare PC-only PK battle key-site terminology corrections.

In the PK battle messages, the direct Japanese term ``\u8981\u6240`` names a
capturable battlefield objective.  A residual Korean rendering uses
``\uc694\uc18c`` (a generic element) instead of the already-established battlefield
term ``\uc694\ucda9\uc9c0``.  This audit scans the complete PC PK ``msggame``
resource, but emits only direct, static literals in battle-message/help blocks.

Every ``0143`` dynamic-grammar record remains an explicit hold.  The script
uses stock PC Japanese plus live PC Korean/SC/TC only; it never reads Switch
Korean and it never writes a game resource.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
V1_SCRIPT = SCRIPT.with_name("prepare_base_msggame_quality_addendum_v1.py")
module_spec = importlib.util.spec_from_file_location(
    "base_msggame_quality_addendum_v1", V1_SCRIPT
)
if module_spec is None or module_spec.loader is None:
    raise RuntimeError(f"cannot load shared validator: {V1_SCRIPT}")
base = importlib.util.module_from_spec(module_spec)
sys.modules[module_spec.name] = base
module_spec.loader.exec_module(base)


STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PK_STOCK_JP = (
    STEAM
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / "MSG_PK"
    / "JP"
    / "msggame.bin"
)
PK_LIVE_KO = STEAM / "MSG_PK" / "JP" / "msggame.bin"
PK_REFERENCES = {
    "sc": STEAM / "MSG_PK" / "SC" / "msggame.bin",
    "tc": STEAM / "MSG_PK" / "TC" / "msggame.bin",
}
EXPECTED_FILE_SHA256 = {
    "jp": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "ko": "DE606E50C9A6241BD0B85D17A000394007952093984F75DB56E296E0CCDE6B01",
    "sc": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    "tc": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
}
OUTPUT = (
    REPO
    / "tmp"
    / "translation_quality_audit_v1"
    / "semantic"
    / "pk_msggame_key_site_addendum.v1.jsonl"
)
AUDIT_ROOT = REPO / "tmp" / "translation_quality_audit_v1"

JP_KEY_SITE = "\u8981\u6240"
KO_GENERIC_ELEMENT = "\uc694\uc18c"
KO_BATTLE_KEY_SITE = "\uc694\ucda9\uc9c0"
CHINESE_KEY_SITE_TERMS = ("\u8981\u5730", "\u8981\u6240")
ALLOWED_BATTLE_BLOCKS = {9, 13, 14}


# The entire PC PK residual scan has exactly 72 direct JP ``要所`` / Korean
# ``요소`` literal pairs.  Fifteen occur in opaque-grammar records and are held;
# these 57 are the static subset authorized for review.  Keeping the full scan
# partition below makes a later source drift or a missed occurrence fail closed.
CANDIDATE_COORDINATES = (
    "9:457:0",
    "9:475:0",
    "9:1122:0",
    "9:1123:0",
    "9:1124:0",
    "9:1127:0",
    "9:1128:0",
    "9:1129:0",
    "9:2800:0",
    "9:2807:0",
    "9:2829:0",
    "9:2830:0",
    "9:2831:0",
    "9:2855:0",
    "9:2856:0",
    "9:2857:0",
    "9:2858:0",
    "9:2884:0",
    "9:2892:0",
    "9:2895:0",
    "9:3004:0",
    "9:3005:0",
    "9:3006:0",
    "9:3007:0",
    "9:3008:0",
    "9:3009:0",
    "9:3010:0",
    "9:3011:0",
    "9:3012:0",
    "9:3013:0",
    "9:3014:0",
    "9:3015:0",
    "9:3053:0",
    "9:3057:0",
    "9:3058:0",
    "9:3061:0",
    "9:3062:0",
    "9:3548:0",
    "9:3550:0",
    "9:3556:0",
    "9:3931:0",
    "9:3936:0",
    "9:3938:0",
    "9:4053:0",
    "9:4054:0",
    "9:4055:0",
    "9:4056:0",
    "9:4057:0",
    "9:4083:0",
    "9:4084:0",
    "13:398:0",
    "13:406:0",
    "14:88:1",
    "14:91:1",
    "14:123:3",
    "14:131:0",
    "14:131:1",
)
OPAQUE_GRAMMAR_HOLD_COORDINATES = (
    "9:1120:0",
    "9:1121:0",
    "9:1130:0",
    "9:3371:0",
    "9:3372:0",
    "9:3373:0",
    "9:3374:0",
    "9:3375:0",
    "9:3376:0",
    "9:3377:0",
    "9:3378:0",
    "9:3379:0",
    "9:3380:0",
    "9:3381:0",
    "9:3382:0",
)


def _load_archives() -> tuple[dict[str, Any], dict[str, str]]:
    paths = {"jp": PK_STOCK_JP, "ko": PK_LIVE_KO, **PK_REFERENCES}
    hashes = {name: base.sha256_bytes(path.read_bytes()) for name, path in paths.items()}
    if hashes != EXPECTED_FILE_SHA256:
        raise ValueError(f"PC PK input file hash drift: {hashes!r}")
    archives = {
        name: base.parse_packed_msggame(path.read_bytes()).archive
        for name, path in paths.items()
    }
    return archives, hashes


def _resource_is_pk_candidate(path: Path, row: dict[str, object]) -> bool:
    """Identify prior PK review rows without mixing Base coordinate namespaces."""
    return path.name.startswith("pk_msggame") or row.get("resource") == "pk_msggame"


def read_prior_coordinates() -> set[str]:
    result: set[str] = set()
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
                if not _resource_is_pk_candidate(path, row):
                    continue
                coordinate = row.get("coordinate")
                if isinstance(coordinate, str):
                    result.add(coordinate)
    return result


def battle_context_class(block_id: int) -> str:
    if block_id == 9:
        return "pk_battlefield_system_or_combat_dialogue"
    if block_id in {13, 14}:
        return "pk_battle_help_or_tutorial"
    raise ValueError(f"coordinate falls outside the allowlisted battle blocks: {block_id}")


def _reference_status(text: str) -> str:
    if not text:
        return "empty_locale_record"
    if not any(term in text for term in CHINESE_KEY_SITE_TERMS):
        raise ValueError("PC Chinese reference lacks the named battle key-site context")
    return "named_key_site_visible"


def _all_direct_residual_coordinates(archives: dict[str, Any]) -> set[str]:
    """Return direct one-literal JP/KO residuals across the complete PK archive."""
    records_by_language: dict[str, dict[tuple[int, int], Any]] = {}
    for language, archive in archives.items():
        records_by_language[language] = {
            (record.block_id, record.record_id): record
            for block in archive.blocks
            for record in block.records
        }
    coordinate_sets = {language: set(records) for language, records in records_by_language.items()}
    if len({frozenset(value) for value in coordinate_sets.values()}) != 1:
        raise ValueError("PC PK msggame record coordinate sets differ")

    result: set[str] = set()
    for record_key in sorted(coordinate_sets["jp"]):
        jp_literals = base.literal_texts(records_by_language["jp"][record_key])
        ko_literals = base.literal_texts(records_by_language["ko"][record_key])
        if len(jp_literals) != len(ko_literals):
            raise ValueError(f"PK literal layout differs at {record_key}")
        for literal_id, (source, current) in enumerate(zip(jp_literals, ko_literals)):
            if JP_KEY_SITE in source and KO_GENERIC_ELEMENT in current:
                result.add(base.coordinate_key(record_key[0], record_key[1], literal_id))
    return result


def build_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    candidates = set(CANDIDATE_COORDINATES)
    holds = set(OPAQUE_GRAMMAR_HOLD_COORDINATES)
    if len(candidates) != len(CANDIDATE_COORDINATES):
        raise ValueError("duplicate static candidate coordinate")
    if len(holds) != len(OPAQUE_GRAMMAR_HOLD_COORDINATES):
        raise ValueError("duplicate opaque-grammar hold coordinate")
    if candidates.intersection(holds):
        raise ValueError("candidate and hold partitions overlap")

    prior_overlap = sorted(read_prior_coordinates().intersection(candidates), key=base.coordinate_tuple)
    if prior_overlap:
        raise ValueError(f"candidate coordinates overlap prior PK artifacts: {prior_overlap}")

    archives, hashes = _load_archives()
    full_residuals = _all_direct_residual_coordinates(archives)
    expected_residuals = candidates.union(holds)
    if full_residuals != expected_residuals:
        missing = sorted(expected_residuals.difference(full_residuals), key=base.coordinate_tuple)
        unexpected = sorted(full_residuals.difference(expected_residuals), key=base.coordinate_tuple)
        raise ValueError(
            "PK direct key-site residual inventory drifted: "
            f"missing={missing!r}, unexpected={unexpected!r}"
        )

    rows: list[dict[str, object]] = []
    replacements: dict[tuple[int, int, int], str] = {}
    for coordinate in sorted(candidates, key=base.coordinate_tuple):
        block_id, record_id, target_literal_id = base.coordinate_tuple(coordinate)
        if block_id not in ALLOWED_BATTLE_BLOCKS:
            raise ValueError(f"{coordinate}: not an allowlisted battlefield/help block")
        records = {
            name: base.get_record(archive, coordinate)
            for name, archive in archives.items()
        }
        texts = {name: base.literal_texts(record) for name, record in records.items()}
        if any(target_literal_id >= len(value) for value in texts.values()):
            raise ValueError(f"{coordinate}: target literal is absent in a PC locale")

        before_skeleton = base.nonliteral_skeleton(records["ko"])
        if base.OPAQUE_GRAMMAR_HEX in before_skeleton.hex():
            raise ValueError(f"{coordinate}: opaque grammar opcode must remain a hold")
        current = texts["ko"][target_literal_id]
        source = texts["jp"][target_literal_id]
        if JP_KEY_SITE not in source:
            raise ValueError(f"{coordinate}: direct Japanese key-site predicate missing")
        if source.count(JP_KEY_SITE) != current.count(KO_GENERIC_ELEMENT):
            raise ValueError(f"{coordinate}: source/target key-site occurrence count differs")
        if base.RUNTIME_RE.search(current) or base.PRINTF_RE.search(current):
            raise ValueError(f"{coordinate}: target must remain a static literal")

        proposal = current.replace(KO_GENERIC_ELEMENT, KO_BATTLE_KEY_SITE)
        if proposal == current:
            raise ValueError(f"{coordinate}: no generic Korean element term to replace")
        if base.profile(current) != base.profile(proposal):
            raise ValueError(f"{coordinate}: target literal format profile changed")

        before_literals = texts["ko"]
        after_literals = list(before_literals)
        after_literals[target_literal_id] = proposal
        before_full = "".join(before_literals)
        after_full = "".join(after_literals)
        if base.profile(before_full) != base.profile(after_full):
            raise ValueError(f"{coordinate}: whole-record format profile changed")
        rebuilt_record = base.MsgGameRecord(
            block_id=records["ko"].block_id,
            record_id=records["ko"].record_id,
            relative_offset=records["ko"].relative_offset,
            data=base.rebuild_record_literals(records["ko"], {target_literal_id: proposal}),
        )
        if base.literal_texts(rebuilt_record) != after_literals:
            raise ValueError(f"{coordinate}: record literal rebuild mismatch")
        after_skeleton = base.nonliteral_skeleton(rebuilt_record)
        if before_skeleton != after_skeleton:
            raise ValueError(f"{coordinate}: nonliteral bytecode changed")

        reference_concatenations = {
            name: "".join(texts[name])
            for name in ("sc", "tc")
        }
        reference_status = {
            name: _reference_status(reference_concatenations[name])
            for name in ("sc", "tc")
        }
        rows.append(
            {
                "coordinate": coordinate,
                "ko": current,
                "proposed_ko": proposal,
                "issue_type": "pk_battle_key_site_generic_element_mistranslation",
                "rationale": (
                    "The direct Japanese source names the capturable battlefield objective "
                    "'\u8981\u6240'.  In these PK battle-system/help contexts, Korean '\uc694\uc18c' means "
                    "a generic element, while nearby PC Korean battle text already uses '\uc694\ucda9\uc9c0' "
                    "for the strategic objective.  Replace only that named-object term."
                ),
                "battle_context_class": battle_context_class(block_id),
                "private_source_text": source,
                "source_text_hash": base.sha256_utf16le(source),
                "current_hash": base.sha256_utf16le(current),
                "proposed_hash": base.sha256_utf16le(proposal),
                "source_file_sha256": hashes["ko"],
                "native_jp_file_sha256": hashes["jp"],
                "reference_file_sha256": {name: hashes[name] for name in ("sc", "tc")},
                "pc_language_contexts": {
                    name: {
                        "literal_texts": texts[name],
                        "literal_concatenation": "".join(texts[name]),
                        "literal_concatenation_hash": base.sha256_utf16le("".join(texts[name])),
                        "nonliteral_skeleton_sha256": base.sha256_bytes(
                            base.nonliteral_skeleton(records[name])
                        ),
                    }
                    for name in ("jp", "sc", "tc")
                },
                "pc_sc_tc_key_site_crosscheck": reference_status,
                "linked_record_contract": {
                    "status": "whole_literal_sequence_newline_runtime_slots_and_nonliteral_bytecode_validated",
                    "literal_layouts": {
                        name: list(range(len(value)))
                        for name, value in texts.items()
                    },
                    "target_literal_id": target_literal_id,
                    "current_ko_literal_texts": before_literals,
                    "proposed_ko_literal_texts": after_literals,
                    "current_ko_literal_concatenation": before_full,
                    "proposed_ko_literal_concatenation": after_full,
                    "whole_record_format": {
                        "newlines": "match",
                        "outer_ascii_whitespace": "match",
                        "question_marks": "unchanged",
                    },
                    "nonliteral_bytecode": {
                        "status": "unchanged_after_rebuild",
                        "before_skeleton_sha256": base.sha256_bytes(before_skeleton),
                        "after_skeleton_sha256": base.sha256_bytes(after_skeleton),
                    },
                },
                "format_validation": {
                    "escape_tags": "match",
                    "runtime_tokens": "match",
                    "printf": "match",
                    "newlines": "match",
                    "outer_ascii_whitespace": "match",
                    "question_marks": "unchanged",
                },
            }
        )
        replacements[(block_id, record_id, target_literal_id)] = proposal

    overlay = base._validate_full_overlay(PK_LIVE_KO.read_bytes(), replacements)
    return rows, {
        "existing_coordinate_overlap": prior_overlap,
        "full_residual_scan": {
            "direct_jp_key_site_to_ko_generic_element_count": len(full_residuals),
            "static_candidate_count": len(candidates),
            "opaque_0143_hold_count": len(holds),
            "opaque_0143_hold_coordinates": sorted(holds, key=base.coordinate_tuple),
            "unexpected_residual_coordinates": [],
        },
        "full_overlay_validation": overlay,
    }


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
            if row["coordinate"] == args.coordinate:
                print(json.dumps(row, ensure_ascii=True, separators=(",", ":")))
                return 0
        raise SystemExit("coordinate not found")
    if args.validate:
        print(
            json.dumps(
                {
                    "row_count": len(rows),
                    "coordinates": [row["coordinate"] for row in rows],
                    "candidate_contract": "whole_literal_sequence_runtime_slots_and_nonliteral_bytecode",
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
        payload = base.serialize(rows)
        if OUTPUT.is_file() and OUTPUT.read_bytes() == payload:
            status = "already_current"
        else:
            base.atomic_write(OUTPUT, payload)
            status = "written"
        print(
            json.dumps(
                {
                    "output": str(OUTPUT),
                    "row_count": len(rows),
                    "sha256": base.sha256_bytes(payload),
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
