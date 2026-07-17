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
import importlib.util
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
LAYOUT_V2_SCRIPT = REPO / "workstreams" / "steam_jp_msgev_full_layout_v2" / "build_steam_jp_msgev_full_layout_v2.py"

RESOURCE = "MSG_PK/JP/msgev.bin"
REVIEW_BATCH = "msgev_highrisk_semantic_propername_v1"
TABLE_COUNT = 17_916
MAX_LOGICAL_COLUMNS = 76
MAX_EVENT_LINES = 3
MAX_EVENT_LINE_PX = 912

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
        "proposed": u(r"\uc8fc\uad70 \x1bCA도키 요리노리\x1bCZ를 몰아내\n\x1bCC미노\x1bCZ 일국의 다이묘가 된 \x1bCA[b924]\x1bCZ는\n수년째 적남 \x1bCA[bm921]\x1bCZ와 맞섰다."),
    },
    5647: {
        "expected_current_text_sha256": "67D7A08D1B7405CA7AEC323003015BDB9F45ABA07358627F0D59B586AE4827BD",
        "rationale": "restore_transfer_surrender_refusal_and_escape_context",
        "proposed": u(r"\x1bCA아마고 요시히사\x1bCZ 등은 \x1bCB모리령\x1bCZ \x1bCC아키\x1bCZ로\n이송됐다. \x1bCA야마나카 시카노스케\x1bCZ 등은\n항복을 거부해 \x1bCC이즈모타이샤\x1bCZ서 탈출했다."),
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
        "proposed": u(r"\x1bCA[b1871]\x1bCZ도 억지로 따랐지만,\n정전만 응했을 뿐, \x1bCB[bs754]\x1bCZ와\n\x1bCB[bs1871]\x1bCZ 양가는 대립한다."),
    },
    8739: {
        "expected_current_text_sha256": "4E0647C9B6DC7F7E2AFECE025B42FDBB783BC80AF3E35CCB485FB71A532A6D20",
        "rationale": "restore_repeated_battles_with_fated_enemy",
        "proposed": u(r"\x1bCA[bm1448]\x1bCZ와 수차례 싸운\n숙명의 대적 \x1bCA다케다 [bm1251]\x1bCZ—\n\x1bCA[bm1448]\x1bCZ은 힘을 차츰 꺾었다."),
    },
    9753: {
        "expected_current_text_sha256": "B8AD25B1B405C5DAD4DC82BE87131D2C146D592EBDEA2CDDAC98FB17061395D2",
        "rationale": "restore_repeated_battles_with_fated_enemy",
        "proposed": u(r"\x1bCA[bm1251]\x1bCZ와 수차례 싸운\n숙명의 대적 \x1bCA[b1448]\x1bCZ—\n\x1bCA[bm1251]\x1bCZ은 힘을 차츰 꺾었다."),
    },
    10817: {
        "expected_current_text_sha256": "9D6D81DFABAD3476C14507D196E3BFB48752AC528597C3FEDFAFD4509C041453",
        "rationale": "fix_woodpecker_pecking_lexical_typo",
        "proposed": u(r"딱따구리는 나무 속 벌레를 잡을 때\n구멍 반대편을 쪼아 벌레를 놀라게 해\n나오면 먹는 습성에서 온 전법이다."),
    },
}

# Three rows were already within the actual event-font budget.  Keep their
# reviewed text byte-for-byte stable while the eight layout-risk rows below
# are reflowed or put on hold.
PRESERVED_PASSING_PROPOSAL_HASHES = {
    3986: "0CE7C14E9A36C3BD2D90B3CBAF67055D3CD1246B87B95EE3B8FCEF7B505728B0",
    7310: "04366CFD88C69AC345A32D1CB7E30BED70A856C7396931B40571A3889142EDD5",
    8128: "6757286E6365883390BDCA9A7A6357FB5B78191AB6254F50B73D96148550F8E5",
}
REFLOW_IDS = {4258, 5647, 8512, 8739, 9753, 10817}

