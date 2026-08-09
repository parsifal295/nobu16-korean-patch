#!/usr/bin/env python3
"""Replace the 25 active PK policy pinyin readings with reviewed Hangul readings.

The builder accepts only the hash-pinned final v0.92 ``MSG_PK/JP/msgdata.bin``
and pristine Steam Japanese source table.  Candidate output is restricted to
the workspace scratch directory and never writes to an installed game.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import re
import sys
from pathlib import Path
from typing import Any, Sequence


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
WORKSPACE = REPO.parents[1]
SCRATCH_ROOT = WORKSPACE / "scratch"


def import_file(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


COMMON = import_file(
    "pk_policy_readings_common",
    REPO
    / "workstreams"
    / "steam_jp_common_messages_v1"
    / "build_steam_jp_common_messages_v1.py",
)


SCHEMA = "nobu16.kr.pk-policy-readings-validation.v1"
RESOURCE = Path("MSG_PK/JP/msgdata.bin")
DISPLAY_START = 21_256
READING_START = 21_356
PAIR_COUNT = 25
DISPLAY_IDS = tuple(range(DISPLAY_START, DISPLAY_START + PAIR_COUNT))
READING_IDS = tuple(range(READING_START, READING_START + PAIR_COUNT))

INPUT_PIN = {
    "packed_size": 477_193,
    "packed_sha256": "DC27B7FA285848AA46289DA4C4E722017A1B3BDAA4E36116CA8FB8D263142898",
    "raw_size": 475_304,
    "raw_sha256": "63D8F0E30114BF91F508FE329EC0CB5F119B338C38E8780159E63A98B3095556",
    "entry_count": 29_218,
}

STOCK_JP_PIN = {
    "packed_size": 272_453,
    "packed_sha256": "13498FBFFF6D33F0BFB0915B6F365F076FE8E78046EE411BB8478235C86C2C9E",
    "raw_size": 434_000,
    "raw_sha256": "D09F61E34E4AA498F3DDEF23E7B7FD2CC8E9FE50B24F39D3BA1034BE82E6D0F6",
    "entry_count": 29_218,
}

OUTPUT_PIN = {
    "packed_size": 476_860,
    "packed_sha256": "6D7DEA6149FE9B40951B507E7E210A614169D8CB19AEDE3EB85BC8B15EDF2410",
    "raw_size": 474_972,
    "raw_sha256": "3C71C6F6B464C69DE6103316F59A18C0CD41C977985DC7BC8AEECFF78CFC6157",
    "entry_count": 29_218,
}

DISPLAY_PREIMAGES = {
    21_256: "제도 개신·이",
    21_257: "영토 보전",
    21_258: "명문의 영예",
    21_259: "학승 초빙",
    21_260: "어용 상인",
    21_261: "병법 지도",
    21_262: "마을 규약",
    21_263: "팔진의 법",
    21_264: "관리 주도",
    21_265: "상급 닌자 규율",
    21_266: "해적 수송술",
    21_267: "에이린 벽서",
    21_268: "적재적소",
    21_269: "오모다카의 정치",
    21_270: "마흔여덟 마리의 매",
    21_271: "하가쿠레",
    21_272: "조슈의 영수",
    21_273: "삼덕 인정",
    21_274: "정도 매진",
    21_275: "향사제",
    21_276: "사가라씨 벽서",
    21_277: "회선 식목",
    21_278: "고쿠시의 통치",
    21_279: "전마제",
    21_280: "군지제",
}

READING_PREIMAGES = {
    21_356: "gexinzhiduer",
    21_357: "baoquanlingtu",
    21_358: "mingmenrongyao",
    21_359: "zhaopinxueseng",
    21_360: "yuyongshangren",
    21_361: "bingfazhinan",
    21_362: "cungui",
    21_363: "bazhenzhifa",
    21_364: "guanlizhudao",
    21_365: "shangrentielv",
    21_366: "haizeiyunshushu",
    21_367: "yinglinbishu",
    21_368: "liangcailuyong",
    21_369: "zexiezhizheng",
    21_370: "sishibaying",
    21_371: "yeyin",
    21_372: "changlushouling",
    21_373: "sanderenzheng",
    21_374: "maijinzhengdao",
    21_375: "xiangshizhi",
    21_376: "xiangliangshibishu",
    21_377: "huichuanshimu",
    21_378: "guosizhizhi",
    21_379: "chuanmazhi",
    21_380: "junsizhi",
}

READING_REPLACEMENTS = {
    21_356: "세이도카이신니",
    21_357: "료도호젠",
    21_358: "고케노호마레",
    21_359: "가쿠소쇼헤이",
    21_360: "고요쇼닌",
    21_361: "헤이호시난",
    21_362: "무라오키테",
    21_363: "하치진노호",
    21_364: "간리슈도",
    21_365: "조닌노오키테",
    21_366: "가이조쿠유소주쓰",
    21_367: "에이린카베가키",
    21_368: "료사이로쿠요",
    21_369: "오모다카노세이",
    21_370: "시주핫타카",
    21_371: "하가쿠레",
    21_372: "조슈노하타가시라",
    21_373: "산토쿠진세이",
    21_374: "쇼도마이신",
    21_375: "고시세이",
    21_376: "사가라시헤키쇼",
    21_377: "가이센시키모쿠",
    21_378: "고쿠시노치",
    21_379: "텐마세이",
    21_380: "군지세이",
}

ASCII_RE = re.compile(r"[A-Za-z]")
ASCII_ONLY_RE = re.compile(r"[A-Za-z]+\Z")
HANGUL_ONLY_RE = re.compile(r"[가-힣]+\Z")
KANA_RE = re.compile(r"[\u3040-\u30ff]")


class BuildError(RuntimeError):
    """Raised when a pin, reviewed mapping, or structural invariant differs."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def load_table(
    path: Path, pin: dict[str, int | str], label: str
) -> tuple[bytes, Any, bytes, Any]:
    packed = path.read_bytes()
    if len(packed) != pin["packed_size"] or sha256(packed) != pin["packed_sha256"]:
        raise BuildError(f"{label} packed pin mismatch: {path}")
    header, raw = COMMON.decompress_wrapper(packed)
    if len(raw) != pin["raw_size"] or sha256(raw) != pin["raw_sha256"]:
        raise BuildError(f"{label} raw pin mismatch: {path}")
    table = COMMON.parse_message_table(raw)
    if table.string_count != pin["entry_count"]:
        raise BuildError(f"{label} entry count mismatch")
    if COMMON.rebuild_message_table(table, table.texts) != raw:
        raise BuildError(f"{label} unchanged raw rebuild is not byte-identical")
    return packed, header, raw, table


