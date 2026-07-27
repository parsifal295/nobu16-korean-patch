#!/usr/bin/env python3
"""Build source-redacted PK B113 segment 1343 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    484,
    485,
    487,
    491,
    519,
)
TARGET_COORDINATES = (
    "15:484:1",
    "15:484:2",
    "15:484:5",
    "15:485:1",
    "15:485:2",
    "15:485:4",
    "15:485:5",
    "15:485:6",
    "15:487:1",
    "15:491:0",
    "15:519:0",
)
TRANSLATIONS = {
    "15:484:1": "!\n",
    "15:484:2": "의",
    "15:484:5": "!",
    "15:485:1": "!\n",
    "15:485:2": "의",
    "15:485:4": "째로",
    "15:485:5": "에 귀순하",
    "15:485:6": "!",
    "15:487:1": "이(가) 부상",
    "15:491:0": "지금은",
    "15:519:0": "의",
}
EXPECTED_ARITY = {
    484: 6,
    485: 7,
    487: 2,
    491: 2,
    519: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "15:484:0",
    "15:484:3",
    "15:484:4",
    "15:485:0",
    "15:485:3",
    "15:487:0",
    "15:491:1",
    "15:519:1",
)
PREFILL_COMPANION_DONOR = {
    "15:484:0": "15:467:0",
    "15:484:3": "15:467:3",
    "15:484:4": "15:467:4",
    "15:485:0": "15:478:0",
    "15:485:3": "15:478:3",
    "15:487:0": "15:480:0",
    "15:491:1": "15:484:1",
    "15:519:1": "15:512:1",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = ()
EXACT_BASE_DONOR = {
    484: (15, 467),
    485: (15, 478),
    487: (15, 480),
    491: (15, 484),
    519: (15, 512),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: tuple(
        f"{donor[0]}:{donor[1]}:{literal_id}"
        for literal_id in range(EXPECTED_ARITY[record_id])
    )
    for record_id, donor in EXACT_BASE_DONOR.items()
}
EXPECTED_BASE_RAW_MATCHES = {
    484: (),
    485: (),
    487: ((15, 480),),
    491: ((15, 484),),
    519: ((15, 512),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    484: tuple((15, record_id) for record_id in range(467, 478)),
    485: ((15, 478),),
    487: ((15, 480),),
    491: ((15, 484),),
    519: ((15, 512),),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
EXPECTED_CONTROLS_BY_RECORD = {
    484: ((82, 550), ("023C", "024833", "025032")),
    485: ((82, 628, 514), ("023C", "024833", "026432", "025032")),
    487: ((), ("024633", "024733")),
    491: ((), ("028C32",)),
    519: ((), ("029632", "028C32")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1343,
    queue_start=0,
    queue_stop=67,
    slice_first="15:484:0",
    slice_last="15:521:0",
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
    source_call_roots=(
        82,
        514,
        550,
        628,
    ),
    boundary_record_keys=tuple(
        (15, record_id)
        for record_id in range(460, 528)
    ),
    speaker_style=(
        (484, "urgent_formal_betrayal_report"),
        (485, "urgent_formal_domain_betrayal_report"),
        (487, "concise_failed_recruitment_report"),
        (491, "pragmatic_adviser_observation"),
        (519, "formal_courtly_material_aid_proposal"),
    ),
    terminology_policy=(
        ("urgent report", "큰일이"),
        ("our house", "우리 가문"),
        ("submission or defection", "귀순"),
        ("whole domain suffix", "째로"),
        ("recruitment persuasion", "회유"),
        ("injury", "부상"),
        ("our side", "우리 편"),
        ("wartime", "전시"),
        ("material supplies", "물자"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record entry was reviewed as auxiliary context; all eleven "
        "residual literals complete approved Base Korean records, with "
        "records 484 and 485 using literal-and-masked-call exact donors and "
        "records 487, 491 and 519 using byte-identical donors; Base runtime "
        "and VM state are never inherited; urgent betrayal reports, whole-"
        "domain defection, recruitment persuasion, injury, pragmatic "
        "material aid and the formal courtly proposal preserve established "
        "project terminology and speaker registers; ASCII exclamation "
        "marks, direct calls, inline person, house, domain and tribe tokens, "
        "gaps, protected outer whitespace, line counts, literal arity, "
        "terminators, all eight same-record companions, all fifty-six slice "
        "prefills, complete assemblies, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, optional "
        "neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=7,
    pins={
        "expected_queue_universe_sha256": (
            "6C349A528565248A1F4B3505C88EFF2FE9319565E988090698E9D8361AE92F89"
        ),
        "expected_queue_slice_sha256": (
            "6439CEC85F31B9733FEF4FFCD639B1E8719716111122E3863471652437583EDE"
        ),
        "expected_prefilled_coordinate_sha256": (
            "3146158A5682BF2AEB8635F5265341E844703CD212330666CBE6CE2FF1D4F4DE"
        ),
        "expected_prefill_slice_context_sha256": (
            "E4DC0D46C3B13F0493C147C3067436C4E330DB76A57901C7432A0EDC25E3169F"
        ),
        "expected_target_coordinate_sha256": (
            "CF2B15078EC5423D8F27EC24B0C10F27BC03E816DE1DB881E4952469E18B79EA"
        ),
        "expected_source_target_sha256": (
            "86C823F787EEEAF875F68BE17077F4BCF302A78161369B4F79FFB0C4445A900E"
        ),
        "expected_current_target_sha256": (
            "A747293BC23517B4EC487B100FDE4FA9FA8950905A6C010365ECD67D38178812"
        ),
        "expected_context_corpus_sha256": (
            "288366D1942DFD99B7108EB5E47075BFE8EFECEC2B67DDEDB512C81668CC7712"
        ),
        "expected_gap_contract_sha256": (
            "43F8180D6A89A34EDBAAB0867B9DCA3CED450581E7ADC572296878E758CF9021"
        ),
        "expected_boundary_sha256": (
            "65EB608BA51821978538FD24B936C8D03351601F4F4327C7A7D97566FF8DFC9E"
        ),
        "expected_runtime_control_sha256": (
            "526C8BC76AFC24F9394DC43779E6F8CBBDC67D4A0EAED51EFD79AC44A49A0E34"
        ),
        "expected_base_search_sha256": (
            "63B79BD0C983B8FFF24964B1574ECE16FD5CB048E26DFAA2E7E41A3EB5C68645"
        ),
        "expected_complete_assembly_sha256": (
            "2328656D12A805496F803D4EBC37EE5BBAFB54CD44ED2C2DCB57E00DDE44205D"
        ),
        "expected_call_graph_sha256": (
            "69BCB17748A252CF3704E57A50C064FFD0CA451E8BA495995C87BA7B4A02338A"
        ),
        "expected_speaker_style_sha256": (
            "3FEE93E8C3B45691D91FDD959174861A342A997C609C34FD2F5CC4D0C3403E52"
        ),
        "expected_terminology_policy_sha256": (
            "67DF1D934C69E4F6985AF3F048A24EF4164D47B66D01DD4A29992CAC935983DC"
        ),
        "expected_translation_policy_sha256": (
            "6C0E85DD02B70B905A488ED8EC68ACC9D21F434C2123AF29512774A3BA4BB141"
        ),
        "expected_candidate_sha256": (
            "595027D20EAAF5051C8CD6D3C39020D0EFFECEED9BE6AA853253824FB206B64C"
        ),
        "expected_combined_slice_candidate_sha256": (
            "C9EFF4BCEA221E3196F444A0FCC7F7D6F456DE04F02FF6ED8FEBD12904BD1076"
        ),
        "expected_combined_changed_literal_count": 61,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B113_S1343",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B113_S1343.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B113_S1344.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B113_S1345.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B113",
    "queue_row_count": 107,
    "queue_visible_count": 200,
    "queue_first": "15:484:0",
    "queue_last": "15:590:0",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
