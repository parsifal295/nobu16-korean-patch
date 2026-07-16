#!/usr/bin/env python3
"""Regenerate the concise Steam-JP v1.1.7 progress block in ``README.md``."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
PROGRESS = ROOT / "data" / "public" / "steam_jp_117_progress.v1.json"
START = "<!-- translation-progress:start -->"
END = "<!-- translation-progress:end -->"
SHA256_RE = re.compile(r"[0-9A-F]{64}\Z")


def load_progress() -> dict:
    payload = json.loads(PROGRESS.read_text(encoding="utf-8"))
    if payload.get("schema") != "nobu16.kr.steam-jp-1.1.7-progress.v1":
        raise ValueError("unsupported Steam JP progress schema")
    if payload.get("release") != "v0.9.0":
        raise ValueError("progress catalog is not the v0.9.0 release")
    expected_runtime = {
        "distribution": "Steam",
        "pk_version": "1.1.7",
        "steam_build_id": 18823764,
        "language_route": "JP",
        "launcher_language": "Japanese",
    }
    if payload.get("runtime") != expected_runtime:
        raise ValueError("unexpected Steam JP runtime contract")
    if not isinstance(payload.get("translation"), dict):
        raise ValueError("progress payload has no translation object")
    qa = payload.get("runtime_qa")
    if not isinstance(qa, dict):
        raise ValueError("progress payload has no runtime QA object")
    expected_qa = {
        "candidate_verification": "PASS",
        "candidate_file_count": 14,
        "steam_install_applied": True,
        "steam_apply_transaction": "PASS",
        "steam_apply_backup_entries": 14,
        "screen_qa": "PASS",
        "manual_korean_screen_output": "PASS",
        "release_published": True,
        "file_only": True,
        "memory_patch": False,
        "dll_injection": False,
        "hooking": False,
        "executable_modified": False,
        "registry_modified": False,
    }
    if any(qa.get(key) != value for key, value in expected_qa.items()):
        raise ValueError("release QA state differs from the final v0.9.0 contract")
    if not isinstance(qa.get("candidate_zip_sha256"), str) or not SHA256_RE.fullmatch(
        qa["candidate_zip_sha256"]
    ):
        raise ValueError("candidate ZIP SHA-256 is invalid")
    return payload


def percent(done: int, total: int) -> float:
    if not isinstance(done, int) or not isinstance(total, int) or done < 0 or total <= 0 or done > total:
        raise ValueError(f"invalid progress fraction: {done}/{total}")
    return done * 100.0 / total


def render() -> str:
    payload = load_progress()
    translation = payload["translation"]
    msgui = translation["msgui"]
    common = translation["common_messages"]
    pk_msggame = translation["pk_msggame"]
    base_msggame = translation["base_msggame"]
    base_ev = translation["base_ev_strdata"]
    strdata = translation["strdata"]
    fonts = translation["fonts"]

    if msgui["safely_mapped"] != msgui["effective_changes"] + msgui["source_equal_noops"]:
        raise ValueError("msgui safe-map accounting mismatch")
    if msgui["catalog_entries"] != msgui["safely_mapped"] + msgui["withheld"]:
        raise ValueError("msgui catalog accounting mismatch")
    if pk_msggame["semantic_targets"] != pk_msggame["applied"] + pk_msggame["remaining"]:
        raise ValueError("PK msggame accounting mismatch")
    if strdata["safe_targets"] != strdata["applied"] + strdata["withheld"]:
        raise ValueError("strdata accounting mismatch")
    if fonts != {"containers": 4, "verified": 4}:
        raise ValueError("four-route font verification is incomplete")
    if (
        common["applied"]
        + common["source_equal_structural_noops"]
        + common["format_contract_blocked"]
        + common["alignment_gap"]
        != common["source_union_effective_coordinates"]
    ):
        raise ValueError("common-message accounting mismatch")
    if common["review_backlog"] != common["format_contract_blocked"] + common["alignment_gap"]:
        raise ValueError("common-message backlog accounting mismatch")
    for name, row in (("base_msggame", base_msggame), ("base_ev_strdata", base_ev)):
        if row["strict_switch_v13_transfer"] + row["residual"] != (
            row["source_script_literals"]
            if name == "base_msggame"
            else row["switch_hangul_candidates"]
        ):
            raise ValueError(f"{name} transfer accounting mismatch")

    qa = payload["runtime_qa"]
    lines = [
        START,
        "| 영역 | 안전 이식/검증 현황 | 별도 검토 |",
        "|---|---:|---:|",
        (
            f"| PK UI `msgui.bin` | {msgui['safely_mapped']:,} / {msgui['catalog_entries']:,} "
            f"({percent(msgui['safely_mapped'], msgui['catalog_entries']):.2f}%) | {msgui['withheld']:,} |"
        ),
        (
            f"| PK 공용 메시지 5종 | 한국어 변경 {common['applied']:,} · 구조 확인 "
            f"{common['source_equal_structural_noops']:,} / 원천 합집합 "
            f"{common['source_union_effective_coordinates']:,} | {common['review_backlog']:,} |"
        ),
        (
            f"| PK 본문 `MSG_PK/JP/msggame.bin` | {pk_msggame['applied']:,} / "
            f"{pk_msggame['semantic_targets']:,} ({percent(pk_msggame['applied'], pk_msggame['semantic_targets']):.1f}%) | "
            f"{pk_msggame['remaining']:,} |"
        ),
        (
            f"| 기본 지도·튜토리얼 `MSG/JP/msggame.bin` | "
            f"{base_msggame['strict_switch_v13_transfer']:,} / {base_msggame['source_script_literals']:,} | "
            f"{base_msggame['residual']:,} |"
        ),
        (
            f"| 기본 이벤트 `MSG/JP/ev_strdata.bin` | "
            f"{base_ev['strict_switch_v13_transfer']:,} / {base_ev['switch_hangul_candidates']:,} | "
            f"{base_ev['residual']:,} |"
        ),
        (
            f"| 공용 `MSG/JP/strdata.bin` | {strdata['applied']:,} / "
            f"{strdata['safe_targets']:,} | {strdata['withheld']:,} |"
        ),
        f"| 일본어 경로 한글 폰트 | {fonts['verified']} / {fonts['containers']} | 0 |",
        "",
        (
            "v0.9.0 정식 배포본은 기존 PK 12파일에 기본판 대사 파일 2개를 더한 정확히 14파일입니다. "
            "이번 버전은 지도·튜토리얼 잔여 대사 270건과 기본 이벤트 잔여 대사 40건을 추가로 반영합니다."
        ),
        (
            f"후보 ZIP SHA-256: `{qa['candidate_zip_sha256']}`. Steam 실적용과 "
            f"{qa['steam_apply_backup_entries']}개 복원 백업, 실제 한글 화면 검증을 모두 완료했습니다."
        ),
        (
            "표의 수치는 원문 해시·줄바꿈·제어문자 계약을 통과한 안전 이식 수입니다. "
            "전체 번역 완료율을 뜻하지 않습니다."
        ),
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
