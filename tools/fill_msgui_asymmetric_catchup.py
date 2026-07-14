#!/usr/bin/env python3
"""Fill the source-private MSGUI asymmetric-slot batch deterministically.

This tracked helper contains only stable numeric IDs and project-owned Korean
text.  The input development batch contains the commercial multilingual source
strings and therefore remains Git-ignored.  The helper never reads or modifies
an installed game resource.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import unicodedata
from pathlib import Path
from typing import Any, Sequence


BATCH_SCHEMA = "nobu16.kr.msgui-translation-batch.v1"

TRANSLATIONS: dict[int, str] = {
    2329: "체력 무적",
    2330: "퇴각 무효",
    2331: "부대 노림",
    2332: "능력",
    2333: "미설정",
    2334: "공격",
    2335: "병력",
    2336: "위축",
    2337: "능력",
    2338: "포박률",
    2339: "체력",
    2340: "피해",
    2341: "체력 회복 속도",
    2342: "부상률",
    2343: "공격",
    2344: "혼란 부여",
    2345: "이동",
    2346: "체력",
    2347: "기마·철포 무효",
    2348: "농촌 석고",
    2408: "완전 자동",
    2409: "성주 자동 지행",
    2419: "체력 회복 가속",
    2420: "체력 회복 감속",
    2457: "추가 효과",
    2459: "Pt",
    2558: "설정 곡",
    2650: "부장 이상",
    2657: "%s, %s 출신.",
    2661: "사격 피해 상승",
    2691: "병력 회복",
    2692: "기마·철포 무효",
    2693: "병력 감소",
    2694: "자기 부대의 병력 감소",
    2695: "아군 부대의 병력 감소",
    2696: "적 부대의 병력 감소",
    2697: "공격 상승",
    2698: "공격 저하",
    2699: "자기 부대의 공격 상승",
    2700: "자기 부대의 공격 저하",
    2701: "아군 부대의 공격 상승",
    2702: "아군 부대의 공격 저하",
    2703: "적 부대의 공격 상승",
    2704: "적 부대의 공격 저하",
    2705: "이동 상승",
    2706: "이동 저하",
    2707: "자기 부대의 이동 상승",
    2708: "자기 부대의 이동 저하",
    2709: "아군 부대의 이동 상승",
    2710: "아군 부대의 이동 저하",
    2711: "적 부대의 이동 상승",
    2712: "적 부대의 이동 저하",
    2713: "방어 상승",
    2714: "방어 저하",
    2715: "자기 부대의 방어 상승",
    2716: "자기 부대의 방어 저하",
    2717: "아군 부대의 방어 상승",
    2718: "아군 부대의 방어 저하",
    2719: "적 부대의 방어 상승",
    2720: "적 부대의 방어 저하",
    2721: "체력 회복",
    2722: "자기 부대의 체력 회복",
    2723: "아군 부대의 체력 회복",
    2724: "적 부대의 체력 회복",
    2725: "체력 저하",
    2726: "자기 부대의 체력 저하",
    2727: "아군 부대의 체력 저하",
    2728: "적 부대의 체력 저하",
    2729: "자기 부대의 병력 회복",
    2730: "아군 부대의 병력 회복",
    2731: "혼란 무효",
    2732: "자기 부대의 혼란 무효",
    2733: "아군 부대의 혼란 무효",
    2734: "적 부대의 혼란 무효",
    2735: "혼란 부여",
    2736: "자기 부대에 혼란 부여",
    2737: "아군 부대에 혼란 부여",
    2738: "적 부대에 혼란 부여",
    2739: "퇴각 무효",
    2740: "자기 부대의 퇴각 무효",
    2741: "아군 부대의 퇴각 무효",
    2742: "적 부대의 퇴각 무효",
    2743: "전법 회복 속도 상승",
    2744: "자기 부대의 전법 회복 속도 상승",
    2745: "아군 부대의 전법 회복 속도 상승",
    2746: "적 부대의 전법 회복 속도 상승",
}

STRUCTURAL_EMPTY_IDS = (733, 734, 1607)
PRESERVED_LANGUAGE_SPECIFIC_IDS = (
    513,
    689,
    691,
    1302,
    1350,
    1352,
    1694,
    *range(1921, 1933),
    2570,
    2571,
    2572,
)
REVIEWED_OVERRIDES = {2657: ["printf:EN"]}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


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


def fill_batch(input_path: Path, output_path: Path) -> dict[str, Any]:
    value = json.loads(input_path.read_text(encoding="utf-8"))
    if value.get("schema") != BATCH_SCHEMA:
        raise ValueError("unsupported MSGUI translation batch schema")
    if value.get("resource") != "msgui" or value.get("base_language") != "SC":
        raise ValueError("translation batch resource/base language mismatch")
    if value.get("development_only") is not True:
        raise ValueError("input must remain a development-only source batch")
    policy = value.get("distribution_policy", {})
    if policy.get("contains_commercial_source_text") is not True:
        raise ValueError("input source-text policy marker is missing")
    if policy.get("include_in_public_patch") is not False:
        raise ValueError("source-containing batch must not enter the public patch")

    entries = value.get("entries")
    if not isinstance(entries, list):
        raise ValueError("entries must be an array")
    ids = [int(item["id"]) for item in entries]
    expected_ids = sorted(set(TRANSLATIONS) | set(PRESERVED_LANGUAGE_SPECIFIC_IDS))
    if ids != expected_ids or len(ids) != len(set(ids)):
        raise ValueError(
            f"input ID inventory mismatch: expected {len(expected_ids)}, got {len(ids)}"
        )
    if len(TRANSLATIONS) != 86:
        raise AssertionError("translated asymmetric inventory must remain exactly 86 IDs")
    if len(PRESERVED_LANGUAGE_SPECIFIC_IDS) != 22:
        raise AssertionError("language-specific preservation inventory must remain exactly 22 IDs")
    if set(TRANSLATIONS) & set(PRESERVED_LANGUAGE_SPECIFIC_IDS):
        raise AssertionError("translated and preserved inventories must not overlap")

    for item in entries:
        entry_id = int(item["id"])
        if entry_id in PRESERVED_LANGUAGE_SPECIFIC_IDS:
            item["ko"] = ""
            item["status"] = "untranslated"
            item["context"] = {
                "category": "language_specific_blank",
                "screen": "sc_layout_preserved",
                "notes": "일본어 읽기·IME 전용 슬롯이므로 공식 SC 공백과 레이아웃을 유지",
            }
            item["review"] = {
                "translator": "project",
                "reviewer": "project",
                "notes": "의도적 미적용: 한국어 문자열을 넣으면 SC 화면 구조나 기능을 활성화할 수 있음",
            }
            continue
        ko = unicodedata.normalize("NFC", TRANSLATIONS[entry_id])
        if not ko.strip() or "\x00" in ko:
            raise ValueError(f"id {entry_id}: invalid Korean translation")
        item["ko"] = ko
        if entry_id in REVIEWED_OVERRIDES:
            item["status"] = "reviewed"
            item["invariant_overrides"] = REVIEWED_OVERRIDES[entry_id]
            item["review"] = {
                "translator": "project",
                "reviewer": "project",
                "notes": "SC 공백 슬롯의 printf 계약을 공식 EN 원문과 대조해 보존",
            }

    value["description"] = (
        "SC 공백 비대칭 슬롯 중 언어 중립 86개의 한국어 초벌과 일본어 읽기·IME "
        "전용 22개의 의도적 공백 보존. 공개물에는 원문을 제외한 ID·SC 해시·한국어만 수록한다."
    )
    value["defaults"]["context"]["notes"] = (
        "SC 경로에서는 공백인 언어별·내부 슬롯의 화면/문맥 검수 전 초벌 번역"
    )
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    atomic_write(output_path, payload)
    return {
        "output": str(output_path),
        "input_entry_count": len(entries),
        "translated_entry_count": len(TRANSLATIONS),
        "preserved_language_specific_count": len(PRESERVED_LANGUAGE_SPECIFIC_IDS),
        "reviewed_override_count": len(REVIEWED_OVERRIDES),
        "structural_empty_ids": list(STRUCTURAL_EMPTY_IDS),
        "sha256": sha256_bytes(payload),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = fill_batch(args.input.resolve(), args.output.resolve())
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
