#!/usr/bin/env python3
"""Build source-redacted PK B133 segment 1404 residual decisions."""

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

TARGET_RECORD_IDS = tuple(range(2502, 2529))
MAIN_RECORD_IDS = tuple(range(2502, 2528))
TARGET_COORDINATES = (
    "15:2502:0",
    "15:2502:1",
    "15:2503:0",
    "15:2503:1",
    "15:2504:0",
    "15:2504:1",
    "15:2504:2",
    "15:2504:3",
    "15:2504:4",
    "15:2505:0",
    "15:2505:1",
    "15:2505:2",
    "15:2505:3",
    "15:2506:0",
    "15:2506:1",
    "15:2506:2",
    "15:2507:0",
    "15:2507:1",
    "15:2507:2",
    "15:2508:0",
    "15:2509:0",
    "15:2509:1",
    "15:2510:0",
    "15:2510:1",
    "15:2511:0",
    "15:2511:1",
    "15:2511:2",
    "15:2512:0",
    "15:2513:0",
    "15:2514:0",
    "15:2515:0",
    "15:2516:0",
    "15:2516:1",
    "15:2517:0",
    "15:2517:1",
    "15:2517:2",
    "15:2517:3",
    "15:2518:0",
    "15:2518:1",
    "15:2518:2",
    "15:2519:0",
    "15:2519:1",
    "15:2519:2",
    "15:2520:0",
    "15:2520:1",
    "15:2521:0",
    "15:2521:1",
    "15:2522:0",
    "15:2522:1",
    "15:2522:2",
    "15:2523:0",
    "15:2523:1",
    "15:2523:2",
    "15:2523:3",
    "15:2524:0",
    "15:2524:2",
    "15:2525:0",
    "15:2525:2",
    "15:2525:3",
    "15:2526:0",
    "15:2526:1",
    "15:2526:2",
    "15:2527:0",
    "15:2527:1",
    "15:2527:2",
    "15:2527:3",
    "15:2528:0",
)
MAIN_TARGET_COORDINATES = TARGET_COORDINATES[:-1]
TRANSLATIONS = {
    "15:2502:0": (
        "의 원정군에 맞서려면,\n"
        "적의 병량을 줄이는 것이 어떻겠습니까"
    ),
    "15:2502:1": (
        "?\n우리 시노비라면 치중대를 습격할 수 있습니다"
    ),
    "15:2503:0": (
        "의 원정군에 맞서려면,\n"
        "조금이라도 적의 병량을 줄입시다"
    ),
    "15:2503:1": "!\n적은 비용으로도 우리 시노비라면……",
    "15:2504:0": "의 시노비에게 치중대를 습격당했습니다",
    "15:2504:1": "……!\n",
    "15:2504:2": "부대 등",
    "15:2504:3": "개 부대의\n휴대 군량이 줄었습니다",
    "15:2504:4": "……",
    "15:2505:0": (
        "의 군이 운용하는 치중대를 습격하는 데 성공했습니다"
    ),
    "15:2505:1": "!\n",
    "15:2505:2": "부대 등",
    "15:2505:3": "개 부대의\n휴대 군량이 줄었습니다",
    "15:2506:0": (
        "의 군이 운용하는 치중대를 습격하는 데 실패했습니다"
    ),
    "15:2506:1": "……\n",
    "15:2506:2": "의 시노비에게 저지당했습니다",
    "15:2507:0": "부대 주변에서\n",
    "15:2507:1": "의 시노비를 발견했습니다",
    "15:2507:2": (
        "!\n다행히 습격하기 전에 쫓아낸 듯합니다"
    ),
    "15:2508:0": "부대의 치중대를 습격하는 데 성공",
    "15:2509:0": "부대 등",
    "15:2509:1": "개 부대의 치중대를 습격하는 데 성공",
    "15:2510:0": "치중대가 습격당해",
    "15:2510:1": "부대가 피해를 입음",
    "15:2511:0": "치중대가 습격당해",
    "15:2511:1": "부대 등",
    "15:2511:2": "개 부대가 피해를 입음",
    "15:2512:0": "이(가) 치중대 습격에 실패",
    "15:2513:0": "의 치중대 습격을 저지",
    "15:2514:0": "이(가) 치중대 습격에 실패",
    "15:2515:0": "의 치중대 습격을 저지",
    "15:2516:0": (
        "일대의 병사들에게\n제 무예를 전수하겠습니다"
    ),
    "15:2516:1": (
        "\n다음 전투에서는 정예병으로 거듭날 것입니다"
    ),
    "15:2517:0": "등",
    "15:2517:1": (
        "개 성의 병사들에게\n제 무예를 전수했습니다"
    ),
    "15:2517:2": "\n다가올 전투에서의 활약을",
    "15:2517:3": "기대해 주십시오",
    "15:2518:0": "이(가)",
    "15:2518:1": "에서",
    "15:2518:2": "을(를) 실시",
    "15:2519:0": "이(가)",
    "15:2519:1": "개 성에서",
    "15:2519:2": "을(를) 실시",
    "15:2520:0": (
        "을(를) 위압하는 일이라면 맡겨 주십시오\n이"
    ),
    "15:2520:1": (
        "의 몸에 흐르는 명문의 피에\n"
        "감히 거역할 자는 그리 많지 않을 것입니다"
    ),
    "15:2521:0": (
        "을(를) 위압하는 일이라면 맡겨 주십시오\n이"
    ),
    "15:2521:1": (
        "의 몸에 흐르는 명문의 피에\n"
        "감히 거역할 자는 그리 많지 않을 것입니다"
    ),
    "15:2522:0": "에서는\n병사 일부가",
    "15:2522:1": (
        "의 권위를 두려워해\n흩어져 달아났습니다"
    ),
    "15:2522:2": "……",
    "15:2523:0": "등",
    "15:2523:1": "개 성에서는\n병사 일부가",
    "15:2523:2": (
        "의 권위를 두려워해\n흩어져 달아났습니다"
    ),
    "15:2523:3": "……",
    "15:2524:0": "적 영지 위압은 성공적으로 끝났습니다",
    "15:2524:2": (
        "에서는\n우리 가문을 두려워한 병사들이 흩어진 듯합니다"
    ),
    "15:2525:0": "적 영지 위압은 성공적으로 끝났습니다",
    "15:2525:2": "등",
    "15:2525:3": (
        "개 성에서는\n"
        "우리 가문을 두려워한 병사들이 흩어진 듯합니다"
    ),
    "15:2526:0": "이(가)",
    "15:2526:1": "의",
    "15:2526:2": "에 성공",
    "15:2527:0": "이(가)",
    "15:2527:1": "을(를) 비롯한",
    "15:2527:2": "개 성의",
    "15:2527:3": "에 성공",
    "15:2528:0": "의",
}
EXPECTED_ARITY = {
    2502: 2,
    2503: 2,
    2504: 5,
    2505: 4,
    2506: 3,
    2507: 3,
    2508: 1,
    2509: 2,
    2510: 2,
    2511: 3,
    2512: 1,
    2513: 1,
    2514: 1,
    2515: 1,
    2516: 2,
    2517: 4,
    2518: 3,
    2519: 3,
    2520: 2,
    2521: 2,
    2522: 3,
    2523: 4,
    2524: 3,
    2525: 4,
    2526: 3,
    2527: 4,
    2528: 3,
}
PREFILL_COMPANION_COORDINATES: tuple[str, ...] = ()
PREFILL_COMPANION_DONOR: dict[str, str] = {}
HIDDEN_CURRENT_COMPANION_COORDINATES = (
    "15:2524:1",
    "15:2525:1",
)
NEIGHBOR_COMPANION_TRANSLATIONS = {
    "15:2528:1": "에 의해,",
    "15:2528:2": "의 병력이 감소",
}
EXACT_BASE_DONOR = {
    2526: (15, 1357),
    2527: (15, 1446),
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ("14:118:1", "15:262:1")
        for record_id in range(2502, 2508)
    },
    **{
        record_id: ("14:118:1",)
        for record_id in range(2508, 2516)
    },
    2516: ("7:1398:0", "15:1496:0", "15:1496:1", "15:1496:2"),
    2517: ("7:1398:0", "15:1496:0", "15:1496:1", "15:1496:2"),
    2518: ("15:1357:0", "15:1357:1", "15:1357:2"),
    2519: ("15:1446:0", "15:1446:1", "15:1446:2", "15:1446:3"),
    2520: ("2:617:0", "2:617:1", "2:617:2", "2:617:3"),
    2521: ("2:617:0", "2:617:1", "2:617:2", "2:617:3"),
    2522: ("2:171:0", "2:171:1", "14:6:7"),
    2523: ("2:171:0", "2:171:1", "14:6:7"),
    2524: ("2:171:0", "2:171:1", "14:6:7"),
    2525: ("2:171:0", "2:171:1", "14:6:7"),
    2526: (),
    2527: (),
    2528: ("6:4113:0", "6:4113:1", "6:4113:2"),
}
EXPECTED_BASE_RAW_MATCHES = {
    **{record_id: () for record_id in range(2502, 2526)},
    2526: ((15, 806), (15, 1357), (15, 1445)),
    2527: ((15, 1446),),
    2528: (),
}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    2502: ((700, 1096), ("025032",)),
    2503: ((514,), ("025032",)),
    2504: ((538, 628), ("025032", "024833", "0232")),
    2505: ((538, 610), ("025032", "024833", "0232")),
    2506: ((538, 634), ("025032", "025032")),
    2507: ((538,), ("024833", "025032")),
    2508: ((), ("024633",)),
    2509: ((), ("024633", "0232")),
    2510: ((), ("024633",)),
    2511: ((), ("024633", "0232")),
    2512: ((), ("024633",)),
    2513: ((), ("025032",)),
    2514: ((), ("024633",)),
    2515: ((), ("025032",)),
    2516: ((148,), ("026432",)),
    2517: ((538, 508, 1174, 412), ("026432", "0232")),
    2518: ((), ("024633", "026432", "023C")),
    2519: ((), ("024633", "0232", "023C")),
    2520: ((1, 160), ("025132",)),
    2521: ((1, 160), ("025132",)),
    2522: ((634,), ("026432", "025032")),
    2523: ((634,), ("026432", "0232", "025032")),
    2524: ((628,), ("026432",)),
    2525: ((628,), ("026432", "0232")),
    2526: ((), ("024633", "026432", "023C")),
    2527: ((), ("024633", "026432", "0232", "023C")),
    2528: ((), ("025032", "023C", "026432")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1404,
    queue_start=67,
    queue_stop=134,
    slice_first="15:2502:0",
    slice_last="15:2528:0",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(
        HIDDEN_CURRENT_COMPANION_COORDINATES
    ),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(
        700, 1096, 514, 538, 628, 610, 634,
        148, 508, 1174, 412, 1, 160,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(2460, 2585)
    ),
    speaker_style=(
        (2502, "formal_shinobi_supply_raid_proposal"),
        (2503, "formal_low_cost_supply_raid_proposal"),
        (2504, "formal_enemy_supply_raid_damage_report"),
        (2505, "formal_successful_supply_raid_report"),
        (2506, "formal_failed_supply_raid_report"),
        (2507, "formal_enemy_shinobi_detection_report"),
        (2508, "concise_system_supply_raid_success"),
        (2509, "concise_system_multi_supply_raid_success"),
        (2510, "concise_system_supply_raid_damage"),
        (2511, "concise_system_multi_supply_raid_damage"),
        (2512, "concise_system_supply_raid_failure"),
        (2513, "concise_system_supply_raid_prevention"),
        (2514, "concise_system_supply_raid_failure"),
        (2515, "concise_system_supply_raid_prevention"),
        (2516, "formal_martial_instruction_proposal"),
        (2517, "formal_martial_instruction_completion"),
        (2518, "concise_system_action_execution"),
        (2519, "concise_system_multi_action_execution"),
        (2520, "formal_noble_blood_intimidation_proposal"),
        (2521, "formal_noble_blood_intimidation_proposal"),
        (2522, "formal_authority_desertion_report"),
        (2523, "formal_multi_authority_desertion_report"),
        (2524, "formal_intimidation_success_report"),
        (2525, "formal_multi_intimidation_success_report"),
        (2526, "concise_system_action_success"),
        (2527, "concise_system_multi_action_success"),
        (2528, "concise_system_troop_reduction"),
    ),
    terminology_policy=(
        ("shinobi", "시노비"),
        ("baggage train", "치중대"),
        ("provisions", "병량"),
        ("carried provisions", "휴대 군량"),
        ("military arts", "무예"),
        ("elite troops", "정예병"),
        ("authority", "권위"),
        ("intimidation", "위압"),
        ("our house", "우리 가문"),
        ("dynamic particles", "이(가), 을(를), 의"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "entire B133 queue slice from zero-based ordinals sixty-seven "
        "through one hundred thirty-three because no approved Base prefill "
        "exists in the slice; pristine PK JP is authoritative and every "
        "populated EN, SC and TC same-record fragment array was manually "
        "reviewed as auxiliary context; two source-identical system records "
        "reuse selected approved completed Base Korean assemblies, while "
        "the remaining PK-specific supply-raiding, martial-instruction and "
        "authority-intimidation records use completed Base rows only as "
        "semantic and glossary context and never inherit Base runtime or VM "
        "state; the right-boundary troop-reduction record is completed with "
        "two manually reviewed companion fragments owned by optional "
        "segment 1405 and any landed neighbor decision must match that "
        "assembly; two source-identical hidden newlines remain "
        "non-translatable while participating in complete assembly; "
        "shinobi, baggage trains, provisions, carried provisions, martial "
        "arts, elite troops, authority, intimidation and our house retain "
        "the established historical project wording; formal proposals and "
        "reports remain distinct from concise system notifications; calls, "
        "inline officer, castle, force, action and count tokens, protected "
        "outer whitespace, line breaks, particles, punctuation, ellipses, "
        "terminators, complete record arity, pins, reverse overlays, "
        "two-run reproduction, tamper rejection, outside-scope identity, "
        "optional neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=50,
    pins={
        "expected_queue_universe_sha256": (
            "A1FCF27A1B837763A4D3B023E5EB2F988DC4BD5C61350EC2AAAA89A92ECA6396"
        ),
        "expected_queue_slice_sha256": (
            "C98B5FD86838F3E5730DBC5E4B74933CBC7B6C9AEC1AACC32BFA4E1FB9AB988C"
        ),
        "expected_prefilled_coordinate_sha256": (
            "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
        ),
        "expected_prefill_slice_context_sha256": (
            "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
        ),
        "expected_target_coordinate_sha256": (
            "C98B5FD86838F3E5730DBC5E4B74933CBC7B6C9AEC1AACC32BFA4E1FB9AB988C"
        ),
        "expected_source_target_sha256": (
            "3A946A926A1C88730FC9D8A6B05AB89F979E6CAA339EBF6BFC658BBD71EC4A67"
        ),
        "expected_current_target_sha256": (
            "E7203DEF27EC9A9BC8CED05F245CD896C58F07619867C4EA6634095E1312858F"
        ),
        "expected_context_corpus_sha256": (
            "074BFBC4DF1748AB72681F9DF929F87C9CD07F07E8C8BC98B45338ED41867311"
        ),
        "expected_gap_contract_sha256": (
            "8D15F718291C1F53F0EDC51EBC51E4190F41CDA685BD93E2E4C54AA54EE27FA7"
        ),
        "expected_boundary_sha256": (
            "F19EB5E9DC5D9010F8AC5B275DFDC792EBAD2F3CDB7B5CD53A26AD0BC0BACB30"
        ),
        "expected_runtime_control_sha256": (
            "D6D2F13918BB3DE7E4F18DF97A14E257852D4C4A2E581EF1F485B98C0D8E17B0"
        ),
        "expected_base_search_sha256": (
            "516304B568506FCC38A8E023BB3CA765719AB8FE25DC4CFF072E9D3AF630C2EC"
        ),
        "expected_complete_assembly_sha256": (
            "A843C33FC28D427159A41C3EC4FC67E2E5FF47A0D0C007385638711C63FC52D6"
        ),
        "expected_call_graph_sha256": (
            "92FF982915C8E31EC557B8F871636CE6D5F203C4D4D7550C7A1E93B0B2F43374"
        ),
        "expected_speaker_style_sha256": (
            "C3E214CF4CC0A513F96CE91806EA580F40B1BA65475B97AEAC6CAD2291ACEA44"
        ),
        "expected_terminology_policy_sha256": (
            "EDC3B240106E779D87BD996A479B7FB74AAC8D7D169E398B29CEA0E7FA9B540B"
        ),
        "expected_translation_policy_sha256": (
            "3214F7056D1DEE165A8E02ECA2CEA647EC2875B68F4B7987A619C5433092CFAE"
        ),
        "expected_candidate_sha256": (
            "31D200321E94E6A5AE9116D28969B3EA19759570459428F0367C1585EA44DE82"
        ),
        "expected_combined_slice_candidate_sha256": (
            "31D200321E94E6A5AE9116D28969B3EA19759570459428F0367C1585EA44DE82"
        ),
        "expected_combined_changed_literal_count": 50,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B133_S1404",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B133_S1404.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B133_S1403.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B133_S1405.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B133",
    "queue_row_count": 73,
    "queue_visible_count": 197,
    "queue_first": "15:2475:0",
    "queue_last": "15:2547:2",
})


def base_and_assembly_evidence_with_boundary(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Guard the in-slice records plus the split right-boundary record."""
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
    key = (15, 2528)
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
    if (
        len(source_literals) != EXPECTED_ARITY[2528]
        or raw_matches != EXPECTED_BASE_RAW_MATCHES[2528]
        or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[2528]
        or masked_matches != EXPECTED_BASE_MASKED_MATCHES[2528]
    ):
        raise RuntimeError("segment 1404 Base search drifted: 2528")

    references: list[tuple[Any, ...]] = []
    for donor_coordinate in SEMANTIC_BASE_CONTEXT[2528]:
        donor = base_rows.get(donor_coordinate)
        if (
            donor is None
            or donor.get("semantic_review") != "approved"
            or donor.get("runtime_review")
            not in {"verified", "not_required"}
        ):
            raise RuntimeError(
                "segment 1404 Base context drifted: "
                f"{donor_coordinate}"
            )
        references.append((
            donor_coordinate,
            str(donor["translation"]),
            str(donor["semantic_review"]),
            str(donor["runtime_review"]),
            "semantic_only",
            "runtime_vm_not_inherited",
        ))

    assembled = [TRANSLATIONS["15:2528:0"]]
    owners = ["segment_manual_multilingual"]
    for coordinate, expected in NEIGHBOR_COMPANION_TRANSLATIONS.items():
        neighbor = neighbor_rows.get(coordinate)
        if (
            neighbor is not None
            and (
                neighbor.get("translation") != expected
                or neighbor.get("semantic_review") != "approved"
                or neighbor.get("runtime_review") != "pending"
            )
        ):
            raise RuntimeError(
                "segment 1404 neighbor companion drifted: "
                f"{coordinate}"
            )
        assembled.append(expected)
        owners.append("optional_next_segment_manual_companion")
    if tuple(assembled) != (
        "의",
        "에 의해,",
        "의 병력이 감소",
    ):
        raise RuntimeError("segment 1404 boundary assembly drifted")

    base_tail = ((
        2528,
        COMMON.sha256_bytes(source.data),
        source_literals,
        current_literals,
        tuple(value.hex().upper() for value in COMMON.gap_bytes(source)),
        raw_matches,
        literal_matches,
        masked_matches,
        tuple(references),
        "semantic_context_only",
    ),)
    assembly_tail = ((
        2528,
        tuple(owners),
        tuple(assembled),
        None,
        COMMON.CORE.runtime_controls(source),
        COMMON.CORE.runtime_controls(current),
        "base_semantics_only",
        "base_runtime_vm_not_inherited",
    ),)
    return (
        tuple(base_evidence) + base_tail,
        tuple(assembly_evidence) + assembly_tail,
    )


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


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
