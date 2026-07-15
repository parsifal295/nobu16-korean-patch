#!/usr/bin/env python3
"""Regenerate the README's file-by-file Korean translation progress table."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
PROGRESS = ROOT / "data" / "public" / "translation_progress.v0.1.json"
TARGET_CATALOG = ROOT / "data" / "public" / "translation_target_keys.v0.1.json"
START = "<!-- translation-progress:start -->"
END = "<!-- translation-progress:end -->"
SHARED_STRDATA_PATH = "MSG/SC/strdata.bin"


def load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root is not an object: {path}")
    return payload


def overlay_entry_key(entry: dict, path: Path) -> tuple[object, ...]:
    entry_id = entry.get("id")
    if isinstance(entry_id, int):
        return ("id", entry_id)
    block_slot = (entry.get("block_id"), entry.get("slot_id"))
    if all(isinstance(value, int) and not isinstance(value, bool) for value in block_slot):
        return ("block_slot", *block_slot)
    coordinate_fields = ("block_id", "record_id", "literal_id")
    coordinate = tuple(entry.get(field) for field in coordinate_fields)
    if all(isinstance(value, int) and not isinstance(value, bool) for value in coordinate):
        return ("msggame", *coordinate)
    raise ValueError(
        f"overlay entry has no integer id, block/slot, or msggame coordinate: {path}"
    )


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


def canonical_hash(value: object) -> str:
    encoded = json.dumps(
        value, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def load_target_keys() -> dict[str, set[tuple[object, ...]]]:
    catalog = load_json(TARGET_CATALOG)
    if catalog.get("schema") != "nobu16.kr.translation-target-keys.v0.1":
        raise ValueError("unsupported translation target-key catalog schema")
    if catalog.get("source_free") is not True or catalog.get("contains_source_text") is not False:
        raise ValueError("translation target-key catalog is not source-free")
    resources = catalog.get("resources")
    if not isinstance(resources, list):
        raise ValueError("translation target-key catalog has no resources list")

    by_path: dict[str, set[tuple[object, ...]]] = {}
    aggregate: dict[str, object] = {}
    for resource in resources:
        if not isinstance(resource, dict):
            raise ValueError("translation target-key resource is not an object")
        path = resource.get("path")
        key_kind = resource.get("key_kind")
        if not isinstance(path, str) or path in by_path:
            raise ValueError(f"invalid or duplicate translation target path: {path!r}")
        if not (path.startswith("MSG_PK/SC/") or path == SHARED_STRDATA_PATH):
            raise ValueError(f"target catalog contains an unsupported runtime path: {path}")
        if path == SHARED_STRDATA_PATH and key_kind != "block_slot_coordinate":
            raise ValueError("shared strdata target keys must use block_slot_coordinate")
        if key_kind == "id":
            raw_keys = resource.get("target_ids")
            if not isinstance(raw_keys, list) or not all(
                isinstance(value, int) and not isinstance(value, bool) for value in raw_keys
            ):
                raise ValueError(f"target_ids are invalid for {path}")
            if raw_keys != sorted(set(raw_keys)):
                raise ValueError(f"target_ids are not sorted and unique for {path}")
            keys = {("id", value) for value in raw_keys}
        elif key_kind == "msggame_coordinate":
            raw_keys = resource.get("target_coordinates")
            if not isinstance(raw_keys, list):
                raise ValueError(f"target_coordinates are invalid for {path}")
            coordinates: list[tuple[int, int, int]] = []
            for value in raw_keys:
                if not (
                    isinstance(value, list)
                    and len(value) == 3
                    and all(isinstance(part, int) and not isinstance(part, bool) for part in value)
                ):
                    raise ValueError(f"invalid msggame coordinate for {path}: {value!r}")
                coordinates.append(tuple(value))
            if coordinates != sorted(set(coordinates)):
                raise ValueError(f"target_coordinates are not sorted and unique for {path}")
            keys = {("msggame", *value) for value in coordinates}
        elif key_kind == "block_slot_coordinate":
            if path != SHARED_STRDATA_PATH:
                raise ValueError(
                    f"block_slot_coordinate is only supported for {SHARED_STRDATA_PATH}"
                )
            raw_keys = resource.get("target_coordinates")
            if not isinstance(raw_keys, list):
                raise ValueError(f"target_coordinates are invalid for {path}")
            block_slots: list[tuple[int, int]] = []
            for value in raw_keys:
                if not (
                    isinstance(value, list)
                    and len(value) == 2
                    and all(isinstance(part, int) and not isinstance(part, bool) for part in value)
                ):
                    raise ValueError(f"invalid block/slot coordinate for {path}: {value!r}")
                block_slots.append(tuple(value))
            if block_slots != sorted(set(block_slots)):
                raise ValueError(f"target_coordinates are not sorted and unique for {path}")
            keys = {("block_slot", *value) for value in block_slots}
        else:
            raise ValueError(f"unknown target key kind {key_kind!r} for {path}")

        if int(resource.get("target_count", -1)) != len(keys):
            raise ValueError(f"target_count mismatch for {path}")
        if resource.get("target_keys_sha256") != canonical_hash(raw_keys):
            raise ValueError(f"target_keys_sha256 mismatch for {path}")
        by_path[path] = keys
        aggregate[path] = raw_keys

    if int(catalog.get("resource_count", -1)) != len(by_path):
        raise ValueError("target catalog resource_count mismatch")
    if int(catalog.get("target_total", -1)) != sum(len(keys) for keys in by_path.values()):
        raise ValueError("target catalog target_total mismatch")
    if catalog.get("all_target_keys_sha256") != canonical_hash(aggregate):
        raise ValueError("target catalog aggregate key hash mismatch")
    return by_path


@dataclass(frozen=True)
class TargetedOverlayStats:
    overlay_coverage: int
    overlay_completed: int
    target_coverage: int
    target_completed: int
    non_target_coverage: int
    non_target_completed: int


def targeted_overlay_stats(
    patterns: list[str],
    completed_statuses: set[str],
    target_keys: set[tuple[object, ...]],
) -> TargetedOverlayStats:
    if patterns:
        coverage_keys, completed_keys = overlay_stats(patterns, completed_statuses)
    else:
        coverage_keys, completed_keys = set(), set()
    if not completed_keys.issubset(coverage_keys):
        raise ValueError("completed overlay keys are not covered by the overlay union")
    return TargetedOverlayStats(
        overlay_coverage=len(coverage_keys),
        overlay_completed=len(completed_keys),
        target_coverage=len(coverage_keys & target_keys),
        target_completed=len(completed_keys & target_keys),
        non_target_coverage=len(coverage_keys - target_keys),
        non_target_completed=len(completed_keys - target_keys),
    )


def percent(done: int, total: int) -> float:
    return 0.0 if total == 0 else done * 100.0 / total


def progress_bar(value: float) -> str:
    filled = max(0, min(10, round(value / 10.0)))
    return "█" * filled + "░" * (10 - filled)


def render_string_row(
    resource: dict,
    *,
    completed_statuses: set[str],
    target_keys_by_path: dict[str, set[tuple[object, ...]]],
    string_paths: set[str],
) -> tuple[str, int, int, TargetedOverlayStats]:
    path = resource["path"]
    note = resource["note"]
    total = int(resource["translation_target_total"])
    total_slots = int(resource["total_slots"])
    if path not in target_keys_by_path:
        raise ValueError(f"target catalog has no keys for {path}")
    if path in string_paths:
        raise ValueError(f"duplicate string progress resource: {path}")
    string_paths.add(path)
    target_keys = target_keys_by_path[path]
    if len(target_keys) != total:
        raise ValueError(
            f"translation_target_total={total}, target catalog={len(target_keys)} for {path}"
        )
    patterns = resource.get("overlay_globs", [])
    stats = targeted_overlay_stats(patterns, completed_statuses, target_keys)
    coverage = stats.target_coverage
    done = stats.target_completed
    if coverage > total:
        raise ValueError(f"draft ids exceed translation target count for {path}")
    if done > coverage:
        raise ValueError(f"completed ids exceed draft coverage for {path}")
    value = percent(done, total)
    coverage_amount = f"{coverage:,}"
    if stats.non_target_coverage:
        coverage_amount += f" (+{stats.non_target_coverage:,} 비대상 활성)"
    row = (
        f"| `{path}` | {done:,} / {total:,} | {coverage_amount} | "
        f"{total_slots:,} 슬롯 | {value:.1f}% `{progress_bar(value)}` | {note} |"
    )
    return row, done, total, stats


def render() -> str:
    config = load_json(PROGRESS)
    target_keys_by_path = load_target_keys()
    resources = config.get("resources")
    if not isinstance(resources, list):
        raise ValueError("progress config has no resources list")
    shared_resources = config.get("shared_strings")
    if not isinstance(shared_resources, list) or len(shared_resources) != 1:
        raise ValueError("progress config must have exactly one shared_strings resource")
    completed_statuses = set(config.get("completed_statuses", []))
    if not completed_statuses:
        raise ValueError("progress config has no completed_statuses")

    rows: list[str] = []
    stage_rows: list[str] = []
    pk_done = 0
    pk_coverage = 0
    pk_non_target_coverage = 0
    pk_non_target_completed = 0
    pk_total = 0
    pk_string_resources = 0
    pk_stage_done = 0
    pk_stage_total = 0
    pk_stage_resources = 0
    shared_done = 0
    shared_coverage = 0
    shared_non_target_coverage = 0
    shared_non_target_completed = 0
    shared_total = 0
    shared_string_resources = 0
    string_paths: set[str] = set()
    for resource in resources:
        if not isinstance(resource, dict):
            raise ValueError("progress resource is not an object")
        path = resource["path"]
        kind = resource["kind"]
        note = resource["note"]
        if kind == "strings":
            if not path.startswith("MSG_PK/SC/"):
                raise ValueError(f"runtime progress must not include non-PK resource: {path}")
            row, done, total, stats = render_string_row(
                resource,
                completed_statuses=completed_statuses,
                target_keys_by_path=target_keys_by_path,
                string_paths=string_paths,
            )
            rows.append(row)
            pk_done += done
            pk_coverage += stats.target_coverage
            pk_non_target_coverage += stats.non_target_coverage
            pk_non_target_completed += stats.non_target_completed
            pk_total += total
            pk_string_resources += 1
        elif kind == "records":
            amount = "0 / 조사 중"
            coverage_amount = "—"
            inventory = f"{int(resource['record_total']):,} 레코드"
            rate = "—"
            rows.append(
                f"| `{path}` | {amount} | {coverage_amount} | {inventory} | {rate} | {note} |"
            )
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
            stage_rows.append(
                f"| `{path}` | {amount} | {coverage_amount} | {inventory} | {rate} | {note} |"
            )
        else:
            raise ValueError(f"unknown progress kind {kind!r} for {path}")

    for resource in shared_resources:
        if not isinstance(resource, dict) or resource.get("kind") != "strings":
            raise ValueError("shared_strings resource must be a strings object")
        if resource.get("path") != SHARED_STRDATA_PATH:
            raise ValueError(
                f"unsupported shared runtime string resource: {resource.get('path')!r}"
            )
        row, done, total, stats = render_string_row(
            resource,
            completed_statuses=completed_statuses,
            target_keys_by_path=target_keys_by_path,
            string_paths=string_paths,
        )
        rows.append(row)
        shared_done += done
        shared_coverage += stats.target_coverage
        shared_non_target_coverage += stats.non_target_coverage
        shared_non_target_completed += stats.non_target_completed
        shared_total += total
        shared_string_resources += 1

    rows.extend(stage_rows)

    if string_paths != set(target_keys_by_path):
        missing = sorted(set(target_keys_by_path) - string_paths)
        extra = sorted(string_paths - set(target_keys_by_path))
        raise ValueError(f"progress/target catalog resource mismatch: missing={missing}, extra={extra}")

    pk_overall = percent(pk_done, pk_total)
    shared_overall = percent(shared_done, shared_total)
    lines = [
        START,
        (
            f"PK 실행 경로 `MSG_PK/SC`의 {pk_string_resources}개 메시지 리소스 기준 "
            f"**번역 완료 {pk_done:,} / {pk_total:,} ({pk_overall:.1f}%)**, "
            f"대상 초벌 커버리지는 **{pk_coverage:,}개**다. 대상 밖에서 활성화된 "
            f"커버리지는 **{pk_non_target_coverage:,}개**로 별도 집계한다."
        ),
        (
            f"PK 실행에서 함께 로드되는 공용 경로 `{SHARED_STRDATA_PATH}`의 "
            f"{shared_string_resources}개 문자열 리소스는 **번역 완료 "
            f"{shared_done:,} / {shared_total:,} ({shared_overall:.1f}%)**, "
            f"대상 초벌 커버리지는 **{shared_coverage:,}개**다."
        ),
        (
            f"PK 공용 글꼴·리소스 경로 `RES_SC`의 {pk_stage_resources}개 검증 단계는 "
            f"**{pk_stage_done} / {pk_stage_total}** 완료다."
        ),
        "",
        "## 현재 한글화 진행 현황",
        "",
        f"PK 실행 기준 {pk_string_resources}개 메시지 리소스 **번역 완료 "
        f"{pk_done:,} / {pk_total:,} ({pk_overall:.1f}%)**, 대상 초벌 커버리지는 "
        f"**{pk_coverage:,}개**다. 비대상 활성 커버리지는 **{pk_non_target_coverage:,}개**"
        f"(그중 완료 상태 {pk_non_target_completed:,}개)로 분리했다.",
        (
            f"PK가 실제로 함께 읽는 공용 본편 표 `{SHARED_STRDATA_PATH}`는 "
            f"**{shared_done:,} / {shared_total:,} ({shared_overall:.1f}%)** 완료, "
            f"대상 초벌 커버리지 **{shared_coverage:,}개**, 비대상 활성 "
            f"**{shared_non_target_coverage:,}개**(그중 완료 상태 "
            f"{shared_non_target_completed:,}개)로 별도 집계한다."
        ),
        "PK `msggame.bin`은 18블록 바이트코드에서 확인한 표시 가능한 SC 리터럴 후보를 분모에 포함했다.",
        "후속 사람 분류에서 코드용 문자열이 확인되면 대상 분모를 보수적으로 조정한다.",
        "번역 대상은 표시 가능한 비공백 문자열과 의도적으로 활성화한 UI 빈 슬롯만 센다.",
        "완료·초벌 커버리지는 source-free target-key 카탈로그와 공개 오버레이 고유 ID·`msggame` 좌표·공용 표 블록/슬롯 좌표 합집합의 교집합만 센다.",
        "target-key 밖에서 새로 활성화한 ID는 번역 대상 완료율에 넣지 않고 비대상 활성 커버리지로 별도 표시한다. 최종 화면 QA 완료를 뜻하지 않는다.",
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
