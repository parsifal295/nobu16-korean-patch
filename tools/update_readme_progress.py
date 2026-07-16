#!/usr/bin/env python3
"""Regenerate the compact public v0.10.0 progress block in ``README.md``."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
RELEASE_PROGRESS = ROOT / "data" / "public" / "steam_jp_117_candidate_v10_progress.v1.json"
START = "<!-- translation-progress:start -->"
END = "<!-- translation-progress:end -->"
EXPECTED_RUNTIME = {
    "distribution": "Steam",
    "pk_version": "1.1.7",
    "steam_build_id": 18823764,
    "language_route": "JP",
    "launcher_language": "Japanese",
}


def load_release_progress() -> dict:
    """Load only the release facts shown in the public README."""

    payload = json.loads(RELEASE_PROGRESS.read_text(encoding="utf-8"))
    if (
        payload.get("schema") != "nobu16.kr.steam-jp-1.1.7-candidate-progress.v1"
        or payload.get("candidate_release") != "v0.10.0"
        or payload.get("status") != "released"
        or payload.get("runtime") != EXPECTED_RUNTIME
    ):
        raise ValueError("unexpected v0.10.0 release ledger")

    translation = payload.get("translation")
    expected_translation = {
        "active_text_tables": 10,
        "high_confidence_scope": 2498,
        "korean_applied": 2489,
        "official_credit_preserved": 6,
        "runtime_structure_preserved": 3,
        "manual_translation_hold": 0,
        "candidate_high_confidence_remaining": 9,
        "strdata_supersede_included_in_p0": 1,
        "mixed_hangul_kana_manual_review": 207,
        "hanja_only_manual_review": 187,
    }
    if translation != expected_translation:
        raise ValueError("unexpected v0.10.0 translation accounting")

    candidate = payload.get("candidate")
    if candidate != {
        "file_count": 14,
        "zip_name": "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.10.0.zip",
        "zip_sha256": "B18A5B2B4AE40BBD80BB8613BE3E6CD81DF7EDD3B7E7434A9446AFD576E2C117",
        "zip_size": 356864822,
    }:
        raise ValueError("unexpected v0.10.0 release asset")

    final = payload.get("final_composition")
    if not isinstance(final, dict):
        raise ValueError("v0.10.0 final composition is missing")
    if final.get("font_widths", {}).get("policy") != "original_widths_retained":
        raise ValueError("v0.10.0 font-width policy differs")
    linebreak = final.get("event_linebreak_rebase", {})
    if (
        linebreak.get("coordinate_count") != 4
        or linebreak.get("hard_break_token_count") != 6
    ):
        raise ValueError("v0.10.0 event linebreak summary differs")

    qa = payload.get("candidate_qa")
    expected_qa = {
        "translation_candidate_verification": "PASS",
        "event_linebreak_rebase": "PASS",
        "zip_rebuild": "PASS",
        "steam_install_applied": True,
        "screen_qa": "NOT_RERUN_AFTER_FONT_ROLLBACK_AND_EVENT_REBASE",
        "release_published": True,
        "file_only": True,
        "memory_patch": False,
        "dll_injection": False,
        "hooking": False,
        "executable_modified": False,
        "registry_modified": False,
    }
    if qa != expected_qa:
        raise ValueError("unexpected v0.10.0 release state")
    return payload


def render() -> str:
    payload = load_release_progress()
    translation = payload["translation"]
    intentionally_preserved = (
        translation["official_credit_preserved"]
        + translation["runtime_structure_preserved"]
    )
    return "\n".join(
        [
            START,
            "### v0.10.0 — 텍스트 번역 완료",
            "",
            "`v0.10.0`은 Steam JP 1.1.7용 공개 배포본입니다. 게임 내 번역 대상 텍스트 번역을 완료했습니다.",
            "",
            (
                f"공식 크레딧과 런타임 구조용 {intentionally_preserved}건은 번역 대상이 아니므로 "
                "원문을 유지합니다. 남은 것은 번역 작업이 아니라 일부 표현·화면의 선택 검수입니다."
            ),
            END,
        ]
    )


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
            print("README progress is stale; run tools/update_readme_progress.py")
            return 1
        print("README progress is current")
        return 0
    if current != expected:
        README.write_text(expected, encoding="utf-8", newline="\n")
        print("updated README progress")
    else:
        print("README progress already current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
