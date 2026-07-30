#!/usr/bin/env python3
"""Build source-redacted PK B062 segment 1194 residual decisions."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B062_S1194.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B062_S1193.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B062_S1195.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1194
QUEUE_BATCH_ID = "pk_msggame-B062"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "7:1723:1",
    "7:1726:0",
    "7:1727:1",
    "7:1728:0",
    "7:1730:1",
)
TRANSLATIONS = {
    "7:1723:1": "의 성—",
    "7:1726:0": "의 성—",
    "7:1727:1": "의 성—",
    "7:1728:0": "고작—",
    "7:1730:1": "의 성—",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (1723, 1726, 1727, 1728, 1730)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {1723: 3, 1726: 2, 1727: 3, 1728: 3, 1730: 3}
PREFILL_COMPANION_COORDINATES = (
    "7:1723:0",
    "7:1723:2",
    "7:1726:1",
    "7:1727:0",
    "7:1727:2",
    "7:1728:2",
    "7:1730:0",
    "7:1730:2",
)
INVISIBLE_COMPANION_COORDINATES = ("7:1728:1",)
FUTURE_COMPANION_COORDINATES: tuple[str, ...] = ()
PRIMARY_BASE_MATCH = {
    1723: (7, 1683),
    1726: (7, 1686),
    1727: (7, 1687),
    1728: (7, 1688),
    1730: (7, 1690),
}
EXPECTED_BASE_MATCHES = {
    record_id: (base_coordinate,)
    for record_id, base_coordinate in PRIMARY_BASE_MATCH.items()
}
EXPECTED_RAW_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_LITERAL_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_MASKED_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_BASE_DONOR_COORDINATES = {
    record_id: tuple(
        f"{base_coordinate[0]}:{base_coordinate[1]}:{literal_id}"
        for literal_id in range(EXPECTED_ARITY[record_id])
    )
    for record_id, base_coordinate in PRIMARY_BASE_MATCH.items()
}
BOUNDARY_RECORD_KEYS = (
    (7, 1693),
    (7, 1694),
    (7, 1721),
    (7, 1722),
    (7, 1723),
    (7, 1724),
    (7, 1725),
    (7, 1726),
    (7, 1727),
    (7, 1728),
    (7, 1729),
    (7, 1730),
    (7, 1731),
    (7, 1775),
    (7, 1776),
    (7, 1834),
    (7, 1835),
)
SOURCE_CALL_ROOTS: tuple[int, ...] = ()
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ("025032", "026432"))
    for record_id in TARGET_RECORD_IDS
}
SPEAKER_STYLE = (
    (1723, "strategy_policy_change_attack_proposal"),
    (1726, "castle_attack_timing_advice"),
    (1727, "policy_reversal_attack_pledge"),
    (1728, "castle_capture_boast"),
    (1730, "castle_capture_encouragement"),
)
TERMINOLOGY_POLICY = (
    ("policy", "지침"),
    ("castle", "성"),
    ("attack", "공격"),
    ("capture", "함락"),
    ("merely", "고작—"),
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
    "E9BED04E132FE50D553B932012827D4F754D2B3EA11B253B5D90F7D088BAFB6B"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "9626A1547A0014C164AF9E2F5D3C7E50DE0CCD264A27C51438A9B144BDD4179B"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "C2E4214366F47A5D86BF6E82C679A326C365D0AD65B9102217A732DB59D90BFB"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "858456CCD12DE23E065C052A79C92FBEC12CE9DD8CE87EC656F5503E8F72DD62"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "12008BC6B9CC3917E7D7A0A627094282C7B92EE52E2CA573752ACB37D7265844"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "32C934EA2ADEB1963D1BFA7DF8F338A3A4A85D3CC819A03163AD98E28599484F"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "44AA4389BC8E86C9E11647028C7C45BC7D43715F5FFA6F4A3AB915CA762998CB"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "EF50B0B5E10DE71B1AD8E7E6B7C05C4FB106870AAB8E3B6C4E1CFA93D9DA1B9A"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "90BC8137E536AC92C196B0DFD6D2AE216304ECD196A47C90EC7006124BDBEA03"
)
EXPECTED_BOUNDARY_SHA256 = (
    "2693C7BEFE3658DCA71CDD217AAD83D682B85CF67F99D4265E99A5ED025ECA5E"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "5C02995D2400211CB7A06C311261AB382470E5144B433038A865A8A70F76C217"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "72F59D4956006C48D1AF28541A76B5646B9B02B1918CC20923B8E1B00D140809"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "20B1C0396B3BDA002E7C0AEB4E82A87A0C174875F04880A95D312A493AF44617"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "3172170AC9A9E31FBE8FB4CB1314EB09C725A5EFE5E40805F1C0DEC323192DCB"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "B11283B07A80569C0748531D1512FAA3C56A15073EBA7AF208CDB49CA7F0895F"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "6AE7EE32EDA88EE8F513F371830CC2C8248B4CFA254FB90A48891B0DB9B44C4F"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "62358305FEDC43B0ED82B2DCC76EC963DE1CB9ED4CA24FD95EBCEEEB21EA6485"
)
EXPECTED_CANDIDATE_SHA256 = (
    "A049B611EFF0A41DDE2E4923D04992458286A0D64B5382BC14D2162D77F474FD"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "BF6A755B62DB6EE70E59B3E5D4B118B0408A5A6D4FB824DD8BF9472B7FB95C4D"
)
EXPECTED_CHANGED_LITERAL_COUNT = 5

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source authoritative; complete PC EN SC TC context "
    "was checked and is empty for all five records; every complete PK "
    "source record has one byte-exact completed Base donor, whose final "
    "Korean is used only after manual semantic, terminology and "
    "speaker-register review; target fragments are assembled with eight "
    "approved Base-prefilled companions and one source-identical invisible "
    "newline fragment; all sixty-two prefills in the queue slice are "
    "validated and the sixty-seven-row combined slice is rebuilt in both "
    "orders and reversed byte-exactly; castle and faction tokens, "
    "particles, newlines, protected outer whitespace, complete records, "
    "queue and segment boundaries, two-run reproduction, tamper rejection, "
    "outside-scope identity and Steam read-only state are guarded; Base "
    "runtime and VM state are not inherited and every residual remains "
    "runtime pending"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1194_parent",
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
runtime_controls = PARENT.PARENT.runtime_controls
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
        len(rows) != 141
        or len(visible) != 200
        or visible[0] != "7:1694:0"
        or visible[-1] != "7:1834:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B062 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "7:1722:1"
        or queue_slice[-1] != "7:1775:0"
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
        len(prefilled) != 62
        or len(residual) != 5
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


def future_rows(prepared: Any) -> dict[str, dict[str, Any]]:
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            ENGINE.validate_decisions(prepared, path, require_complete=False)
    return {}


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
    invisible_set = set(INVISIBLE_COMPANION_COORDINATES)
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
            or raw_matches != expected_matches
            or literal_matches != expected_matches
            or masked_matches != expected_matches
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base exact donor drifted: {record_id}"
            )
        assembled: list[str] = []
        donor_assembled: list[str] = []
        donor_evidence: list[tuple[str, str, str, str]] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"7:{record_id}:{literal_id}"
            donor_coordinate = EXPECTED_BASE_DONOR_COORDINATES[
                record_id
            ][literal_id]
            if coordinate in invisible_set:
                if (
                    source_literals[literal_id] != "\n"
                    or current_literals[literal_id] != "\n"
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} invisible companion drifted"
                    )
                translation = "\n"
                donor_translation = "\n"
                seen_invisible.add(coordinate)
                donor_evidence.append(
                    (
                        donor_coordinate,
                        donor_translation,
                        "source_identity",
                        "not_required",
                    )
                )
            else:
                donor = base_rows.get(donor_coordinate)
                if (
                    donor is None
                    or donor.get("semantic_review") != "approved"
                    or donor.get("runtime_review")
                    not in {"verified", "not_required"}
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} missing donor: "
                        f"{donor_coordinate}"
                    )
                donor_translation = str(donor["translation"])
                donor_evidence.append(
                    (
                        donor_coordinate,
                        donor_translation,
                        str(donor["semantic_review"]),
                        str(donor["runtime_review"]),
                    )
                )
                if coordinate in target_set:
                    translation = TRANSLATIONS[coordinate]
                    if translation != donor_translation:
                        raise RuntimeError(
                            f"segment {SEGMENT} target donor drifted: "
                            f"{coordinate}"
                        )
                    seen_target.add(coordinate)
                elif coordinate in companion_set:
                    companion = prefill_rows.get(coordinate)
                    if (
                        companion is None
                        or companion.get("semantic_review") != "approved"
                        or companion.get("runtime_review") != "pending"
                        or companion["base_exact_reuse_prefill"][
                            "runtime_promotion_authorized"
                        ]
                        is not False
                        or str(companion["translation"])
                        != donor_translation
                    ):
                        raise RuntimeError(
                            f"segment {SEGMENT} prefill companion drifted: "
                            f"{coordinate}"
                        )
                    translation = str(companion["translation"])
                    seen_companion.add(coordinate)
                else:
                    raise RuntimeError(
                        f"segment {SEGMENT} unowned literal: {coordinate}"
                    )
            assembled.append(translation)
            donor_assembled.append(donor_translation)
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
                tuple(donor_evidence),
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
        or len(prefilled) != 62
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
    PARENT.build_combined_slice_candidate = build_combined_slice_candidate
    base_module = PARENT.PARENT
    base_module.future_rows = future_rows
    base_module.base_and_assembly_evidence = base_and_assembly_evidence
    base_module.assert_base_and_complete_assembly = (
        assert_base_and_complete_assembly
    )


def build_rows() -> tuple[Any, ...]:
    configure_parent()
    return PARENT.build_rows()


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
        len(rows) != 5
        or len(validated) != 5
        or counts != Counter({"runtime_fragment_pending": 5})
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
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B062_S1194",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "target_coordinate_first": TARGET_COORDINATES[0],
                "target_coordinate_last": TARGET_COORDINATES[-1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 67,
                "exact_reuse_prefill_count": 62,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "same_slice_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "invisible_identity_companion_count":
                len(INVISIBLE_COMPANION_COORDINATES),
                "raw_exact_complete_base_donor_record_count":
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
