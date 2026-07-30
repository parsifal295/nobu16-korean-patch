#!/usr/bin/env python3
"""Build source-redacted PK B141 segment 1427 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals
_ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE = (
    COMMON.BASE.base_and_assembly_evidence
)

TARGET_COORDINATES = (
    "17:534:0", "17:534:1", "17:535:0", "17:536:0",
    "17:537:0", "17:537:1", "17:538:0", "17:538:1",
    "17:539:0", "17:539:1", "17:540:0",
    "17:541:0", "17:541:1", "17:542:0",
    "17:543:0", "17:543:1",
    "17:544:0", "17:544:1", "17:545:0", "17:546:0",
    "17:547:0", "17:547:1",
    "17:548:0", "17:548:1", "17:548:2",
    "17:549:0", "17:549:1", "17:550:0",
    "17:551:0", "17:551:1", "17:552:0", "17:552:1",
    "17:553:0", "17:554:0", "17:555:0",
    "17:556:0", "17:556:1", "17:557:0", "17:557:1",
    "17:558:0", "17:558:1", "17:558:2", "17:558:3",
    "17:558:4", "17:558:5", "17:558:6",
    "17:559:0", "17:560:0", "17:561:0",
    "17:562:0", "17:562:1", "17:563:0", "17:563:1",
    "17:564:0", "17:565:0",
    "17:566:0", "17:566:1", "17:566:2",
    "17:567:0", "17:567:1", "17:568:0",
    "17:569:0", "17:569:1", "17:570:0",
    "17:571:0", "17:571:1", "17:572:0",
)

TRANSLATIONS = {
    "17:534:0": "각 부대! 소규모 교전을 벌여,\n",
    "17:534:1": "에게서 수비대를 떼어 내라",
    "17:535:0": "맡겨 주십시오!\n저희가 길을 열겠습니다!",
    "17:536:0": "부대를 수비대와 교전시키지 마라",
    "17:537:0": "부대를 수비대와 교전시키지 마라",
    "17:537:1": " 성공",
    "17:538:0": "부대를 수비대와 교전시키지 마라",
    "17:538:1": " 실패",
    "17:539:0": "오다",
    "17:539:1": "의 기습이다!\n모두, 이 무법자들을 베어라!",
    "17:540:0": "기습을 들키다니……!",
    "17:541:0": (
        "이렇게 된 이상 어쩔 수 없다……\n"
        "서로 찔러 죽는 한이 있어도"
    ),
    "17:541:1": "를 쳐라!",
    "17:542:0": "주군을 지켜라! 나아가라!",
    "17:543:0": "쳐라!\n노리는 것은",
    "17:543:1": "의 목 하나뿐이다!",
    "17:544:0": (
        "습격……!? 이 비바람 속에서……!\n"
        "제법이구나,"
    ),
    "17:544:1": "애송이!",
    "17:545:0": "이대로 단숨에 끝장을 내자!",
    "17:546:0": "지금이다! 주군을 따라라!\n대장의 목은 우리가 취하겠다!",
    "17:547:0": "모두, 지금이 고비다!\n",
    "17:547:1": "를 구하러 가지 못하게 하라!",
    "17:548:0": "이런 곳에",
    "17:548:1": "오다",
    "17:548:2": "의 병사가……?\n상관없다, 한 명도 남김없이 베어라!",
    "17:549:0": "좋다! 후퇴하며 적병을 끌어들여라\n",
    "17:549:1": "까지 가는 길을 만드는 것이다!",
    "17:550:0": "부대를 협격하라",
    "17:551:0": "부대를 협격하라",
    "17:551:1": " 성공",
    "17:552:0": "부대를 협격하라",
    "17:552:1": " 실패",
    "17:553:0": "협격……!? 이토록 치밀하다니……!",
    "17:554:0": "의 목이 바로 앞이다!\n반드시 베겠다!",
    "17:555:0": "부대를 격파하라",
    "17:556:0": "부대를 격파하라",
    "17:556:1": " 성공",
    "17:557:0": "부대를 격파하라",
    "17:557:1": " 실패",
    "17:558:0": "으…… 여기서 쓰러지면……\n",
    "17:558:1": "이마가와",
    "17:558:2": " 가문이……　",
    "17:558:3": "우지",
    "17:558:4": "……",
    "17:558:5": "자네",
    "17:558:6": "……!",
    "17:559:0": "를 베었다!\n모두, 승리의 함성을 올려라!",
    "17:560:0": "하늘이 나를 버렸나……\n어쩔 수 없군……",
    "17:561:0": "기습 전에 모든 수비대와 교전하라",
    "17:562:0": "기습 전에 모든 수비대와 교전하라",
    "17:562:1": " 성공",
    "17:563:0": "기습 전에 모든 수비대와 교전하라",
    "17:563:1": " 실패",
    "17:564:0": "적병……? 물자를 빼앗기면 성가시다\n어서 쫓아내라!",
    "17:565:0": (
        "좋아, 이대로 소규모 접전을 계속하라!\n"
        "기습이 성공할 때까지 여기서 버텨라!"
    ),
    "17:566:0": "적병……?　",
    "17:566:1": "오다",
    "17:566:2": "의 소부대가 낙오했나?\n쫓아라! 공으로 삼아 주마!",
    "17:567:0": "적이 미끼를 물었군……\n이대로 물러나",
    "17:567:1": "에게서 떼어 놓겠다!",
    "17:568:0": (
        "좋다! 전투를 계속하는 동안에는\n"
        "수비대 놈들도 움직이지 못하겠지……"
    ),
    "17:569:0": "이 틈에 본대로",
    "17:569:1": "를 노린다!",
    "17:570:0": "알겠습니다!\n이대로 적을 본진에서 떼어 놓겠습니다",
    "17:571:0": "쳐라!\n노리는 것은",
    "17:571:1": "의 목 하나뿐이다!",
    "17:572:0": "본진에 적습이다!\n",
}

TARGET_RECORD_IDS = tuple(range(534, 573))
MAIN_RECORD_IDS = TARGET_RECORD_IDS[:-1]
MAIN_TARGET_COORDINATES = TARGET_COORDINATES[:-1]
NEIGHBOR_COMPANION_TRANSLATIONS = {"17:572:1": "님을 구하라!"}
EXPECTED_ARITY = {
    534: 2, 535: 1, 536: 1, 537: 2, 538: 2, 539: 2,
    540: 1, 541: 2, 542: 1, 543: 2, 544: 2, 545: 1,
    546: 1, 547: 2, 548: 3, 549: 2, 550: 1, 551: 2,
    552: 2, 553: 1, 554: 1, 555: 1, 556: 2, 557: 2,
    558: 7, 559: 1, 560: 1, 561: 1, 562: 2, 563: 2,
    564: 1, 565: 1, 566: 3, 567: 2, 568: 1, 569: 2,
    570: 1, 571: 2, 572: 2,
}
SEMANTIC_BASE_CONTEXT = {
    record_id: (
        ("9:2842:0",)
        if record_id in {
            536, 537, 538, 550, 551, 552, 555, 556, 557,
            561, 562, 563,
        }
        else ("9:3792:0",)
    )
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    **{record_id: ((), ()) for record_id in TARGET_RECORD_IDS},
    534: ((), ("024835",)),
    536: ((), ("024633",)),
    537: ((), ("024633",)),
    538: ((), ("024633",)),
    541: ((), ("024835",)),
    543: ((), ("024835",)),
    544: ((), ("024834",)),
    547: ((), ("024835",)),
    549: ((), ("024835",)),
    554: ((), ("024835",)),
    559: ((), ("024833",)),
    567: ((), ("024835",)),
    569: ((), ("024835",)),
    571: ((), ("024835",)),
    572: ((), ("024835",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1427,
    queue_start=0,
    queue_stop=67,
    slice_first="17:534:0",
    slice_last="17:572:0",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=(),
    prefill_companion_donor={},
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(),
    boundary_record_keys=tuple(
        (17, record_id) for record_id in range(495, 615)
    ),
    speaker_style=tuple(
        (record_id, "okehazama_historical_battle_dialogue")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("Oda", "오다"),
        ("Imagawa", "이마가와"),
        ("Ujizane", "우지자네"),
        ("defense unit", "수비대"),
        ("raid", "기습"),
        ("skirmish", "소규모 교전·접전"),
        ("pincer attack", "협격"),
        ("main camp", "본진"),
        ("target unit", "부대"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "entire first sixty-seven visible B141 queue coordinates because "
        "no approved Base prefill exists in the slice; pristine PK JP is "
        "authoritative and every populated EN same-record fragment array "
        "was manually reviewed as auxiliary context; completed Base "
        "objective and battle-command rows are semantic and terminology "
        "references only because none of the thirty-nine PK records has a "
        "raw, literal or operand-masked Base match; Oda, Imagawa and the "
        "dying Ujizane name assembly retain established historical forms, "
        "and defense-unit, raid, skirmish, pincer, main-camp and target-unit "
        "terms are normalized; objective labels remain concise while "
        "ambush, decoy, pursuit, last-stand, victory and dying registers "
        "remain distinct; colour tags, inline person, force and unit tokens, "
        "protected spaces, line breaks, particles, punctuation, terminators, "
        "complete record arity, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, reciprocal "
        "S1428 and S1429 decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=17,
    pins={
        "expected_queue_universe_sha256":
        "BD0356A7F45265B21128FF30DDB7A86151F86A09F8A54F311FB7A53B03BF2289",
        "expected_queue_slice_sha256":
        "AA0F40A4DBB200EA7A83BAA21CF831F33823DC4C0876031BB99CD884A12A6B20",
        "expected_prefilled_coordinate_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256":
        "AA0F40A4DBB200EA7A83BAA21CF831F33823DC4C0876031BB99CD884A12A6B20",
        "expected_source_target_sha256":
        "A590C4D39AF85BC7CC0F7A216D94449D1E76BFC5681B91A0B2F04A6701D33939",
        "expected_current_target_sha256":
        "689556F989801D81FFB04D88C89E3E9F02372E890BE73908F51ED56AB3AEF697",
        "expected_context_corpus_sha256":
        "50995EF7B0E2D6F4C9407EC0B232A6278066A678D16D93B01D6D9D890C3CC556",
        "expected_gap_contract_sha256":
        "CB27377CC2424430E98A143B60A34E3B79CD7492AC9A167E3600D22C36F09260",
        "expected_boundary_sha256":
        "DEDF7AA25C03B3A726998C89AC3660EDC65397D39F4EB02C6FBA0E95B1236B49",
        "expected_runtime_control_sha256":
        "9E4AA47AB4C37F8428A6F159373D1AA2AEC5A9FD437680A927ACF8B088EA8CB4",
        "expected_base_search_sha256":
        "3C40132DBD9A7F66330AE5C3FFB246187AD4FB520FF2443C6AE742B4442E0A0A",
        "expected_complete_assembly_sha256":
        "60555E9B0561E42A46FA5F6B9B2CA6CAFCDF4053E0A48C3EA66EFC4EC0B52902",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "8C1047CB918860EA33C30351F8FC4E5B7013B5B6380347ED356EF3DA10D706C0",
        "expected_terminology_policy_sha256":
        "17D245EEABAE0EBA02550C6CA8A44AA6469532AF1A13C09478C171C0035459E0",
        "expected_translation_policy_sha256":
        "048EB27F5FC882F98F0D9A7159FCF46B31A4BD92EC94486F2F0CB0E730CA3D21",
        "expected_candidate_sha256":
        "CB70BA094471DF83B93AD95AC741D20889450A0D7E41B1E97D1EB91BA7BA1B58",
        "expected_combined_slice_candidate_sha256":
        "CB70BA094471DF83B93AD95AC741D20889450A0D7E41B1E97D1EB91BA7BA1B58",
        "expected_combined_changed_literal_count": 17,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B141_S1427",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B141_S1427.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B141_S1428.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B141_S1429.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B141",
    "queue_row_count": 94,
    "queue_visible_count": 199,
    "queue_first": "17:534:0",
    "queue_last": "17:627:0",
})


def base_and_assembly_evidence_with_boundary(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Guard the main records plus the split right-boundary record."""
    original_globals = _ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE.__globals__
    saved_record_ids = original_globals["TARGET_RECORD_IDS"]
    saved_coordinates = original_globals["TARGET_COORDINATES"]
    original_globals["TARGET_RECORD_IDS"] = MAIN_RECORD_IDS
    original_globals["TARGET_COORDINATES"] = MAIN_TARGET_COORDINATES
    try:
        base_evidence, assembly_evidence = (
            _ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE(
                prepared,
                records_by_label,
            )
        )
    finally:
        original_globals["TARGET_RECORD_IDS"] = saved_record_ids
        original_globals["TARGET_COORDINATES"] = saved_coordinates

    base_source = COMMON.ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_rows = {
        str(row["coordinate"]): row
        for row in COMMON.read_jsonl(COMMON.BASE_PROMOTED)
    }
    neighbor_rows = {
        str(row["coordinate"]): row
        for path in CONFIG["optional_neighbors"]
        if path.is_file()
        for row in COMMON.read_jsonl(path)
    }
    key = (17, 572)
    source = records_by_label["jp"][key]
    current = records_by_label["current"][key]
    source_literals = COMMON.literal_texts(records_by_label["jp"], key)
    current_literals = COMMON.literal_texts(
        records_by_label["current"], key
    )
    raw_matches = tuple(
        coordinate
        for coordinate, record in base_source.items()
        if record.data == source.data
    )
    literal_matches = tuple(
        coordinate
        for coordinate in base_source
        if COMMON.literal_texts(base_source, coordinate) == source_literals
    )
    masked_matches = tuple(
        coordinate
        for coordinate, record in base_source.items()
        if (
            COMMON.literal_texts(base_source, coordinate) == source_literals
            and COMMON.CORE.mask_call_operands(record)
            == COMMON.CORE.mask_call_operands(source)
        )
    )
    references: list[tuple[Any, ...]] = []
    for donor_coordinate in SEMANTIC_BASE_CONTEXT[572]:
        donor = base_rows.get(donor_coordinate)
        if (
            donor is None
            or donor.get("semantic_review") != "approved"
            or donor.get("runtime_review")
            not in {"verified", "not_required"}
        ):
            raise RuntimeError(
                "segment 1427 Base context drifted: "
                f"{donor_coordinate}"
            )
        references.append((
            donor_coordinate,
            str(donor["translation"]),
            str(donor["runtime_review"]),
        ))
    neighbor_coordinate, expected = next(
        iter(NEIGHBOR_COMPANION_TRANSLATIONS.items())
    )
    neighbor = neighbor_rows.get(neighbor_coordinate)
    if (
        neighbor is not None
        and (
            neighbor.get("translation") != expected
            or neighbor.get("semantic_review") != "approved"
            or neighbor.get("runtime_review") != "pending"
        )
    ):
        raise RuntimeError(
            f"segment 1427 neighbor companion drifted: {neighbor_coordinate}"
        )
    assembled = (TRANSLATIONS["17:572:0"], expected)
    if (
        len(source_literals) != EXPECTED_ARITY[572]
        or raw_matches != EXPECTED_BASE_RAW_MATCHES[572]
        or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[572]
        or masked_matches != EXPECTED_BASE_MASKED_MATCHES[572]
        or assembled != ("본진에 적습이다!\n", "님을 구하라!")
    ):
        raise RuntimeError("segment 1427 boundary assembly drifted")
    return (
        tuple(base_evidence) + ((
            572,
            COMMON.sha256_bytes(source.data),
            source_literals,
            current_literals,
            tuple(
                value.hex().upper()
                for value in COMMON.gap_bytes(source)
            ),
            raw_matches,
            literal_matches,
            masked_matches,
            tuple(references),
            "semantic_context_only",
        ),),
        tuple(assembly_evidence) + ((
            572,
            (
                "segment_manual_multilingual",
                "optional_next_segment_manual_companion",
            ),
            assembled,
            None,
            COMMON.CORE.runtime_controls(source),
            COMMON.CORE.runtime_controls(current),
            "base_semantics_only",
            "base_runtime_vm_not_inherited",
        ),),
    )


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 17)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", {})


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.base_and_assembly_evidence = (
        base_and_assembly_evidence_with_boundary
    )
    COMMON.CORE.base_and_assembly_evidence = (
        base_and_assembly_evidence_with_boundary
    )


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
