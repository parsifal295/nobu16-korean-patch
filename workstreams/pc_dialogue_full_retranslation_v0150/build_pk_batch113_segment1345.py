#!/usr/bin/env python3
"""Build source-redacted PK B113 segment 1345 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = tuple(range(556, 586))
TARGET_COORDINATES = tuple(
    f"15:{record_id}:0" for record_id in TARGET_RECORD_IDS
)
TRANSLATIONS = {
    coordinate: "의" for coordinate in TARGET_COORDINATES
}
EXPECTED_ARITY = {
    record_id: 2 for record_id in TARGET_RECORD_IDS
}
PREFILL_COMPANION_COORDINATES = tuple(
    f"15:{record_id}:1" for record_id in TARGET_RECORD_IDS
)
EXACT_BASE_DONOR = {
    **{record_id: (15, 549) for record_id in range(556, 562)},
    562: (15, 555),
    563: (15, 556),
    564: (15, 557),
    565: (15, 558),
    566: (15, 559),
    567: (15, 560),
    **{record_id: (15, 561) for record_id in range(568, 574)},
    574: (15, 567),
    575: (15, 568),
    576: (15, 569),
    577: (15, 570),
    578: (15, 571),
    579: (15, 572),
    **{record_id: (15, 573) for record_id in range(580, 586)},
}
PREFILL_COMPANION_DONOR = {
    f"15:{record_id}:1": (
        f"{EXACT_BASE_DONOR[record_id][0]}:"
        f"{EXACT_BASE_DONOR[record_id][1]}:1"
    )
    for record_id in TARGET_RECORD_IDS
}
SEMANTIC_BASE_CONTEXT = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    **{
        record_id: tuple(
            (15, donor_id) for donor_id in range(549, 555)
        )
        for record_id in range(556, 562)
    },
    562: ((15, 555),),
    563: ((15, 556),),
    564: ((15, 557),),
    565: ((15, 558),),
    566: ((15, 559),),
    567: ((15, 560),),
    **{
        record_id: tuple(
            (15, donor_id) for donor_id in range(561, 567)
        )
        for record_id in range(568, 574)
    },
    574: ((15, 567),),
    575: ((15, 568),),
    576: ((15, 569),),
    577: ((15, 570),),
    578: ((15, 571),),
    579: ((15, 572),),
    **{
        record_id: tuple(
            (15, donor_id) for donor_id in range(573, 579)
        )
        for record_id in range(580, 586)
    },
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ("029632", "028C32"))
    for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1345,
    queue_start=134,
    queue_stop=200,
    slice_first="15:556:0",
    slice_last="15:590:0",
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
    source_call_roots=(),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(545, 598)
    ),
    speaker_style=(
        *tuple(
            (record_id, "formal_initial_appeasement_proposal")
            for record_id in range(556, 562)
        ),
        (562, "rough_appeasement_continuation"),
        (563, "archaic_appeasement_continuation"),
        (564, "elderly_appeasement_continuation"),
        (565, "formal_appeasement_continuation"),
        (566, "samurai_appeasement_continuation"),
        (567, "energetic_appeasement_continuation"),
        *tuple(
            (record_id, "formal_full_appeasement_proposal")
            for record_id in range(568, 574)
        ),
        (574, "rough_appeasement_completion"),
        (575, "formal_appeasement_completion"),
        (576, "archaic_appeasement_completion"),
        (577, "polite_appeasement_completion"),
        (578, "formal_appeasement_completion"),
        (579, "eccentric_humble_appeasement_completion"),
        *tuple(
            (record_id, "formal_final_appeasement_proposal")
            for record_id in range(580, 586)
        ),
    ),
    terminology_policy=(
        ("appeasement", "회유"),
        ("reinforcements", "원군"),
        ("clan", "우리 가문"),
        ("local warriors", "국인중"),
        ("integrate", "편입"),
        ("retainer", "가신"),
        ("join battle", "참전"),
        ("stratagem", "조략"),
        ("dynamic possessive particle", "의"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record fragment array was reviewed as auxiliary evidence; all "
        "thirty complete records reuse approved completed Base Korean "
        "assemblies selected by raw, literal and operand-masked source "
        "identity; Base runtime and VM state are never inherited; the "
        "manually approved possessive fragments join thirty exact Base "
        "prefill companions while retaining the PK inline local-warrior and "
        "faction tokens; appeasement, reinforcements, clan, local warriors, "
        "integration, retainers, battle participation and stratagem terms "
        "retain their historical project usage, and each continuation and "
        "completion response preserves its completed Base speaker register; "
        "tokens, whitespace, newlines, terminators, complete record arity, "
        "all thirty-six slice prefills, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, optional "
        "neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=0,
    pins={
        "expected_queue_universe_sha256": (
            "6C349A528565248A1F4B3505C88EFF2FE9319565E988090698E9D8361AE92F89"
        ),
        "expected_queue_slice_sha256": (
            "EA2D3633728F530E67CE8BA8AA8C00343D6F29B8783928BE3830029E6E2DE4E0"
        ),
        "expected_prefilled_coordinate_sha256": (
            "5FF5D938492EBFECBA988A58FBE75F22E5B67848401B9D887C34B257ABE46C0B"
        ),
        "expected_prefill_slice_context_sha256": (
            "1A2386EDA840BCB4F9AC209E5BA17933B624026BAC5E74A6123F231CB6AF63D7"
        ),
        "expected_target_coordinate_sha256": (
            "98A3890E5BF7A5440EB37ED4B26EF462FF7985BA25D6EEAC20B74DE9C7F047F7"
        ),
        "expected_source_target_sha256": (
            "3CDA9E27A16E2847E8F96E77191487477C0154898A682971B109DEB40C95A59A"
        ),
        "expected_current_target_sha256": (
            "9FAC0B901E1B40810C1E9CE22A24A81CB8239241FB98F5E675AFEE630AF11E26"
        ),
        "expected_context_corpus_sha256": (
            "288366D1942DFD99B7108EB5E47075BFE8EFECEC2B67DDEDB512C81668CC7712"
        ),
        "expected_gap_contract_sha256": (
            "314C513D96C3BCB03A277DBE70B4AD9D23CD133F39D7A8E9CADF5A84CD2FFEB9"
        ),
        "expected_boundary_sha256": (
            "39009E62CF7F369A2E22F2E7F592E0CEBDEFE1EF4DE72A03E8B3913EBC99C2C4"
        ),
        "expected_runtime_control_sha256": (
            "406537675A79849DDD9A0B9F1C694A29C0C1FA10528BB0B32B3E136F95A34349"
        ),
        "expected_base_search_sha256": (
            "F68FD4963324B5DBFA0147FB0B95DE00E49CBA935FA5325AB968646F3059C10B"
        ),
        "expected_complete_assembly_sha256": (
            "C5D18509756DBCEBD7FC69D121EA12F14C5B34694F51A7E619951ECFEEAFFEE9"
        ),
        "expected_call_graph_sha256": (
            "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
        ),
        "expected_speaker_style_sha256": (
            "93582E718CC62AD9EAF439CF35F3CE2DD96397644865E8CE80EA8CBCE6052F0A"
        ),
        "expected_terminology_policy_sha256": (
            "41A4DD1931E5C2319EFEEF271C89C1599BB2988511E1C6E2F113CAAAC9D24A83"
        ),
        "expected_translation_policy_sha256": (
            "9FAC0B901E1B40810C1E9CE22A24A81CB8239241FB98F5E675AFEE630AF11E26"
        ),
        "expected_candidate_sha256": (
            "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
        ),
        "expected_combined_slice_candidate_sha256": (
            "EDB9C53EBCED5C90652F311F0311C8FDCA80394A2C3909C0DCCDCB5F10022AEC"
        ),
        "expected_combined_changed_literal_count": 36,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B113_S1345",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B113_S1345.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B113_S1343.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B113_S1344.private.v1.jsonl",
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
