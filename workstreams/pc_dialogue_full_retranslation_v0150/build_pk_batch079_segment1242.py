#!/usr/bin/env python3
"""Build source-redacted PK B079 segment 1242 residual decisions."""

from pathlib import Path

from build_pk_batch079_common import make_config, run


SCRIPT = Path(__file__).resolve()
ACTIVATION_RECORD_IDS = tuple(range(427, 439))
TARGET_RECORD_IDS = (
    401, 403, 404, 405, 406, 408, 410, 412,
    413, 414, 415, 416, 417, 418, 420, 421,
    422, 423, 424, 425, *ACTIVATION_RECORD_IDS,
)
ACTIVATION_MATCHES = tuple((9, record_id) for record_id in range(383, 398))
CONFIG = make_config(
    script=SCRIPT,
    segment=1242,
    queue_start=67,
    queue_stop=134,
    slice_first="9:397:0",
    slice_last="9:438:1",
    target_coordinates=(
        "9:401:0",
        "9:401:1",
        "9:403:0",
        "9:403:1",
        "9:404:0",
        "9:405:0",
        "9:406:0",
        "9:406:1",
        "9:408:0",
        "9:410:0",
        "9:412:0",
        "9:413:0",
        "9:413:1",
        "9:414:0",
        "9:414:1",
        "9:415:0",
        "9:415:1",
        "9:416:0",
        "9:417:0",
        "9:418:0",
        "9:420:1",
        "9:421:0",
        "9:422:0",
        "9:422:1",
        "9:423:0",
        "9:423:1",
        "9:424:0",
        "9:425:0",
        "9:427:0",
        "9:427:1",
        "9:428:0",
        "9:428:1",
        "9:429:0",
        "9:429:1",
        "9:430:0",
        "9:430:1",
        "9:431:0",
        "9:431:1",
        "9:432:0",
        "9:432:1",
        "9:433:0",
        "9:433:1",
        "9:434:0",
        "9:434:1",
        "9:435:0",
        "9:435:1",
        "9:436:0",
        "9:436:1",
        "9:437:0",
        "9:437:1",
        "9:438:0",
        "9:438:1",
    ),
    translations={
        "9:401:0": "이(가)",
        "9:401:1": "을(를) 발견",
        "9:403:0": "이(가)",
        "9:403:1": "을(를) 사격",
        "9:404:0": "이(가)",
        "9:405:0": ", 우세",
        "9:406:0": "을(를) 비롯한 총",
        "9:406:1": "개 부대가 우세",
        "9:408:0": "을(를) 비롯한 총",
        "9:410:0": "을(를) 비롯한 총",
        "9:412:0": "을(를) 비롯한 총",
        "9:413:0": ", 출진",
        "9:413:1": "(으)로 진군",
        "9:414:0": "이(가)",
        "9:414:1": "와(과) 교대",
        "9:415:0": "이(가)",
        "9:415:1": "와(과) 교대",
        "9:416:0": "이(가) 패주",
        "9:417:0": "이(가) 패주",
        "9:418:0": "이(가) 전사",
        "9:420:1": "이(가) 부상",
        "9:421:0": "이(가) 궤멸",
        "9:422:0": "이(가)",
        "9:422:1": "을(를) 베어 쓰러뜨림",
        "9:423:0": "이(가)",
        "9:423:1": "을(를) 포박",
        "9:424:0": "이(가) 부상",
        "9:425:0": "을(를) 격파",
        "9:427:0": "이(가)",
        "9:427:1": "을(를) 발동",
        "9:428:0": "이(가)",
        "9:428:1": "을(를) 발동",
        "9:429:0": "이(가)",
        "9:429:1": "을(를) 발동",
        "9:430:0": "이(가)",
        "9:430:1": "을(를) 발동",
        "9:431:0": "이(가)",
        "9:431:1": "을(를) 발동",
        "9:432:0": "이(가)",
        "9:432:1": "을(를) 발동",
        "9:433:0": "이(가)",
        "9:433:1": "을(를) 발동",
        "9:434:0": "이(가)",
        "9:434:1": "을(를) 발동",
        "9:435:0": "이(가)",
        "9:435:1": "을(를) 발동",
        "9:436:0": "이(가)",
        "9:436:1": "을(를) 발동",
        "9:437:0": "이(가)",
        "9:437:1": "을(를) 발동",
        "9:438:0": "이(가)",
        "9:438:1": "을(를) 발동",
    },
    target_record_ids=TARGET_RECORD_IDS,
    target_record_blocks={record_id: 9 for record_id in TARGET_RECORD_IDS},
    expected_arity={
        401: 2,
        403: 2,
        404: 2,
        405: 1,
        406: 2,
        408: 2,
        410: 2,
        412: 2,
        413: 2,
        414: 2,
        415: 2,
        416: 1,
        417: 1,
        418: 1,
        420: 2,
        421: 1,
        422: 2,
        423: 2,
        424: 1,
        425: 1,
        **{record_id: 2 for record_id in ACTIVATION_RECORD_IDS},
    },
    prefill_companion_coordinates=(
        "9:404:1",
        "9:408:1",
        "9:410:1",
        "9:412:1",
        "9:420:0",
    ),
    prefill_companion_donor={
        "9:404:1": "9:360:1",
        "9:408:1": "9:364:1",
        "9:410:1": "9:366:1",
        "9:412:1": "9:368:1",
        "9:420:0": "9:376:0",
    },
    hidden_current_companion_coordinates=(),
    semantic_base_context={
        401: ("9:357:0", "9:357:1"),
        403: ("9:359:0", "9:359:1"),
        404: ("9:360:0", "9:360:1"),
        405: ("9:361:0",),
        406: ("9:362:0", "9:362:1"),
        408: ("9:364:0", "9:364:1"),
        410: ("9:366:0", "9:366:1"),
        412: ("9:368:0", "9:368:1"),
        413: ("9:369:0", "9:369:1"),
        414: ("9:370:0", "9:370:1"),
        415: ("9:371:0", "9:371:1"),
        416: ("9:372:0",),
        417: ("9:373:0",),
        418: ("9:374:0",),
        420: ("9:376:0", "9:376:1"),
        421: ("9:377:0",),
        422: ("9:378:0", "9:378:1"),
        423: ("9:379:0", "9:379:1"),
        424: ("9:380:0",),
        425: ("9:381:0",),
        **{
            record_id: ("9:383:0", "9:383:1")
            for record_id in ACTIVATION_RECORD_IDS
        },
    },
    expected_base_raw_matches={
        401: ((9, 357),),
        403: ((9, 359),),
        404: ((9, 360),),
        405: ((9, 361),),
        406: ((9, 362),),
        408: ((9, 364),),
        410: ((9, 366),),
        412: ((9, 368),),
        413: ((9, 369),),
        414: ((9, 370), (9, 371)),
        415: ((9, 370), (9, 371)),
        416: ((9, 372), (9, 373)),
        417: ((9, 372), (9, 373)),
        418: ((9, 374),),
        420: ((9, 376),),
        421: ((9, 377),),
        422: ((9, 378),),
        423: ((9, 379),),
        424: ((9, 380),),
        425: ((9, 381),),
        **{
            record_id: ACTIVATION_MATCHES
            for record_id in ACTIVATION_RECORD_IDS
        },
    },
    expected_base_literal_matches={
        401: ((9, 357),),
        403: ((9, 359),),
        404: ((9, 360),),
        405: ((9, 361),),
        406: ((9, 362),),
        408: ((9, 364),),
        410: ((9, 366),),
        412: ((9, 368),),
        413: ((9, 369),),
        414: ((9, 370), (9, 371)),
        415: ((9, 370), (9, 371)),
        416: ((9, 372), (9, 373)),
        417: ((9, 372), (9, 373)),
        418: ((9, 374),),
        420: ((9, 376),),
        421: ((7, 487), (9, 377)),
        422: ((9, 378),),
        423: ((9, 379),),
        424: ((9, 380),),
        425: ((7, 549), (9, 381)),
        **{
            record_id: ACTIVATION_MATCHES
            for record_id in ACTIVATION_RECORD_IDS
        },
    },
    expected_base_masked_matches={
        401: ((9, 357),),
        403: ((9, 359),),
        404: ((9, 360),),
        405: ((9, 361),),
        406: ((9, 362),),
        408: ((9, 364),),
        410: ((9, 366),),
        412: ((9, 368),),
        413: ((9, 369),),
        414: ((9, 370), (9, 371)),
        415: ((9, 370), (9, 371)),
        416: ((9, 372), (9, 373)),
        417: ((9, 372), (9, 373)),
        418: ((9, 374),),
        420: ((9, 376),),
        421: ((9, 377),),
        422: ((9, 378),),
        423: ((9, 379),),
        424: ((9, 380),),
        425: ((9, 381),),
        **{
            record_id: ACTIVATION_MATCHES
            for record_id in ACTIVATION_RECORD_IDS
        },
    },
    expected_controls_by_record={
        401: ((), ("02AB32", "02AC32")),
        403: ((), ("02AA32", "02AC32")),
        404: ((), ("02AA32", "02AC32")),
        405: ((), ("02AA32",)),
        406: ((), ("02AA32", "0232")),
        408: ((), ("02AA32", "0232")),
        410: ((), ("02AA32", "0232")),
        412: ((), ("02AA32", "0232")),
        413: ((), ("02AA32", "02AC32")),
        414: ((), ("02AA32", "02AC32")),
        415: ((), ("02AA32", "02AC32")),
        416: ((), ("02AA32",)),
        417: ((), ("02AA32",)),
        418: ((), ("024633",)),
        420: ((), ("024633",)),
        421: ((), ("02AA32",)),
        422: ((), ("024833", "024633")),
        423: ((), ("024833", "024633")),
        424: ((), ("024633",)),
        425: ((), ("02AC32",)),
        **{
            record_id: ((), ("02AA32", "023C"))
            for record_id in ACTIVATION_RECORD_IDS
        },
    },
    source_call_roots=(),
    boundary_record_keys=tuple(
        (9, record_id) for record_id in range(396, 440)
    ),
    speaker_style=(
        (401, "battle_discovery_notification"),
        (403, "battle_ranged_attack_notification"),
        (404, "battle_ranged_damage_notification"),
        (405, "battle_advantage_notification"),
        (406, "battle_unit_advantage_notification"),
        (408, "battle_unit_pressure_notification"),
        (410, "battle_enemy_retreat_notification"),
        (412, "battle_unit_retreat_notification"),
        (413, "battle_march_notification"),
        (414, "battle_unit_replacement_notification"),
        (415, "battle_unit_replacement_notification"),
        (416, "battle_rout_notification"),
        (417, "battle_rout_notification"),
        (418, "battle_death_notification"),
        (420, "battle_injury_after_collapse_notification"),
        (421, "battle_unit_destruction_notification"),
        (422, "battle_defeat_notification"),
        (423, "battle_capture_notification"),
        (424, "battle_injury_notification"),
        (425, "battle_unit_defeat_notification"),
        *tuple(
            (record_id, "battle_facility_activation_notification")
            for record_id in ACTIVATION_RECORD_IDS
        ),
    ),
    terminology_policy=(
        ("unit", "부대"),
        ("advantage", "우세"),
        ("rout", "패주"),
        ("annihilation", "궤멸"),
        ("killed in action", "전사"),
        ("wounded", "부상"),
        ("capture", "포박"),
        ("activate", "발동"),
        ("dynamic particles", "이(가)·을(를)·와(과)·(으)로"),
    ),
    basis=(
        "pristine PK JP is authoritative and complete EN, SC and TC battle "
        "context was manually reviewed; completed Base battle records provide "
        "semantic, terminology and register references only, with no Base "
        "runtime or VM state inherited; all thirty-two complete notification "
        "records preserve historically and tactically distinct rout, "
        "annihilation, death, injury, capture and activation terminology, "
        "dynamic particles, inline tokens, protected whitespace, gaps and "
        "mutual boundaries; two-run reproduction, tamper rejection, reverse "
        "overlays, outside-scope identity and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=50,
    pins={
        "expected_queue_universe_sha256":
        "BE5A0E8B4C4FB397A096B8EDBA465B2CDFA0AB180AD5BF66EE0743C15693F2A2",
        "expected_queue_slice_sha256":
        "35B4E27600CC964EB6DD272A7782BC4D0C5B8CB4A4F4CD1D77BD419D95A08494",
        "expected_prefilled_coordinate_sha256":
        "5C5FA9440193F4B25A1E7224DE7FEFBF90346B85DF81A5DC0E7AF64E087C1F95",
        "expected_prefill_slice_context_sha256":
        "EBC53EF329C7CFBF2EAAE5C198D3D3BBA820535A645CEAA35515BF5F4DBAD728",
        "expected_target_coordinate_sha256":
        "7792F934092CA624CFA9D539386A91DAFA6BCE37F0F4F276A4DF72792F663FF1",
        "expected_source_target_sha256":
        "93C6BA5B21E5482CE980E3B4833CA67935B107B64DEF37DC47C2E8A80C629B45",
        "expected_current_target_sha256":
        "96463E66AD8BF8BDCE59B7DAFE3E38F90564A238434AB009342E8F442B5BC527",
        "expected_context_corpus_sha256":
        "6BC0EDB140EBB450CBC2BCD06C8E80405AA66981052E4521B38197A643291A60",
        "expected_gap_contract_sha256":
        "45072AE38421FACDCAA452D3B760819FC416A0CFD3B76AFF4E051A341547B499",
        "expected_boundary_sha256":
        "AE6B472A4C99C4D66CBB46CAC84D349B089D0A049D6446A9BA10977D0DE06D3B",
        "expected_runtime_control_sha256":
        "FD700C22940C616FF683E861878FF9832588FB5F06C48D42E92EBDCDC2A77D7A",
        "expected_base_search_sha256":
        "D993C20E743F989D479D4DF2CFF0AD3BE4F2B9967E86417B21ADCFF2EA7E2458",
        "expected_complete_assembly_sha256":
        "43E5F4D8E9DCB39EABE830459916E5D8A43C299C4C809C26CC286E7C40C93F68",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "93E40A950C8B2BDEFE72E811E53D2C5DB91E836AAC9161CC278CB2FCD6573AEF",
        "expected_terminology_policy_sha256":
        "0283986F84AFE4AD996D05556F269ACE90854B39EEF55F5248275A723D803360",
        "expected_translation_policy_sha256":
        "CBF09D0E47884896FE8378CE48689632B9EE674C5EBBA4A6A6CFAAE39DDEDB53",
        "expected_candidate_sha256":
        "5AE1748FAC3AD3811A2B4DCE67DE0E44DA3DBA5901199653420D726D9B9C99B4",
        "expected_combined_slice_candidate_sha256":
        "9F0E5EAA7742BF913E31CFA021D81ED6354A5125081FA8ABF518AD9A2EA3B76F",
        "expected_combined_changed_literal_count": 64,
    },
)


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
