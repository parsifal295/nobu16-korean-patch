#!/usr/bin/env python3
"""Read-only evidence collector for current PC runtime-QA holds.

This collector never writes game/Steam resources.  It makes a compact JSON
evidence file inside this workstream from pristine PC Japanese and the current
Wave7 candidate only.  No Switch path is opened.
"""

from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
GAME = REPO.parents[0]
OUTPUT = WORKSTREAM / "runtime_qa_mapping_pc_v1.evidence.json"

if str(REPO / "tools") not in sys.path:
    sys.path.insert(0, str(REPO / "tools"))
if str(REPO / "workstreams" / "msggame") not in sys.path:
    sys.path.insert(0, str(REPO / "workstreams" / "msggame"))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402
from msggame_format import parse_packed_msggame, parse_record_literals  # noqa: E402


BASE_EVENT_IDS = (4657, 4781, 6233, 6668, 7475, 16397)
PK_EVENT_IDS = (16402,)
PK_MSGGAME_IDS = ((2, 330), (2, 551), (2, 628), (6, 1524), (6, 1525), (6, 1526), (6, 3887))
BASE_MSGGAME_IDS = ((6, 1518), (6, 1519), (6, 1520))

CURRENT = REPO / "tmp" / "pc_dialogue_goodwill_runtime_wave7_v1" / "candidate-build-1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def find_all(blob: bytes, needle: bytes) -> list[int]:
    """Return exact offsets without an O(file-size × pattern-count) scan."""

    offsets: list[int] = []
    start = 0
    while True:
        offset = blob.find(needle, start)
        if offset < 0:
            return offsets
        offsets.append(offset)
        start = offset + 1


def message_table_rows(path: Path, identifiers: tuple[int, ...]) -> dict[str, Any]:
    _header, raw = decompress_wrapper(path.read_bytes())
    table = parse_message_table(raw)
    return {
        "path": path.as_posix(),
        "packed_sha256": sha256(path),
        "string_count": table.string_count,
        "rows": {str(identifier): table.texts[identifier] for identifier in identifiers},
    }


def msggame_rows(path: Path, identifiers: tuple[tuple[int, int], ...]) -> dict[str, Any]:
    archive = parse_packed_msggame(path.read_bytes()).archive
    out: dict[str, dict[str, Any]] = {}
    for block_id, record_id in identifiers:
        record = archive.blocks[block_id].records[record_id]
        literals = parse_record_literals(record)
        if not literals:
            raise ValueError(f"missing msggame record literal(s): {block_id}:{record_id}")
        opaque_spans: list[dict[str, Any]] = []
        cursor = 0
        for literal in literals:
            opaque_spans.append(
                {"offset": cursor, "hex": record.data[cursor : literal.marker_offset].hex().upper()}
            )
            cursor = literal.marker_end
        opaque_spans.append({"offset": cursor, "hex": record.data[cursor:].hex().upper()})
        out[f"{block_id}:{record_id}"] = {
            "literals": [{"literal_id": literal.literal_id, "text": literal.text} for literal in literals],
            "opaque_spans": opaque_spans,
        }
    return {"path": path.as_posix(), "packed_sha256": sha256(path), "rows": out}


def scan_binaries_for_utf16_terms(terms: dict[str, str]) -> dict[str, Any]:
    """Find exact PC-only text/term bytes in plausible event data roots."""

    roots = (
        "AI",
        "DLC",
        "DLC_PK",
        "FLOW",
        "FLOW_PK",
        "PARAM",
        "PARAM_PK",
        "SCENARIO",
        "SCENARIO_PK",
        "SUBMIT",
        "SUBMIT_PK",
    )
    patterns = {
        label: (term.encode("utf-16-le"), term.encode("utf-16-be"), term.encode("utf-8"))
        for label, term in terms.items()
    }
    evidence: dict[str, Any] = {label: [] for label in terms}
    for relative_root in roots:
        root = GAME / relative_root
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            blob = path.read_bytes()
            for label, codecs in patterns.items():
                offsets_by_codec = [find_all(blob, pattern) for pattern in codecs]
                if any(offsets_by_codec):
                    evidence[label].append(
                        {
                            "path": path.relative_to(GAME).as_posix(),
                            "offsets": {
                                "utf16le": offsets_by_codec[0],
                                "utf16be": offsets_by_codec[1],
                                "utf8": offsets_by_codec[2],
                            },
                        }
                    )
    return evidence


def scan_flow_for_uint32(ids: tuple[int, ...]) -> dict[str, Any]:
    """Record only exact direct 32-bit FLOW hits; 16-bit matches are noise."""

    roots = ("FLOW", "FLOW_PK")
    patterns = {identifier: (struct.pack("<I", identifier), struct.pack(">I", identifier)) for identifier in ids}
    evidence: dict[str, list[dict[str, Any]]] = {str(identifier): [] for identifier in ids}
    for relative_root in roots:
        root = GAME / relative_root
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            blob = path.read_bytes()
            for identifier, (little, big) in patterns.items():
                little_offsets = find_all(blob, little)
                big_offsets = find_all(blob, big)
                if little_offsets or big_offsets:
                    evidence[str(identifier)].append(
                        {
                            "path": path.relative_to(GAME).as_posix(),
                            "u32le_offsets": little_offsets,
                            "u32be_offsets": big_offsets,
                        }
                    )
    return evidence


