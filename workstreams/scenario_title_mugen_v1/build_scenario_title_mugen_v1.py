#!/usr/bin/env python3
"""Rebuild the Base and PK scenario-title tables with the Atsumori allusion intact."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
sys.path[:0] = [str(REPO_ROOT / "tools"), str(REPO_ROOT / "workstreams" / "strdata")]

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402
from strdata_format import coordinate_texts, parse_raw_strdata, rebuild_raw_strdata  # noqa: E402


BEFORE = "덧없는 꿈처럼"
AFTER = "몽환과 같이"
STRDATA_RELATIVE = Path("MSG/JP/strdata.bin")
MSGDATA_RELATIVE = Path("MSG_PK/JP/msgdata.bin")
STRDATA_COORDINATE = (0, 15_026)
MSGDATA_ID = 15_118
INPUT_PINS = {
    STRDATA_RELATIVE.as_posix(): {
        "size": 940_981,
        "sha256": "70FCB097EE999BA8E50723E262C232F782D7DE564DDAB84C9D28180A7AA7FF55",
    },
    MSGDATA_RELATIVE.as_posix(): {
        "size": 476_948,
        "sha256": "5CDB755D88933218BEF8B97193F572CFDC9BAAA84D92A9E6E5508698106156F2",
    },
}
OFFICIAL_TITLE_MATRIX = {
    "JP": "夢幻の如く",
    "EN": "Like A Dream",
    "SC": "宛如梦幻",
    "TC": "如夢似幻",
    "KO_before": BEFORE,
    "KO_after": AFTER,
}


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def pinned_blob(path: Path, relative: Path) -> bytes:
    blob = path.read_bytes()
    pin = INPUT_PINS[relative.as_posix()]
    actual = {"size": len(blob), "sha256": sha256_bytes(blob)}
    if actual != pin:
        raise ValueError(
            f"input pin mismatch for {relative.as_posix()}: actual={actual} expected={pin}"
        )
    return blob


def rebuild_strdata(blob: bytes) -> tuple[bytes, dict[str, Any]]:
    header, raw = decompress_wrapper(blob)
    archive = parse_raw_strdata(raw)
    before_map = coordinate_texts(archive)
    if before_map[STRDATA_COORDINATE] != BEFORE:
        raise ValueError(
            f"unexpected Base title at {STRDATA_COORDINATE}: "
            f"{before_map[STRDATA_COORDINATE]!r}"
        )

    block_zero = list(archive.blocks[0].texts)
    block_zero[STRDATA_COORDINATE[1]] = AFTER
    rebuilt_raw = rebuild_raw_strdata(archive, {0: block_zero})
    rebuilt = recompress_wrapper(rebuilt_raw, header)
    _, check_raw = decompress_wrapper(rebuilt)
    after_map = coordinate_texts(parse_raw_strdata(check_raw))
    changed = [key for key in before_map if before_map[key] != after_map[key]]
    if changed != [STRDATA_COORDINATE] or after_map[STRDATA_COORDINATE] != AFTER:
        raise ValueError(f"Base change set is not exact: {changed}")
    return rebuilt, {
        "coordinate": list(STRDATA_COORDINATE),
        "before": BEFORE,
        "after": AFTER,
        "changed_coordinates": [list(item) for item in changed],
    }


def rebuild_msgdata(blob: bytes) -> tuple[bytes, dict[str, Any]]:
    header, raw = decompress_wrapper(blob)
    table = parse_message_table(raw)
    if table.texts[MSGDATA_ID] != BEFORE:
        raise ValueError(f"unexpected PK title at id {MSGDATA_ID}: {table.texts[MSGDATA_ID]!r}")

    texts = list(table.texts)
    texts[MSGDATA_ID] = AFTER
    rebuilt_raw = rebuild_message_table(table, texts)
    rebuilt = recompress_wrapper(rebuilt_raw, header)
    _, check_raw = decompress_wrapper(rebuilt)
    check = parse_message_table(check_raw)
    changed = [index for index, pair in enumerate(zip(table.texts, check.texts)) if pair[0] != pair[1]]
    if changed != [MSGDATA_ID] or check.texts[MSGDATA_ID] != AFTER:
        raise ValueError(f"PK change set is not exact: {changed}")
    return rebuilt, {
        "id": MSGDATA_ID,
        "before": BEFORE,
        "after": AFTER,
        "changed_ids": changed,
    }


def build(input_root: Path, output_root: Path, validation_path: Path) -> dict[str, Any]:
    if input_root.resolve() == output_root.resolve():
        raise ValueError("input and output roots must differ")

    results: list[dict[str, Any]] = []
    for relative, builder in (
        (STRDATA_RELATIVE, rebuild_strdata),
        (MSGDATA_RELATIVE, rebuild_msgdata),
    ):
        source_path = input_root / relative
        target_path = output_root / relative
        source = pinned_blob(source_path, relative)
        target, detail = builder(source)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(target)
        results.append(
            {
                "relative_path": relative.as_posix(),
                "input_size": len(source),
                "input_sha256": sha256_bytes(source),
                "output_size": len(target),
                "output_sha256": sha256_bytes(target),
                **detail,
            }
        )

    report: dict[str, Any] = {
        "schema": "nobu16.kr.scenario-title-mugen.v1",
        "scope": "Base and PK 1582 scenario title",
        "official_title_matrix": OFFICIAL_TITLE_MATRIX,
        "translation_policy": "preserve the Kowakamai Atsumori phrase instead of paraphrasing it",
        "resources": results,
    }
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--validation", type=Path, default=WORKSTREAM_ROOT / "validation.v1.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build(args.input_root, args.output_root, args.validation)
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
