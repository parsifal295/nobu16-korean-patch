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
    if payload.get("release") != "v0.7.1":
        raise ValueError("Steam JP progress is not the v0.7.1 catalog")
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
    qa = payload.get("runtime_qa")
    if not isinstance(qa, dict):
        raise ValueError("Steam JP runtime QA object is missing")
    expected_qa_evidence = {
        "steam_install_applied": True,
        "exact_twelve_target_hashes": True,
        "pre_v0_7_predecessor_backups_valid": 12,
        "launcher_update_label": "Update 1.1.7",
        "korean_title_prompt_observed": True,
        "korean_main_menu_observed": True,
        "known_untranslated_ui_observed": True,
        "qhd_windowed": "PASS",
        "qhd_borderless": "PASS",
        "cold_restart": "PASS",
    }
    if any(qa.get(key) != value for key, value in expected_qa_evidence.items()):
        raise ValueError("Steam JP exact-12 runtime QA evidence is incomplete")
    if qa.get("current_release_live_apply") != "FILE_PASS":
        raise ValueError("v0.7.1 file-level live apply is incomplete")
    if qa.get("officer_surname_binary_recomposition") != "PASS":
        raise ValueError("v0.7.1 officer-surname binary regression is incomplete")
    if qa.get("v0_7_1_screen_qa") != "PENDING":
        raise ValueError("v0.7.1 screen QA state differs")
    if qa.get("evidence_release") != "v0.7.0":
        raise ValueError("v0.7.1 inherited screen evidence must identify v0.7.0")
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
    if fonts != {"containers": 4, "verified": 4}:
        raise ValueError("four-route font verification is incomplete")

    common_accounted = (
        common["applied"]
        + common["source_equal_structural_noops"]
        + common["format_contract_blocked"]
        + common["alignment_gap"]
    )
    if common_accounted != common["source_union_effective_coordinates"]:
        raise ValueError("common-message source-union accounting mismatch")
    if common["review_backlog"] != (
        common["format_contract_blocked"] + common["alignment_gap"]
    ):
        raise ValueError("common-message review-backlog accounting mismatch")
    if common["known_internal_dummy"] > common["alignment_gap"]:
        raise ValueError("known internal dummy records must be a subset of alignment gaps")
    if common["reviewed_semantic_gaps_pending"] != 94:
        raise ValueError("reviewed semantic-gap pending count mismatch")
    if common["officer_surnames_recovered"] != 980:
        raise ValueError("officer-surname recovery count mismatch")

    qa = payload["runtime_qa"]
    font_status = (
        f"{fonts['verified']} / {fonts['containers']} 포함 "
        "(v0.7.0 화면 검증 자원 유지)"
    )
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
            f"| PK 공용 메시지 5종 | 한국어 변경 {common['applied']:,} · 구조 확인 "
            f"{common['source_equal_structural_noops']:,} / 원천 합집합 "
            f"{common['source_union_effective_coordinates']:,} | "
            f"검토 {common['review_backlog']:,} |"
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
            f"| 일본어 경로 한글 폰트 | {font_status} | 0 |"
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
            f"v0.7.1에서는 인물 성씨 누락 {common['officer_surnames_recovered']:,}건을 복구했습니다. "
            f"별도 번역 묶음의 검토된 의미 간극 {common['reviewed_semantic_gaps_pending']:,}건은 "
            "이번 오류수정 릴리즈에 포함하지 않았습니다."
        ),
        (
            f"공용 메시지 원천 합집합 {common['source_union_effective_coordinates']:,}건은 한국어 변경 "
            f"{common['applied']:,}건, 원문 동일 구조 확인 "
            f"{common['source_equal_structural_noops']:,}건, 형식 계약 검토 "
            f"{common['format_contract_blocked']:,}건, 정렬 간극 "
            f"{common['alignment_gap']:,}건으로 정확히 분해됩니다."
        ),
        (
            f"남은 검토 {common['review_backlog']:,}건은 형식 계약과 정렬 감사 대상이며, 정렬 간극에는 "
            f"내부 더미 {common['known_internal_dummy']:,}건이 포함됩니다. 전역 번역 완료율이나 "
            "미번역 문장 수로 해석하면 안 됩니다."
        ),
        (
            f"공용 메시지의 중복 문맥 {common['duplicate_context_collapsed']:,}건은 동일 대상으로 "
            "합쳐졌습니다. 수치는"
        ),
        "구조를 보존해 현재 Steam 1.1.7 파일에 안전하게 이식된 항목",
        "기준이며, 줄바꿈·잘림·",
        "문맥 검수 완료율을 뜻하지는 않습니다.",
        "",
        (
            "v0.7.1 exact-12 파일 적용·해시 확인과 `오다 노부나가` 바이너리 재조합 검증을 "
            "마쳤습니다. 화면 검증은 PENDING이며, 기존 v0.7.0의 한글 타이틀·메인 메뉴와 "
            "4개 한글 폰트 화면 검증 자원을 그대로 유지합니다."
        ),
        "배포 구조는 Steam PK v1.1.7 일본어 경로의 원본 파일명 12개와 4개 한글 폰트를 유지하는 파일 전용 방식입니다.",
        "메모리 패치, DLL 주입, 후킹, EXE·레지스트리 변조는 사용하지 않습니다.",
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
