#!/usr/bin/env python3
"""Build source-redacted PK B142 segment 1430 residual decisions."""

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
    "17:628:0", "17:628:1", "17:628:2",
    "17:629:0", "17:629:1", "17:629:2",
    "17:630:0", "17:630:1", "17:630:2", "17:630:3",
    "17:631:0", "17:631:1", "17:631:2", "17:631:3",
    "17:632:0", "17:633:0", "17:634:0", "17:635:0",
    "17:636:0", "17:637:0", "17:638:0", "17:639:0",
    "17:640:0", "17:640:1",
    "17:641:0", "17:641:1", "17:641:2",
    "17:642:0", "17:642:1", "17:642:2", "17:642:3",
    "17:643:0", "17:643:1", "17:643:2", "17:644:0",
    "17:645:0", "17:645:1", "17:645:2",
    "17:646:0", "17:646:1", "17:647:0", "17:648:0",
    "17:649:0", "17:650:0", "17:650:1",
    "17:651:0", "17:651:1", "17:651:2", "17:651:3", "17:651:4",
    "17:652:0", "17:652:1", "17:653:0", "17:653:1",
    "17:654:0", "17:655:0", "17:655:1", "17:656:0",
    "17:657:0", "17:657:1", "17:658:0",
    "17:659:0", "17:659:1",
    "17:660:0", "17:660:1", "17:660:2",
    "17:661:0",
)

TRANSLATIONS = {
    "17:628:0": "포격 지점",
    "17:628:1": "에 도달하기 전에\n",
    "17:628:2": "부대를 격파하라",
    "17:629:0": "포격 지점",
    "17:629:1": "에 도달하기 전에",
    "17:629:2": "부대를 격파하라",
    "17:630:0": "포격 지점",
    "17:630:1": "에 도달하기 전에\n",
    "17:630:2": "부대를 격파하라",
    "17:630:3": " 성공",
    "17:631:0": "포격 지점",
    "17:631:1": "에 도달하기 전에\n",
    "17:631:2": "부대를 격파하라",
    "17:631:3": " 실패",
    "17:632:0": "좋다! 포격은 막아 냈군!",
    "17:633:0": "역시 천하의 견고한 성……\n그리 쉽게 함락할 수는 없나",
    "17:634:0": "전군, 후퇴하라!\n일단 태세를 가다듬겠다!",
    "17:635:0": "아아, 적이 물러나는군……\n우선은 지켜 낸 셈인가",
    "17:636:0": "대포, 천수각을 겨눠라!\n……쏴라!",
    "17:637:0": "제때 막지 못했는가……!",
    "17:638:0": "우리의 승리다! 승리의 함성을 올려라!",
    "17:639:0": "내 힘이 부족했나……",
    "17:640:0": "사기가 최대가 될 때까지",
    "17:640:1": "부대와 교전하지 마라",
    "17:641:0": "사기가 최대가 될 때까지",
    "17:641:1": "부대와 교전하지 마라",
    "17:641:2": " 성공",
    "17:642:0": "사기가 최대가 될 때까지",
    "17:642:1": "부대와 교전하지 마라",
    "17:642:2": "부대를 격파하라",
    "17:642:3": " 실패",
    "17:643:0": "이런 곳까지 ",
    "17:643:1": "도쿠가와",
    "17:643:2": "군이……!?\n이제 항복할 수밖에 없겠군……",
    "17:644:0": "이래도 밀어붙이지 못하나……\n이렇게 되면……",
    "17:645:0": "전군, 공격하라!\n",
    "17:645:1": "도요토미",
    "17:645:2": "측을 짓밟아라!",
    "17:646:0": "여기는",
    "17:646:1": "의 비위를 맞춰 둘까\n전진! 이 싸움을 끝내라!",
    "17:647:0": "모두, 끝까지 버텨라!\n지금이 고비다!",
    "17:648:0": (
        "이 싸움이 내 마지막 싸움이겠지\n"
        "……하지만 이번에는 그것만이 아니다\n"
        "난세가 새롭게 태어나기 위한 싸움이다"
    ),
    "17:649:0": "에게 최후를 고하고\n낡은 세상을 끝낼 때는 지금이다!",
    "17:650:0": (
        "이 싸움에서 반드시 선봉의 역할을 다해\n"
        "술로 저지른 실수……"
    ),
    "17:650:1": "라는 오명을 씻어야 한다!",
    "17:651:0": "우리",
    "17:651:1": "도쿠가와",
    "17:651:2": "의 선봉이 되어 목숨 걸고 나아간다!\n우선",
    "17:651:3": "덴노지",
    "17:651:4": "근처의 적을 친다!",
    "17:652:0": "기다려라, 죽을 셈이냐!\n……큭, 우리도",
    "17:652:1": "부대를 따라라!",
    "17:653:0": "흥, 시시한 싸움이군……\n",
    "17:653:1": ", 모두에게 자리를 지키라고 전하라",
    "17:654:0": "예…… 하지만, 괜찮으십니까?",
    "17:655:0": "이 싸움이 끝나면",
    "17:655:1": "의 천하다\n허무하게 목숨을 버릴 필요는 없다",
    "17:656:0": "놈, 몹시 의욕이 넘치는군\n자, 우리는 결말을 지켜볼까",
    "17:657:0": (
        "성에 틀어박힐 수도, 해자와 강을 이용할 수도 없다\n"
        "아무리"
    ),
    "17:657:1": "라도 손쓸 도리는 없겠지……",
    "17:658:0": (
        "병력이 우세한 대장이 움직이는 것은 하책이다\n"
        "움직이지 말고 결말을 지켜보자"
    ),
    "17:659:0": "덴노지",
    "17:659:1": "의 요충지를 확보하라",
    "17:660:0": "덴노지",
    "17:660:1": "의 요충지를 확보하라",
    "17:660:2": " 성공",
    "17:661:0": "덴노지",
}