# These two semantic corrections cannot be compressed to natural Korean in
# three actual-font lines without dropping a source fact (former clan head at
# 9771; both the Mikawa location and Okudaira castle-defense context at
# 10856).  They remain explicit PC-only holds instead of receiving a
# misleading shortened candidate.
LAYOUT_HOLD_SPECS: dict[int, dict[str, str]] = {
    9771: {
        "expected_current_text_sha256": "9EF74B771F65FDBEE627B85A17DF981B30427F52452FC51DC4FEEA95D4A0798D",
        "rationale": "proper_names_former_clan_head_and_buddhist_training_cannot_all_fit_naturally_in_three_lines",
        "attempted_proposed": u(r"\x1bCB에치고 나가오 가문\x1bCZ과 \x1bCB야마노우치 우에스기 가문\x1bCZ은\n다이묘 가문으로서 멸망했다. 전 당주 \x1bCA[bm1448]\x1bCZ는\n\x1bCC고야산\x1bCZ에서 불도 수행에 힘썼다."),
    },
    10856: {
        "expected_current_text_sha256": "160863361B116C88A2F3D3C131E5F67C7C1266E42AA1BCEE4EDFBA974457C7A9",
        "rationale": "takeda_okudaira_tokugawa_defection_large_army_mikawa_and_castle_defense_facts_cannot_all_fit_naturally_in_three_lines",
        "attempted_proposed": u(r"\x1bCB다케다 측\x1bCZ 국중 \x1bCB오쿠다이라 가문\x1bCZ이 \x1bCB도쿠가와 측\x1bCZ으로 돌아서자,\n\x1bCA가쓰요리\x1bCZ는 대군을 이끌고 \x1bCB오쿠다이라\x1bCZ가 지키는\n\x1bCC미카와\x1bCZ·\x1bCC나가시노성\x1bCZ을 포위했다."),
    },
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


def load_v2_layout_support(
    tables: dict[str, tuple[str, ...]],
    file_hashes: dict[str, str],
) -> tuple[Any, Any, dict[str, int], dict[str, Any], dict[str, Any]]:
    """Load the actual event-font metric and per-token reservation contract.

    The v2 layout builder is the authoritative implementation for the game
    font.  Reusing its ``target_width_pairs`` prevents this semantic audit from
    passing a surrogate logical-column check that the game can still overflow.
    """

    module_spec = importlib.util.spec_from_file_location("msgev_highrisk_layout_v2", LAYOUT_V2_SCRIPT)
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError(f"cannot load v2 MS GEV layout support: {LAYOUT_V2_SCRIPT}")
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_spec.name] = module
    module_spec.loader.exec_module(module)
    if module.MAX_LINES != MAX_EVENT_LINES or module.MAX_LINE_PX != MAX_EVENT_LINE_PX:
        raise RuntimeError("v2 layout limits differ from the audited 3-line/912px contract")

    _source_path, packed, _raw, source_table = module.source_table(STEAM_ROOT)
    if sha256_bytes(packed) != file_hashes["ko"] or tuple(source_table.texts) != tables["ko"]:
        raise RuntimeError("v2 layout source table differs from the live PC Korean table")
    advance, font_file = module.current_font(STEAM_ROOT)
    frozen_reservations, _excluded, reservation_document = module.load_reservations()
    reservation_font = reservation_document.get("font")
    if not isinstance(reservation_font, dict):
        raise RuntimeError("v2 runtime reservation document lacks font evidence")
    packed_font = reservation_font.get("packed")
    if not isinstance(packed_font, dict):
        raise RuntimeError("v2 runtime reservation font evidence is malformed")

    # The frozen v2 reservation file predates the active font resource.  Do
    # not silently use its old pixel numbers: rebuild only the reservations
    # needed by this PC-only batch from the *active* font and live PC table,
    # using the exact v2 policy (numeric token suffix -> full referenced name).
    reviewed_texts = [spec["proposed"] for spec in CANDIDATE_SPECS.values()]
    reviewed_texts.extend(spec["attempted_proposed"] for spec in LAYOUT_HOLD_SPECS.values())
    tokens = sorted({token for text in reviewed_texts for token in RUNTIME_RE.findall(text)})
    actual_reservations: dict[str, int] = {}
    recomputed_token_evidence: dict[str, dict[str, Any]] = {}
    for token in tokens:
        match = re.fullmatch(r"\[([a-z]+)(\d+)\]", token)
        if match is None:
            raise RuntimeError(f"runtime token syntax differs: {token}")
        source_name_id = int(match.group(2))
        if not 0 <= source_name_id < TABLE_COUNT:
            raise RuntimeError(f"runtime token name ID outside the PC table: {token}")
        full_name = tables["ko"][source_name_id]
        width = module.base.visual_line_width(full_name, advance)
        if width <= 0:
            raise RuntimeError(f"runtime token has no visible active-font width: {token}")
        actual_reservations[token] = width
        recomputed_token_evidence[token] = {
            "source_name_id": source_name_id,
            "source_name_utf16le_sha256": text_hash(full_name),
            "reserved_full_name_width_px": width,
            "frozen_v2_reservation_width_px": frozen_reservations.get(token),
        }
    reservation_evidence = {
        "policy": "v2 numeric runtime suffix -> live PC Korean same-ID full name measured with active event font",
        "active_font_sha256": font_file["sha256"],
        "frozen_v2_reservation_font_sha256": packed_font.get("sha256"),
        "frozen_v2_reservation_font_matches_active": packed_font.get("sha256") == font_file["sha256"],
        "recomputed_token_count": len(actual_reservations),
        "recomputed_tokens": recomputed_token_evidence,
    }
    return module, advance, actual_reservations, reservation_document, reservation_evidence