def main() -> int:
    sources = {
        "base_ev_jp": GAME / "MSG" / "JP" / "ev_strdata.bin",
        "base_ev_current_ko": CURRENT / "MSG" / "JP" / "ev_strdata.bin",
        "pk_msgev_current_ko": CURRENT / "MSG_PK" / "JP" / "msgev.bin",
        "pk_msgev_pc_en": GAME / "MSG_PK" / "EN" / "msgev.bin",
        "pk_msgev_pc_sc": GAME / "MSG_PK" / "SC" / "msgev.bin",
        "pk_msgev_pc_tc": GAME / "MSG_PK" / "TC" / "msgev.bin",
        "base_msggame_jp": GAME / "MSG" / "JP" / "msggame.bin",
        "base_msggame_current_ko": CURRENT / "MSG" / "JP" / "msggame.bin",
        "pk_msggame_current_ko": CURRENT / "MSG_PK" / "JP" / "msggame.bin",
        "base_msggame_pc_sc": GAME / "MSG" / "SC" / "msggame.bin",
        "base_msggame_pc_tc": GAME / "MSG" / "TC" / "msggame.bin",
        "pk_msggame_pc_en": GAME / "MSG_PK" / "EN" / "msggame.bin",
        "pk_msggame_pc_sc": GAME / "MSG_PK" / "SC" / "msggame.bin",
        "pk_msggame_pc_tc": GAME / "MSG_PK" / "TC" / "msggame.bin",
    }
    missing = [str(path) for path in sources.values() if not path.is_file()]
    if missing:
        raise SystemExit(f"missing pinned PC input(s): {missing}")

    base_event_jp = message_table_rows(sources["base_ev_jp"], BASE_EVENT_IDS)
    pk_event_current_ko = message_table_rows(sources["pk_msgev_current_ko"], PK_EVENT_IDS)

    terms = {
        "base_4657_anchor": "長野業正",
        "base_4781_anchor": "姉小路",
        "base_6233_anchor": "白餅三つ",
        "base_6668_anchor": "織田殿",
        "base_7475_anchor": "立花道雪",
        "base_16397_anchor": "就任したい役職",
        "pk_16402_anchor": "플레이할 세력",
    }
    evidence = {
        "schema": "nobu16.kr.runtime-qa-mapping-pc.v1",
        "scope": {
            "pc_only": True,
            "switch_opened": False,
            "steam_or_game_written": False,
            "game_launched": False,
        },
        "sources": {
            "base_event_jp": base_event_jp,
            "base_event_current_ko": message_table_rows(sources["base_ev_current_ko"], BASE_EVENT_IDS),
            "pk_msgev_current_ko": pk_event_current_ko,
            "pk_msgev_pc_en": message_table_rows(sources["pk_msgev_pc_en"], PK_EVENT_IDS),
            "pk_msgev_pc_sc": message_table_rows(sources["pk_msgev_pc_sc"], PK_EVENT_IDS),
            "pk_msgev_pc_tc": message_table_rows(sources["pk_msgev_pc_tc"], PK_EVENT_IDS),
            "base_msggame_jp": msggame_rows(sources["base_msggame_jp"], BASE_MSGGAME_IDS),
            "base_msggame_current_ko": msggame_rows(sources["base_msggame_current_ko"], BASE_MSGGAME_IDS),
            "pk_msggame_current_ko": msggame_rows(sources["pk_msggame_current_ko"], PK_MSGGAME_IDS),
            "base_msggame_pc_sc": msggame_rows(sources["base_msggame_pc_sc"], BASE_MSGGAME_IDS),
            "base_msggame_pc_tc": msggame_rows(sources["base_msggame_pc_tc"], BASE_MSGGAME_IDS),
            "pk_msggame_pc_en": msggame_rows(sources["pk_msggame_pc_en"], PK_MSGGAME_IDS),
            "pk_msggame_pc_sc": msggame_rows(sources["pk_msggame_pc_sc"], PK_MSGGAME_IDS),
            "pk_msggame_pc_tc": msggame_rows(sources["pk_msggame_pc_tc"], PK_MSGGAME_IDS),
        },
        "binary_text_hits": scan_binaries_for_utf16_terms(terms),
        "direct_flow_u32_hits": scan_flow_for_uint32(BASE_EVENT_IDS + PK_EVENT_IDS),
    }
    OUTPUT.write_text(json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(OUTPUT), "sha256": sha256(OUTPUT)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
