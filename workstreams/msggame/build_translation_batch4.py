#!/usr/bin/env python3
"""Build source-free PK/SC msggame Korean translation batch 4."""

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


BATCH_ID = "msggame_pk_system_messages_b02r0566_0665.v0.4"
OVERLAY_NAME = "msggame_ko_system_messages_b02r0566_0665.v0.4.json"
EVIDENCE_NAME = "translation_alignment_evidence.v0.4.json"
REVIEW_NAME = "translation_review_index.v0.4.json"
VALIDATION_NAME = "translation_validation.v0.4.json"
RESOURCE = previous.RESOURCE
LANGUAGES = previous.LANGUAGES
SOURCE_PATHS = previous.SOURCE_PATHS
NEXT_COORDINATE = (2, 666, 0)


# None marks a visible but non-linguistic level-format fragment retained from
# the stock resource. Public artifacts contain only coordinates, source hashes,
# project-authored Korean, and the skip reason.
TRANSLATIONS: dict[tuple[int, int], tuple[str | None, ...]] = {
    (2, 566): ("열세야말로\n내 계책을 펼칠 무대다!",),
    (2, 567): ("적은 바로", "!\n여기서 무찔러라!"),
    (2, 568): ("나무아미타불……\n불적에게 벌을 내리리라!",),
    (2, 569): ("나타났는가, 군신이여……\n내 지휘로 악연을 끊겠다!",),
    (2, 570): ("왔는가, 숙적이여!\n이제 자웅을 겨루자!",),
    (2, 571): ("무운을 빌 대상:", "의 무운을 빌겠습니다."),
    (2, 572): ("일부러 배웅해 줘 고맙다.\n좋은 소식을 기다려라.",),
    (2, 573): ("무운을\n빌고 있겠습니다.",),
    (2, 574): ("걱정 마라!\n", "은(는) 앞으로도 계속 출세할 테니!"),
    (2, 575): ("친애하는", "이여, 잘 있어라……"),
    (2, 576): (
        "안심하십시오……\n본가의 앞날을 지켜볼 자:",
        "\n이(가) 끝까지 지켜보겠습니다.",
    ),
    (2, 577): ("친애하는", "이여, 잘 있어라……"),
    (2, 578): ("오합지졸은 두렵지 않다.\n천운의 주인:", "!"),
    (2, 579): ("이 정도 열세는", "이(가) 제압한다!\n출세의 발판으로 삼겠다!"),
    (2, 580): ("고요한 세상을 위해……\n이 주베에, 손을 더럽히는 것도 마다하지 않겠다.",),
    (2, 581): ("실컷 맛보아라……\n살무사의 계략을.",),
    (2, 582): ("적의 수가 많다!\n미카와 무사의 기개를 보일 때다!",),
    (2, 583): ("적도 아군도 똑똑히 보아라!\n이 독안룡이 비상하는 모습을!",),
    (2, 584): ("우리 결사대 아카조나에가……\n열세를 뒤집는다!",),
    (2, 585): ("수의 차이는 지략으로 뒤집는다.\n이것이", "의 전투다!"),
    (2, 586): ("명백한 열세로군.\n어떻게 버텨 낼 것인가……!",),
    (2, 587): ("죽고자 싸우면 살고, 살고자 싸우면 죽는다……\n전군, 목숨을 내게 맡겨라!",),
    (2, 588): ("수로 우리를 누를 수 있다 생각했나?\n", "도 얕보였군."),
    (2, 589): ("허허, 병력이 많아 고생이겠군.\n자…… 어떤 수를 써 볼까.",),
    (2, 590): ("대군을 상대할 땐 필사의 각오를 다져라!\n천하에 우리의 무용을 보여 주자.",),
    (2, 591): ("적의 수가 더 많은가.\n한 수라도 틀리지 않도록 신중한 계책으로 이기자.",),
    (2, 592): ("대적 따위 두렵지 않다.\n어린 도깨비의 창이 꿰뚫지 못할 것은 없다.",),
    (2, 593): ("붉은 귀신의 병사는 수에 기대지 않는다.\n자, 혈로를 열어라.",),
    (2, 594): (
        "『돌아갈 수 없는 흉일』은 사실이었나.\n"
        "……물론 강적을 모조리 쓰러뜨리고,\n출세하겠다는 뜻이다!",
    ),
    (2, 595): ("모두 당황하지 마라.\n내 눈엔 호랑이보다 강한 적은 보이지 않는다.",),
    (2, 596): ("전쟁은 병력의 많고 적음으로 정해지지 않는다.\n모두 하나 되어 대군을 뒤집자.",),
    (2, 597): ("적은 마왕인가……\n이 한판으로 아버지를 뛰어넘겠다!",),
    (2, 598): ("적을 얼간이라 여기지 마라.\n우리는 우리 방식으로 이길 뿐이다.",),
    (2, 599): ("얼간이인가, 걸물인가……\n직접 가려 보는 것도 재미있겠군.",),
    (2, 600): ("천하포무라니 불손하기 짝이 없다!\n비사문천을 대신해 토벌하겠다!",),
    (2, 601): ("이 또한 난세의 이치……\n의형님, 각오하십시오!",),
    (2, 602): ("감히", "에게 활을 겨누다니 가소롭다.\n결국 벼락출세한 자일 뿐인가!"),
    (2, 603): ("수많은 굴욕을 잊을 수 없다……\n용서란 없다. 토벌할 뿐이다!",),
    (2, 604): ("왜 그러느냐, 애송이.\n새 다구가 탐나면 내 목을 노려 보아라.",),
    (2, 605): ("큰아버님, 무례를 용서하십시오!\n이 독안룡에게 길을 내주십시오!",),
    (2, 606): ("적이 가이의 호랑이라 해도,\n", "의 깃발 아래 패배는 용납하지 않는다."),
    (2, 607): ("적은 가이의 호랑이인가……\n무, 무사로서 전율이 멎지 않는군!",),
    (2, 608): ("늙은 호랑이의 실력이 어느 정도인가!\n새로운 전투를 보여 주마!",),
    (2, 609): ("적이 군신이라면 우리는 마왕이다.\n앞을 막는 자는 모조리 쓰러뜨려라!",),
    (2, 610): ("미카와 무사여, 맞서는 기개는 훌륭하다.\n가이의 호랑이가 싸우는 법을 보여 주마.",),
    (2, 611): ("미카와의 너구리도 제법 살이 올랐군……\n모두 마음 단단히 먹어라!",),
    (2, 612): ("불구대천의 원수와 마주치다니……\n달이여, 내 싸움을 지켜보아라!",),
    (2, 613): ("교활한 원숭이 놈……\n내 손으로 짓이겨 주마!",),
    (2, 614): ("모두 절대 방심하지 마라.\n적은 지략가다. 겹겹의 함정을 경계하라.",),
    (2, 615): ("서방님, 다녀오십시오.\n부디 무리는 하지 마세요……",),
    (2, 616): ("집은 걱정 말고 맡겨 주세요.\n이곳은", "이(가) 지키겠습니다."),
    (2, 617): ("님……\n이곳에서 돌아오시길 기다리겠습니다.",),
    (2, 618): (
        "님, 출진하시는군요.\n도움을 드릴 사람:",
        "에게 시키실 일이 있다면 무엇이든 말씀해 주세요……",
    ),
    (2, 619): ("님과 함께할 사람:", "\n둘이서 공을 세우겠습니다!"),
    (2, 620): ("! 늘 고맙다.\n집을 잘 부탁한다.",),
    (2, 621): ("배웅하느라 수고했다.\n그 단도는 절대 놓지 마라.",),
    (2, 622): ("아, 늘 배웅해 줘 고맙다.\n전투의 승리를 네게 바치마.",),
    (2, 623): ("늘 고생이 많다.\n공적의 주인:", "을(를) 잊지 않겠다."),
    (2, 624): ("말한 사람:", "의 말이 맞다!\n내 공은 곧 우리 둘의 공이다!"),
    (2, 625): ("의", "님이 황천길에 올랐습니다.\n고인의 명복을 빕시다."),
    (2, 626): ("원수의 이름:", "다메노부", "!\n그가 얕본 가문:", "에게 무릎 꿇려라."),
    (2, 627): ("악귀", "이(가) 나선다!\n상대할 가문:", "다테", "의 애송이에게 본때를 보여 주마!"),
    (2, 628): ("독안룡이 악귀", "사타케", "를 제압해 주마.\n모두, 지금이 고비다!"),
    (2, 629): ("어리석은 공방이여,\n새 시대를 열 자:", "에게 네놈은 필요 없다!"),
    (2, 630): ("여기는 내게 맡겨라!\n총구를 겨눌 자:", "노부나가", "에게 이 화승총의 위력을 맛보여 주마!"),
    (2, 631): ("적은 서국무쌍의 맹장:", "스에", "!\n모든 계책을 동원해 맞서자!"),
    (2, 632): ("명문", "이치조", "가문도 두렵지 않다.\n하극상을 이룰 자:", "!"),
    (2, 633): ("지금이 절호의 기회다.\n쓰러뜨릴 상대:", "오토모", "를 꺾고 규슈를 제패하자."),
    (2, 634): ("어리석은", "시마즈", "여,\n신의 위광을 똑똑히 보아라!"),
    (2, 635): ("모두 출진할 때다!\n쓰러뜨릴 상대:", "시마즈", "쯤은 단숨에 격파해 주마!"),
    (2, 636): ("의", "님 등\n", "명이 황천길에 올랐습니다.\n고인들의 명복을 빕시다."),
    (2, 637): ("당주", "님이\n서거하셨습니다."),
    (2, 638): ("의", "님 등\n여러 세력의 당주가 서거한 듯합니다."),
    (2, 639): ("주군께서 서거하셨습니다.\n임종에 유언을 남기셨다고 합니다.",),
    (2, 640): ("적은 소문난 지장:", ",\n내 상대로 부족함이 없다!"),
    (2, 641): ("적은 소문난 지장:", ",\n지략을 다해 승기를 잡자."),
    (2, 642): ("부인께서 황천길에 오르셨습니다.\n고인의 명복을 빕시다.",),
    (2, 657): ("군단장이 없어져,\n", "군단이 해산되었습니다."),
    (2, 658): (
        "소속 세력:",
        ", 거점:",
        "에서\n개발 중인 항목:",
        "\n완료까지",
        "일이 걸릴 예정입니다.",
    ),
    (2, 659): (
        "건설 거점:",
        "에서 건설 중인 시설:",
        None,
        ")\n완료까지",
        "일이 걸릴 예정입니다.",
    ),
    (2, 660): (
        "시행할 정책「",
        None,
        ")」\n시행까지",
        "일이 걸릴 예정입니다.",
    ),
    (2, 661): ("완료까지", "일이 걸릴 예정입니다."),
    (2, 662): ("관련 진언을 진행 중입니다.",),
    (2, 663): ("완료까지", "일이 걸릴 예정입니다."),
    (2, 664): (
        "소속 세력:",
        ", 거점:",
        "에서 진행 중인 작업\n",
        "은(는) 완료까지",
        "일이 걸릴 예정입니다.",
    ),
    (2, 665): ("친선을 진행할 세력:", "과의 친선은\n완료까지", "개월 남았습니다."),
}


