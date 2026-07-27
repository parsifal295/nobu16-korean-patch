#!/usr/bin/env python3
"""Build source-redacted PK B101 segment 1307 residual decisions."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
_ORIGINAL_RUN = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_BASE_ASSEMBLY = COMMON.BASE.base_and_assembly_evidence
_ORIGINAL_BASE_READ_JSONL = COMMON.BASE.read_jsonl

TARGET_RECORD_IDS = tuple(range(46, 61))
EXACT_BASE_DONOR = {
    record_id: (12, record_id)
    for record_id in TARGET_RECORD_IDS
}
REAL_PREFILL_COMPANION_COORDINATES = (
    "12:46:2",
    "12:47:0",
    "12:47:3",
    "12:47:4",
    "12:48:2",
    "12:49:0",
    "12:49:3",
    "12:49:4",
    "12:50:1",
    "12:51:0",
    "12:51:2",
    "12:52:0",
    "12:52:2",
    "12:53:0",
    "12:53:2",
    "12:53:3",
    "12:54:1",
    "12:55:0",
    "12:55:3",
    "12:55:4",
    "12:56:2",
    "12:57:0",
    "12:57:3",
    "12:58:4",
    "12:59:0",
    "12:59:3",
    "12:59:4",
    "12:60:0",
    "12:60:2",
)
OUTSIDE_SLICE_BASE_COMPANION = {
    "12:60:3": "12:60:3",
}
PREFILL_COMPANION_COORDINATES = (
    REAL_PREFILL_COMPANION_COORDINATES
    + tuple(OUTSIDE_SLICE_BASE_COMPANION)
)
PREFILL_COMPANION_DONOR = {
    "12:46:2": "12:46:2",
    "12:47:0": "12:45:0",
    "12:47:3": "12:45:3",
    "12:47:4": "12:47:4",
    "12:48:2": "12:48:2",
    "12:49:0": "12:45:0",
    "12:49:3": "12:49:3",
    "12:49:4": "12:49:4",
    "12:50:1": "12:50:1",
    "12:51:0": "12:51:0",
    "12:51:2": "12:51:2",
    "12:52:0": "12:52:0",
    "12:52:2": "12:52:2",
    "12:53:0": "12:53:0",
    "12:53:2": "12:53:2",
    "12:53:3": "12:53:3",
    "12:54:1": "12:54:1",
    "12:55:0": "12:45:0",
    "12:55:3": "12:45:3",
    "12:55:4": "12:55:4",
    "12:56:2": "12:56:2",
    "12:57:0": "12:45:0",
    "12:57:3": "12:57:3",
    "12:58:4": "12:58:4",
    "12:59:0": "12:59:0",
    "12:59:3": "12:59:3",
    "12:59:4": "12:59:4",
    "12:60:0": "12:60:0",
    "12:60:2": "12:60:2",
    **OUTSIDE_SLICE_BASE_COMPANION,
}
EXPECTED_ARITY = {
    46: 4,
    47: 6,
    48: 4,
    49: 6,
    50: 3,
    51: 4,
    52: 4,
    53: 4,
    54: 3,
    55: 6,
    56: 4,
    57: 6,
    58: 6,
    59: 5,
    60: 4,
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1307,
    queue_start=0,
    queue_stop=67,
    slice_first="12:46:0",
    slice_last="12:60:1",
    target_coordinates=(
        "12:46:0",
        "12:46:1",
        "12:46:3",
        "12:47:1",
        "12:47:2",
        "12:47:5",
        "12:48:0",
        "12:48:1",
        "12:48:3",
        "12:49:1",
        "12:49:2",
        "12:49:5",
        "12:50:0",
        "12:50:2",
        "12:51:1",
        "12:51:3",
        "12:52:1",
        "12:52:3",
        "12:53:1",
        "12:54:0",
        "12:54:2",
        "12:55:1",
        "12:55:2",
        "12:55:5",
        "12:56:0",
        "12:56:1",
        "12:56:3",
        "12:57:1",
        "12:57:2",
        "12:57:4",
        "12:57:5",
        "12:58:0",
        "12:58:1",
        "12:58:2",
        "12:58:3",
        "12:58:5",
        "12:59:1",
        "12:59:2",
        "12:60:1",
    ),
    translations={
        "12:46:0": "마침내 ",
        "12:46:1": "오우",
        "12:46:3": "!",
        "12:47:1": "!\n",
        "12:47:2": "반도",
        "12:47:5": "!",
        "12:48:0": "마침내 ",
        "12:48:1": "간토",
        "12:48:3": "!",
        "12:49:1": "!\n",
        "12:49:2": "호쿠리쿠",
        "12:49:5": "!",
        "12:50:0": "호쿠리쿠",
        "12:50:2": "!",
        "12:51:1": "고신",
        "12:51:3": "!",
        "12:52:1": "고신",
        "12:52:3": "!",
        "12:53:1": "도카이",
        "12:54:0": "도카이",
        "12:54:2": "!",
        "12:55:1": "!\n",
        "12:55:2": "긴키",
        "12:55:5": "!",
        "12:56:0": "마침내 ",
        "12:56:1": "기나이",
        "12:56:3": "!",
        "12:57:1": "!\n",
        "12:57:2": "주고쿠",
        "12:57:4": ".\n전례 없는 쾌거입니다",
        "12:57:5": "!",
        "12:58:0": "마침내 ",
        "12:58:1": "산인",
        "12:58:2": "·",
        "12:58:3": "산요",
        "12:58:5": "!",
        "12:59:1": "!\n",
        "12:59:2": "시코쿠",
        "12:60:1": "시코쿠",
    },
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(),
    semantic_base_context={
        record_id: tuple(
            f"12:{record_id}:{literal_id}"
            for literal_id in range(EXPECTED_ARITY[record_id])
        )
        for record_id in TARGET_RECORD_IDS
    },
    expected_base_raw_matches={
        record_id: ()
        for record_id in TARGET_RECORD_IDS
    },
    expected_base_literal_matches={
        record_id: ((12, record_id),)
        for record_id in TARGET_RECORD_IDS
    },
    expected_base_masked_matches={
        record_id: ((12, record_id),)
        for record_id in TARGET_RECORD_IDS
    },
    expected_controls_by_record={
        46: ((586,), ()),
        47: ((376, 538, 520), ()),
        48: ((586,), ()),
        49: ((376, 538, 520), ()),
        50: ((586,), ()),
        51: ((538,), ()),
        52: ((586,), ()),
        53: ((538,), ()),
        54: ((586,), ()),
        55: ((376, 538, 610), ()),
        56: ((586,), ()),
        57: ((376, 538, 520), ()),
        58: ((586,), ()),
        59: ((376, 538), ()),
        60: ((586,), ()),
    },
    source_call_roots=(376, 520, 538, 586, 610),
    boundary_record_keys=tuple(
        (12, record_id) for record_id in range(45, 62)
    ),
    speaker_style=(
        (46, "lord_regional_peace_acknowledgment"),
        (47, "formal_regional_congratulation"),
        (48, "lord_regional_peace_acknowledgment"),
        (49, "formal_regional_congratulation"),
        (50, "lord_regional_peace_acknowledgment"),
        (51, "formal_regional_congratulation"),
        (52, "lord_regional_unification_acknowledgment"),
        (53, "formal_regional_congratulation"),
        (54, "lord_regional_peace_acknowledgment"),
        (55, "formal_regional_congratulation"),
        (56, "lord_regional_peace_acknowledgment"),
        (57, "formal_regional_congratulation"),
        (58, "lord_regional_peace_acknowledgment"),
        (59, "formal_regional_congratulation"),
        (60, "lord_regional_peace_acknowledgment"),
    ),
    terminology_policy=(
        ("northeastern provinces", "오우"),
        ("eastern provinces", "반도"),
        ("eastern region", "간토"),
        ("northern coastal region", "호쿠리쿠"),
        ("central mountain region", "고신"),
        ("eastern coastal region", "도카이"),
        ("capital region", "긴키"),
        ("inner capital provinces", "기나이"),
        ("western mainland region", "주고쿠"),
        ("northern western-mainland route", "산인"),
        ("southern western-mainland route", "산요"),
        ("western island region", "시코쿠"),
        ("unprecedented achievement", "전례 없는 쾌거"),
        ("project ellipsis", "…"),
    ),
    basis=(
        "pristine PK JP is authoritative and all available EN, SC and TC "
        "same-record context was manually reviewed; every complete source "
        "record has a literal-exact and call-operand-masked completed Base "
        "record at the same coordinate, so its Korean is reused solely as "
        "semantic content while PK call operands and bytecode remain "
        "authoritative; Base runtime and VM state are never inherited; "
        "twenty-eight approved static prefills and one completed-Base "
        "semantic companion beyond the slice boundary complete all fifteen "
        "records without creating an extra decision; historical region and "
        "route names follow established completed Base terminology; all "
        "direct calls, color gaps, outer spaces, punctuation, line counts, "
        "literal arity and terminators are preserved; all pins, two-run "
        "reproduction, tamper rejection, call graphs, reverse overlays, "
        "outside-scope identity and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=19,
    pins={
        "expected_queue_universe_sha256":
        "3C022919301136691B49E8999449960DDCC09A8E816D6BA0E3AA912E603BD7AA",
        "expected_queue_slice_sha256":
        "EC41D640CFE2F9FAF7F09A9D1115740DCAD86A29FD042F7967148FBF6DD6EB51",
        "expected_prefilled_coordinate_sha256":
        "202216E7BCBFA4E9300F9B4FC2A1DD87494C032B6C43AAB4FDC453FABBF886BA",
        "expected_prefill_slice_context_sha256":
        "F8496652612600D2A91BBF9362BC6D336E2F509B84D9F9E3CF20B5884757D0B9",
        "expected_target_coordinate_sha256":
        "5A4809866551134CAD10DC45C2CDDDD1451AD1BD7E5117C6A67898EC420F98D9",
        "expected_source_target_sha256":
        "A4DE5A3C62007153C36F972346EE2398BB3B4F129DE85AC68CFB8432B298A210",
        "expected_current_target_sha256":
        "FA7CDF08ED81D79A2283D5D9AC97AE9E650DD46F0069B10807F4294D9A9DBD53",
        "expected_context_corpus_sha256":
        "7E19C89B117A62F83E1014F716BF21A032C6EE7C6428DE88714627BE51A00F07",
        "expected_gap_contract_sha256":
        "6D3222EE72AE5E1D2519D032B91EF5587001C1100D991BF6E218BB22610CA2B9",
        "expected_boundary_sha256":
        "F8D7128609785BAA3C152CF48F115F43F3302FB8ECECD213C906E456C8AD70C9",
        "expected_runtime_control_sha256":
        "156A85D470DF50208E66A56A3CF8DCB32D386C0359D3E8A5611706C09900CE88",
        "expected_base_search_sha256":
        "0600F3699C0E4FE0606C09B738D70F4815806F68630B448286D4F0763B68F876",
        "expected_complete_assembly_sha256":
        "9D2BB2537351373DA11C9870B871DDD2ECE7EB60F242E916857560DF502C9DA8",
        "expected_call_graph_sha256":
        "D6D7A10EE5FBA33580F67A65E831BE88C62B2DDBDEF3F9E08C192B64FE6E30A2",
        "expected_speaker_style_sha256":
        "9811CA1B4F4B0AA27AA6192E2E4357B98623B36999B16D93F1A8754E6728BDE3",
        "expected_terminology_policy_sha256":
        "DE330E15E231DB0CFD59C5C5DA9D9844D461F756A1A331753B3C49BD0285556F",
        "expected_translation_policy_sha256":
        "79B65FFC4A2BE3525A45A7F8D892A54B05E9F06A07D6926A1F8D432F0E9A0866",
        "expected_candidate_sha256":
        "4240D04C6D01E201861DA2DF8575E16EEBE91E2D303F3506D4571EBCD6E66A82",
        "expected_combined_slice_candidate_sha256":
        "EB35A3E50FB7642FA1F125D1D263DEE92A2BF150C8B196CDECC8C2828397CD6F",
        "expected_combined_changed_literal_count": 31,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B101_S1307",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B101_S1307.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B100_S1306.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B101_S1308.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B101",
    "queue_row_count": 117,
    "queue_visible_count": 200,
    "queue_first": "12:46:0",
    "queue_last": "13:98:1",
})


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    """Guard source-only calls that current Korean already flattened."""

    values = COMMON.BASE.CORE.context_evidence(
        prepared, records_by_label
    )
    for label, value, expected in (
        (
            "source target",
            values["source_target"],
            CONFIG["expected_source_target_sha256"],
        ),
        (
            "current target",
            values["current_target"],
            CONFIG["expected_current_target_sha256"],
        ),
        (
            "multilingual context",
            values["corpus"],
            CONFIG["expected_context_corpus_sha256"],
        ),
        (
            "gap contract",
            values["gaps"],
            CONFIG["expected_gap_contract_sha256"],
        ),
        (
            "boundary",
            values["boundary"],
            CONFIG["expected_boundary_sha256"],
        ),
        (
            "runtime control",
            values["controls"],
            CONFIG["expected_runtime_control_sha256"],
        ),
    ):
        COMMON.BASE.CORE.guarded_digest(label, value, expected)

    expected_controls = tuple(
        (
            label,
            record_id,
            (
                CONFIG["expected_controls_by_record"][record_id]
                if label == "jp"
                else ((), ())
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    flattened_gaps_are_exact = all(
        source != current
        and tuple(
            (
                ""
                if gap.startswith("0143") and len(gap) == 12
                else gap
            )
            for gap in source
        )
        == current
        for _, source, current in values["gaps"]
    )
    if (
        values["controls"] != expected_controls
        or not flattened_gaps_are_exact
        or any(
            ("pk_msggame", *COMMON.BASE.coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in CONFIG["target_coordinates"]
        )
    ):
        raise RuntimeError("segment 1307 runtime layout drifted")


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Preserve static prefills and one semantic boundary companion."""

    base_rows = {
        str(row["coordinate"]): row
        for row in _ORIGINAL_BASE_READ_JSONL(COMMON.BASE_PROMOTED)
        if "translation" in row
    }

    def compatible_read_jsonl(path: Path) -> list[dict[str, Any]]:
        rows = _ORIGINAL_BASE_READ_JSONL(path)
        if path != COMMON.PREFILL:
            return rows
        compatible: list[dict[str, Any]] = []
        for row in rows:
            copied = dict(row)
            coordinate = str(copied.get("coordinate", ""))
            if coordinate in REAL_PREFILL_COMPANION_COORDINATES:
                if copied.get("runtime_review") != "not_required":
                    raise RuntimeError(
                        "segment 1307 static prefill review drifted"
                    )
                copied["runtime_review"] = "pending"
            compatible.append(copied)
        for coordinate, donor_coordinate in (
            OUTSIDE_SLICE_BASE_COMPANION.items()
        ):
            donor = base_rows.get(donor_coordinate)
            if (
                donor is None
                or donor.get("semantic_review") != "approved"
                or donor.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    "segment 1307 outside-slice Base companion drifted"
                )
            compatible.append({
                "coordinate": coordinate,
                "translation": str(donor["translation"]),
                "semantic_review": "approved",
                "runtime_review": "pending",
                "base_exact_reuse_prefill": {
                    "base_coordinate": donor_coordinate,
                    "runtime_promotion_authorized": False,
                },
            })
        return compatible

    original_read_jsonl = COMMON.BASE.read_jsonl
    COMMON.BASE.read_jsonl = compatible_read_jsonl
    try:
        base, assembly = _ORIGINAL_BASE_ASSEMBLY(
            prepared, records_by_label
        )
    finally:
        COMMON.BASE.read_jsonl = original_read_jsonl

    adjusted: list[tuple[Any, ...]] = []
    for evidence in assembly:
        record_id = int(evidence[0])
        owners = list(evidence[1])
        for literal_id, owner in enumerate(owners):
            coordinate = f"12:{record_id}:{literal_id}"
            if coordinate in REAL_PREFILL_COMPANION_COORDINATES:
                if owner != "base_exact_prefill_runtime_pending":
                    raise RuntimeError(
                        "segment 1307 static prefill ownership drifted"
                    )
                owners[literal_id] = (
                    "base_exact_prefill_runtime_not_required"
                )
            elif coordinate in OUTSIDE_SLICE_BASE_COMPANION:
                if owner != "base_exact_prefill_runtime_pending":
                    raise RuntimeError(
                        "segment 1307 outside companion ownership drifted"
                    )
                owners[literal_id] = (
                    "completed_base_semantic_companion_outside_slice"
                )
        adjusted.append((evidence[0], tuple(owners), *evidence[2:]))
    return base, tuple(adjusted)


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 12)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)
    setattr(COMMON.BASE, "CURRENT_CALL_ROOTS", ())
    setattr(
        COMMON.BASE.CORE,
        "assert_context_contracts",
        assert_context_contracts,
    )
    setattr(
        COMMON.BASE,
        "base_and_assembly_evidence",
        base_and_assembly_evidence,
    )


COMMON.install_globals = install_globals


def run(config: dict[str, Any]) -> int:
    """Report the independently guarded flattened-current call count."""

    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        status = _ORIGINAL_RUN(config)
    lines = captured.getvalue().splitlines()
    if status != 0 or not lines:
        print(captured.getvalue(), end="")
        return status
    for line in lines[:-1]:
        print(line)
    payload = json.loads(lines[-1])
    payload["current_call_root_count"] = 0
    payload["source_calls_flattened_in_current_record_count"] = len(
        TARGET_RECORD_IDS
    )
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return status


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
