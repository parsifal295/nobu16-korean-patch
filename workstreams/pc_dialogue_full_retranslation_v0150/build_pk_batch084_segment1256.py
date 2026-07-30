#!/usr/bin/env python3
"""Build source-redacted PK B084 segment 1256 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_QUEUE_EVIDENCE = COMMON.queue_evidence

TARGET_RECORD_IDS = (1258,)
CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1256,
    queue_start=0,
    queue_stop=67,
    slice_first="9:1241:0",
    slice_last="9:1306:0",
    target_coordinates=("9:1258:1",),
    translations={"9:1258:1": "이다!"},
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={1258: 2},
    prefill_companion_coordinates=("9:1258:0",),
    prefill_companion_donor={"9:1258:0": "9:1184:0"},
    hidden_current_companion_coordinates=(),
    semantic_base_context={
        1258: ("9:1184:0", "9:1184:1"),
    },
    expected_base_raw_matches={
        1258: ((9, 1184),),
    },
    expected_base_literal_matches={
        1258: ((9, 1184),),
    },
    expected_base_masked_matches={
        1258: ((9, 1184),),
    },
    expected_controls_by_record={
        1258: ((4,), ()),
    },
    source_call_roots=(4,),
    boundary_record_keys=tuple(
        (9, record_id)
        for record_id in (
            1183, 1184, 1185,
            1240, 1241,
            1257, 1258, 1259,
            1306, 1307,
            1373, 1374,
        )
    ),
    speaker_style=(
        (1258, "vengeful_dynamic_avenger_declaration"),
    ),
    terminology_policy=(
        ("the fallen", "쓰러진 모두"),
        ("avenge", "원수를 갚다"),
        ("dynamic avenger", "갚을 자"),
        ("copular declaration", "이다"),
        ("ASCII exclamation", "!"),
    ),
    basis=(
        "pristine PK JP is authoritative and complete EN, SC and TC context "
        "was manually reviewed; the exact completed Base record supplies "
        "semantic, terminology and speaker-register evidence only, with no "
        "Base runtime or VM state inherited; the approved same-record prefill "
        "and the residual copular close assemble the complete vengeful "
        "declaration around the dynamic avenger token while preserving the "
        "call, protected whitespace and gaps; all sixty-six prefills in the "
        "opening slice and all sixty-seven prefills in the zero-residual "
        "middle slice have independently pinned coordinates, contexts and "
        "multilingual boundaries; two-run reproduction, tamper rejection, "
        "mutual neighbors, reverse overlays, outside-scope identity and Steam "
        "read-only state are guarded"
    ),
    expected_changed_literal_count=1,
    pins={
        "expected_queue_universe_sha256":
        "62ED4EA4F16E14C14AD2DF138475242E7459FA539CFD4F655BFBA311B1D2E2FB",
        "expected_queue_slice_sha256":
        "DB873851BB5ADE3970375FF8D93E7D3069E50EA62A0D3070089F6F6B30B25F9E",
        "expected_prefilled_coordinate_sha256":
        "A372B93862582F0D138AB94D6BD1D355DA14E3488355EAD035E89BAC503F5136",
        "expected_prefill_slice_context_sha256":
        "2C4BA2039E66A33E526A1F151D2734B05EA70FF9B5ACA0B7E52FB3C537F590AF",
        "expected_target_coordinate_sha256":
        "E61130530BCAEE70DA5D7A8C58D031BFAB799714AC07870EF53578BCB1215047",
        "expected_source_target_sha256":
        "D95F33428A0B7EAC043099F055B9BE6F53723DDA3E1E463AF6A0F813FA9388B1",
        "expected_current_target_sha256":
        "DCD4D540F3EEEA748A4C8257863BDDD5DDFC9D889E18FAEA01FB6894D7318D1B",
        "expected_context_corpus_sha256":
        "9B9312B977AB0307C30CEEFD3C52B519C9937C6862B7ADC3472A889D79A5DB3B",
        "expected_gap_contract_sha256":
        "68362D01221E2D7D04354026A391D9923A41C56620332F513BA971FDB8E2D31E",
        "expected_boundary_sha256":
        "46D41806ACF4AE8301F9054D9926B6F296D95F237437B49294B399742F2F86C9",
        "expected_runtime_control_sha256":
        "90D73A052EFEA585F5213A6C910D8955DEF5ED3FD57CD639F3D160C2B62E47F2",
        "expected_base_search_sha256":
        "4D5EBC4D9CEABE4E3BB2C042D18378CE5C90DB5FDD301EEA0E6F812D5C356FD9",
        "expected_complete_assembly_sha256":
        "67A75CC9171F8CE52089C50DD4F43B138092FD1E8CC5A39CE80328676FA819CD",
        "expected_call_graph_sha256":
        "D533F6037A0D3576960678D3BE1AF850947985CE89ADD6C62DDEF2957199D768",
        "expected_speaker_style_sha256":
        "D659CBA8E1FC2522917250AE1053CE33484AE0B7C117D7C185D3C62E917EE464",
        "expected_terminology_policy_sha256":
        "DA8BAD2F0D4FF3B727AAB2A1E273ED1AD5CEE993672C74D7E3C0C0A98E5A322F",
        "expected_translation_policy_sha256":
        "DD7C89EFCE801E39DCCA876B5578849C8A10ED91FFDEDA6343DAFD29A25520F6",
        "expected_candidate_sha256":
        "F82AB472E19CF733D589DD0C02A166009B1D21F69A944CF26B870DAA55C5C416",
        "expected_combined_slice_candidate_sha256":
        "AA29BFB02749CE59EA26D8469328A807AE155AD828029BD8B6A24DFEE5E427E7",
        "expected_combined_changed_literal_count": 58,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B084_S1256",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B084_S1256.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B084_S1258.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B084",
    "queue_row_count": 197,
    "queue_visible_count": 200,
    "queue_first": "9:1241:0",
    "queue_last": "9:1437:0",
    "expected_middle_prefilled_coordinate_sha256":
    "E1413E29487CBE27136C4AC9F9CBABF3CA9C4151C6C3FF77335217B1D5159DA3",
    "expected_middle_prefill_context_sha256":
    "688295E783F98D5E40DFD6E652B3AAFCF5CF716B04B8CAA5D6500B30598CCE09",
    "expected_middle_boundary_sha256":
    "8D25C4F95C2DEC4F8106DA4368C080009DF3A39BB86DA5381A420F8C30850BF7",
    "expected_zero_middle_slice_sha256":
    "0194601A5F246DCAF60971CBE1C8AA8241E9DBBC9075CB7223842010B6A6AA5D",
})


def audited_queue_evidence(
    prepared: Any,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[Any, ...],
    tuple[tuple[int, int], ...],
]:
    result = _ORIGINAL_QUEUE_EVIDENCE(prepared)
    visible = result[0]
    prefill_rows = {
        str(row["coordinate"]): row
        for row in COMMON.read_jsonl(COMMON.PREFILL)
    }
    middle = visible[67:134]
    if (
        len(middle) != 67
        or middle[0] != "9:1307:0"
        or middle[-1] != "9:1373:0"
        or len(set(middle)) != 67
        or any(coordinate not in prefill_rows for coordinate in middle)
    ):
        raise RuntimeError(
            "segment 1256 middle zero-residual slice drifted"
        )
    middle_context = tuple(
        (
            coordinate,
            str(prefill_rows[coordinate]["translation"]),
            str(prefill_rows[coordinate]["source_record_raw_sha256"]),
            str(prefill_rows[coordinate]["current_ko_utf16le_sha256"]),
            str(prefill_rows[coordinate]["semantic_review"]),
            str(prefill_rows[coordinate]["runtime_review"]),
            str(prefill_rows[coordinate]["layout_review"]),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "base_coordinate"
                ]
            ),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "translation_utf16le_sha256"
                ]
            ),
            bool(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "runtime_promotion_authorized"
                ]
            ),
        )
        for coordinate in middle
    )
    records_by_label = COMMON.CORE.context_records(prepared)
    middle_record_keys = tuple(
        dict.fromkeys(
            COMMON.coordinate_key(coordinate)[:2]
            for coordinate in middle
        )
    )
    middle_boundary = tuple(
        (
            label,
            key,
            COMMON.sha256_bytes(records_by_label[label][key].data),
            COMMON.literal_texts(records_by_label[label], key),
            tuple(
                value.hex().upper()
                for value in COMMON.gap_bytes(records_by_label[label][key])
            ),
        )
        for label in ("jp", "current", "en", "sc", "tc")
        for key in middle_record_keys
    )
    zero_middle_slice = (
        67,
        134,
        middle[0],
        middle[-1],
        len(middle),
        0,
    )
    for label, value, expected in (
        (
            "middle prefilled coordinate",
            middle,
            CONFIG["expected_middle_prefilled_coordinate_sha256"],
        ),
        (
            "middle prefill context",
            middle_context,
            CONFIG["expected_middle_prefill_context_sha256"],
        ),
        (
            "middle boundary",
            middle_boundary,
            CONFIG["expected_middle_boundary_sha256"],
        ),
        (
            "zero middle slice",
            zero_middle_slice,
            CONFIG["expected_zero_middle_slice_sha256"],
        ),
    ):
        COMMON.CORE.guarded_digest(label, value, expected)
    return result


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 9)
    setattr(COMMON.BASE, "queue_evidence", audited_queue_evidence)


COMMON.queue_evidence = audited_queue_evidence
COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
