#!/usr/bin/env python3
"""Build source-free PK/SC msggame Korean translation batch 13."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
WORKSPACE_ROOT = REPO_ROOT.parent
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_translation_batch1 as previous  # noqa: E402


BATCH_ID = "msggame_pk_system_messages_b06r1839_1991.v0.13"
OVERLAY_NAME = "msggame_ko_system_messages_b06r1839_1991.v0.13.json"
EVIDENCE_NAME = "translation_alignment_evidence.v0.13.json"
REVIEW_NAME = "translation_review_index.v0.13.json"
VALIDATION_NAME = "translation_validation.v0.13.json"
RESOURCE = previous.RESOURCE
LANGUAGES = previous.LANGUAGES
SOURCE_PATHS = previous.SOURCE_PATHS
NEXT_COORDINATE = (6, 1993, 0)


TRANSLATIONS: dict[tuple[int, int], tuple[str | None, ...]] = {
    (6, 1839): ("본가가 막부를 세웠습니다.",),
    (6, 1840): ("막부 세력에만 직위를 요청할 수 있습니다.",),
    (6, 1841): ("본가가 막부 이외의 세력에 신종하고 있습니다.",),
    (6, 1842): ("상대가 본가와의 교섭을 거부하고 있습니다.",),
    (6, 1843): ("본가가 취임할 수 있는 직위가 없습니다.",),
    (6, 1844): ("신용이 부족합니다.",),
    (6, 1845): ("교전 중이거나 교전 직후라 거부하고 있습니다.",),
    (6, 1846): ("충분히 방어할 수 있는 상황이 아닙니다.",),
    (6, 1847): ("관직이 없어 조정에 연줄이 없습니다.",),
    (6, 1848): ("취임할 수 있는 관직이 없습니다.",),
    (6, 1849): ("중개자가 될 수 있는 무장이 없습니다.",),
    (6, 1850): ("취임할 수 있는 관직에 공석이 생기면 임관할 예정입니다.",),
    (6, 1851): ("헌상할 금전이 부족합니다.",),
    (6, 1852): ("아시카가 가문만 실행할 수 있습니다.",),
    (6, 1853): ("다른 세력에 줄 수 있는 관직이 없습니다.",),
    (6, 1854): ("직위를 줄 수 있는 세력이 없습니다.",),
    (6, 1855): ("외교할 수 있는 세력이 없습니다.",),
    (6, 1856): ("다른 세력과 외교합니다.",),
    (6, 1857): ("이 세력과 외교합니다.",),
    (6, 1858): ("단교 상태인 세력입니다.",),
    (6, 1859): ("쇼군 가문 이외의 먼 세력과는 외교할 수 없습니다.",),
    (6, 1860): ("상대가 본가에 노골적인 적의를 드러내고 있습니다.",),
    (6, 1861): ("본가에 제안할 수 있는 교섭 재료가 없습니다.",),
    (6, 1862): ("이 세력과는 외교할 수 없습니다.",),
    (6, 1863): ("다른 가문에 종속된 세력과는 교섭할 수 없습니다.",),
    (6, 1864): ("그 세력과 외교한 지 얼마 되지 않았습니다. 재개까지", "일 남았습니다."),
    (6, 1865): ("그 세력과의 교섭을 결렬시켜 외교에 응하지 않습니다.",),
    (6, 1866): ("그 세력과의 교섭을 결렬시켜 외교에 응하지 않습니다.\n", "개월 후 외교할 수 있습니다."),
    (6, 1867): ("그 세력과의 교섭을 결렬시켜 외교에 응하지 않습니다.\n", "일 후 외교할 수 있습니다"),
    (6, 1868): ("본가와 상대의 악명 차이가 70 이상이라 아무 요청에도 응하지 않을 것입니다.",),
    (6, 1869): ("우호도가 부족해 요청할 수 없습니다.",),
    (6, 1870): ("우호도가 부족해 요청할 수 없습니다.",),
    (6, 1871): ("단교 상태인 세력에는 요청할 수 없습니다.",),
    (6, 1872): ("가치가 너무 높아 교섭이 성립될 가능성이 없습니다.",),
    (6, 1873): ("현재 요청하려는 내용과 동시에 요청할 수 없습니다.",),
    (6, 1874): ("이 교섭 재료는 이미 요청했습니다.",),
    (6, 1875): ("이 교섭 재료에는 대가가 필요하지 않습니다.",),
    (6, 1876): ("이미 대가로 제시한 교섭 재료이므로 요청할 수 없습니다.",),
    (6, 1877): ("본가의 주군 이외와는 거래할 수 없습니다.",),
    (6, 1878): ("우호도가 “친밀”에 미치지 못해 요청할 수 없습니다.",),
    (6, 1879): ("우호도가 “우호”에 미치지 못해 요청할 수 없습니다.",),
    (6, 1880): ("우호도가 “보통”에 미치지 못해 요청할 수 없습니다.",),
    (6, 1881): ("상대와의 악명 차이가 30 이상이라 요청할 수 없습니다.",),
    (6, 1882): ("상대와의 악명 차이가 40 이상이라 요청할 수 없습니다.",),
    (6, 1883): ("상대와의 악명 차이가 70 이상이라 요청할 수 없습니다.",),
    (6, 1885): ("현재 이 내용은 요청할 수 없습니다.",),
    (6, 1886): ("우호도를 더 높일 수 없습니다.",),
    (6, 1887): ("본가의 주군 이외와는 친선할 수 없습니다.",),
    (6, 1888): ("상대의 금전이 부족합니다.",),
    (6, 1889): ("금전 보유 한도를 초과합니다.",),
    (6, 1890): ("상대의 군량이 부족합니다.",),
    (6, 1891): ("상대는 군량을 내놓을 여유가 없는 듯합니다.",),
    (6, 1892): ("군량 보유 한도를 초과합니다.",),
    (6, 1893): ("상대의 군마가 부족합니다.",),
    (6, 1894): ("군마 보유 한도를 초과합니다.",),
    (6, 1895): ("상대의 철포가 부족합니다.",),
    (6, 1896): ("철포?……그게 무엇입니까?",),
    (6, 1897): ("철포 보유 한도를 초과합니다.",),
    (6, 1898): ("가보를 더 요청할 수 없습니다.",),
    (6, 1899): ("상대 다이묘가 가보를 보유하지 않았습니다.",),
    (6, 1900): ("군을 더 요청할 수 없습니다.",),
    (6, 1901): ("상대에게 요청할 수 있는 군이 없습니다.",),
    (6, 1902): ("본가 영지와 인접한 군이 없습니다.",),
    (6, 1903): ("본가가 다른 가문과 교전 중이라 군을 요청할 여유가 없습니다.",),
    (6, 1904): ("본가가 종속 상태이므로 군을 요청할 수 없습니다.",),
    (6, 1905): ("본가 영지와 인접하지 않은 군은 요청할 수 없습니다.",),
    (6, 1906): ("성은 군으로 요청할 수 없습니다.",),
    (6, 1907): ("전쟁에 휘말릴 가능성이 있어 요청할 수 없습니다.",),
    (6, 1908): ("이미 요청한 군입니다.",),
    (6, 1910): ("상대에게 요청할 수 있는 성이 없습니다.",),
    (6, 1911): ("본가 영지와 인접한 성이 없습니다.",),
    (6, 1912): ("본가가 다른 가문과 교전 중이라 성을 요청할 여유가 없습니다.",),
    (6, 1913): ("본가가 종속 상태이므로 성을 요청할 수 없습니다.",),
    (6, 1914): ("상대가 다음 대상의 양도를 거부합니다:",),
    (6, 1915): ("본가 영지와 인접하지 않은 성은 요청할 수 없습니다.",),
    (6, 1916): ("전쟁에 휘말릴 가능성이 있어 요청할 수 없습니다.",),
    (6, 1917): ("상대의 영지를 분단하게 되므로 선택할 수 없습니다.",),
    (6, 1918): ("상대는 정전에 응할 뜻이 없습니다.",),
    (6, 1919): ("아군과는 정전할 필요가 없습니다.",),
    (6, 1920): ("본가가 종속 상태이므로 정전 교섭을 할 수 없습니다.",),
    (6, 1922): ("상대가 본가에 적의를 드러내며 지배를 거부하고 있습니다.",),
    (6, 1923): ("상대는 멀리 떨어진 본가의 지배를 받을 뜻이 없습니다.",),
    (6, 1924): ("본가가 종속 상태이므로 다른 가문을 지배할 수 없습니다.",),
    (6, 1925): ("본가의 규모가 상대를 지배하기에 부족합니다.",),
    (6, 1926): ("이미 상대를 지배하고 있습니다.",),
    (6, 1927): ("본가의 규모가 너무 커 상대에게 종속될 수 없습니다.",),
    (6, 1928): ("본가가 이미 다른 가문에 종속되어 있어 종속이 아니라 주가 변경만 할 수 있습니다.",),
    (6, 1929): ("이미 상대와 종속 관계입니다.",),
    (6, 1930): ("상대는 동맹에 응할 뜻이 없습니다.",),
    (6, 1931): ("본가가 종속 상태이므로 동맹 교섭을 할 수 없습니다.",),
    (6, 1932): ("이미 상대 세력과 장기 동맹을 맺었습니다.",),
    (6, 1933): ("상대는 혼인에 응할 뜻이 없습니다.",),
    (6, 1934): ("본가가 종속 상태이므로 혼인 교섭을 할 수 없습니다.",),
    (6, 1935): ("이미 상대 세력과 혼인 관계입니다.",),
    (6, 1936): ("혼인할 수 있는 공주나 무장이 없습니다.",),
    (6, 1937): ("본가의 종속 세력과는 혼인 동맹을 맺을 수 없습니다.",),
    (6, 1938): ("상대와 단교하도록 요청할 수 있는 세력이 없습니다.",),
    (6, 1939): ("본가가 종속 상태이므로 맹약 파기를 요청할 수 없습니다.",),
    (6, 1940): ("상대가 맹약 파기 교섭을 거부하고 있습니다.",),
    (6, 1941): ("본가의 아군입니다.",),
    (6, 1942): ("혼인 동맹 중인 세력과 단교하도록 요청할 수 없습니다.",),
    (6, 1943): ("종속 세력과 단교하도록 요청할 수 없습니다.",),
    (6, 1944): ("칙명 강화는 단교시킬 수 없습니다.",),
    (6, 1945): ("상대와 원군을 주고받고 있어 단교시킬 수 없습니다.",),
    (6, 1946): ("상대 세력과 외교 관계가 없습니다.",),
    (6, 1947): ("상대가 새 목표로 삼을 수 있는 세력이 없습니다.",),
    (6, 1948): ("상대가 이미 목표 세력과 교전 중이므로 변경을 교섭할 수 없습니다.",),
    (6, 1949): ("본가가 종속 상태이므로 목표 세력 변경을 교섭할 수 없습니다.",),
    (6, 1950): ("본가와 적대하고 있지 않습니다.",),
    (6, 1951): ("상대와 인접하지 않습니다.",),
    (6, 1952): ("이미 상대의 목표입니다.",),
    (6, 1954): ("본가 이외에 종속된 세력에는 원군을 요청할 수 없습니다.",),
    (6, 1955): ("이미 상대와 원군을 주고받고 있습니다.",),
    (6, 1956): ("원군을 의뢰할 수 있는 성이 없습니다.",),
    (6, 1957): ("상대에게 원군을 보낼 여력이 없습니다.",),
    (6, 1959): ("그 성은 교섭 재료로 제시되었습니다.",),
    (6, 1960): ("상대가 교전할 수 없는 세력에는 원군을 보낼 수 없습니다.",),
    (6, 1961): ("상대는 그 성까지 원군을 보낼 수 없습니다.",),
    (6, 1963): ("상대와 끊을 수 있는 외교 관계가 없습니다.",),
    (6, 1964): ("칙명 강화는 중단할 수 없습니다.",),
    (6, 1965): ("상대의 공주를 받아들였으므로 단교할 수 없습니다.",),
    (6, 1966): ("상대에게 공주를 보냈으므로 단교할 수 없습니다.",),
    (6, 1967): ("원군 요청 기간 중이므로 단교할 수 없습니다.",),
    (6, 1968): ("본가의 주군과 동맹인 세력으로는 전향할 수 없습니다.",),
    (6, 1969): ("상대는 이미 본가가 종속된 세력입니다.",),
    (6, 1970): ("본가가 독립 상태이므로 주가를 바꿀 수 없습니다.",),
    (6, 1971): ("본가의 규모가 너무 커 상대에게 주가를 바꿀 수 없습니다.",),
    (6, 1972): ("대가가 필요 없는 교섭 재료를 요청하고 있습니다.",),
    (6, 1973): ("본가의 주군 이외와는 거래할 수 없습니다.",),
    (6, 1974): ("현재 이 내용은 선택할 수 없습니다.",),
    (6, 1975): ("선택할 수 있는 금전이 부족합니다.",),
    (6, 1976): ("상대는 금전이 부족하지 않아 받아들이지 않을 것입니다.",),
    (6, 1977): ("이미 금전을 교섭 재료로 선택했습니다.",),
    (6, 1978): ("선택할 수 있는 군량이 부족합니다.",),
    (6, 1979): ("상대는 군량이 부족하지 않아 받아들이지 않을 것입니다.",),
    (6, 1980): ("이미 군량을 교섭 재료로 선택했습니다.",),
    (6, 1981): ("선택할 수 있는 군마가 부족합니다.",),
    (6, 1982): ("상대는 군마가 부족하지 않아 받아들이지 않을 것입니다.",),
    (6, 1983): ("이미 군마를 교섭 재료로 선택했습니다.",),
    (6, 1984): ("선택할 수 있는 철포가 부족합니다.",),
    (6, 1985): ("상대는 철포가 부족하지 않아 받아들이지 않을 것입니다.",),
    (6, 1986): ("이미 철포를 교섭 재료로 선택했습니다.",),
    (6, 1987): ("철포?……그게 무엇입니까?",),
    (6, 1988): ("선택할 수 있는 가보가 없습니다.",),
    (6, 1989): ("가보는 최대 5개까지 선택할 수 있습니다.",),
    (6, 1990): ("선택할 수 있는 군이 없습니다.",),
    (6, 1991): ("군은 최대 5개까지 선택할 수 있습니다.",),
}

SKIPPED_CANDIDATES: dict[tuple[int, int, int], str] = {}
EXPECTED_RECORD_KEYS = tuple(TRANSLATIONS)


def selected_record_keys() -> list[tuple[int, int]]:
    return sorted(TRANSLATIONS)


def selected_coordinates() -> list[tuple[int, int, int]]:
    return [
        (block_id, record_id, literal_id)
        for (block_id, record_id), replacements in sorted(TRANSLATIONS.items())
        for literal_id, replacement in enumerate(replacements)
        if replacement is not None
    ]


def validate_static_scope() -> None:
    keys = selected_record_keys()
    selected = selected_coordinates()
    if keys != sorted(EXPECTED_RECORD_KEYS):
        raise ValueError("translation scan record set changed")
    if selected[0] != (6, 1839, 0) or selected[-1] != (6, 1991, 0):
        raise ValueError("translation batch boundaries changed")
    if len(selected) != 150 or len(keys) != 147:
        raise ValueError("translation batch scope changed")
    if SKIPPED_CANDIDATES:
        raise ValueError("translation batch unexpectedly contains skips")


def _uncertainty_flags(
    coordinate: tuple[int, int, int],
    record_counts: dict[str, int],
    sc_literal_count: int,
) -> list[str]:
    flags = ["runtime_line_wrap_review"]
    if len(set(record_counts.values())) != 1:
        flags.append("cross_language_literal_shape_diff")
    if sc_literal_count > 1:
        flags.append("runtime_dynamic_join_review")
    if coordinate[:2] in {(4, 83), (4, 107)}:
        flags.append("runtime_fragment_join_review")
    return flags


def _assert_public_source_free(paths: Iterable[Path]) -> dict[str, dict[str, int]]:
    scans: dict[str, dict[str, int]] = {}
    for path in paths:
        counts = previous.script_counts(path.read_text(encoding="utf-8"))
        scans[path.name] = counts
        if counts != {"cjk_unified_count": 0, "kana_count": 0}:
            raise ValueError(f"source-script text leaked into {path}")
    return scans


def build(args: argparse.Namespace) -> dict[str, Any]:
    validate_static_scope()
    paths = {
        language: Path(getattr(args, f"stock_{language.lower()}")).resolve()
        for language in LANGUAGES
    }
    installed_before = {
        language: previous.sha256(path.read_bytes()) for language, path in paths.items()
    }
    loaded = previous.load_sources(paths)
    archives = {
        language: loaded[language]["parsed"].archive for language in LANGUAGES
    }
    records = {
        language: previous._record_map(archive)
        for language, archive in archives.items()
    }
    sc_literals = previous._literal_map(archives["SC"])

    overlay_entries: list[dict[str, Any]] = []
    review_entries: list[dict[str, Any]] = []
    invariant_failures: list[dict[str, Any]] = []
    record_evidence: list[dict[str, Any]] = []
    replacement_map: dict[tuple[int, int, int], str] = {}

    for block_id, record_id in selected_record_keys():
        key = (block_id, record_id)
        source_record_literals = previous.parse_record_literals(records["SC"][key])
        replacements = TRANSLATIONS[key]
        if len(source_record_literals) != len(replacements):
            raise ValueError(
                f"translation literal count mismatch at {key}: "
                f"source={len(source_record_literals)}, ko={len(replacements)}"
            )
        if not all(
            previous.is_visible_translation_candidate(literal.text)
            for literal in source_record_literals
        ):
            raise ValueError(f"scanned record contains a non-visible literal: {key}")
        language_references = {
            language: previous.record_reference(records[language][key])
            for language in LANGUAGES
        }
        literal_counts = {
            language: language_references[language]["literal_count"]
            for language in LANGUAGES
        }
        record_evidence.append(
            {
                "block_id": block_id,
                "record_id": record_id,
                "selected_sc_literal_ids": [
                    literal_id
                    for literal_id, replacement in enumerate(replacements)
                    if replacement is not None
                ],
                "skipped_sc_literal_ids": [],
                "references": language_references,
                "literal_shape_aligned_across_languages": len(set(literal_counts.values()))
                == 1,
                "cross_language_literal_id_alignment_used": False,
                "manual_same_record_semantic_crosscheck": True,
            }
        )
        for literal, replacement in zip(
            source_record_literals, replacements, strict=True
        ):
            if replacement is None:
                continue
            coordinate = (block_id, record_id, literal.literal_id)
            problems = previous.common.invariant_mismatches(literal.text, replacement)
            if previous.bracket_sequence(literal.text) != previous.bracket_sequence(
                replacement
            ):
                problems.append(
                    "bracket_sequence: "
                    f"source={previous.bracket_sequence(literal.text)!r}, "
                    f"ko={previous.bracket_sequence(replacement)!r}"
                )
            if problems:
                invariant_failures.append(
                    {"coordinate": list(coordinate), "problems": problems}
                )
            replacement_map[coordinate] = replacement
            overlay_entries.append(
                {
                    "block_id": block_id,
                    "record_id": record_id,
                    "literal_id": literal.literal_id,
                    "source_sc_utf16le_sha256": previous.text_hash(literal.text),
                    "ko": replacement,
                }
            )
            review_entries.append(
                {
                    "block_id": block_id,
                    "record_id": record_id,
                    "literal_id": literal.literal_id,
                    "status": "translated",
                    "translation_origin": "assistant_generated_draft_from_pinned_sc_jp_en_tc_record_context",
                    "automated_draft": True,
                    "human_review_required": True,
                    "runtime_reviewed": False,
                    "uncertainty_flags": _uncertainty_flags(
                        coordinate, literal_counts, len(source_record_literals)
                    ),
                }
            )
    if invariant_failures:
        raise ValueError(f"replacement invariants failed: {invariant_failures}")

    sc_packed = loaded["SC"]["packed"]
    sc_raw = loaded["SC"]["raw"]
    overlay = {
        "schema": previous.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "defaults": {"status": "translated"},
        "entry_count": len(overlay_entries),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "packed_size": len(sc_packed),
            "packed_sha256": previous.sha256(sc_packed),
            "raw_size": len(sc_raw),
            "raw_sha256": previous.sha256(sc_raw),
            "record_count": archives["SC"].record_count,
            "literal_slot_count": len(sc_literals),
        },
        "entries": overlay_entries,
    }
    rebuilt, binary_manifest = previous.apply_overlay_blob(sc_packed, overlay)
    _target_header, target_raw = previous.decompress_wrapper(rebuilt)
    target = previous.parse_packed_msggame(rebuilt)
    target_literals = previous._literal_map(target.archive)
    target_records = previous._record_map(target.archive)
    if set(target_literals) != set(sc_literals):
        raise ValueError("literal coordinates changed after rebuild")
    for coordinate, source_literal in sc_literals.items():
        expected = replacement_map.get(coordinate, source_literal.text)
        if target_literals[coordinate].text != expected:
            raise ValueError(f"rebuilt literal mismatch at {coordinate}")
    if set(target_records) != set(records["SC"]):
        raise ValueError("record coordinates changed after rebuild")
    if any(
        previous.record_skeleton(records["SC"][key])
        != previous.record_skeleton(target_records[key])
        for key in target_records
    ):
        raise ValueError("opaque record bytecode changed outside literal text")
    if previous.rebuild_raw_msggame(target.archive) != target_raw:
        raise ValueError("rebuilt target raw parse/rebuild is not byte-identical")
    if [len(block.records) for block in archives["SC"].blocks] != [
        len(block.records) for block in target.archive.blocks
    ]:
        raise ValueError("top-level block record counts changed")
    if any(block.offset % 4 for block in target.archive.blocks):
        raise ValueError("rebuilt top-level block offset is not four-byte aligned")

    selected = selected_coordinates()
    actual_coordinates = [
        tuple(entry[key] for key in ("block_id", "record_id", "literal_id"))
        for entry in overlay_entries
    ]
    if actual_coordinates != selected:
        raise ValueError("overlay coordinate order is not deterministic")
    if selected[-1] != (6, 1991, 0) or NEXT_COORDINATE not in sc_literals:
        raise ValueError("batch continuation boundary changed")

    record_keys = selected_record_keys()
    evidence = {
        "schema": "nobu16.kr.msggame-translation-alignment-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "scope": {
            "first_coordinate": list(selected[0]),
            "last_coordinate": list(selected[-1]),
            "selected_record_count": len(record_keys),
            "selected_literal_count": len(selected),
            "next_coordinate": list(NEXT_COORDINATE),
            "scanned_visible_candidate_count": len(selected),
            "skipped_candidates": [],
        },
        "alignment_basis": [
            "same_pk_resource_role",
            "same_18_block_shape",
            "same_block_and_record_coordinates",
            "manual_same_record_semantic_crosscheck",
            "language_literal_shapes_may_differ",
            "cross_language_literal_id_alignment_not_used",
        ],
        "source_files": {
            language: {
                "logical_path": SOURCE_PATHS[language],
                **previous.SOURCE_PINS[SOURCE_PATHS[language]],
            }
            for language in LANGUAGES
        },
        "record_count": len(record_evidence),
        "records": record_evidence,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.msggame-translation-review-index.v1",
        "batch_id": BATCH_ID,
        "quality_state": "draft_not_human_or_runtime_reviewed",
        "entry_count": len(review_entries),
        "entries": review_entries,
        "contains_commercial_source_text": False,
    }

    out_root = args.out_root.resolve()
    artifacts: dict[str, dict[str, Any]] = {}
    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    artifacts["overlay"] = previous.write_json(overlay_path, overlay)
    artifacts["alignment_evidence"] = previous.write_json(evidence_path, evidence)
    artifacts["review_index"] = previous.write_json(review_path, review)
    source_free_scan = _assert_public_source_free(
        (overlay_path, evidence_path, review_path)
    )
    installed_after = {
        language: previous.sha256(path.read_bytes()) for language, path in paths.items()
    }
    if installed_before != installed_after:
        raise ValueError("installed game source changed during read-only batch build")

    validation = {
        "schema": "nobu16.kr.msggame-translation-generation-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": {
            "first_coordinate": list(selected[0]),
            "last_coordinate": list(selected[-1]),
            "selected_record_count": len(record_keys),
            "selected_literal_count": len(selected),
            "next_coordinate": list(NEXT_COORDINATE),
            "selected_coordinates_sha256": previous.sha256(
                json.dumps(selected, separators=(",", ":")).encode("utf-8")
            ),
        },
        "selection": {
            "stable_sc_coordinate_order": True,
            "natural_scan_record_boundaries": True,
            "all_linguistic_literals_in_scanned_records_selected": True,
            "scanned_visible_candidate_count": len(selected),
            "nonlinguistic_visible_candidate_skips": 0,
            "skipped_candidates": [],
        },
        "source_alignment": {
            "languages": list(LANGUAGES),
            "record_coordinates_aligned": True,
            "literal_shapes_assumed_aligned": False,
            "manual_same_record_semantic_crosschecks": len(record_keys),
            "record_reference_count": len(record_keys) * len(LANGUAGES),
        },
        "replacement_invariants": {
            "checked": len(selected),
            "failures": 0,
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "leading_whitespace",
                "trailing_whitespace",
                "escape_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
                "bracket_sequence_in_order",
            ],
        },
        "offline_binary_validation": {
            "entry_count": binary_manifest["entry_count"],
            "target_packed_size": len(rebuilt),
            "target_packed_sha256": previous.sha256(rebuilt),
            "target_raw_size": len(target_raw),
            "target_raw_sha256": previous.sha256(target_raw),
            "literal_coordinates_preserved": True,
            "record_coordinates_preserved": True,
            "opaque_record_bytecode_preserved": True,
            "top_level_offsets_recomputed_and_aligned": True,
            "raw_parse_rebuild_byte_exact": True,
            "skipped_candidates_unchanged": True,
            "installed_game_file_written": False,
        },
        "translation_status": {
            "translated_draft": len(selected),
            "human_review_required": len(selected),
            "runtime_reviewed": 0,
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": previous.sha256(SCRIPT_PATH.read_bytes()),
        },
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
            "byte_identical_offline_binary_required": True,
        },
        "safety": {
            "installed_game_files_modified": False,
            "font_files_modified": False,
            "installer_modified": False,
            "root_readme_modified": False,
            "progress_manifest_modified": False,
            "other_workstreams_modified": False,
            "process_memory_access": False,
            "dll_injection": False,
            "executable_modified": False,
            "registry_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    artifacts["generation_validation"] = previous.write_json(
        validation_path, validation
    )
    if previous.script_counts(validation_path.read_text(encoding="utf-8")) != {
        "cjk_unified_count": 0,
        "kana_count": 0,
    }:
        raise ValueError("source-script text leaked into validation artifact")
    return {
        "out_root": out_root,
        "entry_count": len(selected),
        "record_count": len(record_keys),
        "skipped_count": 0,
        "next_coordinate": NEXT_COORDINATE,
        "target_packed_sha256": previous.sha256(rebuilt),
        "artifacts": artifacts,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    for language in LANGUAGES:
        parser.add_argument(
            f"--stock-{language.lower()}",
            type=Path,
            default=WORKSPACE_ROOT / Path(SOURCE_PATHS[language]),
        )
    parser.add_argument("--out-root", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    try:
        result = build(parse_args())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={result['out_root']}")
    print(f"records={result['record_count']}")
    print(f"entries={result['entry_count']}")
    print(f"skipped={result['skipped_count']}")
    print("next_coordinate=" + ",".join(map(str, result["next_coordinate"])))
    print(f"target_packed_sha256={result['target_packed_sha256']}")
    for name, artifact in result["artifacts"].items():
        print(f"{name}_sha256={artifact['sha256']}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
