#!/usr/bin/env python3
"""Build source-redacted PK B096 segment 1293 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    3507, 3508, 3509, 3512, 3513, 3514,
    3515, 3516, 3518, 3522, 3529, 3533,
)
CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1293,
    queue_start=67,
    queue_stop=134,
    slice_first="9:3507:2",
    slice_last="9:3548:0",
    target_coordinates=(
        "9:3507:2",
        "9:3508:1",
        "9:3508:2",
        "9:3508:3",
        "9:3509:1",
        "9:3509:2",
        "9:3509:3",
        "9:3512:1",
        "9:3513:0",
        "9:3513:1",
        "9:3513:2",
        "9:3514:0",
        "9:3514:1",
        "9:3514:2",
        "9:3515:0",
        "9:3515:2",
        "9:3516:1",
        "9:3518:1",
        "9:3522:0",
        "9:3529:0",
        "9:3533:0",
    ),
    translations={
        "9:3507:2": "…",
        "9:3508:1": "!\n",
        "9:3508:2": "의 대승리",
        "9:3508:3": "!",
        "9:3509:1": "!\n",
        "9:3509:2": "의 대승리",
        "9:3509:3": "!",
        "9:3512:1": "…\n",
        "9:3513:0": "본성을 장악한 것",
        "9:3513:1": "!\n",
        "9:3513:2": ", 이로써 제압한 것",
        "9:3514:0": "본성을 빼앗겨\n",
        "9:3514:1": "은 함락된 것",
        "9:3514:2": "…",
        "9:3515:0": "성주를 항복시킨 것",
        "9:3515:2": ", 이로써 제압한 것",
        "9:3516:1": "…!",
        "9:3518:1": "…!",
        "9:3522:0": "보아하니…",
        "9:3529:0": "보아하니…",
        "9:3533:0": "보아하니…",
    },
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={
        3507: 3,
        3508: 4,
        3509: 4,
        3512: 3,
        3513: 3,
        3514: 3,
        3515: 3,
        3516: 2,
        3518: 2,
        3522: 2,
        3529: 2,
        3533: 2,
    },
    prefill_companion_coordinates=(
        "9:3507:0",
        "9:3507:1",
        "9:3508:0",
        "9:3509:0",
        "9:3512:0",
        "9:3512:2",
        "9:3516:0",
        "9:3518:0",
        "9:3522:1",
        "9:3529:1",
        "9:3533:1",
    ),
    prefill_companion_donor={
        "9:3507:0": "9:3266:0",
        "9:3507:1": "9:3266:1",
        "9:3508:0": "9:3267:0",
        "9:3509:0": "9:3268:0",
        "9:3512:0": "9:3271:0",
        "9:3512:2": "9:3271:2",
        "9:3516:0": "9:3272:0",
        "9:3518:0": "9:3274:0",
        "9:3522:1": "9:3278:1",
        "9:3529:1": "9:3285:1",
        "9:3533:1": "9:3285:1",
    },
    hidden_current_companion_coordinates=("9:3515:1",),
    semantic_base_context={
        3507: ("9:3266:0", "9:3266:1", "9:3266:2"),
        3508: (
            "9:3267:0", "9:3267:1", "9:3267:2", "9:3267:3",
        ),
        3509: (
            "9:3268:0", "9:3268:1", "9:3268:2", "9:3268:3",
        ),
        3512: ("9:3271:0", "9:3271:1", "9:3271:2"),
        3513: ("9:3267:0", "9:3267:1", "9:3267:2", "9:3267:3"),
        3514: ("9:3271:0", "9:3271:1", "9:3271:2"),
        3515: ("9:3267:0", "9:3267:1", "9:3267:2", "9:3267:3"),
        3516: ("9:3272:0", "9:3272:1"),
        3518: ("9:3274:0", "9:3274:1"),
        3522: ("9:3278:0", "9:3278:1"),
        3529: ("9:3285:0", "9:3285:1"),
        3533: ("9:3289:0", "9:3289:1"),
    },
    expected_base_raw_matches={
        3507: (),
        3508: (),
        3509: (),
        3512: (),
        3513: (),
        3514: (),
        3515: (),
        3516: (),
        3518: (),
        3522: ((9, 3278),),
        3529: ((9, 3285), (9, 3289)),
        3533: ((9, 3285), (9, 3289)),
    },
    expected_base_literal_matches={
        3507: ((9, 3266),),
        3508: ((9, 3267),),
        3509: ((9, 3268),),
        3512: ((9, 3271),),
        3513: (),
        3514: (),
        3515: (),
        3516: ((9, 3272),),
        3518: ((9, 3274),),
        3522: ((9, 3278),),
        3529: ((9, 3285), (9, 3289)),
        3533: ((9, 3285), (9, 3289)),
    },
    expected_base_masked_matches={
        3507: ((9, 3266),),
        3508: ((9, 3267),),
        3509: ((9, 3268),),
        3512: ((9, 3271),),
        3513: (),
        3514: (),
        3515: (),
        3516: ((9, 3272),),
        3518: ((9, 3274),),
        3522: ((9, 3278),),
        3529: ((9, 3285), (9, 3289)),
        3533: ((9, 3285), (9, 3289)),
    },
    expected_controls_by_record={
        3507: ((568, 778), ()),
        3508: ((628, 7, 568), ()),
        3509: ((538, 7, 568), ()),
        3512: ((538, 7), ()),
        3513: ((538, 568), ("026432",)),
        3514: ((538,), ("026432",)),
        3515: ((538, 568), ("026432",)),
        3516: ((34, 538), ()),
        3518: ((34, 538), ()),
        3522: ((), ("02AC32",)),
        3529: ((), ("02AC32",)),
        3533: ((), ("02AC32",)),
    },
    source_call_roots=(7, 34, 538, 568, 628, 778),
    boundary_record_keys=tuple(
        (9, record_id) for record_id in range(3265, 3550)
    ),
    speaker_style=(
        (3507, "dynamic_disadvantage_retreat_assessment"),
        (3508, "dynamic_total_enemy_defeat_victory"),
        (3509, "dynamic_last_enemy_retreat_victory"),
        (3512, "dynamic_route_destruction_defeat"),
        (3513, "dynamic_citadel_capture_occupation"),
        (3514, "dynamic_citadel_loss_fall"),
        (3515, "dynamic_castle_lord_surrender_occupation"),
        (3516, "dynamic_officer_death_shock"),
        (3518, "dynamic_officer_capture_shock"),
        (3522, "casual_dynamic_pincer_suggestion"),
        (3529, "formal_dynamic_pincer_suggestion"),
        (3533, "formal_dynamic_pincer_suggestion"),
    ),
    terminology_policy=(
        ("citadel or inner bailey", "본성"),
        ("castle lord", "성주"),
        ("capture or secure", "장악하다"),
        ("castle fall", "함락되다"),
        ("occupation", "제압하다"),
        ("pincer attack", "협격"),
        ("runtime nominal stem", "…한 것"),
        ("project ellipsis", "…"),
    ),
    basis=(
        "pristine PK JP is authoritative and all available EN, SC and TC "
        "same-record context was manually reviewed; nine records reuse exact "
        "completed Base semantic fragments and same-record prefills, while "
        "three PK-only citadel occupation, fall and castle-lord surrender "
        "records use completed Base victory and defeat terminology as meaning "
        "context only; Base runtime and VM state are never inherited; the "
        "PK-only result records were rebuilt as nominal stems so the live "
        "runtime copular terminals form natural Korean across polite, plain, "
        "archaic and honorific speaker variants rather than duplicating a "
        "completed ending; all twelve complete records preserve direct calls, "
        "castle and force tokens, hidden newline, punctuation, literal arity, "
        "gaps and approved same-record prefills; all pins, two-run "
        "reproduction, tamper rejection, mutual neighbors, reverse overlays, "
        "outside-scope identity and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=16,
    pins={
        "expected_queue_universe_sha256":
        "FFE606C0376874044693E13F95C68B233DC7D70ED48366C9EC52010B5E270236",
        "expected_queue_slice_sha256":
        "2228790DFAC3827F11887CB4D1CB89C46CE85711684ACA5C60D07C3667C32BCE",
        "expected_prefilled_coordinate_sha256":
        "7DD0404B6475183DDDD15995B56FF9A6EFD730DE6577F07646924B59C46A1A95",
        "expected_prefill_slice_context_sha256":
        "E844CF8A6ADFC09CA73EDD6558A01F2F4ABDF8655B4A5128D6C95CB14F326748",
        "expected_target_coordinate_sha256":
        "FF8FFACB7A78F010EAC2684E79314B0C0C9D186F38FF87B7E55C70E292BE178E",
        "expected_source_target_sha256":
        "7B90CC1D836367F67375195FF7EB282305EBE2390A3B0BF2C5190EE8C232AEDA",
        "expected_current_target_sha256":
        "D4E25DF15EED0881301F42624F4AA072DF5D9B0A0CE9A4DE3B8D5351DFCEF7F2",
        "expected_context_corpus_sha256":
        "EF8BFDCD39D7AEB724AD77E0657F2AFAECF8C8DF22229A4806CFFC217EABA22A",
        "expected_gap_contract_sha256":
        "3ACFEC380C309FDBAD0B76A05D524E0B423BF951F20D585116B46C804F1EC5A5",
        "expected_boundary_sha256":
        "8A027FC3469D313E48996316549D7338B65B5BDDFC4EB08E3EBCA89E1536F63F",
        "expected_runtime_control_sha256":
        "D08F7767F498596A55F713C3D393F81E8094EC5DD574788C9495A1C2E5391E52",
        "expected_base_search_sha256":
        "C79CF6945E2101F0D5D446F6831309EC0A0ACA3C363AF0F3D427DEA01C62C412",
        "expected_complete_assembly_sha256":
        "1F3630D805587DE5F5DDD199A8F8942E19081E5C2B7540FC8162C9681D229167",
        "expected_call_graph_sha256":
        "4EA3CF32C7A75F77F39A486A53979DB7083C375E61676D1DA3551646B377FAF0",
        "expected_speaker_style_sha256":
        "B22447800CA06425FF2A5EE2B35B230255B1DE43377A006BF0AD4BB8481DD751",
        "expected_terminology_policy_sha256":
        "6E459CA0B1BF207B3F4A11052A6948FCDA231AB2F8B1213C2A53AF7073615671",
        "expected_translation_policy_sha256":
        "6DD3FF7F4414773AA2E7CBFB8AE1D60F4019282859765DA156B2BDA011588BC3",
        "expected_candidate_sha256":
        "BA97EF9D867E788AA0907B1784735E400CD66E955B3AF77613E485F685409125",
        "expected_combined_slice_candidate_sha256":
        "D4C1A9CFBF294F3C874313CDDC63631C01A3B2109A15EDE93AF4370CBCBC01BF",
        "expected_combined_changed_literal_count": 54,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B096_S1293",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B096_S1293.private.v1.jsonl"
    ),
    "optional_neighbors": tuple(
        COMMON.DECISIONS_ROOT
        / f"pk_msggame_B096_S{segment}.private.v1.jsonl"
        for segment in (1292, 1294)
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
