#!/usr/bin/env python3
"""Prepare a PC-only base msggame addendum for fixed proper-name particles.

Each allowlisted coordinate has a literal Japanese proper name immediately
before its Korean particle.  The targeted Korean heads are vowel-final, so
the current object/subject particle is mechanically ungrammatical.  Switch
resources are never read; output remains private review evidence.
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


OUTPUT = (
    REPO
    / "tmp"
    / "translation_quality_audit_v1"
    / "semantic"
    / "base_msggame_quality_addendum.v3.jsonl"
)
PRIOR_CANDIDATE_ARTIFACTS = (
    *base.EXISTING_CANDIDATE_ARTIFACTS,
    base.OUTPUT,
    REPO
    / "tmp"
    / "translation_quality_audit_v1"
    / "semantic"
    / "base_msggame_quality_addendum.v2.jsonl",
)
LAYOUT_THREE = {language: [0, 1, 2] for language in ("jp", "ko", "sc", "tc")}
LAYOUT_NINE_2561 = {
    "jp": [0, 1, 2],
    "ko": [0, 1, 2],
    "sc": [0, 1, 2],
    "tc": [0, 1],
}
LAYOUT_FIVE_WITH_EMPTY_REFERENCES = {
    "jp": [0, 1, 2, 3, 4],
    "ko": [0, 1, 2, 3, 4],
    "sc": [0],
    "tc": [0],
}


CASES: dict[str, dict[str, Any]] = {
    "2:290:2": {
        "expected_preceding": "\uac00\uc774",
        "expected_current": "\uc774 \ud65c\ub85c \ub418\ubc1b\uc544\uce58\ub9ac\ub77c!",
        "proposal": "\uac00 \ud65c\ub85c \ub418\ubc1b\uc544\uce58\ub9ac\ub77c!",
        "expected_layouts": LAYOUT_THREE,
        "issue_type": "proper_name_subject_particle",
        "rationale": (
            "The preceding literal is the fixed vowel-final proper name '\uac00\uc774'. "
            "The following subject particle must be '\uac00', matching the PC Japanese "
            "archery taunt and both PC Chinese contexts."
        ),
    },
    "2:618:2": {
        "expected_preceding": "\uc624\ud1a0\ubaa8",
        "expected_current": "\uc744 \uaebe\uace0, \uc774 \uaddc\uc288\uc5d0 \ud328\uad8c\uc744 \uc678\uce58\ub9ac\ub77c",
        "proposal": "\ub97c \uaebe\uace0, \uc774 \uaddc\uc288\uc5d0 \ud328\uad8c\uc744 \uc678\uce58\ub9ac\ub77c",
        "expected_layouts": LAYOUT_THREE,
        "issue_type": "proper_name_object_particle",
        "rationale": (
            "The preceding literal is the fixed vowel-final proper name '\uc624\ud1a0\ubaa8'. "
            "The Japanese source says to defeat that name; Korean therefore requires "
            "the object particle '\ub97c'."
        ),
    },
    "9:2561:2": {
        "expected_preceding": "\uc2dc\uce58\ud14c\uad6c\ubbf8\n",
        "expected_current": "\uc774 \ud574\ub0c8\uc18c!",
        "proposal": "\uac00 \ud574\ub0c8\uc18c!",
        "expected_layouts": LAYOUT_NINE_2561,
        "issue_type": "proper_name_subject_particle",
        "rationale": (
            "The preceding literal is the fixed vowel-final group name '\uc2dc\uce58\ud14c\uad6c\ubbf8'. "
            "Resolve its subject particle as '\uac00', in line with the PC Japanese "
            "success report."
        ),
    },
    "9:3800:4": {
        "expected_preceding": "\uc624\ud1a0\ubaa8",
        "expected_current": "\uc744 \uc704\ud574\uc11c\ub77c\ub3c4 \uc0b4\uc544 \ub3cc\uc544\uac00\uc57c\u2026",
        "proposal": "\ub97c \uc704\ud574\uc11c\ub77c\ub3c4 \uc0b4\uc544 \ub3cc\uc544\uac00\uc57c\u2026",
        "expected_layouts": LAYOUT_FIVE_WITH_EMPTY_REFERENCES,
        "issue_type": "proper_name_object_particle",
        "rationale": (
            "The preceding literal is the fixed vowel-final proper name '\uc624\ud1a0\ubaa8'. "
            "The Korean phrase for returning alive for that person's sake requires "
            "'\ub97c', as does the direct PC-Japanese source context."
        ),
    },
    "17:31:4": {
        "expected_preceding": "\uc624\ud1a0\ubaa8",
        "expected_current": "\uc744 \uc704\ud574\uc11c\ub77c\ub3c4 \uc0b4\uc544 \ub3cc\uc544\uac00\uc57c\u2026",
        "proposal": "\ub97c \uc704\ud574\uc11c\ub77c\ub3c4 \uc0b4\uc544 \ub3cc\uc544\uac00\uc57c\u2026",
        "expected_layouts": LAYOUT_FIVE_WITH_EMPTY_REFERENCES,
        "issue_type": "proper_name_object_particle",
        "rationale": (
            "This duplicate direct PC-Japanese proper-name line retains the same "
            "vowel-final head '\uc624\ud1a0\ubaa8'.  Resolve its object particle as '\ub97c'."
        ),
    },
}


def read_prior_coordinates() -> set[str]:
    result: set[str] = set()
    for path in PRIOR_CANDIDATE_ARTIFACTS:
        if not path.is_file():
            raise ValueError(f"reviewed candidate artifact is missing: {path}")
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            row = json.loads(line)
            coordinate = row.get("coordinate")
            if not isinstance(coordinate, str):
                raise ValueError(f"invalid coordinate: {path}:{line_number}")
            result.add(coordinate)
    return result


def build_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    overlap = sorted(read_prior_coordinates().intersection(CASES), key=base.coordinate_tuple)
    if overlap:
        raise ValueError(f"candidate coordinates overlap prior artifacts: {overlap}")
    archives, hashes = base._load_archives()
    rows: list[dict[str, object]] = []
    replacements: dict[tuple[int, int, int], str] = {}

    for coordinate in sorted(CASES, key=base.coordinate_tuple):
        case = CASES[coordinate]
        block_id, record_id, target_literal_id = base.coordinate_tuple(coordinate)
        records = {
            name: base.get_record(archive, coordinate) for name, archive in archives.items()
        }
        texts = {name: base.literal_texts(record) for name, record in records.items()}
        layouts = {name: list(range(len(value))) for name, value in texts.items()}
        if layouts != case["expected_layouts"]:
            raise ValueError(f"{coordinate}: literal layout drift: {layouts!r}")
        if target_literal_id == 0:
            raise ValueError(f"{coordinate}: target must follow a literal proper name")
        if texts["ko"][target_literal_id - 1] != case["expected_preceding"]:
            raise ValueError(f"{coordinate}: fixed Korean proper-name head drifted")

        before_skeleton = base.nonliteral_skeleton(records["ko"])
        if base.OPAQUE_GRAMMAR_HEX in before_skeleton.hex():
            raise ValueError(f"{coordinate}: opaque grammar opcode must remain a hold")
        current = texts["ko"][target_literal_id]
        proposal = str(case["proposal"])
        if current != case["expected_current"]:
            raise ValueError(f"{coordinate}: current Korean literal drifted")
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

        source = texts["jp"][target_literal_id]
        rows.append(
            {
                "coordinate": coordinate,
                "ko": current,
                "proposed_ko": proposal,
                "issue_type": case["issue_type"],
                "rationale": case["rationale"],
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
                        "literal_concatenation_hash": base.sha256_utf16le(
                            "".join(texts[name])
                        ),
                        "nonliteral_skeleton_sha256": base.sha256_bytes(
                            base.nonliteral_skeleton(records[name])
                        ),
                    }
                    for name in ("jp", "sc", "tc")
                },
                "linked_record_contract": {
                    "status": "whole_literal_sequence_newline_runtime_slots_and_nonliteral_bytecode_validated",
                    "literal_layouts": layouts,
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

    overlay = base._validate_full_overlay(base.LIVE_KO.read_bytes(), replacements)
    return rows, {
        "existing_coordinate_overlap": overlap,
        "full_overlay_validation": overlay,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
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
