#!/usr/bin/env python3
"""Build source-redacted PK B082 segment 1250 residual decisions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_QUEUE_EVIDENCE = COMMON.queue_evidence

TARGET_RECORD_IDS = (859, 860, 892, 894, 905, 906)
CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1250,
    queue_start=0,
    queue_stop=67,
    slice_first="9:858:0",
    slice_last="9:915:0",
    target_coordinates=(
        "9:859:0",
        "9:859:1",
        "9:859:2",
        "9:860:0",
        "9:860:1",
        "9:860:2",
        "9:892:0",
        "9:894:0",
        "9:905:0",
        "9:906:0",
    ),
    translations={
        "9:859:0": "라고 불리는",
        "9:859:1": "을(를),\n이",
        "9:859:2": "이(가) 사로잡았노라!",
        "9:860:0": "라고 불리는",
        "9:860:1": "을(를),\n이",
        "9:860:2": "이(가) 사로잡았어!",
        "9:892:0": "장하다!　",
        "9:894:0": "……",
        "9:905:0": "대단합니다―",
        "9:906:0": "제법이군!\n",
    },
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={
        859: 3,
        860: 3,
        892: 2,
        894: 2,
        905: 2,
        906: 2,
    },
    prefill_companion_coordinates=(
        "9:892:1",
        "9:894:1",
        "9:905:1",
        "9:906:1",
    ),
    prefill_companion_donor={
        "9:892:1": "9:834:1",
        "9:894:1": "9:836:1",
        "9:905:1": "9:847:1",
        "9:906:1": "9:848:1",
    },
    hidden_current_companion_coordinates=(),
    semantic_base_context={
        859: ("9:795:0", "9:791:0", "7:192:1"),
        860: ("9:795:0", "9:791:0", "9:799:0"),
        892: ("9:834:0", "9:834:1"),
        894: ("9:836:0", "9:836:1"),
        905: ("9:847:0", "9:847:1"),
        906: ("9:848:0", "9:848:1"),
    },
    expected_base_raw_matches={
        859: (),
        860: (),
        892: ((9, 834),),
        894: ((9, 836),),
        905: ((9, 847),),
        906: ((9, 848),),
    },
    expected_base_literal_matches={
        859: (),
        860: (),
        892: ((9, 834),),
        894: ((9, 836),),
        905: ((9, 847),),
        906: ((9, 848),),
    },
    expected_base_masked_matches={
        859: (),
        860: (),
        892: ((9, 834),),
        894: ((9, 836),),
        905: ((9, 847),),
        906: ((9, 848),),
    },
    expected_controls_by_record={
        859: ((), ("02484E", "024833", "024635")),
        860: ((), ("02484E", "024833", "024635")),
        892: ((29,), ()),
        894: ((), ("024833",)),
        905: ((), ("024833",)),
        906: ((1,), ()),
    },
    source_call_roots=(1, 29),
    boundary_record_keys=tuple(
        (9, record_id) for record_id in range(857, 1050)
    ),
    speaker_style=(
        (859, "boastful_male_capture_declaration"),
        (860, "confident_female_capture_declaration"),
        (892, "senior_warrior_enemy_escape_reaction"),
        (894, "shocked_enemy_defeat_reaction"),
        (905, "polite_enemy_overwhelm_praise"),
        (906, "competitive_warrior_praise"),
    ),
    terminology_policy=(
        ("capture action", "사로잡다"),
        ("captured officer", "포박 대상"),
        ("dynamic alias relation", "라고 불리는"),
        ("male victory register", "사로잡았노라"),
        ("female victory register", "사로잡았어"),
        ("overwhelm", "압도"),
        ("dynamic particles", "을(를)·이(가)"),
    ),
    basis=(
        "pristine PK JP is authoritative and complete EN, SC and TC context "
        "was manually reviewed; completed Base capture, escape, defeat and "
        "overwhelm records provide semantic, terminology and register "
        "references only, with no Base runtime or VM state inherited; the two "
        "PK-only capture boasts preserve the alias, captured-officer and "
        "speaker tokens in source order, use dynamic object and subject "
        "particles, and distinguish male and female victory registers; all six "
        "complete records preserve inline tokens, calls, protected whitespace "
        "and gaps; all 133 trailing visible coordinates are exact Base prefills "
        "whose two zero-residual slices, context and multilingual boundaries "
        "are separately pinned; two-run reproduction, tamper rejection, reverse "
        "overlays, outside-scope identity and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=9,
    pins={
        "expected_queue_universe_sha256":
        "D00FEEEBA792DB30B47CF8AABEF4A6749CCCFFF26CC45F13F549D110E1874F01",
        "expected_queue_slice_sha256":
        "F4259EF9349E2EBB07D9F013B4F409E03C999BE8A65AC18B1087BF37853A09AA",
        "expected_prefilled_coordinate_sha256":
        "4919410B677422CDE4A2A14A2BD84BB038F53EE6484EB439FDCDA68FFA15131E",
        "expected_prefill_slice_context_sha256":
        "D8ACBC93FA0B42638A8E69039001C83E5834BD94665B0214C3F99ED325428552",
        "expected_target_coordinate_sha256":
        "17B3543C5CCAC86CD2B2B4F1F31B7B803AC9D7CE600A428E750F69467DCCF466",
        "expected_source_target_sha256":
        "DA772E7ACB5495EAE58540E040D759E29C9181EA2FFBC474625B36ED2A7B4D30",
        "expected_current_target_sha256":
        "614C4DE250B77C347DFA455319967400EE6F934FA65E27757EBD9ED682CC2AE7",
        "expected_context_corpus_sha256":
        "DC1F2C0D74A5F29B51F2A36437A7A80D2B33D9A4EF588C027EC33886116B57F0",
        "expected_gap_contract_sha256":
        "E00DB18997CB3483407213E8A4AE666B734979F1EB6F59357935446EC19EDD02",
        "expected_boundary_sha256":
        "CEE23390080106B61B11377982722F16C3371101A58B381CBF645DE2E5D628F9",
        "expected_runtime_control_sha256":
        "315D8F61A5F81A19B0D0F62604CFC86A0B8D704E51D4F9BD410C593976F6ACC7",
        "expected_base_search_sha256":
        "442118A2260E77C3FCE10844A9162B5FAFCF83706022A7726513D973CE8A08A0",
        "expected_complete_assembly_sha256":
        "71DAC146AA3FD7A84E8B552676591298F75F66DFC531582C40C05B715616270B",
        "expected_call_graph_sha256":
        "A12C3976F135C9413B0E2034852B26065B6D43DBCF7C62195E5508D78F3F8931",
        "expected_speaker_style_sha256":
        "1A6463C0523F4DD12D67DBD23C765E576BD5947A9CDFA16782B08E2BE9729F67",
        "expected_terminology_policy_sha256":
        "9104BB5146E59C555EB32C4E48F529AD09D9E0ABFF6E4E2ADDFC8B8A767F3CB4",
        "expected_translation_policy_sha256":
        "97CD2EDF688D213A471A9A97EEF8A85D5FB99DA11ED62D3AEA1EA8EF6A5201DA",
        "expected_candidate_sha256":
        "02E15920D79CEAC704744D199A71935896303CB0FFE287F41FB4DB3451238358",
        "expected_combined_slice_candidate_sha256":
        "66757394D5BA1DA9020D023DA092D8A06ED772EEED59354E9A054AD875CD060F",
        "expected_combined_changed_literal_count": 59,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B082_S1250",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B082_S1250.private.v1.jsonl"
    ),
    "optional_neighbors": (),
    "queue_batch_id": "pk_msggame-B082",
    "queue_row_count": 191,
    "queue_visible_count": 200,
    "queue_first": "9:858:0",
    "queue_last": "9:1048:0",
    "expected_trailing_prefilled_coordinate_sha256":
    "01F9E4344F70F46D3DF9C70043C33CC2599997EBA33956644E50A32C72AA539F",
    "expected_trailing_prefill_context_sha256":
    "7BC1D0D22ADF1C24FC7BCF1ACC18A3430039B7603846F89B6DD9E976A21E0484",
    "expected_trailing_boundary_sha256":
    "DD2B6EA6AF564A2FD572F5EEE197932B560081EE1DD61EEE731DCDA07ABEC8D2",
    "expected_zero_residual_slices_sha256":
    "0972B96F037F3EA8564C449DC658098DFC618593D7CE697E38BBA021AC843548",
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
    second = visible[67:134]
    third = visible[134:200]
    trailing = second + third
    if (
        len(second) != 67
        or second[0] != "9:916:0"
        or second[-1] != "9:982:0"
        or len(third) != 66
        or third[0] != "9:983:0"
        or third[-1] != "9:1048:0"
        or len(trailing) != 133
        or len(set(trailing)) != 133
        or any(coordinate not in prefill_rows for coordinate in trailing)
    ):
        raise RuntimeError(
            "segment 1250 trailing zero-residual slices drifted"
        )
    trailing_context = tuple(
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
        for coordinate in trailing
    )
    records_by_label = COMMON.CORE.context_records(prepared)
    trailing_record_keys = tuple(
        dict.fromkeys(
            COMMON.coordinate_key(coordinate)[:2]
            for coordinate in trailing
        )
    )
    trailing_boundary = tuple(
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
        for key in trailing_record_keys
    )
    zero_residual_slices = (
        (67, 134, second[0], second[-1], len(second), 0),
        (134, 200, third[0], third[-1], len(third), 0),
    )
    for label, value, expected in (
        (
            "trailing prefilled coordinate",
            trailing,
            CONFIG["expected_trailing_prefilled_coordinate_sha256"],
        ),
        (
            "trailing prefill context",
            trailing_context,
            CONFIG["expected_trailing_prefill_context_sha256"],
        ),
        (
            "trailing boundary",
            trailing_boundary,
            CONFIG["expected_trailing_boundary_sha256"],
        ),
        (
            "zero residual slices",
            zero_residual_slices,
            CONFIG["expected_zero_residual_slices_sha256"],
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
