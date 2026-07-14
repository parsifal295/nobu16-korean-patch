#!/usr/bin/env python3
"""Build source-free PK/SC msggame Korean translation batch 7."""

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


BATCH_ID = "msggame_pk_system_messages_b06r0560_0947.v0.7"
OVERLAY_NAME = "msggame_ko_system_messages_b06r0560_0947.v0.7.json"
EVIDENCE_NAME = "translation_alignment_evidence.v0.7.json"
REVIEW_NAME = "translation_review_index.v0.7.json"
VALIDATION_NAME = "translation_validation.v0.7.json"
RESOURCE = previous.RESOURCE
LANGUAGES = previous.LANGUAGES
SOURCE_PATHS = previous.SOURCE_PATHS
NEXT_COORDINATE = (6, 948, 0)


TRANSLATIONS: dict[tuple[int, int], tuple[str | None, ...]] = {
    (6, 560): ("내 헌책은 들을 생각도 없나……\n참으로 가볍게 보는군",),
    (6, 561): ("내 진언을 하루라도 빨리\n살펴 주었으면 좋겠는데",),
    (6, 562): ("이번에도 내 구신은\n들어 주지 않는 건가……",),
    (6, 563): ("구신에 아무 소식이 없군……",),
    (6, 564): ("진언은 필요 없다……\n그런 뜻인가?",),
    (6, 571): ("주군께 다시 알려야겠군\n내가 구신 중이라고……",),
    (6, 572): ("그렇게 자신 있게 구신했건만\n내버려 두다니……",),
    (6, 583): ("라면\n공략은 반드시 성공할 것이다.",),
    (6, 584): ("공략", "\n아군을 믿어 보자"),
    (6, 585): ("라면\n분명 예상대로 되겠지……",),
    (6, 586): ("공략 대상:", "\n부디 성공하기를"),
    (6, 587): ("에게\n저 성을 함락할 힘이 있을까……",),
    (6, 588): ("인가……\n함락할 수 있으면 좋겠군",),
    (6, 595): ("라면\n분명 문제없을 겁니다",),
    (6, 596): ("공격 대상:", "의 승리를\n반드시 빕니다."),
    (6, 607): ("의 활약이라면\n반드시 무공을 세울 것이다",),
    (6, 608): ("무운을 빈다:", "\n승리가 함께하기를"),
    (6, 609): ("의 전투는\n분명 예상대로 되겠지……",),
    (6, 610): ("작전 대상:", "\n내 계산대로 움직인다면……"),
    (6, 611): ("!\n전력을 다하라",),
    (6, 612): ("!\n온 힘을 쏟아라",),
    (6, 619): ("\n반드시 이겨!",),
    (6, 620): ("\n부디, 꼭 이겨!",),
    (6, 631): ("가증스러운 상대:", "\n본가를 공격 대상으로 삼다니"),
    (6, 632): ("교전 상대:", "와의 싸움이\n눈앞에 닥쳤군"),
    (6, 633): ("의 표적은\n본가인 듯합니다",),
    (6, 634): ("……역시\n본가를 공격하려는 건가",),
    (6, 635): ("수상한 상대:", "……\n불온한 움직임을 보이는군"),
    (6, 636): ("의 군세가\n금방이라도 쳐들어오겠군",),
    (6, 643): ("의 움직임이\n수상합니다……조심하십시오!",),
    (6, 644): ("교전 상대:", "와의 싸움은\n피할 수 없을 듯합니다……"),
    (6, 655): ("저 마을의 제방도……\n많이 낡았군……",),
    (6, 656): ("축제를 허락했다간\n또 소란과 싸움이 나겠군……",),
    (6, 657): ("내 영민들이\n좀 더 편히 살게 하고 싶군……",),
    (6, 658): ("내가 다스리는 곳이니\n내 지행지는 평온하군",),
    (6, 659): ("우선 마을에서\n병사를 내게 해야겠군",),
    (6, 660): ("영민들이 나를\n두려워하는군……",),
    (6, 667): ("지행지를 더 낫게 만들\n좋은 방도가 없을까",),
    (6, 668): ("아아, 지행지 따위\n될 대로 되라지!",),
    (6, 679): ("후후……이 정도 일로\n바쁘다고 할 수는 없지",),
    (6, 680): ("남보다 두 배는 힘써야\n두각을 드러낼 수 있다",),
    (6, 681): ("이야……어제는 그래도\n잠깐이나마 잤습니다",),
    (6, 682): ("후우……격무도 결국\n기대받는다는 뜻인가",),
    (6, 683): ("이런, 칼을 손질할\n시간조차 없을 정도로군",),
    (6, 684): ("한가해지면\n검술 수련이나 할까",),
    (6, 691): ("후후……너무 일해서\n조금 야위었나",),
    (6, 692): ("아아……어깨가 뻐근해\n누가 좀 주물러 줘!",),
    (6, 703): ("자, 이곳의 방식을\n배워 보도록 할까",),
    (6, 704): ("낭비가 많아 보이지만……\n아직 의견을 낼 때는 아니군",),
    (6, 705): ("고참들이 시끄러워 보이니\n얌전히 있어야겠군",),
    (6, 706): ("역시 조금 긴장되네요\n아주 조금……이지만",),
    (6, 707): ("신참이라고\n얕보게 두진 않겠다",),
    (6, 708): ("고참 녀석들……\n다가오면 베겠다!",),
    (6, 715): ("하루빨리 평정중 여러분께\n인정받고 싶군",),
    (6, 716): ("평정중의 일원이니\n힘껏 해내야지",),
    (6, 727): ("동석 상대:", "라니,\n감히 나와 같은 자리에 앉다니"),
    (6, 728): ("평정 참여자:", "라……\n주군은 무슨 생각이신가"),
    (6, 729): ("……\n건방져 보이는 자군요",),
    (6, 730): ("……역시\n긴장하고 있군요",),
    (6, 731): ("마음에 들지 않는 얼굴이 있군\n누구라고는 안 하겠지만……",),
    (6, 732): ("……\n엄하게 지도해야겠군",),
    (6, 739): ("\n설마 이 자리에 오다니.",),
    (6, 740): ("이 자리에 어울리지 않는 자:\n", "."),
    (6, 751): ("주군이 지나치게 강경하면\n가신들의 사기가 꺾이지……",),
    (6, 752): ("이 참상은……\n이제 되돌릴 수 없나",),
    (6, 753): ("간언을 듣지 않는 주군 아래선\n어떤 양책도 무의미하지……",),
    (6, 754): ("이런 꼴이라면\n어떤 양책도 무의미하군……",),
    (6, 755): ("우리 가신들은 그저\n창을 대신하는 도구일 뿐인가",),
    (6, 756): ("헛된 발버둥은 그만두고\n마지막만은 깨끗하게……",),
    (6, 763): ("조금만 더 모두의 의견에\n귀 기울여 주신다면……",),
    (6, 764): ("이렇게 되어 버렸으니\n이제는……",),
    (6, 775): ("가신이 늘었다 해도\n규율은 규율이다",),
    (6, 776): ("본가의 기세를\n막을 자가 어디 있겠는가",),
    (6, 777): ("세력이 커졌기에\n쓸 수 있는 수단도 있지",),
    (6, 778): ("본가의 확대도\n내 예상대로군……",),
    (6, 779): ("견마지로도 마다하지 않고\n본가를 위해 힘쓰겠다",),
    (6, 780): ("우리의 기세는 드높다!\n도약의 명을 내려 주십시오",),
    (6, 787): ("본가의 일거수일투족이\n천하를 뒤흔들 것입니다",),
    (6, 788): ("본가의 규모라면\n반드시 해낼 수 있는 일이 있겠지",),
    (6, 799): ("오래 머물 곳은\n아닌 듯하군",),
    (6, 800): ("나를 품을 만한\n그릇은 아닌가 보군……",),
    (6, 801): ("이 가문의 물은\n내게 맞지 않는 듯하군……",),
    (6, 802): ("내 헌책을 바칠 주군은\n따로 있는 듯하군……",),
    (6, 803): ("인내에도 한계가 있다……",),
    (6, 804): ("분을 풀 길이 없군……",),
    (6, 811): ("가신들의 불만은\n전혀 개의치 않으십니까……",),
    (6, 812): ("가신들의 불만을\n이토록 내버려 두시다니……",),
    (6, 823): ("동석 상대:", "인가……\n모두 본가를 위해서다"),
    (6, 824): ("동료:", "……\n인정 못 할 만큼 옹졸하진 않다"),
    (6, 825): ("뒤처리 대상:", "\n그자의 실수까지 수습하긴 싫군요"),
    (6, 826): ("평정 참여:", "……\n그자를 본가에 둘 필요가 있나"),
    (6, 827): ("따위는\n안중에도 없다",),
    (6, 828): ("무례한 자:", "\n자리도 분간하지 못하는군"),
    (6, 835): ("협력이라……\n상대:", "와도 힘을 합쳐야 한다니"),
    (6, 836): ("의 얼굴이라……\n솔직히 보고 싶지도 않군",),
    (6, 847): ("상처가 아프군……",),
    (6, 848): ("이런 날에는\n몸이 쑤시는군……",),
    (6, 849): ("상처가 좀 아프네요……",),
    (6, 850): ("상처가 나을 때까지\n느긋하게 쉬고 싶군……",),
    (6, 851): ("상처가 아프군……",),
    (6, 852): ("이 정도 상처야\n핥으면 낫는다……",),
    (6, 859): ("상처가……아픕니다……",),
    (6, 860): ("이깟 상처로\n약한 소리는 할 수 없습니다……",),
    (6, 871): ("머리가 어질어질하군……",),
    (6, 872): ("나도 여기까지인가……",),
    (6, 873): ("아아……몸 상태가 좋지 않군……",),
    (6, 874): ("이제 죽을 날이\n가까운 모양이군……",),
    (6, 875): ("한기가 드는군……",),
    (6, 876): ("평생을 전장에서\n살았건만……",),
    (6, 883): ("열이 내리지 않네요……",),
    (6, 884): ("이별할 날이\n가까운지도 모르겠군……",),
    (6, 895): ("어떤 방침이 되려나",),
    (6, 896): ("결단은 빠를수록 좋다",),
    (6, 897): ("새로운 방침인가",),
    (6, 898): ("깊이 생각해 주시면 좋겠군",),
    (6, 899): ("방침이 정해지는 건가",),
    (6, 900): ("현 상황을 타개할 방법이 있는가",),
    (6, 907): ("어떤 지침이 될까요",),
    (6, 908): ("마침내 결단하시는군요",),
    (6, 919): ("정책은 나라 세우기의 기초지.",),
    (6, 920): ("정책은 본가의 지침이니 소홀히 할 수 없다.",),
    (6, 921): ("정책은 신중히 정해야 한다.",),
    (6, 922): ("정책에 따라\n전략도 달라지겠지…… ",),
    (6, 923): ("정책을 발령하시는 건가?",),
    (6, 924): ("그 정책을\n발령해 주신다면……",),
    (6, 931): ("정책을 발령하는 건가?",),
    (6, 932): ("백성의 이해를 얻을\n좋은 정책을 부탁드립니다……",),
    (6, 943): ("군량 재고를\n확인해 봅시다",),
    (6, 944): ("금전과 군량, 어느 쪽도 빠뜨릴 수 없지……",),
    (6, 945): ("남는 군량은\n파는 것도 방법입니다",),
    (6, 946): ("걱정 없을 만큼 많은 쌀에\n파묻혀 보고 싶군",),
    (6, 947): ("상인을 부릅시다",),
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
    if selected[0] != (6, 560, 0) or selected[-1] != (6, 947, 0):
        raise ValueError("translation batch boundaries changed")
    if len(selected) != 150 or len(keys) != 132:
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
                "selected_sc_literal_ids": list(range(len(replacements))),
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
                raise ValueError(f"unexpected skipped literal at {key}")
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
    if selected[-1] != (6, 947, 0) or NEXT_COORDINATE not in sc_literals:
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
