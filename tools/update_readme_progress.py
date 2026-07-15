#!/usr/bin/env python3
"""Regenerate the public Steam JP v1.1.7 progress block in README.md."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
PROGRESS = ROOT / "data" / "public" / "steam_jp_117_progress.v1.json"
START = "<!-- translation-progress:start -->"
END = "<!-- translation-progress:end -->"


def load_progress() -> dict:
    payload = json.loads(PROGRESS.read_text(encoding="utf-8"))
    if payload.get("schema") != "nobu16.kr.steam-jp-1.1.7-progress.v1":
        raise ValueError("unsupported Steam JP progress schema")
    runtime = payload.get("runtime", {})
    expected_runtime = {
        "distribution": "Steam",
        "pk_version": "1.1.7",
        "steam_build_id": 18823764,
        "language_route": "JP",
        "launcher_language": "日本語 / Japanese",
    }
    if runtime != expected_runtime:
        raise ValueError(f"unexpected runtime contract: {runtime!r}")
    translation = payload.get("translation")
    if not isinstance(translation, dict):
        raise ValueError("progress payload has no translation object")
    return payload


def percent(done: int, total: int) -> float:
    if done < 0 or total <= 0 or done > total:
        raise ValueError(f"invalid progress fraction: {done}/{total}")
    return done * 100.0 / total


def render() -> str:
    payload = load_progress()
    translation = payload["translation"]
    msgui = translation["msgui"]
    common = translation["common_messages"]
    msggame = translation["msggame"]
    strdata = translation["strdata"]
    fonts = translation["fonts"]

    if msgui["safely_mapped"] != msgui["effective_changes"] + msgui["source_equal_noops"]:
        raise ValueError("msgui safe-map accounting mismatch")
    if msgui["catalog_entries"] != msgui["safely_mapped"] + msgui["withheld"]:
        raise ValueError("msgui catalog accounting mismatch")
    if msggame["semantic_targets"] != msggame["applied"] + msggame["remaining"]:
        raise ValueError("msggame accounting mismatch")
    if strdata["safe_targets"] != strdata["applied"] + strdata["withheld"]:
        raise ValueError("strdata accounting mismatch")
    if fonts["containers"] != fonts["verified"]:
        raise ValueError("font verification is incomplete")

    common_total = common["applied"] + common["unresolved"]
    lines = [
        START,
        "| 영역 | 적용 현황 | 남은 작업 |",
        "|---|---:|---:|",
        (
            f"| PK UI `msgui.bin` | 안전 이식 {msgui['safely_mapped']:,} / "
            f"{msgui['catalog_entries']:,} "
            f"({percent(msgui['safely_mapped'], msgui['catalog_entries']):.2f}%) | "
            f"{msgui['withheld']:,} |"
        ),
        (
            f"| PK 공용 메시지 5종 | 적용 {common['applied']:,} / {common_total:,} "
            f"({percent(common['applied'], common_total):.1f}%) | "
            f"{common['unresolved']:,} |"
        ),
        (
            f"| PK 본문 `msggame.bin` | 적용 {msggame['applied']:,} / "
            f"{msggame['semantic_targets']:,} "
            f"({percent(msggame['applied'], msggame['semantic_targets']):.1f}%) | "
            f"{msggame['remaining']:,} |"
        ),
        (
            f"| 공용 `strdata.bin` | 안전 이식 {strdata['applied']:,} / "
            f"{strdata['safe_targets']:,} | {strdata['withheld']:,} |"
        ),
        (
            f"| 일본어 경로 한글 폰트 | {fonts['verified']} / "
            f"{fonts['containers']} 실기 확인 | 0 |"
        ),
        "",
        (
            f"`msgui.bin`의 안전 이식 {msgui['safely_mapped']:,}건 중 실제 문구 변경은 "
            f"{msgui['effective_changes']:,}건이고, {msgui['source_equal_noops']:,}건은 원문과"
        ),
        (
            f"동일합니다. 보류 {msgui['withheld']:,}건은 번역 대상 문구가 아닌 비의미 공백 "
            "1자 레코드입니다."
        ),
        (
            f"공용 메시지의 중복 문맥 {common['duplicate_context_collapsed']:,}건은 동일 대상으로 "
            "합쳐졌습니다. 수치는"
        ),
        "구조를 보존해 현재 Steam 1.1.7 파일에 안전하게 이식된 항목",
        "기준이며, 줄바꿈·잘림·",
        "문맥 검수 완료율을 뜻하지는 않습니다.",
        "",
        "Steam PK v1.1.7 실기에서 일본어 런처, 한글 타이틀 안내, 한글 메인 메뉴와 두 한글",
        "폰트 컨테이너를 확인했습니다.",
        END,
    ]
    return "\n".join(lines)


def replace_block(readme: str, block: str) -> str:
    start = readme.find(START)
    end = readme.find(END)
    if start < 0 or end < 0 or end < start:
        raise ValueError("README progress markers are missing or out of order")
    end += len(END)
    return readme[:start] + block + readme[end:]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if README is stale")
    args = parser.parse_args()

    current = README.read_text(encoding="utf-8")
    expected = replace_block(current, render())
    if args.check:
        if current != expected:
            print("README Steam JP progress is stale; run tools/update_readme_progress.py")
            return 1
        print("README Steam JP progress is current")
        return 0
    if current != expected:
        README.write_text(expected, encoding="utf-8", newline="\n")
        print("updated README Steam JP progress")
    else:
        print("README Steam JP progress already current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
