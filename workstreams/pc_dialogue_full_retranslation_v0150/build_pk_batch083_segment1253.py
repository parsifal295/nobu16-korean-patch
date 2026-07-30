#!/usr/bin/env python3
"""Build source-redacted PK B083 segment 1253 residual decisions."""

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
PARENT_PATH = WORKSTREAM / "build_pk_batch080_segment1244.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B083_S1253.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B082_S1252.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B083_S1254.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1253
REPORT_SEGMENT_ID = "pk_msggame_B083_S1253"
QUEUE_BATCH_ID = "pk_msggame-B083"
QUEUE_RECORD_COUNT = 192
QUEUE_UNIVERSE_VISIBLE_COUNT = 200
QUEUE_UNIVERSE_FIRST = "9:1049:0"
QUEUE_UNIVERSE_LAST = "9:1240:0"
QUEUE_START = 0
QUEUE_STOP = 67
QUEUE_SLICE_FIRST = "9:1049:0"
QUEUE_SLICE_LAST = "9:1114:0"
QUEUE_SLICE_VISIBLE_COUNT = 67
QUEUE_SLICE_PREFILL_COUNT = 62
BLOCK_ID = 9
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "9:1075:0",
    "9:1077:0",
    "9:1096:0",
    "9:1099:0",
    "9:1104:0",
)
TRANSLATIONS = {
    "9:1075:0": "후후, 본성 경계는\n소홀히 하지 말게나",
    "9:1077:0": "여기서―",
    "9:1096:0": "알겠다!",
    "9:1099:0": "옛!",
    "9:1104:0": "내게 맡겨라!",
}
TARGET_RECORD_IDS = (1075, 1077, 1096, 1099, 1104)
STATIC_RECORD_IDS = (1075, 1096, 1099, 1104)
DYNAMIC_RECORD_IDS = (1077,)
STATIC_COORDINATES = {
    "9:1075:0", "9:1096:0", "9:1099:0", "9:1104:0",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
EXPECTED_ARITY = {1075: 1, 1077: 2, 1096: 1, 1099: 1, 1104: 1}
PREFILL_COMPANION_COORDINATES = ("9:1077:1",)
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
SEMANTIC_BASE_RECORD = {
    1075: (9, 1016),
    1077: (9, 1018),
    1096: (9, 1037),
    1099: (9, 1040),
    1104: (9, 1045),
}
EXACT_BASE_DONOR: dict[int, tuple[int, int]] = {}
SEMANTIC_BASE_CONTEXT = {
    1075: ("9:1016:0",),
    1077: ("9:1018:0", "9:1018:1"),
    1096: ("9:1037:0",),
    1099: ("9:1040:0",),
    1104: ("9:1045:0",),
}
PREFILL_COMPANION_DONOR = {"9:1077:1": "9:1018:1"}
EXPECTED_BASE_RAW_MATCHES = {
    1075: (),
    1077: ((9, 1018),),
    1096: ((9, 1037),),
    1099: ((9, 1040),),
    1104: ((9, 1045),),
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (9, record_id)
    for record_id in (
        1015, 1016, 1017, 1018, 1019, 1036, 1037, 1038,
        1039, 1040, 1041, 1044, 1045, 1046, 1048, 1049,
        1074, 1075, 1076, 1077, 1078, 1095, 1096, 1097,
        1098, 1099, 1100, 1103, 1104, 1105, 1114, 1115,
    )
)
SOURCE_CALL_ROOTS = (1,)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    1075: ((), ()),
    1077: ((1,), ()),
    1096: ((), ()),
    1099: ((), ()),
    1104: ((), ()),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (1075, "elder_citadel_defense_warning"),
    (1077, "taunting_dynamic_challenge"),
    (1096, "firm_acknowledgement"),
    (1099, "martial_acknowledgement"),
    (1104, "commanding_assurance"),
)
TERMINOLOGY_POLICY = (
    ("citadel", "본성"),
    ("citadel guard", "본성 경계"),
    ("historic assent", "옛"),
    ("project em dash", "―"),
    ("ASCII exclamation", "!"),
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
    "22CDAE64E015768DB2F0A3E7AA82F996428B905681654E30B3D08335CB0D9BE2"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "2C4FB49C00591CBA4321891997C45ACA1ADA19D7E205B127D21E83DF94BEB289"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "7FD77ACD88474751DC21BC8DD15AF77AE887F5EC0ED3EA68F12CA9325B2932BB"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "A090BC3BDFE3C9CD1D49B3BD216D700C1FF78854ACEA2187EEAC33F62D13416B"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "15359685059E28E57B3B573477EE76770477208F331A1609153DD7FF32F7DE83"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "0AD18FEC2EAB81DAD8FDC77EA39E9AC66C67B41F9140C558FB4BFD2C4E6DA604"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "290726672751153CE3A6C61A479B553A60DCB160A70D5B6FFEB16C06FC2EAC87"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "06DDB55EED65FA1067F9E0AC9031C05197CA1F44542B4D8DA1252C4E7FF1E87B"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "735DA002CBB3A995A96FCF20B519EDD3D580B8ECE47FD3FD7C48166805F1A2CB"
)
EXPECTED_BOUNDARY_SHA256 = (
    "ED8D886611CE02134F32116021C26A101AAFCEFB480067743B53D3FFA1367273"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "467A67EF926F4722E10F3587913B2E0951F0A5994736B36A752E0CC5B1C9E1EC"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "916027321CF59339ABDB0CE5D6CD98932ADCB5C496AB89DE302967A531F72D2E"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "EEAD811F787321625F528863F6876A4D65F2EBF0FBCE6BA810C6C788018E6F3D"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "9F6F46D774474371A103483E9C9BFA5C47CE1819CB17620E9DBFE32BDF9CD7BD"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "5281072AFABE5904340CF90A7B5D35F9A6275FFE03102956E9A4504E1A3B4020"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "602453AFA2D301F1108E4CDDE2D020FA33597C2391D94271E5993469A5CEAB93"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "C0831046AF117C15DFAA2052EB1E2C85F22D15713C0CD9F994AC2DC43D181AA1"
)
EXPECTED_CANDIDATE_SHA256 = (
    "855AD2CA718AB47CABB71A111721DA68E236EF5006CDE0A4F338CE5C89928AB2"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "5E26CA2F331A6DB5D88B6B2658D9B541E39080B356E58A89A3CFCE195E436BCA"
)
EXPECTED_CHANGED_LITERAL_COUNT = 5
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 50

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese source authoritative; PC English, Simplified "
    "Chinese and Traditional Chinese auxiliaries were reviewed; completed "
    "Base records were used only as semantic, terminology and speaker-"
    "register context without inheriting Base runtime or VM state; the "
    "citadel warning is contextually adapted from the corresponding Base "
    "retreat-route warning, while the challenge and command responses use "
    "the completed Base wording and preserve the dynamic speaker call, "
    "historic assent, project em dash and punctuation; five residual "
    "translations plus one approved prefill companion assemble all five "
    "complete records; all sixty-two prefills in the sixty-seven-row "
    "opening slice, source/current gaps, controls, protected whitespace and "
    "complete assemblies are guarded; both overlay orders, byte-exact "
    "reversal, two-run reproduction, tamper rejection, outside-scope "
    "identity and Steam read-only state are verified; discovered pins are "
    "immutable and Base runtime state is never inherited"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1253_parent",
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
coordinate_key = PARENT.PARENT.coordinate_key
literal_texts = PARENT.PARENT.literal_texts
gap_bytes = PARENT.PARENT.gap_bytes
read_jsonl = PARENT.PARENT.read_jsonl

