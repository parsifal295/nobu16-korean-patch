#!/usr/bin/env python3
"""Build source-redacted PK B118 segment 1358 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = tuple(range(1106, 1128))
TARGET_COORDINATES = tuple(
    f"15:{record_id}:1"
    for record_id in TARGET_RECORD_IDS
)
TRANSLATIONS = {
    coordinate: "와(과)"
    for coordinate in TARGET_COORDINATES
}
EXPECTED_ARITY = {
    record_id: 3
    for record_id in TARGET_RECORD_IDS
}
PREFILL_COMPANION_COORDINATES = tuple(
    f"15:{record_id}:{literal_id}"
    for record_id in TARGET_RECORD_IDS
    for literal_id in (0, 2)
)
PREFILL_COMPANION_DONOR = {
    f"15:{record_id}:{literal_id}": (
        f"15:{1097 if record_id <= 1116 else 1109}:{literal_id}"
    )
    for record_id in TARGET_RECORD_IDS
    for literal_id in (0, 2)
}
HIDDEN_CURRENT_COMPANION_COORDINATES = ()
EXACT_BASE_DONOR = {
    record_id: (15, 1097 if record_id <= 1116 else 1109)
    for record_id in TARGET_RECORD_IDS
}
SEMANTIC_BASE_CONTEXT = {
    record_id: tuple(
        f"{donor[0]}:{donor[1]}:{literal_id}"
        for literal_id in range(EXPECTED_ARITY[record_id])
    )
    for record_id, donor in EXACT_BASE_DONOR.items()
}
FIRST_BASE_MATCHES = tuple(
    (15, record_id)
    for record_id in range(1097, 1109)
)
SECOND_BASE_MATCHES = tuple(
    (15, record_id)
    for record_id in range(1109, 1121)
)
EXPECTED_BASE_MATCHES = {
    record_id: (
        FIRST_BASE_MATCHES
        if record_id <= 1116
        else SECOND_BASE_MATCHES
    )
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ("025032", "025132"))
    for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1358,
    queue_start=0,
    queue_stop=67,
    slice_first="15:1106:0",
    slice_last="15:1128:0",
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
    expected_base_raw_matches=EXPECTED_BASE_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(),
    boundary_record_keys=tuple(
        (15, record_id)
        for record_id in range(1090, 1136)
    ),
    speaker_style=tuple(
        (
            record_id,
            (
                "smug_formal_intrigue_success_report"
                if record_id <= 1116
                else "apologetic_formal_intrigue_failure_report"
            ),
        )
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("estrangement operation", "이간 공작"),
        ("our house", "우리 가문"),
        ("other factions", "다른 세력"),
        ("dynamic faction conjunction", "와(과)"),
        ("formal completed action", "하옵니다"),
        ("formal future question", "쓰오리까"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between the first sixty-seven visible B118 queue "
        "coordinates and the approved Base prefill; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; all twenty-two "
        "records reuse approved byte-identical Base Korean assemblies, with "
        "the first eleven selecting completed success-report record 1097 "
        "and the next eleven selecting completed failure-report record "
        "1109 from their duplicate families; Base runtime and VM state are "
        "never inherited; the dynamic faction conjunction, estrangement "
        "operation, house and formal adviser registers retain established "
        "project wording; both inline faction tokens, protected outer "
        "whitespace, line counts, gaps, literal arity, terminators, all "
        "forty-four same-record prefills, all forty-five slice prefills, "
        "complete assemblies, pins, reverse overlays, two-run reproduction, "
        "tamper rejection, outside-scope identity, optional neighbor "
        "decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=22,
    pins={
        "expected_queue_universe_sha256": (
            "1207015E2B3B81B1D053FA00F35628E780A874C0D44CFB013764244FF33CAAC3"
        ),
        "expected_queue_slice_sha256": (
            "393EF8D74A68E47D4D7DDE456640CF88A9D867B48D8A77DF11EA1FC8B5C81F00"
        ),
        "expected_prefilled_coordinate_sha256": (
            "EBD5036EC97133631310B0D727AF1214A7A3F8F89901D35BBCF0795164BD96BA"
        ),
        "expected_prefill_slice_context_sha256": (
            "AED9AFFA4B02A93A8C7E754302B5F064000633985E40B442840987B2AC1A6779"
        ),
        "expected_target_coordinate_sha256": (
            "AAD91F7AFE8D0C0014BEF24DD25936F3838B97D29C05CB516A5104F0004D4595"
        ),
        "expected_source_target_sha256": (
            "30790AF86ACC408B14A5C8203F0CF8D4CA3FD7BE3709830BAFA6562C05537540"
        ),
        "expected_current_target_sha256": (
            "832F9E072E21BC7E4F52627204FA6D7E967D21F9F2F605EFD8EAF992BD3537A6"
        ),
        "expected_context_corpus_sha256": (
            "01132F26EE8C33E41493AAE3EC7099BA97DC2F1DFB38E6B5FD215321136F9F4A"
        ),
        "expected_gap_contract_sha256": (
            "AB938EA1391A145615AF3446167F749F9053A223D91388D61F6B4C6E3F64BD15"
        ),
        "expected_boundary_sha256": (
            "1E55848A4456875B723CA867BBACC2288348640ACE3D1B05AD20EA878F567F8C"
        ),
        "expected_runtime_control_sha256": (
            "6FC681ECE73942463121A2954DE07DDE339EE6AFFBD8A2AA77BABFB935755588"
        ),
        "expected_base_search_sha256": (
            "69C35037E6A827AD774217DEAB221E6AC72A3A59E7E34EBBE01BBF2BE3EE6EB7"
        ),
        "expected_complete_assembly_sha256": (
            "722A7365069040DEA393DAADD6805DF5FBE28CEA856DA54934C46774D69DCEB5"
        ),
        "expected_call_graph_sha256": (
            "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
        ),
        "expected_speaker_style_sha256": (
            "8A5EFAC73FDC66C605A04433D5271C9315E9ECD421ED5D4DDABE4156360A3291"
        ),
        "expected_terminology_policy_sha256": (
            "4A01ACE0D106B3809DEF7AF671F4A4BE64C39A5BA4194E5B1F4E8766E2F26B06"
        ),
        "expected_translation_policy_sha256": (
            "9AC67049FF8F31DF10D32A613AC6CF488ECD91F69A5055733310DA73388848C5"
        ),
        "expected_candidate_sha256": (
            "7CF80AE1AD2FE17D2F17B79CAB4AE0B3071A31BB454EAEA9445ECE36376B0FA9"
        ),
        "expected_combined_slice_candidate_sha256": (
            "FF7A6250ABB22749695CEEBBE3DE6C41196CF435B2BCC426321B985BAD751211"
        ),
        "expected_combined_changed_literal_count": 55,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B118_S1358",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B118_S1358.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B118_S1359.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B118_S1360.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B118",
    "queue_row_count": 111,
    "queue_visible_count": 200,
    "queue_first": "15:1106:0",
    "queue_last": "15:1216:1",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
