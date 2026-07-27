#!/usr/bin/env python3
"""Build source-redacted PK B120 segment 1364 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:1343:0",
    "15:1343:2",
    "15:1343:4",
    "15:1344:0",
    "15:1344:2",
    "15:1344:4",
    "15:1345:1",
    "15:1345:2",
    "15:1346:1",
    "15:1346:2",
    "15:1347:1",
    "15:1348:1",
    "15:1349:0",
    "15:1349:1",
    "15:1349:3",
    "15:1350:0",
    "15:1352:0",
    "15:1353:0",
    "15:1353:2",
    "15:1355:2",
    "15:1356:0",
    "15:1356:1",
    "15:1356:2",
    "15:1357:0",
    "15:1359:0",
    "15:1359:1",
    "15:1359:2",
    "15:1359:3",
)
TRANSLATIONS = {
    "15:1343:0": "·",
    "15:1343:2": "증가\n·",
    "15:1343:4": "감소",
    "15:1344:0": "·",
    "15:1344:2": "증가\n·",
    "15:1344:4": "감소",
    "15:1345:1": "→",
    "15:1345:2": "에",
    "15:1346:1": "→",
    "15:1346:2": "에",
    "15:1347:1": "증가",
    "15:1348:1": "증가",
    "15:1349:0": "에게 자객을 보내",
    "15:1349:1": "인가\n",
    "15:1349:3": "인가 하고",
    "15:1350:0": "에 자객을 보내",
    "15:1352:0": "맹장·",
    "15:1353:0": "의 성주·",
    "15:1353:2": "……",
    "15:1355:2": "만……",
    "15:1356:0": "우리에게 적 성주 일제 습격을",
    "15:1356:1": "명해 주십시오……\n",
    "15:1356:2": (
        "도 부상자투성이가 되면\n"
        "더는 제대로 싸우지 못할 것입니다"
    ),
    "15:1357:0": "의 성주·",
    "15:1359:0": "습격을 감행한",
    "15:1359:1": "명 가운데,",
    "15:1359:2": "을(를) 비롯한\n",
    "15:1359:3": "명에게 상처를 입혀 주",
}
TARGET_RECORD_IDS = (
    1343,
    1344,
    1345,
    1346,
    1347,
    1348,
    1349,
    1350,
    1352,
    1353,
    1355,
    1356,
    1357,
    1359,
)
EXPECTED_ARITY = {
    1343: 5,
    1344: 5,
    1345: 3,
    1346: 3,
    1347: 2,
    1348: 2,
    1349: 4,
    1350: 2,
    1352: 4,
    1353: 3,
    1355: 3,
    1356: 3,
    1357: 3,
    1359: 5,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1343:1",
    "15:1343:3",
    "15:1344:1",
    "15:1344:3",
    "15:1345:0",
    "15:1346:0",
    "15:1347:0",
    "15:1348:0",
    "15:1349:2",
    "15:1350:1",
    "15:1352:1",
    "15:1352:2",
    "15:1352:3",
    "15:1353:1",
    "15:1355:0",
    "15:1355:1",
    "15:1357:1",
    "15:1357:2",
    "15:1359:4",
)
PREFILL_COMPANION_DONOR = {
    "15:1343:1": "15:1335:1",
    "15:1343:3": "15:1335:1",
    "15:1344:1": "15:1335:1",
    "15:1344:3": "15:1335:1",
    "15:1345:0": "15:1337:0",
    "15:1346:0": "15:1337:0",
    "15:1347:0": "15:1339:0",
    "15:1348:0": "15:1339:0",
    "15:1349:2": "15:1341:2",
    "15:1350:1": "15:1342:1",
    "15:1352:1": "15:1344:1",
    "15:1352:2": "15:1344:2",
    "15:1352:3": "15:1344:3",
    "15:1353:1": "15:1345:1",
    "15:1355:0": "15:1347:0",
    "15:1355:1": "15:1347:1",
    "15:1357:1": "15:1348:1",
    "15:1357:2": "15:1348:2",
    "15:1359:4": "15:1348:2",
}
EXACT_BASE_DONOR = {
    1343: (15, 1335),
    1344: (15, 1335),
    1345: (15, 1337),
    1346: (15, 1337),
    1347: (15, 1339),
    1348: (15, 1339),
    1349: (15, 1341),
    1350: (15, 1342),
    1352: (15, 1344),
    1353: (15, 1345),
    1355: (15, 1347),
    1357: (15, 1348),
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ()
        for record_id in TARGET_RECORD_IDS
        if record_id not in {1356, 1359}
    },
    1356: (
        "15:1341:0",
        "15:1341:2",
        "15:1348:1",
        "15:1348:2",
    ),
    1359: (
        "15:1348:1",
        "15:1348:2",
    ),
}
EXPECTED_BASE_RAW_MATCHES = {
    1343: ((15, 1335), (15, 1336)),
    1344: ((15, 1335), (15, 1336)),
    1345: ((15, 1337), (15, 1338)),
    1346: ((15, 1337), (15, 1338)),
    1347: ((15, 1339), (15, 1340)),
    1348: ((15, 1339), (15, 1340)),
    1349: (),
    1350: (),
    1352: (),
    1353: (),
    1355: ((15, 1347),),
    1356: (),
    1357: (),
    1359: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    1345: (
        (15, 716),
        (15, 979),
        (15, 1337),
        (15, 1338),
        (15, 1453),
    ),
    1346: (
        (15, 716),
        (15, 979),
        (15, 1337),
        (15, 1338),
        (15, 1453),
    ),
    1349: ((15, 1341),),
    1350: ((15, 1342),),
    1352: ((15, 1344),),
    1353: ((15, 1345),),
    1357: ((15, 1348),),
}
EXPECTED_BASE_MASKED_MATCHES = {
    **EXPECTED_BASE_LITERAL_MATCHES,
    1345: ((15, 1337), (15, 1338)),
    1346: ((15, 1337), (15, 1338)),
}
EXPECTED_CONTROLS_BY_RECORD = {
    1343: ((), ("026E32", "0232", "026432", "0232")),
    1344: ((), ("026E32", "0232", "026432", "0232")),
    1345: ((), ("026E32", "0232", "0233")),
    1346: ((), ("026E32", "0232", "0233")),
    1347: ((), ("026E32", "0232")),
    1348: ((), ("026E32", "0232")),
    1349: ((1078, 1048), ("024833", "026432")),
    1350: ((1078,), ("026432",)),
    1352: ((1066,), ("024833", "026432")),
    1353: ((610,), ("026432", "024833")),
    1355: ((226,), ("026432",)),
    1356: ((1174, 610), ("025032",)),
    1357: ((628, 610, 730), ("026432", "024833")),
    1359: ((628, 610, 730), ("0233", "024833", "0232")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1364,
    queue_start=0,
    queue_stop=67,
    slice_first="15:1326:0",
    slice_last="15:1359:4",
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
    source_call_roots=(1078, 1048, 1066, 610, 226, 1174, 628, 730),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(1320, 1371)
    ),
    speaker_style=(
        (1343, "system_troop_transfer_summary"),
        (1344, "system_troop_transfer_summary"),
        (1345, "system_troop_change"),
        (1346, "system_troop_change"),
        (1347, "system_troop_increase"),
        (1348, "system_troop_increase"),
        (1349, "formal_assassination_proposal"),
        (1350, "formal_assassination_proposal"),
        (1352, "covert_assassination_proposal"),
        (1353, "covert_poisoning_proposal"),
        (1355, "covert_poisoning_proposal"),
        (1356, "formal_mass_assassination_proposal"),
        (1357, "confident_assassination_success"),
        (1359, "confident_mass_assassination_success"),
    ),
    terminology_policy=(
        ("troops", "병력"),
        ("assassin", "자객"),
        ("castle lord", "성주"),
        ("brave general", "맹장"),
        ("castle defense", "수성"),
        ("poison", "독"),
        ("wounded", "부상자"),
        ("assault", "습격"),
        ("dynamic object particle", "을(를)"),
        ("project middle dot", "·"),
        ("project ellipsis", "……"),
        ("project arrow", "→"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between the first sixty-seven visible B120 queue "
        "coordinates and the approved Base prefill; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; twelve complete "
        "records reuse approved completed Base Korean assemblies selected "
        "by raw, literal and operand-masked source identity, while two "
        "PK-only mass-assassination records use completed Base assassination "
        "and injury wording as semantic context; Base runtime and VM state "
        "are never inherited; troops, assassins, castle lords, brave "
        "generals, castle defense, poison, wounded soldiers, assaults, "
        "dynamic particles and formal, covert or confident registers retain "
        "established historical project wording; calls, inline officer, "
        "castle, faction, old and new troop values, counts and proposal "
        "tokens, protected outer whitespace, line breaks, middle dots, "
        "ellipses, arrows, terminators, complete record arity, all thirty-"
        "nine slice prefills, pins, reverse overlays, two-run reproduction, "
        "tamper rejection, outside-scope identity, optional neighbor "
        "decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=11,
    pins={
        "expected_queue_universe_sha256": (
            "F31FED1CD112AA0ADB2BFBEEC7F459040B9E5892A5E59BE751060D0B8D50E138"
        ),
        "expected_queue_slice_sha256": (
            "DE9D8BB20902FBEBA7259D25198A27D65BA6CA58C9BD2A31D40134BE749CDF55"
        ),
        "expected_prefilled_coordinate_sha256": (
            "E1E50F66FCEB65935954CD908B26376F29EC59BB3082ED8BC34F547945C48705"
        ),
        "expected_prefill_slice_context_sha256": (
            "7047AC7B98DEF32CA3B310D756860A68BBBB36BB989C07ECD5435BEC40DD4C35"
        ),
        "expected_target_coordinate_sha256": (
            "59A47D9F38AE8BE0F97C27533296F8743990191ECD58AE205D7D7F9A227295A6"
        ),
        "expected_source_target_sha256": (
            "A69D768A3E01F3C420C149AE6E2E6EF8506F3989BEB8762443B2DDFB7F89B677"
        ),
        "expected_current_target_sha256": (
            "C71F1A9AA06A4708D95F6EEEA4DF0F92B00AE7B8DF028B2C2A74FD4E8C7D5B93"
        ),
        "expected_context_corpus_sha256": (
            "BC631B3C918EB592932A4ACEA0AFB6AA32A42B3FD7E4BDA644E3B6AA6F607FA1"
        ),
        "expected_gap_contract_sha256": (
            "768267443F4759D9E66B89B424F032696D42AE4A4D51735AFA92466ACA54900C"
        ),
        "expected_boundary_sha256": (
            "454694ECAC6BFCEB21CB3995C065A26111D23601DDDCF80D0A6C53891E4BF51D"
        ),
        "expected_runtime_control_sha256": (
            "0DAC8B5389ADD94B8D0B085C08E9F049B6C900441E86076C93A375E54DBB7E37"
        ),
        "expected_base_search_sha256": (
            "40B1ADCA5CFC493D7E7388D2B0695740B14EA8EF3470D49EAA7C6F9F2E8DD196"
        ),
        "expected_complete_assembly_sha256": (
            "020A6EDCE79BDFD725E0E8A2CA73B22EDF91AEC97DFEDBE9F6AC348911586A37"
        ),
        "expected_call_graph_sha256": (
            "3F8BB147ED03A5C7E350F28FE07A66F831D5A22BA835182E1058D3E7482E1470"
        ),
        "expected_speaker_style_sha256": (
            "26B20C4A4B9E3D34D09DDEE1502B349943922837209B801F793986768E5CF3FB"
        ),
        "expected_terminology_policy_sha256": (
            "A620463ABB5B94F36CC0D0098E308EAD3E54AFFC3E87F0461C0F129C5B2FF8FF"
        ),
        "expected_translation_policy_sha256": (
            "4727FB0535601D61C7D4E776F9C4102AB6B3881F4B6994397452E42896394998"
        ),
        "expected_candidate_sha256": (
            "1AD727C0AD66D2D96ACBA9084E669C79664722D41D4F0E60BE97E49FDA3B1959"
        ),
        "expected_combined_slice_candidate_sha256": (
            "24F945CC916BB7470761340787B369456D6699A59006DDD35927EDA0E549CDA2"
        ),
        "expected_combined_changed_literal_count": 40,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B120_S1364",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B120_S1364.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B120_S1365.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B120_S1366.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B120",
    "queue_row_count": 72,
    "queue_visible_count": 200,
    "queue_first": "15:1326:0",
    "queue_last": "15:1399:4",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
