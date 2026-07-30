#!/usr/bin/env python3
"""Build source-redacted mixed-block PK B101 segment 1308 decisions."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import build_pk_batch100_segment1306 as MIXED


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B101_S1308.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B101_S1307.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B101_S1309.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1308
SEGMENT_NAME = "pk_msggame_B101_S1308"
QUEUE_BATCH_ID = "pk_msggame-B101"
QUEUE_START = 67
QUEUE_STOP = 134
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "12:60:3",
    "12:61:1",
    "12:61:2",
    "12:61:5",
    "12:62:0",
    "12:62:1",
    "12:62:3",
    "12:63:0",
    "12:63:1",
    "12:64:1",
    "12:65:1",
    "12:66:1",
    "12:67:1",
    "13:21:0",
)
TRANSLATIONS = {
    "12:60:3": "!",
    "12:61:1": "!\n",
    "12:61:2": "규슈",
    "12:61:5": "!",
    "12:62:0": "이 ",
    "12:62:1": "진제이",
    "12:62:3": "!",
    "12:63:0": "이(가)",
    "12:63:1": "(으)로 개명",
    "12:64:1": "들",
    "12:65:1": "(병력",
    "12:66:1": "들",
    "12:67:1": "(병력",
    "13:21:0": "예!",
}
TARGET_RECORD_KEYS = (
    (12, 60),
    (12, 61),
    (12, 62),
    (12, 63),
    (12, 64),
    (12, 65),
    (12, 66),
    (12, 67),
    (13, 21),
)
STATIC_RECORD_KEYS = {(13, 21)}
STATIC_COORDINATES = {"13:21:0"}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
EXPECTED_ARITY = {
    (12, 60): 4,
    (12, 61): 6,
    (12, 62): 4,
    (12, 63): 2,
    (12, 64): 6,
    (12, 65): 5,
    (12, 66): 4,
    (12, 67): 3,
    (13, 21): 1,
}
CROSS_SEGMENT_COMPANION_COORDINATES = ("12:60:1",)
MANUAL_CROSS_SEGMENT_TRANSLATIONS = {
    "12:60:1": "시코쿠",
}
PREFILL_COMPANION_COORDINATES = (
    "12:60:0",
    "12:60:2",
    "12:61:0",
    "12:61:3",
    "12:61:4",
    "12:62:2",
    "12:64:0",
    "12:64:2",
    "12:64:3",
    "12:64:4",
    "12:64:5",
    "12:65:0",
    "12:65:2",
    "12:65:3",
    "12:65:4",
    "12:66:0",
    "12:66:2",
    "12:66:3",
    "12:67:0",
    "12:67:2",
)
PREFILL_COMPANION_DONOR = {
    "12:60:0": "12:60:0",
    "12:60:2": "12:60:2",
    "12:61:0": "12:45:0",
    "12:61:3": "12:45:3",
    "12:61:4": "12:61:4",
    "12:62:2": "12:62:2",
    "12:64:0": "12:64:0",
    "12:64:2": "12:64:2",
    "12:64:3": "12:64:3",
    "12:64:4": "12:64:2",
    "12:64:5": "12:64:5",
    "12:65:0": "12:65:0",
    "12:65:2": "12:65:2",
    "12:65:3": "12:65:3",
    "12:65:4": "12:65:4",
    "12:66:0": "12:66:0",
    "12:66:2": "12:66:2",
    "12:66:3": "12:66:3",
    "12:67:0": "12:67:0",
    "12:67:2": "12:67:2",
}
PREFILL_COMPANION_RUNTIME_REVIEW = {
    coordinate: (
        "not_required"
        if coordinate.startswith(("12:60:", "12:61:", "12:62:"))
        else "pending"
    )
    for coordinate in PREFILL_COMPANION_COORDINATES
}
EXACT_BASE_RECORD_KEYS = set(TARGET_RECORD_KEYS)
EXPECTED_BASE_RAW_MATCHES = {
    (12, 60): (),
    (12, 61): (),
    (12, 62): (),
    (12, 63): ((12, 63),),
    (12, 64): ((12, 64),),
    (12, 65): ((12, 65),),
    (12, 66): ((12, 66),),
    (12, 67): ((12, 67),),
    (13, 21): ((13, 21),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    key: (key,) for key in TARGET_RECORD_KEYS
}
EXPECTED_BASE_MASKED_MATCHES = {
    key: (key,) for key in TARGET_RECORD_KEYS
}
RECORD_BASE_CONTEXT = {
    key: tuple(
        f"{key[0]}:{key[1]}:{literal_id}"
        for literal_id in range(EXPECTED_ARITY[key])
    )
    for key in TARGET_RECORD_KEYS
}
BOUNDARY_RECORD_KEYS = tuple(
    (12, record_id) for record_id in range(59, 69)
) + (
    (13, 20),
    (13, 21),
    (13, 22),
)
SOURCE_CALL_ROOTS = (376, 520, 538, 586)
CURRENT_CALL_ROOTS: tuple[int, ...] = ()
EXPECTED_CONTROLS = {
    (12, 60): (((586,), ()), ((), ())),
    (12, 61): (((376, 538, 520), ()), ((), ())),
    (12, 62): (((586,), ()), ((), ())),
    (12, 63): (((), ("023C", "023D")), ((), ("023C", "023D"))),
    (12, 64): (
        ((), ("0232", "0233", "0234", "0235")),
        ((), ("0232", "0233", "0234", "0235")),
    ),
    (12, 65): (
        ((), ("0233", "0234", "0235")),
        ((), ("0233", "0234", "0235")),
    ),
    (12, 66): (
        ((), ("0232", "0233")),
        ((), ("0232", "0233")),
    ),
    (12, 67): (((), ("0233",)), ((), ("0233",))),
    (13, 21): (((), ()), ((), ())),
}
EXPECTED_SOURCE_CURRENT_GAP_EQUALITY = {
    key: key not in {(12, 60), (12, 61), (12, 62)}
    for key in TARGET_RECORD_KEYS
}
SPEAKER_STYLE = (
    ((12, 60), "lord_regional_peace_acknowledgment"),
    ((12, 61), "formal_regional_congratulation"),
    ((12, 62), "lord_regional_peace_acknowledgment"),
    ((12, 63), "runtime_force_rename_notification"),
    ((12, 64), "runtime_multi_unit_return_confirmation"),
    ((12, 65), "runtime_single_unit_return_confirmation"),
    ((12, 66), "runtime_multi_unit_return_notification"),
    ((12, 67), "runtime_single_unit_return_notification"),
    ((13, 21), "formal_short_acknowledgment"),
)
TERMINOLOGY_POLICY = (
    ("western island region", "시코쿠"),
    ("southern island region", "규슈"),
    ("historical western-defense region", "진제이"),
    ("unprecedented achievement", "전무후무한 쾌거"),
    ("dynamic subject particle", "이(가)"),
    ("dynamic directional particle", "(으)로"),
    ("unit strength", "병력"),
    ("return", "귀환"),
    ("project ellipsis", "…"),
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
    "3C022919301136691B49E8999449960DDCC09A8E816D6BA0E3AA912E603BD7AA"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "E2D8747EE2621044D51310DD33C68BC4DC7822F2DA3367B6C99D0EEBBAF46241"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "1D13CBD065198BD8DF6E94589445DD8E04C1CD50E871E682178B1CF5F966B7D9"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "31DDD9D90E02947073F6CFB9692A1990EA6446D5688EA14B64DFECCC07638AA0"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "C158408714202DA332A53BABBC2CCB0AB34A1A9C85E5447F42FF12DE0B417B8B"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "16A85E7E88FA14A8876EBBF2C30FC900972F73A8E8801108D243AE4F16D565D3"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "02532B1D0473E0C224F32C2F91DD2C78C2B618B8279DE7AC5199BB49806E74AD"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "7E19C89B117A62F83E1014F716BF21A032C6EE7C6428DE88714627BE51A00F07"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "E7BB7A3E9B53BEA9DB057938BA520EF509D8999BDBAB0F4436F43DBAA0618247"
)
EXPECTED_BOUNDARY_SHA256 = (
    "763D74F168E83B219F904BED09207372EDEEC20BAC8BBF026A4821236AEA3D28"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "5EE42CE824AB2E09CA3609A98BB9427BC9CC23CFFCF6C3FCD6F26E9559BA8899"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "7A9668DB768C9CF27C187C826B4872CBAABD477ADC5B6EBCECE6E5509AAE92A0"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "653F34B963DE0E393B8AD40D0BCFEDB469B2BF08234FA4504523F0FACBA71CC0"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "B4EE8E863D3DCC76F5E862609616C5138249401118B949F025405A1470039FFF"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "AFC2BF1F802686D6114BE24858DDDAB0FC65F6220639315FAE3367D367B58755"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "7F046765237436235E53B021B7C990AC46D83687CA114B2B49098DB03D819FA4"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "0ED9EFCA613C7610DB3FDC47EA61CC69A7AD447B13FF0457F4B5D9687FA2B9D0"
)
EXPECTED_CANDIDATE_SHA256 = (
    "B25EB16DBD6F6DC43F63390DB75AF5096F79F2FFBC6DAA732D98C71F3AF09C81"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "1734A8BC59632B70DF35C58D368A99BE6B0F566FCEF9BC65438D33216903E698"
)
EXPECTED_CHANGED_LITERAL_COUNT = 7
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 45

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese is authoritative and every populated English, "
    "Simplified Chinese and Traditional Chinese same-record context was "
    "reviewed; all nine complete mixed-block records have approved completed "
    "Base donors at the identical coordinates, whose Korean is reused only "
    "as semantic content while PK bytecode, calls and inline tokens remain "
    "authoritative; Base runtime and VM state are never inherited; one "
    "approved S1307 boundary companion and twenty approved exact-prefill "
    "companions complete every record, with both S1307 and S1309 outputs "
    "required to be present and validated; region names, dynamic particles, "
    "unit-return terminology, outer spaces, line counts, color gaps, calls, "
    "tokens, literal arity and terminators are preserved; all pins, two-run "
    "reproduction, tamper rejection, call graphs, reverse overlays, "
    "outside-scope identity and Steam read-only state are guarded"
)

BASE = MIXED.BASE
ENGINE = MIXED.ENGINE
sha256_bytes = MIXED.sha256_bytes
canonical_sha256 = MIXED.canonical_sha256
coordinate_key = MIXED.coordinate_key
literal_texts = MIXED.literal_texts
gap_bytes = MIXED.gap_bytes
read_jsonl = MIXED.read_jsonl
context_records = MIXED.context_records
runtime_controls = MIXED.runtime_controls
mask_call_operands = MIXED.mask_call_operands


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


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
        len(rows) != 117
        or len(visible) != 200
        or visible[0] != "12:46:0"
        or visible[-1] != "13:98:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B101 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "12:60:2"
        or queue_slice[-1] != "13:44:0"
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
    if len(prefilled) != 53 or residual != TARGET_COORDINATES:
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
        tuple(
            int(value)
            for value in str(row["record_coordinate"]).split(":")
        )
        for row in rows
    )
    return visible, queue_slice, prefilled, prefill_context, record_keys


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    values = BASE.context_evidence(prepared, records_by_label)
    for label, value, expected in (
        ("source target", values["source_target"],
         EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", values["current_target"],
         EXPECTED_CURRENT_TARGET_SHA256),
        ("multilingual context", values["corpus"],
         EXPECTED_CONTEXT_CORPUS_SHA256),
        ("gap contract", values["gaps"], EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", values["boundary"], EXPECTED_BOUNDARY_SHA256),
        ("runtime control", values["controls"],
         EXPECTED_RUNTIME_CONTROL_SHA256),
    ):
        guarded_digest(label, value, expected)
    expected_controls = tuple(
        (
            label,
            key,
            EXPECTED_CONTROLS[key][0 if label == "jp" else 1],
        )
        for label in ("jp", "current")
        for key in TARGET_RECORD_KEYS
    )
    flattened_are_exact = all(
        (
            source == current
            if EXPECTED_SOURCE_CURRENT_GAP_EQUALITY[key]
            else (
                source != current
                and tuple(
                    ""
                    if gap.startswith("0143") and len(gap) == 12
                    else gap
                    for gap in source
                )
                == current
            )
        )
        for key, source, current in values["gaps"]
    )
    if (
        values["controls"] != expected_controls
        or not flattened_are_exact
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
    neighbor_rows: dict[str, dict[str, Any]] = {}
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            for row in read_jsonl(path):
                neighbor_rows[str(row["coordinate"])] = row
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_cross: set[str] = set()
    seen_prefill: set[str] = set()
    for key in TARGET_RECORD_KEYS:
        source = records_by_label["jp"][key]
        current = records_by_label["current"][key]
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
            len(source_literals) != EXPECTED_ARITY[key]
            or raw_matches != EXPECTED_BASE_RAW_MATCHES[key]
            or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[key]
            or masked_matches != EXPECTED_BASE_MASKED_MATCHES[key]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base search drifted: {key}"
            )
        context_rows: list[tuple[Any, ...]] = []
        for reference in RECORD_BASE_CONTEXT[key]:
            row = base_rows.get(reference)
            if (
                row is None
                or row.get("semantic_review") != "approved"
                or row.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} missing Base context: {reference}"
                )
            context_rows.append((
                reference,
                str(row["translation"]),
                str(row["semantic_review"]),
                str(row["runtime_review"]),
                "semantic_only",
                "runtime_vm_not_inherited",
            ))
        owners: list[str] = []
        assembled: list[str] = []
        literal_evidence: list[tuple[Any, ...]] = []
        for literal_id in range(EXPECTED_ARITY[key]):
            coordinate = f"{key[0]}:{key[1]}:{literal_id}"
            if coordinate in TRANSLATIONS:
                translation = TRANSLATIONS[coordinate]
                owner = "segment_exact_base_semantic_reuse"
                seen_target.add(coordinate)
            elif coordinate in CROSS_SEGMENT_COMPANION_COORDINATES:
                translation = MANUAL_CROSS_SEGMENT_TRANSLATIONS[coordinate]
                neighbor = neighbor_rows.get(coordinate)
                if (
                    neighbor is None
                    or neighbor.get("semantic_review") != "approved"
                    or neighbor.get("runtime_review") != "pending"
                    or str(neighbor.get("translation")) != translation
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} neighbor companion drifted: "
                        f"{coordinate}"
                    )
                owner = "s1307_verified_companion"
                seen_cross.add(coordinate)
            elif coordinate in PREFILL_COMPANION_COORDINATES:
                companion = prefill_rows.get(coordinate)
                if (
                    companion is None
                    or companion.get("semantic_review") != "approved"
                    or companion.get("runtime_review")
                    != PREFILL_COMPANION_RUNTIME_REVIEW[coordinate]
                    or companion["base_exact_reuse_prefill"][
                        "runtime_promotion_authorized"
                    ]
                    is not False
                    or str(
                        companion["base_exact_reuse_prefill"][
                            "base_coordinate"
                        ]
                    )
                    != PREFILL_COMPANION_DONOR[coordinate]
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} prefill companion drifted: "
                        f"{coordinate}"
                    )
                translation = str(companion["translation"])
                owner = "base_exact_prefill_companion"
                seen_prefill.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} unowned companion: {coordinate}"
                )
            owners.append(owner)
            assembled.append(translation)
            literal_evidence.append((coordinate, owner, translation))
        donor_assembled = tuple(
            str(
                base_rows[f"{key[0]}:{key[1]}:{literal_id}"][
                    "translation"
                ]
            )
            for literal_id in range(EXPECTED_ARITY[key])
        )
        if tuple(assembled) != donor_assembled:
            raise RuntimeError(
                f"segment {SEGMENT} exact Base assembly drifted: {key}"
            )
        base_evidence.append((
            key,
            sha256_bytes(source.data),
            source_literals,
            current_literals,
            tuple(value.hex().upper() for value in gap_bytes(source)),
            raw_matches,
            literal_matches,
            masked_matches,
            tuple(context_rows),
            tuple(literal_evidence),
            "complete_approved_base_semantic_assembly",
            "base_runtime_vm_not_inherited",
        ))
        assembly_evidence.append((
            key,
            tuple(owners),
            tuple(assembled),
            donor_assembled,
            runtime_controls(source),
            runtime_controls(current),
            "complete_translation_equals_approved_base",
            "base_runtime_vm_not_inherited",
        ))
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_cross != set(CROSS_SEGMENT_COMPANION_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


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
        current_blob, replacements
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
        or len(prefilled) != 53
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


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    key: tuple[int, int],
) -> dict[str, Any]:
    source = records_by_label["jp"][key]
    current = records_by_label["current"][key]
    source_controls = runtime_controls(source)
    current_controls = runtime_controls(current)
    dynamic = key not in STATIC_RECORD_KEYS
    return {
        "runtime_category": dict(SPEAKER_STYLE)[key],
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
        "approved_complete_base_semantic_assembly",
        "base_context_reference_coordinates": RECORD_BASE_CONTEXT[key],
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "cross_segment_companions_reviewed": key == (12, 60),
        "same_record_prefill_companions_reviewed": any(
            coordinate.startswith(f"{key[0]}:{key[1]}:")
            for coordinate in PREFILL_COMPANION_COORDINATES
        ),
        "manual_multilingual_context_reviewed": True,
        "completed_base_context_reviewed": True,
        "protected_outer_whitespace_preserved": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_runtime_state_inherited": False,
        "base_vm_state_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": dynamic,
        "runtime_review_required": dynamic,
        "runtime_promotion_authorized": False,
    }


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
        "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "TARGET_RECORD_KEYS": TARGET_RECORD_KEYS,
        "STATIC_RECORD_KEYS": STATIC_RECORD_KEYS,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "BOUNDARY_RECORD_KEYS": BOUNDARY_RECORD_KEYS,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
        "SPEAKER_STYLE": SPEAKER_STYLE,
        "TERMINOLOGY_POLICY": TERMINOLOGY_POLICY,
        "RECORD_BASE_CONTEXT": RECORD_BASE_CONTEXT,
        "EXPECTED_STEAM_PK_SHA256": EXPECTED_STEAM_PK_SHA256,
        "EXPECTED_PRISTINE_PK_SHA256": EXPECTED_PRISTINE_PK_SHA256,
        "EXPECTED_PREFILL_SHA256": EXPECTED_PREFILL_SHA256,
        "EXPECTED_BASE_PROMOTED_SHA256": EXPECTED_BASE_PROMOTED_SHA256,
        "EXPECTED_QUEUE_UNIVERSE_SHA256":
        EXPECTED_QUEUE_UNIVERSE_SHA256,
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
        "EXPECTED_RUNTIME_CONTROL_SHA256":
        EXPECTED_RUNTIME_CONTROL_SHA256,
        "EXPECTED_BASE_SEARCH_SHA256": EXPECTED_BASE_SEARCH_SHA256,
        "EXPECTED_COMPLETE_ASSEMBLY_SHA256":
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
        "EXPECTED_CALL_GRAPH_SHA256": EXPECTED_CALL_GRAPH_SHA256,
        "EXPECTED_SPEAKER_STYLE_SHA256":
        EXPECTED_SPEAKER_STYLE_SHA256,
        "EXPECTED_TERMINOLOGY_POLICY_SHA256":
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256":
        EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256,
        "EXPECTED_CHANGED_LITERAL_COUNT":
        EXPECTED_CHANGED_LITERAL_COUNT,
        "DISCOVERED_PINS": DISCOVERED_PINS,
        "BASIS": BASIS,
    }
    for name, value in values.items():
        setattr(BASE, name, value)
    BASE.queue_evidence = queue_evidence
    BASE.assert_context_contracts = assert_context_contracts
    BASE.base_and_assembly_evidence = base_and_assembly_evidence
    BASE.build_combined_slice_candidate = build_combined_slice_candidate
    BASE.runtime_evidence = runtime_evidence


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
    int,
    str,
    int,
    tuple[str, ...],
]:
    install_base_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = BASE.assert_queue_and_residual_contract(prepared)
    expected_neighbors = tuple(path.name for path in OPTIONAL_NEIGHBORS)
    if optional_present != expected_neighbors:
        raise RuntimeError(
            f"segment {SEGMENT} required neighbors absent: "
            f"{optional_present}"
        )
    records = context_records(prepared)
    BASE.assert_context_contracts(prepared, records)
    BASE.assert_base_and_complete_assembly(prepared, records)
    BASE.assert_call_graphs(prepared)
    BASE.assert_semantics(records)
    candidate, candidate_sha256, changed = BASE.build_candidate(
        prepared, records
    )
    combined_sha256, combined_changed = build_combined_slice_candidate(
        prepared, records
    )
    rows: list[dict[str, Any]] = []
    style_map = dict(SPEAKER_STYLE)
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        key = (block_id, record_id)
        current_text = literal_texts(records["current"], key)[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        dynamic = coordinate in DYNAMIC_COORDINATES
        references = RECORD_BASE_CONTEXT[key]
        rows.append({
            "schema": ENGINE.DECISION_SCHEMA,
            "resource": "pk_msggame",
            "coordinate": coordinate,
            "source_record_raw_sha256":
            target["source_record_raw_sha256"],
            "current_ko_utf16le_sha256":
            target["current_ko_utf16le_sha256"],
            "translation": TRANSLATIONS[coordinate],
            "semantic_review": "approved",
            "scope_classification": (
                "runtime_fragment_pending" if dynamic else "retranslated"
            ),
            "layout_review": (
                "runtime_pending" if dynamic else "unchanged_from_current"
            ),
            "runtime_review": "pending" if dynamic else "not_required",
            "basis": BASIS,
            "historic_korean_used": False,
            "switch_korean_used": False,
            "base_exact_reuse_prefill_excluded": True,
            "all_available_predecessors_validated": True,
            "optional_neighbor_outputs_validated_if_present": True,
            "required_bilateral_neighbors_validated": True,
            "manual_multilingual_context_review": True,
            "adjacent_record_context_review": True,
            "complete_record_fragment_review": True,
            "cross_segment_companions_reviewed": key == (12, 60),
            "same_record_prefill_companions_reviewed": any(
                value.startswith(f"{block_id}:{record_id}:")
                for value in PREFILL_COMPANION_COORDINATES
            ),
            "speaker_register_reviewed": True,
            "historical_terminology_reviewed": True,
            "protected_outer_whitespace_preserved": True,
            "completed_base_corpus_searched": True,
            "base_context_reference_coordinate":
            references[0] if references else None,
            "base_context_reference_coordinates": references,
            "base_context_is_automatic_reuse": False,
            "base_wording_contextually_adapted": False,
            "manual_complete_base_donor_translation_selected": True,
            "base_runtime_state_inherited": False,
            "base_vm_state_inherited": False,
            "speaker_style": style_map[key],
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after": TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
            "runtime_assembly_evidence": runtime_evidence(records, key),
        })
    return (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        combined_sha256,
        combined_changed,
        optional_present,
    )


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
        raise RuntimeError(
            f"segment {SEGMENT} second-run reproduction drifted"
        )
    steam_before = sha256_bytes(STEAM_PK.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: {steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared, OUTPUT, require_complete=False
    )
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    expected_counts = Counter({
        "runtime_fragment_pending": len(DYNAMIC_COORDINATES),
        "retranslated": len(STATIC_COORDINATES),
    })
    if (
        len(rows) != 14
        or len(validated) != 14
        or counts != expected_counts
        or any(
            row["semantic_review"] != "approved"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["base_vm_state_inherited"] is not False
            or row["line_count_preserved"] is not True
            or row["required_bilateral_neighbors_validated"] is not True
            for row in rows
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} decision validation drifted"
        )
    if EXPECTED_CANDIDATE_SHA256 != "TO_PIN":
        install_base_globals()
        BASE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(json.dumps({
        "status": "ok",
        "segment": SEGMENT_NAME,
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "approved": len(rows),
        "scope_classification_counts": dict(counts),
        "queue_slice_visible_count": 67,
        "exact_reuse_prefill_count": 53,
        "residual_count": len(rows),
        "reviewed_complete_record_count": len(TARGET_RECORD_KEYS),
        "cross_segment_companion_count":
        len(CROSS_SEGMENT_COMPANION_COORDINATES),
        "same_record_prefill_companion_count":
        len(PREFILL_COMPANION_COORDINATES),
        "exact_complete_base_assembly_record_count":
        len(EXACT_BASE_RECORD_KEYS),
        "semantic_base_only_record_count": 0,
        "source_call_root_count": len(SOURCE_CALL_ROOTS),
        "current_call_root_count": len(CURRENT_CALL_ROOTS),
        "source_calls_flattened_in_current_record_count": 3,
        "optional_neighbors_present": list(optional_present),
        "bilateral_neighbors_required": True,
        "changed_literal_count": changed,
        "unchanged_literal_count": len(rows) - changed,
        "combined_slice_changed_literal_count": combined_changed,
        "candidate_sha256": candidate_sha256,
        "combined_slice_candidate_sha256": combined_sha256,
        "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
        "steam_sha256_before": steam_before,
        "steam_sha256_after": steam_after,
        "base_runtime_state_inherited": False,
        "base_vm_state_inherited": False,
        "source_current_gap_equality_guarded": True,
        "source_current_call_graphs_guarded": True,
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
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
