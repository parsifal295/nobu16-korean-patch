"""Build private PC-only residual findings for ``strdata`` and ``msgdata``.

The committed workstream artifacts intentionally contain no source or Korean
payload.  This utility reads only the allowed direct PC files and writes a
private JSONL file below ``tmp`` for the coordinating audit; it never reads
Switch, historical Korean outputs, a generic overlay, or the contaminated
``F:\\Games\\NOBU16\\MSG_PK\\SC`` path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


WORK = Path(r"I:\Workspaces\NOBU16-Korean\repository\KR_PATCH_WORK")
STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
BACKUP = STEAM / "KR_PATCH_BACKUP" / "file_only_transaction" / "steam-jp-1.1.7-v0.6.0" / "originals"
PRIVATE_OUTPUT = WORK / "tmp" / "pc_translation_residuals_pc_only_v1" / "private_findings.v1.jsonl"

sys.path.insert(0, str(WORK / "tools"))
sys.path.insert(0, str(WORK / "workstreams" / "strdata"))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402
from strdata_format import parse_raw_strdata, rebuild_raw_strdata  # noqa: E402


JP_SCRIPT = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u9fff]")
HANGUL = re.compile(r"[가-힣]")
CJK = re.compile(r"[\u3400-\u9fff]")
LOWERCASE_LATIN = re.compile(r"[a-z]")
PLACEHOLDER = re.compile(r"%(?:\+?\d+)?[A-Za-z%]")
ESCAPE = re.compile(r"\x1b.{2}")


PATHS = {
    "strdata": {
        "jp": BACKUP / "MSG" / "JP" / "strdata.bin",
        "current_ko": STEAM / "MSG" / "JP" / "strdata.bin",
        "sc": STEAM / "MSG" / "SC" / "strdata.bin",
        "tc": STEAM / "MSG" / "TC" / "strdata.bin",
    },
    "msgdata": {
        "jp": BACKUP / "MSG_PK" / "JP" / "msgdata.bin",
        "current_ko": STEAM / "MSG_PK" / "JP" / "msgdata.bin",
        "en": STEAM / "MSG_PK" / "EN" / "msgdata.bin",
        "sc": STEAM / "MSG_PK" / "SC" / "msgdata.bin",
        "tc": STEAM / "MSG_PK" / "TC" / "msgdata.bin",
    },
}


PINNED_WRAPPED_SHA256 = {
    "strdata": {
        "jp": "FF172741A7ADC0F8C9E903A4BB3F4482639CE5AB80EA44C8CC458C300940DEE0",
        "current_ko": "D518A91E36B9A59EAD0B5ED1FDD067941E4BF72E43AFCB19C296C8AD77C8C128",
        "sc": "93F88D71210B96783749CEB948E0713D7E6552F764F644092B71A5FD0C994B88",
        "tc": "16481F0B4B1E544F8F7C0B1C92210D13592560470AC062847DA32375B77DA861",
    },
    "msgdata": {
        "jp": "13498FBFFF6D33F0BFB0915B6F365F076FE8E78046EE411BB8478235C86C2C9E",
        "current_ko": "7EAA33BC80C021A028660DF1A7934886591A1DA36DB7BC53146749C3A4AEF040",
        "en": "BDE25DFD7265C5B6E765F2FA2A8F800E171C6C2B23FB8A66F05AE239BF71E033",
        "sc": "A3A0260B74191D4676C43403B587BB4EC676A7D96E56725844F24C8107B1604E",
        "tc": "E266A9C43AAE09BEEA739812AD8E3E8DDDBC4710EF5A81E174A9D215D6B03676",
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def format_signature(text: str) -> dict[str, Any]:
    return {
        "newline_count": text.count("\n"),
        "carriage_return_count": text.count("\r"),
        "placeholder_tokens": PLACEHOLDER.findall(text),
        "escape_tokens": ESCAPE.findall(text),
        "ascii_percent_count": text.count("%"),
        "fullwidth_percent_count": text.count("％"),
    }


def load_strdata(path: Path) -> tuple[dict[tuple[int, int], str], dict[str, str]]:
    wrapped = path.read_bytes()
    header, raw = decompress_wrapper(wrapped)
    archive = parse_raw_strdata(raw)
    if rebuild_raw_strdata(archive) != raw:
        raise ValueError(f"strdata unchanged rebuild mismatch: {path}")
    return (
        {
            (block.block_id, slot_id): text
            for block in archive.blocks
            for slot_id, text in enumerate(block.texts)
        },
        {"wrapped_sha256": sha256(wrapped), "raw_sha256": sha256(raw), "wrapper_prefix": header.prefix.hex().upper()},
    )


def load_msgdata(path: Path) -> tuple[dict[int, str], dict[str, str]]:
    wrapped = path.read_bytes()
    header, raw = decompress_wrapper(wrapped)
    table = parse_message_table(raw)
    if rebuild_message_table(table, table.texts) != raw:
        raise ValueError(f"msgdata unchanged rebuild mismatch: {path}")
    return (
        dict(enumerate(table.texts)),
        {"wrapped_sha256": sha256(wrapped), "raw_sha256": sha256(raw), "wrapper_prefix": header.prefix.hex().upper()},
    )


def anchor_index(jp: dict[Any, str], ko: dict[Any, str]) -> dict[str, list[Any]]:
    result: dict[str, list[Any]] = defaultdict(list)
    for coordinate, source in jp.items():
        if HANGUL.search(ko[coordinate]):
            result[source].append(coordinate)
    return result


def finding(
    *,
    resource: str,
    coordinate: Any,
    category: str,
    texts: dict[str, dict[Any, str]],
    anchors: dict[str, list[Any]],
) -> dict[str, Any]:
    current = texts["current_ko"][coordinate]
    anchor_coordinates = [
        value
        for value in anchors[texts["jp"][coordinate]]
        if value != coordinate and format_signature(texts["current_ko"][value]) == format_signature(current)
    ]
    auto_eligible = category in {"jp_script_residue", "jp_cjk_residue"} and bool(anchor_coordinates)
    row: dict[str, Any] = {
        "resource": resource,
        "coordinate": list(coordinate) if isinstance(coordinate, tuple) else coordinate,
        "category": category,
        "status": (
            "AUTO_ELIGIBLE_EXACT_PC_ANCHOR"
            if auto_eligible
            else "HOLD_NO_CANONICAL_FULL_TITLE_ANCHOR"
        ),
        "jp": texts["jp"][coordinate],
        "current_ko": current,
        "en": texts.get("en", {}).get(coordinate),
        "sc": texts["sc"][coordinate],
        "tc": texts["tc"][coordinate],
        "same_resource_exact_jp_anchor_coordinates": [list(value) if isinstance(value, tuple) else value for value in anchor_coordinates],
        "same_resource_exact_jp_anchor_ko": [texts["current_ko"][value] for value in anchor_coordinates],
        "format_signature": format_signature(current),
    }
    return row


def build() -> list[dict[str, Any]]:
    loaded: dict[str, dict[str, dict[Any, str]]] = {}
    source_meta: dict[str, dict[str, dict[str, str]]] = {}
    for resource, lang_paths in PATHS.items():
        loaded[resource] = {}
        source_meta[resource] = {}
        for language, path in lang_paths.items():
            table, meta = load_strdata(path) if resource == "strdata" else load_msgdata(path)
            if meta["wrapped_sha256"] != PINNED_WRAPPED_SHA256[resource][language]:
                raise ValueError(f"unexpected {resource}/{language} source hash")
            loaded[resource][language] = table
            source_meta[resource][language] = meta

    rows: list[dict[str, Any]] = []
    strdata = loaded["strdata"]
    strdata_anchors = anchor_index(strdata["jp"], strdata["current_ko"])
    for coordinate, current in strdata["current_ko"].items():
        if JP_SCRIPT.search(current) and not HANGUL.search(current):
            rows.append(finding(resource="strdata", coordinate=coordinate, category="jp_script_residue", texts=strdata, anchors=strdata_anchors))

    msgdata = loaded["msgdata"]
    msgdata_anchors = anchor_index(msgdata["jp"], msgdata["current_ko"])
    for coordinate, current in msgdata["current_ko"].items():
        if CJK.search(current) and not HANGUL.search(current):
            rows.append(finding(resource="msgdata", coordinate=coordinate, category="jp_cjk_residue", texts=msgdata, anchors=msgdata_anchors))
        elif (
            current == "dummy"
            and current == msgdata["sc"][coordinate]
            and current != msgdata["en"][coordinate]
            and JP_SCRIPT.search(msgdata["jp"][coordinate])
        ):
            rows.append(finding(resource="msgdata", coordinate=coordinate, category="crosslocale_dummy_hold", texts=msgdata, anchors=msgdata_anchors))
        elif (
            current != "dummy"
            and current == msgdata["sc"][coordinate]
            and current != msgdata["en"][coordinate]
            and LOWERCASE_LATIN.search(current)
            and not JP_SCRIPT.search(current)
            and not HANGUL.search(current)
            and JP_SCRIPT.search(msgdata["jp"][coordinate])
        ):
            rows.append(finding(resource="msgdata", coordinate=coordinate, category="sc_pinyin_residue", texts=msgdata, anchors=msgdata_anchors))

    rows.sort(key=lambda row: (row["resource"], row["coordinate"]))
    expected = {"strdata": 45, "msgdata_jp": 68, "msgdata_pinyin": 303, "msgdata_dummy": 17}
    actual = {
        "strdata": sum(row["category"] == "jp_script_residue" for row in rows),
        "msgdata_jp": sum(row["category"] == "jp_cjk_residue" for row in rows),
        "msgdata_pinyin": sum(row["category"] == "sc_pinyin_residue" for row in rows),
        "msgdata_dummy": sum(row["category"] == "crosslocale_dummy_hold" for row in rows),
    }
    if actual != expected:
        raise ValueError(f"unexpected finding count: {actual}")
    if any("\ufffd" in row["current_ko"] for row in rows):
        raise ValueError("replacement character found")
    auto_eligible_count = sum(row["status"] == "AUTO_ELIGIBLE_EXACT_PC_ANCHOR" for row in rows)
    if auto_eligible_count != 25:
        raise ValueError(f"unexpected exact-anchor candidate count: {auto_eligible_count}")
    meta_row = {
        "type": "meta",
        "schema": "nobu16.translation_quality.pc_only_private_findings.v1",
        "source_policy": "PC JP + current Steam KO + Steam EN/SC/TC only; Switch/historical Korean/generic excluded",
        "source_meta": source_meta,
        "finding_count": len(rows),
        "exact_pc_anchor_candidate_count": auto_eligible_count,
    }
    return [meta_row, *rows]


def write(rows: list[dict[str, Any]]) -> None:
    PRIVATE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
    PRIVATE_OUTPUT.write_text(payload, encoding="utf-8", newline="\n")
    print(f"output={PRIVATE_OUTPUT}")
    print(f"rows={len(rows) - 1}")
    print(f"sha256={sha256(payload.encode('utf-8'))}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    rows = build()
    if args.write:
        write(rows)
    else:
        print(f"validated_rows={len(rows) - 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
