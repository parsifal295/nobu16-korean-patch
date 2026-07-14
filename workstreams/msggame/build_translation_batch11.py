#!/usr/bin/env python3
"""Build source-free PK/SC msggame Korean translation batch 11."""

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


BATCH_ID = "msggame_pk_system_messages_b06r1515_1677.v0.11"
OVERLAY_NAME = "msggame_ko_system_messages_b06r1515_1677.v0.11.json"
EVIDENCE_NAME = "translation_alignment_evidence.v0.11.json"
REVIEW_NAME = "translation_review_index.v0.11.json"
VALIDATION_NAME = "translation_validation.v0.11.json"
RESOURCE = previous.RESOURCE
LANGUAGES = previous.LANGUAGES
SOURCE_PATHS = previous.SOURCE_PATHS
NEXT_COORDINATE = (6, 1677, 1)


TRANSLATIONS: dict[tuple[int, int], tuple[str | None, ...]] = {
    (6, 1515): (": 우호 상대:", ", 우호도가 상승했습니다."),
    (6, 1516): (": 우호 상대:", ", 이전 우호도:", ", 변경 후:", "."),
    (6, 1517): (": 우호 상대:", ", 우호도가 하락했습니다."),
    (6, 1518): (": 우호 상대:", ", 이전 우호도:", ", 변경 후:", "."),
    (6, 1519): ("거리가 너무 멀어 친선을 중지합니다. 대상:", "."),
    (6, 1520): ("비용이 부족해 친선을 중지합니다. 대상:", "."),
    (6, 1521): ("중개자가 없어 친선을 중지합니다. 대상:", "."),
    (6, 1522): (": 친선 상대:", ", 거리가 너무 멀어\n계속할 수 없습니다."),
    (6, 1523): (": 친선 상대:", ", 비용이 부족해\n계속할 수 없습니다."),
    (6, 1524): (": 친선 상대:", ", 중개자가 없어\n계속할 수 없습니다."),
    (6, 1525): (": 도달한 신용:", "."),
    (6, 1526): (": 동맹 상대:", ", 동맹이 종료되었습니다."),
    (6, 1527): (": 정전 상대:", ", 정전이 종료되었습니다."),
    (6, 1528): ("원군 요청 세력:", ", 종료까지 2개월."),
    (6, 1529): ("비용 부족으로 조정에 대한 헌금을 중지했습니다.",),
    (6, 1530): ("중개자가 없어 조정에 대한 헌금을 중지했습니다.",),
    (6, 1531): ("조정에 헌금을 마치고 관직 추천을 기다립니다.",),
    (6, 1536): ("이런 식으로 단교할 상대:", "\n단교하면 여러 나라가\n우리를 믿기 어려워질 것입니다"),
    (6, 1537): ("어쩔 수 없다 해도 단교하면\n", "도 체면이 서지 않겠지요.\n우리를 공격할지도 모릅니다"),
    (6, 1538): ("단교 상대:", ", 다른 나라들도\n우리를 공격할 수 있습니다.\n전쟁에 대비해야 합니다"),
    (6, 1539): (": 단교 상대:", ", 전쟁이 일어날 수 있습니다.\n우리에게도\n중대한 고비입니다"),
    (6, 1540): (": 단교 상대:", ", 전쟁이 일어나겠군요.\n하하하,\n벌써부터 피가 끓습니다"),
    (6, 1541): (": 본가와 단교한 세력:", ". 여러 나라까지 우리를 버릴지 모릅니다.\n그러니\n철저히 대비해야 합니다"),
    (6, 1548): (": 단교 상대:", ", 전쟁은 피할 수 없습니다.\n반드시\n대비해야 합니다"),
    (6, 1549): ("단교로 교섭이 이미\n결렬되었으니 전쟁에 대비해야 합니다",),
    (6, 1556): (": 본가와 단교할 세력:", ". 여러 나라가 우리를 노릴 수 있습니다……\n그러니\n철저히 대비해야 합니다"),
    (6, 1557): ("단교 상대:", ", 앞으로 외교가 매우 어려워질 것입니다……\n미리\n병마를 갖춰야 합니다"),
    (6, 1558): ("과연 주군:", ". 단교 상대:", ", 평판이 나빠져도 자기 길을 택하시다니……\n참으로\n본가의 주군이십니다!"),
    (6, 1563): (": 감히 단교를 말하다니\n용서할 수 없다.\n응분의 대가를 치르게 하자",),
    (6, 1564): ("단교를 선언한 세력:", ". 이를 내버려 두면\n다른 가문도\n우리를 얕볼 것입니다"),
    (6, 1565): (": 본가와 단교했습니다.\n사태가 심각하니\n서둘러 토벌해야 합니다",),
    (6, 1566): ("합종연횡이 난세의 도리라 해도 이번에는\n", "의 배신이 신의를 저버렸으니\n반드시 벌해야 합니다"),
    (6, 1567): (": 감히 단교하다니!\n본가의 이름을 더럽힌 원한을 갚지 않고는\n분이 풀리지 않는다!",),
    (6, 1568): ("이제 벌할 세력:", ".\n우리를 배신한 대가가 무엇인지\n여러 나라에 보여 주자!"),
    (6, 1575): ("본가가 내민 손을 뿌리치다니,\n", "의 행위는 용서할 수 없습니다.\n반드시 대가를 치르게 합시다"),
    (6, 1576): ("본가 휘하의 세력:", ".\n감히 단교하다니,\n내버려 두면 훗날 화근이 될 것입니다"),
    (6, 1587): (": 본가에 속했다면\n이제 함께 싸우고 전진하는\n한마음의 동료가 된 것입니다",),
    (6, 1588): ("본가에 속했다 해도 상대:", "\n그들은 우리와 달리 다음 가문의 가신이 아닙니다:", ".\n대우에 신경 써야 합니다"),
    (6, 1589): ("종속 세력:", ". 우리 세력은 커졌지만\n적도 함께 늘었다고 보아야 합니다.\n주의하십시오"),
    (6, 1590): (": 우리에게 굴복했지만\n멸망한 것은 아닙니다. 단교를 생각하지 못하도록\n단단히 다스려야 합니다",),
    (6, 1591): ("변설만으로\n굴복시킨 세력:", ".\n하지만 저 같은 무인은 흉내 내기 어렵습니다"),
    (6, 1592): ("호오, 본가에 종속한 세력:", ".\n이제 그들과 나란히 무공을 겨루겠군요.\n생각만 해도 피가 끓습니다"),
    (6, 1599): ("종속 세력:", ". 앞으로 우리가 그들의 후원자가 되어\n더욱\n강하게 키워야 합니다"),
    (6, 1600): (": 본가에 종속했지만\n우리 힘을 이용하려는 것뿐일지 모릅니다.\n주의하십시오",),
    (6, 1611): ("지금은 약한 처지이므로 다음 세력에\n", "종속했습니다. 시간을 벌어\n힘을 비축해야 합니다"),
    (6, 1612): ("한번 종속했다면 섬길 세력:", "\n예의와 신의를 다해야 합니다.\n단교하면 악명이 퍼질 것입니다"),
    (6, 1613): ("종속된 세력:", ". 그렇다고 위축될 필요는 없습니다.\n그들을 창과 방패로 삼아\n우리 힘을 키웁시다"),
    (6, 1614): ("종속은 일방적인 복종이 아닙니다.\n운명을 함께할 세력:", ". 각오는 하되\n우리도 자립해야 합니다"),
    (6, 1615): ("남의 아래에 서는 건 성미에 맞지 않지만,\n본가의 힘은 다음 세력과", "비교할 수 없습니다.\n어쩔 수 없지요"),
    (6, 1616): ("주군:", ", 굴복한 세력:", ". 이는 우리의 힘이 부족한 탓입니다.\n이 고통을 잊지 말고\n정진하겠습니다"),
    (6, 1623): ("무릎 꿇은 상대:", ". 굴욕스럽지만 여러 나라를 적으로 돌리는 것보다는 낫습니다.\n휘하에서 힘을 길러\n앞날을 도모합시다"),
    (6, 1624): ("종속이 아니라 후원자를 얻었다고 생각할 세력:", ".\n전쟁이 나면\n든든한 아군이 될 것입니다"),
    (6, 1633): ("혼인을 축하합니다. 당사자:", ", 상대:", ".\n본가와 서로 신뢰하는 인척이 되기를 바랍니다"),
    (6, 1634): ("혼인 당사자:", ", 상대:", ". 두 가문이 혼인으로 하나가 되어\n함께\n밝은 미래를 열어 갑시다"),
    (6, 1635): ("부부가 된 당사자:", ". 두 가문을 잇는 인연의 상징입니다.\n그 이야기는 나중에 하고\n먼저 연회를 열지요"),
    (6, 1639): ("혼인이 정해진 상대:", ". 이제 두 가문은\n한 식구이자 동맹으로\n함께 나아갑시다"),
    (6, 1643): ("세력 전체의 금전과 군량 세율을 변경할 수 있습니다",),
    (6, 1644): ("세력 전체의 금전과 군량 세율을 변경할 수 있습니다",),
    (6, 1645): ("금전 세율을 변경합니다",),
    (6, 1646): ("군량 세율을 변경합니다",),
    (6, 1647): ("세력 전체의 각 부문 수준을 변경할 수 있습니다",),
    (6, 1648): ("수준을 높일 부문:", "."),
    (6, 1649): ("수준을 낮출 부문:", "."),
    (6, 1650): ("세율 변경을 확정합니다",),
    (6, 1651): ("변경된 항목이 없습니다",),
    (6, 1652): ("세율 변경이 확정되지 않았습니다\n변경을 취소하시겠습니까?",),
    (6, 1653): ("알겠습니다\n새 세율에 맞춰 준비하겠습니다",),
    (6, 1654): ("금전 부족으로 모든 정책을 철회합니다.",),
    (6, 1655): ("재정을 유지할 수 없어 수준이 낮아질 부문:", "외 여러 부문."),
    (6, 1659): ("금전이 부족해 정책을 유지할 수 없습니다.\n모든 정책을 일단 철회했습니다.\n발령할 정책을 다시 검토해야 합니다.",),
    (6, 1660): ("금전 부족으로 정책이 무너지고 있습니다.\n우선 정책을 철회했습니다.\n낭비를 줄이고 다시 검토합시다.",),
    (6, 1661): ("금전이 돌지 않아 정책을 지속할 수 없습니다.\n정책을 철회할 수밖에 없습니다.\n모두를 위해 서둘러 재검토해야 합니다.",),
    (6, 1665): ("금전 부족으로 정책을 유지할 수 없다는 보고입니다……\n서둘러 모든 정책을 철회했습니다.\n본가에 필요한 정책만 다시 고릅시다.",),
    (6, 1671): ("재정에 문제가 생긴 듯합니다. 금전 부족으로\n다음 부문의 수준이 감소했습니다:", "\n권농", ", 상공", ", 기반 시설", ", 문화", ", 치안"),
    (6, 1672): ("금전 부족으로 재정을 유지하기 어려워\n다음 부문의 수준이 감소했습니다:", "\n권농", ", 상공", ", 기반 시설", ", 문화", ", 치안"),
    (6, 1673): ("간략히 보고합니다. 금전 부족으로 재정난이 생겨……\n다음 부문의 수준이 감소했습니다:", "\n권농", ", 상공", ", 기반 시설", ", 문화", ", 치안"),
    (6, 1677): ("금전 부족으로 재정을 유지할 수 없어\n다음 부문의 수준이 감소했습니다:", None, None, None, None, None),
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
    if selected[0] != (6, 1515, 0) or selected[-1] != (6, 1677, 0):
        raise ValueError("translation batch boundaries changed")
    if len(selected) != 150 or len(keys) != 77:
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
    if selected[-1] != (6, 1677, 0) or NEXT_COORDINATE not in sc_literals:
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
