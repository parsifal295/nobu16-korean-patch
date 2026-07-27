#!/usr/bin/env python3
"""Build source-redacted PK B111 segment 1339 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:361:0",
    "15:362:0",
    "15:379:0",
    "15:379:2",
    "15:380:0",
    "15:380:1",
    "15:381:0",
    "15:383:0",
    "15:384:2",
    "15:384:3",
    "15:385:0",
    "15:386:0",
    "15:388:1",
    "15:389:1",
    "15:389:2",
    "15:390:1",
    "15:390:2",
    "15:391:0",
    "15:392:0",
    "15:393:0",
)
TRANSLATIONS = {
    "15:361:0": "이름은",
    "15:362:0": ",",
    "15:379:0": "은(는)\n등용에 응할 뜻이 있어 보입니다",
    "15:379:2": "어떻겠습니까?",
    "15:380:0": "이(가)",
    "15:380:1": "을(를) 등용",
    "15:381:0": "이(가)",
    "15:383:0": "적의 군에",
    "15:384:2": "의 실행을",
    "15:384:3": "허가해 주시옵소서",
    "15:385:0": "의",
    "15:386:0": "의",
    "15:388:1": "의",
    "15:389:1": "의",
    "15:389:2": "에게……",
    "15:390:1": "의",
    "15:390:2": "(이)라든가",
    "15:391:0": "의",
    "15:392:0": "의",
    "15:393:0": "의",
}
TARGET_RECORD_IDS = (
    361,
    362,
    379,
    380,
    381,
    383,
    384,
    385,
    386,
    388,
    389,
    390,
    391,
    392,
    393,
)
EXPECTED_ARITY = {
    361: 2,
    362: 3,
    379: 3,
    380: 2,
    381: 2,
    383: 3,
    384: 4,
    385: 2,
    386: 2,
    388: 3,
    389: 3,
    390: 3,
    391: 2,
    392: 2,
    393: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "15:361:1",
    "15:362:1",
    "15:362:2",
    "15:379:1",
    "15:381:1",
    "15:383:1",
    "15:383:2",
    "15:384:0",
    "15:384:1",
    "15:385:1",
    "15:386:1",
    "15:388:0",
    "15:388:2",
    "15:389:0",
    "15:390:0",
    "15:391:1",
    "15:392:1",
    "15:393:1",
    "15:393:2",
)
PREFILL_COMPANION_DONOR = {
    "15:361:1": "15:354:1",
    "15:362:1": "15:355:1",
    "15:362:2": "15:355:2",
    "15:379:1": "15:372:1",
    "15:381:1": "15:374:1",
    "15:383:1": "15:376:1",
    "15:383:2": "15:376:2",
    "15:384:0": "15:377:0",
    "15:384:1": "15:377:1",
    "15:385:1": "15:378:1",
    "15:386:1": "15:379:1",
    "15:388:0": "15:381:0",
    "15:388:2": "15:381:2",
    "15:389:0": "15:382:0",
    "15:390:0": "15:383:0",
    "15:391:1": "15:384:1",
    "15:392:1": "15:385:1",
    "15:393:1": "15:386:1",
    "15:393:2": "15:386:2",
}
EXACT_BASE_DONOR = {
    361: (15, 354),
    362: (15, 355),
    380: (15, 373),
    381: (15, 374),
    383: (15, 376),
    384: (15, 377),
    385: (15, 378),
    386: (15, 379),
    388: (15, 381),
    389: (15, 382),
    390: (15, 383),
    391: (15, 384),
    392: (15, 385),
    393: (15, 386),
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ()
        for record_id in TARGET_RECORD_IDS
        if record_id != 379
    },
    379: (
        "15:372:0",
        "15:372:1",
        "15:372:2",
    ),
}
EXPECTED_BASE_RAW_MATCHES = {
    361: ((15, 354), (15, 1407), (15, 1425)),
    362: ((15, 355), (15, 1408), (15, 1426)),
    379: (),
    380: ((15, 373), (15, 1411), (15, 1429), (15, 1527)),
    381: ((15, 374),),
    383: (),
    384: (),
    385: ((15, 378),),
    386: ((15, 379),),
    388: ((15, 381),),
    389: ((15, 382),),
    390: ((15, 383),),
    391: ((15, 384),),
    392: ((15, 385),),
    393: ((15, 386),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    383: ((15, 376),),
    384: ((15, 377),),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
EXPECTED_CONTROLS_BY_RECORD = {
    361: ((), ("024633",)),
    362: ((1, 8), ("024633",)),
    379: ((37, 568, 700, 616), ()),
    380: ((), ("024633", "024733")),
    381: ((), ("024633", "024733")),
    383: ((610,), ("026432",)),
    384: ((1174,), ("026432",)),
    385: ((29,), ("02483E",)),
    386: ((21,), ("02483E",)),
    388: ((21,), ("02483E",)),
    389: ((21,), ("02483E",)),
    390: ((21,), ("02483E",)),
    391: ((21,), ("02483E",)),
    392: ((21,), ("02483E",)),
    393: ((21, 1), ("02483E",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1339,
    queue_start=134,
    queue_stop=199,
    slice_first="15:361:0",
    slice_last="15:394:1",
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
    source_call_roots=(1, 8, 21, 29, 37, 568, 610, 616, 700, 1174),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(350, 405)
    ),
    speaker_style=(
        (361, "male_archaic_service_introduction"),
        (362, "female_polite_service_introduction"),
        (379, "formal_recruitment_proposal"),
        (380, "neutral_recruitment_result"),
        (381, "neutral_recruitment_failure"),
        (383, "formal_stratagem_proposal"),
        (384, "male_humble_stratagem_proposal"),
        (385, "male_informal_defection_intelligence"),
        (386, "male_humble_defection_intelligence"),
        (388, "male_humble_defection_rumor"),
        (389, "male_archaic_defection_proposal"),
        (390, "male_archaic_target_example"),
        (391, "male_humble_defection_proposal"),
        (392, "male_archaic_defection_proposal"),
        (393, "male_archaic_defection_proposal"),
    ),
    terminology_policy=(
        ("name", "이름"),
        ("employ", "등용"),
        ("enemy army", "적의 군"),
        ("stratagem", "조략"),
        ("defection", "귀순"),
        ("dynamic subject particle", "이(가)"),
        ("dynamic object particle", "을(를)"),
        ("dynamic possessive particle", "의"),
        ("dynamic destination particle", "에게"),
        ("project ellipsis", "……"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record fragment array was reviewed as auxiliary evidence; "
        "fourteen complete records reuse approved completed Base Korean "
        "assemblies, while the remaining recruitment proposal is freshly "
        "reviewed against the completed Base proposal with the same meaning; "
        "Base runtime and VM state are never inherited; dynamic person and "
        "faction calls retain their source ordering, subject, object, "
        "possessive and destination particles remain explicit, and name, "
        "employment, enemy army, stratagem, defection and ellipsis wording "
        "retains established project terminology and speaker register; calls, "
        "inline name and faction tokens, leading and trailing whitespace, "
        "punctuation fragments, terminators, complete record arity, all "
        "forty-five slice prefills, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, optional "
        "neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=12,
    pins={
        "expected_queue_universe_sha256": (
            "B7EEC6BF26F798B3C3B00BAC72A3E07BF5A68F3F242518911158017CD99BD584"
        ),
        "expected_queue_slice_sha256": (
            "A5BF76CC028D2F0A4659DC73F042B6759AC2646D277990EC700B59EB6C83BA7C"
        ),
        "expected_prefilled_coordinate_sha256": (
            "4819D111CE08470696F886535BF09C50B76209FAB907230BC79C0E63BC9EC4CE"
        ),
        "expected_prefill_slice_context_sha256": (
            "40099F427FC175AD011072AC664F6644568434C9B676368BD379C1EEF609C136"
        ),
        "expected_target_coordinate_sha256": (
            "7B7333672AA09D2E2766993D6EBF5DD6FFBD38D058A91A672845B616E55886A5"
        ),
        "expected_source_target_sha256": (
            "380844B2081769B6A7C7FD9FF3EC4124012E44E7834F3DC914117089A68271B4"
        ),
        "expected_current_target_sha256": (
            "CCDD0D3FC615BCE47F0D654F01F45AFAEE333D483EB27AD4F4E170D983744355"
        ),
        "expected_context_corpus_sha256": (
            "5E7230FB3D0D4FF3D4E8B19E8604363C4653FB44D52095DA5027BE70B00FB41D"
        ),
        "expected_gap_contract_sha256": (
            "A96F511B475805B16EC938C14DE877AC25E8192E2DE84FFEDD0CC572E8DB1171"
        ),
        "expected_boundary_sha256": (
            "02E4689F69620076EE2F1A7A5C552BEFF78DB547912F22F470B9F16852E537C9"
        ),
        "expected_runtime_control_sha256": (
            "CB6D17F8B8ED24008F8D443C1F8F3F120C6C65D06FCD30AA4E204A639BDED319"
        ),
        "expected_base_search_sha256": (
            "8ADD89BCA2C45B37EEC5C2DB266F35000260CB29D6696F0180E8152386E6DB2E"
        ),
        "expected_complete_assembly_sha256": (
            "FEB8E5ADB4E010E98FE6EFBFF666DFD10F4236948EEC1AE62244827FDB11F209"
        ),
        "expected_call_graph_sha256": (
            "76B9411E67D1A9FF815D0B316A3E98F6540BB66CC50737E2DCABB092F64B8CB7"
        ),
        "expected_speaker_style_sha256": (
            "36DCDE541623E750315B5AEA944D39FBA686FFE73775C165042E174C450853EA"
        ),
        "expected_terminology_policy_sha256": (
            "97796969F5943FCB6C055FC114E2BD94988E732CDEC3F8A578E84458C9B8BBF7"
        ),
        "expected_translation_policy_sha256": (
            "0E0A66084730BD2660EEB5B6A660B943B6855B25908B73ED3BC7E0A7FF42B674"
        ),
        "expected_candidate_sha256": (
            "518F3BD981BAF5754B20FD6717A5142D7D5004BF20B11076338F0E2AD2A2E54C"
        ),
        "expected_combined_slice_candidate_sha256": (
            "371A85E95AB411FC42E104309C864DF8FFEA570DD9B6DB0D33832E8832F8772B"
        ),
        "expected_combined_changed_literal_count": 53,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B111_S1339",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B111_S1339.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B111_S1337.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B111_S1338.private.v1.jsonl",
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
