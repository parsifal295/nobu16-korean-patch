#!/usr/bin/env python3
"""Prepare a PC-only addendum for high-confidence base msggame quality fixes.

The cases are deliberately narrow: fixed Korean particle agreement after
literal headquarters nouns, several direct particle/meaning corrections, and
six enemy-headquarters boundary repairs.  This workflow reads only pristine
PC Japanese plus installed live PC Korean, Simplified Chinese, and Traditional
Chinese resources.  It never reads Switch Korean and never writes a game
resource; its JSONL output is private review evidence only.
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


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
sys.path.insert(0, str(REPO / "workstreams" / "msggame"))

from msggame_format import (  # noqa: E402
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_with_literals,
    rebuild_record_literals,
)


STOCK_JP = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
    r"\file_only_transaction\steam-jp-1.1.7-v0.8.0"
    r"\originals\MSG\JP\msggame.bin"
)
LIVE_KO = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG\JP\msggame.bin")
REFERENCES = {
    "sc": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG\SC\msggame.bin"),
    "tc": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG\TC\msggame.bin"),
}
EXPECTED_FILE_SHA256 = {
    "jp": "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    "ko": "8DBFCDB21BBDAAD4FE3928AD5B7AAA0D51E56D01F206DFE4D129E354FA5DEDE2",
    "sc": "B2FC3C18DA0F03ACFA93B1EAB0D09FBFCF7CD5076E667602D1AF212953A09BF7",
    "tc": "20E710A11CDADFAF514EBC3B9C664E9C57B1A737138F29BF38CFB6527C0A5E95",
}
OUTPUT = (
    REPO
    / "tmp"
    / "translation_quality_audit_v1"
    / "semantic"
    / "base_msggame_quality_addendum.v1.jsonl"
)
EXISTING_CANDIDATE_ARTIFACTS = (
    REPO / "tmp" / "translation_quality_audit_v1" / "semantic" / "base_msggame_findings.v1.jsonl",
    REPO / "tmp" / "translation_quality_audit_v1" / "semantic" / "base_msggame_additional_findings.v1.jsonl",
    REPO / "tmp" / "translation_quality_audit_v1" / "semantic" / "base_msggame_castle_capture_addendum.v1.jsonl",
    REPO / "tmp" / "translation_quality_audit_v1" / "semantic" / "base_msggame_japanese_punctuation_candidates.v1.jsonl",
    REPO / "tmp" / "translation_quality_audit_v1" / "semantic" / "base_msggame_quality_candidates.v2.jsonl",
)

ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
OPAQUE_GRAMMAR_HEX = "0143"

LAYOUT_TWO = {language: [0, 1] for language in ("jp", "ko", "sc", "tc")}
LAYOUT_TWO_WITH_EMPTY_REFERENCES = {
    "jp": [0, 1],
    "ko": [0, 1],
    "sc": [0],
    "tc": [0],
}
LAYOUT_SINGLE = {language: [0] for language in ("jp", "ko", "sc", "tc")}
LAYOUT_DIRECT_FACILITY = {
    "jp": [0, 1],
    "ko": [0, 1],
    "sc": [0, 1, 2],
    "tc": [0, 1, 2],
}


# These particles follow Korean nouns already spelled in the preceding literal.
# They are not runtime-name fallbacks: the noun's final Hangul syllable makes the
# correct particle deterministic.  Every coordinate is explicitly allowlisted.
STATIC_HEADQUARTERS_PREFIXES: dict[str, tuple[str, str]] = {
    "7:645:1": ("\uc774 ", "\uac00 "),
    "7:647:1": ("\uc744 ", "\ub97c "),
    "7:648:1": ("\uc740(\ub294) ", "\ub294 "),
    "7:649:1": ("\uc744 ", "\ub97c "),
    "7:652:1": ("\uc774 ", "\uac00 "),
    "7:653:1": ("\uc774 ", "\uac00 "),
    "7:655:1": ("\uc744 ", "\ub97c "),
    "7:656:1": ("\uc740(\ub294) ", "\ub294 "),
    "7:657:1": ("\uc744 ", "\ub97c "),
    "7:658:1": ("\uc740(\ub294) ", "\ub294 "),
    "7:661:1": ("\uc774 ", "\uac00 "),
    "7:662:1": ("\uc740(\ub294) ", "\ub294 "),
    "7:667:1": ("\uc740(\ub294) ", "\ub294 "),
    "7:668:1": ("\uc740(\ub294) ", "\ub294 "),
    "7:669:1": ("\uc744 ", "\ub97c "),
    "7:670:1": ("\uc744 ", "\ub97c "),
    "7:673:1": ("\uc744 ", "\ub97c "),
    "7:674:1": ("\uc73c\ub85c ", "\ub85c "),
    "7:676:1": ("\uc744 ", "\ub97c "),
    "7:678:1": ("\uc740(\ub294) ", "\ub294 "),
    "7:679:1": ("\uc744 ", "\ub97c "),
    "7:683:1": ("\uc774 ", "\uac00 "),
    "7:684:1": ("\uc744 ", "\ub97c "),
    "7:752:1": ("\uc744 ", "\ub97c "),
    "7:753:1": ("\uc740(\ub294) ", "\ub294 "),
    "7:754:1": ("\uc774 ", "\uac00 "),
    "7:757:1": ("\uc740(\ub294) ", "\ub294 "),
    "7:758:1": ("\uc774 ", "\uac00 "),
    "7:760:1": ("\uc740(\ub294) ", "\ub294 "),
    "7:763:1": ("\uc740(\ub294) ", "\ub294 "),
    "7:764:1": ("\uc744 ", "\ub97c "),
    "7:765:1": ("\uc740(\ub294) ", "\ub294 "),
    "7:767:1": ("\uc740(\ub294) ", "\ub294 "),
    "7:771:1": ("\uc740(\ub294) ", "\ub294 "),
    "7:774:1": ("\uc744 ", "\ub97c "),
    "7:775:1": ("\uc744 ", "\ub97c "),
    "7:778:1": ("\uc744 ", "\ub97c "),
    "7:779:1": ("\uc740(\ub294) ", "\ub294 "),
    "7:782:1": ("\uc744 ", "\ub97c "),
    "7:783:1": ("\uc740(\ub294) ", "\ub294 "),
    "7:788:1": ("\uc744 ", "\ub97c "),
    "7:789:1": ("\uc740(\ub294) ", "\ub294 "),
}
STATIC_EMPTY_REFERENCE_COORDINATES = {
    "7:661:1",
    "7:662:1",
    "7:673:1",
    "7:674:1",
    "7:676:1",
    "7:679:1",
    "7:683:1",
    "7:684:1",
    "7:767:1",
    "7:778:1",
    "7:779:1",
    "7:782:1",
    "7:788:1",
    "7:789:1",
}


DIRECT_CASES: dict[str, dict[str, Any]] = {
    "6:4310:1": {
        "expected_current": "\ub97c \uac74\uc124\ud588\uc2b5\ub2c8\ub2e4",
        "proposal": "\uc744 \uac74\uc124\ud588\uc2b5\ub2c8\ub2e4",
        "expected_layouts": LAYOUT_DIRECT_FACILITY,
        "issue_type": "fixed_facility_object_particle",
        "rationale": (
            "The preceding Korean literal spells the fixed vowel-final noun phrase "
            "for a castle-town facility.  The following object particle must be "
            "'\uc744', matching the PC Japanese construction statement and both PC Chinese references."
        ),
    },
    "7:383:1": {
        "expected_current": "\uc744 \uc785\uc218",
        "proposal": "\ub97c \uc785\uc218",
        "expected_layouts": LAYOUT_DIRECT_FACILITY,
        "issue_type": "fixed_heirloom_object_particle",
        "rationale": (
            "The preceding literal contains the fixed vowel-final Korean noun '\uac00\ubcf4'. "
            "Its object particle is '\ub97c', consistent with the Japanese acquisition statement "
            "and the PC Chinese reference contexts."
        ),
    },
    "7:399:0": {
        "expected_current": "\uc0b4\uc544\uc11c \ub3cc\uc544\uac00\ub9ac\ub77c \uc5ec\uacbc\ub354\ub0d0",
        "proposal": "\uc0b4\uc544\uc11c \ub3cc\uc544\uac08 \uc218 \uc788\uc744 \uc904\uc774\uc57c",
        "expected_layouts": LAYOUT_SINGLE,
        "issue_type": "return_alive_semantic_direction",
        "rationale": (
            "The Japanese line expresses surprise that someone could return alive; "
            "both PC Chinese references preserve that possibility.  The current Korean "
            "instead says that the speaker expected to return alive, reversing the sense."
        ),
    },
    "7:2138:0": {
        "expected_current": "\ud6c4\uc6d0\uad70\uc774 \ub3c4\ucc29\ud558\uae30 \uc804\uc5d0\n\ub5a8\uc5b4\ub728\ub9ac\uba74 \ub429\ub2c8\ub2e4",
        "proposal": "\ud6c4\uc6d0\uad70\uc774 \ub3c4\ucc29\ud558\uae30 \uc804\uc5d0\n\ud568\ub77d\ud558\uba74 \ub429\ub2c8\ub2e4",
        "expected_layouts": LAYOUT_SINGLE,
        "issue_type": "castle_capture_action_terminology",
        "rationale": (
            "The PC Japanese and both PC Chinese texts say to capture the castle before "
            "reinforcements arrive.  The Korean siege-action verb is normalized to "
            "'\ud568\ub77d\ud558\ub2e4', preserving the existing line break."
        ),
    },
}


# Five word-boundary fixes and one missing object particle.  They deliberately
# alter literal-edge whitespace only; the concatenated rendered sentence gains
# exactly the missing Korean boundary.
ENEMY_HEADQUARTERS_BOUNDARY_CASES: dict[str, dict[str, Any]] = {
    "7:756:0": {
        "expected_current": "\uc801 \ubcf8\uac70",
        "proposal": "\uc801 \ubcf8\uac70 ",
        "expected_layouts": LAYOUT_TWO,
        "issue_type": "enemy_headquarters_compound_word_boundary",
        "rationale": (
            "The Japanese source uses the compound for an enemy-headquarters attack. "
            "The adjacent Korean literals concatenate as one run-on noun; one boundary "
            "space restores '\uc801 \ubcf8\uac70 \uacf5\ub7b5'."
        ),
    },
    "7:766:0": {
        "expected_current": "\uc801 \ubcf8\uac70",
        "proposal": "\uc801 \ubcf8\uac70 ",
        "expected_layouts": LAYOUT_TWO,
        "issue_type": "enemy_headquarters_compound_word_boundary",
        "rationale": (
            "The adjacent Korean literals render the enemy-headquarters attack as a "
            "run-on compound.  Add the single missing Korean word boundary."
        ),
    },
    "7:770:0": {
        "expected_current": "\uc801 \ubcf8\uac70",
        "proposal": "\uc801 \ubcf8\uac70 ",
        "expected_layouts": LAYOUT_TWO_WITH_EMPTY_REFERENCES,
        "issue_type": "enemy_headquarters_compound_word_boundary",
        "rationale": (
            "The adjacent Korean literals render the enemy-headquarters attack as a "
            "run-on compound.  Add the single missing Korean word boundary."
        ),
    },
    "7:772:1": {
        "expected_current": "\ud568\ub77d\uc2dc\ucf30\ub2e4!",
        "proposal": "\ub97c \ud568\ub77d\uc2dc\ucf30\ub2e4!",
        "expected_layouts": LAYOUT_TWO,
        "issue_type": "enemy_headquarters_missing_object_particle",
        "rationale": (
            "The preceding literal is the fixed vowel-final phrase '\uc801 \ubcf8\uac70'. "
            "The Japanese source says that it was captured; adding '\ub97c ' yields the "
            "grammatical Korean sentence '\uc801 \ubcf8\uac70\ub97c \ud568\ub77d\uc2dc\ucf30\ub2e4!'."
        ),
    },
    "7:781:0": {
        "expected_current": "\uc801 \ubcf8\uac70",
        "proposal": "\uc801 \ubcf8\uac70 ",
        "expected_layouts": LAYOUT_TWO_WITH_EMPTY_REFERENCES,
        "issue_type": "enemy_headquarters_compound_word_boundary",
        "rationale": (
            "The adjacent Korean literals render the enemy-headquarters attack as a "
            "run-on compound.  Add the single missing Korean word boundary."
        ),
    },
    "7:784:0": {
        "expected_current": "\uc801 \ubcf8\uac70",
        "proposal": "\uc801 \ubcf8\uac70 ",
        "expected_layouts": LAYOUT_TWO,
        "issue_type": "enemy_headquarters_compound_word_boundary",
        "rationale": (
            "The adjacent Korean literals render the enemy-headquarters attack as a "
            "run-on compound.  Add the single missing Korean word boundary."
        ),
    },
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_utf16le(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def coordinate_key(block_id: int, record_id: int, literal_id: int) -> str:
    return f"{block_id}:{record_id}:{literal_id}"


def coordinate_tuple(coordinate: str) -> tuple[int, int, int]:
    values = tuple(int(part) for part in coordinate.split(":"))
    if len(values) != 3:
        raise ValueError(f"invalid literal coordinate: {coordinate}")
    return values


def literal_texts(record: MsgGameRecord) -> list[str]:
    return [literal.text for literal in parse_record_literals(record)]


def nonliteral_skeleton(record: MsgGameRecord) -> bytes:
    output = bytearray()
    cursor = 0
    for literal in parse_record_literals(record):
        output.extend(record.data[cursor : literal.marker_offset])
        output.extend(f"<L{literal.literal_id}>".encode("ascii"))
        cursor = literal.marker_end
    output.extend(record.data[cursor:])
    return bytes(output)


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
        "question_marks": text.count("?"),
    }


def profile_without_outer_whitespace(text: str) -> dict[str, object]:
    value = profile(text)
    value.pop("outer_ascii_whitespace")
    return value


def get_record(archive: Any, coordinate: str) -> MsgGameRecord:
    block_id, record_id, _literal_id = coordinate_tuple(coordinate)
    return archive.blocks[block_id].records[record_id]


def read_existing_coordinates() -> set[str]:
    result: set[str] = set()
    for path in EXISTING_CANDIDATE_ARTIFACTS:
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


def _load_archives() -> tuple[dict[str, Any], dict[str, str]]:
    paths = {"jp": STOCK_JP, "ko": LIVE_KO, **REFERENCES}
    hashes = {name: sha256_bytes(path.read_bytes()) for name, path in paths.items()}
    if hashes != EXPECTED_FILE_SHA256:
        raise ValueError(f"PC input file hash drift: {hashes!r}")
    archives = {
        name: parse_packed_msggame(path.read_bytes()).archive for name, path in paths.items()
    }
    return archives, hashes


def build_cases() -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}
    for coordinate, (old_prefix, new_prefix) in STATIC_HEADQUARTERS_PREFIXES.items():
        cases[coordinate] = {
            "kind": "static_particle",
            "old_prefix": old_prefix,
            "new_prefix": new_prefix,
            "expected_layouts": (
                LAYOUT_TWO_WITH_EMPTY_REFERENCES
                if coordinate in STATIC_EMPTY_REFERENCE_COORDINATES
                else LAYOUT_TWO
            ),
            "issue_type": "static_headquarters_particle_concordance",
            "rationale": (
                "The preceding Korean literal itself spells a fixed headquarters noun, "
                "whose final syllable is vowel-final.  Resolve the following particle "
                "deterministically instead of retaining the ungrammatical form."
            ),
        }
    for source, target in DIRECT_CASES.items():
        cases[source] = {"kind": "direct", **target}
    for source, target in ENEMY_HEADQUARTERS_BOUNDARY_CASES.items():
        cases[source] = {
            "kind": "boundary",
            "allow_target_outer_whitespace_change": True,
            **target,
        }
    return cases


def resolve_proposal(case: dict[str, Any], current: str) -> str:
    if case["kind"] == "static_particle":
        old_prefix = str(case["old_prefix"])
        new_prefix = str(case["new_prefix"])
        if not current.startswith(old_prefix):
            raise ValueError(
                f"static particle current literal does not start with {old_prefix!r}"
            )
        return new_prefix + current[len(old_prefix) :]
    expected_current = str(case["expected_current"])
    if current != expected_current:
        raise ValueError(
            f"current Korean literal drifted: {current!r} != {expected_current!r}"
        )
    return str(case["proposal"])


def validate_case_shape(
    coordinate: str,
    case: dict[str, Any],
    records: dict[str, MsgGameRecord],
    texts: dict[str, list[str]],
) -> None:
    layouts = {name: list(range(len(value))) for name, value in texts.items()}
    if layouts != case["expected_layouts"]:
        raise ValueError(f"{coordinate}: literal layout drift: {layouts!r}")
    skeleton = nonliteral_skeleton(records["ko"])
    if OPAQUE_GRAMMAR_HEX in skeleton.hex():
        raise ValueError(f"{coordinate}: opaque grammar opcode must remain a hold")
    if case["kind"] == "static_particle":
        target_literal_id = coordinate_tuple(coordinate)[2]
        if target_literal_id == 0:
            raise ValueError(f"{coordinate}: static particle target must follow a literal")
        preceding = texts["ko"][target_literal_id - 1]
        if not preceding.rstrip().endswith(("\ubcf8\uac70", "\ubcf8\uac70\uc9c0")):
            raise ValueError(
                f"{coordinate}: preceding Korean literal is not a fixed headquarters noun"
            )


def _validate_full_overlay(
    source_packed: bytes,
    expected_replacements: dict[tuple[int, int, int], str],
) -> dict[str, object]:
    before = parse_packed_msggame(source_packed).archive
    rebuilt_packed = rebuild_packed_with_literals(source_packed, expected_replacements)
    after = parse_packed_msggame(rebuilt_packed).archive
    changed: list[str] = []
    for before_block, after_block in zip(before.blocks, after.blocks):
        if len(before_block.records) != len(after_block.records):
            raise ValueError("full overlay changed record count")
        for before_record, after_record in zip(before_block.records, after_block.records):
            if nonliteral_skeleton(before_record) != nonliteral_skeleton(after_record):
                raise ValueError(
                    "full overlay changed nonliteral bytecode at "
                    f"{before_record.block_id}:{before_record.record_id}"
                )
            before_texts = literal_texts(before_record)
            after_texts = literal_texts(after_record)
            if len(before_texts) != len(after_texts):
                raise ValueError("full overlay changed literal count")
            for literal_id, (old, new) in enumerate(zip(before_texts, after_texts)):
                if old != new:
                    changed.append(
                        coordinate_key(before_record.block_id, before_record.record_id, literal_id)
                    )
    expected = sorted(
        (coordinate_key(*coordinate) for coordinate in expected_replacements),
        key=coordinate_tuple,
    )
    actual = sorted(changed, key=coordinate_tuple)
    if actual != expected:
        raise ValueError(f"full overlay changed unexpected literals: {actual!r}")
    return {
        "source_sha256": sha256_bytes(source_packed),
        "rebuilt_sha256": sha256_bytes(rebuilt_packed),
        "changed_coordinates": actual,
        "all_nonliteral_skeletons_unchanged": True,
    }


def build_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    cases = build_cases()
    overlap = sorted(read_existing_coordinates().intersection(cases), key=coordinate_tuple)
    if overlap:
        raise ValueError(f"candidate coordinates overlap prior artifacts: {overlap}")

    archives, hashes = _load_archives()
    rows: list[dict[str, object]] = []
    replacements: dict[tuple[int, int, int], str] = {}

    for coordinate in sorted(cases, key=coordinate_tuple):
        case = cases[coordinate]
        block_id, record_id, target_literal_id = coordinate_tuple(coordinate)
        records = {
            name: get_record(archive, coordinate) for name, archive in archives.items()
        }
        texts = {name: literal_texts(record) for name, record in records.items()}
        validate_case_shape(coordinate, case, records, texts)

        current = texts["ko"][target_literal_id]
        proposal = resolve_proposal(case, current)
        source = texts["jp"][target_literal_id]
        if current == proposal:
            raise ValueError(f"{coordinate}: proposal is a no-op")

        before_target_profile = profile(current)
        after_target_profile = profile(proposal)
        if (
            case.get("allow_target_outer_whitespace_change")
            and before_target_profile != after_target_profile
        ):
            if profile_without_outer_whitespace(current) != profile_without_outer_whitespace(
                proposal
            ):
                raise ValueError(f"{coordinate}: target format profile changed")
        elif before_target_profile != after_target_profile:
            raise ValueError(f"{coordinate}: target literal format profile changed")

        before_literals = texts["ko"]
        after_literals = list(before_literals)
        after_literals[target_literal_id] = proposal
        before_full = "".join(before_literals)
        after_full = "".join(after_literals)
        if profile(before_full) != profile(after_full):
            raise ValueError(f"{coordinate}: whole-record format profile changed")

        before_skeleton = nonliteral_skeleton(records["ko"])
        rebuilt_record = MsgGameRecord(
            block_id=records["ko"].block_id,
            record_id=records["ko"].record_id,
            relative_offset=records["ko"].relative_offset,
            data=rebuild_record_literals(records["ko"], {target_literal_id: proposal}),
        )
        if literal_texts(rebuilt_record) != after_literals:
            raise ValueError(f"{coordinate}: record literal rebuild mismatch")
        after_skeleton = nonliteral_skeleton(rebuilt_record)
        if before_skeleton != after_skeleton:
            raise ValueError(f"{coordinate}: nonliteral bytecode changed")

        row: dict[str, object] = {
            "coordinate": coordinate,
            "ko": current,
            "proposed_ko": proposal,
            "issue_type": case["issue_type"],
            "rationale": case["rationale"],
            "private_source_text": source,
            "source_text_hash": sha256_utf16le(source),
            "current_hash": sha256_utf16le(current),
            "proposed_hash": sha256_utf16le(proposal),
            "source_file_sha256": hashes["ko"],
            "native_jp_file_sha256": hashes["jp"],
            "reference_file_sha256": {name: hashes[name] for name in ("sc", "tc")},
            "pc_language_contexts": {
                name: {
                    "literal_texts": texts[name],
                    "literal_concatenation": "".join(texts[name]),
                    "literal_concatenation_hash": sha256_utf16le("".join(texts[name])),
                    "nonliteral_skeleton_sha256": sha256_bytes(
                        nonliteral_skeleton(records[name])
                    ),
                }
                for name in ("jp", "sc", "tc")
            },
            "linked_record_contract": {
                "status": "whole_literal_sequence_newline_runtime_slots_and_nonliteral_bytecode_validated",
                "literal_layouts": {
                    name: list(range(len(value))) for name, value in texts.items()
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
                    "before_skeleton_sha256": sha256_bytes(before_skeleton),
                    "after_skeleton_sha256": sha256_bytes(after_skeleton),
                },
            },
            "format_validation": {
                "escape_tags": "match",
                "runtime_tokens": "match",
                "printf": "match",
                "newlines": "match",
                "outer_ascii_whitespace": (
                    "intentional_literal_boundary_space_only"
                    if (
                        case.get("allow_target_outer_whitespace_change")
                        and before_target_profile != after_target_profile
                    )
                    else "match"
                ),
                "question_marks": "unchanged",
            },
        }
        if case["kind"] == "static_particle":
            row["static_particle_contract"] = {
                "preceding_ko_literal": before_literals[target_literal_id - 1],
                "current_prefix": case["old_prefix"],
                "proposed_prefix": case["new_prefix"],
                "status": "fixed_literal_head_is_vowel_final_and_particle_is_deterministic",
            }
        if (
            case.get("allow_target_outer_whitespace_change")
            and before_target_profile != after_target_profile
        ):
            # These five allowlisted slot-0 edits add the one ASCII separator
            # required before the unchanged next literal.  The full joined
            # record and unchanged bytecode are already pinned above; the
            # generic builder admits this narrow profile delta only through
            # its matching base-msggame adjacency contract.
            row["allowed_format_delta"] = ["trailing_whitespace"]
        rows.append(row)
        replacements[(block_id, record_id, target_literal_id)] = proposal

    overlay = _validate_full_overlay(LIVE_KO.read_bytes(), replacements)
    return rows, {
        "existing_coordinate_overlap": overlap,
        "full_overlay_validation": overlay,
    }


def serialize(rows: list[dict[str, object]]) -> bytes:
    return b"".join(
        json.dumps(row, ensure_ascii=True, separators=(",", ":")).encode("utf-8") + b"\n"
        for row in rows
    )


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


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
        payload = serialize(rows)
        if OUTPUT.is_file() and OUTPUT.read_bytes() == payload:
            status = "already_current"
        else:
            atomic_write(OUTPUT, payload)
            status = "written"
        print(
            json.dumps(
                {
                    "output": str(OUTPUT),
                    "row_count": len(rows),
                    "sha256": sha256_bytes(payload),
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
