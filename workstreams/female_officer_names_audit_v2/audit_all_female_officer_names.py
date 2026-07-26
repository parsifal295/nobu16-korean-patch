#!/usr/bin/env python3
"""Read-only final static audit for every built-in female officer name.

The audit has two deliberately separate results:

* ``component_static`` compares every source-compatible two-component name
  candidate with the Korean direct ``msgev`` display after applying the
  complete 29-component candidate in memory.  It is not a claim about the
  runtime record pair.
* ``convention_review`` identifies the small set where the direct Korean
  display uses a different Japanese rendering style (``츠`` versus ``쓰``)
  from the project's strict rendering baseline.  These are review items,
  not automatic replacements: historical Korean usage can legitimately
  retain an established variant.

Neither the game root nor the supplied static officer table is changed.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any, Sequence


HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parents[1]


def load_component_audit() -> Any:
    module_path = HERE / "audit_female_officer_component_combinations.py"
    spec = importlib.util.spec_from_file_location("female_component_audit", module_path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load component audit module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


COMPONENT_AUDIT = load_component_audit()

def load_v3_builder() -> Any:
    module_path = HERE / "build_msgdata_female_officer_components_v3_complete.py"
    spec = importlib.util.spec_from_file_location("female_component_build_v3", module_path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load final component builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V3 = load_v3_builder()

SCHEMA = "nobu16.kr.all-female-officer-name-audit.v2-complete"
SAFE_COMPONENT_IDS: tuple[int, ...] = tuple(entry["id"] for entry in V3.all_patches())
BLOCKED_COMPONENT_IDS: tuple[int, ...] = ()
HISTORICAL_OFFICER_MAX_ID = 2206
HISTORY_RECORD_COUNT = 2400
HISTORY_HEADER_SIZE = 0x14
HISTORY_RECORD_STRIDE = 0x386
HISTORY_ID_OFFSET = 0x14
FEMALE_CLASS_OFFSET = 0x4C
FEMALE_CLASS_VALUES = frozenset((0x09, 0x0A, 0x0B))

# This list is the reviewed result of the static selector below.  Keeping it
# explicit prevents a future file-layout change from silently widening the
# roster.  It includes the project hime roster and all additional built-in
# historical women discovered through the same static table.
EXPECTED_FEMALE_OFFICER_IDS: tuple[int, ...] = (
    164, 172, 178, 231, 403, 404, 405, 406, 407, 410, 486, 567, 636, 692,
    715, 719, 745, 789, 843, 925, 1016, 1088, 1094, 1120, 1121, 1157, 1170,
    1171, 1176, 1179, 1265, 1310, 1348, 1390, 1391, 1416, 1517, 1571, 1581,
    1582, 1583, 1674, 1724, 1729, 1809, 1827, 1861, 1969, 1970, 2005, 2007,
    2029, 2088, 2106, 2147, 2151, 2177,
)

# Japanese 외래어 표기법의 일관성만 보는 보수적 검토 목록이다. 이 값은 "통용
# 표기가 틀렸다"는 판정이 아니다. 특히 마츠/마쓰처럼 관용 표기가 공존하는 경우,
# 사용자 정책을 정하기 전에는 현재 표시를 바꾸지 않는다.
CONVENTION_STYLE_REVIEWS: dict[int, dict[str, str]] = {
    486: {
        "strict_rendering": "오호리 쓰루",
        "reason": "つ의 엄격 전사는 쓰이나 현재 직접 표기는 츠를 쓴다.",
        "status": "STYLE_VARIANT_REVIEW",
    },
    567: {
        "strict_rendering": "오쓰야노가타",
        "reason": "つ·か의 엄격 전사와 현재 관용형 오츠야노카타가 다르다.",
        "status": "STYLE_VARIANT_REVIEW",
    },
    1827: {
        "strict_rendering": "마쓰",
        "reason": "마츠/마쓰가 공존한다. 마쓰히메와의 내부 일관성도 함께 판단해야 한다.",
        "status": "COMMON_VARIANT_POLICY_REQUIRED",
    },
    2005: {
        "strict_rendering": "무라마쓰도노",
        "reason": "마쓰히메의 마쓰와 달리 현재 직접 표기는 마츠를 쓴다.",
        "status": "STYLE_VARIANT_REVIEW",
    },
}


class AuditError(RuntimeError):
    """Raised when a static input no longer matches the pinned layout."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def read_historical_female_ids(path: Path) -> tuple[list[int], dict[str, Any]]:
    data = path.read_bytes()
    expected_size = HISTORY_HEADER_SIZE + HISTORY_RECORD_COUNT * HISTORY_RECORD_STRIDE
    if len(data) != expected_size:
        raise AuditError(f"historical table size differs: {len(data)} != {expected_size}")

    selected: list[int] = []
    for record_index in range(HISTORY_RECORD_COUNT):
        offset = HISTORY_HEADER_SIZE + record_index * HISTORY_RECORD_STRIDE
        record_id = int.from_bytes(
            data[offset + HISTORY_ID_OFFSET : offset + HISTORY_ID_OFFSET + 2], "little"
        )
        if record_id != record_index:
            raise AuditError(f"historical table id mismatch at record {record_index}")
        if record_index <= HISTORICAL_OFFICER_MAX_ID and data[offset + FEMALE_CLASS_OFFSET] in FEMALE_CLASS_VALUES:
            selected.append(record_index)

    if tuple(selected) != EXPECTED_FEMALE_OFFICER_IDS:
        raise AuditError("female roster selector differs from the reviewed 57-officer roster")
    return selected, {
        "path": str(path),
        "sha256": sha256_bytes(data),
        "size": len(data),
        "header_size": HISTORY_HEADER_SIZE,
        "record_stride": HISTORY_RECORD_STRIDE,
        "record_count": HISTORY_RECORD_COUNT,
        "id_offset": HISTORY_ID_OFFSET,
        "selector_offset": FEMALE_CLASS_OFFSET,
        "selector_values": sorted(FEMALE_CLASS_VALUES),
    }


