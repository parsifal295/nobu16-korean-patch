#!/usr/bin/env python3
"""Build source-redacted PK B121 segment 1369 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    1446,
    1449,
    1451,
    1454,
    1455,
    1456,
    1457,
    1458,
    1459,
    1460,
    1461,
    1462,
    1463,
    1464,
    1465,
    1466,
)
TARGET_COORDINATES = (
    "15:1446:2",
    "15:1446:3",
    "15:1449:1",
    "15:1451:0",
    "15:1454:0",
    "15:1455:0",
    "15:1455:1",
    "15:1456:0",
    "15:1456:1",
    "15:1456:2",
    "15:1457:1",
    "15:1457:3",
    "15:1458:1",
    "15:1458:2",
    "15:1458:4",
    "15:1459:2",
    "15:1460:0",
    "15:1460:1",
    "15:1460:2",
    "15:1461:0",
    "15:1461:1",
    "15:1461:2",
    "15:1461:3",
    "15:1462:0",
    "15:1462:2",
    "15:1463:0",
    "15:1463:1",
    "15:1464:0",
    "15:1464:1",
    "15:1464:2",
    "15:1465:0",
    "15:1465:1",
    "15:1466:0",
    "15:1466:1",
    "15:1466:2",
)
TRANSLATIONS = {
    "15:1446:2": "\n부디,",
    "15:1446:3": "허락을……",
    "15:1449:1": (
        "\n저 성의 움직임을 봉쇄하고자\n"
        "방화로 병량을 빼앗아 보는 것은 어떻겠습니까?"
    ),
    "15:1451:0": "인근의",
    "15:1454:0": "의",
    "15:1455:0": "을(를) 비롯한",
    "15:1455:1": "개 성에서",
    "15:1456:0": "을(를) 시도한",
    "15:1456:1": "개 성 가운데,\n",
    "15:1456:2": "을(를) 비롯한",
    "15:1457:1": "을(를) 받아\n",
    "15:1457:3": "……",
    "15:1458:1": "을(를) 받아\n",
    "15:1458:2": "을(를) 비롯한",
    "15:1458:4": "……",
    "15:1459:2": "이(가) 벌인",
    "15:1460:0": "이(가)",
    "15:1460:1": "에 대한",
    "15:1460:2": "에 성공",
    "15:1461:0": "이(가)",
    "15:1461:1": "을(를) 비롯한",
    "15:1461:2": "개 성의",
    "15:1461:3": "에 성공",
    "15:1462:0": "에 대한",
    "15:1462:2": "이(가) 부상",
    "15:1463:0": "에 대한",
    "15:1463:1": "에 실패",
    "15:1464:0": "을(를) 비롯한",
    "15:1464:1": "개 성의",
    "15:1464:2": "에 실패",
    "15:1465:0": "의",
    "15:1465:1": "으로 인해,",
    "15:1466:0": "의",
    "15:1466:1": "으로 인해,",
    "15:1466:2": "을(를) 비롯한",
}
EXPECTED_ARITY = {
    1446: 4,
    1449: 2,
    1451: 2,
    1454: 3,
    1455: 4,
    1456: 5,
    1457: 4,
    1458: 5,
    1459: 4,
    1460: 3,
    1461: 4,
    1462: 3,
    1463: 2,
    1464: 3,
    1465: 3,
    1466: 4,
}
PREFILL_COMPANION_COORDINATES = (
    "15:1446:0",
    "15:1446:1",
    "15:1449:0",
    "15:1451:1",
    "15:1454:1",
    "15:1454:2",
    "15:1455:2",
    "15:1455:3",
    "15:1456:3",
    "15:1456:4",
    "15:1457:0",
    "15:1457:2",
    "15:1458:0",
    "15:1458:3",
    "15:1459:0",
    "15:1459:3",
    "15:1462:1",
    "15:1465:2",
    "15:1466:3",
)
PREFILL_COMPANION_DONOR = {
    "15:1446:0": "15:1431:0",
    "15:1446:1": "15:1431:1",
    "15:1449:0": "15:1434:0",
    "15:1451:1": "15:1436:1",
    "15:1454:1": "15:1439:1",
    "15:1454:2": "15:1439:2",
    "15:1455:2": "15:1440:2",
    "15:1455:3": "15:1440:3",
    "15:1456:3": "15:1441:3",
    "15:1456:4": "15:1441:4",
    "15:1457:0": "15:1442:0",
    "15:1457:2": "15:1442:2",
    "15:1458:0": "15:1443:0",
    "15:1458:3": "15:1443:3",
    "15:1459:0": "15:973:0",
    "15:1459:3": "15:973:3",
    "15:1462:1": "15:810:1",
    "15:1465:2": "15:1450:2",
    "15:1466:3": "15:1451:3",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = ("15:1459:1",)
EXACT_BASE_DONOR = {
    1446: (15, 1431),
    1451: (15, 1436),
    1454: (15, 1439),
    1455: (15, 1440),
    1456: (15, 1441),
    1457: (15, 1442),
    1458: (15, 1443),
    1460: (15, 1445),
    1461: (15, 1446),
    1462: (15, 1447),
    1463: (15, 1448),
    1464: (15, 1449),
    1465: (15, 1450),
    1466: (15, 1451),
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ()
        for record_id in TARGET_RECORD_IDS
        if record_id not in (1449, 1459)
    },
    1449: (
        "15:1434:0",
        "15:1434:1",
    ),
    1459: (
        "15:973:0",
        "15:973:2",
        "15:973:3",
    ),
}
OPERATION_SUCCESS_MATCHES = (
    (15, 806),
    (15, 1357),
    (15, 1445),
)
OPERATION_FAILURE_INJURY_MATCHES = (
    (15, 810),
    (15, 1358),
    (15, 1447),
)
COUNTERINTELLIGENCE_LITERAL_MATCHES = (
    (15, 907),
    (15, 973),
    (15, 1276),
    (15, 1365),
    (15, 1444),
    (15, 1485),
)
COUNTERINTELLIGENCE_MASKED_MATCHES = (
    (15, 973),
    (15, 1276),
    (15, 1365),
    (15, 1444),
    (15, 1485),
)
EXPECTED_BASE_RAW_MATCHES = {
    1446: (),
    1449: (),
    1451: ((15, 1436),),
    1454: (),
    1455: (),
    1456: (),
    1457: (),
    1458: (),
    1459: (),
    1460: OPERATION_SUCCESS_MATCHES,
    1461: ((15, 1446),),
    1462: OPERATION_FAILURE_INJURY_MATCHES,
    1463: ((15, 1359), (15, 1448)),
    1464: ((15, 1449),),
    1465: ((15, 1450),),
    1466: ((15, 1451),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    1446: ((15, 1431),),
    1454: ((15, 1439),),
    1455: ((15, 1440),),
    1456: ((15, 1441),),
    1457: ((15, 1442),),
    1458: ((15, 1443),),
    1459: COUNTERINTELLIGENCE_LITERAL_MATCHES,
}
EXPECTED_BASE_MASKED_MATCHES = {
    **EXPECTED_BASE_LITERAL_MATCHES,
    1459: COUNTERINTELLIGENCE_MASKED_MATCHES,
}
EXPECTED_CONTROLS_BY_RECORD = {
    1446: ((1096, 1174), ("026432",)),
    1449: ((568, 730), ("026432",)),
    1451: ((), ("026432",)),
    1454: ((538,), ("026432", "023C")),
    1455: ((538,), ("026432", "0232", "023C")),
    1456: ((538,), ("023C", "0233", "026432", "0232")),
    1457: ((538,), ("025032", "023C", "026432")),
    1458: ((538,), ("025032", "023C", "026432", "0232")),
    1459: ((538, 592), ("026432", "025032", "023C")),
    1460: ((), ("024633", "026432", "023C")),
    1461: ((), ("024633", "026432", "0232", "023C")),
    1462: ((), ("026432", "023C", "024633")),
    1463: ((), ("026432", "023C")),
    1464: ((), ("026432", "0232", "023C")),
    1465: ((), ("025032", "023C", "026432")),
    1466: ((), ("025032", "023C", "026432", "0232")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1369,
    queue_start=134,
    queue_stop=199,
    slice_first="15:1445:0",
    slice_last="15:1466:3",
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
    source_call_roots=(538, 568, 592, 730, 1096, 1174),
    boundary_record_keys=tuple(
        (15, record_id)
        for record_id in range(1430, 1467)
    ),
    speaker_style=(
        (1446, "humble_arson_proposal"),
        (1449, "polite_arson_proposal"),
        (1451, "formal_arson_obstruction_proposal"),
        (1454, "formal_arson_success_report"),
        (1455, "formal_multi_castle_arson_success_report"),
        (1456, "formal_multi_castle_arson_summary"),
        (1457, "formal_arson_damage_report"),
        (1458, "formal_multi_castle_arson_damage_report"),
        (1459, "informal_counterintelligence_report"),
        (1460, "system_arson_success"),
        (1461, "system_multi_castle_arson_success"),
        (1462, "system_arson_failure_injury"),
        (1463, "system_arson_failure"),
        (1464, "system_multi_castle_arson_failure"),
        (1465, "system_arson_damage"),
        (1466, "system_multi_castle_arson_damage"),
    ),
    terminology_policy=(
        ("arson", "방화"),
        ("provisions", "병량"),
        ("defenses", "방비"),
        ("sortie", "출병"),
        ("spy", "간자"),
        ("troops", "병력"),
        ("damage", "피해"),
        ("castle", "성"),
        ("operation", "공작"),
        ("completion", "완수"),
        ("dynamic subject particle", "이(가)"),
        ("dynamic object particle", "을(를)"),
        ("dynamic grouped castle", "을(를) 비롯한"),
        ("project ellipsis", "……"),
        ("project exclamation mark", "!"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between visible B121 queue ordinals 134 through 198 and "
        "the approved Base prefill; pristine PK JP is authoritative and "
        "every populated EN, SC and TC same-record fragment array was "
        "reviewed as auxiliary context; fourteen complete records reuse "
        "approved completed Base Korean assemblies selected by raw, literal "
        "and operand-masked source identity; the changed-call arson proposal "
        "retains approved Base arson, provisions and blockade terminology "
        "while adapting the completed wording to its polite speaker, and the "
        "counterintelligence record preserves its source-identical hidden "
        "newline through visible Base semantic references; Base runtime and "
        "VM state are never inherited; arson, provisions, defenses, sortie, "
        "spy, troops, damage, castle, operation, completion, grouped-castle "
        "wording, dynamic particles, ellipsis and each speaker register "
        "retain established project and historical terminology; direct "
        "calls, inline person, castle, faction, count, operation and value "
        "tokens, protected outer whitespace, newlines, gaps, literal arity, "
        "terminators, all nineteen same-record prefills, the hidden newline, "
        "all thirty slice prefills, complete assemblies, pins, reverse "
        "overlays, two-run reproduction, tamper rejection, outside-scope "
        "identity, reciprocal S1367 and S1368 decisions and Steam read-only "
        "state are guarded"
    ),
    expected_changed_literal_count=25,
    pins={
        "expected_queue_universe_sha256": (
            "E0DCC642542229DF2D59AE5B9CF620BF65B79C0C779075E71922EB0C2D1919EA"
        ),
        "expected_queue_slice_sha256": (
            "A42F790BA7086EB945077FD3EA15A21C9B0445887D681A925F2D53DBA7BC9AE1"
        ),
        "expected_prefilled_coordinate_sha256": (
            "EF217426339DA205D1495786843870AE09986CD1AC5C7972276F89169D57AA7B"
        ),
        "expected_prefill_slice_context_sha256": (
            "1E87DC561069D4DC08788A84B66FA698E6EDC074D4B57D9A9D1E5FDE0A34A054"
        ),
        "expected_target_coordinate_sha256": (
            "28244A7795F56A38EA9B569B45E3A07EB3D21D8E0786E53E5C78E157E819BF13"
        ),
        "expected_source_target_sha256": (
            "8D75C64FEE40BA429D7AE32A6D2FBE54B9153C864912C1AF9F7F7C4717A72640"
        ),
        "expected_current_target_sha256": (
            "DB316BE58DCE8911F9420EC68F3877377A204FD51C66BCCE44FFDAA6B144A524"
        ),
        "expected_context_corpus_sha256": (
            "C910BF86586144338EA332B83DB8FC645C0A85429B0EC5F87253A347DDC58E42"
        ),
        "expected_gap_contract_sha256": (
            "079450AE933040AC994A205D433928BDA9D05A66B1656FE42FACA522B91A463F"
        ),
        "expected_boundary_sha256": (
            "9DD33F8FDD02D7C9B28D1AB5852E4D050968E2F7BBBF67AC0CDEC8EA1FBDDF4A"
        ),
        "expected_runtime_control_sha256": (
            "E15302F884489EAB13F8773BADB94231F403CA85512A126AF2C796A9844C88F5"
        ),
        "expected_base_search_sha256": (
            "ACD00064E0E25B0F15FCE1A9827EF8D36904D2FE781E16A74E9BCB98181D1A93"
        ),
        "expected_complete_assembly_sha256": (
            "2AA871191FC685DC4AA59439DB2A6F7AA77FA9592928CECF5B2FECF5FACCF5D7"
        ),
        "expected_call_graph_sha256": (
            "1C41D55809FA2E574AD4EE59C9D97058216BE2776903044D1E838DF1921893E1"
        ),
        "expected_speaker_style_sha256": (
            "C2785F6A66616F7961584B3267FDB17CFBB0305B6B259AEDE8537852CE68FCA4"
        ),
        "expected_terminology_policy_sha256": (
            "4DDFAD527E7F8286EF35465B74A3284B79621FE29550A3336AC83D87689816E6"
        ),
        "expected_translation_policy_sha256": (
            "A40843D969A5BD75A2CCE1B8FD2D8D5D4A8342BF833A96E3C1700C7B0B79C84F"
        ),
        "expected_candidate_sha256": (
            "43BA561811046246D8A783D3058820DA869ACA6840C0DA234A67420ECD5FD614"
        ),
        "expected_combined_slice_candidate_sha256": (
            "BBDE4EF1030B87369426E4FB6A4DFC5920E8F84D901583DFCCB00E616D4B4961"
        ),
        "expected_combined_changed_literal_count": 50,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B121_S1369",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B121_S1369.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B121_S1367.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B121_S1368.private.v1.jsonl",
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
