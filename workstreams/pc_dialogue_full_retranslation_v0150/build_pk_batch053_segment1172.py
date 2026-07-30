#!/usr/bin/env python3
"""Build source-redacted PK B053 segment 1172 residual decisions."""

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
PARENT_PATH = WORKSTREAM / "build_pk_batch052_segment1169.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B053_S1172.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B053_S1170.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B053_S1171.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1172
QUEUE_BATCH_ID = "pk_msggame-B053"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "7:491:0",
    "7:492:1",
    "7:501:0",
    "7:516:0",
    "7:520:1",
    "7:532:1",
)
TRANSLATIONS = {
    "7:491:0": "이(가) 궤멸",
    "7:492:1": "이(가) 동요",
    "7:501:0": "좋아,",
    "7:516:0": "보라, 「",
    "7:520:1": "!",
    "7:532:1": "을(를) 격파했다!",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (491, 492, 501, 516, 520, 532)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {491: 1, 492: 2, 501: 2, 516: 2, 520: 2, 532: 2}
PREFILL_COMPANION_COORDINATES = (
    "7:492:0",
    "7:501:1",
    "7:516:1",
    "7:520:0",
    "7:532:0",
)
EXPECTED_BASE_MATCHES = {
    491: ((7, 487),),
    492: (),
    501: ((7, 496),),
    516: ((7, 511),),
    520: ((7, 515),),
    532: ((7, 527),),
}
EXPECTED_RAW_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_LITERAL_BASE_MATCHES = {
    491: ((7, 487), (9, 377)),
    492: (),
    501: ((7, 496),),
    516: ((7, 511),),
    520: ((7, 515),),
    532: ((7, 527),),
}
EXPECTED_MASKED_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_BASE_DONOR_COORDINATES = {
    491: ("7:487:0",),
    492: ("7:550:0",),
    501: ("7:496:0", "7:496:1"),
    516: ("7:511:0", "7:511:1"),
    520: ("7:515:0", "7:515:1"),
    532: ("7:527:0", "7:527:1"),
}
BOUNDARY_RECORD_KEYS = (
    (7, 489),
    (7, 490),
    (7, 491),
    (7, 492),
    (7, 493),
    (7, 500),
    (7, 501),
    (7, 502),
    (7, 515),
    (7, 516),
    (7, 517),
    (7, 519),
    (7, 520),
    (7, 521),
    (7, 531),
    (7, 532),
    (7, 533),
    (7, 544),
    (7, 545),
)
SOURCE_CALL_ROOTS: tuple[int, ...] = ()
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
SPEAKER_STYLE = (
    (491, "battle_unit_destroyed_notice"),
    (492, "battle_destruction_morale_notice"),
    (501, "veteran_battle_victory_dynamic_unit"),
    (516, "veteran_battle_victory_dynamic_unit"),
    (520, "rough_battle_victory_dynamic_unit"),
    (532, "warrior_battle_victory_dynamic_unit"),
)
TERMINOLOGY_POLICY = (
    ("destroyed", "궤멸"),
    ("agitated", "동요"),
    ("martial prowess", "무용"),
    ("defeated", "격파"),
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
    "9C86F55F5B2D0937D5297CFC1C9859D7B1ED59FC0C2F166348C7A457A78DB982"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "AAE4BA17153320B295FCBB06C26F7208750851BDFBF6434B10B0943D10DB1D09"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "42D7314EE926E026FB37EAB0647AD571265F6A7BF9ADFB8D7F1B62F87CC2E9BC"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "5F7AC14926256152609E4232F9D88AD93BEE198BFCAAF131CA87F1D1B0DE9658"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "D4C4B7E95AA8424375FA884D6D02F00A54F6B78BCBB126F13BAA87575A5B103B"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "4CD19FED71FA8E524636EBCD295E9E05573AA978075EE9DE4A70E175A446E1AD"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "77E9F5E364B3DC8BF3997B059905F8EDB22A4CF10966DF0CADD390B2140ABA0B"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "2525B9875E782924D88AE8290C3C33C09C91F0E58C2F6CBC9F72C2DEF484416E"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "CDC5DFB9E51EF6EEE66FB1019AC071E3B6C9855FE312DAD6D94BBD263205A025"
)
EXPECTED_BOUNDARY_SHA256 = (
    "03C7966F376A369536586E7DA19A767AFCA6D13B61B2632C06AEEA9F58041B9A"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "72164764528B1B64A554A467023C60CE5F27408E416B28C3BE752C2A12803D08"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "D660845525418EDCE17FAE66C12C8012D2C2AAC82A6A42EFDCD42A34C3E2D1B1"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "E1C693467454677CE6E4B24B9C0A4F94C9C5BB8922255F5BD84AA9520A1FFE82"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "CF739FEB7D4886747164AC09A5F5E5D6FA2986B1D2E1D8ECDC7058682DDC816D"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "B557A06B35CC0CBB463777D6218E279097067FFD1B92A3B4B0B9AF58715D6B8D"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "CD2542FFE41E10C875599B8123242E59B98EA2DD9675B35F9CC2851FEF25655E"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "96677773F85818336F335714D8E5D38F0DAFDCD778F6120E26F772133636DD2E"
)
EXPECTED_CANDIDATE_SHA256 = (
    "C91006D4BDB9AFEFCD628C9BBFAF9B247063046E01AF81A497E6678C246A56F1"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "0EAE2C596FF749B791E983EEB34155969EACD6D94CFD8D0231F9E6A3DE7C47AF"
)
EXPECTED_CHANGED_LITERAL_COUNT = 4

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source authoritative; complete PC EN SC TC records "
    "reviewed; five complete source records have byte-exact completed Base "
    "donors and their Korean wording is manually selected; the remaining "
    "two-literal morale notice has no complete or target-literal Base "
    "match, so its second literal is manually retained after multilingual "
    "review while its first literal uses a separately completed Base "
    "donor; all five same-record prefilled companions and all sixty Base "
    "prefills in the queue slice are reviewed; complete dynamic unit-name "
    "assemblies, particles, paired quotes, full-width spacing, punctuation, "
    "newlines, calls, inline tokens, protected whitespace, boundaries, "
    "two-run reproduction, tamper rejection, reverse overlays, outside-"
    "scope identity and Steam read-only state are guarded; Base runtime "
    "and VM state are not inherited and every residual remains runtime "
    "pending"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1172_parent",
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
        len(rows) != 178
        or len(visible) != 200
        or visible[0] != "7:367:0"
        or visible[-1] != "7:544:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B053 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "7:490:0"
        or queue_slice[-1] != "7:544:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    if (
        len(prefilled) != 60
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
    values = PARENT.PARENT.context_evidence(prepared, records_by_label)
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
        ("jp", 491, ((), ("026E32",))),
        ("jp", 492, ((), ("026E32", "026432"))),
        ("jp", 501, ((), ("026E32",))),
        ("jp", 516, ((), ("026E32",))),
        ("jp", 520, ((), ("026E32",))),
        ("jp", 532, ((), ("026E32",))),
        ("current", 491, ((), ("026E32",))),
        ("current", 492, ((), ("026E32", "026432"))),
        ("current", 501, ((), ("026E32",))),
        ("current", 516, ((), ("026E32",))),
        ("current", 520, ((), ("026E32",))),
        ("current", 532, ((), ("026E32",))),
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
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
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
        if record_id == 492:
            first = prefill_rows.get("7:492:0")
            first_donor = base_rows.get("7:550:0")
            target_base_literal_hits = tuple(
                f"{base_key[0]}:{base_key[1]}:{literal_id}"
                for base_key in base_source
                for literal_id, text in enumerate(
                    literal_texts(base_source, base_key)
                )
                if text == source_literals[1]
            )
            if (
                first is None
                or first_donor is None
                or first["base_exact_reuse_prefill"]["base_coordinate"]
                != "7:550:0"
                or str(first["translation"])
                != str(first_donor["translation"])
                or target_base_literal_hits
                or TRANSLATIONS["7:492:1"] != current_literals[1]
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} partial Base context drifted"
                )
            seen_companion.add("7:492:0")
            seen_target.add("7:492:1")
            assembled.extend(
                (str(first["translation"]), TRANSLATIONS["7:492:1"])
            )
            donor_assembled.extend(
                (str(first_donor["translation"]), "manual_multilingual")
            )
            donor_rows.append(first_donor)
        else:
            base_key = EXPECTED_BASE_MATCHES[record_id][0]
            for literal_id in range(EXPECTED_ARITY[record_id]):
                coordinate = f"{BLOCK_ID}:{record_id}:{literal_id}"
                donor_coordinate = (
                    f"{base_key[0]}:{base_key[1]}:{literal_id}"
                )
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
                if coordinate in target_set:
                    if TRANSLATIONS[coordinate] != str(donor["translation"]):
                        raise RuntimeError(
                            f"segment {SEGMENT} target donor drifted: "
                            f"{coordinate}"
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
                else:
                    raise RuntimeError(
                        f"segment {SEGMENT} unowned literal: {coordinate}"
                    )
                donor_assembled.append(str(donor["translation"]))
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
    if seen_target != target_set or seen_companion != companion_set:
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
        "base_complete_record_match_kind":
        "raw_exact" if complete_matches else "none",
        "base_complete_record_coordinates": tuple(
            f"{block_id}:{base_record_id}"
            for block_id, base_record_id in complete_matches
        ),
        "base_partial_context_coordinates":
        EXPECTED_BASE_DONOR_COORDINATES[record_id],
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "same_record_prefill_companion_reviewed":
        record_id != 491,
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
    PARENT.runtime_evidence = runtime_evidence
    PARENT.build_combined_slice_candidate = build_combined_slice_candidate
    ORIGINAL_PATCH_PARENT_GLOBALS()
    PARENT.PARENT.runtime_evidence = runtime_evidence


PARENT.patch_parent_globals = patch_parent_globals


def build_rows() -> tuple[Any, ...]:
    patch_parent_globals()
    result = list(PARENT.PARENT.build_rows())
    rows = result[1]
    for row in rows:
        record_id = coordinate_key(str(row["coordinate"]))[1]
        has_complete_donor = bool(EXPECTED_BASE_MATCHES[record_id])
        row["manual_complete_base_donor_translation_selected"] = (
            has_complete_donor
        )
        row["manual_partial_base_context_reviewed"] = (
            not has_complete_donor
        )
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
        len(rows) != 6
        or len(validated) != 6
        or counts != Counter({"runtime_fragment_pending": 6})
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
        PARENT.PARENT.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B053_S1172",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 66,
                "exact_reuse_prefill_count": 60,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "raw_exact_complete_base_donor_record_count":
                sum(bool(value) for value in EXPECTED_RAW_BASE_MATCHES.values()),
                "no_complete_base_match_record_count":
                sum(not value for value in EXPECTED_BASE_MATCHES.values()),
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
