#!/usr/bin/env python3
"""Build source-redacted PK B084 segment 1258 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_QUEUE_EVIDENCE = COMMON.queue_evidence

TARGET_RECORD_IDS = (1386, 1397)
CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1258,
    queue_start=134,
    queue_stop=200,
    slice_first="9:1374:0",
    slice_last="9:1437:0",
    target_coordinates=(
        "9:1386:0",
        "9:1386:1",
        "9:1397:1",
    ),
    translations={
        "9:1386:0": "어, 어이!\n",
        "9:1386:1": "이(가) 아직……!",
        "9:1397:1": "까지……",
    },
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={
        1386: 2,
        1397: 2,
    },
    prefill_companion_coordinates=("9:1397:0",),
    prefill_companion_donor={"9:1397:0": "9:1323:0"},
    hidden_current_companion_coordinates=(),
    semantic_base_context={
        1386: ("9:1312:0", "9:1312:1"),
        1397: ("9:1323:0", "9:1323:1"),
    },
    expected_base_raw_matches={
        1386: ((9, 1312),),
        1397: ((9, 1323),),
    },
    expected_base_literal_matches={
        1386: ((9, 1312),),
        1397: ((9, 1323),),
    },
    expected_base_masked_matches={
        1386: ((9, 1312),),
        1397: ((9, 1323),),
    },
    expected_controls_by_record={
        1386: ((1,), ()),
        1397: ((1,), ()),
    },
    source_call_roots=(1,),
    boundary_record_keys=tuple(
        (9, record_id)
        for record_id in (
            1311, 1312, 1313,
            1322, 1323, 1324,
            1373, 1374,
            1385, 1386, 1387,
            1396, 1397, 1398,
            1437, 1438,
        )
    ),
    speaker_style=(
        (1386, "alarmed_dynamic_flood_reaction"),
        (1397, "shocked_dynamic_collateral_reaction"),
    ),
    terminology_policy=(
        ("urgent call", "어, 어이"),
        ("dynamic subject particle", "이(가)"),
        ("lingering danger", "아직"),
        ("incredulous reaction", "어째서"),
        ("inclusive extent particle", "까지"),
        ("project ellipsis", "……"),
        ("ASCII exclamation", "!"),
    ),
    basis=(
        "pristine PK JP is authoritative and all available EN, SC and TC "
        "context was manually reviewed; the two exact completed Base records "
        "supply semantic, terminology, punctuation and speaker-register "
        "evidence only, with no Base runtime or VM state inherited; the first "
        "complete reaction preserves the dynamic subject call and uses "
        "particle-safe 이(가), while the second combines its approved prefill "
        "companion with the extent particle and project ellipsis; all calls, "
        "protected newlines, gaps and complete assemblies are guarded; all "
        "sixty-three prefills in the closing slice and all sixty-seven "
        "prefills in the zero-residual middle slice have independently pinned "
        "coordinates, contexts and multilingual boundaries; two-run "
        "reproduction, tamper rejection, mutual neighbors, reverse overlays, "
        "outside-scope identity and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=2,
    pins={
        "expected_queue_universe_sha256":
        "62ED4EA4F16E14C14AD2DF138475242E7459FA539CFD4F655BFBA311B1D2E2FB",
        "expected_queue_slice_sha256":
        "47EC368E060B435619C3187B0CD776B8BA7B54B4BE64720A96AAEC1E8EBCA09B",
        "expected_prefilled_coordinate_sha256":
        "B189B75C76BE15A5EB84676E2F21D7F62CC28413E73DCBDD9C0D65FED273940C",
        "expected_prefill_slice_context_sha256":
        "ED131D2B1B0344578FB142C99141B9FC4C7F5C9B3AE02A12D881FF41C4DD4607",
        "expected_target_coordinate_sha256":
        "C6E3FFCC6E0D9B013894F2FDFE6B98C0833A73A064F1F2E1859CD0D2A0731E4E",
        "expected_source_target_sha256":
        "1B7111C44C4B4381FB48210EEBA6BC5A2E9535C4FBC7AADE50E64A2AAA145E82",
        "expected_current_target_sha256":
        "3CB8E7DEC247203E2D9380F87249A43AAAFF71C7450044D9BC16136250EC8729",
        "expected_context_corpus_sha256":
        "9B9312B977AB0307C30CEEFD3C52B519C9937C6862B7ADC3472A889D79A5DB3B",
        "expected_gap_contract_sha256":
        "13B60ADEFEB4DEC0FE3C94F9D57F4721B6DED576AF17E8FD9EFB0A2D4AF5E1BE",
        "expected_boundary_sha256":
        "6888BCA9FC788E549B2EEF51005BEF6B8974EC73D43E91EDE356D10DF7C9C2AC",
        "expected_runtime_control_sha256":
        "767359AC484EA8E7FDCA1F83170FC84B833FA779B73515AA8E548DDB8466B08B",
        "expected_base_search_sha256":
        "0C1CAFB1F3BE2F4E2B5C6731149406E772D458A666035C9D0D8128A38CB7E48D",
        "expected_complete_assembly_sha256":
        "E69AECAD45C7AA232E4642848C89DAFD274907BBB9BA9AF0464141DFB9EB2B26",
        "expected_call_graph_sha256":
        "9F6F46D774474371A103483E9C9BFA5C47CE1819CB17620E9DBFE32BDF9CD7BD",
        "expected_speaker_style_sha256":
        "21D88726BD7F829658A5D185FB8511C548A5DF23F845AD4AA65CCFD186B40077",
        "expected_terminology_policy_sha256":
        "4967CF02B92C73B3B01776D63792EB3CB26221231DAF77CF9B458EA82196FCFD",
        "expected_translation_policy_sha256":
        "845F9D52A870AF8D18C742A52A08CD5CD58FFC20ACE9F61E9EAA90782A03AB3B",
        "expected_candidate_sha256":
        "B47F9636B016D60A866C28129D6FD6158DB7992C577432FE4BFF8EE458AECA88",
        "expected_combined_slice_candidate_sha256":
        "41AE34FA21DB44FE9EDEA4AB13C3F1870B43E2C6427C2754755299E144BACD1B",
        "expected_combined_changed_literal_count": 55,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B084_S1258",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B084_S1258.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B084_S1256.private.v1.jsonl",
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
            "segment 1258 middle zero-residual slice drifted"
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
