#!/usr/bin/env python3
"""Build three isolated, PC-only translation-quality candidate records.

This is deliberately an evidence builder, not an applicator.  It reads the
pristine PC Japanese sources, the installed PC Korean targets, and installed
PC EN/SC/TC context only.  Switch Korean and historical Korean backups are
never opened.  The sole output is a private JSONL candidate file under tmp;
no game file, generic builder, Steam installation, or release artifact is
written.
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
from pathlib import Path
from typing import Any, Callable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp"
OUTPUT = (
    TMP_ROOT
    / "translation_quality_residual_three_pc_only_v1"
    / "private_candidates.v1.jsonl"
)
STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
LOCAL_PRISTINE_BASE_JP = Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin")
PC_ORIGINAL_ROOT = (
    STEAM_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
)
LAYOUT_V2_SCRIPT = (
    REPO
    / "workstreams"
    / "steam_jp_msgev_full_layout_v2"
    / "build_steam_jp_msgev_full_layout_v2.py"
)

SCHEMA = "nobu16.kr.translation-quality-residual-three.pc-only.v1"
REVIEW_BATCH = "translation_quality_residual_three_pc_only_v1"
MAX_EVENT_LINES = 3
MAX_EVENT_LINE_PX = 912

ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")


def u(value: str) -> str:
    """Decode only the explicit ASCII escapes used in this source file."""

    def replace(match: re.Match[str]) -> str:
        token = match.group(1)
        if token == "n":
            return "\n"
        if token == "r":
            return "\r"
        if token == "t":
            return "\t"
        return chr(int(token[1:], 16))

    return re.sub(r"\\(x[0-9A-Fa-f]{2}|u[0-9A-Fa-f]{4}|[nrt])", replace, value)


# Every expected file hash is a gate, not a source of translation authority.
# The installed Korean file hashes and literal hashes make the candidates fail
# closed if an overlapping patch is applied before review.
FILE_SPECS: dict[str, dict[str, Any]] = {
    "base_jp": {
        "path": LOCAL_PRISTINE_BASE_JP,
        "sha256": "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    },
    "base_ko": {
        "path": STEAM_ROOT / "MSG" / "JP" / "msggame.bin",
        "sha256": "8DBFCDB21BBDAAD4FE3928AD5B7AAA0D51E56D01F206DFE4D129E354FA5DEDE2",
    },
    "base_sc": {
        "path": STEAM_ROOT / "MSG" / "SC" / "msggame.bin",
        "sha256": "B2FC3C18DA0F03ACFA93B1EAB0D09FBFCF7CD5076E667602D1AF212953A09BF7",
    },
    "base_tc": {
        "path": STEAM_ROOT / "MSG" / "TC" / "msggame.bin",
        "sha256": "20E710A11CDADFAF514EBC3B9C664E9C57B1A737138F29BF38CFB6527C0A5E95",
    },
    "pk_jp": {
        "path": PC_ORIGINAL_ROOT / "MSG_PK" / "JP" / "msggame.bin",
        "sha256": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    },
    "pk_ko": {
        "path": STEAM_ROOT / "MSG_PK" / "JP" / "msggame.bin",
        "sha256": "DE606E50C9A6241BD0B85D17A000394007952093984F75DB56E296E0CCDE6B01",
    },
    "pk_en": {
        "path": STEAM_ROOT / "MSG_PK" / "EN" / "msggame.bin",
        "sha256": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    },
    "pk_sc": {
        "path": STEAM_ROOT / "MSG_PK" / "SC" / "msggame.bin",
        "sha256": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    },
    "pk_tc": {
        "path": STEAM_ROOT / "MSG_PK" / "TC" / "msggame.bin",
        "sha256": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
    },
    "msgev_jp": {
        "path": PC_ORIGINAL_ROOT / "MSG_PK" / "JP" / "msgev.bin",
        "sha256": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
    },
    "msgev_ko": {
        "path": STEAM_ROOT / "MSG_PK" / "JP" / "msgev.bin",
        "sha256": "B8B3B1C5A635419E590DB866C240A1B6609799E0FEA0E69F86D6208F27E5C52B",
    },
    "msgev_en": {
        "path": STEAM_ROOT / "MSG_PK" / "EN" / "msgev.bin",
        "sha256": "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E",
    },
    "msgev_sc": {
        "path": STEAM_ROOT / "MSG_PK" / "SC" / "msgev.bin",
        "sha256": "7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA",
    },
    "msgev_tc": {
        "path": STEAM_ROOT / "MSG_PK" / "TC" / "msgev.bin",
        "sha256": "89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6",
    },
}

BASE_EN_MSGGAME = STEAM_ROOT / "MSG" / "EN" / "msggame.bin"

MSGGAME_CASES: tuple[dict[str, Any], ...] = (
    {
        "resource_key": "base",
        "resource": "MSG/JP/msggame.bin",
        "coordinate": "8:937:2",
        "jp_file": "base_jp",
        "ko_file": "base_ko",
        "context_files": {"en": None, "sc": "base_sc", "tc": "base_tc"},
        "expected_source": u(r"\n\u6025\u304e\u624b\u914d"),
        "expected_current": u(r"\n\uae09\ud788 \uc218\ubc30\ud558"),
        "proposal": u(r"\n\uae09\ud788 \uc900\ube44\ud558"),
        "expected_source_hash": "B81A69F9107FA0D50DE512E9D13ABA43B6F99782501C5BE2C7A1E19754798707",
        "expected_current_hash": "96EC6BC9CC9291DA1B9B5B20F7AEB4D73A43431A75DE8B9A98E1CB70F9DC1D78",
        "expected_proposal_hash": "BC91DF60F73730D1395CEABDAA65B6CF9D94B94C14CCA0693B61B9EE96977E79",
        "context_hashes": {
            "sc": "FAB70902F9A20656AF26C9B8156F1EC9A6FFB6B868A3EDFD3DD3113601CAA8C4",
            "tc": "88D77E99DB8C4777926BBF19ADE89D0D51BD2DC163A97C2A624F12EE27577552",
        },
        "rationale": (
            "The pristine PC Japanese says to make arrangements immediately. "
            "PC SC explicitly says to begin preparation promptly, while PC TC "
            "says to proceed at once.  Replace the unrelated recruitment-like "
            "wording with prepare promptly."
        ),
    },
    {
        "resource_key": "pk",
        "resource": "MSG_PK/JP/msggame.bin",
        "coordinate": "8:949:2",
        "jp_file": "pk_jp",
        "ko_file": "pk_ko",
        "context_files": {"en": "pk_en", "sc": "pk_sc", "tc": "pk_tc"},
        "expected_source": u(r"\n\u6025\u304e\u624b\u914d"),
        "expected_current": u(r"\n\uae09\ud788 \uc218\ubc30\ud558"),
        "proposal": u(r"\n\uae09\ud788 \uc900\ube44\ud558"),
        "expected_source_hash": "B81A69F9107FA0D50DE512E9D13ABA43B6F99782501C5BE2C7A1E19754798707",
        "expected_current_hash": "96EC6BC9CC9291DA1B9B5B20F7AEB4D73A43431A75DE8B9A98E1CB70F9DC1D78",
        "expected_proposal_hash": "BC91DF60F73730D1395CEABDAA65B6CF9D94B94C14CCA0693B61B9EE96977E79",
        "context_hashes": {
            "sc": "FAB70902F9A20656AF26C9B8156F1EC9A6FFB6B868A3EDFD3DD3113601CAA8C4",
            "tc": "88D77E99DB8C4777926BBF19ADE89D0D51BD2DC163A97C2A624F12EE27577552",
        },
        "rationale": (
            "The pristine PC Japanese is identical to the base-PC coordinate. "
            "PC SC and TC again mean immediate preparation/proceeding.  The PK "
            "EN file exists but this coordinate is absent, so it is recorded as "
            "unavailable rather than inferred.  The matching base-PC Japanese "
            "coordinate is included as source-only corroboration."
        ),
    },
)

MSGEV_CASE = {
    "resource": "MSG_PK/JP/msgev.bin",
    "id": 7256,
    "expected_source": u(
        r"\u9762\u767d\u3044\u3001\u306a\u3089\u3070\u95a2\u767d\u304c\u76f8\u624b\u3058\u3083\uff01"
        r"\n\x1bCC\u56db\u56fd\x1bCZ\u3092\u4e0a\u56de\u308b\u5927\u8ecd\u3067"
        r"\x1bCB\u5cf6\u6d25\x1bCZ\u3092\u6210\u6557\u305b\u3088\uff01"
    ),
    "expected_current": u(
        r"\uc7ac\ubbf8\uc788\uad70, \uadf8\ub807\ub2e4\uba74 \uad00\ubc31\uc774 \uc0c1\ub300\ub2e4!"
        r"\n\x1bCC\uc2dc\ucf54\ucfe0\x1bCZ\ub97c \uc6c3\ub3c4\ub294 \ub300\uad70\uc73c\ub85c"
        r"\n\x1bCB\uc2dc\ub9c8\uc988\x1bCZ\ub97c \uc131\ud328\ud558\ub77c!"
    ),
    "proposal": u(
        r"\uc7ac\ubbf8\uc788\uad70, \uadf8\ub807\ub2e4\uba74 \uad00\ubc31\uc774 \uc0c1\ub300\ub2e4!"
        r"\n\x1bCC\uc2dc\ucf54\ucfe0\x1bCZ\ub97c \uc6c3\ub3c4\ub294 \ub300\uad70\uc73c\ub85c"
        r"\n\x1bCB\uc2dc\ub9c8\uc988\x1bCZ\ub97c \ucc98\ub2e8\ud558\ub77c!"
    ),
    "expected_source_hash": "9D53236E7E9BAF8BADBF8E8EAE318BFEFAFEA1F9681B74E5220B974AAC760D01",
    "expected_current_hash": "F544EE2D262D7B7A832A470B69BE8FAA698A7C28BE7059B313E09ACC72939A4D",
    "expected_proposal_hash": "6B8750BB63961F5965525C1CD8AE7751EB2F3614FF1CADB2DABB2931AD743B65",
    "context_hashes": {
        "en": "C629AE68D05AA61131B30797C0F0343C43018BCC0428A2D394EFAB8A99B5B934",
        "sc": "1377EC17D44BDDE02B977D705A83344A58AD7C46027ADB50484678C4CD128CC0",
        "tc": "34F3F60D9B31B33929FA9C25B2359ED49526065C9817A6AB15AC95A7266647B6",
    },
    "rationale": (
        "The Japanese uses the punitive command to bring Shimazu to justice. "
        "PC EN says Shimazu will be brought to justice; PC SC and TC respectively "
        "say punish and sanction.  Replace the malformed current verb with "
        "the direct punitive command."
    ),
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def require_file(key: str) -> tuple[Path, str]:
    spec = FILE_SPECS[key]
    path = Path(spec["path"])
    if not path.is_file():
        raise RuntimeError(f"required PC input is missing: {key}: {path}")
    actual = sha256_file(path)
    expected = str(spec["sha256"])
    if actual != expected:
        raise RuntimeError(
            f"PC input hash drift at {key}: expected {expected}, got {actual}"
        )
    return path, actual


def load_module(name: str, path: Path) -> Any:
    module_spec = importlib.util.spec_from_file_location(name, path)
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError(f"cannot load support module: {path}")
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[name] = module
    module_spec.loader.exec_module(module)
    return module


MSGGAME = load_module(
    "translation_quality_residual_three_msggame",
    REPO / "workstreams" / "msggame" / "msggame_format.py",
)
LZ4 = load_module("translation_quality_residual_three_lz4", REPO / "tools" / "nobu16_lz4.py")
MESSAGE = load_module(
    "translation_quality_residual_three_message",
    REPO / "tools" / "nobu16_msg_table.py",
)


def coordinate_tuple(value: str) -> tuple[int, int, int]:
    parts = tuple(int(part) for part in value.split(":"))
    if len(parts) != 3:
        raise RuntimeError(f"invalid msggame coordinate: {value}")
    return parts


def msggame_rows(path: Path) -> tuple[Any, dict[str, str]]:
    archive = MSGGAME.parse_packed_msggame(path.read_bytes()).archive
    rows = {
        f"{literal.block_id}:{literal.record_id}:{literal.literal_id}": literal.text
        for literal in MSGGAME.iter_literals(archive)
    }
    return archive, rows


def common_rows(path: Path) -> tuple[str, ...]:
    _header, raw = LZ4.decompress_wrapper(path.read_bytes())
    return MESSAGE.parse_message_table(raw).texts


def ascii_outer_whitespace(value: str) -> dict[str, str]:
    return {
        "leading": value[: len(value) - len(value.lstrip(" \t"))],
        "trailing": value[len(value.rstrip(" \t")) :],
    }


def format_profile(value: str) -> dict[str, Any]:
    return {
        "escape_tokens": ESC_RE.findall(value),
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": PRINTF_RE.findall(value),
        "linebreak_sequence": LINEBREAK_RE.findall(value),
        "outer_ascii_whitespace": ascii_outer_whitespace(value),
        "other_controls": [
            f"U+{ord(character):04X}"
            for character in value
            if ord(character) < 32 and character not in {"\x1b", "\n", "\r", "\t"}
        ],
    }


def record_for_coordinate(archive: Any, coordinate: str) -> Any:
    block_id, record_id, _literal_id = coordinate_tuple(coordinate)
    try:
        return archive.blocks[block_id].records[record_id]
    except IndexError as exc:
        raise RuntimeError(f"missing msggame record at {coordinate}") from exc


def nonliteral_skeleton(record: Any) -> bytes:
    output = bytearray()
    cursor = 0
    for literal in MSGGAME.parse_record_literals(record):
        output.extend(record.data[cursor : literal.marker_offset])
        output.extend(f"<L{literal.literal_id}>".encode("ascii"))
        cursor = literal.marker_end
    output.extend(record.data[cursor:])
    return bytes(output)


def msggame_join_safety(
    archive: Any,
    coordinate: str,
    current: str,
    proposal: str,
) -> dict[str, Any]:
    block_id, record_id, literal_id = coordinate_tuple(coordinate)
    record = record_for_coordinate(archive, coordinate)
    before = MSGGAME.parse_record_literals(record)
    if literal_id >= len(before):
        raise RuntimeError(f"target literal does not exist at {coordinate}")
    before_texts = [literal.text for literal in before]
    if before_texts[literal_id] != current:
        raise RuntimeError(f"current literal differs before msggame rebuild at {coordinate}")
    rebuilt_bytes = MSGGAME.rebuild_record_literals(record, {literal_id: proposal})
    rebuilt_record = MSGGAME.MsgGameRecord(
        block_id=block_id,
        record_id=record_id,
        relative_offset=record.relative_offset,
        data=rebuilt_bytes,
    )
    after = MSGGAME.parse_record_literals(rebuilt_record)
    after_texts = [literal.text for literal in after]
    if len(before_texts) != len(after_texts):
        raise RuntimeError(f"literal count changes at {coordinate}")
    if after_texts[literal_id] != proposal:
        raise RuntimeError(f"proposal did not rebuild at {coordinate}")
    if any(
        before_text != after_text
        for index, (before_text, after_text) in enumerate(zip(before_texts, after_texts, strict=True))
        if index != literal_id
    ):
        raise RuntimeError(f"non-target literal changed at {coordinate}")
    before_skeleton = nonliteral_skeleton(record)
    after_skeleton = nonliteral_skeleton(rebuilt_record)
    if before_skeleton != after_skeleton:
        raise RuntimeError(f"nonliteral msggame bytecode changed at {coordinate}")

    before_join = "".join(before_texts)
    after_join = "".join(after_texts)
    return {
        "record_coordinate": f"{block_id}:{record_id}",
        "target_literal_id": literal_id,
        "literal_count": len(before_texts),
        "literal_sequence_before": before_texts,
        "literal_sequence_after": after_texts,
        "literal_text_utf16le_sha256_before": [text_hash(value) for value in before_texts],
        "literal_text_utf16le_sha256_after": [text_hash(value) for value in after_texts],
        "whole_record_join_before": before_join,
        "whole_record_join_after": after_join,
        "whole_record_join_utf16le_sha256_before": text_hash(before_join),
        "whole_record_join_utf16le_sha256_after": text_hash(after_join),
        "record_bytes_sha256_before": sha256_bytes(record.data),
        "record_bytes_sha256_after": sha256_bytes(rebuilt_bytes),
        "record_byte_length_before": len(record.data),
        "record_byte_length_after": len(rebuilt_bytes),
        "all_non_target_literals_unchanged": True,
        "nonliteral_skeleton_unchanged": True,
        "nonliteral_skeleton_sha256": sha256_bytes(before_skeleton),
    }


def msggame_context(
    language: str,
    file_key: str | None,
    coordinate: str,
    expected_text_hash: str | None,
) -> dict[str, Any]:
    if file_key is None:
        if BASE_EN_MSGGAME.exists():
            raise RuntimeError(
                "base PC EN msggame unexpectedly exists; its coordinate must be reviewed explicitly"
            )
        return {
            "language": language,
            "availability": "file_absent",
            "relative_path": "MSG/EN/msggame.bin",
            "text": None,
            "text_utf16le_sha256": None,
        }

    path, file_hash = require_file(file_key)
    _archive, rows = msggame_rows(path)
    text = rows.get(coordinate)
    if text is None:
        if language != "en":
            raise RuntimeError(f"required {language} context coordinate is absent: {coordinate}")
        return {
            "language": language,
            "availability": "coordinate_absent",
            "relative_path": path.relative_to(STEAM_ROOT).as_posix(),
            "file_sha256": file_hash,
            "text": None,
            "text_utf16le_sha256": None,
        }
    actual_hash = text_hash(text)
    if expected_text_hash is None or actual_hash != expected_text_hash:
        raise RuntimeError(
            f"PC {language} context hash differs at {coordinate}: "
            f"expected {expected_text_hash}, got {actual_hash}"
        )
    return {
        "language": language,
        "availability": "coordinate_present",
        "relative_path": path.relative_to(STEAM_ROOT).as_posix(),
        "file_sha256": file_hash,
        "text": text,
        "text_utf16le_sha256": actual_hash,
    }


def build_msggame_case(spec: dict[str, Any]) -> dict[str, Any]:
    jp_path, jp_file_hash = require_file(str(spec["jp_file"]))
    ko_path, ko_file_hash = require_file(str(spec["ko_file"]))
    jp_archive, jp_rows = msggame_rows(jp_path)
    ko_archive, ko_rows = msggame_rows(ko_path)
    coordinate = str(spec["coordinate"])
    source = jp_rows.get(coordinate)
    current = ko_rows.get(coordinate)
    if source is None or current is None:
        raise RuntimeError(f"source/current coordinate missing: {spec['resource']} {coordinate}")
    if source != spec["expected_source"] or text_hash(source) != spec["expected_source_hash"]:
        raise RuntimeError(f"pristine PC Japanese literal differs: {spec['resource']} {coordinate}")
    if current != spec["expected_current"] or text_hash(current) != spec["expected_current_hash"]:
        raise RuntimeError(f"live PC Korean literal hash gate failed: {spec['resource']} {coordinate}")
    proposal = str(spec["proposal"])
    if text_hash(proposal) != spec["expected_proposal_hash"]:
        raise RuntimeError(f"proposal literal hash differs: {spec['resource']} {coordinate}")
    if format_profile(current) != format_profile(proposal):
        raise RuntimeError(f"format/profile contract differs: {spec['resource']} {coordinate}")
    if not proposal.endswith(u(r"\ud558")):
        raise RuntimeError(f"proposal ending is not deterministic: {spec['resource']} {coordinate}")
    contexts = {
        language: msggame_context(
            language,
            file_key,
            coordinate,
            spec["context_hashes"].get(language),
        )
        for language, file_key in spec["context_files"].items()
    }
    record_safety = msggame_join_safety(ko_archive, coordinate, current, proposal)
    if spec["resource_key"] == "pk":
        base_jp_path, _base_jp_file_hash = require_file("base_jp")
        _base_jp_archive, base_jp_rows = msggame_rows(base_jp_path)
        base_source = base_jp_rows.get("8:937:2")
        if base_source != source or text_hash(base_source) != text_hash(source):
            raise RuntimeError("base-PC source corroboration no longer matches PK source")
        pc_source_corroboration: dict[str, Any] | None = {
            "comparison_resource": "MSG/JP/msggame.bin",
            "comparison_coordinate": "8:937:2",
            "comparison_source_japanese": base_source,
            "comparison_source_utf16le_sha256": text_hash(base_source),
            "matches_pk_pristine_source": True,
            "use": "PC Japanese source corroboration only; no Korean text is compared.",
        }
    else:
        pc_source_corroboration = None

    return {
        "schema": SCHEMA,
        "review_batch": REVIEW_BATCH,
        "record_type": "candidate",
        "resource": spec["resource"],
        "coordinate": coordinate,
        "source_japanese": source,
        "current_korean": current,
        "proposed_korean": proposal,
        "source_japanese_utf16le_sha256": text_hash(source),
        "current_korean_utf16le_sha256": text_hash(current),
        "proposed_korean_utf16le_sha256": text_hash(proposal),
        "current_korean_role": (
            "hash_gate_and_structural_format_preservation_only_not_semantic_evidence"
        ),
        "input_file_sha256": {
            "pristine_pc_jp": jp_file_hash,
            "live_pc_ko": ko_file_hash,
            **{
                language: context["file_sha256"]
                for language, context in contexts.items()
                if "file_sha256" in context
            },
        },
        "pc_references": contexts,
        "pc_source_corroboration": pc_source_corroboration,
        "rationale": spec["rationale"],
        "format_profile": {
            "source_japanese": format_profile(source),
            "current_korean": format_profile(current),
            "proposed_korean": format_profile(proposal),
            "current_equals_proposed_contract": True,
        },
        "msggame_whole_record_join_safety": record_safety,
        "current_korean_hash_gate_passed": True,
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "generic_builder_changed": False,
        "steam_game_files_written": False,
        "release_or_commit_created": False,
    }


def load_active_event_font() -> tuple[Any, Callable[[str], int], dict[str, Any]]:
    layout_v2 = load_module(
        "translation_quality_residual_three_layout_v2",
        LAYOUT_V2_SCRIPT,
    )
    if (
        layout_v2.MAX_LINES != MAX_EVENT_LINES
        or layout_v2.MAX_LINE_PX != MAX_EVENT_LINE_PX
    ):
        raise RuntimeError("v2 event layout limits differ from the 3-line/912px contract")
    advance, font = layout_v2.current_font(STEAM_ROOT)
    if not isinstance(font, dict) or not isinstance(font.get("sha256"), str):
        raise RuntimeError("active event font evidence is malformed")
    return layout_v2, advance, font


def event_font_layout(
    layout_v2: Any,
    advance: Callable[[str], int],
    font: dict[str, Any],
    proposal: str,
) -> dict[str, Any]:
    tokens = RUNTIME_RE.findall(proposal)
    if tokens:
        raise RuntimeError("residual 7256 proposal unexpectedly contains runtime tokens")
    actual_widths, reserved_widths = layout_v2.target_width_pairs(proposal, advance, {})
    if not actual_widths or len(actual_widths) != len(reserved_widths):
        raise RuntimeError("active event-font width evidence is malformed")
    result = {
        "engine": "steam_jp_msgev_full_layout_v2.target_width_pairs",
        "active_event_font": {
            "sha256": font["sha256"],
            "size": font.get("size"),
        },
        "max_lines": MAX_EVENT_LINES,
        "max_line_px": MAX_EVENT_LINE_PX,
        "runtime_tokens": tokens,
        "runtime_reservations_px": {},
        "line_count": len(actual_widths),
        "target_width_pairs": [
            {
                "line": index + 1,
                "actual_px": actual,
                "reserved_px": reserved,
            }
            for index, (actual, reserved) in enumerate(
                zip(actual_widths, reserved_widths, strict=True)
            )
        ],
        "max_actual_px": max(actual_widths),
        "max_reserved_px": max(reserved_widths),
        "within_three_lines": len(actual_widths) <= MAX_EVENT_LINES,
        "within_actual_pixel_budget": max(actual_widths) <= MAX_EVENT_LINE_PX,
        "within_runtime_reserved_pixel_budget": max(reserved_widths)
        <= MAX_EVENT_LINE_PX,
    }
    if not (
        result["within_three_lines"]
        and result["within_actual_pixel_budget"]
        and result["within_runtime_reserved_pixel_budget"]
    ):
        raise RuntimeError(f"msgev 7256 fails active event-font budget: {result}")
    return result


def build_msgev_case() -> dict[str, Any]:
    paths = {key: require_file(key) for key in ("msgev_jp", "msgev_ko", "msgev_en", "msgev_sc", "msgev_tc")}
    tables = {key: common_rows(path) for key, (path, _hash) in paths.items()}
    identifier = int(MSGEV_CASE["id"])
    if any(identifier >= len(table) for table in tables.values()):
        raise RuntimeError(f"msgev table lacks id {identifier}")
    source = tables["msgev_jp"][identifier]
    current = tables["msgev_ko"][identifier]
    proposal = str(MSGEV_CASE["proposal"])
    if source != MSGEV_CASE["expected_source"] or text_hash(source) != MSGEV_CASE["expected_source_hash"]:
        raise RuntimeError("pristine PC Japanese msgev source differs at 7256")
    if current != MSGEV_CASE["expected_current"] or text_hash(current) != MSGEV_CASE["expected_current_hash"]:
        raise RuntimeError("live PC Korean msgev hash gate failed at 7256")
    if text_hash(proposal) != MSGEV_CASE["expected_proposal_hash"]:
        raise RuntimeError("msgev 7256 proposal hash differs")
    if format_profile(current) != format_profile(proposal):
        raise RuntimeError("msgev 7256 format/profile contract differs")
    references: dict[str, Any] = {}
    for language, key in (("en", "msgev_en"), ("sc", "msgev_sc"), ("tc", "msgev_tc")):
        text = tables[key][identifier]
        actual_hash = text_hash(text)
        expected_hash = MSGEV_CASE["context_hashes"][language]
        if actual_hash != expected_hash:
            raise RuntimeError(
                f"PC {language} msgev context differs at 7256: "
                f"expected {expected_hash}, got {actual_hash}"
            )
        path, file_hash = paths[key]
        references[language] = {
            "language": language,
            "availability": "coordinate_present",
            "relative_path": path.relative_to(STEAM_ROOT).as_posix(),
            "file_sha256": file_hash,
            "text": text,
            "text_utf16le_sha256": actual_hash,
        }
    layout_v2, advance, font = load_active_event_font()
    layout = event_font_layout(layout_v2, advance, font, proposal)
    return {
        "schema": SCHEMA,
        "review_batch": REVIEW_BATCH,
        "record_type": "candidate",
        "resource": MSGEV_CASE["resource"],
        "id": identifier,
        "source_japanese": source,
        "current_korean": current,
        "proposed_korean": proposal,
        "source_japanese_utf16le_sha256": text_hash(source),
        "current_korean_utf16le_sha256": text_hash(current),
        "proposed_korean_utf16le_sha256": text_hash(proposal),
        "current_korean_role": (
            "hash_gate_and_structural_format_preservation_only_not_semantic_evidence"
        ),
        "input_file_sha256": {
            "pristine_pc_jp": paths["msgev_jp"][1],
            "live_pc_ko": paths["msgev_ko"][1],
            "en": paths["msgev_en"][1],
            "sc": paths["msgev_sc"][1],
            "tc": paths["msgev_tc"][1],
        },
        "pc_references": references,
        "rationale": MSGEV_CASE["rationale"],
        "format_profile": {
            "source_japanese": format_profile(source),
            "current_korean": format_profile(current),
            "proposed_korean": format_profile(proposal),
            "current_equals_proposed_contract": True,
        },
        "actual_event_font_layout": layout,
        "current_korean_hash_gate_passed": True,
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "generic_builder_changed": False,
        "steam_game_files_written": False,
        "release_or_commit_created": False,
    }


def build() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = [build_msggame_case(spec) for spec in MSGGAME_CASES]
    rows.append(build_msgev_case())
    summary = {
        "schema": SCHEMA,
        "review_batch": REVIEW_BATCH,
        "candidate_count": len(rows),
        "candidate_coordinates": [
            f"{row['resource']}:{row.get('coordinate', row.get('id'))}" for row in rows
        ],
        "current_korean_hashes": {
            f"{row['resource']}:{row.get('coordinate', row.get('id'))}": row[
                "current_korean_utf16le_sha256"
            ]
            for row in rows
        },
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "generic_builder_changed": False,
        "steam_game_files_written": False,
        "release_or_commit_created": False,
    }
    return rows, summary


def validate(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    expected_locations = [
        ("MSG/JP/msggame.bin", "8:937:2"),
        ("MSG_PK/JP/msggame.bin", "8:949:2"),
        ("MSG_PK/JP/msgev.bin", 7256),
    ]
    actual_locations = [
        (row.get("resource"), row.get("coordinate", row.get("id"))) for row in rows
    ]
    if actual_locations != expected_locations:
        raise RuntimeError(f"candidate locations differ: {actual_locations!r}")
    if summary.get("candidate_count") != 3:
        raise RuntimeError("candidate count is not exactly three")
    for row in rows:
        if (
            row.get("switch_korean_translation_used")
            or row.get("historic_korean_backup_used")
            or row.get("generic_builder_changed")
            or row.get("steam_game_files_written")
            or row.get("release_or_commit_created")
        ):
            raise RuntimeError("PC-only/read-only scope contract changed")
        if row["current_korean_utf16le_sha256"] == row["proposed_korean_utf16le_sha256"]:
            raise RuntimeError(f"candidate lacks an actual text change: {row['resource']}")
        profile = row.get("format_profile")
        if not isinstance(profile, dict) or not profile.get("current_equals_proposed_contract"):
            raise RuntimeError(f"format contract missing: {row['resource']}")
        if profile["current_korean"] != profile["proposed_korean"]:
            raise RuntimeError(f"format contract fails: {row['resource']}")
        if "msggame_whole_record_join_safety" in row:
            safety = row["msggame_whole_record_join_safety"]
            if not (
                safety.get("all_non_target_literals_unchanged")
                and safety.get("nonliteral_skeleton_unchanged")
                and safety.get("literal_count", 0) > safety.get("target_literal_id", -1)
            ):
                raise RuntimeError(f"msggame record safety fails: {row['resource']}")
        if row.get("id") == 7256:
            layout = row.get("actual_event_font_layout")
            if not isinstance(layout, dict) or not (
                layout.get("within_three_lines")
                and layout.get("within_actual_pixel_budget")
                and layout.get("within_runtime_reserved_pixel_budget")
            ):
                raise RuntimeError("msgev active-font 3-line proof fails")
            pairs = layout.get("target_width_pairs")
            if not isinstance(pairs, list) or len(pairs) != 3:
                raise RuntimeError("msgev candidate is not exactly three lines")
            if any(
                pair.get("actual_px", MAX_EVENT_LINE_PX + 1) > MAX_EVENT_LINE_PX
                or pair.get("reserved_px", MAX_EVENT_LINE_PX + 1) > MAX_EVENT_LINE_PX
                for pair in pairs
            ):
                raise RuntimeError("msgev candidate exceeds its active-font budget")


def canonical_jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(
        json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    )


def atomic_write(path: Path, payload: str) -> None:
    resolved = path.resolve(strict=False)
    tmp_resolved = TMP_ROOT.resolve()
    if resolved != tmp_resolved and tmp_resolved not in resolved.parents:
        raise RuntimeError(f"private output must remain under tmp: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="require the existing private JSONL to equal the deterministic build",
    )
    parser.add_argument("--kind", choices=("summary", "candidates"), default="summary")
    args = parser.parse_args()

    rows, summary = build()
    validate(rows, summary)
    payload = canonical_jsonl(rows)
    if args.write:
        atomic_write(OUTPUT, payload)
        summary["private_candidate_output"] = OUTPUT.relative_to(REPO).as_posix()
        summary["private_candidate_output_sha256"] = sha256_file(OUTPUT)
    if args.validate:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != payload:
            raise RuntimeError("existing private JSONL differs from the deterministic build")
    if args.kind == "candidates":
        print("@@JSONL@@")
        print(payload, end="")
    else:
        print("@@SUMMARY@@")
        print(json.dumps(summary, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
