#!/usr/bin/env python3
"""Repair one lost tea-utensil proper-name reference in PC ``msgire``.

The PC Japanese ``初花`` in msgire:19 is the named tea utensil Hatsuhana,
not the generic phrase "first flower."  The same pristine PC-Japanese
description is already rendered with ``하쓰하나`` in PC strdata, and the
separate PC item label agrees.  This script reads only local PC JP/KO and PC
cross-resource evidence; it does not read Switch Korean or write a game file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
BACKUP = STEAM / "KR_PATCH_BACKUP" / "file_only_transaction" / "steam-jp-1.1.7-v0.6.0" / "originals"
PRISTINE_MSGIRE = BACKUP / "MSG_PK" / "JP" / "msgire.bin"
LIVE_MSGIRE = STEAM / "MSG_PK" / "JP" / "msgire.bin"
PRISTINE_STRDATA = BACKUP / "MSG" / "JP" / "strdata.bin"
LIVE_STRDATA = STEAM / "MSG" / "JP" / "strdata.bin"
PRISTINE_MSGDATA = BACKUP / "MSG_PK" / "JP" / "msgdata.bin"
LIVE_MSGDATA = STEAM / "MSG_PK" / "JP" / "msgdata.bin"
TMP_ROOT = REPO / "tmp"
OUTPUT = TMP_ROOT / "translation_quality_audit_v1" / "semantic" / "msgire_proper_name_reference_addendum.v1.jsonl"
IDENTIFIER = 19
STRDATA_DESCRIPTION = (3, 19)
STRDATA_ITEM_LABEL = (0, 14054)
MSGDATA_ITEM_LABEL = 14138
SOURCE_PROPER_NAME = "\u521d\u82b1"
CURRENT_GENERIC_PHRASE = "\uccab \uaf43"
PROPER_NAME_KO = "\ud558\uc4f0\ud558\ub098"
RUNTIME_RE = re.compile(r"\[([a-z]+\d+)\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-16-le")).hexdigest().upper()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_common(path: Path) -> list[str]:
    import sys

    sys.path.insert(0, str(REPO / "tools"))
    from nobu16_lz4 import decompress_wrapper
    from nobu16_msg_table import parse_message_table

    _header, raw = decompress_wrapper(path.read_bytes())
    return parse_message_table(raw).texts


def load_strdata(path: Path) -> dict[tuple[int, int], str]:
    import sys

    sys.path.insert(0, str(REPO / "tools"))
    sys.path.insert(0, str(REPO / "workstreams" / "strdata"))
    from nobu16_lz4 import decompress_wrapper
    from strdata_format import coordinate_texts, parse_raw_strdata

    _header, raw = decompress_wrapper(path.read_bytes())
    return coordinate_texts(parse_raw_strdata(raw))


def format_profile(text: str) -> dict[str, object]:
    return {
        "runtime_tokens": RUNTIME_RE.findall(text),
        "printf_tokens": PRINTF_RE.findall(text),
        "escape_tags": ESC_RE.findall(text),
        "line_breaks": re.findall(r"\r\n|\n|\r", text),
        "outer_ascii_whitespace": [text[: len(text) - len(text.lstrip())], text[len(text.rstrip()) :]],
    }


def existing_msgire_ids() -> set[int]:
    result: set[int] = set()
    for directory in (
        TMP_ROOT / "translation_quality_audit_v1" / "semantic",
        TMP_ROOT / "translation_quality_audit_v1" / "proposals",
    ):
        for path in directory.glob("msgire*.jsonl"):
            if path.resolve() == OUTPUT.resolve():
                continue
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line:
                    continue
                identifier = json.loads(line).get("id")
                if isinstance(identifier, int):
                    result.add(identifier)
    return result


def safe_under_tmp(path: Path) -> Path:
    root = TMP_ROOT.resolve()
    resolved = path.resolve(strict=False)
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"output escapes tmp: {resolved}")
    return resolved


def atomic_write(path: Path, payload: str) -> None:
    path = safe_under_tmp(path)
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


def build() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if IDENTIFIER in existing_msgire_ids():
        raise ValueError(f"msgire proper-name addendum overlaps an existing candidate: {IDENTIFIER}")
    msgire_jp = load_common(PRISTINE_MSGIRE)
    msgire_ko = load_common(LIVE_MSGIRE)
    str_jp = load_strdata(PRISTINE_STRDATA)
    str_ko = load_strdata(LIVE_STRDATA)
    msgdata_jp = load_common(PRISTINE_MSGDATA)
    msgdata_ko = load_common(LIVE_MSGDATA)
    if len(msgire_jp) != 122 or len(msgire_ko) != 122 or len(msgdata_jp) != 29218 or len(msgdata_ko) != 29218:
        raise ValueError("PC message-table cardinality changed")
    source = msgire_jp[IDENTIFIER]
    current = msgire_ko[IDENTIFIER]
    if source != str_jp[STRDATA_DESCRIPTION] or SOURCE_PROPER_NAME not in source:
        raise ValueError("PC cross-resource Japanese description gate differs")
    if current.count(CURRENT_GENERIC_PHRASE) != 1:
        raise ValueError("current msgire wording does not contain one generic phrase occurrence")
    proposed = current.replace(CURRENT_GENERIC_PHRASE, PROPER_NAME_KO)
    if str_ko[STRDATA_DESCRIPTION].count(PROPER_NAME_KO) != 1:
        raise ValueError("PC strdata description does not retain the proper-name reading")
    if str_jp[STRDATA_ITEM_LABEL] != SOURCE_PROPER_NAME + "\u80a9\u885d" or PROPER_NAME_KO not in str_ko[STRDATA_ITEM_LABEL]:
        raise ValueError("PC strdata item-label evidence differs")
    if msgdata_jp[MSGDATA_ITEM_LABEL] != SOURCE_PROPER_NAME + "\u80a9\u885d" or PROPER_NAME_KO not in msgdata_ko[MSGDATA_ITEM_LABEL]:
        raise ValueError("PC msgdata item-label evidence differs")
    before = format_profile(current)
    after = format_profile(proposed)
    source_profile = format_profile(source)
    if before != after or source_profile != after:
        raise ValueError("replacement would alter protected format fields")
    row = {
        "id": IDENTIFIER,
        "ko": current,
        "proposed_ko": proposed,
        "current_hash": sha_text(current),
        "source_text": source,
        "source_text_hash": sha_text(source),
        "live_ko_file_sha256": sha_file(LIVE_MSGIRE),
        "pristine_jp_file_sha256": sha_file(PRISTINE_MSGIRE),
        "issue_type": "named_tea_utensil_reference_lost_as_generic_phrase",
        "rationale": "初花 is the named tea utensil Hatsuhana in this PC-Japanese description. The same PC description and both PC item labels retain 하쓰하나, so replace only the generic Korean phrase with that established name.",
        "pc_cross_resource_evidence": {
            "strdata_same_description_coordinate": "3:19",
            "strdata_item_label_coordinate": "0:14054",
            "msgdata_item_label_id": MSGDATA_ITEM_LABEL,
            "proper_name_ko": PROPER_NAME_KO,
            "switch_korean_translation_used": False,
        },
        "format_validation": {
            "current_to_proposed": "runtime_printf_escape_newline_and_outer_whitespace_match",
            "pristine_jp_to_proposed": "runtime_printf_escape_newline_and_outer_whitespace_match",
            "all_required_checks_pass": True,
        },
        "switch_korean_translation_used": False,
    }
    summary = {
        "row_count": 1,
        "candidate_id": IDENTIFIER,
        "existing_candidate_overlap": [],
        "source_current_hashes": "all_exact_utf16le",
        "switch_korean_translation_used": False,
        "game_files_written": False,
        "json_encoding": "ensure_ascii_true_utf8",
    }
    return [row], summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.validate and args.write:
        parser.error("choose either --validate or --write")
    rows, summary = build()
    if args.write:
        payload = "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows)
        atomic_write(OUTPUT, payload)
        print(json.dumps({**summary, "output": str(OUTPUT)}, ensure_ascii=True, sort_keys=True))
    else:
        print(json.dumps(summary, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
