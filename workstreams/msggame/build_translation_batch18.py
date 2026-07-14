#!/usr/bin/env python3
"""Build source-free PK/SC msggame Korean translation batch 18."""

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


BATCH_ID = "msggame_pk_system_messages_b06r3050_3298.v0.18"
OVERLAY_NAME = "msggame_ko_system_messages_b06r3050_3298.v0.18.json"
EVIDENCE_NAME = "translation_alignment_evidence.v0.18.json"
REVIEW_NAME = "translation_review_index.v0.18.json"
VALIDATION_NAME = "translation_validation.v0.18.json"
RESOURCE = previous.RESOURCE
LANGUAGES = previous.LANGUAGES
SOURCE_PATHS = previous.SOURCE_PATHS
NEXT_COORDINATE = (6, 3302, 0)


TRANSLATIONS: dict[tuple[int, int], tuple[str | None, ...]] = {
    (6, 3050): (None, None, None, "개월 후 소멸합니다."),
    (6, 3051): ("사망한 인물:", ". 사망으로,\n혼인 관계였던 세력:", ". 해당 동맹도\n", "개월 후 소멸합니다."),
    (6, 3052): ("사망한 인물:", ". 사망으로,\n혼인 관계였던 세력:", ". 해당 동맹도\n", "개월 후 소멸합니다."),
    (6, 3056): ("사망한 인물:", ". 사망으로,\n혼인 관계였던 세력:", ". 해당 동맹도\n", "개월 후 소멸합니다."),
    (6, 3060): ("혼인 관계를 유지할 수 없게 되어,\n동맹 상대:", "의 동맹은 앞으로", "개월 남았습니다.\n각별히 주의하십시오."),
    (6, 3063): ("혼인 관계가 사라졌습니다. 동맹 상대:\n", ". 혼인으로 맺은 동맹도\n앞으로", "개월 후 효력을 잃으니 주의하십시오."),
    (6, 3064): ("안타깝게도 혼인 관계가 사라져,\n동맹 상대:", ". 해당 동맹도\n", "개월 후 효력을 잃습니다."),
    (6, 3065): ("혼인 관계가 끝난 세력:", ". 더는 친척이 아니므로,\n동맹은 앞으로", "개월 후 소멸합니다.\n그때는 전쟁이 벌어질지도 모릅니다."),
    (6, 3069): ("특별한 관계가 끝난 세력:", ". 더는 특별한 관계가 아니며,\n", "개월 후 동맹도 효력을 잃습니다.\n이후의 대응은 그때 판단해야 합니다."),
    (6, 3075): (": 본가를 떠났습니다.\n혼인 동맹 상대:", "의 동맹도\n앞으로", "개월 후 효력을 잃습니다."),
    (6, 3076): ("매우 안타깝습니다.\n본가를 떠난 인물:", ". 본가를 떠났습니다. 동맹 상대:", ". 해당 동맹은\n앞으로", "개월 남았습니다."),
    (6, 3077): (": 본가를 떠났습니다.\n혼인 동맹 상대:", "의 동맹도\n앞으로", "개월 후 효력을 잃습니다."),
    (6, 3081): ("상실한 인물:", ". 그 아픔에 더해,\n혼인 동맹 상대:", ". 혼인 관계도 사라졌습니다.\n", "개월 후 동맹마저 효력을 잃으니 상황이 어렵습니다."),
    (6, 3082): (": 취향에 맞는 진품입니다. 대상:", ".\n기뻐하지 않을 리 없습니다."),
    (6, 3083): ("뭐라고, 선물이:", "……!\n그런데 취향의 주인:", ". 그 취향을 알다니,\n놀라울 따름입니다."),
    (6, 3087): ("귀가는 이제 충분히 강해졌습니다\n이제 주종 관계를 끝내고 대등한 동맹을 맺어\n각자의 발전을 위해 함께 싸웁시다",),
    (6, 3088): ("귀가는 이제 충분히 강해졌습니다\n이제 주종 관계를 끝내고 대등한 동맹을 맺어\n각자의 발전을 위해 함께 싸웁시다",),
    (6, 3089): ("귀가는 이제 충분히 강해졌습니다\n이제 주종 관계를 끝내고 대등한 동맹을 맺어\n각자의 발전을 위해 함께 싸웁시다",),
    (6, 3093): ("귀가는 이제 충분히 강해졌습니다\n이제 주종 관계를 끝내고 대등한 동맹을 맺어\n각자의 발전을 위해 함께 싸웁시다",),
    (6, 3097): ("전봉할 성을 선택하십시오.",),
    (6, 3098): ("전봉 방식을 선택하십시오.",),
    (6, 3099): ("이동시킬 무장을 선택하십시오",),
    (6, 3100): ("다른 성을 선택하십시오",),
    (6, 3101): ("성 사이를 이동할 무장을 선택하십시오",),
    (6, 3102): ("성주에게 지행으로 줄 군의 수를 정하십시오.",),
    (6, 3103): ("이동할 곳:",),
    (6, 3104): ("이동을 시작합니다",),
    (6, 3105): ("무장을 이동시킬 필요는 없다고 생각합니다",),
    (6, 3106): (": 입성한 곳:", "."),
    (6, 3107): ("명. 포함 무장:", ". 입성한 곳:", "."),
    (6, 3108): ("아, 더는 참을 수 없다!\n섬기지 않을 주군:", ". 이제 더는 섬길 수 없다!"),
    (6, 3109): ("아, 더는 참을 수 없다!\n섬기지 않을 주군:", ". 이제 더는 섬길 수 없다!"),
    (6, 3110): (": 출분한 곳:", "."),
    (6, 3111): ("의 당주:", ". 출분했습니다."),
    (6, 3112): (": 출분했습니다.",),
    (6, 3113): ("귀하와의 맹약은\n곧 한낱 종잇장이 될 것입니다……\n이제 관계를 끊겠습니다",),
    (6, 3116): ("앞으로도\n계속 힘쓰겠습니다",),
    (6, 3117): ("괜찮은 교섭이었던 것 같습니다",),
    (6, 3118): ("끈질기게 교섭한 보람이 있었습니다",),
    (6, 3122): ("이번 교섭도 나쁘지 않았습니다",),
    (6, 3128): ("좋다\n이번 전투는 여기서 끝내자",),
    (6, 3129): ("좋습니다\n정전을 받아들이겠습니다",),
    (6, 3130): ("좋다\n일단 전투를 멈추자",),
    (6, 3134): ("어쩔 수 없군요\n일단 군사를 거둡시다",),
    (6, 3140): ("전투는 여기서 끝입니다……\n약속을 어기지 마십시오",),
    (6, 3141): ("당분간 정전입니다\n다행이군요……",),
    (6, 3142): ("전투는 잠시 끝났습니다\n잘 받아들여 주셨습니다",),
    (6, 3146): ("전투는 여기서 끝입니다\n잊지 마십시오",),
    (6, 3152): ("가문을 지키기 위한 결단입니다\n부끄러워할 일은 없습니다……",),
    (6, 3153): ("이 또한 가문을 지키기 위해서입니다……\n잘 부탁드립니다",),
    (6, 3154): ("이 또한 가문을 지키기 위해서입니다……\n잘 부탁드립니다",),
    (6, 3158): ("이 또한 가문을 지키기 위해서입니다……\n잘 부탁드립니다",),
    (6, 3164): ("종속 의식은 받아들이겠다\n따를 세력:", ". 그 휘하에서 가명을 지켜라"),
    (6, 3165): ("따르겠다면 받아들이겠습니다\n", ": 귀가를 보호할 것입니다"),
    (6, 3166): ("따르겠다면 받아들이겠다\n", ": 그대를 보호하겠다"),
    (6, 3170): ("따르겠다면 받아들이겠습니다\n", ": 그대를 보호하겠습니다"),
    (6, 3176): ("좋다\n맹약 갱신에 이의는 없다",),
    (6, 3177): ("알겠습니다\n맹약 갱신에 이의는 없습니다",),
    (6, 3178): ("알겠다\n앞으로도 우리는 맹우다",),
    (6, 3182): ("좋습니다\n저도 계속 맹우로 남고 싶었습니다",),
    (6, 3188): ("우리 동맹은 확고해졌습니다\n앞으로도 잘 부탁드립니다",),
    (6, 3189): ("우리 동맹은 반석처럼 굳건합니다\n앞으로도 잘 부탁드립니다",),
    (6, 3190): ("우리 동맹은 마침내 반석처럼 굳건해졌습니다\n앞으로도 잘 부탁드립니다",),
    (6, 3194): ("동맹의 우의가 반석처럼 굳어졌습니다\n앞으로도 잘 부탁드립니다",),
    (6, 3200): ("동맹 제안을 받아들이겠다\n당분간은 동맹을 맺어 두자\n그 뒤의 일은 그때 생각하겠다",),
    (6, 3201): ("동맹 제안을 받아들이겠습니다\n당분간은 손을 잡읍시다\n그 뒤의 일은 그때 이야기하지요",),
    (6, 3202): ("맹약을 받아들이겠다\n당분간은 함께 나아가자\n그 뒤의 일은 그때 생각하겠다",),
    (6, 3206): ("동맹 제안을 받아들이겠습니다\n당분간은 손을 잡읍시다\n그 뒤의 일은 그때 이야기하지요",),
    (6, 3212): ("당분간 우리는 맹우다\n적으로는 까다롭지만\n아군이라면 든든하겠군",),
    (6, 3213): ("당분간 우리는 맹우입니다\n지난 원한은 이제 잊읍시다",),
    (6, 3214): ("당분간 우리는 맹우다\n서로의 옛 원한은 잊도록 하자",),
    (6, 3218): ("당분간 우리는 맹우입니다\n지난 다툼과 불쾌함은 잊어 주십시오",),
    (6, 3224): ("혼인 제안을 받아들이겠다\n두 가문이 오래도록 인연을 이어 가길 바란다",),
    (6, 3225): ("혼인 제안을 받아들이겠습니다\n이제부터 두 가문은 친척입니다\n화목하게 난세를 헤쳐 갑시다",),
    (6, 3226): ("혼인 제안을 감사히 받아들이겠다\n두 가문의 인연이 영원하기를 바란다",),
    (6, 3230): ("혼인 제안을 받아들이겠습니다\n이제부터 우리는 한집안입니다\n무슨 일이든 서로 돕도록 합시다",),
    (6, 3236): ("두 분의 혼인을 진심으로 축하합니다!\n백년해로하시길 바랍니다",),
    (6, 3237): ("이제 우리는…… 친척이군요\n좋은 인연이 오래 이어지길 바랍니다",),
    (6, 3238): ("이제 우리는 친척이다\n좋은 인연이 오래 이어지길 바란다",),
    (6, 3242): ("이제 우리는 친척입니다\n함께 난세를 살아남읍시다",),
    (6, 3248): ("믿을 수 없군…… 우리와 단교하다니 어리석다",),
    (6, 3249): ("그럴 수가!\n우리와 단교하겠다고!",),
    (6, 3250): ("뭐라고…… 우리와 단교하겠다는 건가?",),
    (6, 3254): ("갑자기 단교하다니……",),
    (6, 3260): ("알겠습니다\n공략 대상:",),
    (6, 3261): ("알겠습니다\n공략할 대상:", ". 공격하겠습니다"),
    (6, 3262): ("알겠다\n함락할 대상:", ". 함락시키겠다"),
    (6, 3266): ("알겠습니다\n공략할 대상:", ". 이 정도는 손쉽습니다"),
    (6, 3272): ("알겠다\n전력을 다해 지킬 곳:",),
    (6, 3273): ("알겠습니다\n본가의 병력으로 지킬 곳:", ". 방어하겠습니다"),
    (6, 3274): ("알겠다\n", ": 우리가 지키겠다"),
    (6, 3278): ("어려울 때일수록 서로 도와야 합니다……\n방어할 곳:", ". 방어에 나서겠습니다"),
    (6, 3284): ("무용으로 이름난 귀가라면\n공략할 곳:", ". 어렵지 않을 것입니다"),
    (6, 3285): (": 공략을\n반드시 성공시켜 주십시오",),
    (6, 3286): (": 공략을\n부탁드립니다",),
    (6, 3290): ("혼내 줄 상대:", ".\n본때를 보여 주십시오"),
    (6, 3296): (": 우리의 요충지입니다\n반드시 지켜 주십시오",),
    (6, 3297): (": 방어를\n반드시 완수해 주십시오",),
    (6, 3298): (": 요지입니다\n반드시 지켜 주십시오",),
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
    if selected[0] != (6, 3050, 3) or selected[-1] != (6, 3298, 0):
        raise ValueError("translation batch boundaries changed")
    if len(selected) != 150 or len(keys) != 99:
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
    if selected[-1] != (6, 3298, 0) or NEXT_COORDINATE not in sc_literals:
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
