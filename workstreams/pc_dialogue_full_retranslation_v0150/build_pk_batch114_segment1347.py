#!/usr/bin/env python3
"""Build source-redacted PK B114 segment 1347 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:655:0",
    "15:667:0",
    "15:667:1",
    "15:668:0",
    "15:679:0",
    "15:679:1",
    "15:680:0",
    "15:690:1",
    "15:691:1",
)
TRANSLATIONS = {
    "15:655:0": "아무래도",
    "15:667:0": "우리와 ",
    "15:667:1": (
        " 은(는)\n"
        "이제 한배를 탄 사이\n"
        "속히 휘하에 들여야 할 듯하옵니다"
    ),
    "15:668:0": "우리 가문과",
    "15:679:0": "우리와 ",
    "15:679:1": (
        " 은(는)\n"
        "이제 한배를 탄 사이\n"
        "속히 휘하에 들여야 할 듯하옵니다"
    ),
    "15:680:0": "우리 가문과",
    "15:690:1": "은(는)\n",
    "15:691:1": "은(는)",
}
TARGET_RECORD_IDS = (
    655,
    667,
    668,
    679,
    680,
    690,
    691,
)
EXPECTED_ARITY = {
    655: 2,
    667: 2,
    668: 2,
    679: 2,
    680: 2,
    690: 4,
    691: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "15:655:1",
    "15:668:1",
    "15:680:1",
    "15:690:0",
    "15:690:2",
    "15:690:3",
    "15:691:0",
    "15:691:2",
)
PREFILL_COMPANION_DONOR = {
    "15:655:1": "15:648:1",
    "15:668:1": "15:661:1",
    "15:680:1": "15:661:1",
    "15:690:0": "15:683:0",
    "15:690:2": "15:683:2",
    "15:690:3": "15:683:3",
    "15:691:0": "15:684:0",
    "15:691:2": "15:684:2",
}
EXACT_BASE_DONOR = {
    655: (15, 648),
    668: (15, 661),
    680: (15, 661),
    690: (15, 683),
    691: (15, 684),
}
SEMANTIC_BASE_CONTEXT = {
    655: (),
    667: ("15:660:0", "15:660:1"),
    668: (),
    679: ("15:660:0", "15:660:1"),
    680: (),
    690: (),
    691: (),
}
EXPECTED_BASE_RAW_MATCHES = {
    655: ((15, 648),),
    667: ((15, 660), (15, 672)),
    668: ((15, 661), (15, 673)),
    679: ((15, 660), (15, 672)),
    680: ((15, 661), (15, 673)),
    690: (),
    691: ((15, 684),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    690: ((15, 683),),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
EXPECTED_CONTROLS_BY_RECORD = {
    655: ((), ("028C32",)),
    667: ((), ("028C32",)),
    668: ((), ("028C32",)),
    679: ((), ("028C32",)),
    680: ((), ("028C32",)),
    690: ((442, 322), ("028C32", "025032")),
    691: ((7,), ("023C", "029632")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1347,
    queue_start=67,
    queue_stop=134,
    slice_first="15:644:1",
    slice_last="15:691:2",
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
    source_call_roots=(7, 322, 442),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(635, 702)
    ),
    speaker_style=(
        (655, "male_archaic_incorporation_advice"),
        (667, "male_humble_incorporation_advice"),
        (668, "formal_retainer_incorporation_proposal"),
        (679, "male_humble_incorporation_advice"),
        (680, "formal_retainer_incorporation_proposal"),
        (690, "kunishu_fealty_pledge"),
        (691, "male_boastful_incorporation_report"),
    ),
    terminology_policy=(
        ("kunishu", "국인중"),
        ("clan", "우리 가문"),
        ("under command", "휘하"),
        ("retainer", "가신"),
        ("incorporate", "편입"),
        ("fealty", "충성"),
        ("share one fate", "한배를 탄 사이"),
        ("dynamic subject particle", "은(는)"),
        ("dynamic destination particle", "에게"),
        ("PK name boundary", "앞뒤 공백 보존"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record fragment array was reviewed as auxiliary evidence; five "
        "complete records reuse approved completed Base Korean assemblies, "
        "while the two duplicated shared-fate records use the same completed "
        "Base wording semantically but retain their PK-specific protected "
        "spaces around the runtime kunishu-name token; Base runtime and VM "
        "state are never inherited; dynamic kunishu, clan and speaker calls "
        "retain their source ordering, subject and destination particles "
        "remain explicit, and kunishu, clan, command, retainer, "
        "incorporation, fealty and shared-fate terminology follows the "
        "historical project glossary and each completed speaker register; "
        "the queue and prefill difference independently derives and pins all "
        "nine residual coordinates; calls, inline tokens, protected outer "
        "whitespace, line breaks, terminators, complete record arity, all "
        "fifty-eight slice prefills, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, optional "
        "neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=5,
    pins={
        "expected_queue_universe_sha256": (
            "9546FDEB560A7A0E6A75D7731A5614F817AEFBA97DE9F75154D76AD3643DD569"
        ),
        "expected_queue_slice_sha256": (
            "5DF4D279CB720690279645B75BBC0653B6D8F9C2BD12D087F326CF65F245F5B9"
        ),
        "expected_prefilled_coordinate_sha256": (
            "94A6324AD93CBF5DC982C20CA088E9507EAD6E227B1C5477A6ABC119A8AD29FC"
        ),
        "expected_prefill_slice_context_sha256": (
            "8518E2AD32EE97C08C95F47AD49DB74616D1FFDDBE7A769B6909046CC4CF8103"
        ),
        "expected_target_coordinate_sha256": (
            "F0541F363D06E60C464D511ACB4AB7DD9B76A28A387434650A3A78A137B6C956"
        ),
        "expected_source_target_sha256": (
            "17E4A88B667E240D8894A0F08CD47E23FCE71460E277A03928DEA62BB38E5BD5"
        ),
        "expected_current_target_sha256": (
            "8804947C4E5AC4DB95B9D8C612D5B54F7187A6475C508C43C50AF0DE76F13771"
        ),
        "expected_context_corpus_sha256": (
            "138F0B7C994002E05B1FB12D96F35E0EC2BC78CCCBC5230AC0E98C3750AEE912"
        ),
        "expected_gap_contract_sha256": (
            "5CF51B69492E482B06D2D8A170C6DCA781F66B9C318147EF271F2A8BE07A810E"
        ),
        "expected_boundary_sha256": (
            "AA81A9B93016AD4F50D52BA6932784BC0F0175EFEFE4D4B0D74133223143AFFA"
        ),
        "expected_runtime_control_sha256": (
            "35A371557305F9B7184516F19B7174CDB2593D43942F6FB7339A339395A1FC00"
        ),
        "expected_base_search_sha256": (
            "C40ECF1D4F1FD607EC27C4E71111375D869EC248C7A49722D785FAF3FDC4A326"
        ),
        "expected_complete_assembly_sha256": (
            "0AF679474E5F10516368D069CB41F00AD0B2530AFA373FDA84D33715F0DEC6FB"
        ),
        "expected_call_graph_sha256": (
            "E3EE20A456016FBF6FAD8E8A05F9FD03377961AD42903AB06F0159F1AAC41AB0"
        ),
        "expected_speaker_style_sha256": (
            "765F7EC60F5657B80E99A6AC7F1C4B01D72A637F603E5C930B19B13A401B1B0B"
        ),
        "expected_terminology_policy_sha256": (
            "9843E0CEE8450B91731A4ECDF2E46ACFB47A5E975E22F273C33C55FADEC64503"
        ),
        "expected_translation_policy_sha256": (
            "60810BB4DBE5EAC53387D6AD9ACE3A0E74A07F600AA037162C3888163F2154A1"
        ),
        "expected_candidate_sha256": (
            "6A83A906D49ED8D66D8D68B90985E7B21B31183A352E2FF09F6CD8344FBEA54A"
        ),
        "expected_combined_slice_candidate_sha256": (
            "4E93857A1E6F6996C1B447F7F9D04D1517FFFFE0C161FED80138F14EC4ECF7F0"
        ),
        "expected_combined_changed_literal_count": 60,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B114_S1347",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B114_S1347.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B114_S1346.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B114_S1348.private.v1.jsonl",
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
