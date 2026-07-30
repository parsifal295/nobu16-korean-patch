#!/usr/bin/env python3
"""Build source-redacted PK B058 segment 1186 residual decisions."""

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
PARENT_PATH = WORKSTREAM / "build_pk_batch057_segment1183.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B058_S1186.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B058_S1185.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1186
QUEUE_BATCH_ID = "pk_msggame-B058"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = ("7:1047:1",)
TRANSLATIONS = {
    "7:1047:1": (
        "은(는) 싸울 때를 잘못 짚었는지도 모르겠군\n"
        "이 피해로는 당분간 싸우기 어렵겠어……"
    ),
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (1047,)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {1047: 2}
PREFILL_COMPANION_COORDINATES: tuple[str, ...] = ()
FUTURE_COMPANION_COORDINATES: tuple[str, ...] = ()
OUTSIDE_SLICE_COMPANION_COORDINATES = ("7:1047:0",)
EXPECTED_COMPANION_TRANSLATION = "상대에게 이토록 패하다니……\n"
EXPECTED_BASE_MATCHES = {1047: ()}
EXPECTED_RAW_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_LITERAL_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_MASKED_BASE_MATCHES = EXPECTED_BASE_MATCHES
PRIMARY_BASE_MATCH: dict[int, tuple[int, int]] = {}
EXPECTED_BASE_DONOR_COORDINATES = {
    1047: ("7:994:0", "15:1823:0", "15:1858:0", "6:3194:0"),
}
BOUNDARY_RECORD_KEYS = (
    (7, 1002),
    (7, 1003),
    (7, 1046),
    (7, 1047),
    (7, 1048),
    (7, 1112),
    (7, 1113),
    (7, 1176),
    (7, 1177),
)
SOURCE_CALL_ROOTS = (1,)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    1047: ((1,), ("025032",)),
}
SPEAKER_STYLE = (
    (1047, "battle_loss_recovery_assessment"),
)
TERMINOLOGY_POLICY = (
    ("battle opportunity", "싸울 때"),
    ("damage", "피해"),
    ("for a while", "당분간"),
    ("difficult to fight", "싸우기 어렵다"),
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
    "4AAA68453D0B5ADA984EDB3ADC13CAF7BD57952640B15351135138705612A808"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "467ACF7A03ECDDBDC658E0F5EA3B15A2697D994C0972362207C63F50A4F48629"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "7493DBDFB67B69502F0C9D08520474364D1344E148DED7CDCBB51C4181C3C456"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "C824F696D488E946DE4DAA2B6535C5DD9290AD2C7B3F618F4A2783EB391C6082"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "7EBDC34215ADEF74EF55AA20CBE1065ED4976E745CEE13C25485676945808ECF"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "3AC7339FF647FD7205958FE171028C1CE68C24762C46A5C0E341DAFC8D7839C5"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "F8330695989F614845DB81BB24B3B76EB58B4D707AC15831FA119FE863597F11"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "CCE35AB5EA30617D091F2A53FF9FA3435E12AC24C9A8B4EB46F9D9DC894EBEC4"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "622EA3CE20528CE78896409C59F830C07E397C6468592DBBC10E03A4176DADEF"
)
EXPECTED_BOUNDARY_SHA256 = (
    "FF15B9450B80D00697CC303304D1075CC52B34F8E7C6EBA4FD63CF09A72632C4"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "77905B0582222F37F3F9ED0B3D5AAC110A76078369BA5A05EC5A00AFD1A3BF49"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "16B8098C23B285E6FF87256125B5A852A521D06FFAE8AC5DA389A876C9942FC6"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "4D24FA0705B6AD6B5178C8751160B824859E818AB4020FBA3417D60067C79656"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "EBC9893B9457F5CF89127228ECBDF444F65D81066837900F3EA1963D74930FAE"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "6C65E1102B141920B6CD8E8B4190D70BA5AD285BCB99359EF450799E85942B3A"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "1B629F12C5EDB309B530BCC9E906FB5EDB320CEBC2CDB9376770AE385FF5BA66"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "9977661391E0B931D3B5AA28B884A47DA37DE70F4CB37961BFB6A6A42ACBB289"
)
EXPECTED_CANDIDATE_SHA256 = (
    "C2827FBEC1DA3CB7214D3911AE817675C3B824FDA7C8F774DA2BCE5D33D286D2"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "7C785A17B2E9980F001D807FD67118E88839EEA623DC134825E5769E100D91C8"
)
EXPECTED_CHANGED_LITERAL_COUNT = 1

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source authoritative; complete PC EN SC TC context "
    "was checked and is empty for this record; the completed Base corpus "
    "contains no complete or literal source match, so verified Base rows "
    "are used only as manual semantic references for defeat, battle "
    "opportunity and temporary recovery wording; the preceding literal "
    "from optional segment 1185 is checked when present and its reviewed "
    "fallback is assembled when absent; all sixty-six Base-prefilled rows "
    "in the queue slice are validated and the sixty-seven-row combined "
    "slice is rebuilt in both orders and reversed byte-exactly; the direct "
    "call, inline dynamic token, particles, newlines, protected outer "
    "whitespace, full record, queue and segment boundaries, two-run "
    "reproduction, tamper rejection, outside-scope identity and Steam "
    "read-only state are guarded; Base runtime and VM state are not "
    "inherited and the residual remains runtime pending"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1186_parent",
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
sha256_bytes = PARENT.sha256_bytes
canonical_sha256 = PARENT.canonical_sha256
coordinate_key = PARENT.coordinate_key
literal_texts = PARENT.literal_texts
gap_bytes = PARENT.gap_bytes
read_jsonl = PARENT.read_jsonl
context_records = PARENT.context_records
runtime_controls = PARENT.runtime_controls
mask_call_operands = PARENT.PARENT.mask_call_operands


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
    return actual


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
        len(rows) != 174
        or len(visible) != 200
        or visible[0] != "7:1003:0"
        or visible[-1] != "7:1176:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B058 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "7:1047:1"
        or queue_slice[-1] != "7:1112:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in prefill_rows
    )
    if (
        len(prefilled) != 66
        or len(residual) != 1
        or residual != TARGET_COORDINATES
    ):
        raise RuntimeError(f"segment {SEGMENT} queue residual drifted")
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


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    values = PARENT.PARENT.engine_builder().context_evidence(
        prepared,
        records_by_label,
    )
    for label, value, expected in (
        ("source target", values["source_target"], EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", values["current_target"], EXPECTED_CURRENT_TARGET_SHA256),
        ("multilingual context", values["corpus"], EXPECTED_CONTEXT_CORPUS_SHA256),
        ("gap contract", values["gaps"], EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", values["boundary"], EXPECTED_BOUNDARY_SHA256),
        ("runtime control", values["controls"], EXPECTED_RUNTIME_CONTROL_SHA256),
    ):
        guarded_digest(label, value, expected)
    expected_controls = tuple(
        (label, record_id, EXPECTED_CONTROLS_BY_RECORD[record_id])
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    if (
        any(source != current for _, source, current in values["gaps"])
        or values["controls"] != expected_controls
        or any(
            ("pk_msggame", *coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime layout drifted")


def optional_companion(prepared: Any) -> tuple[str, bool]:
    path = OPTIONAL_NEIGHBORS[0]
    if not path.is_file():
        return EXPECTED_COMPANION_TRANSLATION, False
    ENGINE.validate_decisions(prepared, path, require_complete=False)
    matches = [
        row
        for row in read_jsonl(path)
        if str(row.get("coordinate"))
        == OUTSIDE_SLICE_COMPANION_COORDINATES[0]
    ]
    if (
        len(matches) != 1
        or matches[0].get("semantic_review") != "approved"
        or matches[0].get("runtime_review") != "pending"
        or str(matches[0].get("translation"))
        != EXPECTED_COMPANION_TRANSLATION
    ):
        raise RuntimeError(f"segment {SEGMENT} optional companion drifted")
    return EXPECTED_COMPANION_TRANSLATION, True


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_rows = {
        str(row["coordinate"]): row for row in read_jsonl(BASE_PROMOTED)
    }
    key = (BLOCK_ID, 1047)
    source = records_by_label["jp"][key]
    source_literals = literal_texts(records_by_label["jp"], key)
    current_literals = literal_texts(records_by_label["current"], key)
    raw_matches = tuple(
        coordinate
        for coordinate, record in base_source.items()
        if record.data == source.data
    )
    literal_matches = tuple(
        coordinate
        for coordinate in base_source
        if literal_texts(base_source, coordinate) == source_literals
    )
    masked_matches = tuple(
        coordinate
        for coordinate, record in base_source.items()
        if (
            literal_texts(base_source, coordinate) == source_literals
            and mask_call_operands(record) == mask_call_operands(source)
        )
    )
    if (
        len(source_literals) != EXPECTED_ARITY[1047]
        or raw_matches
        or literal_matches
        or masked_matches
    ):
        raise RuntimeError(f"segment {SEGMENT} Base no-match contract drifted")
    semantic_rows: list[dict[str, Any]] = []
    for coordinate in EXPECTED_BASE_DONOR_COORDINATES[1047]:
        row = base_rows.get(coordinate)
        if (
            row is None
            or row.get("semantic_review") != "approved"
            or row.get("runtime_review") not in {"verified", "not_required"}
        ):
            raise RuntimeError(
                f"segment {SEGMENT} missing semantic reference: {coordinate}"
            )
        semantic_rows.append(row)
    companion, _ = optional_companion(prepared)
    ENGINE.validate_translation_shape(
        current_literals[0],
        companion,
        "runtime_pending",
        OUTSIDE_SLICE_COMPANION_COORDINATES[0],
    )
    if (
        companion.count("\n") != current_literals[0].count("\n")
        or ENGINE.protected_signature(companion)
        != ENGINE.protected_signature(current_literals[0])
    ):
        raise RuntimeError(f"segment {SEGMENT} companion shape drifted")
    assembled = (companion, TRANSLATIONS[TARGET_COORDINATES[0]])
    base_evidence = (
        (
            1047,
            sha256_bytes(source.data),
            source_literals,
            current_literals,
            tuple(value.hex().upper() for value in gap_bytes(source)),
            raw_matches,
            literal_matches,
            masked_matches,
            tuple(
                (
                    coordinate,
                    str(row["translation"]),
                    str(row["semantic_review"]),
                    str(row["runtime_review"]),
                )
                for coordinate, row in zip(
                    EXPECTED_BASE_DONOR_COORDINATES[1047],
                    semantic_rows,
                )
            ),
        ),
    )
    assembly_evidence = (
        (
            1047,
            assembled,
            runtime_controls(source),
            runtime_controls(records_by_label["current"][key]),
            "manual_complete_record_reviewed",
            "semantic_base_references_only",
            "base_runtime_state_not_inherited",
        ),
    )
    return base_evidence, assembly_evidence


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
    base, assembly = base_and_assembly_evidence(prepared, records_by_label)
    guarded_digest("Base search", base, EXPECTED_BASE_SEARCH_SHA256)
    guarded_digest(
        "complete assembly",
        assembly,
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )


def call_graph_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[Any, ...]:
    evidence = tuple(
        (
            label,
            record_id,
            runtime_controls(
                records_by_label[label][(BLOCK_ID, record_id)]
            )[0],
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    expected = tuple(
        (label, 1047, (1,))
        for label in ("jp", "current")
    )
    if evidence != expected:
        raise RuntimeError(f"segment {SEGMENT} direct call graph drifted")
    return evidence


def assert_call_graphs(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    guarded_digest(
        "call graph",
        call_graph_evidence(records_by_label),
        EXPECTED_CALL_GRAPH_SHA256,
    )


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source = records_by_label["jp"][(BLOCK_ID, record_id)]
    current = records_by_label["current"][(BLOCK_ID, record_id)]
    source_controls = runtime_controls(source)
    current_controls = runtime_controls(current)
    return {
        "runtime_category": dict(SPEAKER_STYLE)[record_id],
        "source_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(source))
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(current))
        ),
        "source_direct_call_operands": source_controls[0],
        "current_direct_call_operands": current_controls[0],
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal":
        gap_bytes(source) == gap_bytes(current),
        "base_complete_record_match_kind": "none",
        "base_complete_record_coordinates": (),
        "base_semantic_reference_coordinates":
        EXPECTED_BASE_DONOR_COORDINATES[record_id],
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "same_record_prefill_companion_reviewed": False,
        "outside_slice_companion_reviewed": True,
        "manual_multilingual_context_reviewed": True,
        "completed_base_corpus_searched": True,
        "completed_base_donor_reviewed": True,
        "protected_outer_whitespace_preserved": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_runtime_state_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }


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
    candidate = ENGINE.rebuild_packed_with_literals(
        current_blob,
        replacements,
    )
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
        or len(prefilled) != 66
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
        and candidate_sha256
        != EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} combined candidate drifted: "
            f"{candidate_sha256}"
        )
    if EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS["combined slice candidate"] = candidate_sha256
        DISCOVERED_PINS["combined slice changed count"] = str(changed)
    return candidate_sha256, changed


def configure_parent() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
        "OPTIONAL_NEIGHBORS": OPTIONAL_NEIGHBORS,
        "STEAM_PK": STEAM_PK,
        "SEGMENT": SEGMENT,
        "QUEUE_BATCH_ID": QUEUE_BATCH_ID,
        "QUEUE_START": QUEUE_START,
        "QUEUE_STOP": QUEUE_STOP,
        "BLOCK_ID": BLOCK_ID,
        "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "PREFILL_COMPANION_COORDINATES": PREFILL_COMPANION_COORDINATES,
        "FUTURE_COMPANION_COORDINATES": FUTURE_COMPANION_COORDINATES,
        "PRIMARY_BASE_MATCH": PRIMARY_BASE_MATCH,
        "EXPECTED_BASE_MATCHES": EXPECTED_BASE_MATCHES,
        "EXPECTED_RAW_BASE_MATCHES": EXPECTED_RAW_BASE_MATCHES,
        "EXPECTED_LITERAL_BASE_MATCHES": EXPECTED_LITERAL_BASE_MATCHES,
        "EXPECTED_MASKED_BASE_MATCHES": EXPECTED_MASKED_BASE_MATCHES,
        "EXPECTED_BASE_DONOR_COORDINATES":
        EXPECTED_BASE_DONOR_COORDINATES,
        "BOUNDARY_RECORD_KEYS": BOUNDARY_RECORD_KEYS,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
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
        "DISCOVERED_PINS": DISCOVERED_PINS,
        "BASIS": BASIS,
    }
    for name, value in values.items():
        setattr(PARENT, name, value)
    PARENT.queue_evidence = queue_evidence
    PARENT.assert_context_contracts = assert_context_contracts
    PARENT.runtime_evidence = runtime_evidence
    PARENT.build_combined_slice_candidate = build_combined_slice_candidate
    base_module = PARENT.PARENT
    base_module.base_and_assembly_evidence = base_and_assembly_evidence
    base_module.assert_base_and_complete_assembly = (
        assert_base_and_complete_assembly
    )
    core = base_module.engine_builder()
    core.call_graph_evidence = call_graph_evidence
    core.assert_call_graphs = assert_call_graphs


def build_rows() -> tuple[Any, ...]:
    configure_parent()
    result = list(PARENT.build_rows())
    rows = result[1]
    for row in rows:
        row["manual_complete_base_donor_translation_selected"] = False
        row["manual_semantic_base_references_reviewed"] = True
        row["manual_multilingual_translation_selected"] = True
        row["same_record_prefill_companion_reviewed"] = False
        row["outside_slice_companion_reviewed"] = True
        row["next_slice_companion_reviewed"] = False
    return tuple(result)


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        combined_sha256,
        combined_changed,
        optional_present,
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
    steam_before = sha256_bytes(STEAM_PK.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: {steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
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
            ]
            is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    if EXPECTED_CANDIDATE_SHA256 != "TO_PIN":
        PARENT.PARENT.engine_builder().assert_tamper_rejection(
            prepared,
            rows,
            candidate,
        )
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    _, companion_present = optional_companion(prepared)
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B058_S1186",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "target_coordinate_first": TARGET_COORDINATES[0],
                "target_coordinate_last": TARGET_COORDINATES[-1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 67,
                "exact_reuse_prefill_count": 66,
                "residual_count": len(rows),
                "reviewed_complete_record_count": 1,
                "same_record_outside_slice_companion_count": 1,
                "optional_companion_output_present": companion_present,
                "complete_base_match_record_count": 0,
                "no_complete_base_match_record_count": 1,
                "semantic_base_reference_count":
                len(EXPECTED_BASE_DONOR_COORDINATES[1047]),
                "source_call_root_count": len(SOURCE_CALL_ROOTS),
                "current_call_root_count": len(CURRENT_CALL_ROOTS),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "unchanged_literal_count": len(rows) - changed,
                "combined_slice_changed_literal_count": combined_changed,
                "candidate_sha256": candidate_sha256,
                "combined_slice_candidate_sha256": combined_sha256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "steam_sha256_before": steam_before,
                "steam_sha256_after": steam_after,
                "base_runtime_state_inherited": False,
                "source_current_gap_equality_guarded": True,
                "inline_token_controls_guarded": True,
                "direct_call_controls_guarded": True,
                "complete_record_assemblies_guarded": True,
                "all_slice_prefills_guarded": True,
                "combined_slice_reverse_order_exact": True,
                "source_redacted": True,
                "reverse_order_overlay_exact": True,
                "reverse_overlay_exact": True,
                "second_run_reproduced": True,
                "outside_scope_identity_guarded": True,
                "tamper_rejection_passed":
                EXPECTED_CANDIDATE_SHA256 != "TO_PIN",
                "discovered_pins": DISCOVERED_PINS,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
