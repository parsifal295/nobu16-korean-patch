#!/usr/bin/env python3
"""Build source-redacted PK B114 segment 1348 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:701:1",
    "15:717:0",
    "15:717:2",
    "15:717:3",
    "15:718:0",
    "15:718:2",
    "15:719:0",
    "15:720:0",
    "15:721:0",
    "15:722:0",
    "15:723:1",
    "15:723:2",
    "15:724:0",
)
TRANSLATIONS = {
    "15:701:1": "은(는)",
    "15:717:0": "·",
    "15:717:2": "을(를) 지배\n·",
    "15:717:3": "을(를) 등용",
    "15:718:0": "·",
    "15:718:2": "을(를) 지배",
    "15:719:0": "·",
    "15:720:0": "이(가)",
    "15:721:0": "을(를) 비롯한 총",
    "15:722:0": "을(를) 등용",
    "15:723:1": "→",
    "15:723:2": "으로(로)",
    "15:724:0": "이(가)",
}
TARGET_RECORD_IDS = (
    701,
    717,
    718,
    719,
    720,
    721,
    722,
    723,
    724,
)
EXPECTED_ARITY = {
    701: 3,
    717: 4,
    718: 3,
    719: 2,
    720: 2,
    721: 2,
    722: 1,
    723: 3,
    724: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "15:701:0",
    "15:701:2",
    "15:717:1",
    "15:718:1",
    "15:719:1",
    "15:720:1",
    "15:721:1",
    "15:723:0",
    "15:724:1",
)
PREFILL_COMPANION_DONOR = {
    "15:701:0": "15:694:0",
    "15:701:2": "15:694:2",
    "15:717:1": "15:710:1",
    "15:718:1": "15:711:1",
    "15:719:1": "15:712:1",
    "15:720:1": "15:713:1",
    "15:721:1": "15:714:1",
    "15:723:0": "15:716:0",
    "15:724:1": "15:717:1",
}
EXACT_BASE_DONOR = {
    701: (15, 694),
    717: (15, 710),
    718: (15, 711),
    719: (15, 712),
    720: (15, 713),
    721: (15, 714),
    722: (15, 715),
    723: (15, 716),
    724: (15, 717),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    701: ((15, 694),),
    717: ((15, 710),),
    718: ((15, 711),),
    719: ((15, 712),),
    720: ((15, 713),),
    721: ((15, 714), (15, 1038)),
    722: ((15, 715), (15, 1039)),
    723: ((15, 716), (15, 979), (15, 1453)),
    724: ((15, 717),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    723: (
        (15, 716),
        (15, 979),
        (15, 1337),
        (15, 1338),
        (15, 1453),
    ),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_CONTROLS_BY_RECORD = {
    701: ((7,), ("023C", "029632")),
    717: ((), ("023C", "029632", "024633")),
    718: ((), ("023C", "029632")),
    719: ((), ("028C32",)),
    720: ((), ("024633", "028C32")),
    721: ((), ("024633", "0232")),
    722: ((), ("024633",)),
    723: ((), ("026432", "0232", "0233")),
    724: ((), ("024633", "028C32")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1348,
    queue_start=134,
    queue_stop=200,
    slice_first="15:692:0",
    slice_last="15:730:0",
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
    source_call_roots=(7,),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(680, 742)
    ),
    speaker_style=(
        (701, "formal_integration_result"),
        (717, "system_integration_summary"),
        (718, "system_integration_summary"),
        (719, "system_integration_failure"),
        (720, "system_integration_success"),
        (721, "system_employment_summary"),
        (722, "system_employment_result"),
        (723, "system_troop_change"),
        (724, "system_integration_failure"),
    ),
    terminology_policy=(
        ("integration", "편입"),
        ("employ", "등용"),
        ("rule", "지배"),
        ("territory", "영지"),
        ("troops", "병력"),
        ("total", "총"),
        ("dynamic subject particle", "이(가)"),
        ("dynamic object particle", "을(를)"),
        ("dynamic directional particle", "으로(로)"),
        ("project middle dot", "·"),
        ("project arrow", "→"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record fragment array was reviewed as auxiliary evidence; all "
        "nine complete records reuse approved completed Base Korean "
        "assemblies selected by raw, literal and operand-masked source "
        "identity; Base runtime and VM state are never inherited; the troop "
        "change record selects completed Base record 716, whose directional "
        "particle safely follows a runtime number token, rather than the "
        "less general duplicate variants; integration, employment, rule, "
        "territory, troops, total, subject, object and directional particles, "
        "middle dots and arrows retain established project terminology; "
        "calls, inline person, faction, territory and number tokens, "
        "whitespace, newlines, terminators, complete record arity, all "
        "fifty-three slice prefills, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, optional "
        "neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=8,
    pins={
        "expected_queue_universe_sha256": (
            "9546FDEB560A7A0E6A75D7731A5614F817AEFBA97DE9F75154D76AD3643DD569"
        ),
        "expected_queue_slice_sha256": (
            "CF1EA43771E6823ED8C8A6A8AC2A05F67FEF483C6D15E865876E622EF39B3265"
        ),
        "expected_prefilled_coordinate_sha256": (
            "AABAF837C5417F3AE8938530CC5336B81C9F80F8E040A4D0C6A2E081DB4A5A7C"
        ),
        "expected_prefill_slice_context_sha256": (
            "6C32E960959AEC287B292A0A0978E310EDB153E6FF14BEA410826D1EBBFD1D0E"
        ),
        "expected_target_coordinate_sha256": (
            "8179E00635E5DF9857F21C462D4320BFEA7FF0B6F87A2AF2597BA4F3CC741FBC"
        ),
        "expected_source_target_sha256": (
            "00D5ED5C5059436979393CF22A6587E03F14753881B911374691218C5EB363B0"
        ),
        "expected_current_target_sha256": (
            "0CF1E3A1C7BA05ACE7507B99243D0200EA0D6F8B26FBE59CD59711BACD5303D4"
        ),
        "expected_context_corpus_sha256": (
            "138F0B7C994002E05B1FB12D96F35E0EC2BC78CCCBC5230AC0E98C3750AEE912"
        ),
        "expected_gap_contract_sha256": (
            "2B8FF6471F24289BFB022B7FA6BEE571E3CEBAB00F9CCE8F72F2F2E5BE07E498"
        ),
        "expected_boundary_sha256": (
            "E6159649028BC02A74982FC937A2492F41CB780A45E970EDA6F6E607C8DDBAD6"
        ),
        "expected_runtime_control_sha256": (
            "2C75A02EB4527022E100A673CC67DCFAC16E46004CDBE361E9BA581B38DAE748"
        ),
        "expected_base_search_sha256": (
            "9CD569B51904516D3E22F8F75C77296C289EB1487FD498B21DF12BB4C3D5C543"
        ),
        "expected_complete_assembly_sha256": (
            "AC4AF9427F76C682B31708811A248140A8D5FF6CA437757747187F623CF9D318"
        ),
        "expected_call_graph_sha256": (
            "C4765167CD1096FA6654A9D18EF4F56583E4BB661E40C8DAB0A0BA1840632DB4"
        ),
        "expected_speaker_style_sha256": (
            "97BB64C7EC66773D9C78B71CF1CF86B8644488948C6BB48D0BA6DD31C8FB38C3"
        ),
        "expected_terminology_policy_sha256": (
            "7CE416CA4DEA4843189782418173355C5E91D177D6EE45729DD9CBE954152183"
        ),
        "expected_translation_policy_sha256": (
            "CC7304A5CF055501AA60E6C837A7C92C78CC1EB02C70796D25AE0CE08FB83B34"
        ),
        "expected_candidate_sha256": (
            "5E76D12E7EEA581EB978EDD3C0CF15BEB3E5BBB093FA2420DAAD9276F31C9C7B"
        ),
        "expected_combined_slice_candidate_sha256": (
            "9C56CE3D582651FFD08FBFB8692E2771E9FA10E44EFAAC8459D71F2F86D52A26"
        ),
        "expected_combined_changed_literal_count": 50,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B114_S1348",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B114_S1348.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B114_S1346.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B114_S1347.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B114",
    "queue_row_count": 140,
    "queue_visible_count": 200,
    "queue_first": "15:591:0",
    "queue_last": "15:730:0",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
