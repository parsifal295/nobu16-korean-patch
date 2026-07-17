#!/usr/bin/env python3
"""Prepare the PC-only base msggame quality-correction review artifact.

This source-gated review has four deliberately narrow corrections.  It reads
only the pristine PC Japanese base resource, the current PC Korean resource,
and installed PC Simplified/Traditional Chinese resources.  Switch Korean is
not read.  The JSONL output is private review evidence below tmp; this script
never writes a game resource.
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
    / "base_msggame_quality_candidates.v2.jsonl"
)
EXISTING_CANDIDATE_ARTIFACTS = (
    REPO / "tmp" / "translation_quality_audit_v1" / "semantic" / "base_msggame_findings.v1.jsonl",
    REPO / "tmp" / "translation_quality_audit_v1" / "semantic" / "base_msggame_additional_findings.v1.jsonl",
    REPO / "tmp" / "translation_quality_audit_v1" / "semantic" / "base_msggame_castle_capture_addendum.v1.jsonl",
    REPO / "tmp" / "translation_quality_audit_v1" / "semantic" / "base_msggame_japanese_punctuation_candidates.v1.jsonl",
)

ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
CHILD_OPCODE_HEX = "024635"


# Definitions pin the current Korean literal, the pristine PC-Japanese literal,
# and the complete PC-SC/TC record context through hashes.  Korean values are
# escaped so tracked workflow code remains source-free.
CASES: dict[str, dict[str, Any]] = {
    "6:4324:0": {
        "proposal": "\uc790\uae30 \uc138\ub825\uc774\ub098 \uc885\uc18d \uc138\ub825\uc758 \uc131\ub9cc \uc120\ud0dd\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4",
        "expected_current": "\uc790\uae30 \uc138\ub825\uc774\ub098 \uc885\uc18d\ud558\ub294 \uc138\ub825\uc758 \uc131\ub9cc \uc120\ud0dd\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4",
        "expected_current_hash": "F1C6631D758CCFB0010F9BB146813581687809128EB31CD98F44BC05BB4107F4",
        "expected_source_hash": "BA9240BD04D4BA100C5BE775881B13A9130B89A689912FEB2BF601E64CC286E6",
        "allowed_substitution": (
            "\uc885\uc18d\ud558\ub294 \uc138\ub825",
            "\uc885\uc18d \uc138\ub825",
        ),
        "expected_layouts": {name: [0] for name in ("jp", "ko", "sc", "tc")},
        "reference_concat_hashes": {
            "sc": "1AD7B3883674ADCF56DFE32F4ACBD1B7CE72031111A94A400E9933A7D7BA693D",
            "tc": "4CDD13BEE551E7C87A979762F6401919F666563772AEB2829D5D38E1F9F33A24",
        },
        "issue_type": "subordinate_faction_modifier_grammar",
        "rationale": (
            "The selection rule means own-faction or subordinate-faction castles. "
            "The current Korean relative clause lacks its governed object; replacing "
            "'\uc885\uc18d\ud558\ub294 \uc138\ub825' with the established noun phrase '\uc885\uc18d \uc138\ub825' "
            "restores the intended UI grammar without changing scope."
        ),
    },
    "6:4505:0": {
        "proposal": "\ub0b4 \uc544\uc774\uc778",
        "expected_current": "\ub0b4 \uc544\uc774\uc5ec,",
        "expected_current_hash": "4927CAC69E7649AED75559EE13DB0AE4E1DF04B52178D265AE923E93749606AF",
        "expected_source_hash": "33F56AAB5B19C95F0BA45D1E5CD1D52C4AAAE3198DCD984F4C7647AE4B0939B2",
        "allowed_substitution": ("\ub0b4 \uc544\uc774\uc5ec,", "\ub0b4 \uc544\uc774\uc778"),
        "expected_layouts": {
            "jp": [0, 1],
            "ko": [0, 1],
            "sc": [0],
            "tc": [0],
        },
        "reference_concat_hashes": {
            "sc": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
            "tc": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        },
        "issue_type": "dynamic_child_name_vocative_to_appositive",
        "rationale": (
            "The dynamic child-name opcode follows the literal.  The current Korean "
            "vocative renders as an address before a subject particle; the appositive "
            "form '\ub0b4 \uc544\uc774\uc778' matches the nearby spouse-message pattern and yields a "
            "grammatical dynamic child-name subject phrase."
        ),
        "family_validation": True,
    },
    "6:4506:0": {
        "proposal": "\ub0b4 \uc544\uc774\uc778",
        "expected_current": "\ub0b4 \uc544\uc774\uc5ec,",
        "expected_current_hash": "4927CAC69E7649AED75559EE13DB0AE4E1DF04B52178D265AE923E93749606AF",
        "expected_source_hash": "33F56AAB5B19C95F0BA45D1E5CD1D52C4AAAE3198DCD984F4C7647AE4B0939B2",
        "allowed_substitution": ("\ub0b4 \uc544\uc774\uc5ec,", "\ub0b4 \uc544\uc774\uc778"),
        "expected_layouts": {
            "jp": [0, 1],
            "ko": [0, 1],
            "sc": [0],
            "tc": [0],
        },
        "reference_concat_hashes": {
            "sc": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
            "tc": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        },
        "issue_type": "dynamic_child_name_vocative_to_appositive",
        "rationale": (
            "The dynamic child-name opcode follows the literal.  The current Korean "
            "vocative renders as an address before an object particle; the appositive "
            "form '\ub0b4 \uc544\uc774\uc778' matches the nearby spouse-message pattern and yields a "
            "grammatical dynamic child-name object phrase."
        ),
        "family_validation": True,
    },
    "8:246:2": {
        "proposal": ")",
        "expected_current": "\uff09",
        "expected_current_hash": "EC2ECD1F00A02E832C0CB995B74CCE568FA3F9DF9BD8654A5816B24E0E20661E",
        "expected_source_hash": "EC2ECD1F00A02E832C0CB995B74CCE568FA3F9DF9BD8654A5816B24E0E20661E",
        "allowed_substitution": ("\uff09", ")"),
        "expected_layouts": {
            "jp": [0, 1, 2],
            "ko": [0, 1, 2],
            "sc": [0, 1, 2, 3],
            "tc": [0, 1, 2],
        },
        "reference_concat_hashes": {
            "sc": "9A8E2739D56C60FC2E996085C42E41EE17CAA6075A410A5FF6CA0733427F8C69",
            "tc": "4515A459BE6EAAB437E8E852250FD51E158A33C9ADAF1F9EE4EA51D92A4FDC65",
        },
        "issue_type": "mixed_width_parenthesis",
        "rationale": (
            "The Korean score summary opens with ASCII '(' in its first literal but "
            "closes with a full-width Japanese parenthesis.  Replacing only the "
            "closing delimiter with ASCII ')' restores a matched Korean delimiter "
            "pair while preserving all dynamic score slots."
        ),
    },
}
SIBLING_APPOSITIVES = {
    "6:4501": "\uc544\ub0b4\uc778",
    "6:4503": "\ub0a8\ud3b8\uc778",
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


def _validate_sibling_contract(archives: dict[str, Any]) -> dict[str, str]:
    actual = {
        coordinate: literal_texts(get_record(archives["ko"], f"{coordinate}:0"))[0]
        for coordinate in SIBLING_APPOSITIVES
    }
    if actual != SIBLING_APPOSITIVES:
        raise ValueError(f"spouse appositive sibling contract drifted: {actual!r}")
    return actual


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
    overlap = sorted(read_existing_coordinates().intersection(CASES), key=coordinate_tuple)
    if overlap:
        raise ValueError(f"candidate coordinates overlap prior artifacts: {overlap}")

    archives, hashes = _load_archives()
    sibling_actual = _validate_sibling_contract(archives)
    rows: list[dict[str, object]] = []
    replacements: dict[tuple[int, int, int], str] = {}

    for coordinate in sorted(CASES, key=coordinate_tuple):
        case = CASES[coordinate]
        block_id, record_id, target_literal_id = coordinate_tuple(coordinate)
        records = {
            name: get_record(archive, coordinate) for name, archive in archives.items()
        }
        texts = {name: literal_texts(record) for name, record in records.items()}
        layouts = {name: list(range(len(value))) for name, value in texts.items()}
        if layouts != case["expected_layouts"]:
            raise ValueError(f"{coordinate}: literal layout drift: {layouts!r}")

        current = texts["ko"][target_literal_id]
        source = texts["jp"][target_literal_id]
        proposal = str(case["proposal"])
        if current != case["expected_current"]:
            raise ValueError(f"{coordinate}: current Korean literal drifted")
        if sha256_utf16le(current) != case["expected_current_hash"]:
            raise ValueError(f"{coordinate}: current Korean literal hash drifted")
        if sha256_utf16le(source) != case["expected_source_hash"]:
            raise ValueError(f"{coordinate}: pristine PC-Japanese literal hash drifted")
        for language, expected_hash in case["reference_concat_hashes"].items():
            if sha256_utf16le("".join(texts[language])) != expected_hash:
                raise ValueError(f"{coordinate}: PC-{language} reference context drifted")

        before, after = case["allowed_substitution"]
        if current.count(before) != 1 or current.replace(before, after, 1) != proposal:
            raise ValueError(f"{coordinate}: proposal exceeds approved substitution")
        if profile(current) != profile(proposal):
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

        family_validation: dict[str, object] | None = None
        if case.get("family_validation"):
            if CHILD_OPCODE_HEX not in before_skeleton.hex():
                raise ValueError(f"{coordinate}: dynamic child-name opcode missing")
            family_validation = {
                "same_dynamic_opcode_sibling_coordinates": ["6:4501", "6:4503"],
                "current_pc_ko_appositive_literals": sibling_actual,
                "status": "spouse_messages_use_appositive_form_before_same_opcode",
            }

        row: dict[str, object] = {
            "coordinate": coordinate,
            "ko": current,
            "proposed_ko": proposal,
            "issue_type": case["issue_type"],
            "rationale": case["rationale"],
            "private_source_text": source,
            "source_text_hash": sha256_utf16le(source),
            "current_hash": sha256_utf16le(current),
            "source_file_sha256": hashes["ko"],
            "native_jp_file_sha256": hashes["jp"],
            "reference_file_sha256": {name: hashes[name] for name in ("sc", "tc")},
            "pc_target_contexts": {
                name: {
                    "literal_texts": texts[name],
                    "literal_concatenation": "".join(texts[name]),
                    "nonliteral_skeleton_sha256": sha256_bytes(
                        nonliteral_skeleton(records[name])
                    ),
                }
                for name in ("sc", "tc")
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
                    "before_skeleton_sha256": sha256_bytes(before_skeleton),
                    "after_skeleton_sha256": sha256_bytes(after_skeleton),
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
        if family_validation is not None:
            row["nearby_family_validation"] = family_validation
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
