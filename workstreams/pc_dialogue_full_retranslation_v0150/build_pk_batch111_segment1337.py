#!/usr/bin/env python3
"""Build source-redacted PK B111 segment 1337 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:283:0",
    "15:284:2",
    "15:290:0",
    "15:291:0",
    "15:293:0",
    "15:297:0",
    "15:298:0",
    "15:299:0",
    "15:300:0",
    "15:313:2",
    "15:316:1",
    "15:317:0",
    "15:317:1",
    "15:319:0",
    "15:319:2",
    "15:320:1",
    "15:320:3",
)
TRANSLATIONS = {
    "15:283:0": "더 성공하기 쉬운 계책이라 할 수 있",
    "15:284:2": "까",
    "15:290:0": "성하에서",
    "15:291:0": "낭인·",
    "15:293:0": "낭인·",
    "15:297:0": "성하에서",
    "15:298:0": "성하에서",
    "15:299:0": "낭인·",
    "15:300:0": "성하에서",
    "15:313:2": "까?",
    "15:316:1": "까 하옵니다",
    "15:317:0": (
        "등의 낭인들이\n"
        "우리 가문의 승전보를 듣고 꼭 섬기고 싶다 하니\n"
        "한 번 만나 보시는 것도"
    ),
    "15:317:1": "까 하옵니다",
    "15:319:0": "사관을 바라는 낭인들이",
    "15:319:2": (
        "(이)라는 자 등, 벌써\n"
        "승전 소식을 전해 들은 모양입니다"
    ),
    "15:320:1": "인",
    "15:320:3": "인견",
}
TARGET_RECORD_IDS = (
    283,
    284,
    290,
    291,
    293,
    297,
    298,
    299,
    300,
    313,
    316,
    317,
    319,
    320,
)
EXPECTED_ARITY = {
    283: 3,
    284: 3,
    290: 2,
    291: 2,
    293: 2,
    297: 2,
    298: 2,
    299: 2,
    300: 2,
    313: 3,
    316: 2,
    317: 2,
    319: 3,
    320: 5,
}
PREFILL_COMPANION_COORDINATES = (
    "15:283:1",
    "15:283:2",
    "15:284:0",
    "15:284:1",
    "15:290:1",
    "15:291:1",
    "15:293:1",
    "15:297:1",
    "15:298:1",
    "15:299:1",
    "15:300:1",
    "15:313:0",
    "15:313:1",
    "15:316:0",
    "15:320:0",
    "15:320:2",
    "15:320:4",
)
PREFILL_COMPANION_DONOR = {
    "15:283:1": "15:272:1",
    "15:283:2": "15:272:2",
    "15:284:0": "15:281:0",
    "15:284:1": "15:281:1",
    "15:290:1": "15:287:1",
    "15:291:1": "15:288:1",
    "15:293:1": "15:290:1",
    "15:297:1": "15:294:1",
    "15:298:1": "15:295:1",
    "15:299:1": "15:296:1",
    "15:300:1": "15:297:1",
    "15:313:0": "15:310:0",
    "15:313:1": "15:310:1",
    "15:316:0": "15:313:0",
    "15:320:0": "15:315:0",
    "15:320:2": "15:315:2",
    "15:320:4": "15:315:4",
}
EXACT_BASE_DONOR = {
    283: (15, 272),
    284: (15, 281),
    290: (15, 287),
    291: (15, 288),
    293: (15, 290),
    297: (15, 294),
    298: (15, 295),
    299: (15, 296),
    300: (15, 297),
    313: (15, 310),
    316: (15, 313),
    320: (15, 315),
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ()
        for record_id in TARGET_RECORD_IDS
        if record_id not in {317, 319}
    },
    317: (
        "15:313:0",
        "15:313:1",
    ),
    319: (
        "15:314:0",
        "15:314:2",
    ),
}
EXPECTED_BASE_RAW_MATCHES = {
    283: (),
    284: (),
    290: ((15, 287),),
    291: ((15, 288),),
    293: ((15, 290),),
    297: ((15, 294),),
    298: ((15, 295),),
    299: ((15, 296),),
    300: ((15, 297),),
    313: (),
    316: (),
    317: (),
    319: (),
    320: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    283: ((15, 272), (15, 273), (15, 280)),
    284: ((15, 281),),
    290: ((15, 287),),
    291: ((15, 288),),
    293: ((15, 290),),
    297: ((15, 294),),
    298: ((15, 295),),
    299: ((15, 296),),
    300: ((15, 297),),
    313: ((15, 310),),
    316: ((15, 313),),
    317: (),
    319: (),
    320: ((15, 315), (15, 316)),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
EXPECTED_CONTROLS_BY_RECORD = {
    283: ((1066, 940, 1096), ()),
    284: ((568, 772), ()),
    290: ((), ("024833",)),
    291: ((), ("024833",)),
    293: ((), ("024833",)),
    297: ((), ("024833",)),
    298: ((), ("024833",)),
    299: ((), ("024833",)),
    300: ((), ("024833",)),
    313: ((1066,), ("024833",)),
    316: ((1048,), ("024833",)),
    317: ((1048,), ("024833",)),
    319: ((178, 724), ("024833",)),
    320: ((8, 1174, 796), ("024833", "023C")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1337,
    queue_start=0,
    queue_stop=67,
    slice_first="15:282:0",
    slice_last="15:321:0",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=("15:319:1",),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(
        8,
        178,
        568,
        724,
        772,
        940,
        1048,
        1066,
        1096,
        1174,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(270, 333)
    ),
    speaker_style=(
        (283, "formal_strategy_evaluation"),
        (284, "reflective_strategy_response"),
        (290, "formal_recruitment_proposal"),
        (291, "archaic_recruitment_proposal"),
        (293, "forceful_recruitment_proposal"),
        (297, "humble_recruitment_proposal"),
        (298, "female_humble_recruitment_proposal"),
        (299, "female_polite_recruitment_proposal"),
        (300, "formal_recruitment_proposal"),
        (313, "formal_recruitment_arrangement"),
        (316, "formal_victory_recruitment_report"),
        (317, "formal_plural_victory_recruitment_report"),
        (319, "formal_plural_service_report"),
        (320, "formal_audience_proposal"),
    ),
    terminology_policy=(
        ("strategy", "계책"),
        ("solid progress", "착실히 진행"),
        ("cost", "비용"),
        ("idea", "방안"),
        ("device", "궁리"),
        ("castle town", "성하"),
        ("ronin", "낭인"),
        ("employ", "등용"),
        ("clan", "우리 가문"),
        ("victory report", "승전보"),
        ("enter service", "사관"),
        ("audience", "인견"),
        ("dynamic subject particle", "(이)"),
        ("dynamic object particle", "을(를)"),
        ("project middle dot", "·"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record fragment array was reviewed as auxiliary evidence; "
        "twelve complete records reuse approved completed Base Korean "
        "assemblies, while the two plural service reports are manually "
        "adapted from the completed Base singular and service-report "
        "assemblies; Base runtime and VM state are never inherited; dynamic "
        "person and speaker calls retain their source ordering, subject and "
        "object particles remain explicit, and strategy, solid progress, "
        "cost, idea, device, castle town, ronin, employment, clan, victory "
        "report, service and audience terms retain the completed Base "
        "register; calls, inline name tokens, leading and trailing newlines, "
        "punctuation fragments, terminators, complete record arity, the "
        "source-identical hidden newline, all fifty slice prefills, pins, "
        "reverse overlays, two-run reproduction, tamper rejection, "
        "outside-scope identity, optional neighbor decisions and Steam "
        "read-only state are guarded"
    ),
    expected_changed_literal_count=13,
    pins={
        "expected_queue_universe_sha256": (
            "B7EEC6BF26F798B3C3B00BAC72A3E07BF5A68F3F242518911158017CD99BD584"
        ),
        "expected_queue_slice_sha256": (
            "8777E43ECC474867DE88BA00DB0E3F9703A9D90E797B2DEFCE3B7310236AD911"
        ),
        "expected_prefilled_coordinate_sha256": (
            "B60271303F99701B218253B3BE656058B0DBFA2FE37B48C7A41C4D7501160C48"
        ),
        "expected_prefill_slice_context_sha256": (
            "BC41548BDDACD4B555327355F3A97E59592B712D1BB1A537CA865014E0A99B2F"
        ),
        "expected_target_coordinate_sha256": (
            "D12455782AC0E1E48C1B19A4C59DABF1D70F4E747E697FE68D8BA063A97276CC"
        ),
        "expected_source_target_sha256": (
            "6A844AE4162228E3ADFC29DC61925CC01E49AA41E87242FBD3CA10EFF0FB9F3B"
        ),
        "expected_current_target_sha256": (
            "B98E6981460F5279DE974FD52A665275B2F29CA0032B0483BC7E17DBB386D240"
        ),
        "expected_context_corpus_sha256": (
            "5E7230FB3D0D4FF3D4E8B19E8604363C4653FB44D52095DA5027BE70B00FB41D"
        ),
        "expected_gap_contract_sha256": (
            "62A3EA1EC965FD6B268E2EC110E43AB8C1AA47E7457672F5FEA5AE41A3658D08"
        ),
        "expected_boundary_sha256": (
            "A6D578C564E7C12C1D7321CF5A6D96AD97FE504979CCE7F691A7FD08733F0114"
        ),
        "expected_runtime_control_sha256": (
            "76AC866029CF5C2C466BD64F6CE71942C5356C4D663FF6103BB762A176360EBC"
        ),
        "expected_base_search_sha256": (
            "EEFDB6235002B6D34458EBC101CF8B270D90D7F7590AE2064B57487ED9088B59"
        ),
        "expected_complete_assembly_sha256": (
            "5AD4B6022F67AAC6D0A6796C53689D62EDD8DF3FE5A8949BAA97C3B43BFF141B"
        ),
        "expected_call_graph_sha256": (
            "ACD5B75B6B4315216E9F406D5AAFBB28725BB21B8FB0DD1FE894B8C19D7379A3"
        ),
        "expected_speaker_style_sha256": (
            "3240B088773A94AC57F6ABD24D4DA09C0BA15A5AB0DBC44EB35AB8F4ED9CA4AF"
        ),
        "expected_terminology_policy_sha256": (
            "1B67957566180485F6EF260728F46576056BCCDD727668D71748215B411BFF42"
        ),
        "expected_translation_policy_sha256": (
            "DF366D29C810F42B5AC921A75144F9AD1433894E0645B19405A5582B8A0FB7F4"
        ),
        "expected_candidate_sha256": (
            "08310DD6C2913623F8D544204B89C4A5BF9992E495A9A229261DFBCC797BE062"
        ),
        "expected_combined_slice_candidate_sha256": (
            "BDC25D7233B3912328F992C7333A94A2929F64FDA2CB4B0B4FE494776740894C"
        ),
        "expected_combined_changed_literal_count": 58,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B111_S1337",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B111_S1337.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B111_S1338.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B111_S1339.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B111",
    "queue_row_count": 113,
    "queue_visible_count": 199,
    "queue_first": "15:282:0",
    "queue_last": "15:394:1",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
