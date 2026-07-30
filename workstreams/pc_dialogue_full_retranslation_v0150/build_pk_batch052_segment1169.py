#!/usr/bin/env python3
"""Build source-redacted PK B052 segment 1169 residual decisions."""

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
PARENT_PATH = WORKSTREAM / "build_pk_batch051_segment1166.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B052_S1169.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B052_S1167.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B052_S1168.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1169
QUEUE_BATCH_ID = "pk_msggame-B052"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "7:325:1",
    "7:327:0",
    "7:329:0",
    "7:333:0",
    "7:335:2",
    "7:336:0",
    "7:338:0",
)
TRANSLATIONS = {
    "7:325:1": "에게",
    "7:327:0": "거절하",
    "7:329:0": "거절하",
    "7:333:0": "아무리 그래도 「",
    "7:335:2": "……",
    "7:336:0": "면목이",
    "7:338:0": "을(를) 비롯한 총",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (325, 327, 329, 333, 335, 336, 338)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    325: 3,
    327: 2,
    329: 3,
    333: 2,
    335: 3,
    336: 2,
    338: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "7:325:0",
    "7:325:2",
    "7:327:1",
    "7:329:2",
    "7:333:1",
    "7:335:0",
    "7:335:1",
    "7:336:1",
    "7:338:1",
)
INVISIBLE_CURRENT_COORDINATES = ("7:329:1",)
EXPECTED_BASE_MATCHES = {
    325: ((7, 321),),
    327: ((7, 323),),
    329: ((7, 325),),
    333: ((7, 329),),
    335: ((7, 331),),
    336: ((7, 332),),
    338: ((7, 334),),
}
EXPECTED_RAW_BASE_MATCHES = {
    325: ((7, 321),),
    327: (),
    329: (),
    333: (),
    335: (),
    336: (),
    338: ((7, 334),),
}
EXPECTED_BASE_DONOR_COORDINATES = {
    325: ("7:321:0", "7:321:1", "7:321:2"),
    327: ("7:323:0", "7:323:1"),
    329: ("7:325:0", "7:325:2"),
    333: ("7:329:0", "7:329:1"),
    335: ("7:331:0", "7:331:1", "7:331:2"),
    336: ("7:332:0", "7:332:1"),
    338: ("7:334:0", "7:334:1"),
}
BOUNDARY_RECORD_KEYS = (
    (7, 315),
    (7, 316),
    (7, 324),
    (7, 325),
    (7, 326),
    (7, 327),
    (7, 328),
    (7, 329),
    (7, 330),
    (7, 332),
    (7, 333),
    (7, 334),
    (7, 335),
    (7, 336),
    (7, 337),
    (7, 338),
    (7, 339),
    (7, 366),
    (7, 367),
)
SOURCE_CALL_ROOTS = (
    1,
    20,
    160,
    466,
    742,
    748,
    1073,
    1091,
    1096,
    1168,
)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
SPEAKER_STYLE = (
    (325, "hostile_recruitment_refusal_dynamic_name"),
    (327, "hostile_recruitment_refusal_accusation"),
    (329, "hostile_recruitment_refusal_dynamic_name"),
    (333, "proud_recruitment_refusal_dynamic_name"),
    (335, "courteous_recruitment_refusal"),
    (336, "bereaved_recruitment_refusal"),
    (338, "group_recruitment_failure_count"),
)
TERMINOLOGY_POLICY = (
    ("serve", "섬기다"),
    ("submit", "귀순하다"),
    ("main house", "주가"),
    ("employment", "등용"),
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
    "38DEBDA30048ECB7752EE59F5C25BE9408363A1D65677AE34EE14C3C4CBA2DCC"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "7CA0609F8564663AF210186E1D1A930AF931ABA2DDED08A40048CDDCB3ECAF9F"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "E4B411E1587278FC4EAD6504F4ABFCDB5AF02B4829D029491EF39FB2CED32500"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "A1DD5CD8656A9D3A746B1427F30D52287CC34DD8BE855BE805FEABAF207F623B"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "2D01154CFF4E5FFD0A19786AFBF9D25F334514DBED7E3BFE64664EDABEAD897D"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "9D4B1FF3AF905B9136CDAA54B1C6BDA4248FB8088C96BA75312DEABAD9D12293"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "4B6F15B24771274DEC2711E2E1262F5E34AC1F51DF6F5CDBAD27B9AC321C7781"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "3E839B15DBCB047CE156B26474D13A46C224194BE993445FAFDA1A4C444B2D66"
)
EXPECTED_BOUNDARY_SHA256 = (
    "1B160860C66F10A44EC09725B7F0A95BFFC852938211BECE0EF89566294372CF"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "A2325B8A7F390CC1C3E3F1B85514A67316418DF9DFD12196EF9686DFD49B879C"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "24E04AA7F3ACA339B1DF8E7B90BF33368D1122AC20D355DD7BE6C30DE4D9C753"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "E6ABCC8273DE410980BDF8E554196A6FC2EE459135C9C1B86D11AD1833460AC0"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "E7311E91DAEFA1C357A91C8208EF363CCD481C3FA9D7E72B1021D8C9931DC46D"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "3E9466A2D0864E6AA8E1C37FE8EF8E98AA60C58EF5E57BCBBE7AB62094C219C1"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "0DB034E6B456455EC29EB71245D13876ACE545D72C3703BB0AF7FA905695726D"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "10184E8DF1FC6ACCD80D28831BDEBB9711136735AACE140CE1BB75A81704C0CE"
)
EXPECTED_CANDIDATE_SHA256 = (
    "0140C00B4CA96957B2415C0B1B09FB4D11C606678159BE0E8B1EC66399027648"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "4FAD535D2A6A1F28237520F0A122A1A9FF777F025042DEB8DFA48033244FB6CA"
)
EXPECTED_CHANGED_LITERAL_COUNT = 7

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source authoritative; complete PC EN SC TC records "
    "reviewed; each complete PK source record was compared against the "
    "completed Base corpus; two records have byte-exact Base donors and "
    "five have literal-plus-masked-control exact Base donors whose call "
    "operands differ only by edition address; completed Base Korean is "
    "manually selected for the seven residual literals while all nine "
    "same-record prefilled companions and the one invisible newline "
    "literal are reviewed as complete assemblies; all fifty-nine Base "
    "prefills in the queue slice are validated and the sixty-six-row "
    "combined slice is rebuilt in both orders and reversed byte-exactly; "
    "dynamic names, particles, paired quotes, ellipsis, newlines, calls, "
    "inline tokens, protected whitespace, record boundaries, two-run "
    "reproduction, tamper rejection, outside-scope identity and Steam "
    "read-only state are guarded; Base runtime and VM state are not "
    "inherited and every residual remains runtime pending"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1169_parent",
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
        len(queue_slice) != 66
        or queue_slice[0] != "7:316:0"
        or queue_slice[-1] != "7:366:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    if (
        len(prefilled) != 59
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
        ("jp", 325, ((20, 1), ())),
        ("jp", 327, ((1091, 1073), ())),
        ("jp", 329, ((1091, 1091), ("025032",))),
        ("jp", 333, ((748,), ("025032",))),
        ("jp", 335, ((1168, 466, 1096), ())),
        ("jp", 336, ((742, 160), ())),
        ("jp", 338, ((), ("024633", "0232"))),
        ("current", 325, ((20, 1), ())),
        ("current", 327, ((1091, 1073), ())),
        ("current", 329, ((1091, 1091), ("025032",))),
        ("current", 333, ((748,), ("025032",))),
        ("current", 335, ((1168, 466, 1096), ())),
        ("current", 336, ((742, 160), ())),
        ("current", 338, ((), ("024633", "0232"))),
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
    target_set = set(TARGET_COORDINATES)
    companion_set = set(PREFILL_COMPANION_COORDINATES)
    invisible_set = set(INVISIBLE_CURRENT_COORDINATES)
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    seen_invisible: set[str] = set()
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
        expected_matches = EXPECTED_BASE_MATCHES[record_id]
        if (
            len(source_literals) != EXPECTED_ARITY[record_id]
            or raw_matches != EXPECTED_RAW_BASE_MATCHES[record_id]
            or literal_matches != expected_matches
            or masked_matches != expected_matches
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base donor drifted: {record_id}"
            )
        base_key = expected_matches[0]
        donor_coordinates = EXPECTED_BASE_DONOR_COORDINATES[record_id]
        donor_rows: list[dict[str, Any]] = []
        assembled: list[str] = []
        donor_assembled: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"{BLOCK_ID}:{record_id}:{literal_id}"
            donor_coordinate = f"{base_key[0]}:{base_key[1]}:{literal_id}"
            donor = base_rows.get(donor_coordinate)
            if coordinate in target_set:
                if (
                    donor is None
                    or donor.get("semantic_review") != "approved"
                    or donor.get("runtime_review")
                    not in {"verified", "not_required"}
                    or TRANSLATIONS[coordinate]
                    != str(donor["translation"])
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} target donor drifted: "
                        f"{coordinate}"
                    )
                seen_target.add(coordinate)
                assembled.append(TRANSLATIONS[coordinate])
                donor_assembled.append(str(donor["translation"]))
                donor_rows.append(donor)
            elif coordinate in companion_set:
                companion = prefill_rows.get(coordinate)
                if (
                    companion is None
                    or donor is None
                    or companion.get("semantic_review") != "approved"
                    or companion.get("runtime_review") != "pending"
                    or companion["base_exact_reuse_prefill"][
                        "runtime_promotion_authorized"
                    ]
                    is not False
                    or companion["base_exact_reuse_prefill"][
                        "base_coordinate"
                    ]
                    != donor_coordinate
                    or str(companion["translation"])
                    != str(donor["translation"])
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} companion donor drifted: "
                        f"{coordinate}"
                    )
                seen_companion.add(coordinate)
                assembled.append(str(companion["translation"]))
                donor_assembled.append(str(donor["translation"]))
                donor_rows.append(donor)
            elif coordinate in invisible_set:
                if (
                    donor is not None
                    or current_literals[literal_id] != source_literals[literal_id]
                    or current_literals[literal_id].strip()
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} invisible literal drifted: "
                        f"{coordinate}"
                    )
                seen_invisible.add(coordinate)
                assembled.append(current_literals[literal_id])
                donor_assembled.append(
                    literal_texts(base_source, base_key)[literal_id]
                )
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} unowned assembly literal: "
                    f"{coordinate}"
                )
        if tuple(assembled) != tuple(donor_assembled):
            raise RuntimeError(
                f"segment {SEGMENT} complete assembly drifted: {record_id}"
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
                "complete_translation_equals_completed_base_donor",
                "base_runtime_state_not_inherited",
            )
        )
    if (
        seen_target != target_set
        or seen_companion != companion_set
        or seen_invisible != invisible_set
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
    if any(
        runtime_controls(records_by_label["jp"][(BLOCK_ID, record_id)])[0]
        != runtime_controls(
            records_by_label["current"][(BLOCK_ID, record_id)]
        )[0]
        for record_id in TARGET_RECORD_IDS
    ):
        raise RuntimeError(f"segment {SEGMENT} source/current call drifted")
    return evidence


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
        len(replacements) != 66
        or len(prefilled) != 59
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


def patch_parent_globals() -> None:
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
                "segment": "pk_msggame_B052_S1169",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 66,
                "exact_reuse_prefill_count": 59,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "invisible_current_companion_count":
                len(INVISIBLE_CURRENT_COORDINATES),
                "raw_exact_complete_base_donor_record_count":
                sum(bool(value) for value in EXPECTED_RAW_BASE_MATCHES.values()),
                "literal_masked_complete_base_donor_record_count":
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
