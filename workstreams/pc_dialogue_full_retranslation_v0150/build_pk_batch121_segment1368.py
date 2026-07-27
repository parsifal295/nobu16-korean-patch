#!/usr/bin/env python3
"""Build source-redacted PK B121 segment 1368 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:1417:1",
    "15:1418:0",
    "15:1420:0",
    "15:1422:0",
    "15:1423:0",
    "15:1425:2",
    "15:1425:3",
    "15:1425:4",
    "15:1426:0",
    "15:1426:1",
    "15:1427:0",
    "15:1427:1",
    "15:1432:0",
    "15:1432:1",
    "15:1433:0",
    "15:1433:1",
    "15:1435:1",
    "15:1436:0",
    "15:1438:0",
    "15:1440:0",
    "15:1441:0",
    "15:1443:1",
    "15:1444:0",
    "15:1444:1",
)
TRANSLATIONS = {
    "15:1417:1": "놈을\n",
    "15:1418:0": "불초,",
    "15:1420:0": "은(는)",
    "15:1422:0": "이름은",
    "15:1423:0": ",",
    "15:1425:2": "가\n",
    "15:1425:3": "시",
    "15:1425:4": "인가?",
    "15:1426:0": "이(가)",
    "15:1426:1": "을(를) 등용",
    "15:1427:0": "이(가)",
    "15:1427:1": "에 실패",
    "15:1432:0": "은(는)",
    "15:1432:1": "(이)라 하오\n",
    "15:1433:0": "은(는)",
    "15:1433:1": "(이)라 하오\n",
    "15:1435:1": "놈을\n",
    "15:1436:0": "불초,",
    "15:1438:0": "은(는)",
    "15:1440:0": "이름은",
    "15:1441:0": ",",
    "15:1443:1": "인가?",
    "15:1444:0": "이(가)",
    "15:1444:1": "을(를) 등용",
}
TARGET_RECORD_IDS = (
    1417,
    1418,
    1420,
    1422,
    1423,
    1425,
    1426,
    1427,
    1432,
    1433,
    1435,
    1436,
    1438,
    1440,
    1441,
    1443,
    1444,
)
EXPECTED_ARITY = {
    **{
        record_id: 3
        for record_id in (
            1417,
            1418,
            1420,
            1423,
            1432,
            1433,
            1435,
            1436,
            1438,
            1441,
        )
    },
    **{
        record_id: 2
        for record_id in (
            1422,
            1426,
            1427,
            1440,
            1443,
            1444,
        )
    },
    1425: 5,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1417:0",
    "15:1417:2",
    "15:1418:1",
    "15:1418:2",
    "15:1420:1",
    "15:1420:2",
    "15:1422:1",
    "15:1423:1",
    "15:1423:2",
    "15:1425:0",
    "15:1425:1",
    "15:1432:2",
    "15:1433:2",
    "15:1435:0",
    "15:1435:2",
    "15:1436:1",
    "15:1436:2",
    "15:1438:1",
    "15:1438:2",
    "15:1440:1",
    "15:1441:1",
    "15:1441:2",
    "15:1443:0",
)
PREFILL_COMPANION_DONOR = {
    "15:1417:0": "15:349:0",
    "15:1417:2": "15:349:2",
    "15:1418:1": "15:350:1",
    "15:1418:2": "15:350:2",
    "15:1420:1": "15:352:1",
    "15:1420:2": "15:352:2",
    "15:1422:1": "15:354:1",
    "15:1423:1": "15:355:1",
    "15:1423:2": "15:355:2",
    "15:1425:0": "15:1410:0",
    "15:1425:1": "15:1410:1",
    "15:1432:2": "15:346:2",
    "15:1433:2": "15:347:2",
    "15:1435:0": "15:349:0",
    "15:1435:2": "15:349:2",
    "15:1436:1": "15:350:1",
    "15:1436:2": "15:350:2",
    "15:1438:1": "15:352:1",
    "15:1438:2": "15:352:2",
    "15:1440:1": "15:354:1",
    "15:1441:1": "15:355:1",
    "15:1441:2": "15:355:2",
    "15:1443:0": "15:1428:0",
}
EXACT_BASE_DONOR = {
    1417: (15, 1402),
    1418: (15, 1403),
    1420: (15, 1405),
    1422: (15, 1407),
    1423: (15, 1408),
    1425: (15, 1410),
    1426: (15, 1411),
    1427: (15, 1412),
    1432: (15, 1417),
    1433: (15, 1418),
    1435: (15, 1420),
    1436: (15, 1421),
    1438: (15, 1423),
    1440: (15, 1425),
    1441: (15, 1426),
    1443: (15, 1428),
    1444: (15, 1429),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
DECLARATION_A_MATCHES = ((15, 349), (15, 1402), (15, 1420))
DECLARATION_B_MATCHES = ((15, 350), (15, 1403), (15, 1421))
DECLARATION_C_MATCHES = ((15, 352), (15, 1405), (15, 1423))
DECLARATION_D_MATCHES = ((15, 354), (15, 1407), (15, 1425))
DECLARATION_E_MATCHES = ((15, 355), (15, 1408), (15, 1426))
EMPLOYMENT_MATCHES = (
    (15, 373),
    (15, 1411),
    (15, 1429),
    (15, 1527),
)
EXPECTED_BASE_RAW_MATCHES = {
    1417: DECLARATION_A_MATCHES,
    1418: DECLARATION_B_MATCHES,
    1420: DECLARATION_C_MATCHES,
    1422: DECLARATION_D_MATCHES,
    1423: DECLARATION_E_MATCHES,
    1425: (),
    1426: EMPLOYMENT_MATCHES,
    1427: ((15, 1412), (15, 2180)),
    1432: ((15, 346), (15, 1399), (15, 1417)),
    1433: ((15, 347), (15, 1400), (15, 1418)),
    1435: DECLARATION_A_MATCHES,
    1436: DECLARATION_B_MATCHES,
    1438: DECLARATION_C_MATCHES,
    1440: DECLARATION_D_MATCHES,
    1441: DECLARATION_E_MATCHES,
    1443: (),
    1444: EMPLOYMENT_MATCHES,
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    1425: ((15, 1410),),
    1443: ((15, 1428),),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
EXPECTED_CONTROLS_BY_RECORD = {
    1417: ((8,), ("024635",)),
    1418: ((8,), ("024633",)),
    1420: ((1, 8), ("024633",)),
    1422: ((), ("024633",)),
    1423: ((1, 8), ("024633",)),
    1425: ((538, 568, 700, 1066), ("024833",)),
    1426: ((), ("024633", "024733")),
    1427: ((), ("024633", "023C")),
    1432: ((1, 8), ("024633",)),
    1433: ((1, 8), ("024633",)),
    1435: ((8,), ("024635",)),
    1436: ((8,), ("024633",)),
    1438: ((1, 8), ("024633",)),
    1440: ((), ("024633",)),
    1441: ((1, 8), ("024633",)),
    1443: ((34, 748), ()),
    1444: ((), ("024633", "024733")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1368,
    queue_start=67,
    queue_stop=134,
    slice_first="15:1416:1",
    slice_last="15:1444:1",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(8, 1, 538, 568, 700, 1066, 34, 748),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1390, 1476)
    ),
    speaker_style=(
        (1417, "formal_ronin_blade_service_declaration"),
        (1418, "formal_ronin_talent_service_declaration"),
        (1420, "archaic_ronin_lifetime_service_declaration"),
        (1422, "blunt_ronin_service_declaration"),
        (1423, "polite_feminine_ronin_service_declaration"),
        (1425, "formal_ronin_employment_proposal"),
        (1426, "system_ronin_employment_success"),
        (1427, "system_ronin_employment_failure"),
        (1432, "archaic_ronin_warrior_service_declaration"),
        (1433, "archaic_ronin_hegemony_service_declaration"),
        (1435, "formal_ronin_blade_service_declaration"),
        (1436, "formal_ronin_talent_service_declaration"),
        (1438, "archaic_ronin_lifetime_service_declaration"),
        (1440, "blunt_ronin_service_declaration"),
        (1441, "polite_feminine_ronin_service_declaration"),
        (1443, "formal_ronin_employment_proposal"),
        (1444, "system_ronin_employment_success"),
    ),
    terminology_policy=(
        ("ronin", "낭인"),
        ("service", "사관"),
        ("employment", "등용"),
        ("warrior", "무사"),
        ("hegemony", "패업"),
        ("blade", "칼날"),
        ("unworthy self-reference", "불초"),
        ("talent", "재주"),
        ("dynamic subject particle", "이(가), 은(는)"),
        ("dynamic object particle", "을(를)"),
        ("project comma", ","),
        ("project question mark", "?"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between B121 queue coordinates sixty-seven through one "
        "hundred thirty-three and the approved Base prefill; pristine PK JP "
        "is authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; all seventeen "
        "complete records reuse approved completed Base Korean assemblies "
        "selected by raw, literal and operand-masked source identity, with "
        "explicit donors fixing the intended completed assembly among "
        "duplicate ronin declarations; Base runtime and VM state are never "
        "inherited; ronin service, employment, warrior honor, hegemony, "
        "blades, humble self-reference, talent and dynamic particles retain "
        "established historical project wording and formal, archaic, blunt, "
        "feminine or system registers; calls, inline officer, faction, "
        "proposal and operation tokens, protected outer whitespace, line "
        "breaks, commas, question marks, terminators, complete record arity, "
        "all forty-three slice prefills, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, optional "
        "neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=12,
    pins={
        "expected_queue_universe_sha256": (
            "E0DCC642542229DF2D59AE5B9CF620BF65B79C0C779075E71922EB0C2D1919EA"
        ),
        "expected_queue_slice_sha256": (
            "C0028766FE67AE521F5B686C3BDC0273418E8327A0CB2789925EC5D0F3B9FB31"
        ),
        "expected_prefilled_coordinate_sha256": (
            "B321B5278A41C925DE309C10B614FCA2BAD5ECDA1F421B6AE5B568A332CAF291"
        ),
        "expected_prefill_slice_context_sha256": (
            "465CE559D8E4B9964FCD376C7E69BF71D351E2E3C94FC27451B87A7057E8EBB5"
        ),
        "expected_target_coordinate_sha256": (
            "9AFFF7E4E1E89F2AA0E1DE136559602C374C44E735807C2726E96EE17DC7DFBB"
        ),
        "expected_source_target_sha256": (
            "6141FDFCDC982722D8A66B0B4DE2F5E4D96C3BB9B7431802D9267757758D993C"
        ),
        "expected_current_target_sha256": (
            "9FFD6BB0B4EB20096381CC75678B39CD0EC951C1FE7E56B6CB91DA11BD47A4E8"
        ),
        "expected_context_corpus_sha256": (
            "C910BF86586144338EA332B83DB8FC645C0A85429B0EC5F87253A347DDC58E42"
        ),
        "expected_gap_contract_sha256": (
            "66AFC527751FEE9993F0B47585210D4BE218543F0F322B02C606BE14A14DDD4B"
        ),
        "expected_boundary_sha256": (
            "5B7D5D501AA8F5B9006441C99B28D047B7F22CC4F1E7A85C24D83C27594D615B"
        ),
        "expected_runtime_control_sha256": (
            "56510E6D6C51995133F9DD0B451EE4E0025D1712E868AE916470D1B2608F7C8E"
        ),
        "expected_base_search_sha256": (
            "A1F9D233FF61B06190B3E615B205F87FC1BC59963E571B72AD8331DFF750A6CA"
        ),
        "expected_complete_assembly_sha256": (
            "1F3E5821C94E5B9DDAEE2A8DAC3099CF80D338FC68504A911F1916443EED93AC"
        ),
        "expected_call_graph_sha256": (
            "30A263F50AD36550C9FC147C97453F0A728864FB5B3628A2056E26786446EEEA"
        ),
        "expected_speaker_style_sha256": (
            "2C2187328803FB102E0EE5CBFBDFF629187D0F1F6F8F7BEBC31444C86E1EF552"
        ),
        "expected_terminology_policy_sha256": (
            "C6B7BD8FB3D0142EE035394B38669AF52EDCCEE8D0C3E949D7AA91F64CD03DB1"
        ),
        "expected_translation_policy_sha256": (
            "7564B329AEF51B84558522A9F9F51B40EFD2028753C671B31CA915FE5ED1B777"
        ),
        "expected_candidate_sha256": (
            "292B295893D6E346CE63826F4EEA0A2A4618D5519AFD31F77DE76894F9CBFF3F"
        ),
        "expected_combined_slice_candidate_sha256": (
            "6BAF353FA16826E7AC7322A2815E32770ACD9F6ADE1866413ECA21412990FD47"
        ),
        "expected_combined_changed_literal_count": 52,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B121_S1368",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B121_S1368.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B121_S1367.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B121_S1369.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B121",
    "queue_row_count": 67,
    "queue_visible_count": 199,
    "queue_first": "15:1400:0",
    "queue_last": "15:1466:3",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
