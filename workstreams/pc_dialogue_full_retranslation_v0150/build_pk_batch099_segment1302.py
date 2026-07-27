#!/usr/bin/env python3
"""Build source-redacted PK B099 segment 1302 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_BASE_ASSEMBLY = COMMON.BASE.base_and_assembly_evidence
_ORIGINAL_BASE_READ_JSONL = COMMON.BASE.read_jsonl

CROSS_COORDINATE = "9:3970:0"
CROSS_TRANSLATION = "적군은 성하에서 방어 태세를 갖추고 있습니다"
CROSS_DONOR_LABEL = "manual-neighbor:pk_msggame_B099_S1301"

TARGET_RECORD_IDS = (
    3970,
    3971,
    3972,
    3973,
    3974,
    3975,
    3976,
    3977,
    3978,
    3979,
    3980,
    3981,
    3982,
    3983,
    3984,
    3985,
    3986,
    3988,
    3993,
    3994,
    3995,
    3996,
    3997,
    3998,
    3999,
    4000,
    4001,
    4002,
    4003,
    4004,
)

TARGET_COORDINATES = (
    "9:3970:2",
    "9:3970:3",
    "9:3970:4",
    "9:3970:5",
    *(
        f"9:{record_id}:{literal_id}"
        for record_id in range(3971, 3983)
        for literal_id in range(2)
    ),
    "9:3983:0",
    "9:3983:1",
    "9:3984:0",
    "9:3984:1",
    "9:3985:0",
    "9:3986:0",
    "9:3986:1",
    "9:3988:0",
    "9:3993:0",
    "9:3993:1",
    "9:3993:2",
    "9:3994:0",
    "9:3994:1",
    "9:3994:2",
    "9:3995:0",
    "9:3996:0",
    "9:3997:0",
    "9:3997:1",
    "9:3998:0",
    "9:3999:0",
    "9:4000:0",
    "9:4001:0",
    "9:4002:0",
    "9:4003:0",
    "9:4004:0",
)

DEFENSE_TRANSLATIONS = {
    f"9:{record_id}:0": "이곳의 방비는 충분히 갖춰졌습니다"
    for record_id in range(3971, 3983)
}
DEFENSE_TRANSLATIONS.update({
    f"9:{record_id}:1": (
        "\n설비를 활용해 아군을 교대로 쉬게 하면서\n"
        "적의 맹공을 끝까지 버텨 냅시다"
    )
    for record_id in range(3971, 3983)
})

_TRANSLATIONS = {
    "9:3970:2": "이(가) 지키는 저 「",
    "9:3970:3": "」…\n강력한 설비로 보이니",
    "9:3970:4": ",",
    "9:3970:5": "주의하십시오",
    **DEFENSE_TRANSLATIONS,
    "9:3983:0": "수성하기에는 다소 불안한 병력",
    "9:3983:1": (
        "이지만…\n어떻게든 적의 맹공을 막아 내면서\n"
        "고립된 적부터 쳐야 합니다"
    ),
    "9:3984:0": "오랜 주둔으로 적병이 지쳐 보입니다",
    "9:3984:1": (
        "\n설비를 지키며 시간을 잘 끌 수 있다면\n"
        "적의 퇴각도 머지않았을 것입니다"
    ),
    "9:3985:0": (
        "성하의 방비가 갖춰지기도 전에\n"
        "이곳까지 침공당하다니…\n"
        "설비가 없는 곳은 두텁게 지켜야 합니다"
    ),
    "9:3986:0": "이만한 전력 차이라면 성의 함락을 피하기 어렵습니다",
    "9:3986:1": "만…\n적어도 놈들에게 한 방은 먹여 줍시다",
    "9:3988:0": "본성을 파괴하는 것이\n승리로 가는 지름길이다",
    "9:3993:0": "라 불리는―",
    "9:3993:1": ",\n바로―",
    "9:3993:2": "이(가) 베어 쓰러뜨렸노라!",
    "9:3994:0": "라 불리는―",
    "9:3994:1": ",\n바로―",
    "9:3994:2": "이(가) 베어 쓰러뜨렸어!",
    "9:3995:0": "이 설비는 버린다!\n우선 대열을 가다듬어야 한다",
    "9:3996:0": "설비를 포기하겠습니다\n대열을 가다듬어야 합니다",
    "9:3997:0": "반격할 채비가 필요하다\n",
    "9:3997:1": "로 향하라!",
    "9:3998:0": "이대로는 고립된다\n아군에 맞춰 퇴각한다!",
    "9:3999:0": "성문으로 급히 가라!\n적을 성 안에 들이지 마라!",
    "9:4000:0": "성문으로 서두르겠습니다!\n우선 성부터 지켜야 합니다…",
    "9:4001:0": "이곳은 더 버티지 못한다…\n후방 설비에서 적을 막는다!",
    "9:4002:0": "이곳은 더 버티지 못합니다\n한 걸음 물러나 지키겠습니다",
    "9:4003:0": "여기서는 물러난다!\n우선 대열을 가다듬어야 한다",
    "9:4004:0": "우선 물러나겠습니다\n대열을 가다듬어야 합니다",
}
TRANSLATIONS = {
    coordinate: _TRANSLATIONS[coordinate]
    for coordinate in TARGET_COORDINATES
}

SEMANTIC_BASE_CONTEXT = {
    3970: ("14:55:1", "15:894:0"),
    **{
        record_id: ("8:1003:0", "14:55:1")
        for record_id in range(3971, 3983)
    },
    3983: ("8:1003:0", "7:1458:0"),
    3984: ("9:2477:0", "9:2599:0"),
    3985: ("15:894:0", "14:55:1"),
    3986: ("7:1172:0", "7:1996:0"),
    3988: ("7:528:0", "7:2587:0"),
    3993: ("7:2527:0", "9:768:0", "9:783:1"),
    3994: ("7:2527:0", "9:786:0", "9:786:1", "9:3276:0"),
    3995: ("9:2469:0", "2:257:0"),
    3996: ("9:2469:0", "2:257:0"),
    3997: ("9:1543:0",),
    3998: ("7:1458:0", "7:558:0"),
    3999: ("7:1996:0", "14:55:1"),
    4000: ("7:1996:0", "14:55:1"),
    4001: ("9:587:0", "7:555:1"),
    4002: ("9:587:0", "7:555:1"),
    4003: ("9:2469:0", "2:257:0"),
    4004: ("9:2469:0", "2:257:0"),
}

EXPECTED_CONTROLS_BY_RECORD = {
    3970: ((562, 1096, 1174), ("024833",)),
    **{
        record_id: ((376, 364), ())
        for record_id in range(3971, 3983)
    },
    3983: ((562, 364), ()),
    3984: ((1096, 610), ()),
    3985: ((808,), ()),
    3986: ((1114, 1126, 514), ()),
    3988: ((508,), ()),
    3993: ((), ("02484E", "024833", "024635")),
    3994: ((), ("02484E", "024833", "024635")),
    3995: ((), ()),
    3996: ((), ()),
    3997: ((), ("023C",)),
    3998: ((), ()),
    3999: ((), ()),
    4000: ((), ()),
    4001: ((), ()),
    4002: ((), ()),
    4003: ((), ()),
    4004: ((), ()),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1302,
    queue_start=67,
    queue_stop=134,
    slice_first="9:3970:2",
    slice_last="9:4013:0",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={
        3970: 6,
        **{record_id: 2 for record_id in range(3971, 3985)},
        3985: 1,
        3986: 2,
        3988: 1,
        3993: 3,
        3994: 3,
        3995: 1,
        3996: 1,
        3997: 2,
        3998: 1,
        3999: 1,
        4000: 1,
        4001: 1,
        4002: 1,
        4003: 1,
        4004: 1,
    },
    prefill_companion_coordinates=(CROSS_COORDINATE,),
    prefill_companion_donor={CROSS_COORDINATE: CROSS_DONOR_LABEL},
    hidden_current_companion_coordinates=("9:3970:1",),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches={record_id: () for record_id in TARGET_RECORD_IDS},
    expected_base_literal_matches={
        record_id: () for record_id in TARGET_RECORD_IDS
    },
    expected_base_masked_matches={
        record_id: () for record_id in TARGET_RECORD_IDS
    },
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(
        562,
        1096,
        1174,
        376,
        364,
        610,
        808,
        1114,
        1126,
        514,
        508,
    ),
    boundary_record_keys=tuple(
        (9, record_id) for record_id in range(3940, 4016)
    ),
    speaker_style=(
        (3970, "formal_dynamic_castle_town_defense_warning"),
        *(
            (record_id, "formal_rotating_defense_endurance_advice")
            for record_id in range(3971, 3983)
        ),
        (3983, "formal_outnumbered_defense_advice"),
        (3984, "formal_enemy_fatigue_assessment"),
        (3985, "formal_unprepared_castle_town_defense"),
        (3986, "resolute_last_resistance_proposal"),
        (3988, "forceful_main_keep_destruction_maxim"),
        (3993, "male_named_enemy_slain_boast"),
        (3994, "female_named_enemy_slain_boast"),
        (3995, "forceful_equipment_abandonment_order"),
        (3996, "polite_equipment_abandonment_report"),
        (3997, "forceful_counterattack_regroup_order"),
        (3998, "forceful_anti_isolation_retreat_order"),
        (3999, "forceful_castle_gate_defense_order"),
        (4000, "polite_castle_gate_defense_report"),
        (4001, "forceful_rear_equipment_fallback_order"),
        (4002, "polite_fallback_defense_report"),
        (4003, "forceful_regrouping_retreat_order"),
        (4004, "polite_regrouping_retreat_report"),
    ),
    terminology_policy=(
        ("castle town", "성하"),
        ("defensive equipment", "설비"),
        ("castle defense", "수성"),
        ("main keep", "본성"),
        ("castle gate", "성문"),
        ("castle fall", "함락"),
        ("enemy onslaught", "맹공"),
        ("rotating rest", "교대로 쉬게 하다"),
        ("enemy withdrawal", "적의 퇴각"),
        ("battle regrouping", "대열을 가다듬다"),
        ("enemy slain", "베어 쓰러뜨리다"),
        ("alias attribution", "라 불리는"),
        ("dynamic particles", "이(가)"),
        ("project ellipsis", "…"),
    ),
    basis=(
        "pristine PK JP is authoritative and all available EN, SC and TC "
        "same-record arrays were manually reviewed; completed Base defense, "
        "equipment, fatigue, castle-fall, retreat and named-enemy victory "
        "rows provide semantic terminology and register references only, "
        "with no Base runtime or VM state inherited; the twelve repeated "
        "defense records share one faithful Korean core while dynamic calls "
        "retain their source speaker variation, and the two named-enemy "
        "boasts reuse the already approved B081 token ordering and male/"
        "female register; split record 3970 preserves its source-identical "
        "hidden newline and requires the approved S1301 first literal as a "
        "manual reciprocal neighbor, never as Base runtime evidence; castle "
        "town, defensive equipment, main keep, gate, withdrawal, regrouping "
        "and slain-enemy terminology, all calls, inline tokens, literal "
        "arity, protected whitespace, line shapes, gaps, terminators, all "
        "fourteen slice prefills, reverse overlays, two-run reproduction, "
        "tamper rejection, outside-scope identity and Steam read-only state "
        "are guarded"
    ),
    expected_changed_literal_count=52,
    pins={
        "expected_queue_universe_sha256":
        "62B1664F152F3E326B2586BA11931EC17A0B4B7D27F0C7C4F0926C945B94B6F1",
        "expected_queue_slice_sha256":
        "2850D5B71E50F7CAA2B60CACB8ED7800807F35AFFF65C480164C3D693AA39DA3",
        "expected_prefilled_coordinate_sha256":
        "42FE6B3B064EE46D97971824495EEFC7935FCA829BE5E52702D8CDFECBED17C3",
        "expected_prefill_slice_context_sha256":
        "9B4F30DE54126A80430F6E2FD7B389CBE13C90A35A1D158C4DCAE80BEDFC2D32",
        "expected_target_coordinate_sha256":
        "53B4ABE3BF7FFB3E5071AD251F9807807C228803D499FD239A1A87A9722D0FB4",
        "expected_source_target_sha256":
        "E68EF8FCFFD10EDD17996D02F68D5B67902E0BF7FFDC4D80AB9AA4D5BBFFB3B9",
        "expected_current_target_sha256":
        "C014D55303DC9F4476004B67EE2968D586A0EC0EBBE8D3905308FDB29D423980",
        "expected_context_corpus_sha256":
        "849833B4ECD7AF90786293309DEF5DEA1F4971191DA3A0A46C8730220B7B3997",
        "expected_gap_contract_sha256":
        "3425256FA81C242F783D71DF1B5F339115D445EA2A6DC515E1E482A5163569D1",
        "expected_boundary_sha256":
        "3E549778DD5448305A02E76083617339E5E10D20FC9DA4DDCB87B41CAA67CF7D",
        "expected_runtime_control_sha256":
        "6B5518AFD8AE723577B2AD5F4417209877A866BE3124E945CDF4C3D7DCF96756",
        "expected_base_search_sha256":
        "D41A657A957E44FB1EC548D35A2BE1A8AE826DF006140C2A1CDB9967DAAADF92",
        "expected_complete_assembly_sha256":
        "FFC5029825916B57F018A79021161756A40965F0D02810AA002D2AB1E0F8642A",
        "expected_call_graph_sha256":
        "7FAAEA328796EF6FBB28230BBE0A2867558F9756BEDB0DD7B1B30A76D170A369",
        "expected_speaker_style_sha256":
        "E5D8FC4675A123ED047F695B7C3103E6D20675CE3A236C4E017B7D77AA3DD5E4",
        "expected_terminology_policy_sha256":
        "8A3582E0F2920EA65AD3393B1B0102484AF78C77BA9FD2A6D15F6B9D61760877",
        "expected_translation_policy_sha256":
        "CCAEF16F0AC89C453AAFA7FADA0039543ED9D360A836FD33F520349E163F7A3C",
        "expected_candidate_sha256":
        "76CCE744DE9DF8EF853A5C26875CE037A9BE29363AA6D0667BAA919073DD7334",
        "expected_combined_slice_candidate_sha256":
        "3E4E6B800EB4242B8EE847B965B6B2CD1F131764C555DB1D0CFF8E36E2E5191F",
        "expected_combined_changed_literal_count": 66,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B099_S1302",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B099_S1302.private.v1.jsonl"
    ),
    "optional_neighbors": tuple(
        COMMON.DECISIONS_ROOT
        / f"pk_msggame_B099_S{segment}.private.v1.jsonl"
        for segment in (1301, 1303)
    ),
    "queue_batch_id": "pk_msggame-B099",
    "queue_row_count": 140,
    "queue_visible_count": 200,
    "queue_first": "9:3943:0",
    "queue_last": "9:4079:0",
})


def base_and_assembly_evidence(
    prepared: object,
    records_by_label: dict[tuple[str, str], object],
) -> tuple[tuple[object, ...], tuple[object, ...]]:
    """Model the first literal of split record 3970 as a manual neighbor."""

    neighbor_path = (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B099_S1301.private.v1.jsonl"
    )
    if neighbor_path.is_file():
        neighbor_rows = {
            str(row["coordinate"]): row
            for row in _ORIGINAL_BASE_READ_JSONL(neighbor_path)
        }
        neighbor = neighbor_rows.get(CROSS_COORDINATE)
        if (
            neighbor is None
            or neighbor.get("semantic_review") != "approved"
            or neighbor.get("runtime_review") != "pending"
            or str(neighbor.get("translation")) != CROSS_TRANSLATION
        ):
            raise RuntimeError(
                "segment 1302 reciprocal S1301 translation drifted"
            )

    synthetic_neighbor = {
        "coordinate": CROSS_COORDINATE,
        "translation": CROSS_TRANSLATION,
        "semantic_review": "approved",
        "runtime_review": "pending",
        "base_exact_reuse_prefill": {
            "base_coordinate": CROSS_DONOR_LABEL,
            "runtime_promotion_authorized": False,
        },
    }

    def compatible_read_jsonl(path: Path) -> list[dict[str, object]]:
        rows = _ORIGINAL_BASE_READ_JSONL(path)
        if path != COMMON.PREFILL:
            return rows
        if any(str(row["coordinate"]) == CROSS_COORDINATE for row in rows):
            raise RuntimeError("segment 1302 cross coordinate became prefilled")
        return [*rows, synthetic_neighbor]

    original_read_jsonl = COMMON.BASE.read_jsonl
    COMMON.BASE.read_jsonl = compatible_read_jsonl
    try:
        base, assembly = _ORIGINAL_BASE_ASSEMBLY(
            prepared, records_by_label
        )
    finally:
        COMMON.BASE.read_jsonl = original_read_jsonl

    adjusted: list[tuple[object, ...]] = []
    for evidence in assembly:
        if evidence[0] != 3970:
            adjusted.append(evidence)
            continue
        owners = list(evidence[1])
        if (
            owners[0] != "base_exact_prefill_runtime_pending"
            or owners[1] != "source_identical_hidden_newline"
        ):
            raise RuntimeError(
                "segment 1302 split-record ownership drifted"
            )
        owners[0] = "neighbor_segment_manual_runtime_pending"
        adjusted.append((evidence[0], tuple(owners), *evidence[2:]))
    return base, tuple(adjusted)


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 9)
    setattr(
        COMMON.BASE,
        "base_and_assembly_evidence",
        base_and_assembly_evidence,
    )


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