CONFIG_NAMES = (
    "SCRIPT", "OUTPUT", "PREFILL", "BASE_PROMOTED", "OPTIONAL_NEIGHBORS",
    "STEAM_PK", "SEGMENT", "QUEUE_BATCH_ID", "QUEUE_START", "QUEUE_STOP",
    "QUEUE_SLICE_FIRST", "QUEUE_SLICE_LAST", "QUEUE_SLICE_VISIBLE_COUNT",
    "QUEUE_SLICE_PREFILL_COUNT", "BLOCK_ID", "PK_RECORD_COUNT",
    "TARGET_COORDINATES", "TRANSLATIONS", "TARGET_RECORD_IDS",
    "STATIC_RECORD_IDS", "DYNAMIC_RECORD_IDS", "STATIC_COORDINATES",
    "DYNAMIC_COORDINATES", "EXPECTED_ARITY",
    "PREFILL_COMPANION_COORDINATES",
    "HIDDEN_CURRENT_COMPANION_COORDINATES", "SEMANTIC_BASE_RECORD",
    "PREFILL_COMPANION_DONOR", "EXACT_BASE_DONOR",
    "SEMANTIC_BASE_CONTEXT", "EXPECTED_BASE_RAW_MATCHES",
    "EXPECTED_BASE_LITERAL_MATCHES", "EXPECTED_BASE_MASKED_MATCHES",
    "BOUNDARY_RECORD_KEYS", "SOURCE_CALL_ROOTS", "CURRENT_CALL_ROOTS",
    "EXPECTED_CONTROLS_BY_RECORD", "EXPECTED_SOURCE_CONTROLS_BY_RECORD",
    "EXPECTED_CURRENT_CONTROLS_BY_RECORD",
    "SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS", "SPEAKER_STYLE",
    "TERMINOLOGY_POLICY", "EXPECTED_STEAM_PK_SHA256",
    "EXPECTED_PRISTINE_PK_SHA256", "EXPECTED_PREFILL_SHA256",
    "EXPECTED_BASE_PROMOTED_SHA256", "EXPECTED_QUEUE_UNIVERSE_SHA256",
    "EXPECTED_QUEUE_SLICE_SHA256",
    "EXPECTED_PREFILLED_COORDINATE_SHA256",
    "EXPECTED_PREFILL_SLICE_CONTEXT_SHA256",
    "EXPECTED_TARGET_COORDINATE_SHA256", "EXPECTED_SOURCE_TARGET_SHA256",
    "EXPECTED_CURRENT_TARGET_SHA256", "EXPECTED_CONTEXT_CORPUS_SHA256",
    "EXPECTED_GAP_CONTRACT_SHA256", "EXPECTED_BOUNDARY_SHA256",
    "EXPECTED_RUNTIME_CONTROL_SHA256", "EXPECTED_BASE_SEARCH_SHA256",
    "EXPECTED_COMPLETE_ASSEMBLY_SHA256", "EXPECTED_CALL_GRAPH_SHA256",
    "EXPECTED_SPEAKER_STYLE_SHA256",
    "EXPECTED_TERMINOLOGY_POLICY_SHA256",
    "EXPECTED_TRANSLATION_POLICY_SHA256", "EXPECTED_CANDIDATE_SHA256",
    "EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256",
    "EXPECTED_CHANGED_LITERAL_COUNT",
    "EXPECTED_COMBINED_CHANGED_LITERAL_COUNT", "DISCOVERED_PINS", "BASIS",
)


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
        len(rows) != QUEUE_RECORD_COUNT
        or len(visible) != QUEUE_UNIVERSE_VISIBLE_COUNT
        or visible[0] != QUEUE_UNIVERSE_FIRST
        or visible[-1] != QUEUE_UNIVERSE_LAST
    ):
        raise RuntimeError(f"segment {SEGMENT} queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != QUEUE_SLICE_VISIBLE_COUNT
        or queue_slice[0] != QUEUE_SLICE_FIRST
        or queue_slice[-1] != QUEUE_SLICE_LAST
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
        len(prefilled) != QUEUE_SLICE_PREFILL_COUNT
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
        len(replacements) != QUEUE_SLICE_VISIBLE_COUNT
        or len(prefilled) != QUEUE_SLICE_PREFILL_COUNT
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


def install_globals() -> None:
    namespace = globals()
    for name in CONFIG_NAMES:
        setattr(PARENT, name, namespace[name])
    PARENT.install_globals()
    PARENT.PARENT.queue_evidence = queue_evidence
    PARENT.PARENT.build_combined_slice_candidate = (
        build_combined_slice_candidate
    )
    for name in CONFIG_NAMES:
        setattr(PARENT.PARENT, name, namespace[name])


def build_rows() -> tuple[
    Any, list[dict[str, Any]], bytes, str, int, str, int, tuple[str, ...],
]:
    install_globals()
    return PARENT.PARENT.build_rows()


def run_segment() -> int:
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
        len(rows) != len(TARGET_COORDINATES)
        or len(validated) != len(TARGET_COORDINATES)
        or counts != Counter({
            "runtime_fragment_pending": len(TARGET_COORDINATES),
        })
        or any(
            row["semantic_review"] != "approved"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["line_count_preserved"] is not True
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ] is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    install_globals()
    PARENT.PARENT.propagate_parent_globals()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    if DISCOVERED_PINS:
        raise RuntimeError(f"segment {SEGMENT} pins remained mutable")
    print(json.dumps({
        "status": "ok",
        "segment": REPORT_SEGMENT_ID,
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "approved": len(rows),
        "scope_classification_counts": dict(counts),
        "queue_slice_visible_count": QUEUE_SLICE_VISIBLE_COUNT,
        "exact_reuse_prefill_count": QUEUE_SLICE_PREFILL_COUNT,
        "residual_count": len(rows),
        "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
        "same_record_prefill_companion_count":
        len(PREFILL_COMPANION_COORDINATES),
        "raw_exact_complete_base_donor_record_count": 0,
        "masked_complete_base_donor_record_count": 0,
        "semantic_base_context_record_count": len(SEMANTIC_BASE_RECORD),
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


def main() -> int:
    return run_segment()


if __name__ == "__main__":
    raise SystemExit(main())
