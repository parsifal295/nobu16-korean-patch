#!/usr/bin/env python3
"""Unify the gameplay rank 組頭 as 조장 in Base/PK dialogue and PK UI."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = SCRIPT.parents[2]
sys.path[:0] = [str(REPO / "tools"), str(REPO / "workstreams" / "msggame")]

import msggame_format as msggame  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


JP_TERM = "組頭"
BEFORE = "조두"
AFTER = "조장"

FILES: dict[str, dict[str, Any]] = {
    "MSG/JP/msggame.bin": {
        "kind": "msggame",
        "input_size": 1_556_016,
        "input_sha256": "3FAE2B624ED1D0C164CCDACF757360C9EAE1DC56EC54D61A6CEBAD06B231BFC7",
        "jp_size": 610_163,
        "jp_sha256": "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
        "coordinates": (
            (6, 4084, 0),
            (13, 83, 0),
            (13, 174, 0),
            (13, 383, 0),
            (14, 32, 3),
            (14, 33, 1),
            (14, 113, 1),
            (14, 117, 3),
            (14, 148, 1),
            (15, 1505, 2),
            (15, 1506, 0),
            (15, 1507, 0),
            (15, 1643, 0),
        ),
        "output_size": 1_556_016,
        "output_sha256": "AC3365D83C3A083A2C20F5C518B74C1C5E5D860347CBC7FB5156B3D8A3E363B8",
    },
    "MSG_PK/JP/msggame.bin": {
        "kind": "msggame",
        "input_size": 1_813_943,
        "input_sha256": "F09D9CCE819E26E3B14E368DD4AA7A7254D7CB81CBB5EB3860D0D1A099C4CFC1",
        "jp_size": 721_304,
        "jp_sha256": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
        "coordinates": (
            (6, 4094, 0),
            (13, 83, 0),
            (13, 174, 0),
            (13, 416, 0),
            (13, 417, 0),
            (14, 48, 3),
            (14, 49, 3),
            (14, 50, 1),
            (14, 51, 1),
            (14, 156, 1),
            (14, 157, 1),
            (14, 164, 3),
            (14, 165, 3),
            (14, 206, 1),
            (14, 207, 1),
            (15, 1520, 2),
            (15, 1521, 0),
            (15, 1522, 0),
            (15, 1673, 0),
        ),
        "output_size": 1_813_943,
        "output_sha256": "2DACF44094FD3D309BEC415AE4F1DFC5303410435FDD997CC34B95F49AC17C1C",
    },
    "MSG_PK/JP/msgui.bin": {
        "kind": "message_table",
        "input_size": 122_733,
        "input_sha256": "61D1C6691B97058D02753C088F95FB044DA09E015520A9FA74CC2050C7113EC9",
        "jp_size": 64_976,
        "jp_sha256": "9775D4B7253828899F7EF0DF2E88AB28121ACB260E1381F3D706C6A1065D504A",
        "ids": (160, 839, 3436),
        "output_size": 122_733,
        "output_sha256": "9AE0AC44491488383FBBC73BE0F7F188643E3AE17E5E4E984BE9D0FE0AD1AC65",
    },
}


class Issue125Error(ValueError):
    """Raised when a pinned input or exact-change contract differs."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def pinned_blob(root: Path, relative: str, *, size_key: str, hash_key: str) -> bytes:
    path = root / Path(relative)
    blob = path.read_bytes()
    policy = FILES[relative]
    if len(blob) != policy[size_key] or sha256(blob) != policy[hash_key]:
        raise Issue125Error(
            f"pin mismatch for {path}: size={len(blob)} sha256={sha256(blob)}"
        )
    return blob


def msggame_texts(blob: bytes) -> dict[tuple[int, int, int], str]:
    parsed = msggame.parse_packed_msggame(blob)
    return {
        (item.block_id, item.record_id, item.literal_id): item.text
        for item in msggame.iter_literals(parsed.archive)
    }


def build_msggame(relative: str, current: bytes, japanese: bytes) -> tuple[bytes, dict[str, Any]]:
    policy = FILES[relative]
    expected = tuple(policy["coordinates"])
    before_map = msggame_texts(current)
    jp_map = msggame_texts(japanese)
    before_hits = tuple(sorted(key for key, text in before_map.items() if BEFORE in text))
    jp_hits = tuple(sorted(key for key, text in jp_map.items() if JP_TERM in text))
    if before_hits != expected:
        raise Issue125Error(f"unexpected {BEFORE} coordinates in {relative}: {before_hits}")
    if jp_hits != expected:
        raise Issue125Error(f"unexpected {JP_TERM} coordinates in {relative}: {jp_hits}")

    replacements: dict[tuple[int, int, int], str] = {}
    for coordinate in expected:
        before = before_map[coordinate]
        source = jp_map[coordinate]
        if before.count(BEFORE) != 1 or source.count(JP_TERM) != 1:
            raise Issue125Error(f"non-unique term at {relative} {coordinate}")
        after = before.replace(BEFORE, AFTER)
        if len(after.encode("utf-16le")) != len(before.encode("utf-16le")):
            raise Issue125Error(f"UTF-16 length changed at {relative} {coordinate}")
        if after.count("\n") != before.count("\n"):
            raise Issue125Error(f"line topology changed at {relative} {coordinate}")
        replacements[coordinate] = after

    output = msggame.rebuild_packed_with_literals(current, replacements)
    after_map = msggame_texts(output)
    changed = tuple(sorted(key for key in before_map if before_map[key] != after_map[key]))
    if changed != expected:
        raise Issue125Error(f"unexpected changed coordinates in {relative}: {changed}")
    if any(BEFORE in text for text in after_map.values()):
        raise Issue125Error(f"{BEFORE} remains in {relative}")
    for coordinate in expected:
        if after_map[coordinate] != replacements[coordinate]:
            raise Issue125Error(f"replacement mismatch at {relative} {coordinate}")
    return output, {
        "relative_path": relative,
        "kind": policy["kind"],
        "changed_count": len(changed),
        "coordinates": [list(item) for item in changed],
    }


