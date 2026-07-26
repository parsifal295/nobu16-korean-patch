#!/usr/bin/env python3
"""Build source-redacted PK B080 segment 1246 residual decisions."""

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
PARENT_PATH = WORKSTREAM / "build_pk_batch075_segment1231.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B080_S1246.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B080_S1245.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B081_S1247.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1246
QUEUE_BATCH_ID = "pk_msggame-B080"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 9
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = ("9:635:0",)
TRANSLATIONS = {"9:635:0": "설마―"}
TARGET_RECORD_IDS = (635,)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {635: 2}
PREFILL_COMPANION_COORDINATES = ("9:635:1",)
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
SEMANTIC_BASE_RECORD = {635: (9, 581)}
EXACT_BASE_DONOR: dict[int, tuple[int, int]] = {}
SEMANTIC_BASE_CONTEXT = {635: ("9:581:0", "9:581:1")}
PREFILL_COMPANION_DONOR = {"9:635:1": "9:581:1"}
EXPECTED_BASE_RAW_MATCHES = {635: ((9, 581),)}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = (
    (9, 580), (9, 581), (9, 582), (9, 634), (9, 635), (9, 636),
    (9, 671), (9, 672),
)
SOURCE_CALL_ROOTS = (4,)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {635: ((4,), ())}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS: tuple[int, ...] = ()
SPEAKER_STYLE = ((635, "shocked_defeat_disbelief"),)
TERMINOLOGY_POLICY = (
    ("defeat pressure", "밀려나다"),
    ("even I", "마저"),
    ("project em dash", "―"),
    ("project ellipsis", "……"),
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
    "E797F5045EF74D1A9675A9AC5541647B60BC4D6A6E9D15478D77B4EB17727800"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "33A9E785169F217C67B9718A078245B3508EFD7A4840A87A463C255E577286BD"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "5DCFCE2163C2F9C6F07831E2D2D2048C9BF6350000694F847160A785B66E7BD3"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "4323F475AD8538B2B8FD5A60240200BFDA6FC5634D44BEEB36336BC60CEE4EF0"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "CCB3D6759AF65FFB89CF4E57A4D4F45E153494B590154FE342DD4FB84BF585E3"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "AF81C26BE4B90DDE2849A73FB5E781D4B22CBB58BB9711EB1CC5D09DF3491ECF"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "39D248A59B2D35C85ED2D96F993CE053650D04F960E025F36033EB9FCC861B53"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "F9F8B7AB0AB216707519CE4BA6AD504D42321E7D7D60D47E39661FAEEC9E1026"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "20CA35C594D7E662128B62D3B58517AE1F658FC94DB9B0C4735A23F87B9201CE"
)
EXPECTED_BOUNDARY_SHA256 = (
    "958EFD04A86707725BE815B8AD5F1A2D19D15C1B565A515E19AFCBA19ED1F7DF"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "97621739C3B7C33361BD1B96B8CEF70614559EA5F77311AE872F8FF60935E4F1"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "6B4C40AD79A7A08A2309A2DAF2EA9A27B3DB731273B42462B1F4CB0A7CFC5AC0"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "8090DFAAA53BC369DE0EA7782A723DAF7D87DE518F07ACD7F0BAAF81E100CCAA"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "D533F6037A0D3576960678D3BE1AF850947985CE89ADD6C62DDEF2957199D768"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "C520F1981BBCC5AF81DA2F8B9159D8DC85D31A29DA950ADC12CD804D151539E4"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "D1329457B7050CEB12237E7D143D4B093BFDF313B80788A455CE3EDB728FF08E"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "408F548F8D0F7BEE204F4BA46A4736DA757A08662281ED4E0DEC35FF4C6104B4"
)
EXPECTED_CANDIDATE_SHA256 = (
    "8502B420B6F113B119F2021DFBA82151B92489680AF2987523224783FEB5ED8A"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "73B63FA549A265654ED73A62863C1449F5B4C7ED73576B4DC67886F47470F3B9"
)
EXPECTED_CHANGED_LITERAL_COUNT = 1
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 64

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese source authoritative; empty PC English, "
    "Simplified Chinese and Traditional Chinese auxiliary records were "
    "recorded; the completed Base record was used only as semantic, "
    "terminology and speaker-register context without inheriting Base "
    "runtime or VM state; the complete PK shock-at-defeat line combines "
    "one manually reviewed residual with one approved prefill companion, "
    "preserving the dynamic speaker call, emphatic em dash, newline, "
    "defeat wording and project ellipsis; all sixty-five prefills in the "
    "sixty-six-row final slice, source/current gaps, protected whitespace, "
    "direct call graph and complete assembly are guarded; both overlay "
    "orders, byte-exact reversal, two-run reproduction, tamper rejection, "
    "outside-scope identity and Steam read-only state are verified; the "
    "residual remains PK runtime pending and discovered pins are immutable"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1246_parent",
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


def queue_evidence(
    prepared: Any,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[Any, ...],
    tuple[tuple[int, int], ...],
]:
    rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        str(target["coordinate"])
        for row in rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(rows) != 186
        or len(visible) != 200
        or visible[0] != "9:487:0"
        or visible[-1] != "9:672:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B080 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "9:608:0"
        or queue_slice[-1] != "9:672:0"
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
    if (
        len(prefilled) != 65
        or residual != TARGET_COORDINATES
    ):
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
        len(replacements) != 66
        or len(prefilled) != 65
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
        "HIDDEN_CURRENT_COMPANION_COORDINATES":
        HIDDEN_CURRENT_COMPANION_COORDINATES,
        "SEMANTIC_BASE_RECORD": SEMANTIC_BASE_RECORD,
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
        "EXPECTED_SOURCE_CONTROLS_BY_RECORD":
        EXPECTED_SOURCE_CONTROLS_BY_RECORD,
        "EXPECTED_CURRENT_CONTROLS_BY_RECORD":
        EXPECTED_CURRENT_CONTROLS_BY_RECORD,
        "SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS":
        SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS,
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
        "queue_evidence": queue_evidence,
        "build_combined_slice_candidate": build_combined_slice_candidate,
    }
    for name, value in values.items():
        setattr(PARENT, name, value)


def build_rows() -> tuple[
    Any, list[dict[str, Any]], bytes, str, int, str, int, tuple[str, ...],
]:
    patch_parent_globals()
    return PARENT.build_rows()


def propagate_parent_globals() -> None:
    patch_parent_globals()
    PARENT.propagate_parent_globals()


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
        len(rows) != 1
        or len(validated) != 1
        or counts != Counter({"runtime_fragment_pending": 1})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["line_count_preserved"] is not True
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ] is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    propagate_parent_globals()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    if DISCOVERED_PINS:
        raise RuntimeError(f"segment {SEGMENT} pins remained mutable")
    print(json.dumps({
        "status": "ok",
        "segment": "pk_msggame_B080_S1246",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "approved": len(rows),
        "scope_classification_counts": dict(counts),
        "queue_slice_visible_count": 66,
        "exact_reuse_prefill_count": 65,
        "residual_count": len(rows),
        "reviewed_complete_record_count": 1,
        "same_record_prefill_companion_count": 1,
        "raw_exact_complete_base_donor_record_count": 0,
        "masked_complete_base_donor_record_count": 0,
        "semantic_base_context_record_count": 1,
        "source_call_root_count": 1,
        "current_call_root_count": 1,
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
        "source_current_gap_contract_guarded": True,
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
        "discovered_pins_empty": True,
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
