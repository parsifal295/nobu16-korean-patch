#!/usr/bin/env python3
"""Build source-redacted PK B116 segment 1352 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:884:1",
    "15:884:2",
    "15:884:3",
    "15:885:1",
    "15:885:2",
    "15:885:3",
    "15:887:0",
    "15:888:0",
    "15:889:1",
    "15:890:0",
    "15:891:1",
    "15:891:2",
    "15:892:0",
    "15:893:0",
    "15:894:0",
    "15:895:0",
    "15:897:0",
)
TRANSLATIONS = {
    "15:884:1": "만큼 확대(",
    "15:884:2": "→",
    "15:884:3": ")",
    "15:885:1": "만큼 상승(",
    "15:885:2": "→",
    "15:885:3": ")",
    "15:887:0": "의",
    "15:888:0": "의",
    "15:889:1": "의\n",
    "15:890:0": "의",
    "15:891:1": "의",
    "15:891:2": "일까",
    "15:892:0": "의",
    "15:893:0": "의",
    "15:894:0": "의",
    "15:895:0": "의",
    "15:897:0": "의",
}
TARGET_RECORD_IDS = (
    884,
    885,
    887,
    888,
    889,
    890,
    891,
    892,
    893,
    894,
    895,
    897,
)
EXPECTED_ARITY = {
    884: 4,
    885: 4,
    887: 3,
    888: 2,
    889: 3,
    890: 2,
    891: 3,
    892: 2,
    893: 2,
    894: 2,
    895: 2,
    897: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "15:884:0",
    "15:885:0",
    "15:887:1",
    "15:887:2",
    "15:888:1",
    "15:889:0",
    "15:889:2",
    "15:890:1",
    "15:891:0",
    "15:892:1",
    "15:893:1",
    "15:894:1",
    "15:895:1",
    "15:897:1",
)
PREFILL_COMPANION_DONOR = {
    "15:884:0": "15:877:0",
    "15:885:0": "15:877:0",
    "15:887:1": "15:880:1",
    "15:887:2": "15:880:2",
    "15:888:1": "15:881:1",
    "15:889:0": "15:882:0",
    "15:889:2": "15:882:2",
    "15:890:1": "15:883:1",
    "15:891:0": "15:884:0",
    "15:892:1": "15:885:1",
    "15:893:1": "15:886:1",
    "15:894:1": "15:887:1",
    "15:895:1": "15:888:1",
    "15:897:1": "15:890:1",
}
EXACT_BASE_DONOR = {
    884: (15, 877),
    885: (15, 878),
    887: (15, 880),
    888: (15, 881),
    889: (15, 882),
    890: (15, 883),
    891: (15, 884),
    892: (15, 885),
    893: (15, 886),
    894: (15, 887),
    895: (15, 888),
    897: (15, 890),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MATCHES = {
    record_id: (EXACT_BASE_DONOR[record_id],)
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_CONTROLS_BY_RECORD = {
    884: ((), ("029632", "0232", "0233", "0234")),
    885: ((), ("029632", "0232", "0233", "0234")),
    887: ((1,), ("025032", "026432")),
    888: ((), ("025032", "026432")),
    889: ((1,), ("025032", "026432")),
    890: ((), ("025032", "026432")),
    891: ((), ("025032", "026432")),
    892: ((), ("025032", "026432")),
    893: ((), ("025032", "026432")),
    894: ((), ("025032", "026432")),
    895: ((), ("025032", "026432")),
    897: ((), ("025032", "026432")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1352,
    queue_start=0,
    queue_stop=67,
    slice_first="15:867:0",
    slice_last="15:905:1",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(1,),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(870, 916)
    ),
    speaker_style=(
        (884, "system_control_expansion_result"),
        (885, "system_control_rate_increase"),
        (887, "enthusiastic_vanguard_proposal"),
        (888, "formal_siege_caution"),
        (889, "formal_tactical_assessment"),
        (890, "informal_stratagem_suggestion"),
        (891, "informal_weakening_target_suggestion"),
        (892, "formal_fortification_caution"),
        (893, "forceful_siege_caution"),
        (894, "female_polite_stratagem_suggestion"),
        (895, "cautious_weakening_suggestion"),
        (897, "formal_fortification_weakening_proposal"),
    ),
    terminology_policy=(
        ("control rate", "지배율"),
        ("increase amount", "만큼"),
        ("expand", "확대"),
        ("rise", "상승"),
        ("capture", "공략"),
        ("vanguard", "선봉"),
        ("weakening stratagem", "약화 공작"),
        ("castle", "성"),
        ("fall of castle", "함락"),
        ("dynamic possessive particle", "의"),
        ("project ellipsis", "……"),
        ("numeric transition", "→"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record fragment array was reviewed as auxiliary evidence; all "
        "twelve complete records are byte-identical to approved completed "
        "Base donors and reuse their Korean assemblies while retaining each "
        "speaker's established register; Base runtime and VM state are never "
        "inherited; the two system result records restore the omitted amount "
        "marker before control-rate expansion and increase values, while "
        "capture, vanguard, weakening-stratagem, castle and fall terminology "
        "and possessive particles follow the historical project glossary; "
        "the queue and prefill difference independently derives and pins all "
        "seventeen residual coordinates; numeric value tokens, castle, "
        "speaker and force calls, inline control-rate and transition tokens, "
        "parentheses, arrows, protected whitespace, line breaks, terminators, "
        "complete record arity, all fifty slice prefills, pins, reverse "
        "overlays, two-run reproduction, tamper rejection, outside-scope "
        "identity, optional neighbor decisions and Steam read-only state are "
        "guarded"
    ),
    expected_changed_literal_count=2,
    pins={
        "expected_queue_universe_sha256": (
            "C6ADAF56AFF67E1F3846197DC22BF265DE81ABFFABFA5D87F3E976F29F3D76D9"
        ),
        "expected_queue_slice_sha256": (
            "3273FE9A373DFBDE7A087AA3217CF5481A1D5076D4208A6A98183EC1646277F3"
        ),
        "expected_prefilled_coordinate_sha256": (
            "9F07EDC663233AA1537BEA3F3E71A81BAF9C6F35969D0F186B18B07D5CD32E38"
        ),
        "expected_prefill_slice_context_sha256": (
            "064C47614848F1549A2B010F04919C2A541E4DF41DF8CD611212BE96C2AE5AB6"
        ),
        "expected_target_coordinate_sha256": (
            "42DD1601CECEF6F3013AE543EF53978427ED713BEB14B180C69212E455E9510F"
        ),
        "expected_source_target_sha256": (
            "42950B37B68E6736436E6D03A71C81459FB9D46428A0C359E3588582894561AD"
        ),
        "expected_current_target_sha256": (
            "B7C753EA8D54E8E54F4B085043D2C45BAFB99E53B0B43344EE08D91B5C04D400"
        ),
        "expected_context_corpus_sha256": (
            "8930F43DFB214781CF143FAC6A98B068B6446B0436C164F75DCBCF1E51E7F8D9"
        ),
        "expected_gap_contract_sha256": (
            "E8A1357BEA2317921FD8A8DCC3993B72B73B3247AD34A261615453A682EB36E9"
        ),
        "expected_boundary_sha256": (
            "572B5C0857C70B786CEF85C43A42AE9417B3618704DC529D4BC168F1CFE1BB96"
        ),
        "expected_runtime_control_sha256": (
            "B44F84AF37885A8D76C4BD617BC5B9EE29814F677D2DFFEDFAEAF238D116DFD0"
        ),
        "expected_base_search_sha256": (
            "C319F7A705344F0B7C39D4CCCE9FC2F81C5F35DF9F83FAF8FA057576D275B0A4"
        ),
        "expected_complete_assembly_sha256": (
            "FB64ED7490A85B2C58E281649202F1E2E5D1B750F63B563374DAFA49A30F90D9"
        ),
        "expected_call_graph_sha256": (
            "9F6F46D774474371A103483E9C9BFA5C47CE1819CB17620E9DBFE32BDF9CD7BD"
        ),
        "expected_speaker_style_sha256": (
            "FEA8B8CA06AA2E5671818D47FC1667BA6B02D4101D9206CED4D43B8EF4C318C1"
        ),
        "expected_terminology_policy_sha256": (
            "073A0AE9450085FD8AC738FF7BC522884722F82CC17E1075FED709278012100B"
        ),
        "expected_translation_policy_sha256": (
            "34F193051215B9A55A01EFC39198FBBCF03F83A708B5135637742C58E90411AC"
        ),
        "expected_candidate_sha256": (
            "B9E019DA6C20A861BE949B38607F9ED3942D3B909BDEA36877BD06A11F01CD3F"
        ),
        "expected_combined_slice_candidate_sha256": (
            "FCDD55B1F5069D9F65652A64C9D49D4E20A8E57F86F4935D3C6777EC148344B2"
        ),
        "expected_combined_changed_literal_count": 49,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B116_S1352",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B116_S1352.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B116_S1353.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B116_S1354.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B116",
    "queue_row_count": 118,
    "queue_visible_count": 199,
    "queue_first": "15:867:0",
    "queue_last": "15:984:1",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
