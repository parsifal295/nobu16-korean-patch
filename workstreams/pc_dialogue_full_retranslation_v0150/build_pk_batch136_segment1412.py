#!/usr/bin/env python3
"""Build source-redacted PK B136 segment 1412 residual decisions."""

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
    "17:58:0", "17:58:1",
    "17:59:0", "17:59:1",
    "17:60:0", "17:60:1", "17:60:2", "17:60:3",
    "17:61:0",
    "17:62:0", "17:62:1",
    "17:63:0", "17:63:1",
    "17:64:0",
    "17:65:0",
    "17:66:0",
    "17:67:0",
    "17:69:0",
    "17:70:0", "17:70:1",
    "17:71:0", "17:71:1",
    "17:72:0", "17:72:1",
    "17:77:0", "17:77:1",
    "17:78:0", "17:78:1",
    "17:79:0", "17:79:1", "17:79:2",
    "17:80:0", "17:80:1", "17:80:2", "17:80:3",
    "17:81:0",
    "17:82:0", "17:82:1",
    "17:83:0", "17:83:1",
    "17:84:0",
    "17:85:0",
    "17:86:0",
    "17:87:0", "17:87:1",
    "17:88:0", "17:88:1", "17:88:2", "17:88:3", "17:88:4",
    "17:89:0",
    "17:90:0", "17:90:1",
    "17:91:0", "17:91:1",
    "17:92:0", "17:92:1", "17:92:2",
    "17:93:0", "17:93:1",
    "17:94:0",
    "17:95:0",
    "17:96:0", "17:96:1",
    "17:97:0",
    "17:98:0",
    "17:99:0",
)

TRANSLATIONS = {
    "17:58:0": "하하, 설마 정말 쫓아올 줄이야!\n",
    "17:58:1": "도 아직 풋내기로 보이는군",
    "17:59:0": (
        "상당히 서둘렀는지 진형이 흐트러졌군\n"
        "눈여겨볼 자는"
    ),
    "17:59:1": "정도인가",
    "17:60:0": "저곳이 바로",
    "17:60:1": "도쿠가와",
    "17:60:2": "진형의 핵심이겠지\n선봉!",
    "17:60:3": "부대에 공격을 집중하라!",
    "17:61:0": "격파하라",
    "17:62:0": "격파하라",
    "17:62:1": " 성공",
    "17:63:0": "격파하라",
    "17:63:1": " 실패",
    "17:64:0": (
        "이길 수 없는 싸움에 덤비다니……\n"
        "어리석은 주군을 모시면 고생이 많구나!"
    ),
    "17:65:0": (
        "이놈, 감히 우리 주군을 우롱하느냐!\n"
        "놈을 쫓아라!"
    ),
    "17:66:0": (
        "그 더러운 입을\n"
        "다시는 열지 못하게 해 주마!"
    ),
    "17:67:0": (
        "적장을 제대로 도발한 모양이군\n"
        "이대로 아군 진지로 유인해 협격하라!"
    ),
    "17:69:0": "와 접촉해 도발하라",
    "17:70:0": "와 접촉해 도발하라",
    "17:70:1": " 성공",
    "17:71:0": "와 접촉해 도발하라",
    "17:71:1": " 실패",
    "17:72:0": "길이 열렸다!\n전진하라!　",
    "17:72:1": "부대의 측면을 쳐라!",
    "17:77:0": "창을 제법 쓰는구나,",
    "17:77:1": (
        "라고 했던가!\n"
        "이 난전에서도 상처 하나 없다니!"
    ),
    "17:78:0": "불사신 바바 미노",
    "17:78:1": (
        "님이십니까……\n"
        "평생 상처 하나 없던 귀하께는 아직 못 미칩니다"
    ),
    "17:79:0": "기마대! 달려라!\n",
    "17:79:1": "오다",
    "17:79:2": "의 원군에게 공포를 심어 줘라!",
    "17:80:0": "다케다 ",
    "17:80:1": (
        "기마대…… 무시무시한 기세로군!\n"
        "우리 "
    ),
    "17:80:2": "오다 가문",
    "17:80:3": "이 맞설 방법이 있는가……?",
    "17:81:0": "격파하라",
    "17:82:0": "격파하라",
    "17:82:1": " 성공",
    "17:83:0": "격파하라",
    "17:83:1": " 실패",
    "17:84:0": (
        "주군, 어서 피하십시오!\n"
        "이곳은 제가 미끼가 되겠습니다"
    ),
    "17:85:0": (
        "……! 와 주었구나……\n"
        "미안하다, 나는 네게 아무것도 돌려줄 수 없구나……"
    ),
    "17:86:0": (
        "그럼 그 투구를 포상으로 받겠습니다\n"
        "……자, 어서 피하십시오!"
    ),
    "17:87:0": "이 투구를 보아라! 내가 바로",
    "17:87:1": (
        "다!\n"
        "공을 세우고 싶다면 이 목을 베어 보아라!"
    ),
    "17:88:0": "도쿠가와",
    "17:88:1": "군을",
    "17:88:2": "미카타가하라",
    "17:88:3": (
        "로 유인해 냈습니다\n"
        "여기서 적군을 대파하고,"
    ),
    "17:88:4": (
        "를 쓰러뜨리면\n"
        "교토로 진군하기도 쉬워질 것입니다"
    ),
    "17:89:0": "격파하라",
    "17:90:0": "격파하라",
    "17:90:1": " 성공",
    "17:91:0": "격파하라",
    "17:91:1": " 실패",
    "17:92:0": (
        "더는 유인할 상황이 아닌가……\n"
        "하지만 우세한 것은 변함없다! "
    ),
    "17:92:1": "이에야스",
    "17:92:2": "를 쳐라!",
    "17:93:0": "적진이 생각보다 견고합니다\n",
    "17:93:1": ", 역시 만만치 않군……",
    "17:94:0": (
        "그렇다면 우회책을 쓰겠다\n"
        "아무리 견고한 진도 측면과 배후는 약한 법……"
    ),
    "17:95:0": (
        "! 네가 나설 차례다!\n"
        "적의 좌익을 이쪽으로 유인하라"
    ),
    "17:96:0": "연계를 무너뜨려 각개격파하고,\n",
    "17:96:1": "부대로 향하는 우회로를 열어라",
    "17:97:0": (
        "잠시 적진을 도발하고 오겠습니다\n"
        "욕설이라면 자신이 있으니까요"
    ),
    "17:98:0": (
        "유인이라고……!?\n"
        "비겁한 수를 쓰는군……!"
    ),
    "17:99:0": "내가 바로",
}

