#!/usr/bin/env python3
"""Prepare PC-only high-confidence MS GEV semantic/proper-name candidates.

This is an audit generator, not an applicator.  It reads only the pristine
PC Japanese source and the currently installed PC Korean/EN/SC/TC tables.  It
does not declare or open a Switch path, and it never reads a historical Korean
backup.  It writes no game resources.

The candidates are deliberately manual and conservative: the corpus-wide
signals merely surface rows for review; this script emits only the rows whose
meaning or proper-name loss was independently checked against all four PC
references.  Existing MS GEV review artifacts are consulted only for numeric
coordinate exclusion, never as Korean linguistic evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
TMP_ROOT = REPO / "tmp" / "translation_quality_audit_v1"
SEMANTIC_ROOT = TMP_ROOT / "semantic"
PROPOSAL_ROOT = TMP_ROOT / "proposals"
OUTPUT = SEMANTIC_ROOT / "msgev_highrisk_semantic_propername_v1.jsonl"
HOLD_OUTPUT = SEMANTIC_ROOT / "msgev_highrisk_semantic_propername_holds.v1.jsonl"

RESOURCE = "MSG_PK/JP/msgev.bin"
REVIEW_BATCH = "msgev_highrisk_semantic_propername_v1"
TABLE_COUNT = 17_916
MAX_LOGICAL_COLUMNS = 76

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

ESC_TOKEN_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ID_RE = re.compile(r'"id"\s*:\s*(\d+)')
ASCII_KEY_RE = re.compile(r"^[a-z][a-z0-9_]{4,}$")
KANA_RE = re.compile(r"[\u3040-\u30ff]")


def u(value: str) -> str:
    """Decode explicit escapes without transforming literal Unicode text."""

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


# Each source hash pins the exact installed PC-Korean text that was reviewed.
# No proposal changes line breaks only; each restores a missing semantic fact,
# clarifies a proper name, or fixes a lexical typo.
CANDIDATE_SPECS: dict[int, dict[str, str]] = {
    3986: {
        "expected_current_text_sha256": "E64D380A399169AE51AAF48D5D1CF45839BDC46AFAEC3DFFD29D818AF221D09F",
        "rationale": "restore_suicide_report_and_correct_actor_relationship",
        "proposed": u(r"\x1bCA\ub2e4\uce74\ud6c4\uc0ac\x1bCZ\ub294 \x1bCA\uc694\uc2dc\ud0c0\uce74\x1bCZ\uac00\n\x1bCA\ud558\ub8e8\ud788\ub370\x1bCZ\uc5d0\uac8c \uac00\ub3c5\ub9cc \ub118\uae38 \uac83\uc73c\ub85c \uc5ec\uaca8,\n\uc8fc\uad70 \uc790\uacb0 \uc18c\uc2dd\uc5d0 \ub3d9\uc694\ud588\ub2e4."),
    },
    4258: {
        "expected_current_text_sha256": "4D18E67DAF82D496FCCDFDF0FC5BE78740A8421998536AA93DC84FE6BA7136D8",
        "rationale": "restore_becoming_mino_daimyo_and_multiyear_conflict",
        "proposed": u(r"\uc8fc\uad70 \x1bCA\ub3c4\ud0a4 \uc694\ub9ac\ub178\ub9ac\x1bCZ\ub97c \ucad3\uc544\ub0b4\n\x1bCC\ubbf8\ub178\x1bCZ\uc758 \ub2e4\uc774\ubb18\uac00 \ub41c \x1bCA[b924]\x1bCZ\ub294\n\uc218\ub144\uc9f8 \uc801\uc7a5\uc790 \x1bCA[bm921]\x1bCZ\uc640 \ub300\ub9bd\ud588\ub2e4."),
    },
    5647: {
        "expected_current_text_sha256": "67D7A08D1B7405CA7AEC323003015BDB9F45ABA07358627F0D59B586AE4827BD",
        "rationale": "restore_transfer_surrender_refusal_and_escape_context",
        "proposed": u(r"\x1bCA\uc544\ub9c8\uace0 \uc694\uc2dc\ud788\uc0ac\x1bCZ \uc77c\ud589\uc740 \x1bCB\ubaa8\ub9ac \uac00\ubb38\x1bCZ\uc758\n\x1bCC\uc544\ud0a4\x1bCZ\ub85c \uc774\uc1a1\ub410\uace0, \ud56d\ubcf5\uc5d0 \ubd88\ubcf5\ud55c \x1bCA\uc57c\ub9c8\ub098\uce74 \uc2dc\uce74\ub178\uc2a4\ucf00\x1bCZ \ub4f1\uc740\n\x1bCC\uc774\uc988\ubaa8\ud0c0\uc774\uc0e4\x1bCZ\uc5d0\uc11c \ud0c8\ucd9c\ud588\ub2e4."),
    },
    7310: {
        "expected_current_text_sha256": "1B9C772202BEB89CD7894AB3FFC54AD5B362FDB1BCCCE063EDA68FACEFD9AE3B",
        "rationale": "restore_that_the_lord_was_confined",
        "proposed": u(r"\x1bCA\uad6c\ub9ac\uc57c\ub9c8 \uc820\uc2a4\ucf00\x1bCZ\ub294 \uc131 \uc548\uc73c\ub85c \ub4e4\uc5b4\uac00,\n\uc720\ud3d0\ub41c \uc8fc\uad70 \x1bCA[b826]\x1bCZ\uc758 \uac10\uc625\uc73c\ub85c\n\ud5a5\ud588\ub2e4."),
    },
    8128: {
        "expected_current_text_sha256": "AADAC9B87183D566B61E27A66287EEFD7FD210188D61ED9B25B2D5255DF46A67",
        "rationale": "restore_retirement_motive_to_prevent_internal_power_struggle",
        "proposed": u(r"\uac00\ubb38 \ub0b4 \uad8c\ub825 \ub2e4\ud23c\uc744 \ub9c9\uc73c\ub824\n\x1bCA\ub370\ub8e8\ubb34\ub124\x1bCZ\uac00 \ub3cc\uc5f0 \uc740\uac70\ud558\uc790,\n\x1bCA\ub9c8\uc0ac\ubb34\ub124\x1bCZ\ub294 \x1bCB\ub2e4\ud14c \uac00\ubb38\x1bCZ 17\ub300 \ub2f9\uc8fc\uac00 \ub410\ub2e4."),
    },
    8512: {
        "expected_current_text_sha256": "F1B0C48DDC7B49402964359D49EEE5A61A5A21F92281EF38E861DF256E576D43",
        "rationale": "restore_reluctant_truce_only_and_continued_interclan_tension",
        "proposed": u(r"\x1bCA[b1871]\x1bCZ\ub3c4 \uc5b4\uca54 \uc218 \uc5c6\uc774 \uc751\ud588\uc9c0\ub9cc\n\uadf8\uc800 \uc815\uc804\ub9cc \ubc1b\uc544\ub4e4\uc600\uc744 \ubfd0,\n\x1bCB[bs754]\x1bCZ\u00b7\x1bCB[bs1871]\x1bCZ \uc591\uac00\ub294 \uc544\uc9c1 \uae34\uc7a5 \uc911\uc774\ub2e4."),
    },
    8739: {
        "expected_current_text_sha256": "4E0647C9B6DC7F7E2AFECE025B42FDBB783BC80AF3E35CCB485FB71A532A6D20",
        "rationale": "restore_repeated_battles_with_fated_enemy",
        "proposed": u(r"\x1bCA[bm1448]\x1bCZ\uc640 \uc218\uc5c6\uc774 \uc2f8\uc6b4\n\uc219\uba85\uc758 \uc801 \x1bCA\ub2e4\ucf00\ub2e4 [bm1251]\x1bCZ\u2014\n\x1bCA[bm1448]\x1bCZ\ub294 \uadf8 \ud798을 \uc11c\uc11c\ud788 \uae4e\uc544 \uac14\ub2e4."),
    },
    9753: {
        "expected_current_text_sha256": "B8AD25B1B405C5DAD4DC82BE87131D2C146D592EBDEA2CDDAC98FB17061395D2",
        "rationale": "restore_repeated_battles_with_fated_enemy",
        "proposed": u(r"\x1bCA[bm1251]\x1bCZ\uc640 \uc218\uc5c6\uc774 \uc2f8\uc6b4\n\uc219\uba85\uc758 \uc801 \x1bCA[b1448]\x1bCZ\u2014\n\x1bCA[bm1251]\x1bCZ\ub294 \uadf8 \ud798\uc744 \uc11c\uc11c\ud788 \uae4e\uc544 \uac14\ub2e4."),
    },
    9771: {
        "expected_current_text_sha256": "9EF74B771F65FDBEE627B85A17DF981B30427F52452FC51DC4FEEA95D4A0798D",
        "rationale": "restore_echigo_nagao_and_yamanouchi_uesugi_proper_names",
        "proposed": u(r"\x1bCB\uc5d0\uce58\uace0 \ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uacfc \x1bCB\uc57c\ub9c8\ub178\uc6b0\uce58 \uc6b0\uc5d0\uc2a4\uae30 \uac00\ubb38\x1bCZ\uc740\n\ub2e4\uc774\ubb18 \uac00\ubb38\uc73c\ub85c서 \uba78\ub9dd했다. \uc804 \ub2f9\uc8fc \x1bCA[bm1448]\x1bCZ\ub294\n\x1bCC\uace0\uc57c\uc0b0\x1bCZ\uc5d0서 \ubd88\ub3c4 \uc218\ud589에 \ud798썼다."),
    },
    10817: {
        "expected_current_text_sha256": "9D6D81DFABAD3476C14507D196E3BFB48752AC528597C3FEDFAFD4509C041453",
        "rationale": "fix_woodpecker_pecking_lexical_typo",
        "proposed": u(r"\ub531\ub530\uad6c\ub9ac\ub294 \ub098\ubb34 \uc18d \ubc8c\ub808\ub97c \uc7a1\uc744 \ub54c\n\uad6c\uba4d \ubc18\ub300\ud3b8\uc744 \ucabc\uc544 \ub180\ub77c \ub098\uc628 \ubc8c\ub808\ub97c \uba39\ub294\n\uc2b5\uc131\uc774 \uc788\ub2e4. \uc774 \uc804\ubc95\uc740 \uc5ec\uae30\uc11c \uc654\ub2e4."),
    },
    10856: {
        "expected_current_text_sha256": "160863361B116C88A2F3D3C131E5F67C7C1266E42AA1BCEE4EDFBA974457C7A9",
        "rationale": "restore_okudaira_defection_large_army_and_castle_defense_context",
        "proposed": u(r"\x1bCB\ub2e4\ucf00\ub2e4 \uce21\x1bCZ \uad6d\uc911 \x1bCB\uc624\ucfe0\ub2e4\uc774\ub77c \uac00\ubb38\x1bCZ\uc774 \x1bCB\ub3c4\ucfe0\uac00와 \uce21\x1bCZ\uc73c\ub85c \ub3cc\uc544\uc11c자,\n\x1bCA\uac00\uc4f0\uc694\ub9ac\x1bCZ\ub294 \ub300\uad70\uc744 \uc774\ub04c\uace0 \x1bCB\uc624\ucfe0\ub2e4\uc774\ub77c\x1bCZ\uac00 \uc9c0\ud0a4\ub294\n\x1bCC\ubbf8\uce74\uc640\x1bCZ\u00b7\x1bCC\ub098\uac00\uc2dc\ub178\uc131\x1bCZ\uc744 \ud3ec\uc704\ud588\ub2e4."),
}
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def load_table(path: Path) -> tuple[str, tuple[str, ...]]:
    sys.path.insert(0, str(REPO / "tools"))
    from nobu16_lz4 import decompress_wrapper
    from nobu16_msg_table import parse_message_table

    packed = path.read_bytes()
    packed_hash = sha256_bytes(packed)
    _, raw = decompress_wrapper(packed)
    return packed_hash, parse_message_table(raw).texts


def load_inputs() -> tuple[dict[str, tuple[str, ...]], dict[str, str]]:
    tables: dict[str, tuple[str, ...]] = {}
    hashes: dict[str, str] = {}
    for language, path in PC_PATHS.items():
        packed_hash, table = load_table(path)
        if packed_hash != EXPECTED_FILE_HASHES[language]:
            raise RuntimeError(
                f"unexpected {language} PC file hash: {packed_hash} "
                f"!= {EXPECTED_FILE_HASHES[language]}"
            )
        if len(table) != TABLE_COUNT:
            raise RuntimeError(f"unexpected {language} table count: {len(table)}")
        tables[language] = table
        hashes[language] = packed_hash
    return tables, hashes


def existing_msgev_artifact_coordinates() -> tuple[set[int], list[str]]:
    """Read only coordinate IDs from existing review artifacts.

    Their Korean payloads are intentionally not used as linguistic evidence.
    """

    blocked: set[int] = set()
    files: list[str] = []
    skip = {OUTPUT.resolve(), HOLD_OUTPUT.resolve()}
    for root in (SEMANTIC_ROOT, PROPOSAL_ROOT):
        if not root.exists():
            continue
        for path in sorted(root.glob("*msgev*.jsonl")):
            if path.resolve() in skip:
                continue
            files.append(path.relative_to(REPO).as_posix())
            for match in ID_RE.finditer(path.read_text(encoding="utf-8")):
                blocked.add(int(match.group(1)))
    return blocked, files


def format_signature(text: str) -> dict[str, tuple[str, ...]]:
    return {
        "escape_tokens": tuple(ESC_TOKEN_RE.findall(text)),
        "runtime_tokens": tuple(RUNTIME_RE.findall(text)),
        "printf_tokens": tuple(PRINTF_RE.findall(text)),
    }


def logical_columns(line: str) -> int:
    rendered = ESC_TOKEN_RE.sub("", line)
    # A fixed reservation makes the check conservative while preserving an
    # identical runtime-token sequence between current and proposal.
    rendered = RUNTIME_RE.sub("XXXXXXXX", rendered)
    width = 0
    for char in rendered:
        if unicodedata.combining(char):
            continue
        width += 2 if unicodedata.east_asian_width(char) in {"W", "F"} else 1
    return width


def line_metrics(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    return {
        "line_count": len(lines),
        "logical_display_columns": [logical_columns(line) for line in lines],
    }


def semantic_visible(text: str) -> str:
    return ESC_TOKEN_RE.sub("", text).replace("\r", "").replace("\n", "")


def source_keyword_counts(jp_table: tuple[str, ...]) -> dict[str, int]:
    """Corpus-wide, read-only high-risk semantic sweep evidence."""

    families = {
        "confinement": ("\u5e7d\u9589", "\u76e3\u7981", "\u8edf\u7981"),
        "exile_or_banishment": ("\u8ffd\u653e", "\u653e\u9010", "\u6d41\u7f6a", "\u6d41\u5211"),
        "hostage": ("\u4eba\u8cea",),
        "assassination": ("\u6697\u6bba", "\u8b00\u6bba", "\u6bd2\u6bba", "\u523a\u5ba2", "\u523a\u6bba"),
        "self_death": ("\u81ea\u5bb3", "\u5207\u8179", "\u81ea\u5203", "\u81ea\u6bba"),
        "rebellion": ("\u8b00\u53cd", "\u53cd\u4e71", "\u53cd\u65d7", "\u53db\u4e71", "\u8702\u8d77"),
        "collapse": ("\u6ec5\u4ea1", "\u6ec5\u307c", "\u58ca\u6ec5", "\u6ec5\u3073"),
        "surrender": ("\u964d\u4f0f", "\u5c48\u670d", "\u964d\u308b", "\u964d\u3059"),
        "priesthood_or_retirement": ("\u51fa\u5bb6", "\u96a0\u5c45"),
        "defection": ("\u5bdd\u8fd4", "\u96e2\u53cd", "\u88cf\u5207"),
        "capture": ("\u6355\u7e1b", "\u6355\u3089\u3048", "\u6355\u3048", "\u902e\u6355"),
        "recapture": ("\u596a\u9084",),
        "confiscation": ("\u6539\u6613", "\u6ca1\u53ce"),
        "succession": ("\u5373\u4f4d", "\u7d99\u627f", "\u5bb6\u7763", "\u5ec3\u5ae1"),
    }
    return {
        name: sum(any(token in text for token in tokens) for text in jp_table)
        for name, tokens in families.items()
    }


def find_pinyin_key_like_ids(tables: dict[str, tuple[str, ...]]) -> list[int]:
    ids: list[int] = []
    for index, ko in enumerate(tables["ko"]):
        jp = tables["jp"][index]
        en = tables["en"][index]
        if (
            ASCII_KEY_RE.fullmatch(ko)
            and ko == tables["sc"][index]
            and ko != jp
            and KANA_RE.search(jp)
            and KANA_RE.search(en)
        ):
            ids.append(index)
    return ids


def duplicate_title_hold(tables: dict[str, tuple[str, ...]], index: int) -> dict[str, Any]:
    source = tables["jp"][index]
    comparison_id = next(
        (
            other
            for other, other_source in enumerate(tables["jp"])
            if other != index
            and other_source == source
            and tables["ko"][other] != tables["ko"][index]
        ),
        None,
    )
    return {
        "schema_version": REVIEW_BATCH,
        "review_batch": REVIEW_BATCH,
        "record_type": "hold_group",
        "reason": "duplicate_title_localization_ambiguous_without_runtime_visibility_proof",
        "ids": [index],
        "current_pc_korean": {str(index): tables["ko"][index]},
        "same_jp_reference_coordinate": comparison_id,
        "same_jp_current_pc_korean": (
            tables["ko"][comparison_id] if comparison_id is not None else None
        ),
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
    }


def build() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    tables, file_hashes = load_inputs()
    blocked, active_artifacts = existing_msgev_artifact_coordinates()

    overlap = sorted(set(CANDIDATE_SPECS) & blocked)
    if overlap:
        raise RuntimeError(f"candidate IDs overlap existing MS GEV artifacts: {overlap}")

    jp_ko_tag_mismatches = sum(
        format_signature(jp)["escape_tokens"] != format_signature(ko)["escape_tokens"]
        for jp, ko in zip(tables["jp"], tables["ko"])
    )

    rows: list[dict[str, Any]] = []
    for index in sorted(CANDIDATE_SPECS):
        spec = CANDIDATE_SPECS[index]
        current = tables["ko"][index]
        proposed = spec["proposed"]
        if text_hash(current) != spec["expected_current_text_sha256"]:
            raise RuntimeError(f"current PC Korean text changed at {index}")
        if current == proposed:
            raise RuntimeError(f"proposal is a no-op at {index}")
        if format_signature(current) != format_signature(proposed):
            raise RuntimeError(f"format/token contract mismatch at {index}")
        if semantic_visible(current) == semantic_visible(proposed):
            raise RuntimeError(f"linebreak-only proposal rejected at {index}")

        current_lines = line_metrics(current)
        proposed_lines = line_metrics(proposed)
        if proposed_lines["line_count"] != current_lines["line_count"]:
            raise RuntimeError(f"line-count drift at {index}")
        if proposed_lines["line_count"] > 3:
            raise RuntimeError(f"three-line constraint violated at {index}")
        if max(proposed_lines["logical_display_columns"], default=0) > MAX_LOGICAL_COLUMNS:
            raise RuntimeError(f"logical width budget exceeded at {index}")

        rows.append(
            {
                "schema_version": REVIEW_BATCH,
                "review_batch": REVIEW_BATCH,
                "record_type": "candidate",
                "resource": RESOURCE,
                "id": index,
                "source_japanese": tables["jp"][index],
                "current_korean": current,
                "proposed_korean": proposed,
                "pc_references": {
                    "en": tables["en"][index],
                    "sc": tables["sc"][index],
                    "tc": tables["tc"][index],
                },
                "input_file_sha256": file_hashes,
                "current_text_sha256": text_hash(current),
                "proposed_text_sha256": text_hash(proposed),
                "rationale": spec["rationale"],
                "format_contract": format_signature(current),
                "current_layout": current_lines,
                "proposed_layout": proposed_lines,
                "logical_width_budget": MAX_LOGICAL_COLUMNS,
                "active_artifact_coordinate_overlap": False,
                "current_korean_source": "live_pc_only",
                "switch_korean_translation_used": False,
                "historic_korean_backup_used": False,
                "game_files_written": False,
            }
        )

    pinyin_ids = find_pinyin_key_like_ids(tables)
    if len(pinyin_ids) != 62:
        raise RuntimeError(f"unexpected pinyin/key-like hold count: {len(pinyin_ids)}")
    holds: list[dict[str, Any]] = [
        {
            "schema_version": REVIEW_BATCH,
            "review_batch": REVIEW_BATCH,
            "record_type": "hold_group",
            "reason": "ko_equals_sc_pinyin_key_like_value_runtime_or_visibility_unverified",
            "ids": pinyin_ids,
            "resource": RESOURCE,
            "input_file_sha256": file_hashes,
            "switch_korean_translation_used": False,
            "historic_korean_backup_used": False,
            "game_files_written": False,
        },
        duplicate_title_hold(tables, 14391),
        duplicate_title_hold(tables, 14403),
    ]

    colored_span_count = sum(len(ESC_TOKEN_RE.findall(text)) for text in tables["jp"])
    summary = {
        "review_batch": REVIEW_BATCH,
        "resource": RESOURCE,
        "pc_table_count": TABLE_COUNT,
        "full_pc_jp_entries_scanned": TABLE_COUNT,
        "candidate_id_count": len(rows),
        "candidate_ids": [row["id"] for row in rows],
        "hold_group_count": len(holds),
        "pinyin_key_like_hold_id_count": len(pinyin_ids),
        "duplicate_title_hold_ids": [14391, 14403],
        "pc_jp_ko_escape_tag_mismatch_count": jp_ko_tag_mismatches,
        "pc_jp_colored_escape_token_count": colored_span_count,
        "jp_high_risk_keyword_source_hit_counts": source_keyword_counts(tables["jp"]),
        "active_artifact_coordinate_union_count": len(blocked),
        "active_artifacts_scanned_for_id_exclusion": active_artifacts,
        "candidate_overlap_count": len(overlap),
        "input_file_sha256": file_hashes,
        "current_korean_source": "live_pc_only",
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
    }
    return rows, holds, summary


def canonical_jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(
        json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    )


def atomic_write(path: Path, payload: str) -> None:
    """Write a deterministic private review artifact, never a game resource."""

    root = TMP_ROOT.resolve()
    resolved = path.resolve(strict=False)
    if resolved != root and root not in resolved.parents:
        raise RuntimeError(f"output must remain below {TMP_ROOT}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
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
    parser.add_argument("--kind", choices=("candidates", "holds", "summary"), default="summary")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    candidates, holds, summary = build()
    if args.write:
        atomic_write(OUTPUT, canonical_jsonl(candidates))
        atomic_write(HOLD_OUTPUT, canonical_jsonl(holds))
        summary["candidate_output"] = OUTPUT.relative_to(REPO).as_posix()
        summary["candidate_output_sha256"] = sha256_bytes(OUTPUT.read_bytes())
        summary["hold_output"] = HOLD_OUTPUT.relative_to(REPO).as_posix()
        summary["hold_output_sha256"] = sha256_bytes(HOLD_OUTPUT.read_bytes())
    if args.kind == "candidates":
        print("@@JSONL@@")
        print(canonical_jsonl(candidates), end="")
    elif args.kind == "holds":
        print("@@JSONL@@")
        print(canonical_jsonl(holds), end="")
    else:
        print("@@SUMMARY@@")
        print(json.dumps(summary, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
