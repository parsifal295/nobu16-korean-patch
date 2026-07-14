#!/usr/bin/env python3
"""Build source-free PK/SC msggame Korean translation batch 12."""

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


BATCH_ID = "msggame_pk_system_messages_b06r1677_1838.v0.12"
OVERLAY_NAME = "msggame_ko_system_messages_b06r1677_1838.v0.12.json"
EVIDENCE_NAME = "translation_alignment_evidence.v0.12.json"
REVIEW_NAME = "translation_review_index.v0.12.json"
VALIDATION_NAME = "translation_validation.v0.12.json"
RESOURCE = previous.RESOURCE
LANGUAGES = previous.LANGUAGES
SOURCE_PATHS = previous.SOURCE_PATHS
NEXT_COORDINATE = (6, 1839, 0)


TRANSLATIONS: dict[tuple[int, int], tuple[str | None, ...]] = {
    (6, 1677): (None, "\n권농", ", 상공", ", 기반 시설", ", 문화", ", 치안"),
    (6, 1680): ("정책을 발령해 세력을 강화합니다.",),
    (6, 1681): ("정책 변경이 확정되지 않았습니다\n변경을 취소하시겠습니까?",),
    (6, 1682): ("정책 변경을 확정합니다.",),
    (6, 1683): ("변경된 항목이 없습니다",),
    (6, 1684): ("조정을 의뢰한 세력과의 외교 자세가\n일시적으로 낮아지거나 오르지 않게 됩니다.\n계속하시겠습니까?",),
    (6, 1685): ("교섭 상대:", ". 교섭이 성립하면\n다른 가문과 주고받던 원군이 중지됩니다.\n계속하시겠습니까?"),
    (6, 1686): ("외교 관계를 파기할 상대:", ". 주변 세력의 불신을 사고\n가신의 충성도도 낮아질 수 있습니다.\n계속하시겠습니까?"),
    (6, 1689): ("종속할 세력:", ". 종속하면\n다른 세력과의 외교 관계가 모두 해소됩니다.\n주의하십시오."),
    (6, 1690): ("종속할 세력:", ". 종속하면\n다른 세력과의 외교 관계가 모두 해소됩니다.\n주의하십시오."),
    (6, 1691): ("종속할 세력:", ". 종속하면\n다른 세력과의 외교 관계가 모두 해소됩니다.\n주의하십시오."),
    (6, 1695): ("종속할 세력:", ". 종속하면\n다른 세력과의 외교 관계가 모두 해소됩니다.\n주의하십시오."),
    (6, 1699): ("종속할 세력:", ". 종속하면\n다른 외교 관계가 모두 해소됩니다.\n계속하시겠습니까?"),
    (6, 1702): ("칙명 강화를 사용하면\n다음 위계에 오를 때까지 다시 사용할 수 없습니다.\n주의하십시오.",),
    (6, 1703): ("칙명 강화를 사용하면\n다음 위계에 오를 때까지 다시 사용할 수 없습니다.\n주의하십시오.",),
    (6, 1704): ("칙명 강화를 사용하면\n다음 위계에 오를 때까지 다시 사용할 수 없습니다.\n주의하십시오.",),
    (6, 1708): ("칙명 강화를 사용하면\n다음 위계에 오를 때까지 다시 사용할 수 없습니다.\n주의하십시오.",),
    (6, 1714): ("일방적으로 단교하면 악명이 퍼져\n외교에 악영향을 줍니다.\n주의하십시오.",),
    (6, 1715): ("일방적으로 단교하면 악명이 퍼져\n외교에 악영향을 줍니다.\n주의하십시오.",),
    (6, 1716): ("일방적으로 단교하면 악명이 퍼져\n외교에 악영향을 줍니다.\n주의하십시오.",),
    (6, 1720): ("일방적으로 단교하면 악명이 퍼져\n외교에 악영향을 줍니다.\n주의하십시오.",),
    (6, 1724): ("본가 부대가 머무는 세력:", ". 그 영내에서 단교하면\n악명이 크게 높아집니다.\n계속하시겠습니까?"),
    (6, 1727): ("주가를 바꾸면 악명이 퍼져\n외교에 악영향을 줍니다.\n주의하십시오.",),
    (6, 1728): ("주가를 바꾸면 악명이 퍼져\n외교에 악영향을 줍니다.\n주의하십시오.",),
    (6, 1729): ("주가를 바꾸면 악명이 퍼져\n외교에 악영향을 줍니다.\n주의하십시오.",),
    (6, 1733): ("주가를 바꾸면 악명이 퍼져\n외교에 악영향을 줍니다.\n주의하십시오.",),
    (6, 1737): ("혼인할 무장이나 공주를 선택하십시오.",),
    (6, 1738): ("혼인할 무장과 공주가 선택되지 않았습니다.",),
    (6, 1739): ("다음 세력과 단교시킬 상대:", "\n선택하십시오."),
    (6, 1740): ("이 세력과 단교할 상대:", ".\n단교를 지시합니다."),
    (6, 1741): ("다음 세력과 정전시킬 상대:", "\n선택하십시오."),
    (6, 1742): ("이 세력과 정전할 상대:", "\n정전을 지시합니다."),
    (6, 1743): ("다음 세력의 목표로 삼을 상대:", "\n선택하십시오."),
    (6, 1744): ("이 세력을 다음 세력의 목표로 지정합니다:", "."),
    (6, 1745): ("원군을 보낼 목표 성을 선택하십시오.",),
    (6, 1746): ("이 세력을 원군 목표로 지정할 세력:\n", "입니다."),
    (6, 1747): ("제안할 가보를 선택하십시오.",),
    (6, 1748): ("제안할 관직을 선택하십시오.",),
    (6, 1749): ("단교할 세력을 선택하십시오.",),
    (6, 1750): ("교섭의 대가로 이 세력과 단교합니다.",),
    (6, 1751): ("군이나 성을 교환하면\n자동으로 6개월 정전이 맺어집니다.\n계속하시겠습니까?",),
    (6, 1752): ("원군이나 조정 교섭에 필요한 신용입니다.",),
    (6, 1753): ("동맹 교섭에 필요한 신용입니다.",),
    (6, 1754): ("혼인 동맹 교섭에 필요한 신용입니다.",),
    (6, 1755): ("혼인 동맹이나 직위 교섭에 필요한 신용입니다.",),
    (6, 1756): ("동맹이나 종속 관계가 아니면 원군이나 조정을 의뢰할 수 없습니다.",),
    (6, 1757): ("동맹 관계가 아니면 혼인 동맹을 신청할 수 없습니다.",),
    (6, 1758): ("쇼군 가문 이외의 먼 세력과는 외교할 수 없습니다.",),
    (6, 1759): ("본가가 다른 가문에 종속되어 있어 주군 세력 이외와 외교할 수 없습니다.",),
    (6, 1760): ("상대가 다른 세력에 종속되어 있어 외교할 수 없습니다.",),
    (6, 1761): ("상대가 본가의 친선을 거부하고 있습니다.",),
    (6, 1762): ("친선에 필요한 금전이 부족합니다.",),
    (6, 1763): ("중개자가 될 수 있는 무장이 없습니다.",),
    (6, 1764): ("본가가 다른 가문에 종속되어 있어 주군 세력 이외와 외교할 수 없습니다.",),
    (6, 1765): ("상대가 다른 세력에 종속되어 있어 외교할 수 없습니다.",),
    (6, 1766): ("상대는 본가와 교섭할 뜻이 없습니다.",),
    (6, 1767): ("교섭할 수 있는 항목이 없습니다.",),
    (6, 1768): ("막부 세력에는 직위를 줄 수 없습니다.",),
    (6, 1769): ("다른 가문에 종속된 세력에는 직위를 줄 수 없습니다.",),
    (6, 1770): ("상대가 본가와의 교섭을 거부하고 있습니다.",),
    (6, 1771): ("외교 자세를 더 개선할 수 없습니다.",),
    (6, 1772): ("이 세력에 줄 수 있는 직위가 없습니다.",),
    (6, 1773): ("교전 중이거나 교전을 마친 지 얼마 되지 않았습니다.",),
    (6, 1774): ("공물의 효과가 앞으로", "개월간 지속됩니다."),
    (6, 1775): ("동맹 기간:", "개월을 제안합니다."),
    (6, 1776): ("성 공략을 위한 원군을 요청합니다.",),
    (6, 1777): ("지정 세력과의 정전 기간:", "개월의 조정을 의뢰합니다."),
    (6, 1778): ("혼인 동맹 체결을 제안합니다.",),
    (6, 1779): ("외교 관계를 파기합니다.",),
    (6, 1780): ("본가에 종속하도록 권고합니다.",),
    (6, 1781): ("상대에게 신종을 요청합니다.",),
    (6, 1782): ("막부에 직위 수여를 요청합니다.",),
    (6, 1783): ("본가 또는 종속 세력의 성 방어를 요청합니다.",),
    (6, 1784): ("어느 세력도 본가와 친선할 뜻이 없습니다.",),
    (6, 1785): ("친선에 필요한 금전이 부족합니다.",),
    (6, 1786): ("중개자가 될 수 있는 무장이 없습니다.",),
    (6, 1787): ("어느 세력도 본가와 교섭할 뜻이 없습니다.",),
    (6, 1788): ("어느 세력과도 교섭할 수 있는 항목이 없습니다",),
    (6, 1789): ("이미 장기 동맹을 맺고 있습니다.",),
    (6, 1790): ("본가가 종속되어 있어 동맹을 맺을 수 없습니다.",),
    (6, 1791): ("상대가 종속되어 있어 동맹을 맺을 수 없습니다.",),
    (6, 1792): ("상대가 본가와의 교섭을 거부하고 있습니다.",),
    (6, 1793): ("신용이 부족합니다.",),
    (6, 1794): ("교전 중이거나 교전 직후인 세력과는 동맹을 맺을 수 없습니다.",),
    (6, 1795): ("다른 가문이 요청한 원군이 상대와 교전 중입니다",),
    (6, 1796): ("신종한 세력 이외에는 원군을 요청할 수 없습니다.",),
    (6, 1797): ("상대가 본가 이외의 세력에 신종하여 원군을 요청할 수 없습니다.",),
    (6, 1798): ("동맹 또는 종속 관계가 아니면 원군을 요청할 수 없습니다.",),
    (6, 1799): ("이미 상대에게 원군을 요청했습니다.",),
    (6, 1800): ("원군을 의뢰할 수 있는 성이 없습니다.",),
    (6, 1801): ("상대는 현재 원군을 보낼 수 없는 상태입니다.",),
    (6, 1802): ("상대가 본가와의 교섭을 거부하고 있습니다.",),
    (6, 1803): ("신용이 부족합니다.",),
    (6, 1804): ("신종한 세력 이외에는 조정을 의뢰할 수 없습니다.",),
    (6, 1805): ("상대가 종속 세력이므로 조정을 의뢰할 수 없습니다.",),
    (6, 1806): ("동맹 또는 종속 관계가 아니면 조정을 의뢰할 수 없습니다.",),
    (6, 1807): ("상대가 정전을 조정할 수 있는 세력이 없습니다.",),
    (6, 1808): ("상대가 본가와의 교섭을 거부하고 있습니다.",),
    (6, 1809): ("신용이 부족합니다.",),
    (6, 1810): ("이미 혼인 관계를 맺고 있습니다.",),
    (6, 1811): ("본가가 종속되어 있어 혼인 동맹을 맺을 수 없습니다.",),
    (6, 1812): ("동맹 관계가 아니면 혼인 동맹을 맺을 수 없습니다.",),
    (6, 1813): ("상대가 종속되어 있어 혼인 동맹을 맺을 수 없습니다.",),
    (6, 1814): ("혼인할 수 있는 공주나 무장이 없습니다.",),
    (6, 1815): ("상대가 본가와의 교섭을 거부하고 있습니다.",),
    (6, 1816): ("신용이 부족합니다.",),
    (6, 1817): ("상대와 끊을 수 있는 외교 관계가 없습니다.",),
    (6, 1818): ("원군 요청 기간 중이므로 파기할 수 없습니다.",),
    (6, 1819): ("본가 부대가 상대 또는 상대의 종속 세력 영내에\n있거나 진입하려 하고 있습니다.",),
    (6, 1820): ("막부는 다른 가문의 휘하에 들어갈 수 없습니다.",),
    (6, 1821): ("이미 상대와 주종 관계입니다.",),
    (6, 1822): ("본가가 독립 상태가 아니므로 다른 가문을 종속시킬 수 없습니다.",),
    (6, 1823): ("다른 가문과 동맹·종속·신종 관계인 세력은\n종속시킬 수 없습니다.",),
    (6, 1824): ("너무 멀어 종속시킬 수 없습니다.",),
    (6, 1825): ("본가 또는 종속 세력과 인접하지 않습니다.",),
    (6, 1826): ("상대가 본가에 종속되기를 거부하고 있습니다.",),
    (6, 1827): ("상대가 아직 강대하여 종속시킬 수 없습니다.",),
    (6, 1828): ("상대와 비교해 본가의 위신과 병력이 부족합니다.",),
    (6, 1829): ("교전 중이거나 교전 직후인 세력과는 종속·신종 관계를 맺을 수 없습니다.",),
    (6, 1830): ("막부는 다른 가문의 휘하에 들어갈 수 없습니다.",),
    (6, 1831): ("이미 상대와 주종 관계입니다.",),
    (6, 1832): ("본가가 다른 가문에 종속되어 있어 다른 가문에 신종할 수 없습니다.",),
    (6, 1833): ("독립 상태가 아닌 세력에는 신종할 수 없습니다.",),
    (6, 1834): ("다른 가문에 종속된 세력에는 신종할 수 없습니다.",),
    (6, 1835): ("본가 또는 종속 세력과 인접하지 않습니다.",),
    (6, 1836): ("상대가 본가의 신종을 거부하고 있습니다.",),
    (6, 1837): ("상대는 본가에 아직 여력이 있다고 보아 신종을 의심하고 있습니다.",),
    (6, 1838): ("본가의 규모로는 신종을 제안해도\n믿음을 얻을 수 없습니다.",),
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
    if selected[0] != (6, 1677, 1) or selected[-1] != (6, 1838, 0):
        raise ValueError("translation batch boundaries changed")
    if len(selected) != 150 or len(keys) != 128:
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
    if selected[-1] != (6, 1838, 0) or NEXT_COORDINATE not in sc_literals:
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