TARGET_RECORD_IDS = (
    58, 59, 60, 61, 62, 63, 64, 65, 66, 67,
    69, 70, 71, 72, 77, 78, 79, 80, 81, 82,
    83, 84, 85, 86, 87, 88, 89, 90, 91, 92,
    93, 94, 95, 96, 97, 98, 99,
)
EXPECTED_ARITY = {
    58: 2, 59: 2, 60: 4, 61: 1, 62: 2, 63: 2,
    64: 1, 65: 1, 66: 1, 67: 1, 69: 1, 70: 2,
    71: 2, 72: 2, 77: 2, 78: 2, 79: 3, 80: 4,
    81: 1, 82: 2, 83: 2, 84: 1, 85: 1, 86: 1,
    87: 2, 88: 5, 89: 1, 90: 2, 91: 2, 92: 3,
    93: 2, 94: 1, 95: 1, 96: 2, 97: 1, 98: 1,
    99: 2,
}
MAIN_RECORD_IDS = TARGET_RECORD_IDS[:-1]
MAIN_TARGET_COORDINATES = TARGET_COORDINATES[:-1]
NEIGHBOR_COMPANION_TRANSLATIONS = {
    "17:99:1": (
        "다!\n"
        "병사 한 명도 이곳을 지나게 두지 않겠다!"
    ),
}