def actual_font_layout(
    layout_v2: Any,
    target: str,
    advance: Any,
    reservations: dict[str, int],
) -> dict[str, Any]:
    """Return exact per-line actual and runtime-reserved event-font widths."""

    actual, reserved = layout_v2.target_width_pairs(target, advance, reservations)
    if len(actual) != len(reserved) or not actual:
        raise RuntimeError("v2 target width pairs are malformed")
    tokens = tuple(RUNTIME_RE.findall(target))
    if any(token not in reservations for token in tokens):
        raise RuntimeError("target uses a runtime token without a v2 reservation")
    return {
        "engine": "steam_jp_msgev_full_layout_v2.target_width_pairs",
        "max_lines": MAX_EVENT_LINES,
        "max_line_px": MAX_EVENT_LINE_PX,
        "line_count": len(actual),
        "target_width_pairs": [
            {"line": number + 1, "actual_px": visible, "reserved_px": projected}
            for number, (visible, projected) in enumerate(zip(actual, reserved, strict=True))
        ],
        "max_actual_px": max(actual),
        "max_reserved_px": max(reserved),
        "runtime_token_reservations_px": {token: reservations[token] for token in tokens},
        "within_actual_budget": max(actual) <= MAX_EVENT_LINE_PX,
        "within_reserved_budget": max(reserved) <= MAX_EVENT_LINE_PX,
        "within_line_budget": len(actual) <= MAX_EVENT_LINES,
    }


def require_candidate_layout(layout: dict[str, Any], index: int) -> None:
    if not (
        layout["within_line_budget"]
        and layout["within_actual_budget"]
        and layout["within_reserved_budget"]
    ):
        raise RuntimeError(
            f"actual/reserved event-font layout exceeds the 3-line/912px budget at {index}: {layout}"
        )