def build_message_table(relative: str, current: bytes, japanese: bytes) -> tuple[bytes, dict[str, Any]]:
    policy = FILES[relative]
    expected = tuple(policy["ids"])
    header, current_raw = decompress_wrapper(current)
    _jp_header, jp_raw = decompress_wrapper(japanese)
    before_table = parse_message_table(current_raw)
    jp_table = parse_message_table(jp_raw)
    before_hits = tuple(index for index, text in enumerate(before_table.texts) if BEFORE in text)
    jp_hits = tuple(index for index, text in enumerate(jp_table.texts) if JP_TERM in text)
    if before_hits != expected:
        raise Issue125Error(f"unexpected {BEFORE} IDs in {relative}: {before_hits}")
    if jp_hits != expected:
        raise Issue125Error(f"unexpected {JP_TERM} IDs in {relative}: {jp_hits}")

    texts = list(before_table.texts)
    for index in expected:
        if texts[index].count(BEFORE) != 1 or jp_table.texts[index].count(JP_TERM) != 1:
            raise Issue125Error(f"non-unique term at {relative} ID {index}")
        texts[index] = texts[index].replace(BEFORE, AFTER)
    output = recompress_wrapper(rebuild_message_table(before_table, texts), header)
    _output_header, output_raw = decompress_wrapper(output)
    after_table = parse_message_table(output_raw)
    changed = tuple(
        index
        for index, pair in enumerate(zip(before_table.texts, after_table.texts))
        if pair[0] != pair[1]
    )
    if changed != expected:
        raise Issue125Error(f"unexpected changed IDs in {relative}: {changed}")
    if any(BEFORE in text for text in after_table.texts):
        raise Issue125Error(f"{BEFORE} remains in {relative}")
    return output, {
        "relative_path": relative,
        "kind": policy["kind"],
        "changed_count": len(changed),
        "ids": list(changed),
    }


def validate_output_pin(relative: str, blob: bytes) -> None:
    policy = FILES[relative]
    if len(blob) != policy["output_size"] or sha256(blob) != policy["output_sha256"]:
        raise Issue125Error(
            f"output pin mismatch for {relative}: size={len(blob)} sha256={sha256(blob)}"
        )


def assert_safe_output(input_root: Path, jp_root: Path, output_root: Path) -> None:
    inputs = (input_root.resolve(), jp_root.resolve())
    output = output_root.resolve()
    for item in inputs:
        if output == item or item in output.parents:
            raise Issue125Error(f"output must not contain or replace an input root: {output}")
    folded = str(output).replace("/", "\\").casefold()
    if "\\steamapps\\common\\nobu16" in folded:
        raise Issue125Error("builder must not write into a Steam game installation")


def build(input_root: Path, jp_root: Path, output_root: Path, validation_path: Path) -> dict[str, Any]:
    assert_safe_output(input_root, jp_root, output_root)
    reports: list[dict[str, Any]] = []
    for relative, policy in FILES.items():
        target_path = output_root / Path(relative)
        if target_path.exists():
            raise Issue125Error(f"refusing to overwrite candidate output: {target_path}")
        current = pinned_blob(input_root, relative, size_key="input_size", hash_key="input_sha256")
        japanese = pinned_blob(jp_root, relative, size_key="jp_size", hash_key="jp_sha256")
        if policy["kind"] == "msggame":
            output, detail = build_msggame(relative, current, japanese)
        else:
            output, detail = build_message_table(relative, current, japanese)
        validate_output_pin(relative, output)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(output)
        reports.append(
            {
                **detail,
                "input_size": len(current),
                "input_sha256": sha256(current),
                "output_size": len(output),
                "output_sha256": sha256(output),
            }
        )

    report: dict[str, Any] = {
        "schema": "nobu16.kr.issue-125-kumigashira.v1",
        "issue": 125,
        "scope": "gameplay rank dialogue and UI",
        "japanese_term": JP_TERM,
        "before": BEFORE,
        "after": AFTER,
        "changed_count": sum(item["changed_count"] for item in reports),
        "resources": reports,
        "excluded_contexts": [
            "historical biography uses such as 근습조두 and 칠수조 조두",
        ],
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
    parser.add_argument("--jp-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--validation", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validation = args.validation or (args.output_root / "validation.v1.json")
    report = build(args.input_root, args.jp_root, args.output_root, validation)
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
