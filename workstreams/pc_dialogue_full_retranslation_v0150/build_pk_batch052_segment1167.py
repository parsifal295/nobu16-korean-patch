#!/usr/bin/env python3
"""Build source-redacted PK B052 segment 1167 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import Counter, deque
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
PARENT_PATH = WORKSTREAM / "build_pk_batch051_segment1166.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B052_S1167.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B052_S1168.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B052_S1169.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1167
QUEUE_BATCH_ID = "pk_msggame-B052"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = ("7:268:1",)
TRANSLATIONS = {"7:268:1": "인가"}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (268,)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {268: 2}
PREFILL_COMPANION_COORDINATES = ("7:268:0",)
EXPECTED_BASE_MATCHES = {268: ((7, 264),)}
EXPECTED_RAW_BASE_MATCHES = {268: ()}
EXPECTED_BASE_DONOR_COORDINATES = {
    268: ("7:264:0", "7:264:1"),
}
BOUNDARY_RECORD_KEYS = (
    (7, 208),
    (7, 209),
    (7, 267),
    (7, 268),
    (7, 269),
    (7, 315),
    (7, 316),
    (7, 366),
    (7, 367),
)
SOURCE_CALL_ROOTS = (1126,)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
BASE_CALL_ROOTS = (1114,)
SPEAKER_STYLE = (
    (268, "loyal_service_acceptance_dynamic_name"),
)
TERMINOLOGY_POLICY = (
    ("serve under", "따르다"),
    ("objection", "이의"),
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
    "5D3A7493802C14398A89156C90727A3E92EB8DD55D526E91AD8F5138BE86688F"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "DFA84983EE58DC89A7245AA627D82A6AF07AB7DF574C4EF2610F21D71A7B51D9"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "C672D46EEF9B35632CE5504F80EC5D8C1F8C23E4ADD6C127AF684780135D721E"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "0D3B65E16E84BB83BEDA2C4858A7C36176B764E860191159E60545FB90BDC3D4"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "5085FB08CF18C60C201CB511A4BDA632C224DD8AA633CEAB7C0C47ADB4E9CD51"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "24ABD31473834D74A5834915985771588CC586229F0FB87160F09F08F667E586"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "0B5E7A7C1ADB3481B9E8C4DAEA0D58F85F79F7FFF01B795F155CCF14C743C629"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "4B6F15B24771274DEC2711E2E1262F5E34AC1F51DF6F5CDBAD27B9AC321C7781"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "E02F22B1B7B6DDBCD823E032FA617C0745C2FB010489C90A5730911E0FBE68E5"
)
EXPECTED_BOUNDARY_SHA256 = (
    "B268E44B44E51FED22EFDAEA90CF615CE410692E1556D286CE29C8B7A93C83CF"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "53371EB41481A6B13926CD24CC3251D48AEC7CF37C047F6301E31498633CCD44"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "9A0AFC5B9C3BB9CCCD019A10A112E2E1FC8B34FC9363E178A7D5220EB2554539"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "BEFAC7372018EE6B0E758B39FF81BD50DDDCF2F459376A9BF553CEEA54F60519"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "AECD2F5280C58D817C62690FB8EBF06965533008FCFC18B8B2CE138ECA5653B0"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "E78F0DB6F8C046E1F9E506E0EA3C572D42705AA38DC2136C57369EE10B300CAF"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "98FBFCE21018C50AE1C99A05D5514C82EA2485D9689D29996407C80FB8515ACD"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "0B5E7A7C1ADB3481B9E8C4DAEA0D58F85F79F7FFF01B795F155CCF14C743C629"
)
EXPECTED_CANDIDATE_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "8DC9CE7374193D29025BB1247039B801FD96344C6A9000A409D0BAADA4D02E6B"
)
EXPECTED_CHANGED_LITERAL_COUNT = 0

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source authoritative; complete PC EN SC TC record and "
    "adjacent context reviewed; the complete PK source record has one "
    "literal-plus-masked-control exact completed Base donor, but the PK "
    "direct call operand 1126 differs from the Base donor operand 1114; "
    "completed Base Korean is therefore used only as manually reviewed "
    "semantic wording for the residual second literal while the first "
    "literal remains the approved Base-prefilled PK companion; all sixty-"
    "six prefills in the sixty-seven-row queue slice are validated and the "
    "combined slice is rebuilt in both orders and reversed byte-exactly; "
    "the dynamic name call, newlines, protected whitespace, full record, "
    "queue and segment boundaries, source/current reachable call graphs, "
    "two-run reproduction, tamper rejection, outside-scope identity and "
    "Steam read-only state are guarded; Base runtime and VM state are not "
    "inherited and the residual remains runtime pending"
)

ALL_CALL_RE = re.compile(b"\x01([\x43\x4A])(.{4})", re.DOTALL)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1167_parent",
        PARENT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {PARENT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PARENT = load_parent()
ORIGINAL_PATCH_PARENT_GLOBALS = PARENT.patch_parent_globals
ENGINE = PARENT.ENGINE
sha256_bytes = PARENT.sha256_bytes
canonical_sha256 = PARENT.canonical_sha256
coordinate_key = PARENT.coordinate_key
literal_texts = PARENT.literal_texts
gap_bytes = PARENT.gap_bytes
read_jsonl = PARENT.read_jsonl
context_records = PARENT.context_records
runtime_controls = PARENT.runtime_controls
mask_call_operands = PARENT.mask_call_operands


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
        len(rows) != 158
        or len(visible) != 200
        or visible[0] != "7:209:0"
        or visible[-1] != "7:366:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B052 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "7:209:0"
        or queue_slice[-1] != "7:268:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    if (
        len(prefilled) != 66
        or tuple(
            coordinate
            for coordinate in queue_slice
            if coordinate not in prefill_rows
        )
        != TARGET_COORDINATES
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


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    values = PARENT.context_evidence(prepared, records_by_label)
    for label, value, expected in (
        ("source target", values["source_target"], EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", values["current_target"], EXPECTED_CURRENT_TARGET_SHA256),
        ("multilingual context", values["corpus"], EXPECTED_CONTEXT_CORPUS_SHA256),
        ("gap contract", values["gaps"], EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", values["boundary"], EXPECTED_BOUNDARY_SHA256),
        ("runtime control", values["controls"], EXPECTED_RUNTIME_CONTROL_SHA256),
    ):
        guarded_digest(label, value, expected)
    expected_controls = (
        ("jp", 268, ((8, 1126), ())),
        ("current", 268, ((8, 1126), ())),
    )
    if (
        any(source != current for _, source, current in values["gaps"])
        or values["controls"] != expected_controls
        or ("pk_msggame", 7, 268, 1) not in prepared.visible_targets
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime layout drifted")


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
    source = records_by_label["jp"][(BLOCK_ID, 268)]
    source_literals = literal_texts(records_by_label["jp"], (BLOCK_ID, 268))
    current_literals = literal_texts(
        records_by_label["current"],
        (BLOCK_ID, 268),
    )
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
        len(source_literals) != 2
        or raw_matches != EXPECTED_RAW_BASE_MATCHES[268]
        or literal_matches != EXPECTED_BASE_MATCHES[268]
        or masked_matches != EXPECTED_BASE_MATCHES[268]
    ):
        raise RuntimeError(f"segment {SEGMENT} Base donor drifted")
    base_key = EXPECTED_BASE_MATCHES[268][0]
    base_controls = runtime_controls(base_source[base_key])
    if (
        runtime_controls(source) != ((8, 1126), ())
        or base_controls != ((8, 1114), ())
    ):
        raise RuntimeError(f"segment {SEGMENT} edition call operand drifted")
    donor_coordinates = EXPECTED_BASE_DONOR_COORDINATES[268]
    donors = tuple(base_rows.get(coordinate) for coordinate in donor_coordinates)
    companion = prefill_rows.get(PREFILL_COMPANION_COORDINATES[0])
    if (
        any(row is None for row in donors)
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] not in {"verified", "not_required"}
            for row in donors
        )
        or companion is None
        or companion["semantic_review"] != "approved"
        or companion["runtime_review"] != "pending"
        or companion["base_exact_reuse_prefill"][
            "runtime_promotion_authorized"
        ]
        is not False
        or companion["base_exact_reuse_prefill"]["base_coordinate"]
        != donor_coordinates[0]
        or str(companion["translation"]) != str(donors[0]["translation"])
        or TRANSLATIONS[TARGET_COORDINATES[0]]
        != str(donors[1]["translation"])
    ):
        raise RuntimeError(f"segment {SEGMENT} Base semantic donor drifted")
    assembled = (
        str(companion["translation"]),
        TRANSLATIONS[TARGET_COORDINATES[0]],
    )
    donor_assembled = tuple(str(row["translation"]) for row in donors)
    if assembled != donor_assembled:
        raise RuntimeError(f"segment {SEGMENT} complete assembly drifted")
    base_evidence = (
        (
            268,
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
                for coordinate, row in zip(donor_coordinates, donors)
            ),
            runtime_controls(source),
            base_controls,
        ),
    )
    assembly_evidence = (
        (
            268,
            ("base_exact_prefill_runtime_pending", "segment_manual"),
            assembled,
            donor_assembled,
            runtime_controls(source),
            runtime_controls(records_by_label["current"][(BLOCK_ID, 268)]),
            base_controls,
            "complete_translation_equals_completed_base_donor",
            "pk_and_base_call_operands_differ",
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


def reachable_call_graph(
    records: dict[tuple[int, int], Any],
    root: tuple[int, int],
) -> tuple[tuple[Any, ...], tuple[tuple[int, int], ...]]:
    pending: deque[tuple[int, int]] = deque([root])
    visited: set[tuple[int, int]] = set()
    edges: list[tuple[Any, ...]] = []
    terminals: list[tuple[int, int]] = []
    while pending:
        coordinate = pending.popleft()
        if coordinate in visited:
            continue
        if coordinate not in records:
            raise RuntimeError(
                f"segment {SEGMENT} missing call target: {coordinate}"
            )
        visited.add(coordinate)
        joined = b"".join(gap_bytes(records[coordinate]))
        next_coordinates: list[tuple[int, int]] = []
        for match in ALL_CALL_RE.finditer(joined):
            operand = int.from_bytes(match.group(2), "little")
            target = (operand // 10_000, operand % 10_000)
            edges.append(
                (
                    coordinate,
                    ("01" + match.group(1).hex()).upper(),
                    operand,
                    target,
                )
            )
            next_coordinates.append(target)
            pending.append(target)
        if not next_coordinates:
            terminals.append(coordinate)
    graph = tuple(
        (
            coordinate,
            sha256_bytes(records[coordinate].data),
            literal_texts(records, coordinate),
            tuple(
                value.hex().upper()
                for value in gap_bytes(records[coordinate])
            ),
        )
        for coordinate in sorted(visited)
    ) + (("edges", tuple(sorted(edges))),)
    return graph, tuple(sorted(terminals))


def call_graph_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[Any, ...]:
    evidence: list[tuple[Any, ...]] = []
    for label, roots in (
        ("jp", SOURCE_CALL_ROOTS),
        ("current", CURRENT_CALL_ROOTS),
    ):
        records = records_by_label[label]
        for operand in roots:
            graph, terminals = reachable_call_graph(records, (0, operand))
            terminal_literals = tuple(
                literal_texts(records, coordinate)
                for coordinate in terminals
            )
            if not graph or not terminals:
                raise RuntimeError(
                    f"segment {SEGMENT} call graph drifted: {label}:{operand}"
                )
            evidence.append(
                (label, operand, graph, terminals, terminal_literals)
            )
    source_graph = evidence[0][2]
    current_graph = evidence[1][2]
    if (
        tuple(row[0] for row in source_graph[:-1])
        != tuple(row[0] for row in current_graph[:-1])
        or source_graph[-1] != current_graph[-1]
        or evidence[0][3] != evidence[1][3]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} source/current call graph shape differs"
        )
    return tuple(evidence)


def assert_call_graphs(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    guarded_digest(
        "call graph",
        call_graph_evidence(records_by_label),
        EXPECTED_CALL_GRAPH_SHA256,
    )


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
        "base_direct_call_operands": (8, 1114),
        "source_current_runtime_gap_equal":
        gap_bytes(source) == gap_bytes(current),
        "base_complete_record_match_kind":
        "literal_and_operand_masked_semantic_only",
        "base_complete_record_coordinate": "7:264",
        "pk_base_call_operands_differ": True,
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "same_record_prefill_companion_reviewed": True,
        "manual_multilingual_context_reviewed": True,
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


def patch_parent_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
        "OPTIONAL_NEIGHBORS": OPTIONAL_NEIGHBORS,
        "STEAM_PK": STEAM_PK,
        "DECISIONS_ROOT": DECISIONS_ROOT,
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
    }
    for name, value in values.items():
        setattr(PARENT, name, value)
    PARENT.queue_evidence = queue_evidence
    PARENT.assert_context_contracts = assert_context_contracts
    PARENT.assert_base_and_complete_assembly = (
        assert_base_and_complete_assembly
    )
    PARENT.assert_call_graphs = assert_call_graphs
    PARENT.build_combined_slice_candidate = build_combined_slice_candidate
    PARENT.runtime_evidence = runtime_evidence
    ORIGINAL_PATCH_PARENT_GLOBALS()


PARENT.patch_parent_globals = patch_parent_globals


def main() -> int:
    patch_parent_globals()
    first = PARENT.build_rows()
    second = PARENT.build_rows()
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
        PARENT.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B052_S1167",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 67,
                "exact_reuse_prefill_count": 66,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "raw_exact_complete_base_donor_record_count": 0,
                "literal_masked_complete_base_donor_record_count": 1,
                "source_call_root_count": len(SOURCE_CALL_ROOTS),
                "current_call_root_count": len(CURRENT_CALL_ROOTS),
                "base_call_root_count": len(BASE_CALL_ROOTS),
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
                "pk_base_call_operands_differ": True,
                "source_current_gap_equality_guarded": True,
                "inline_token_controls_guarded": True,
                "reachable_call_graphs_guarded": True,
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