def validate_static_contract() -> None:
    if DISPLAY_IDS != tuple(range(21_256, 21_281)):
        raise BuildError("display coordinate vector differs")
    if READING_IDS != tuple(range(21_356, 21_381)):
        raise BuildError("reading coordinate vector differs")
    if set(DISPLAY_PREIMAGES) != set(DISPLAY_IDS):
        raise BuildError("display preimage domain differs")
    if set(READING_PREIMAGES) != set(READING_IDS):
        raise BuildError("reading preimage domain differs")
    if set(READING_REPLACEMENTS) != set(READING_IDS):
        raise BuildError("reading replacement domain differs")
    if any(reading_id - display_id != 100 for display_id, reading_id in zip(DISPLAY_IDS, READING_IDS, strict=True)):
        raise BuildError("display/reading pair offset differs")
    if any(ASCII_ONLY_RE.fullmatch(value) is None for value in READING_PREIMAGES.values()):
        raise BuildError("a reading preimage is not lexical ASCII")
    if any(HANGUL_ONLY_RE.fullmatch(value) is None for value in READING_REPLACEMENTS.values()):
        raise BuildError("a reading replacement is not Hangul-only")
    if any("\x00" in value for value in READING_REPLACEMENTS.values()):
        raise BuildError("a reading replacement contains NUL")


def opaque_prefix(raw: bytes, table: Any) -> bytes:
    """Return all opaque pre-table bytes except the mutable logical-size u32."""
    return raw[:8] + raw[12 : table.table_offset]


