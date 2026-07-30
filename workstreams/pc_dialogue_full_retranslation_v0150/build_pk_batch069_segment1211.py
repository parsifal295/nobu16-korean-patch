#!/usr/bin/env python3
"""Build source-redacted PK B069 segment 1211 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
PARENT_PATH = WORKSTREAM / "build_pk_batch068_segment1210.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B069_S1211.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B069_S1212.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B069_S1213.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1211
QUEUE_BATCH_ID = "pk_msggame-B069"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "7:2750:0",
    "7:2750:1",
    "7:2752:0",
    "7:2753:0",
    "7:2754:0",
    "7:2755:0",
    "7:2756:0",
)
TRANSLATIONS = {
    "7:2750:0": "훌륭하구나,",
    "7:2750:1": "!\n",
    "7:2752:0": "역시,",
    "7:2753:0": "역시,",
    "7:2754:0": "역시 대단하구나,",
    "7:2755:0": "오오,",
    "7:2756:0": "그에 비해,",
}
TARGET_RECORD_IDS = (2750, 2752, 2753, 2754, 2755, 2756)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    2750: 3,
    2752: 2,
    2753: 3,
    2754: 2,
    2755: 2,
    2756: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "7:2750:2",
    "7:2752:1",
    "7:2753:1",
    "7:2753:2",
    "7:2754:1",
    "7:2755:1",
    "7:2756:1",
)
PREFILL_COMPANION_DONOR = {
    "7:2750:2": "7:2684:2",
    "7:2752:1": "7:2686:1",
    "7:2753:1": "7:2687:1",
    "7:2753:2": "7:2687:2",
    "7:2754:1": "7:2688:1",
    "7:2755:1": "7:2689:1",
    "7:2756:1": "7:2690:1",
}
EXACT_BASE_DONOR = {
    2750: (7, 2684),
    2752: (7, 2686),
    2753: (7, 2687),
    2754: (7, 2688),
    2755: (7, 2689),
    2756: (7, 2690),
}
SEMANTIC_BASE_CONTEXT: dict[int, tuple[str, ...]] = {}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: (base_coordinate,)
    for record_id, base_coordinate in EXACT_BASE_DONOR.items()
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (7, record_id)
    for record_id in (
        2683, 2684, 2685, 2686, 2687, 2688, 2689, 2690, 2691,
        2733, 2734, 2749, 2750, 2751, 2752, 2753, 2754,
        2755, 2756, 2757, 2785, 2786, 2857, 2858,
    )
)
SOURCE_CALL_ROOTS = (1,)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    2750: ((1,), ("024733",)),
    2752: ((), ("024733",)),
    2753: ((1,), ("024733",)),
    2754: ((), ("024733",)),
    2755: ((), ("024733",)),
    2756: ((1,), ()),
}
SPEAKER_STYLE = (
    (2750, "competitive_peer_praise"),
    (2752, "retainer_house_honor_praise"),
    (2753, "reassured_ally_praise"),
    (2754, "joyful_personal_praise"),
    (2755, "house_prosperity_praise"),
    (2756, "comparative_self_assessment"),
)
TERMINOLOGY_POLICY = (
    ("splendid", "훌륭하구나"),
    ("as expected", "역시"),
    ("house", "우리 가문"),
    ("battle merit", "전공"),
    ("highest merit", "전공 제일"),
    ("in comparison", "그에 비해"),
    ("ASCII exclamation fragment", "!"),
)

EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PRISTINE_PK_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)
EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "354BFB11CF3F62EFFFDDDA9AF4C66A8876A027D6DF273DBF6496ACEC50DB6C53"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "D955F9BC819D4D9FB6AFCDF672AB280833E3BE3B88583F3CD5BA8A63B03D932F"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "061D3E4189368080D9D6F075B1509E71786A4CCA9BCC30F9CDDF6B9F4C3D2F66"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "66F05CE82F970F00ADA1A7194EE23903ED550509F45D9059238CBC0D73107F22"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "0E6ED40BDC66DCAF8875087B0B9EBA856BEC6BF2DC2137E816FE2EE726948EA9"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "3AD9A1C9588CEDFF2847B054753CA1DCEE8C2F5B675C8592428F539C10912669"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "C815B5D8FB77C2E9B48989CD3F2C3AA76795D9FDFDFD12CD6FB49BD1E7CDB4B6"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "AF8A1FE16C106E5C16663F0AFA81C3287B33C4F28EE72F120EBA2E455F2FB1F3"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "27171A158CA14F3ED6F91C73606B29F27622AEA91E59FDA00E47582BEFF0303D"
)
EXPECTED_BOUNDARY_SHA256 = (
    "D11CE2A83ED45439EAD02FD9F2F9830FC10582C5D4560D1B63424C5783297DC6"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "8CB1D329DFD21B8A870217F8AC1E46788263C7EEFF4066FCB25333B382ABCA24"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "CAF9BC2FC45B59A9204A2C725F3AD0AF2EEA5F6381955F457D6E9CD3A2C618E3"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "DA0153DD2D223EB807C0D6BC4390F794C55A000A7746790112675E8DA5B6C88A"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "9F6F46D774474371A103483E9C9BFA5C47CE1819CB17620E9DBFE32BDF9CD7BD"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "2B72CE733E18B6F98BC96A79EA6F7D8002700732F66E5B3FAFC32678F8CDBDB7"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "1C67B33D62D5916B27F68EB0404F16863AEE7498ACCD81034FE4EFCE7091A1E2"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "33D3FD254D9A62223F882342A5DAE465D1DC986E417454183098AB1720270F77"
)
EXPECTED_CANDIDATE_SHA256 = (
    "522D77B0B3CB109E735EB38668D423D31F33D27E9E930C4FBB47286EEDB56B04"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "7349F26AB806D5AAA02E61E224B8DD54BD2BEEA11984A9B91B7ADDC77FB664B3"
)
EXPECTED_CHANGED_LITERAL_COUNT = 6
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 58

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese source authoritative; complete PC English, "
    "Simplified Chinese and Traditional Chinese records are empty except "
    "where queue context says otherwise and were manually reviewed; all "
    "six complete PK source records have one raw, literal and call-"
    "operand-exact completed Base donor, whose final Korean was reused "
    "only after manual semantic, terminology and speaker-register review; "
    "the seven residual fragments and seven approved same-record "
    "prefills reproduce every complete donor translation; praise, house, "
    "battle-merit and comparison terminology, ASCII punctuation, officer "
    "and call operands, newlines, protected outer whitespace, source and "
    "current gaps and inline tokens are guarded; all sixty prefills in "
    "the sixty-seven-row first slice are validated and the combined slice "
    "is rebuilt in both orders and reversed byte-exactly; two-run "
    "reproduction, tamper rejection, outside-scope identity and Steam "
    "read-only state are guarded; completed Base runtime and VM state are "
    "never inherited and all residual fragments remain PK runtime pending"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1211_parent",
        PARENT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {PARENT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PARENT = load_parent()
ENGINE = PARENT.ENGINE
CORE = PARENT.CORE
sha256_bytes = PARENT.sha256_bytes
coordinate_key = PARENT.coordinate_key
literal_texts = PARENT.literal_texts
gap_bytes = PARENT.gap_bytes
read_jsonl = PARENT.read_jsonl


def queue_rows(prepared: Any) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]


def queue_evidence(
    prepared: Any,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[Any, ...],
    tuple[tuple[int, int], ...],
]:
    rows = queue_rows(prepared)
    visible = tuple(
        str(target["coordinate"])
        for row in rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(rows) != 125
        or len(visible) != 200
        or visible[0] != "7:2734:0"
        or visible[-1] != "7:2858:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B069 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "7:2734:0"
        or queue_slice[-1] != "7:2785:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    residual = tuple(
        coordinate for coordinate in queue_slice if coordinate not in prefill_rows
    )
    if len(prefilled) != 60 or residual != TARGET_COORDINATES:
        raise RuntimeError(f"segment {SEGMENT} prefill slice drifted")
    prefill_context = tuple(
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
        for coordinate in prefilled
    )
    record_keys = tuple(
        tuple(int(value) for value in str(row["record_coordinate"]).split(":"))
        for row in rows
    )
    if len(record_keys) != len(set(record_keys)):
        raise RuntimeError(f"segment {SEGMENT} duplicate queue records")
    return visible, queue_slice, prefilled, prefill_context, record_keys


def build_combined_slice_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[str, int]:
    _, queue_slice, prefilled, _, _ = queue_evidence(prepared)
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    replacements = {
        coordinate_key(coordinate): (
            TRANSLATIONS[coordinate]
            if coordinate in TRANSLATIONS
            else str(prefill_rows[coordinate]["translation"])
        )
        for coordinate in queue_slice
    }
    current = records_by_label["current"]
    reverse = {
        key: literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    current_blob = prepared.resources["pk_msggame"].current_blob
    candidate = ENGINE.rebuild_packed_with_literals(current_blob, replacements)
    reverse_order = ENGINE.rebuild_packed_with_literals(
        current_blob,
        dict(reversed(tuple(replacements.items()))),
    )
    if (
        candidate != reverse_order
        or ENGINE.rebuild_packed_with_literals(candidate, reverse)
        != current_blob
    ):
        raise RuntimeError(f"segment {SEGMENT} combined overlay drifted")
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    touched_records = {key[:2] for key in replacements}
    if (
        len(replacements) != 67
        or len(prefilled) != 60
        or any(
            candidate_records[key].data != record.data
            for key, record in current.items()
            if key not in touched_records
        )
        or any(
            gap_bytes(candidate_records[key]) != gap_bytes(current[key])
            for key in touched_records
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} combined scope drifted")
    changed = sum(
        translation != literal_texts(current, key[:2])[key[2]]
        for key, translation in replacements.items()
    )
    candidate_sha256 = sha256_bytes(candidate)
    if (
        EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 != "TO_PIN"
        and candidate_sha256 != EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} combined candidate drifted: "
            f"{candidate_sha256}"
        )
    if (
        EXPECTED_COMBINED_CHANGED_LITERAL_COUNT >= 0
        and changed != EXPECTED_COMBINED_CHANGED_LITERAL_COUNT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} combined changed count drifted: {changed}"
        )
    if EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS["combined slice candidate"] = candidate_sha256
        DISCOVERED_PINS["combined slice changed count"] = str(changed)
    return candidate_sha256, changed


def patch_parent_globals() -> None:
    values = {
        "SCRIPT": SCRIPT, "OUTPUT": OUTPUT, "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
        "OPTIONAL_NEIGHBORS": OPTIONAL_NEIGHBORS, "STEAM_PK": STEAM_PK,
        "SEGMENT": SEGMENT, "QUEUE_BATCH_ID": QUEUE_BATCH_ID,
        "QUEUE_START": QUEUE_START, "QUEUE_STOP": QUEUE_STOP,
        "BLOCK_ID": BLOCK_ID, "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "STATIC_RECORD_IDS": STATIC_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "PREFILL_COMPANION_COORDINATES": PREFILL_COMPANION_COORDINATES,
        "PREFILL_COMPANION_DONOR": PREFILL_COMPANION_DONOR,
        "EXACT_BASE_DONOR": EXACT_BASE_DONOR,
        "SEMANTIC_BASE_CONTEXT": SEMANTIC_BASE_CONTEXT,
        "EXPECTED_BASE_RAW_MATCHES": EXPECTED_BASE_RAW_MATCHES,
        "EXPECTED_BASE_LITERAL_MATCHES": EXPECTED_BASE_LITERAL_MATCHES,
        "EXPECTED_BASE_MASKED_MATCHES": EXPECTED_BASE_MASKED_MATCHES,
        "BOUNDARY_RECORD_KEYS": BOUNDARY_RECORD_KEYS,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
        "EXPECTED_CONTROLS_BY_RECORD": EXPECTED_CONTROLS_BY_RECORD,
        "SPEAKER_STYLE": SPEAKER_STYLE,
        "TERMINOLOGY_POLICY": TERMINOLOGY_POLICY,
        "EXPECTED_STEAM_PK_SHA256": EXPECTED_STEAM_PK_SHA256,
        "EXPECTED_PRISTINE_PK_SHA256": EXPECTED_PRISTINE_PK_SHA256,
        "EXPECTED_PREFILL_SHA256": EXPECTED_PREFILL_SHA256,
        "EXPECTED_BASE_PROMOTED_SHA256": EXPECTED_BASE_PROMOTED_SHA256,
        "EXPECTED_QUEUE_UNIVERSE_SHA256": EXPECTED_QUEUE_UNIVERSE_SHA256,
        "EXPECTED_QUEUE_SLICE_SHA256": EXPECTED_QUEUE_SLICE_SHA256,
        "EXPECTED_PREFILLED_COORDINATE_SHA256":
        EXPECTED_PREFILLED_COORDINATE_SHA256,
        "EXPECTED_PREFILL_SLICE_CONTEXT_SHA256":
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
        "EXPECTED_TARGET_COORDINATE_SHA256":
        EXPECTED_TARGET_COORDINATE_SHA256,
        "EXPECTED_SOURCE_TARGET_SHA256": EXPECTED_SOURCE_TARGET_SHA256,
        "EXPECTED_CURRENT_TARGET_SHA256": EXPECTED_CURRENT_TARGET_SHA256,
        "EXPECTED_CONTEXT_CORPUS_SHA256": EXPECTED_CONTEXT_CORPUS_SHA256,
        "EXPECTED_GAP_CONTRACT_SHA256": EXPECTED_GAP_CONTRACT_SHA256,
        "EXPECTED_BOUNDARY_SHA256": EXPECTED_BOUNDARY_SHA256,
        "EXPECTED_RUNTIME_CONTROL_SHA256": EXPECTED_RUNTIME_CONTROL_SHA256,
        "EXPECTED_BASE_SEARCH_SHA256": EXPECTED_BASE_SEARCH_SHA256,
        "EXPECTED_COMPLETE_ASSEMBLY_SHA256":
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
        "EXPECTED_CALL_GRAPH_SHA256": EXPECTED_CALL_GRAPH_SHA256,
        "EXPECTED_SPEAKER_STYLE_SHA256": EXPECTED_SPEAKER_STYLE_SHA256,
        "EXPECTED_TERMINOLOGY_POLICY_SHA256":
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256":
        EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_COMBINED_CHANGED_LITERAL_COUNT":
        EXPECTED_COMBINED_CHANGED_LITERAL_COUNT,
        "DISCOVERED_PINS": DISCOVERED_PINS,
        "BASIS": BASIS,
    }
    for name, value in values.items():
        setattr(PARENT, name, value)
    PARENT.queue_evidence = queue_evidence
    PARENT.build_combined_slice_candidate = build_combined_slice_candidate
    PARENT.patch_parent_globals()
    CORE.queue_evidence = queue_evidence


def build_rows() -> tuple[
    Any, list[dict[str, Any]], bytes, str, int, str, int, tuple[str, ...],
]:
    patch_parent_globals()
    return PARENT.build_rows()


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared, rows, candidate, candidate_sha256, changed,
        combined_sha256, combined_changed, optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or combined_sha256 != second[5]
        or combined_changed != second[6]
        or optional_present != second[7]
    ):
        raise RuntimeError(f"segment {SEGMENT} second-run reproduction drifted")
    if DISCOVERED_PINS:
        print(json.dumps(
            DISCOVERED_PINS, sort_keys=True, separators=(",", ":"),
        ))
        return 2
    steam_before = sha256_bytes(STEAM_PK.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: {steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared, OUTPUT, require_complete=False,
    )
    counts = Counter(str(row["scope_classification"]) for row in rows)
    if (
        len(rows) != 7
        or len(validated) != 7
        or counts != Counter({"runtime_fragment_pending": 7})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ] is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    patch_parent_globals()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(json.dumps({
        "status": "ok",
        "segment": "pk_msggame_B069_S1211",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "approved": len(rows),
        "scope_classification_counts": dict(counts),
        "queue_slice_visible_count": 67,
        "exact_reuse_prefill_count": 60,
        "residual_count": len(rows),
        "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
        "same_record_prefill_companion_count":
        len(PREFILL_COMPANION_COORDINATES),
        "raw_exact_complete_base_donor_record_count":
        len(EXACT_BASE_DONOR),
        "masked_complete_base_donor_record_count": 0,
        "semantic_base_context_record_count":
        len(SEMANTIC_BASE_CONTEXT),
        "source_call_root_count": len(SOURCE_CALL_ROOTS),
        "current_call_root_count": len(CURRENT_CALL_ROOTS),
        "optional_neighbors_present": list(optional_present),
        "changed_literal_count": changed,
        "unchanged_literal_count": len(rows) - changed,
        "combined_slice_changed_literal_count": combined_changed,
        "candidate_sha256": candidate_sha256,
        "combined_slice_candidate_sha256": combined_sha256,
        "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
        "builder_sha256": sha256_bytes(SCRIPT.read_bytes()),
        "steam_sha256_before": steam_before,
        "steam_sha256_after": steam_after,
        "base_runtime_state_inherited": False,
        "source_current_gap_equality_guarded": True,
        "inline_token_controls_guarded": True,
        "direct_call_graphs_guarded": True,
        "complete_record_assemblies_guarded": True,
        "all_slice_prefills_guarded": True,
        "combined_slice_reverse_order_exact": True,
        "source_redacted": True,
        "reverse_order_overlay_exact": True,
        "reverse_overlay_exact": True,
        "outside_scope_identity_guarded": True,
        "second_run_reproduced": True,
        "tamper_rejection_passed": True,
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