TARGET_RECORD_IDS = tuple(range(628, 662))
MAIN_RECORD_IDS = TARGET_RECORD_IDS[:-1]
MAIN_TARGET_COORDINATES = TARGET_COORDINATES[:-1]
EXPECTED_ARITY = {
    628: 3, 629: 3, 630: 4, 631: 4, 632: 1, 633: 1,
    634: 1, 635: 1, 636: 1, 637: 1, 638: 1, 639: 1,
    640: 2, 641: 3, 642: 4, 643: 3, 644: 1, 645: 3,
    646: 2, 647: 1, 648: 1, 649: 1, 650: 2, 651: 5,
    652: 2, 653: 2, 654: 1, 655: 2, 656: 1, 657: 2,
    658: 1, 659: 2, 660: 3, 661: 3,
}
NEIGHBOR_COMPANION_TRANSLATIONS = {
    "17:661:1": "의 요충지를 확보하라",
    "17:661:2": " 실패",
}
SEMANTIC_BASE_CONTEXT = {
    record_id: (
        ("9:2842:0",)
        if record_id in {
            628, 629, 630, 631, 640, 641, 642, 659, 660, 661,
        }
        else ("9:1006:0",)
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
    640: ((), ("024633",)),
    641: ((), ("024633",)),
    642: ((), ("024633",)),
    646: ((), ("024835",)),
    649: ((), ("024734",)),
    650: ((), ("024634",)),
    652: ((), ("024735",)),
    653: ((), ("024735",)),
    655: ((), ("024734",)),
    656: ((), ("024735",)),
    657: ((), ("024734",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1430,
    queue_start=0,
    queue_stop=67,
    slice_first="17:628:0",
    slice_last="17:661:0",
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
        (17, record_id) for record_id in range(590, 705)
    ),
    speaker_style=tuple(
        (record_id, "osaka_historical_battle_dialogue")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("Tokugawa", "도쿠가와"),
        ("Toyotomi", "도요토미"),
        ("Tennōji", "덴노지"),
        ("firing point", "포격 지점"),
        ("cannon", "대포"),
        ("castle tower", "천수각"),
        ("morale", "사기"),
        ("surrender", "항복"),
        ("vanguard", "선봉"),
        ("strategic point", "요충지"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "entire first sixty-seven visible B142 queue coordinates because "
        "no approved Base prefill exists in the slice; pristine PK JP is "
        "authoritative and every populated EN same-record fragment array "
        "was manually reviewed as auxiliary context; completed Base "
        "objective, strategic-point and officer dialogue rows are semantic "
        "and terminology references only because none of the thirty-four "
        "PK records has a raw, literal or operand-masked Base match; "
        "Tokugawa, Toyotomi and Tennōji retain established historical "
        "project forms, while firing-point, cannon, tower, morale, surrender, "
        "vanguard and strategic-point terminology is normalized; objective "
        "labels remain concise while siege, withdrawal, final-battle and "
        "observer registers remain distinct; colour tags, inline person, "
        "force, unit and location tokens, protected spaces, line breaks, "
        "particles, punctuation, terminators, complete record arity, pins, "
        "reverse overlays, two-run reproduction, tamper rejection, "
        "outside-scope identity, reciprocal S1431 and S1432 decisions and "
        "Steam read-only state are guarded"
    ),
    expected_changed_literal_count=13,
    pins={
        "expected_queue_universe_sha256":
        "9ADC9B4DD0A084887292B974B664291A50102FAC706F3F8FD9A07A4FD782C767",
        "expected_queue_slice_sha256":
        "404E3F4CB51FD07964320CA75A093728ED3794D13CD1E1DB13A93A97810FC8E3",
        "expected_prefilled_coordinate_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256":
        "404E3F4CB51FD07964320CA75A093728ED3794D13CD1E1DB13A93A97810FC8E3",
        "expected_source_target_sha256":
        "3F65926685CF26259247749D9D91681C0625E82B660B44D6024EC50C5ABCCED7",
        "expected_current_target_sha256":
        "1F16176A241342C8D6EDDE4563502B6E66DBBC8B2458616044932D82AB610B9B",
        "expected_context_corpus_sha256":
        "D37D0147B94C15EFAD70A3E9F8EC94A9D06CC6FCB3575430EE470F5EAC990A7C",
        "expected_gap_contract_sha256":
        "94F486C47963EC557FFFFE6AFC4F4C4D056203EF894785E80466D0B641350F13",
        "expected_boundary_sha256":
        "79C04ECF093960A4458CE787895750291C9BB6D22EDF71182D4EC700EA5A0F8A",
        "expected_runtime_control_sha256":
        "0DC7CD346B40900555ABC535D556E2C58A15BCA315D84A5D3BBBF9101809B696",
        "expected_base_search_sha256":
        "B131C4DB44B80E64BD4FDB743AA4434425C6C144BFD76AFE1360A8BDA42938F0",
        "expected_complete_assembly_sha256":
        "ABDD9D3B4F2B511B68DB78CDAB746A4970CDAC35851E089B9D43FFA6FB9A4BA6",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "392E65E574A1D592E77C1E0C4D2E18C1258F9E96A712745E61CE0929AC7E2456",
        "expected_terminology_policy_sha256":
        "65EEE0718946C4F39ABF5198E9DE3A662C3E79A5520FE19E52779C503C8FBD79",
        "expected_translation_policy_sha256":
        "B3BE7F6D38D40E1E8A846A918F23BD4995793C5FD8C4A560F78E1F21156F4FD0",
        "expected_candidate_sha256":
        "F0313D211F3DDE1248B931063F13DE27D8EAB7B79EEF29E9CDDB9D9FC5B82902",
        "expected_combined_slice_candidate_sha256":
        "F0313D211F3DDE1248B931063F13DE27D8EAB7B79EEF29E9CDDB9D9FC5B82902",
        "expected_combined_changed_literal_count": 13,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B142_S1430",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B142_S1430.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B142_S1431.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B142_S1432.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B142",
    "queue_row_count": 106,
    "queue_visible_count": 200,
    "queue_first": "17:628:0",
    "queue_last": "17:733:1",
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
    key = (17, 661)
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
    for donor_coordinate in SEMANTIC_BASE_CONTEXT[661]:
        donor = base_rows.get(donor_coordinate)
        if (
            donor is None
            or donor.get("semantic_review") != "approved"
            or donor.get("runtime_review")
            not in {"verified", "not_required"}
        ):
            raise RuntimeError(
                "segment 1430 Base context drifted: "
                f"{donor_coordinate}"
            )
        references.append((
            donor_coordinate,
            str(donor["translation"]),
            str(donor["runtime_review"]),
        ))
    for neighbor_coordinate, expected in (
        NEIGHBOR_COMPANION_TRANSLATIONS.items()
    ):
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
                "segment 1430 neighbor companion drifted: "
                f"{neighbor_coordinate}"
            )
    assembled = (
        TRANSLATIONS["17:661:0"],
        NEIGHBOR_COMPANION_TRANSLATIONS["17:661:1"],
        NEIGHBOR_COMPANION_TRANSLATIONS["17:661:2"],
    )
    if (
        len(source_literals) != EXPECTED_ARITY[661]
        or raw_matches != EXPECTED_BASE_RAW_MATCHES[661]
        or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[661]
        or masked_matches != EXPECTED_BASE_MASKED_MATCHES[661]
        or assembled != ("덴노지", "의 요충지를 확보하라", " 실패")
    ):
        raise RuntimeError("segment 1430 boundary assembly drifted")
    return (
        tuple(base_evidence) + ((
            661,
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
            661,
            (
                "segment_manual_multilingual",
                "optional_next_segment_manual_companion",
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