def build_candidate(
    input_packed: bytes,
    input_header: Any,
    input_raw: bytes,
    input_table: Any,
    stock_table: Any,
) -> tuple[bytes, dict[str, Any]]:
    validate_static_contract()

    for display_id in DISPLAY_IDS:
        actual = input_table.texts[display_id]
        if actual != DISPLAY_PREIMAGES[display_id]:
            raise BuildError(f"display preimage mismatch at {display_id}: {actual!r}")
        if not stock_table.texts[display_id] or "ダミー" in stock_table.texts[display_id]:
            raise BuildError(f"stock display is blank or dummy at {display_id}")

    for reading_id in READING_IDS:
        actual = input_table.texts[reading_id]
        if actual != READING_PREIMAGES[reading_id]:
            raise BuildError(f"reading preimage mismatch at {reading_id}: {actual!r}")
        stock_reading = stock_table.texts[reading_id]
        if KANA_RE.search(stock_reading) is None or "ダミー" in stock_reading:
            raise BuildError(f"stock reading is not an active kana reading at {reading_id}")

    before_ascii = sum(
        bool(ASCII_RE.search(input_table.texts[reading_id])) for reading_id in READING_IDS
    )
    if before_ascii != PAIR_COUNT:
        raise BuildError(f"ASCII policy reading count before differs: {before_ascii}")

    texts = list(input_table.texts)
    for reading_id, replacement in READING_REPLACEMENTS.items():
        texts[reading_id] = replacement

    raw = COMMON.rebuild_message_table(input_table, texts)
    candidate = COMMON.recompress_wrapper(raw, input_header)
    checked_header, checked_raw = COMMON.decompress_wrapper(candidate)
    checked_table = COMMON.parse_message_table(checked_raw)

    if checked_table.texts != tuple(texts):
        raise BuildError("candidate parse verification mismatch")
    changed_ids = [
        entry_id
        for entry_id, (before, after) in enumerate(
            zip(input_table.texts, checked_table.texts, strict=True)
        )
        if before != after
    ]
    if changed_ids != list(READING_IDS):
        raise BuildError(f"changed coordinate vector differs: {changed_ids!r}")
    if any(
        input_table.texts[entry_id] != checked_table.texts[entry_id]
        for entry_id in range(input_table.string_count)
        if entry_id not in READING_REPLACEMENTS
    ):
        raise BuildError("a non-target string changed")
    if any(
        checked_table.texts[display_id] != DISPLAY_PREIMAGES[display_id]
        for display_id in DISPLAY_IDS
    ):
        raise BuildError("a paired display name changed")

    after_ascii = sum(
        bool(ASCII_RE.search(checked_table.texts[reading_id])) for reading_id in READING_IDS
    )
    if after_ascii != 0:
        raise BuildError(f"ASCII policy reading count after differs: {after_ascii}")

    if checked_header.prefix != input_header.prefix:
        raise BuildError("wrapper opaque prefix changed")
    if checked_table.block_offset != input_table.block_offset:
        raise BuildError("message block offset changed")
    if checked_table.table_offset != input_table.table_offset:
        raise BuildError("message table offset changed")
    if checked_table.table_size != input_table.table_size:
        raise BuildError("message table size changed")
    if checked_table.string_count != input_table.string_count:
        raise BuildError("message entry count changed")
    if opaque_prefix(checked_raw, checked_table) != opaque_prefix(input_raw, input_table):
        raise BuildError("opaque raw metadata changed")
    if any(checked_table.padding):
        raise BuildError("candidate alignment padding is nonzero")

    output = {
        "packed_size": len(candidate),
        "packed_sha256": sha256(candidate),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
        "entry_count": checked_table.string_count,
    }
    if OUTPUT_PIN is not None and output != OUTPUT_PIN:
        raise BuildError(f"output pin mismatch: {output!r}")

    pairs = []
    for display_id, reading_id in zip(DISPLAY_IDS, READING_IDS, strict=True):
        pairs.append(
            {
                "display_id": display_id,
                "reading_id": reading_id,
                "display": input_table.texts[display_id],
                "before_reading": input_table.texts[reading_id],
                "after_reading": checked_table.texts[reading_id],
                "stock_display_utf16le_sha256": COMMON.text_hash(stock_table.texts[display_id]),
                "stock_reading_utf16le_sha256": COMMON.text_hash(stock_table.texts[reading_id]),
            }
        )

    validation = {
        "schema": SCHEMA,
        "resource": RESOURCE.as_posix(),
        "input": INPUT_PIN,
        "stock_jp": STOCK_JP_PIN,
        "output": output,
        "pair_count": PAIR_COUNT,
        "display_coordinate_range": [DISPLAY_IDS[0], DISPLAY_IDS[-1]],
        "reading_coordinate_range": [READING_IDS[0], READING_IDS[-1]],
        "changed_coordinates": changed_ids,
        "changed_coordinates_sha256": COMMON.canonical_hash(changed_ids),
        "ascii_policy_readings_before": before_ascii,
        "ascii_policy_readings_after": after_ascii,
        "paired_display_names_unchanged": True,
        "all_other_strings_exact": True,
        "opaque_metadata_preserved": True,
        "wrapper_prefix_preserved": True,
        "entry_count_preserved": True,
        "pairs": pairs,
        "steam_written": False,
        "result": "PASS",
    }
    return candidate, validation


def require_scratch_output(output_root: Path) -> Path:
    resolved = output_root.resolve()
    scratch = SCRATCH_ROOT.resolve()
    try:
        resolved.relative_to(scratch)
    except ValueError as exc:
        raise BuildError(f"output root must be below workspace scratch: {scratch}") from exc
    return resolved


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("verify", "build"))
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--stock-jp-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path)
    args = parser.parse_args(argv)

    input_root = args.input_root.resolve()
    stock_root = args.stock_jp_root.resolve()
    input_packed, input_header, input_raw, input_table = load_table(
        input_root / RESOURCE, INPUT_PIN, "v0.92 final target"
    )
    _stock_packed, _stock_header, _stock_raw, stock_table = load_table(
        stock_root / RESOURCE, STOCK_JP_PIN, "pristine Steam JP"
    )
    candidate, validation = build_candidate(
        input_packed, input_header, input_raw, input_table, stock_table
    )

    if args.mode == "build":
        if args.output_root is None:
            parser.error("build requires --output-root")
        output_root = require_scratch_output(args.output_root)
        if output_root in (input_root, stock_root):
            raise BuildError("output root must differ from input roots")
        output_path = output_root / RESOURCE
        validation_path = output_root / "validation.pk_policy_readings.v1.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(candidate)
        validation_path.write_bytes(COMMON.pretty_bytes(validation))
        print(f"candidate={output_path}")
        print(f"validation={validation_path}")

    print(f"output_size={validation['output']['packed_size']}")
    print(f"output_sha256={validation['output']['packed_sha256']}")
    print(f"raw_size={validation['output']['raw_size']}")
    print(f"raw_sha256={validation['output']['raw_sha256']}")
    print(f"changed_coordinates={','.join(str(value) for value in validation['changed_coordinates'])}")
    print("result=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