def require_layout_hold(layout: dict[str, Any], index: int) -> None:
    if (
        layout["within_line_budget"]
        and layout["within_actual_budget"]
        and layout["within_reserved_budget"]
    ):
        raise RuntimeError(f"layout hold unexpectedly fits the 3-line/912px contract at {index}")


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
    layout_v2, advance, reservations, reservation_document, runtime_reservation_evidence = load_v2_layout_support(
        tables, file_hashes
    )
    blocked, active_artifacts = existing_msgev_artifact_coordinates()

    reviewed_ids = set(CANDIDATE_SPECS) | set(LAYOUT_HOLD_SPECS)
    if set(CANDIDATE_SPECS).intersection(LAYOUT_HOLD_SPECS):
        raise RuntimeError("candidate and layout-hold IDs overlap")
    if set(PRESERVED_PASSING_PROPOSAL_HASHES).difference(CANDIDATE_SPECS):
        raise RuntimeError("a preserved actual-font-passing candidate is absent")
    if not REFLOW_IDS.issubset(CANDIDATE_SPECS):
        raise RuntimeError("a reflow ID is absent from the candidate partition")
    if reviewed_ids != ({3986, 7310, 8128} | REFLOW_IDS | {9771, 10856}):
        raise RuntimeError("the eight layout-risk IDs are not partitioned deterministically")

    overlap = sorted(reviewed_ids & blocked)
    if overlap:
        raise RuntimeError(f"reviewed IDs overlap existing MS GEV artifacts: {overlap}")

    font_document = reservation_document["font"]
    font_evidence = {
        "resource": font_document["resource"],
        "active_packed_sha256": runtime_reservation_evidence["active_font_sha256"],
        "frozen_v2_reservation_packed_sha256": runtime_reservation_evidence[
            "frozen_v2_reservation_font_sha256"
        ],
        "table": font_document["table"],
        "runtime_reservation_document_sha256": sha256_bytes(layout_v2.RESERVATIONS_PATH.read_bytes()),
        "active_runtime_reservation_evidence": runtime_reservation_evidence,
        "width_engine": "steam_jp_msgev_full_layout_v2.target_width_pairs",
    }

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
        if layout_v2.protected_signature(current) != layout_v2.protected_signature(proposed):
            raise RuntimeError(f"v2 protected-token contract mismatch at {index}")
        if semantic_visible(current) == semantic_visible(proposed):
            raise RuntimeError(f"linebreak-only proposal rejected at {index}")

        current_lines = line_metrics(current)
        proposed_lines = line_metrics(proposed)
        if proposed_lines["line_count"] != current_lines["line_count"]:
            raise RuntimeError(f"line-count drift at {index}")
        if proposed_lines["line_count"] > 3:
            raise RuntimeError(f"three-line constraint violated at {index}")
        if index in REFLOW_IDS and proposed_lines["line_count"] != MAX_EVENT_LINES:
            raise RuntimeError(f"reflow must retain exactly three natural lines at {index}")
        if index in PRESERVED_PASSING_PROPOSAL_HASHES and text_hash(proposed) != PRESERVED_PASSING_PROPOSAL_HASHES[index]:
            raise RuntimeError(f"previously-passing proposal changed at {index}")
        actual_layout = actual_font_layout(layout_v2, proposed, advance, reservations)
        require_candidate_layout(actual_layout, index)

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
                "actual_event_font_layout": actual_layout,
                "actual_event_font_evidence": font_evidence,
                "active_artifact_coordinate_overlap": False,
                "current_korean_source": "live_pc_only",
                "switch_korean_translation_used": False,
                "historic_korean_backup_used": False,
                "game_files_written": False,
            }
        )

    layout_holds: list[dict[str, Any]] = []
    for index in sorted(LAYOUT_HOLD_SPECS):
        spec = LAYOUT_HOLD_SPECS[index]
        current = tables["ko"][index]
        attempted = spec["attempted_proposed"]
        if text_hash(current) != spec["expected_current_text_sha256"]:
            raise RuntimeError(f"current PC Korean text changed at layout hold {index}")
        if current == attempted or semantic_visible(current) == semantic_visible(attempted):
            raise RuntimeError(f"layout hold lacks a real semantic candidate at {index}")
        if format_signature(current) != format_signature(attempted):
            raise RuntimeError(f"layout-hold format/token contract mismatch at {index}")
        if layout_v2.protected_signature(current) != layout_v2.protected_signature(attempted):
            raise RuntimeError(f"v2 protected-token contract mismatch at layout hold {index}")
        attempted_layout = actual_font_layout(layout_v2, attempted, advance, reservations)
        require_layout_hold(attempted_layout, index)
        layout_holds.append(
            {
                "schema_version": REVIEW_BATCH,
                "review_batch": REVIEW_BATCH,
                "record_type": "hold_actual_font_overflow",
                "resource": RESOURCE,
                "id": index,
                "reason": spec["rationale"],
                "source_japanese": tables["jp"][index],
                "current_korean": current,
                "attempted_proposed_korean": attempted,
                "pc_references": {
                    "en": tables["en"][index],
                    "sc": tables["sc"][index],
                    "tc": tables["tc"][index],
                },
                "input_file_sha256": file_hashes,
                "current_text_sha256": text_hash(current),
                "attempted_text_sha256": text_hash(attempted),
                "format_contract": format_signature(current),
                "attempted_logical_layout": line_metrics(attempted),
                "attempted_actual_event_font_layout": attempted_layout,
                "actual_event_font_evidence": font_evidence,
                "required_next_action": "human semantic compaction or real-game UI decision; do not drop named/source facts only to fit",
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
        *layout_holds,
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
        "actual_font_passing_candidate_count": len(rows),
        "actual_font_layout_hold_count": len(layout_holds),
        "actual_font_layout_hold_ids": [row["id"] for row in layout_holds],
        "reflow_candidate_ids": sorted(REFLOW_IDS),
        "preserved_actual_font_passing_ids": sorted(PRESERVED_PASSING_PROPOSAL_HASHES),
        "actual_event_font_evidence": font_evidence,
        "pinyin_key_like_hold_id_count": len(pinyin_ids),
        "duplicate_title_hold_ids": [14391, 14403],
        "pc_jp_ko_escape_tag_mismatch_count": jp_ko_tag_mismatches,
        "pc_jp_colored_escape_token_count": colored_span_count,
        "jp_high_risk_keyword_source_hit_counts": source_keyword_counts(tables["jp"]),
        "active_artifact_coordinate_union_count": len(blocked),
        "active_artifacts_scanned_for_id_exclusion": active_artifacts,
        "reviewed_coordinate_overlap_count": len(overlap),
        "input_file_sha256": file_hashes,
        "current_korean_source": "live_pc_only",
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
    }
    return rows, holds, summary


def validate_build(
    candidates: list[dict[str, Any]],
    holds: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    """Validate the deterministic candidate/hold partition before emission."""

    candidate_ids = [row.get("id") for row in candidates]
    if candidate_ids != sorted(CANDIDATE_SPECS):
        raise RuntimeError("candidate IDs differ from the deterministic PC-only partition")
    if len(candidate_ids) != len(set(candidate_ids)):
        raise RuntimeError("candidate IDs are duplicated")
    for row in candidates:
        if row.get("switch_korean_translation_used") or row.get("historic_korean_backup_used") or row.get("game_files_written"):
            raise RuntimeError("candidate scope is no longer PC-only/read-only")
        layout = row.get("actual_event_font_layout")
        if not isinstance(layout, dict):
            raise RuntimeError("candidate lacks actual event-font layout evidence")
        if not (
            layout.get("within_line_budget")
            and layout.get("within_actual_budget")
            and layout.get("within_reserved_budget")
        ):
            raise RuntimeError(f"candidate layout budget failed at {row.get('id')}")
        pairs = layout.get("target_width_pairs")
        if not isinstance(pairs, list) or len(pairs) > MAX_EVENT_LINES:
            raise RuntimeError(f"candidate width-pair evidence differs at {row.get('id')}")
        for pair in pairs:
            if not isinstance(pair, dict) or pair.get("actual_px", MAX_EVENT_LINE_PX + 1) > MAX_EVENT_LINE_PX or pair.get("reserved_px", MAX_EVENT_LINE_PX + 1) > MAX_EVENT_LINE_PX:
                raise RuntimeError(f"candidate width pair exceeds the actual event-font budget at {row.get('id')}")

    layout_holds = [row for row in holds if row.get("record_type") == "hold_actual_font_overflow"]
    if [row.get("id") for row in layout_holds] != sorted(LAYOUT_HOLD_SPECS):
        raise RuntimeError("actual-font layout holds differ from the deterministic partition")
    for row in layout_holds:
        if row.get("switch_korean_translation_used") or row.get("historic_korean_backup_used") or row.get("game_files_written"):
            raise RuntimeError("layout hold scope is no longer PC-only/read-only")
        layout = row.get("attempted_actual_event_font_layout")
        if not isinstance(layout, dict):
            raise RuntimeError("layout hold lacks actual event-font evidence")
        if layout.get("within_line_budget") and layout.get("within_actual_budget") and layout.get("within_reserved_budget"):
            raise RuntimeError(f"layout hold unexpectedly fits at {row.get('id')}")

    if summary.get("candidate_ids") != candidate_ids or summary.get("actual_font_layout_hold_ids") != sorted(LAYOUT_HOLD_SPECS):
        raise RuntimeError("summary ID vectors differ from deterministic outputs")
    if summary.get("actual_font_passing_candidate_count") != len(candidates):
        raise RuntimeError("summary candidate count differs")
    if summary.get("actual_font_layout_hold_count") != len(layout_holds):
        raise RuntimeError("summary layout-hold count differs")
    if summary.get("switch_korean_translation_used") or summary.get("historic_korean_backup_used") or summary.get("game_files_written"):
        raise RuntimeError("summary scope is no longer PC-only/read-only")


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
    parser.add_argument("--validate", action="store_true", help="verify deterministic private outputs and actual-font evidence")
    args = parser.parse_args()
    candidates, holds, summary = build()
    validate_build(candidates, holds, summary)
    candidate_payload = canonical_jsonl(candidates)
    hold_payload = canonical_jsonl(holds)
    if args.write:
        atomic_write(OUTPUT, candidate_payload)
        atomic_write(HOLD_OUTPUT, hold_payload)
        summary["candidate_output"] = OUTPUT.relative_to(REPO).as_posix()
        summary["candidate_output_sha256"] = sha256_bytes(OUTPUT.read_bytes())
        summary["hold_output"] = HOLD_OUTPUT.relative_to(REPO).as_posix()
        summary["hold_output_sha256"] = sha256_bytes(HOLD_OUTPUT.read_bytes())
    if args.validate:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != candidate_payload:
            raise RuntimeError("existing candidate output differs from deterministic PC-only evidence")
        if not HOLD_OUTPUT.is_file() or HOLD_OUTPUT.read_text(encoding="utf-8") != hold_payload:
            raise RuntimeError("existing hold output differs from deterministic PC-only evidence")
    if args.kind == "candidates":
        print("@@JSONL@@")
        print(candidate_payload, end="")
    elif args.kind == "holds":
        print("@@JSONL@@")
        print(hold_payload, end="")
    else:
        print("@@SUMMARY@@")
        print(json.dumps(summary, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
