#!/usr/bin/env python3
"""Build source-free PK/SC msggame Korean translation batch 17."""

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


BATCH_ID = "msggame_pk_system_messages_b06r2787_3050.v0.17"
OVERLAY_NAME = "msggame_ko_system_messages_b06r2787_3050.v0.17.json"
EVIDENCE_NAME = "translation_alignment_evidence.v0.17.json"
REVIEW_NAME = "translation_review_index.v0.17.json"
VALIDATION_NAME = "translation_validation.v0.17.json"
RESOURCE = previous.RESOURCE
LANGUAGES = previous.LANGUAGES
SOURCE_PATHS = previous.SOURCE_PATHS
NEXT_COORDINATE = (6, 3050, 3)


TRANSLATIONS: dict[tuple[int, int], tuple[str | None, ...]] = {
    (6, 2787): (None, "\n가신으로 끌어들이는 건 어떻겠습니까?"),
    (6, 2788): ("새 가신:", ". 이제부터 가신으로\n주군께 평생 충성을 다하겠습니다!\n잘 부탁드립니다."),
    (6, 2789): ("알겠습니다\n이 이야기는 일단 거두겠습니다",),
    (6, 2790): (": 본가의 휘하로 들어왔습니다",),
    (6, 2791): ("의 새 주군:", ". 휘하로 들어갔습니다"),
    (6, 2794): ("빌린 장병의 반환 기한이 지났지만\n아직 공성을 계속하고 있습니다\n이번 공성이 끝날 때까지 기다려 주시겠습니까?",),
    (6, 2795): ("빌린 장병의 반환 기한이 지났지만\n아직 공성을 계속하고 있습니다\n이번 공성이 끝날 때까지 기다려 주시겠습니까?",),
    (6, 2796): ("빌린 장병의 반환 기한이 지났지만\n아직 공성을 계속하고 있습니다\n이번 공성이 끝날 때까지 기다려 주시겠습니까?",),
    (6, 2800): ("빌린 장병의 반환 기한이 지났지만\n아직 공성을 계속하고 있습니다\n이번 공성이 끝날 때까지 기다려 주시겠습니까?",),
    (6, 2806): ("오, 정말 감사합니다!\n공성이 끝나는 즉시\n돌려드리겠다고 약속하겠습니다",),
    (6, 2807): ("오, 정말 감사합니다!\n공성이 끝나는 즉시\n돌려드리겠다고 약속하겠습니다",),
    (6, 2808): ("오, 정말 감사합니다!\n공성이 끝나는 즉시\n돌려드리겠다고 약속하겠습니다",),
    (6, 2812): ("오, 정말 감사합니다!\n공성이 끝나는 즉시\n돌려드리겠다고 약속하겠습니다",),
    (6, 2818): ("알겠습니다\n관계를 끊을 세력:", ". 인연도 여기까지입니다."),
    (6, 2819): ("알겠습니다\n동맹을 해소할 세력:", ". 맹약을 해소하겠습니다."),
    (6, 2820): ("알겠습니다\n동맹을 파기할 세력:", ". 이제 동맹은 무효입니다."),
    (6, 2824): ("알겠습니다\n동맹을 폐기할 세력:", ". 동맹을 폐기하겠습니다."),
    (6, 2830): ("맹약을 끊을 상대:", ".\n현명한 판단입니다"),
    (6, 2831): ("맹약을 끊을 상대:", ". 그 결심을\n결코 잊지 않겠습니다"),
    (6, 2832): ("맹약을 끊을 상대:", ". 그 각오를\n깊이 새기겠습니다"),
    (6, 2836): ("동맹을 백지로 돌릴 상대:", ".\n현명한 선택이라 생각합니다"),
    (6, 2842): ("알겠습니다\n관계를 끊을 세력:", ". 인연도 여기까지입니다."),
    (6, 2843): ("알겠습니다\n동맹을 해소할 세력:", ". 맹약을 해소하겠습니다."),
    (6, 2844): ("알겠습니다\n동맹을 파기할 세력:", ". 이제 동맹은 무효입니다."),
    (6, 2848): ("알겠습니다\n동맹을 폐기할 세력:", ". 동맹을 폐기하겠습니다."),
    (6, 2854): ("좋다, 결정했다\n공격할 세력:", ". 출진하자"),
    (6, 2855): ("알겠습니다\n공격할 세력:", ". 공격합시다"),
    (6, 2856): ("좋습니다\n공격할 세력:", ". 공격하겠습니다"),
    (6, 2860): ("알겠습니다\n공격하겠습니다. 대상:",),
    (6, 2866): ("그렇다면 약속을 어기지 마십시오\n공격 대상:", ". 반드시 공격해야 합니다"),
    (6, 2867): ("반드시 약속을 지키십시오\n공격 대상:", ". 밀약을 어겨서는 안 됩니다"),
    (6, 2868): ("잊지 마십시오. 공격 대상:", ". 공격 약속을 지켜야 합니다"),
    (6, 2872): ("공략 대상:", ". 공략은 맡기겠습니다\n절대 잊지 마십시오"),
    (6, 2878): ("저버리고 온 세력:", "\n궁지에 몰린 새는 품어 주는 법.\n이제부터 본가가 지켜 주겠습니다"),
    (6, 2879): ("등을 돌린 세력:", "입니까?\n본가를 방패로 택한 것은 현명합니다\n앞으로 활약을 기대하겠습니다"),
    (6, 2880): ("떠나온 세력:", ". 본가에 의탁하겠습니까?\n안심하십시오\n앞으로는 반드시 지켜 드리겠습니다"),
    (6, 2884): ("저버린 세력:", ".\n탁월한 안목입니다\n저와 함께 천하를 노립시다"),
    (6, 2890): ("미래가 불안한 옛 주군:", ".\n앞으로 잘 부탁드립니다"),
    (6, 2891): (": 믿을 수 없습니다……\n이제부터 잘 부탁드립니다",),
    (6, 2892): (": 기댈 만한 이가 아닙니다……\n앞으로 잘 부탁드립니다",),
    (6, 2896): ("기대를 버린 옛 주군:", ".\n이제부터 귀가를 위해 힘쓰겠습니다"),
    (6, 2902): ("용서할 수 없는 대상:", ". 맹약을 끊은 행위,\n배후 세력:", ". 그 사주 모두 용서할 수 없습니다"),
    (6, 2903): (": 단교를 통고해 왔습니까?\n배후 세력:", ". 그 사주가 분명합니다"),
    (6, 2904): (": 단교한다고……?\n배후 세력:", ". 그 사주인가?"),
    (6, 2908): (": 맹약을 파기하다니!?\n배후 세력:", ". 분명 그들의 짓입니다"),
    (6, 2914): ("배신한 세력:", "!\n감히 우리를 배신하다니!"),
    (6, 2915): (": ……용서할 수 없습니다\n감히 본가를 떠나다니!",),
    (6, 2916): ("배신한 세력:", "!\n감히 우리를 배신하다니!"),
    (6, 2920): ("이럴 수가……\n", "의 배신이라니……"),
    (6, 2926): ("배신한 세력:", "!\n감히 우리를 배신하다니!"),
    (6, 2927): (": ……용서할 수 없습니다\n감히 본가를 떠나다니!",),
    (6, 2928): ("배신한 세력:", "!\n감히 우리를 배신하다니!"),
    (6, 2932): ("이럴 수가……\n", "의 배신이라니……"),
    (6, 2936): ("제안 내용을 철회하고\n상대의 요구를 표시합니다\n계속하시겠습니까?",),
    (6, 2937): ("이 정도 부탁이라면 어렵지 않지만,\n보답은 얼마나 받을 수 있겠습니까?",),
    (6, 2938): ("호오, 제법 비용이 들겠군요\n보답을 기대해도 되겠습니까?",),
    (6, 2939): ("상당히 어려운 부탁이군요……\n그에 맞는 보답은 준비했겠지요?",),
    (6, 2942): ("이 정도 금액으로는\n조정이 납득하지 않을 것입니다……",),
    (6, 2943): ("이 정도 금액으로는\n조정이 받아들이지 않을 것입니다……",),
    (6, 2944): ("이 정도 금액으로는\n조정이 응하지 않을 것입니다……",),
    (6, 2948): ("이 정도 금액으로는\n조정도 납득하지 않을 것입니다……",),
    (6, 2954): ("이만큼이면\n조정도 기꺼이 청을 들어줄 것입니다",),
    (6, 2955): ("이만큼이면\n조정도 흔쾌히 청을 받아들일 것입니다",),
    (6, 2956): ("이만큼이면 조정도 기꺼이 응할 것입니다",),
    (6, 2960): ("이만큼이면,\n조정도 외면하지 않을 것입니다",),
    (6, 2964): ("에서\n친선 요청이 왔습니다\n확인하십시오",),
    (6, 2965): ("에서\n종속 요청이 왔습니다\n확인하십시오",),
    (6, 2966): ("에서\n본가에 신종하겠다는 사자가 왔습니다\n확인하십시오",),
    (6, 2967): ("에서\n단교 통고가 왔습니다!",),
    (6, 2968): ("에서\n교섭 요청이 왔습니다\n확인하십시오",),
    (6, 2969): ("에서 사자가 왔습니다\n전향할 세력:", ". 그 휘하에서 전향을 청합니다.\n확인하십시오"),
    (6, 2972): ("님\n제 부탁을 들어주시겠습니까?",),
    (6, 2973): ("님\n제 부탁을 들어주시겠습니까?",),
    (6, 2974): ("님\n제 부탁을 들어주시겠습니까?",),
    (6, 2978): ("님\n제 부탁을 들어주시겠습니까?",),
    (6, 2984): ("아, 오신 분:", "님이시군요?"),
    (6, 2985): ("아, 오신 분:", "님이시군요?"),
    (6, 2986): ("아, 오신 분:", "님이시군요?"),
    (6, 2990): ("아, 오신 분:", "님이시군요?"),
    (6, 2996): ("님\n어떤 보답을 원하십니까?",),
    (6, 2997): ("님\n어떤 보답을 원하십니까?",),
    (6, 2998): ("님\n어떤 보답을 원하십니까?",),
    (6, 3002): ("님\n어떤 보답을 원하십니까?",),
    (6, 3008): ("보답을 지나치게 높이면\n상대의 화만 돋울 것입니다……",),
    (6, 3009): ("보답을 지나치게 높이면\n상대의 화만 돋울 것입니다……",),
    (6, 3010): ("보답을 지나치게 높이면\n상대의 화만 돋울 것입니다……",),
    (6, 3014): ("보답을 지나치게 높이면\n상대의 화만 돋울 것입니다……",),
    (6, 3020): ("보답을 너무 높인 건 아닐까?",),
    (6, 3021): ("보답을 너무 높인 건 아닐까?",),
    (6, 3022): ("보답을 너무 높인 건 아닐까?",),
    (6, 3026): ("보답을 너무 높인 건 아닐까?",),
    (6, 3032): ("그렇다면 부탁을 말씀해 보십시오",),
    (6, 3033): ("그렇다면 부탁을 말씀해 보십시오",),
    (6, 3034): ("그렇다면 부탁을 말씀해 보십시오",),
    (6, 3038): ("그렇다면 부탁을 말씀해 보십시오",),
    (6, 3042): ("이 내용으로 교섭을 제안합니다\n계속하시겠습니까?",),
    (6, 3043): ("조정과의 교섭을 중단합니다. 계속하시겠습니까?",),
    (6, 3044): ("선택한 주청 내용을 모두 지웁니다\n계속하시겠습니까?",),
    (6, 3045): ("선택한 제안 내용을 모두 지웁니다\n계속하시겠습니까?",),
    (6, 3046): ("혼인 동맹 해소 대상:", ". 혼인 동맹이 해소되었습니다."),
    (6, 3047): ("동맹 전환 대상:", ". 기간:", "개월 동맹으로 전환되었습니다."),
    (6, 3050): ("사망한 인물:", ". 사망으로,\n혼인 관계였던 세력:", ". 해당 동맹도\n", None),
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
    if selected[0] != (6, 2787, 1) or selected[-1] != (6, 3050, 2):
        raise ValueError("translation batch boundaries changed")
    if len(selected) != 150 or len(keys) != 102:
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
    if selected[-1] != (6, 3050, 2) or NEXT_COORDINATE not in sc_literals:
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
