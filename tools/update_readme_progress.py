#!/usr/bin/env python3
"""Regenerate the README's file-by-file Korean translation progress table."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
PROGRESS = ROOT / "data" / "public" / "translation_progress.v0.1.json"
START = "<!-- translation-progress:start -->"
END = "<!-- translation-progress:end -->"


def load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root is not an object: {path}")
    return payload


def overlay_entry_key(entry: dict, path: Path) -> tuple[object, ...]:
    entry_id = entry.get("id")
    if isinstance(entry_id, int):
        return ("id", entry_id)
    coordinate_fields = ("block_id", "record_id", "literal_id")
    coordinate = tuple(entry.get(field) for field in coordinate_fields)
    if all(isinstance(value, int) for value in coordinate):
        return ("msggame", *coordinate)
    raise ValueError(f"overlay entry has no integer id or msggame coordinate: {path}")


def overlay_stats(
    patterns: list[str], completed_statuses: set[str]
) -> tuple[set[tuple[object, ...]], set[tuple[object, ...]]]:
    ids: set[tuple[object, ...]] = set()
    completed: set[tuple[object, ...]] = set()
    matched: set[Path] = set()
    for pattern in patterns:
        paths = sorted(ROOT.glob(pattern))
        if not paths:
            raise ValueError(f"overlay glob matched no files: {pattern}")
        for path in paths:
            if path in matched:
                continue
            matched.add(path)
            payload = load_json(path)
            entries = payload.get("entries")
            if not isinstance(entries, list):
                raise ValueError(f"overlay has no entries list: {path}")
            defaults = payload.get("defaults")
            translation_policy = payload.get("translation_policy")
            default_status = None
            if isinstance(defaults, dict):
                default_status = defaults.get("status")
            if default_status is None and isinstance(translation_policy, dict):
                default_status = translation_policy.get("status")
            for entry in entries:
                if not isinstance(entry, dict):
                    raise ValueError(f"overlay entry is not an object: {path}")
                entry_id = overlay_entry_key(entry, path)
                ids.add(entry_id)
                status = entry.get("status", default_status)
                if status in completed_statuses:
                    completed.add(entry_id)
    return ids, completed


def percent(done: int, total: int) -> float:
    return 0.0 if total == 0 else done * 100.0 / total


def progress_bar(value: float) -> str:
    filled = max(0, min(10, round(value / 10.0)))
    return "█" * filled + "░" * (10 - filled)


def render() -> str:
    config = load_json(PROGRESS)
    resources = config.get("resources")
    if not isinstance(resources, list):
        raise ValueError("progress config has no resources list")
    completed_statuses = set(config.get("completed_statuses", []))
    if not completed_statuses:
        raise ValueError("progress config has no completed_statuses")

    rows: list[str] = []
    pk_done = 0
    pk_coverage = 0
    pk_total = 0
    pk_string_resources = 0
    pk_stage_done = 0
    pk_stage_total = 0
    pk_stage_resources = 0
    for resource in resources:
        path = resource["path"]
        kind = resource["kind"]
        note = resource["note"]
        if kind == "strings":
            if not path.startswith("MSG_PK/"):
                raise ValueError(f"runtime progress must not include non-PK resource: {path}")
            total = int(resource["translation_target_total"])
            total_slots = int(resource["total_slots"])
            patterns = resource.get("overlay_globs", [])
            if patterns:
                coverage_ids, completed_ids = overlay_stats(patterns, completed_statuses)
            else:
                coverage_ids, completed_ids = set(), set()
            coverage = len(coverage_ids)
            done = len(completed_ids)
            if coverage > total:
                raise ValueError(f"draft ids exceed translation target count for {path}")
            if done > coverage:
                raise ValueError(f"completed ids exceed draft coverage for {path}")
            value = percent(done, total)
            amount = f"{done:,} / {total:,}"
            coverage_amount = f"{coverage:,}"
            inventory = f"{total_slots:,} 슬롯"
            rate = f"{value:.1f}% `{progress_bar(value)}`"
            pk_done += done
            pk_coverage += coverage
            pk_total += total
            pk_string_resources += 1
            if path.endswith("msgev.bin"):
                note = f"장수명 2,207 + 대사 {coverage - 2207:,}"
            elif path.endswith("msgdata.bin"):
                note = f"장수 구성요소 + 성 이름 + 옛 지방명; 검수 대기 {coverage - done:,}"
        elif kind == "records":
            amount = "0 / 조사 중"
            coverage_amount = "—"
            inventory = f"{int(resource['record_total']):,} 레코드"
            rate = "—"
        elif kind == "stages":
            done = int(resource["done"])
            total = int(resource["total"])
            unit = resource["unit"]
            value = percent(done, total)
            amount = f"{done:,} / {total:,} {unit}"
            coverage_amount = "—"
            inventory = "—"
            rate = f"{value:.1f}% `{progress_bar(value)}`"
            if path.startswith("RES_SC/"):
                pk_stage_done += done
                pk_stage_total += total
                pk_stage_resources += 1
        else:
            raise ValueError(f"unknown progress kind {kind!r} for {path}")
        rows.append(
            f"| `{path}` | {amount} | {coverage_amount} | {inventory} | {rate} | {note} |"
        )

    pk_overall = percent(pk_done, pk_total)
    lines = [
        START,
        (
            f"PK 실행 경로 `MSG_PK/SC`의 {pk_string_resources}개 메시지 리소스 기준 "
            f"**번역 완료 {pk_done:,} / {pk_total:,} ({pk_overall:.1f}%)**, "
            f"초벌 커버리지는 **{pk_coverage:,}개**다."
        ),
        (
            f"PK 공용 글꼴·리소스 경로 `RES_SC`의 {pk_stage_resources}개 검증 단계는 "
            f"**{pk_stage_done} / {pk_stage_total}** 완료다."
        ),
        "",
        "## 현재 한글화 진행 현황",
        "",
        f"PK 실행 기준 {pk_string_resources}개 메시지 리소스 **번역 완료 "
        f"{pk_done:,} / {pk_total:,} ({pk_overall:.1f}%)**, 초벌 커버리지는 "
        f"**{pk_coverage:,}개**다.",
        "PK `msggame.bin`은 18블록 바이트코드에서 확인한 표시 가능한 SC 리터럴 후보를 분모에 포함했다.",
        "후속 사람 분류에서 코드용 문자열이 확인되면 대상 분모를 보수적으로 조정한다.",
        "번역 대상은 표시 가능한 비공백 문자열과 의도적으로 활성화한 UI 빈 슬롯만 센다.",
        "완료는 공개 오버레이의 `translated`·`reviewed` 고유 ID·`msggame` 좌표 합집합이다. 최종 화면 QA 완료를 뜻하지 않는다.",
        "",
        "| 한글화 대상 파일 | 번역 완료 / 대상 | 초벌 커버리지 | 전체 슬롯·레코드 | 진행률 | 현재 상태 |",
        "|---|---:|---:|---:|---|---|",
        *rows,
        "",
        "이 표는 `tools/update_readme_progress.py`가 공개 오버레이를 다시 집계해 만든다. 모든",
        "커밋은 표를 갱신한 뒤 `--check`를 통과해야 한다.",
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
            print("README translation progress is stale; run tools/update_readme_progress.py")
            return 1
        print("README translation progress is current")
        return 0
    if current != expected:
        README.write_text(expected, encoding="utf-8", newline="\n")
        print("updated README translation progress")
    else:
        print("README translation progress already current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
