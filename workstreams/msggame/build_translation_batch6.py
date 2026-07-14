#!/usr/bin/env python3
"""Build source-free PK/SC msggame Korean translation batch 6."""

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


BATCH_ID = "msggame_pk_system_messages_b04r0076_b06r0559.v0.6"
OVERLAY_NAME = "msggame_ko_system_messages_b04r0076_b06r0559.v0.6.json"
EVIDENCE_NAME = "translation_alignment_evidence.v0.6.json"
REVIEW_NAME = "translation_review_index.v0.6.json"
VALIDATION_NAME = "translation_validation.v0.6.json"
RESOURCE = previous.RESOURCE
LANGUAGES = previous.LANGUAGES
SOURCE_PATHS = previous.SOURCE_PATHS
NEXT_COORDINATE = (6, 560, 0)


TRANSLATIONS: dict[tuple[int, int], tuple[str | None, ...]] = {
    (4, 76): ("외교 대상 세력을 선택하십시오",),
    (4, 77): ("종속 중에는 종주 세력 외의 세력과 외교할 수 없습니다",),
    (4, 78): ("다른 가문에 종속된 세력과 외교할 수 없습니다",),
    (4, 79): ("신용 설정",),
    (4, 80): ("외교 관계를 동맹으로 변경",),
    (4, 81): ("이미 동맹을 맺었습니다",),
    (4, 82): ("멀리 떨어진 세력과는 동맹을 맺을 수 없습니다",),
    (4, 83): ("종속:", "→"),
    (4, 84): ("대상 세력 및 그 종속 세력과 인접하지 않았습니다",),
    (4, 85): ("이미 종속되어 있습니다",),
    (4, 86): ("외교 관계를 정전으로 변경",),
    (4, 87): ("외교 관계 파기",),
    (4, 88): ("파기할 외교 관계가 없습니다",),
    (4, 89): ("편집할 성을 선택하십시오",),
    (4, 90): ("병력 설정",),
    (4, 91): ("내구 설정",),
    (4, 92): ("성하 시설 설정",),
    (4, 94): ("군량 설정",),
    (4, 95): ("병력 설정",),
    (4, 96): ("기마 LV 설정",),
    (4, 97): ("철포 LV 설정",),
    (4, 98): ("휴대 군량 설정",),
    (4, 99): ("얼굴 CG 설정",),
    (4, 100): ("음성 설정",),
    (4, 101): ("소속 세력 설정",),
    (4, 102): (
        "신분을 올립니다.\n"
        "아시가루 대장은 영주, 사무라이 대장은 성주, 가로는 군단장으로 임명할 수 있습니다.",
    ),
    (4, 103): ("더 이상 신분을 올릴 수 없습니다",),
    (4, 104): ("다이묘는 변경할 수 없습니다",),
    (4, 106): ("직위 취임 조건을 충족하지 못했습니다",),
    (4, 107): ("변경 대상:", "의 장악 상태"),
    (4, 108): ("상위 취락 장악",),
    (4, 109): ("장악할 수 있는 상위 취락이 없습니다",),
    (4, 110): ("이미 장악했습니다",),
    (4, 111): ("출진 중인 부대가 없습니다",),
    (4, 112): ("게임 중 편집하면 업적을 획득할 수 없습니다.\n계속하시겠습니까?",),
    (4, 113): ("게임 중 편집하면 트로피를 획득할 수 없습니다.\n계속하시겠습니까?",),
    (4, 114): ("더 이상 외교 관계를 맺을 수 없습니다",),
    (4, 115): ("멀리 떨어진 세력과는 외교할 수 없습니다",),
    (4, 116): ("보급 군량 설정",),
    (4, 117): ("방위 병력 설정",),
    (4, 118): ("각종 데이터 편집",),
    (4, 119): ("각종 데이터 편집\n게임 중 편집하면 업적을 획득할 수 없습니다.",),
    (4, 120): ("각종 데이터 편집\n게임 중 편집하면 트로피를 획득할 수 없습니다",),
    (4, 122): (
        "【확인 메시지】\n각 명령 실행 시 표시되는 확인 메시지를 설정합니다\n\n"
        "[사용자 설정]\n“다음부터 표시하지 않음”으로 설정한 메시지 외에는 모두 표시\n\n"
        "[모두 표시]\n모든 확인 메시지 표시",
    ),
    (4, 123): (
        "【난이도】\n게임 난이도를 설정합니다\n"
        "[입문]\n느긋하게 즐기려는 플레이어에게 적합\n"
        "[초급]\n적당한 난이도를 즐기려는 플레이어에게 적합\n"
        "[중급]\n게임에 익숙한 플레이어에게 적합\n"
        "[상급]\n도전을 원하는 플레이어에게 적합\n"
        "[최상급]\n더 높은 경지를 원하는 플레이어에게 적합\n"
        "[사용자 설정]\n취향에 맞는 난이도로 즐기려는 플레이어에게 적합",
    ),
    (4, 124): ("《노부나가의 야망·신생 파워업키트》",),
    (4, 125): (
        "《노부나가의 야망·신생 파워업키트》 발매!\n"
        "여러 추가 요소 중 일부를 소개합니다!\n"
        "한층 진화한 “군신일체의 전국 체험”을 즐겨 보십시오.\n\n"
        "·모든 성이 전용 전장이 되는 시리즈 최대 규모의 “공성전”\n"
        "·“군단 전략”과 “평정중”의 새로운 전략, 무장이 제안하는 교섭 “직담”\n"
        "·휴대 군량 보급 거점 등 성에 역할을 부여하는 “성 역할”\n"
        "·자유로운 편집 기능 “국가 변경”“신규 세력 생성”“실존 무장 편집”\n"
        "·“자동 지행”“이벤트 전투”, 새로운 시나리오와 정책 등 풍부한 콘텐츠",
    ),
    (6, 279): ("설정한 명령을 취소합니다\n계속하시겠습니까?",),
    (6, 280): ("적에게 노려지고 있습니다.",),
    (6, 285): ("무슨 이야기를\n하는 걸까?",),
    (6, 286): ("어려운 일에는 시간을 들여\n도전해야 한다",),
    (6, 287): ("나와 상관없는\n이야기뿐이군",),
    (6, 288): ("충분히 검토해\n보는 것이 좋겠습니다",),
    (6, 289): ("지루한 이야기뿐이군",),
    (6, 290): ("생각할 시간이 필요하군",),
    (6, 297): ("흠,\n무슨 이야기 중이지?",),
    (6, 298): ("잠시 쉬어 가자",),
    (6, 309): ("모두를 소집한 건가",),
    (6, 310): ("낯선 얼굴이 있군.",),
    (6, 311): ("평정 시간이 되었나?",),
    (6, 312): ("언제 와도\n훌륭한 성이군",),
    (6, 313): ("급한 용건인가?",),
    (6, 314): ("여기는\n마치 내 집 같군",),
    (6, 321): ("갑자기 불러내다니……\n무슨 일일까?",),
    (6, 322): ("그분도\n오실까?",),
    (6, 333): ("그래야지",),
    (6, 334): ("우선\n실행해 보자",),
    (6, 335): ("역시\n혜안이십니다",),
    (6, 336): ("좋다고 봅니다",),
    (6, 337): ("내게 맡겨라!",),
    (6, 338): ("이의는 없소",),
    (6, 345): ("미력하나마\n돕겠습니다",),
    (6, 346): ("훌륭한 생각입니다",),
    (6, 357): ("돈을 쓰는 법을 보면,\n그 사람의 그릇을 알 수 있지.",),
    (6, 358): ("영지의 일을\n잘 생각하고 계시는군요.",),
    (6, 359): ("이렇게 쓰는 것이군요?\n알겠습니다.",),
    (6, 360): ("훗……\n역시 그렇습니까?",),
    (6, 361): ("그렇군,\n뜻대로 하게.",),
    (6, 362): ("지출이 꽤 크겠군.",),
    (6, 369): ("정책 문안을\n정리하겠습니다.",),
    (6, 370): ("본가의 정책은\n이것이 최선일까……",),
    (6, 381): ("이번 거래는\n좋은 판단이었습니다",),
    (6, 382): ("상인에게도 이익을 줘야\n장사가 성립하는 법",),
    (6, 383): ("절반 이상의 성과를\n거둔 거래로 보이는군.",),
    (6, 384): ("이번 거래는\n예상한 바입니다.",),
    (6, 385): ("거래하느라 수고했네.",),
    (6, 386): ("숨 막히는 공방이군……\n상인도 제법이야.",),
    (6, 393): ("좋은 거래를\n성사시킨 듯하군요.",),
    (6, 394): ("나도……\n뭔가 사고 싶었는데……",),
    (6, 405): ("흠…… 싸울 준비를 마쳤나?",),
    (6, 406): ("충분히\n생각하셨군요.",),
    (6, 407): ("그렇군\n이런 전술인가",),
    (6, 408): ("역시 이런 식으로\n사람을 움직였군요.",),
    (6, 409): ("수비든 공격이든\n성을 맡은 장수에게 달렸지",),
    (6, 410): ("호오, 절묘한 배치로군",),
    (6, 417): ("장수 배치를 바꾼다……\n전쟁인가?",),
    (6, 418): ("이런 배치로\n맞서려는 건가?",),
    (6, 429): ("신상필벌은 무가가\n서 있는 근본이다",),
    (6, 430): ("그리 눈에 띄는 일은\n하지 않는 편이 좋겠군……",),
    (6, 431): ("그자는\n충성을 다하겠지",),
    (6, 432): ("역시 가보를\n빼앗겼군",),
    (6, 433): ("부러운 일이군.",),
    (6, 434): ("신분에 맞지 않는 명품을\n가지고 있었으니 말이야.",),
    (6, 441): ("훌륭히 일하다 보면\n언젠가는 나도……",),
    (6, 442): ("상을 받아도 마냥\n기뻐할 수는 없군……",),
    (6, 453): ("오래도록 행복하기를",),
    (6, 454): ("좋은 인연이 되기를",),
    (6, 455): ("축하합니다\n오래도록 행복하십시오.",),
    (6, 456): ("역시 두 사람은\n맺어질 운명이었군",),
    (6, 457): ("경사로다",),
    (6, 458): ("그 두 사람이\n부부가 되다니",),
    (6, 465): ("멋진 일이야……",),
    (6, 466): ("진심으로\n축하합니다!",),
    (6, 477): ("새 당주를\n뒷받침해야겠군.",),
    (6, 478): ("참으로 어려운\n결단을 내리셨군……",),
    (6, 479): ("본가를 둘러싼 상황도\n달라지겠군……",),
    (6, 480): ("역시 은거할 때는\n지금이었나",),
    (6, 481): ("선대 당주의\n훌륭한 물러남이군",),
    (6, 482): ("이 시기에\n은거하시다니",),
    (6, 489): ("당주가 바뀌었으니\n새 마음으로 시작해야겠군",),
    (6, 490): ("이것이\n세상사의 무상함인가?",),
    (6, 501): ("가문을 통솔하려면,\n어쩔 수 없는 일이지.",),
    (6, 502): ("이것도\n어쩔 수 없는 조치다",),
    (6, 503): ("이런 처분도\n때로는 필요합니다",),
    (6, 504): ("역시 그자가\n추방되었군요",),
    (6, 505): ("어쩔 수 없지",),
    (6, 506): ("이런, 안타깝군……",),
    (6, 513): ("가엾지만,\n어쩔 수 없지",),
    (6, 514): ("당연한 응보다",),
    (6, 525): ("군단은 운용이 중요하다.",),
    (6, 526): ("군단을 어떻게 다루느냐가\n본가의 미래를 정한다……",),
    (6, 527): ("상황을\n잘 살피셨군요",),
    (6, 528): ("역시 군단을\n조정하셨군요.",),
    (6, 529): ("어디에 있든\n온 힘을 다할 뿐",),
    (6, 530): ("참으로 훌륭한\n솜씨로군요.",),
    (6, 537): ("군단 변경은 마음에 들 때까지\n자유롭게 하십시오",),
    (6, 538): ("군단을 조정할 때면,\n문득 진지한 눈빛이 되시는군요.",),
    (6, 545): ("당연하지.",),
    (6, 546): ("다음에도 힘내자.",),
    (6, 547): ("호오,\n그렇게 나오는군.",),
    (6, 548): ("어떻게든\n공훈을 세워야 한다.",),
    (6, 549): ("어떻게 해야\n주군의 눈에 들 수 있을까?",),
    (6, 550): ("무슨 일이든 신뢰가 있어야 하지.",),
    (6, 551): ("두루 신경을 쓰는 것도\n중요한 일이다.",),
    (6, 552): ("주군께서는\n그렇게 생각하시는가?",),
    (6, 553): ("조정과의 관계도\n소홀히 할 수 없다.",),
    (6, 554): ("사전 교섭을\n게을리해서는 안 된다.",),
    (6, 559): ("자, 내 진언을\n받아들여 주실까?",),
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
    if selected[0] != (4, 76, 0) or selected[-1] != (6, 559, 0):
        raise ValueError("translation batch boundaries changed")
    if len(selected) != 150 or len(keys) != 148:
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
    if selected[-1] != (6, 559, 0) or NEXT_COORDINATE not in sc_literals:
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