def ensure_output_is_safe(
    output: Path, game_root: Path, source_root: Path, historical_table: Path
) -> None:
    for protected in (game_root.resolve(), source_root.resolve(), historical_table.resolve()):
        try:
            output.resolve().relative_to(protected)
        except ValueError:
            continue
        raise AuditError("report output must not be written under an input game/data root")


def atomic_json_write(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def build_report(game_root: Path, source_root: Path, historical_table: Path) -> dict[str, Any]:
    female_ids, historical_info = read_historical_female_ids(historical_table)
    entries = V3.all_patches()

    tables: dict[str, tuple[str, ...]] = {}
    table_reports: dict[str, dict[str, Any]] = {}
    for resource_name, root, relative in (
        ("SC_msgev", source_root, COMPONENT_AUDIT.MSGEV_RELATIVE),
        ("JP_msgev", game_root, COMPONENT_AUDIT.MSGEV_RELATIVE),
        ("SC_msgdata", source_root, COMPONENT_AUDIT.MSGDATA_RELATIVE),
        ("JP_msgdata", game_root, COMPONENT_AUDIT.MSGDATA_RELATIVE),
    ):
        language = resource_name[:2]
        texts, metadata = COMPONENT_AUDIT.read_table(
            root / Path(str(relative).format(language=language))
        )
        expected_count = (
            COMPONENT_AUDIT.EXPECTED_MSGEV_COUNT
            if resource_name.endswith("msgev")
            else COMPONENT_AUDIT.EXPECTED_MSGDATA_COUNT
        )
        if len(texts) != expected_count:
            raise AuditError(f"{resource_name} string count differs")
        tables[resource_name] = texts
        table_reports[resource_name] = metadata

    safe_entries = list(entries)
    if tuple(entry["id"] for entry in safe_entries) != SAFE_COMPONENT_IDS:
        raise AuditError("final component set differs from the reviewed scope")
    component_texts = COMPONENT_AUDIT.apply_overlay_in_memory(tables["JP_msgdata"], safe_entries)
    source_component_index = COMPONENT_AUDIT.component_index(tables["SC_msgdata"])
    rows: list[dict[str, Any]] = []

    for officer_id in female_ids:
        source_pairs = COMPONENT_AUDIT.exact_pairs(
            tables["SC_msgev"][officer_id], source_component_index
        )
        pair_results: list[dict[str, Any]] = []
        for left, right in source_pairs:
            candidate = component_texts[left] + component_texts[right]
            pair_results.append(
                {
                    "component_ids": [left, right],
                    "candidate_ko": candidate,
                    "comparison_with_direct_msgev": COMPONENT_AUDIT.compare(
                        candidate, tables["JP_msgev"][officer_id]
                    ),
                }
            )

        row: dict[str, Any] = {
            "msgev_id": officer_id,
            "direct_ko": tables["JP_msgev"][officer_id],
            "source_name_utf16le_sha256": COMPONENT_AUDIT.text_hash(
                tables["SC_msgev"][officer_id]
            ),
            "exact_source_pair_count": len(pair_results),
            "component_static": {
                "classification": COMPONENT_AUDIT.classify_pair_results(
                    [
                        {
                            "candidate_ko": item["candidate_ko"],
                            "comparison": item["comparison_with_direct_msgev"],
                        }
                        for item in pair_results
                    ]
                ),
                "pairs": pair_results,
                "runtime_record_pair_proven": False,
            },
        }
        style_review = CONVENTION_STYLE_REVIEWS.get(officer_id)
        if style_review is None:
            row["convention_review"] = {"status": "NO_STYLE_VARIANT_FLAG"}
        else:
            row["convention_review"] = {
                **style_review,
                "current_direct_ko": tables["JP_msgev"][officer_id],
                "automatic_change_authorized": False,
            }
        known_link = COMPONENT_AUDIT.KNOWN_NONDECOMPOSITION_LINKS.get(officer_id)
        if known_link is not None:
            left, right = known_link
            candidate = component_texts[left] + component_texts[right]
            row["known_non_decomposition_link"] = {
                "component_ids": [left, right],
                "candidate_ko": candidate,
                "comparison_with_direct_msgev": COMPONENT_AUDIT.compare(candidate, tables["JP_msgev"][officer_id]),
                "evidence": "observed Oichi defect reconstruction; competing historical 市-token names use alternate exact pairs without 2083",
            }
            if row["known_non_decomposition_link"]["comparison_with_direct_msgev"] == "EXACT":
                row["component_static"]["classification"] = "KNOWN_NONDECOMPOSITION_LINK_FIXED"
        rows.append(row)

    component_counts = Counter(row["component_static"]["classification"] for row in rows)
    convention_counts = Counter(row["convention_review"]["status"] for row in rows)
    return {
        "schema": SCHEMA,
        "scope": {
            "classification": "all_built_in_historical_female_officers",
            "female_officer_count": len(rows),
            "historical_officer_id_range": [0, HISTORICAL_OFFICER_MAX_ID],
            "analysis_is_static_only": True,
        },
        "safety": {
            "game_files_modified": False,
            "source_language_files_modified": False,
            "historical_data_modified": False,
            "runtime_record_mapping_proven": False,
        },
        "static_roster_evidence": historical_info,
        "input_tables": table_reports,
        "final_in_memory_component_overlay": {
            "entry_ids": [entry["id"] for entry in safe_entries],
            "blocked_component_ids": list(BLOCKED_COMPONENT_IDS),
            "applied_in_memory_only": True,
        },
        "convention_policy": {
            "strict_baseline": "Korean Japanese rendering consistency, including つ→쓰",
            "policy_note": "Established Korean historical variants are not automatically replaced.",
            "authority_note": "A style review is not a claim that every alternate historical spelling is incorrect.",
        },
        "rows": rows,
        "summary": {
            "component_static_classification_counts": dict(sorted(component_counts.items())),
            "convention_review_counts": dict(sorted(convention_counts.items())),
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--historical-table", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        game_root = args.game_root.resolve()
        source_root = args.source_root.resolve()
        historical_table = args.historical_table.resolve()
        report = args.report.resolve()
        ensure_output_is_safe(report, game_root, source_root, historical_table)
        document = build_report(game_root, source_root, historical_table)
        atomic_json_write(report, document)
    except (OSError, ValueError, AuditError) as exc:
        print(f"error: {exc}")
        return 2
    print(f"report={report}")
    print(f"female_officers={document['scope']['female_officer_count']}")
    print("component_static=" + json.dumps(document["summary"]["component_static_classification_counts"], ensure_ascii=False))
    print("convention_review=" + json.dumps(document["summary"]["convention_review_counts"], ensure_ascii=False))
    print("result=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