SKIPPED_CANDIDATES: dict[tuple[int, int, int], str] = {
    (2, 659, 2): "nonlinguistic_level_format_prefix",
    (2, 660, 1): "nonlinguistic_level_format_prefix",
}
EXPECTED_RECORD_IDS = tuple(range(566, 643)) + tuple(range(657, 666))


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
    if keys != [(2, record_id) for record_id in EXPECTED_RECORD_IDS]:
        raise ValueError("translation scan record set changed")
    if selected[0] != (2, 566, 0) or selected[-1] != (2, 665, 2):
        raise ValueError("translation batch boundaries changed")
    if len(selected) != 150 or len(keys) != 86:
        raise ValueError("translation batch scope changed")
    if set(SKIPPED_CANDIDATES) != {(2, 659, 2), (2, 660, 1)}:
        raise ValueError("translation batch skip set changed")
    if set(selected) & set(SKIPPED_CANDIDATES):
        raise ValueError("a skipped coordinate is also selected")


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
    if coordinate[1] in range(657, 666):
        flags.append("runtime_value_join_review")
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
    observed_skips: set[tuple[int, int, int]] = set()

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
            previous.is_visible_translation_candidate(item.text)
            for item in source_record_literals
        ):
            raise ValueError(f"scanned record contains an invisible SC literal: {key}")

        language_references = {
            language: previous.record_reference(records[language][key])
            for language in LANGUAGES
        }
        literal_counts = {
            language: language_references[language]["literal_count"]
            for language in LANGUAGES
        }
        selected_ids = [
            literal_id
            for literal_id, replacement in enumerate(replacements)
            if replacement is not None
        ]
        skipped_ids = [
            literal_id
            for literal_id, replacement in enumerate(replacements)
            if replacement is None
        ]
        record_evidence.append(
            {
                "block_id": block_id,
                "record_id": record_id,
                "selected_sc_literal_ids": selected_ids,
                "skipped_sc_literal_ids": skipped_ids,
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
            coordinate = (block_id, record_id, literal.literal_id)
            if replacement is None:
                if coordinate not in SKIPPED_CANDIDATES:
                    raise ValueError(f"unexplained skipped coordinate: {coordinate}")
                observed_skips.add(coordinate)
                continue
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
    if observed_skips != set(SKIPPED_CANDIDATES):
        raise ValueError("declared skipped coordinates were not observed")
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
    if selected[-1] != (2, 665, 2) or NEXT_COORDINATE not in sc_literals:
        raise ValueError("batch continuation boundary changed")

    record_keys = selected_record_keys()
    skipped = [
        {"coordinate": list(coordinate), "reason": reason}
        for coordinate, reason in sorted(SKIPPED_CANDIDATES.items())
    ]
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
            "scanned_visible_candidate_count": len(selected) + len(skipped),
            "skipped_candidates": skipped,
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
            "scanned_visible_candidate_count": len(selected) + len(skipped),
            "nonlinguistic_visible_candidate_skips": len(skipped),
            "skipped_candidates": skipped,
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
            "skipped_candidates_unchanged": all(
                target_literals[coordinate].text == sc_literals[coordinate].text
                for coordinate in SKIPPED_CANDIDATES
            ),
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
        "skipped_count": len(skipped),
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