OBJECTIVE_RECORD_IDS = (61, 62, 63, 69, 70, 71, 81, 82, 83, 89, 90, 91)
TAUNT_RECORD_IDS = (64, 65, 66, 67, 77, 78, 80, 84, 85, 86, 87, 93, 97, 98, 99)
COMMAND_RECORD_IDS = (58, 59, 60, 72, 79, 88, 92, 94, 95, 96)
SEMANTIC_BASE_CONTEXT = {
    **{record_id: ("7:1974:1",) for record_id in OBJECTIVE_RECORD_IDS},
    **{record_id: ("7:1040:0",) for record_id in TAUNT_RECORD_IDS},
    **{record_id: ("9:3792:0",) for record_id in COMMAND_RECORD_IDS},
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    **{record_id: ((), ()) for record_id in TARGET_RECORD_IDS},
    58: ((), ("024835",)),
    59: ((), ("024833",)),
    60: ((), ("024834",)),
    72: ((), ("024834",)),
    77: ((), ("024835",)),
    85: ((), ("024834",)),
    87: ((), ("024833",)),
    88: ((), ("024835",)),
    93: ((), ("024833",)),
    95: ((), ("024834",)),
    96: ((), ("024834",)),
    99: ((), ("024833",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1412,
    queue_start=0,
    queue_stop=67,
    slice_first="17:58:0",
    slice_last="17:99:0",
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
        (17, record_id) for record_id in range(18, 140)
    ),
    speaker_style=(
        (58, "taunting_pursuit_observation"),
        (59, "confident_enemy_formation_assessment"),
        (60, "commanding_enemy_center_attack"),
        (61, "scenario_defeat_objective"),
        (62, "scenario_defeat_objective_success"),
        (63, "scenario_defeat_objective_failure"),
        (64, "elderly_taunt_about_foolish_lord"),
        (65, "enraged_lord_defense_and_pursuit"),
        (66, "enraged_retort_to_insult"),
        (67, "commanding_provocation_pincer"),
        (69, "scenario_provocation_objective"),
        (70, "scenario_provocation_objective_success"),
        (71, "scenario_provocation_objective_failure"),
        (72, "commanding_flank_attack"),
        (77, "admiring_spearwarrior_challenge"),
        (78, "modest_reply_to_baba_mino"),
        (79, "commanding_takeda_cavalry_charge"),
        (80, "astonished_oda_cavalry_assessment"),
        (81, "scenario_defeat_objective"),
        (82, "scenario_defeat_objective_success"),
        (83, "scenario_defeat_objective_failure"),
        (84, "formal_loyal_decoy_offer"),
        (85, "regretful_lord_to_rescuer"),
        (86, "formal_helmet_reward_decoy"),
        (87, "defiant_false_identity_challenge"),
        (88, "formal_mikatagahara_strategy_report"),
        (89, "scenario_defeat_objective"),
        (90, "scenario_defeat_objective_success"),
        (91, "scenario_defeat_objective_failure"),
        (92, "commanding_advance_against_ieyasu"),
        (93, "formal_enemy_formation_assessment"),
        (94, "commanding_flanking_plan"),
        (95, "commanding_left_wing_lure"),
        (96, "commanding_defeat_in_detail"),
        (97, "formal_comic_provocation_offer"),
        (98, "outraged_response_to_lure"),
        (99, "defiant_last_stand"),
    ),
    terminology_policy=(
        ("formation", "진형"),
        ("lord", "주군"),
        ("pincer attack", "협격"),
        ("engage", "접촉"),
        ("provoke", "도발"),
        ("flank", "측면"),
        ("Mino Baba the Undying", "불사신 바바 미노"),
        ("Takeda cavalry", "다케다 기마대"),
        ("Oda Clan", "오다 가문"),
        ("Tokugawa forces", "도쿠가와군"),
        ("Mikatagahara", "미카타가하라"),
        ("capital", "교토"),
        ("defeat in detail", "각개격파"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "entire first sixty-seven visible B136 queue coordinates because "
        "no approved Base prefill exists in the slice; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record "
        "fragment array was manually reviewed as auxiliary context, while "
        "the JP-only Ieyasu record was reviewed from its complete assembly "
        "and adjacent Mikatagahara sequence; completed Base objective, "
        "battle-command and taunting rows are used only as independent "
        "semantic and terminology references because none of the thirty-"
        "seven PK records has a raw, literal or operand-masked Base match; "
        "the historical names Baba Mino, Takeda, Oda, Tokugawa, Ieyasu and "
        "Mikatagahara retain established project forms, and pincer attack, "
        "formation, flank, provocation and defeat-in-detail terminology is "
        "normalized; objective labels remain concise while dialogue "
        "preserves each commanding, taunting, enraged, formal, modest, "
        "regretful, astonished or defiant register; colour tags, inline "
        "person, force and unit tokens, protected full-width and ASCII "
        "spaces, line breaks, particles, punctuation, terminators, complete "
        "record arity, pins, reverse overlays, two-run reproduction, tamper "
        "rejection, outside-scope identity, reciprocal S1413 and S1414 "
        "decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=11,
    pins={
        "expected_queue_universe_sha256":
        "9875C5BDFC630EE0ACB5EB425F8ADE458E850FCAF249DD388A37E7336B631D1B",
        "expected_queue_slice_sha256":
        "2810FB28A26ABA43F4F71039564A111990A9BB9F6CC5CDA5B5936EF12208E80D",
        "expected_prefilled_coordinate_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256":
        "2810FB28A26ABA43F4F71039564A111990A9BB9F6CC5CDA5B5936EF12208E80D",
        "expected_source_target_sha256":
        "4FFEFAD6252531A54A55045B9F612DCBC5785385D08CABCCA793492C317FBD4B",
        "expected_current_target_sha256":
        "86DE486F82C32A100ADBE8665B2C5175DCDE84355DD2E20983FA88A2FDEC3F70",
        "expected_context_corpus_sha256":
        "02EB336E27DC8BD87228E49E57CB46F10056DE13C4F4FFCC4BDFE71D3A645836",
        "expected_gap_contract_sha256":
        "69F648801F5E0FEE81EF94857519B0C9E31C564685B1FAEE7B6A11EBE63EF104",
        "expected_boundary_sha256":
        "C77FC687623844D2B472523B9FFCB36832C36EBC42136458D023F30CE9F2443E",
        "expected_runtime_control_sha256":
        "333E357C933F373ED5F3ABDBF189697AF560D85F1058F3BB297A3564217AF6F6",
        "expected_base_search_sha256":
        "70ABC299A3D64A2693F0CA183FEA502EC8E582E6FC2103DBD74C65F98E073F07",
        "expected_complete_assembly_sha256":
        "315A7D3174C14CDC85ED8C2989E8182E908C85ABF9219B60C0C67D932E82FB98",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "FFD16109088E5AB3BE4FDFB60E92D0DD13F4F9A41022947BFD00B3D6C406E5C0",
        "expected_terminology_policy_sha256":
        "82436495F5101622AA4E32184B4B93ACD7C1726FC242291E2E2678BC8B4C974A",
        "expected_translation_policy_sha256":
        "82B6A4F67470B3EB26A44F6357156EB3223A4984F557EB535E076A3DFBDC4C56",
        "expected_candidate_sha256":
        "134536EDC63DB75FE9C796551A7F8FBC21E23DC2960022C4A1A8271B3C767DFB",
        "expected_combined_slice_candidate_sha256":
        "134536EDC63DB75FE9C796551A7F8FBC21E23DC2960022C4A1A8271B3C767DFB",
        "expected_combined_changed_literal_count": 11,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B136_S1412",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B136_S1412.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B136_S1413.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B136_S1414.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B136",
    "queue_row_count": 96,
    "queue_visible_count": 198,
    "queue_first": "17:58:0",
    "queue_last": "17:153:0",
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
    key = (17, 99)
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
    for donor_coordinate in SEMANTIC_BASE_CONTEXT[99]:
        donor = base_rows.get(donor_coordinate)
        if (
            donor is None
            or donor.get("semantic_review") != "approved"
            or donor.get("runtime_review")
            not in {"verified", "not_required"}
        ):
            raise RuntimeError(
                "segment 1412 Base context drifted: "
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
            f"segment 1412 neighbor companion drifted: {neighbor_coordinate}"
        )
    assembled = (TRANSLATIONS["17:99:0"], expected)
    if (
        len(source_literals) != EXPECTED_ARITY[99]
        or raw_matches != EXPECTED_BASE_RAW_MATCHES[99]
        or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[99]
        or masked_matches != EXPECTED_BASE_MASKED_MATCHES[99]
        or assembled != (
            "내가 바로",
            "다!\n병사 한 명도 이곳을 지나게 두지 않겠다!",
        )
    ):
        raise RuntimeError("segment 1412 boundary assembly drifted")
    return (
        tuple(base_evidence) + ((
            99,
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
            99,
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
