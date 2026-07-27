#!/usr/bin/env python3
"""Build source-redacted PK B096 segment 1294 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    3559, 3562, 3565, 3569, 3570, 3571, 3572, 3573, 3574,
    3575, 3576, 3577, 3578, 3579, 3580, 3581, 3582, 3584,
)
TARGET_COORDINATES = (
    "9:3559:0",
    "9:3562:0",
    "9:3565:0",
    "9:3569:0",
    "9:3570:0",
    "9:3571:0",
    "9:3572:0",
    "9:3573:0",
    "9:3574:0",
    "9:3575:0",
    "9:3576:0",
    "9:3577:0",
    "9:3578:0",
    "9:3579:0",
    "9:3580:0",
    "9:3581:0",
    "9:3582:0",
    "9:3582:1",
    "9:3584:1",
)
TRANSLATIONS = {
    "9:3559:0": "지금이야말로 쓸 것은…",
    "9:3562:0": "지금이야말로 쓸 것은…",
    "9:3565:0": "지금 활용할 수 있는 것은…",
    "9:3569:0": "지금이야말로 쓸 것은…",
    "9:3570:0": "놈들이 쓰려는 것은…",
    "9:3571:0": "적이 쓰려는 것은…",
    "9:3572:0": "놈들이 꾸미는 것은…",
    "9:3573:0": "적이 노리는 것은…",
    "9:3574:0": "놈들의 노림수는…",
    "9:3575:0": "적이 준비하는 것은…",
    "9:3576:0": "적이 노리는 것은…",
    "9:3577:0": "놈들이 노리는 것은…",
    "9:3578:0": "적이 노리는 것은…",
    "9:3579:0": "적이 준비하는 것은…",
    "9:3580:0": "적이 노리는 것은…",
    "9:3581:0": "적이 쓰려는 것은…",
    "9:3582:0": "적이 쓰려는 것은…",
    "9:3582:1": "인 듯합니다\n경계가 필요합니다",
    "9:3584:1": "에게 조금만 더 힘이 있었다면…",
}
PRIMARY_BASE_RECORD = {
    3559: 3315,
    3562: 3318,
    3565: 3321,
    3569: 3318,
    3570: 3326,
    3571: 3327,
    3572: 3328,
    3573: 3329,
    3574: 3330,
    3575: 3331,
    3576: 3329,
    3577: 3333,
    3578: 3334,
    3579: 3335,
    3580: 3334,
    3581: 3337,
    3584: 3339,
}
MULTI_BASE_MATCHES = {
    3562: ((9, 3318), (9, 3325)),
    3569: ((9, 3318), (9, 3325)),
    3573: ((9, 3329), (9, 3332)),
    3576: ((9, 3329), (9, 3332)),
    3578: ((9, 3334), (9, 3336)),
    3580: ((9, 3334), (9, 3336)),
}
EXPECTED_BASE_MATCHES = {
    record_id: (
        ()
        if record_id == 3582
        else MULTI_BASE_MATCHES.get(
            record_id,
            ((9, PRIMARY_BASE_RECORD[record_id]),),
        )
    )
    for record_id in TARGET_RECORD_IDS
}
SEMANTIC_BASE_CONTEXT = {
    record_id: (
        ("9:3337:0", "9:3337:1")
        if record_id == 3582
        else tuple(
            f"9:{PRIMARY_BASE_RECORD[record_id]}:{literal_id}"
            for literal_id in range(2)
        )
    )
    for record_id in TARGET_RECORD_IDS
}
PREFILL_COMPANION_DONOR = {
    **{
        f"9:{record_id}:1":
        f"9:{PRIMARY_BASE_RECORD[record_id]}:1"
        for record_id in TARGET_RECORD_IDS
        if record_id not in (3582, 3584)
    },
    "9:3584:0": "9:3339:0",
}
EXPECTED_CONTROLS_BY_RECORD = {
    **{
        record_id: ((), ("023C",))
        for record_id in TARGET_RECORD_IDS
        if record_id not in (3582, 3584)
    },
    3582: ((610, 730), ("023C",)),
    3584: ((1,), ("024833",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1294,
    queue_start=134,
    queue_stop=200,
    slice_first="9:3549:0",
    slice_last="9:3595:0",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={record_id: 2 for record_id in TARGET_RECORD_IDS},
    prefill_companion_coordinates=tuple(PREFILL_COMPANION_DONOR),
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(1, 610, 730),
    boundary_record_keys=tuple(
        (9, record_id) for record_id in range(3314, 3597)
    ),
    speaker_style=(
        (3559, "polite_strategy_activation_proposal"),
        (3562, "samurai_strategy_activation_proposal"),
        (3565, "archaic_polite_strategy_opportunity"),
        (3569, "samurai_strategy_activation_proposal"),
        (3570, "rough_enemy_strategy_warning"),
        (3571, "formal_enemy_strategy_warning"),
        (3572, "archaic_polite_enemy_strategy_warning"),
        (3573, "polite_enemy_strategy_warning"),
        (3574, "concerned_enemy_strategy_warning"),
        (3575, "genteel_enemy_strategy_counterproposal"),
        (3576, "polite_enemy_strategy_warning"),
        (3577, "scholarly_enemy_strategy_warning"),
        (3578, "polite_enemy_strategy_warning"),
        (3579, "formal_enemy_strategy_warning"),
        (3580, "polite_enemy_strategy_warning"),
        (3581, "archaic_formal_enemy_strategy_warning"),
        (3582, "systemic_enemy_strategy_warning"),
        (3584, "dynamic_lord_death_lament"),
    ),
    terminology_policy=(
        ("runtime strategy token", "inline token 023C"),
        ("runtime house token", "inline token 024833"),
        ("enemy intent", "쓰려는 것·노리는 것·노림수"),
        ("prepared strategy", "준비하는 것"),
        ("scheme", "꾸미는 것"),
        ("warning", "경계"),
        ("scholarly proverb", "군자는 위태로운 곳에 가까이하지 않는 법"),
        ("lord death", "님께서 전사하셨다고"),
        ("dynamic house particle", "에게"),
        ("project ellipsis", "…"),
    ),
    basis=(
        "pristine PK JP is authoritative and all available EN, SC and TC "
        "same-record arrays were manually reviewed; sixteen strategy-token "
        "records and the lord-death record have exact completed Base source "
        "matches, whose final Korean supplies semantic wording, historical "
        "speaker register and approved same-record companions only, while the "
        "two-call strategy warning uses the closest completed Base semantic "
        "pattern; Base runtime and VM state are never inherited; each strategy "
        "name remains between its established predicate prefix and companion "
        "ending, and rough, polite, archaic, samurai, concerned, genteel and "
        "scholarly registers remain distinct; inline tokens 023C and 024833, "
        "direct calls 1, 610 and 730, literal arity, newlines, gaps, "
        "terminators and all forty-seven slice prefills are guarded; all "
        "pins, two-run reproduction, tamper rejection, mutual neighbors, "
        "reverse overlays, outside-scope identity and Steam read-only state "
        "are also guarded"
    ),
    expected_changed_literal_count=19,
    pins={
        "expected_queue_universe_sha256":
        "FFE606C0376874044693E13F95C68B233DC7D70ED48366C9EC52010B5E270236",
        "expected_queue_slice_sha256":
        "C62E8B0050C45267A33AC8F37F87DA9E2141894D905AF9B9F393A077F64CCB4B",
        "expected_prefilled_coordinate_sha256":
        "45D6A10988F892F0D15009AE097F24C21DF8D2E9130E80BEFB6C25D943DF5591",
        "expected_prefill_slice_context_sha256":
        "4DA420A28BF037DEA5646333591AED2B455960E2CB7491F0CFDA930BF1D6803E",
        "expected_target_coordinate_sha256":
        "EFC7204E574FDA4AE833DE6C05D6E73EFB31E97CC27399A17F099AF730DE08F1",
        "expected_source_target_sha256":
        "05381EF5F8D942337C4D53F383037D9B53A6838AA7D8B750EB62B9D1A57EC547",
        "expected_current_target_sha256":
        "8898C774B4C90D86E65C921D4020610FC5E293C8689F03D5212EBE751C72699C",
        "expected_context_corpus_sha256":
        "EF8BFDCD39D7AEB724AD77E0657F2AFAECF8C8DF22229A4806CFFC217EABA22A",
        "expected_gap_contract_sha256":
        "2C154C43EFAA87777F07483AB15FF7CA92B52B7932EC894BBCBB51A6726561CE",
        "expected_boundary_sha256":
        "93EFBF0E35BFE2111AB826DA7C31E2CC9031149BE244E12691E992609963C876",
        "expected_runtime_control_sha256":
        "52DEF610005372E635CE820D879FF72A54C7FC889DBAB3A791A3F59DC82A0A30",
        "expected_base_search_sha256":
        "D97D9E4B11D968449EBD9DC2699C0353E7A561391680B92D5205B4ADC11D282D",
        "expected_complete_assembly_sha256":
        "87612D7367F3B80424A256BAD2E7DBECC889D4308C91A00F6E9E6859E056EF74",
        "expected_call_graph_sha256":
        "2D781A80132E105816B3CF7C817D5E5570B7B87DA8EE592A05D35366E11EE153",
        "expected_speaker_style_sha256":
        "796B66BB1CA1A60CCDF4EE4F72B47E6281D21BB82C109D7BAE1339B8093EE5B4",
        "expected_terminology_policy_sha256":
        "00D0249896A259FF0D40F8CB906E49BA8621C8A882884CA97B14C9B53C1ABA81",
        "expected_translation_policy_sha256":
        "C62EB0D42E0018D3DEFC37AA4649D223E5798ACF6219F8BA93020D5E3F6AD143",
        "expected_candidate_sha256":
        "36B37651324612B98349C1A5617614044E98F3FD59C5F20F143A6535B333475C",
        "expected_combined_slice_candidate_sha256":
        "257A5F07A1D0A143A2A2843ED30A05441ED1C872C521C03F63AB49097E2B1DED",
        "expected_combined_changed_literal_count": 63,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B096_S1294",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B096_S1294.private.v1.jsonl"
    ),
    "optional_neighbors": tuple(
        COMMON.DECISIONS_ROOT
        / f"pk_msggame_B096_S{segment}.private.v1.jsonl"
        for segment in (1292, 1293)
    ),
    "queue_batch_id": "pk_msggame-B096",
    "queue_row_count": 140,
    "queue_visible_count": 200,
    "queue_first": "9:3456:0",
    "queue_last": "9:3595:0",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 9)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
