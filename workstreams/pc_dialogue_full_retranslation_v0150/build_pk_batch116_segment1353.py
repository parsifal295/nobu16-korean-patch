#!/usr/bin/env python3
"""Build source-redacted PK B116 segment 1353 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "15:905:2",
    "15:910:1",
    "15:911:0",
    "15:912:0",
    "15:913:1",
    "15:914:2",
    "15:915:1",
    "15:916:1",
    "15:917:1",
    "15:918:1",
    "15:919:1",
    "15:920:1",
    "15:921:0",
    "15:923:2",
    "15:925:2",
)
TRANSLATIONS = {
    "15:905:2": "!",
    "15:910:1": "의",
    "15:911:0": "의",
    "15:912:0": "의",
    "15:913:1": "의",
    "15:914:2": "이(가) 벌인",
    "15:915:1": "의",
    "15:916:1": "의",
    "15:917:1": "의",
    "15:918:1": "의",
    "15:919:1": "의",
    "15:920:1": "의",
    "15:921:0": "의",
    "15:923:2": "허가를……",
    "15:925:2": "에게",
}
TARGET_RECORD_IDS = (
    905,
    910,
    911,
    912,
    913,
    914,
    915,
    916,
    917,
    918,
    919,
    920,
    921,
    923,
    925,
)
EXPECTED_ARITY = {
    905: 3,
    910: 3,
    911: 2,
    912: 2,
    913: 3,
    914: 4,
    915: 3,
    916: 3,
    917: 3,
    918: 3,
    919: 3,
    920: 3,
    921: 2,
    923: 3,
    925: 4,
}
PREFILL_COMPANION_COORDINATES = (
    "15:905:0",
    "15:905:1",
    "15:910:0",
    "15:910:2",
    "15:911:1",
    "15:912:1",
    "15:913:0",
    "15:913:2",
    "15:914:0",
    "15:914:3",
    "15:915:0",
    "15:915:2",
    "15:916:0",
    "15:916:2",
    "15:917:0",
    "15:917:2",
    "15:918:0",
    "15:918:2",
    "15:919:0",
    "15:919:2",
    "15:920:0",
    "15:920:2",
    "15:921:1",
    "15:923:0",
    "15:923:1",
    "15:925:0",
    "15:925:1",
    "15:925:3",
)
PREFILL_COMPANION_DONOR = {
    "15:905:0": "15:898:0",
    "15:905:1": "15:898:1",
    "15:910:0": "15:903:0",
    "15:910:2": "15:903:2",
    "15:911:1": "15:904:1",
    "15:912:1": "15:905:1",
    "15:913:0": "15:906:0",
    "15:913:2": "15:906:2",
    "15:914:0": "15:907:0",
    "15:914:3": "15:907:3",
    "15:915:0": "15:908:0",
    "15:915:2": "15:908:2",
    "15:916:0": "15:909:0",
    "15:916:2": "15:909:2",
    "15:917:0": "15:910:0",
    "15:917:2": "15:910:2",
    "15:918:0": "15:911:0",
    "15:918:2": "15:911:2",
    "15:919:0": "15:912:0",
    "15:919:2": "15:912:2",
    "15:920:0": "15:913:0",
    "15:920:2": "15:913:2",
    "15:921:1": "15:914:1",
    "15:923:0": "15:916:0",
    "15:923:1": "15:916:1",
    "15:925:0": "15:918:0",
    "15:925:1": "15:918:1",
    "15:925:3": "15:918:3",
}
EXACT_BASE_DONOR = {
    905: (15, 898),
    910: (15, 903),
    911: (15, 904),
    912: (15, 905),
    913: (15, 906),
    915: (15, 908),
    916: (15, 909),
    917: (15, 910),
    918: (15, 911),
    919: (15, 912),
    920: (15, 913),
    921: (15, 914),
    923: (15, 916),
    925: (15, 918),
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: ()
        for record_id in TARGET_RECORD_IDS
        if record_id != 914
    },
    914: (
        "15:907:0",
        "15:907:2",
        "15:907:3",
    ),
}
EXPECTED_BASE_RAW_MATCHES = {
    905: ((15, 898),),
    910: ((15, 903),),
    911: ((15, 904),),
    912: ((15, 905),),
    913: ((15, 906),),
    914: (),
    915: ((15, 908),),
    916: ((15, 909),),
    917: ((15, 910),),
    918: ((15, 911),),
    919: ((15, 912),),
    920: ((15, 913),),
    921: ((15, 914),),
    923: (),
    925: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    914: (
        (15, 907),
        (15, 973),
        (15, 1276),
        (15, 1365),
        (15, 1444),
        (15, 1485),
    ),
    923: ((15, 916),),
    925: ((15, 918),),
}
EXPECTED_BASE_MASKED_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    914: ((15, 907),),
    923: ((15, 916),),
    925: ((15, 918),),
}
EXPECTED_CONTROLS_BY_RECORD = {
    905: ((1, 322), ()),
    910: ((), ("025032", "026432")),
    911: ((), ("025032", "026432")),
    912: ((), ("025032", "026432")),
    913: ((), ("025032", "026432")),
    914: ((538, 592), ("029632", "025032", "023C")),
    915: ((), ("025032", "026432")),
    916: ((), ("025032", "026432")),
    917: ((), ("025032", "026432")),
    918: ((), ("025032", "026432")),
    919: ((), ("025032", "026432")),
    920: ((), ("025032", "026432")),
    921: ((), ("025032", "026432")),
    923: ((1174,), ("026432",)),
    925: ((958, 82), ("026432", "024635")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1353,
    queue_start=67,
    queue_stop=134,
    slice_first="15:905:2",
    slice_last="15:937:0",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=("15:914:1",),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(1, 82, 322, 538, 592, 958, 1174),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(894, 949)
    ),
    speaker_style=(
        (905, "forceful_siege_advice"),
        (910, "rough_destabilization_proposal"),
        (911, "energetic_destabilization_proposal"),
        (912, "formal_destabilization_proposal"),
        (913, "polite_destabilization_proposal"),
        (914, "informal_counterintelligence_report"),
        (915, "archaic_destabilization_proposal"),
        (916, "humble_destabilization_proposal"),
        (917, "elderly_destabilization_proposal"),
        (918, "formal_destabilization_proposal"),
        (919, "deliberative_destabilization_proposal"),
        (920, "polite_destabilization_proposal"),
        (921, "formal_destabilization_proposal"),
        (923, "humble_spy_proposal"),
        (925, "confident_ninja_proposal"),
    ),
    terminology_policy=(
        ("castle", "성"),
        ("stratagem", "계책"),
        ("destabilization", "공작"),
        ("military strength", "전력"),
        ("spy", "간자"),
        ("ninja", "시노비"),
        ("defenses", "방비"),
        ("enemy territory", "적 영지"),
        ("dynamic subject particle", "이(가)"),
        ("dynamic destination particle", "에게"),
        ("project ellipsis", "……"),
        ("project exclamation mark", "!"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record fragment array was reviewed as auxiliary evidence; "
        "fourteen complete records reuse approved completed Base Korean "
        "assemblies selected by raw, literal and operand-masked source "
        "identity, while the counterintelligence record uses the same exact "
        "Base assembly through visible semantic references because its "
        "source-identical newline-only fragment has no promoted decision row; "
        "Base runtime and VM state are never inherited; castle, stratagem, "
        "destabilization, military strength, spy, ninja, defenses, enemy "
        "territory, dynamic particles, ellipsis and exclamation wording "
        "retain established historical terminology and each speaker's "
        "completed Base register; calls, inline person, faction, castle and "
        "operation tokens, whitespace, newlines, terminators, complete "
        "record arity, all fifty-two slice prefills, pins, reverse overlays, "
        "two-run reproduction, tamper rejection, outside-scope identity, "
        "optional neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=4,
    pins={
        "expected_queue_universe_sha256": (
            "C6ADAF56AFF67E1F3846197DC22BF265DE81ABFFABFA5D87F3E976F29F3D76D9"
        ),
        "expected_queue_slice_sha256": (
            "268536951F35A2F199277CE4DCD2F0F9D36FF2E284CB1045B69B10052D6A3DAB"
        ),
        "expected_prefilled_coordinate_sha256": (
            "EF680C027B30FC9732C5504FD44B968952E03BFABBBF646366F7D3F96A10DAA0"
        ),
        "expected_prefill_slice_context_sha256": (
            "D50729BA712B3161339703AED7BD631ABAFAD0A70BF8ED061D3F0A7FB515B84E"
        ),
        "expected_target_coordinate_sha256": (
            "F29333A8FFFD1FC91DCC44763339560624D6C58818AA3294CC3759B2973459AA"
        ),
        "expected_source_target_sha256": (
            "24397680517FDB24F88F3CD9C423BB7728591DAAADBE0BE75128E8CDD2D8C9E5"
        ),
        "expected_current_target_sha256": (
            "6B91DD291471491E905545BBF7AAB4C485872AA42F3D4F1F0E44DA50DE9371D9"
        ),
        "expected_context_corpus_sha256": (
            "8930F43DFB214781CF143FAC6A98B068B6446B0436C164F75DCBCF1E51E7F8D9"
        ),
        "expected_gap_contract_sha256": (
            "2554860D3854CDFE0DEA2A88057611AE4B26E08277A0904576DD97514B29B450"
        ),
        "expected_boundary_sha256": (
            "0C576EE7421261C8DF1DA3BD6AC31D24CC9518DC8E0EB9CE68A5992FB4E8C7C5"
        ),
        "expected_runtime_control_sha256": (
            "FBDF57907837F2CEFF488BFF3DAF72126561D3A6E67FE2146C41DFEDA9B99669"
        ),
        "expected_base_search_sha256": (
            "F58A70259DC95E1A1860824B787DD972B578FEF1F41651C0F40209E0C65F039F"
        ),
        "expected_complete_assembly_sha256": (
            "C21E323471E6BF83E92A4C9EE6C94D7FF228934FD15550DB83CBF032EEFA7282"
        ),
        "expected_call_graph_sha256": (
            "23A7142E6B89EB365A43802D3B07F24B05DB1752F5499CF6A222D66E0F41EC03"
        ),
        "expected_speaker_style_sha256": (
            "9C61190D005803C2894A1E2CF7B07AF209EAE556F04F6EDADB9A566F527CA22E"
        ),
        "expected_terminology_policy_sha256": (
            "63F6DC9B5D99CA9E1D9140AA5F9C602F1BCC7A6622F6077D69E8B120616C9788"
        ),
        "expected_translation_policy_sha256": (
            "F59498F9C9BDD107642D4E21A29486AABFE25F90391E92124CA11754A011E5B5"
        ),
        "expected_candidate_sha256": (
            "FE7B76606E58061087990652229E660FC9D36A9827F16EB2E1893EFE4FBDFB50"
        ),
        "expected_combined_slice_candidate_sha256": (
            "8F8CD4EBAAF42DC4B533A60042FC909529765ECD7C540FDF4446FF683BD1B406"
        ),
        "expected_combined_changed_literal_count": 47,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B116_S1353",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B116_S1353.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B116_S1352.private.v1.jsonl",
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
