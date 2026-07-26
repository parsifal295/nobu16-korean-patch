#!/usr/bin/env python3
"""Build source-redacted PK B079 segment 1243 residual decisions."""

from pathlib import Path

from build_pk_batch079_common import make_config, run


SCRIPT = Path(__file__).resolve()
ACTIVATION_RECORD_IDS = (439, 440, 441)
TARGET_RECORD_IDS = (
    *ACTIVATION_RECORD_IDS,
    443, 445, 447, 449, 451, 458, 460, 462,
    467, 469, 471, 473, 476, 478, 479, 480, 485,
)
ACTIVATION_MATCHES = tuple((9, record_id) for record_id in range(383, 398))
CONFIG = make_config(
    script=SCRIPT,
    segment=1243,
    queue_start=134,
    queue_stop=199,
    slice_first="9:439:0",
    slice_last="9:486:0",
    target_coordinates=(
        "9:439:0",
        "9:439:1",
        "9:440:0",
        "9:440:1",
        "9:441:0",
        "9:441:1",
        "9:443:0",
        "9:443:1",
        "9:445:0",
        "9:447:0",
        "9:449:0",
        "9:451:0",
        "9:458:0",
        "9:460:0",
        "9:462:0",
        "9:467:0",
        "9:469:0",
        "9:471:0",
        "9:473:0",
        "9:476:0",
        "9:478:0",
        "9:479:0",
        "9:480:0",
        "9:480:1",
        "9:485:0",
    ),
    translations={
        "9:439:0": "이(가)",
        "9:439:1": "을(를) 발동",
        "9:440:0": "이(가)",
        "9:440:1": "을(를) 발동",
        "9:441:0": "이(가)",
        "9:441:1": "을(를) 발동",
        "9:443:0": "적군이",
        "9:443:1": "을(를) 발동",
        "9:445:0": "이(가) 설비를 제압",
        "9:447:0": "에게 설비를 빼앗김",
        "9:449:0": "이(가) 본성을 파괴",
        "9:451:0": "에게 본성을 빼앗김",
        "9:458:0": "설비 발동에 실패",
        "9:460:0": "을(를) 포함한 총",
        "9:462:0": "을(를) 포함한 총",
        "9:467:0": "을(를) 포함한 총",
        "9:469:0": "을(를) 포함한 총",
        "9:471:0": "을(를) 포함한 총",
        "9:473:0": "을(를) 포함한 총",
        "9:476:0": "적군이\n설비 발동에 실패",
        "9:478:0": "을(를) 포함한 총",
        "9:479:0": "적군,",
        "9:480:0": "적군,",
        "9:480:1": "을(를) 포함한 총",
        "9:485:0": "을(를) 포함한 총",
    },
    target_record_ids=TARGET_RECORD_IDS,
    target_record_blocks={record_id: 9 for record_id in TARGET_RECORD_IDS},
    expected_arity={
        439: 2,
        440: 2,
        441: 2,
        443: 2,
        445: 1,
        447: 1,
        449: 1,
        451: 1,
        458: 1,
        460: 2,
        462: 2,
        467: 2,
        469: 2,
        471: 2,
        473: 2,
        476: 1,
        478: 2,
        479: 2,
        480: 3,
        485: 2,
    },
    prefill_companion_coordinates=(
        "9:460:1",
        "9:462:1",
        "9:467:1",
        "9:469:1",
        "9:471:1",
        "9:473:1",
        "9:478:1",
        "9:479:1",
        "9:480:2",
        "9:485:1",
    ),
    prefill_companion_donor={
        "9:460:1": "9:411:1",
        "9:462:1": "9:413:1",
        "9:467:1": "9:418:1",
        "9:469:1": "9:420:1",
        "9:471:1": "9:422:1",
        "9:473:1": "9:424:1",
        "9:478:1": "9:411:1",
        "9:479:1": "9:429:1",
        "9:480:2": "9:430:2",
        "9:485:1": "9:435:1",
    },
    hidden_current_companion_coordinates=(),
    semantic_base_context={
        **{
            record_id: ("9:383:0", "9:383:1")
            for record_id in ACTIVATION_RECORD_IDS
        },
        443: ("9:399:0", "9:399:1"),
        445: ("14:55:1", "2:204:0"),
        447: ("14:55:1", "7:616:0"),
        449: ("6:4191:0", "6:4291:1"),
        451: ("7:616:0", "7:604:0"),
        458: ("9:409:0", "14:55:1"),
        460: ("9:411:0", "9:411:1"),
        462: ("9:413:0", "9:413:1"),
        467: ("9:418:0", "9:418:1"),
        469: ("9:420:0", "9:420:1"),
        471: ("9:422:0", "9:422:1"),
        473: ("9:424:0", "9:424:1"),
        476: ("9:426:0", "14:55:1"),
        478: ("9:411:0", "9:411:1"),
        479: ("9:429:0", "9:429:1"),
        480: ("9:430:0", "9:430:1", "9:430:2"),
        485: ("9:435:0", "9:435:1"),
    },
    expected_base_raw_matches={
        **{
            record_id: ACTIVATION_MATCHES
            for record_id in ACTIVATION_RECORD_IDS
        },
        443: ((9, 399),),
        445: (),
        447: (),
        449: (),
        451: (),
        458: (),
        460: ((9, 411), (9, 428)),
        462: ((9, 413),),
        467: ((9, 418),),
        469: ((9, 420),),
        471: ((9, 422),),
        473: ((9, 424), (9, 441)),
        476: (),
        478: ((9, 411), (9, 428)),
        479: ((9, 429),),
        480: ((9, 430),),
        485: ((9, 435),),
    },
    expected_base_literal_matches={
        **{
            record_id: ACTIVATION_MATCHES
            for record_id in ACTIVATION_RECORD_IDS
        },
        443: ((9, 399),),
        445: (),
        447: (),
        449: (),
        451: (),
        458: (),
        460: ((9, 411), (9, 428)),
        462: ((9, 413),),
        467: ((9, 418),),
        469: ((9, 420),),
        471: ((9, 422),),
        473: ((9, 424), (9, 441)),
        476: (),
        478: ((9, 411), (9, 428)),
        479: ((9, 429),),
        480: ((9, 430),),
        485: ((9, 435),),
    },
    expected_base_masked_matches={
        **{
            record_id: ACTIVATION_MATCHES
            for record_id in ACTIVATION_RECORD_IDS
        },
        443: ((9, 399),),
        445: (),
        447: (),
        449: (),
        451: (),
        458: (),
        460: ((9, 411), (9, 428)),
        462: ((9, 413),),
        467: ((9, 418),),
        469: ((9, 420),),
        471: ((9, 422),),
        473: ((9, 424), (9, 441)),
        476: (),
        478: ((9, 411), (9, 428)),
        479: ((9, 429),),
        480: ((9, 430),),
        485: ((9, 435),),
    },
    expected_controls_by_record={
        **{
            record_id: ((), ("02AA32", "023C"))
            for record_id in ACTIVATION_RECORD_IDS
        },
        443: ((), ("023C",)),
        445: ((), ("02AA32",)),
        447: ((), ("02AA32",)),
        449: ((), ("02AA32",)),
        451: ((), ("02AA32",)),
        458: ((), ()),
        460: ((), ("02AC32", "0232")),
        462: ((), ("02AC32", "0232")),
        467: ((), ("02AC32", "0232")),
        469: ((), ("02AC32", "0232")),
        471: ((), ("02AC32", "0232")),
        473: ((), ("02AC32", "0232")),
        476: ((), ()),
        478: ((), ("02AC32", "0232")),
        479: ((), ("02AC32",)),
        480: ((), ("02AC32", "0232")),
        485: ((), ("02AC32", "0232")),
    },
    source_call_roots=(),
    boundary_record_keys=tuple(
        (9, record_id) for record_id in range(438, 487)
    ),
    speaker_style=(
        *tuple(
            (record_id, "battle_facility_activation_notification")
            for record_id in ACTIVATION_RECORD_IDS
        ),
        (443, "enemy_facility_activation_notification"),
        (445, "facility_capture_notification"),
        (447, "facility_loss_notification"),
        (449, "citadel_destruction_notification"),
        (451, "citadel_loss_notification"),
        (458, "facility_activation_failure_notification"),
        (460, "falling_rocks_unit_notification"),
        (462, "encouragement_unit_notification"),
        (467, "downhill_charge_unit_notification"),
        (469, "decoy_troop_retreat_notification"),
        (471, "unit_interdiction_notification"),
        (473, "local_warrior_reinforcement_notification"),
        (476, "enemy_facility_activation_failure_notification"),
        (478, "falling_rocks_unit_notification"),
        (479, "enemy_encouragement_notification"),
        (480, "enemy_unit_encouragement_notification"),
        (485, "downhill_advance_unit_notification"),
    ),
    terminology_policy=(
        ("facility", "설비"),
        ("citadel", "본성"),
        ("capture", "제압"),
        ("loss", "빼앗김"),
        ("activate", "발동"),
        ("decoy troop stratagem", "위병계"),
        ("local warrior", "토착 무사"),
        ("encouragement", "격려"),
        ("dynamic particles", "이(가)·을(를)·에게"),
    ),
    basis=(
        "pristine PK JP is authoritative and complete EN, SC and TC siege "
        "context was manually reviewed; completed Base battle, facility, "
        "citadel and activation-failure rows provide semantic, terminology and "
        "register references only, with no Base runtime or VM state inherited; "
        "all twenty complete records preserve established citadel and facility "
        "terms, historically appropriate local-warrior and decoy-stratagem "
        "wording, dynamic particles, inline tokens, protected whitespace, gaps "
        "and mutual boundaries; two-run reproduction, tamper rejection, reverse "
        "overlays, outside-scope identity and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=25,
    pins={
        "expected_queue_universe_sha256":
        "BE5A0E8B4C4FB397A096B8EDBA465B2CDFA0AB180AD5BF66EE0743C15693F2A2",
        "expected_queue_slice_sha256":
        "8B132750D95ABF583D480CEA571E14ACFEF1E351531DA5F4F6C9DA5968DC9E1D",
        "expected_prefilled_coordinate_sha256":
        "A985CBB0AA61C9AE09D813E20A9B9844C2B624F8EF5E6301CACF8F8309D4AF87",
        "expected_prefill_slice_context_sha256":
        "7CA52F72C4D8CE0C7539F9729F3D1BA637EA9D2735B61E2BAFFE0F5A8595096F",
        "expected_target_coordinate_sha256":
        "0972DF53B304C5C238815418E4E3BA2EBBA95A55D8BC4A92B365E22E51A7AC5E",
        "expected_source_target_sha256":
        "CE583D30D924DE9149A43DB455A002E63DF39EE088EDB3120E81088F58254A42",
        "expected_current_target_sha256":
        "F6C6C593FF6A4EBCA9A735E23D223D4584C51ADFFCDDF11FB01F37059AE33362",
        "expected_context_corpus_sha256":
        "6BC0EDB140EBB450CBC2BCD06C8E80405AA66981052E4521B38197A643291A60",
        "expected_gap_contract_sha256":
        "268440FA4E7BDFC76FBAB6A99C304548F99DE8079E156C8F79BFDF56D300E7DB",
        "expected_boundary_sha256":
        "E5C7CB77E1791BE5C89A5774164F37B895596F602D91AC50EA0574CF56165D21",
        "expected_runtime_control_sha256":
        "64F82AA16FCC85707FA825C516CCC08C7C238EA3E47DD4285B7A4D81DA9E90D6",
        "expected_base_search_sha256":
        "1218E1E9FE520C6285E617C4DB17F178DD4704315521C45D3A113A97AA08F84F",
        "expected_complete_assembly_sha256":
        "1EBA583E9D698C1E3A9FE0325E12F89BF4AC314293645A254DB3C1D4C142F629",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "9D2D8783498202759D5F15D854ACE4E8CB1D4F12787B2DACC2849768099616F5",
        "expected_terminology_policy_sha256":
        "37B458F13DCD7849B0E9AA64881B5D52573E28F55F1ED98D90E533B2AAF97723",
        "expected_translation_policy_sha256":
        "FD8994B3F8D74F5606EF4859208BACF3364045F3B32C5D1A0F9A2919CDEA0369",
        "expected_candidate_sha256":
        "7DADC267B903387D372307E49FD18610EF549BFC30DB82044DC58CF128F46FC9",
        "expected_combined_slice_candidate_sha256":
        "78B89A3846098ED15B7AEA1CA2C9EEBAA58D1EAE10F0ACBFCA5BD1C8529DB209",
        "expected_combined_changed_literal_count": 61,
    },
)


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
