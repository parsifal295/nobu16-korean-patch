#!/usr/bin/env python3
"""Build source-redacted PK B056 segment 1181 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch056_segment1180.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B056_S1181.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B056_S1179.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B056_S1180.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1181
QUEUE_BATCH_ID = "pk_msggame-B056"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = tuple(
    """
    7:850:4
    7:851:1 7:851:2 7:851:4
    7:852:1 7:852:2 7:852:4
    7:858:0
    7:860:0
    7:862:0
    7:863:0
    7:869:0
    7:871:0
    7:877:0 7:877:1
    7:879:0 7:879:2
    7:887:0
    7:888:0 7:888:2
    7:889:0 7:889:2
    """.split()
)
TRANSLATIONS = {
    "7:850:4": "!",
    "7:851:1": "·",
    "7:851:2": "이(가)\n",
    "7:851:4": "!",
    "7:852:1": "·",
    "7:852:2": "이(가)\n",
    "7:852:4": "!",
    "7:858:0": "모신",
    "7:860:0": "독안룡",
    "7:862:0": "오니시마즈",
    "7:863:0": "오니시마즈",
    "7:869:0": "불적·",
    "7:871:0": "·",
    "7:877:0": "마침내 「",
    "7:877:1": "」이(가) 왔는가……!\n",
    "7:879:0": "놈이 나타나",
    "7:879:2": "도록 하라",
    "7:887:0": "·",
    "7:888:0": "·",
    "7:888:2": "!",
    "7:889:0": "·",
    "7:889:2": "!",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    850,
    851,
    852,
    858,
    860,
    862,
    863,
    869,
    871,
    877,
    879,
    887,
    888,
    889,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    850: 5,
    851: 5,
    852: 5,
    858: 1,
    860: 1,
    862: 1,
    863: 1,
    869: 2,
    871: 2,
    877: 3,
    879: 3,
    887: 2,
    888: 3,
    889: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "7:850:0",
    "7:850:3",
    "7:851:0",
    "7:851:3",
    "7:852:0",
    "7:852:3",
    "7:869:1",
    "7:871:1",
    "7:877:2",
    "7:879:1",
    "7:887:1",
    "7:888:1",
    "7:889:1",
)
PREVIOUS_COMPANION_COORDINATES = ("7:850:1", "7:850:2")
REPEATED_BASE_MATCHES = tuple((7, record_id) for record_id in range(831, 842))
EXPECTED_BASE_MATCHES = {
    850: REPEATED_BASE_MATCHES,
    851: REPEATED_BASE_MATCHES,
    852: REPEATED_BASE_MATCHES,
    858: ((7, 847),),
    860: ((7, 849),),
    862: ((7, 851), (7, 852)),
    863: ((7, 851), (7, 852)),
    869: ((7, 858),),
    871: ((7, 860),),
    877: ((7, 866),),
    879: ((7, 868),),
    887: ((7, 876),),
    888: ((7, 877),),
    889: ((7, 878),),
}
EXPECTED_RAW_BASE_MATCHES = {
    850: (),
    851: (),
    852: (),
    858: ((7, 847),),
    860: ((7, 849),),
    862: ((7, 851), (7, 852)),
    863: ((7, 851), (7, 852)),
    869: ((7, 858),),
    871: ((7, 860),),
    877: (),
    879: (),
    887: (),
    888: (),
    889: (),
}
EXPECTED_LITERAL_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_MASKED_BASE_MATCHES = EXPECTED_BASE_MATCHES
PRIMARY_BASE_MATCH = {
    850: (7, 831),
    851: (7, 831),
    852: (7, 831),
    858: (7, 847),
    860: (7, 849),
    862: (7, 851),
    863: (7, 851),
    869: (7, 858),
    871: (7, 860),
    877: (7, 866),
    879: (7, 868),
    887: (7, 876),
    888: (7, 877),
    889: (7, 878),
}
EXPECTED_BASE_DONOR_COORDINATES = {
    record_id: tuple(
        f"{base_key[0]}:{base_key[1]}:{literal_id}"
        for literal_id in range(EXPECTED_ARITY[record_id])
    )
    for record_id, base_key in PRIMARY_BASE_MATCH.items()
}
BOUNDARY_RECORD_KEYS = (
    (7, 849),
    *tuple((7, record_id) for record_id in TARGET_RECORD_IDS),
    (7, 853),
    (7, 857),
    (7, 859),
    (7, 861),
    (7, 864),
    (7, 868),
    (7, 870),
    (7, 872),
    (7, 876),
    (7, 878),
    (7, 880),
    (7, 886),
    (7, 890),
)
SOURCE_CALL_ROOTS = (7, 490, 496, 538, 1066)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
SPEAKER_STYLE = tuple(
    (
        record_id,
        (
            "renowned_officer_invasion"
            if record_id <= 852
            else "historical_epithet"
            if record_id <= 871
            else "rival_officer_arrival"
        ),
    )
    for record_id in TARGET_RECORD_IDS
)
TERMINOLOGY_POLICY = (
    ("Mori title", "모신"),
    ("Date Masamune title", "독안룡"),
    ("Shimazu title", "오니시마즈"),
    ("Buddhist enemy", "불적"),
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
    "08759A9A03002395F51AA0CCE8E996881B24DC2540577FCFBD3E422603416874"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "559839131A289E601BE4FD1DED704C5B246DD75F1CD25895E508568E3AC1C144"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "1D68AA6FDD4B25CCD4DC019B674C0B6F894E545AF2BAFB2EE11DBA07B885E70D"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "979CA54811C897B111D840D363946EFA79E8C11FBA4983CB1BD1E7C25E17F7D3"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "37FEF8B586060BB5ADCFE352BEC98FF26F4766782E4A739DE161F067761D7430"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "1E95ED98E302854C3F7B56650ADAB6890B8AC8ACD7E21913A5A19998A4E0988F"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "2D0889CABEDB1AF0427146419F02683BA1D1D990B3CF4011946B6071C407B2F7"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "733995DA11DE0FCFD5A0EEE0DA50C021CDEEB7D0B887C851ABEB6CB60C7EBD54"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "76D1D75ADF923A4DD54BC34CCF2E9B39DB7E5C9AFCB2C77D6571BE3943C9D304"
)
EXPECTED_BOUNDARY_SHA256 = (
    "DE5769AE4EE5C26750D7682C6EC1FC334421D2E0A73B4DA24BEDCDACA606C50A"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "E3655D52CDC062489191E4C4DCE2280CACCCC023462045DF7B12E32304BA53CE"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "5F578A6EC956896BD0C59D6D61D9426CFA301FD0630A9DEB6F881285EF66D5CA"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "8175350FDF261FA9DE9D99BD5795458208CB03D3C66DDDEFEAC2A3D3B63669C7"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "B7B9EE3B9B3898D366C04EA0936F39CF868352EF826441D4DBBC7C27D639776D"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "6AE9EC079725EEC17FC1F7D6BC50F7F2CFDB708995B4FA7AA32AF129DAB4C465"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "F073F9558E76498FBEA15276D4AC849F7B1ED2FABB58A39EC3DEE03A29D24270"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "299E5F2FA1DE1379A8FF7C256F72ED50316CB8F5DB770CB8C5EAD0EE02C5EEC7"
)
EXPECTED_CANDIDATE_SHA256 = (
    "F963256D7B2A6252C5E2D4F3EE52870998110A570A843CEDECB054C804D8DC8C"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "FC04D0D816DC153BE95120E1602B7561AC1A0B4EF0CFE398B164658AF2E1B10D"
)
EXPECTED_CHANGED_LITERAL_COUNT = 13

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source authoritative; complete PC EN SC TC records "
    "reviewed; every target record has a completed Base literal-plus-"
    "masked-call semantic donor; thirteen same-slice prefilled companions "
    "and two preceding-slice companions are reviewed as complete record "
    "assemblies, validating the preceding output if present and otherwise "
    "pinning its completed Base wording; all forty-four Base prefills in "
    "the queue slice are validated; officer and force tokens, particles, "
    "middle-dot separators, line breaks, calls, inline tokens, protected "
    "whitespace, boundaries, two-run reproduction, tamper rejection, "
    "reverse overlays, outside-scope identity and Steam read-only state "
    "are guarded; Base runtime and VM state are not inherited and every "
    "residual remains runtime pending"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1181_base",
        BASE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_base()
ENGINE = BASE.ENGINE
sha256_bytes = BASE.sha256_bytes
canonical_sha256 = BASE.canonical_sha256
coordinate_key = BASE.coordinate_key
literal_texts = BASE.literal_texts
gap_bytes = BASE.gap_bytes
read_jsonl = BASE.read_jsonl
context_records = BASE.context_records
runtime_controls = BASE.runtime_controls
mask_call_operands = BASE.mask_call_operands


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
        len(rows) != 93
        or len(visible) != 200
        or visible[0] != "7:798:0"
        or visible[-1] != "7:890:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B056 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "7:850:4"
        or queue_slice[-1] != "7:890:0"
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
        len(prefilled) != 44
        or len(residual) != 22
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


EXPECTED_CONTROLS = {
    850: ((538,), ("023D", "024833", "023C")),
    851: ((538,), ("023D", "024833", "023C")),
    852: ((538,), ("023D", "024833", "023C")),
    858: ((), ()),
    860: ((), ()),
    862: ((), ()),
    863: ((), ()),
    869: ((), ("024833",)),
    871: ((), ("023C", "024833")),
    877: ((7, 1066), ("023C",)),
    879: ((538, 490), ("023C",)),
    887: ((496,), ("023C", "024833")),
    888: ((1066,), ("023C", "024833")),
    889: ((1066,), ("023C", "024833")),
}


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    values = BASE.engine_builder().context_evidence(prepared, records_by_label)
    for label, value, expected in (
        ("source target", values["source_target"], EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", values["current_target"], EXPECTED_CURRENT_TARGET_SHA256),
        ("multilingual context", values["corpus"], EXPECTED_CONTEXT_CORPUS_SHA256),
        ("gap contract", values["gaps"], EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", values["boundary"], EXPECTED_BOUNDARY_SHA256),
        ("runtime control", values["controls"], EXPECTED_RUNTIME_CONTROL_SHA256),
    ):
        BASE.guarded_digest(label, value, expected)
    if (
        any(source != current for _, source, current in values["gaps"])
        or any(
            ("pk_msggame", *coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime layout drifted")
    for label in ("jp", "current"):
        for record_id in TARGET_RECORD_IDS:
            if (
                runtime_controls(records_by_label[label][(BLOCK_ID, record_id)])
                != EXPECTED_CONTROLS[record_id]
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} control drifted: {label} {record_id}"
                )


def previous_rows(prepared: Any) -> dict[str, dict[str, Any]]:
    path = OPTIONAL_NEIGHBORS[1]
    if not path.is_file():
        return {}
    ENGINE.validate_decisions(prepared, path, require_complete=False)
    return {
        str(row["coordinate"]): row
        for row in read_jsonl(path)
        if str(row.get("coordinate")) in PREVIOUS_COMPANION_COORDINATES
    }


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
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prior_rows = previous_rows(prepared)
    target_set = set(TARGET_COORDINATES)
    companion_set = set(PREFILL_COMPANION_COORDINATES)
    previous_set = set(PREVIOUS_COMPANION_COORDINATES)
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    seen_previous: set[str] = set()
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        key = (BLOCK_ID, record_id)
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
            len(source_literals) != EXPECTED_ARITY[record_id]
            or raw_matches != EXPECTED_RAW_BASE_MATCHES[record_id]
            or literal_matches != EXPECTED_LITERAL_BASE_MATCHES[record_id]
            or masked_matches != EXPECTED_MASKED_BASE_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base search drifted: {record_id}"
            )
        assembled: list[str] = []
        donor_assembled: list[str] = []
        donor_rows: list[dict[str, Any]] = []
        base_key = PRIMARY_BASE_MATCH[record_id]
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"{BLOCK_ID}:{record_id}:{literal_id}"
            donor_coordinate = (
                f"{base_key[0]}:{base_key[1]}:{literal_id}"
            )
            donor = base_rows.get(donor_coordinate)
            if (
                donor is None
                or donor.get("semantic_review") != "approved"
                or donor.get("runtime_review") not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} missing donor: {donor_coordinate}"
                )
            donor_translation = str(donor["translation"])
            if coordinate in target_set:
                if TRANSLATIONS[coordinate] != donor_translation:
                    raise RuntimeError(
                        f"segment {SEGMENT} target donor drifted: {coordinate}"
                    )
                seen_target.add(coordinate)
                assembled.append(TRANSLATIONS[coordinate])
            elif coordinate in companion_set:
                companion = prefill_rows.get(coordinate)
                if (
                    companion is None
                    or companion.get("runtime_review") != "pending"
                    or companion["base_exact_reuse_prefill"][
                        "runtime_promotion_authorized"
                    ]
                    is not False
                    or str(companion["translation"]) != donor_translation
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} prefill companion drifted: "
                        f"{coordinate}"
                    )
                seen_companion.add(coordinate)
                assembled.append(str(companion["translation"]))
            elif coordinate in previous_set:
                previous = prior_rows.get(coordinate)
                if previous and (
                    previous.get("semantic_review") != "approved"
                    or previous.get("runtime_review") != "pending"
                    or str(previous["translation"]) != donor_translation
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} previous companion drifted: "
                        f"{coordinate}"
                    )
                seen_previous.add(coordinate)
                assembled.append(
                    str(previous["translation"])
                    if previous
                    else donor_translation
                )
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} unowned literal: {coordinate}"
                )
            donor_assembled.append(donor_translation)
            donor_rows.append(donor)
        if tuple(assembled) != tuple(donor_assembled):
            raise RuntimeError(
                f"segment {SEGMENT} complete donor assembly drifted: "
                f"{record_id}"
            )
        base_evidence.append(
            (
                record_id,
                sha256_bytes(source.data),
                source_literals,
                current_literals,
                tuple(value.hex().upper() for value in gap_bytes(source)),
                raw_matches,
                literal_matches,
                masked_matches,
                tuple(
                    (
                        str(row["coordinate"]),
                        str(row["translation"]),
                        str(row["semantic_review"]),
                        str(row["runtime_review"]),
                    )
                    for row in donor_rows
                ),
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(assembled),
                tuple(donor_assembled),
                runtime_controls(source),
                runtime_controls(records_by_label["current"][key]),
                "complete_record_reviewed",
                "base_runtime_state_not_inherited",
            )
        )
    if (
        seen_target != target_set
        or seen_companion != companion_set
        or seen_previous != previous_set
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
    base, assembly = base_and_assembly_evidence(prepared, records_by_label)
    BASE.guarded_digest("Base search", base, EXPECTED_BASE_SEARCH_SHA256)
    BASE.guarded_digest(
        "complete assembly",
        assembly,
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source = records_by_label["jp"][(BLOCK_ID, record_id)]
    current = records_by_label["current"][(BLOCK_ID, record_id)]
    source_controls = runtime_controls(source)
    current_controls = runtime_controls(current)
    complete_matches = EXPECTED_BASE_MATCHES[record_id]
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
        "base_complete_record_match_kind": (
            "raw_literal_and_operand_exact"
            if EXPECTED_RAW_BASE_MATCHES[record_id]
            else "literal_and_masked_call_exact"
        ),
        "base_complete_record_coordinates": tuple(
            f"{block_id}:{base_record_id}"
            for block_id, base_record_id in complete_matches
        ),
        "base_semantic_reference_coordinates":
        EXPECTED_BASE_DONOR_COORDINATES[record_id],
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "same_slice_prefill_companion_reviewed":
        any(
            coordinate.startswith(f"7:{record_id}:")
            for coordinate in PREFILL_COMPANION_COORDINATES
        ),
        "previous_slice_companion_reviewed":
        any(
            coordinate.startswith(f"7:{record_id}:")
            for coordinate in PREVIOUS_COMPANION_COORDINATES
        ),
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
        len(replacements) != 66
        or len(prefilled) != 44
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
    if EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS["combined slice candidate"] = candidate_sha256
        DISCOVERED_PINS["combined slice changed count"] = str(changed)
    return candidate_sha256, changed


def install_base_globals() -> None:
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
        "EXPECTED_BASE_MATCHES": EXPECTED_BASE_MATCHES,
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
        "queue_evidence": queue_evidence,
        "assert_context_contracts": assert_context_contracts,
        "assert_base_and_complete_assembly":
        assert_base_and_complete_assembly,
        "runtime_evidence": runtime_evidence,
        "build_combined_slice_candidate": build_combined_slice_candidate,
    }
    for name, value in values.items():
        setattr(BASE, name, value)
    BASE.PARENT.patch_parent_globals = BASE.patch_parent_globals


def build_rows() -> tuple[Any, ...]:
    install_base_globals()
    result = list(BASE.build_rows())
    rows = result[1]
    for row in rows:
        record_id = coordinate_key(str(row["coordinate"]))[1]
        row["manual_complete_base_donor_translation_selected"] = True
        row["manual_semantic_base_references_reviewed"] = True
        row["manual_multilingual_translation_selected"] = False
        row["next_slice_companion_reviewed"] = False
        row["previous_slice_companion_reviewed"] = record_id == 850
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
    counts = Counter(str(row["scope_classification"]) for row in rows)
    if (
        len(rows) != 22
        or len(validated) != 22
        or counts != Counter({"runtime_fragment_pending": 22})
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
        BASE.engine_builder().assert_tamper_rejection(
            prepared,
            rows,
            candidate,
        )
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B056_S1181",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
                "target_coordinate_first": TARGET_COORDINATES[0],
                "target_coordinate_last": TARGET_COORDINATES[-1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 66,
                "exact_reuse_prefill_count": 44,
                "residual_count": len(rows),
                "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
                "same_slice_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "previous_companion_count":
                len(PREVIOUS_COMPANION_COORDINATES),
                "previous_companion_output_present":
                bool(previous_rows(prepared)),
                "complete_base_match_record_count":
                len(EXPECTED_BASE_MATCHES),
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
                "complete_record_assemblies_guarded": True,
                "all_slice_prefills_guarded": True,
                "combined_slice_reverse_order_exact": True,
                "source_redacted": True,
                "reverse_order_overlay_exact": True,
                "reverse_overlay_exact": True,
                "outside_scope_identity_guarded": True,
                "second_run_reproduced": True,
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
