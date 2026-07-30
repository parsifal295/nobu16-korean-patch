#!/usr/bin/env python3
"""Build source-redacted PK B067 segment 1205 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch064_segment1201.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B067_S1205.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B067_S1206.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B067_S1207.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1205
QUEUE_BATCH_ID = "pk_msggame-B067"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "7:2469:0",
    "7:2470:0",
    "7:2471:0",
    "7:2480:0",
    "7:2481:0",
    "7:2490:1",
    "7:2490:3",
    "7:2490:6",
    "7:2491:2",
    "7:2491:3",
    "7:2492:0",
    "7:2494:2",
    "7:2495:0",
    "7:2495:1",
    "7:2495:2",
    "7:2496:0",
    "7:2496:1",
    "7:2496:2",
    "7:2496:3",
)
TRANSLATIONS = {
    "7:2469:0": (
        "와 우리의 전력은 거의 호각\n"
        "승패는 지휘에 달렸다는 것이군"
    ),
    "7:2470:0": (
        "와 우리의 전력은 거의 호각\n"
        "승패는 지휘에 달렸다는 것이군"
    ),
    "7:2471:0": (
        "와 우리의 전력은 거의 호각\n"
        "승패는 지휘에 달렸다는 것이군"
    ),
    "7:2480:0": "즉시—",
    "7:2481:0": "즉시—",
    "7:2490:1": "!\n",
    "7:2490:3": "도움",
    "7:2490:6": "!",
    "7:2491:2": "의 방안도",
    "7:2491:3": "검토",
    "7:2492:0": "의\n",
    "7:2494:2": "인가?",
    "7:2495:0": "이번 출진에는\n우리 군단도",
    "7:2495:1": "힘을 보태게 해 주",
    "7:2495:2": "!",
    "7:2496:0": (
        "우리 군단에는 출진할 수 있는 병력이\n"
        "부족하"
    ),
    "7:2496:1": "\n이번 출진에서는",
    "7:2496:2": "도움이 되지 못하겠군",
    "7:2496:3": "……",
}
TARGET_RECORD_IDS = (
    2469,
    2470,
    2471,
    2480,
    2481,
    2490,
    2491,
    2492,
    2494,
    2495,
    2496,
)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    2469: 3,
    2470: 2,
    2471: 1,
    2480: 3,
    2481: 2,
    2490: 7,
    2491: 4,
    2492: 3,
    2494: 3,
    2495: 3,
    2496: 4,
}
PREFILL_COMPANION_COORDINATES = (
    "7:2469:1",
    "7:2469:2",
    "7:2470:1",
    "7:2480:1",
    "7:2480:2",
    "7:2481:1",
    "7:2490:0",
    "7:2490:2",
    "7:2490:5",
    "7:2491:0",
    "7:2492:1",
    "7:2492:2",
    "7:2494:0",
    "7:2494:1",
)
HIDDEN_CURRENT_COMPANION_COORDINATES = (
    "7:2490:4",
    "7:2491:1",
)
EXACT_BASE_DONOR = {
    2469: (7, 2423),
    2470: (7, 2424),
    2471: (7, 2425),
    2480: (7, 2434),
    2481: (7, 2435),
    2490: (7, 2444),
    2491: (7, 2445),
    2492: (7, 2446),
    2494: (7, 2448),
}
SEMANTIC_BASE_CONTEXT = {
    2495: (
        "6:1464:0",
        "9:622:0",
        "6:4405:1",
    ),
    2496: (
        "7:112:0",
        "6:1958:0",
        "8:448:0",
        "15:230:0",
        "15:230:1",
    ),
}
EXPECTED_BASE_RAW_MATCHES = {
    2469: (),
    2470: (),
    2471: (),
    2480: (),
    2481: ((7, 2435),),
    2490: (),
    2491: (),
    2492: (),
    2494: (),
    2495: (),
    2496: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    2469: ((7, 2423),),
    2470: ((7, 2424),),
    2471: ((7, 2415), (7, 2425)),
    2480: ((7, 2434),),
    2481: ((7, 2435),),
    2490: ((7, 2444),),
    2491: ((7, 2445),),
    2492: ((7, 2446),),
    2494: ((7, 2448),),
    2495: (),
    2496: (),
}
EXPECTED_BASE_MASKED_MATCHES = {
    record_id: (
        (EXACT_BASE_DONOR[record_id],)
        if record_id in EXACT_BASE_DONOR
        else ()
    )
    for record_id in TARGET_RECORD_IDS
}
BOUNDARY_RECORD_KEYS = tuple(
    (7, record_id)
    for record_id in (
        2423,
        2424,
        2425,
        2434,
        2435,
        2444,
        2445,
        2446,
        2448,
        2468,
        2469,
        2470,
        2471,
        2472,
        2479,
        2480,
        2481,
        2482,
        2489,
        2490,
        2491,
        2492,
        2493,
        2494,
        2495,
        2496,
        2497,
    )
)
SOURCE_CALL_ROOTS = (
    1,
    8,
    160,
    178,
    190,
    286,
    292,
    322,
    412,
    466,
    502,
    700,
    940,
    1090,
    1126,
    1168,
    1174,
)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    2469: ((1126, 1090), ("025032",)),
    2470: ((1126, 160), ("025032",)),
    2471: ((1126,), ("025032",)),
    2480: ((190, 502), ("029632",)),
    2481: ((190,), ("029632",)),
    2490: ((178, 8, 1174, 412, 1174, 940), ()),
    2491: ((1090, 1, 1174, 322), ("026432",)),
    2492: ((700, 292, 1126), ("023C", "0232")),
    2494: ((466,), ("026432",)),
    2495: ((1174, 322), ()),
    2496: ((160, 1168, 286), ()),
}
SPEAKER_STYLE = (
    (2469, "balanced_forces_supply_caution"),
    (2470, "balanced_forces_enemy_supply_shortage"),
    (2471, "balanced_forces_command_assessment"),
    (2480, "urgent_occupation_supply_caution"),
    (2481, "urgent_occupation_order"),
    (2490, "corps_domain_reinforcement_request"),
    (2491, "alternate_attack_route_proposal"),
    (2492, "roundabout_multi_direction_attack_proposal"),
    (2494, "direct_all_units_order_confirmation"),
    (2495, "corps_assistance_offer"),
    (2496, "insufficient_troops_assistance_refusal"),
)
TERMINOLOGY_POLICY = (
    ("military strength", "전력"),
    ("command", "지휘"),
    ("provisions", "병량"),
    ("occupation", "제압"),
    ("corps domain", "군단령"),
    ("assistance", "도움"),
    ("proposal", "방안"),
    ("sortie", "출진"),
    ("corps", "군단"),
    ("insufficient troops", "병력이 부족하다"),
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
    "E90C8D4135039416C5DE61A523DB7D2703740D9108A1B8FCE410795A9733D15F"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "196770B4A990C21EB775605972960BBE6660CD35BC9842FC8A7E791AB8ED573B"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "CA85C1FB6B761C7A515271C6FCBBC184C3237397B38317DEA6FF9EC7CB017702"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "A47E9FB6EA1576CA131370606C65FDBA4367A1250A4EF806A8A0344A62D5D862"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "C9D8BCBE6A3B1CA7DD7384CF2B399CBBF0933BECC00CC2C1144D6DA982AE6537"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "D9481EC6E019CAF236B21DCBB3E247A6E8BD28155AF1E378628B4B8A39587ADC"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "C1F74450409EFF35601EEB8CFC416F72BBC1B99CF6BF4980EBC4F534AC1C4D25"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "0DC1474C54C21DA5A0AA573296BB613D2E721B52AB0C27BCB9E287673ADE5976"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "D5D6A6382E6D2357D698B32608316FDBEDBB966884B5AFE7B0B603D55EBFB1E6"
)
EXPECTED_BOUNDARY_SHA256 = (
    "5DEF74D591E4DDBC3A5D151F7C241BD37E07BC74A571529D6F30DEB839D82524"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "921DEA40B42E5C6558C3756AFBF058657E21EEA8308188D249AA4CECB6EE2AF9"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "F0AF3F851B72315ED13691BAC16185CA7EFCB4E83C9657F6CB6811A2C64397C1"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "190F2EA849B656AF09B427D89320D098BC148C7B826FF96A2997DAFE0406F51A"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "1DC7BDAD19CD6F12835FEFD7F8B12709B92BCF1FD8A1D657A8D75F4540A142A4"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "DF123331768A149795F5CF313E906EA84788C4219B8B1992384E95074A837287"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "894F59D4D6EB831686898194B826D61250D896077C24199BC2C7B62D578A78A9"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "D90523DD9AAB344071E4C9B3AE344B97542F5DE90B2021D6420D04E15255E2C5"
)
EXPECTED_CANDIDATE_SHA256 = (
    "B6A7074FC8CBCD20B6CEEAA38774630C9D5D572EFCEB1059D0C5795C9127E05E"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "CA733E2B8C4A23D9598A270BB5DCF3A9E5511A2420855BF11B5EC97D882EEF1F"
)
EXPECTED_CHANGED_LITERAL_COUNT = 13
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 37

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative and complete PK EN SC TC context "
    "was manually reviewed; nine complete records use completed raw or "
    "literal-and-call-masked Base donors and two PK-only corps-assistance "
    "records use manually reviewed completed Base sortie, assistance, "
    "shortage, negative-predicate, and ellipsis wording as semantic context; "
    "two hidden newline literals, all forty-eight slice prefills, and "
    "fourteen same-record companions are validated; Base runtime and VM "
    "state are never inherited; complete records, calls, direction, castle, "
    "person and force tokens, protected outer whitespace, source and current "
    "gaps, queue and segment boundaries, two-run reproduction, tamper "
    "rejection, reverse overlays, outside-scope identity, and Steam "
    "read-only state are guarded"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1205_base",
        BASE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_base()
CORE = BASE.CORE
ENGINE = BASE.ENGINE
sha256_bytes = BASE.sha256_bytes
coordinate_key = BASE.coordinate_key
literal_texts = BASE.literal_texts
gap_bytes = BASE.gap_bytes
read_jsonl = BASE.read_jsonl


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
        len(rows) != 111
        or len(visible) != 200
        or visible[0] != "7:2469:0"
        or visible[-1] != "7:2579:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B067 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "7:2469:0"
        or queue_slice[-1] != "7:2496:3"
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
        len(prefilled) != 48
        or len(residual) != 19
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


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
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
    hidden_set = set(HIDDEN_CURRENT_COMPANION_COORDINATES)
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    seen_hidden: set[str] = set()
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
                and CORE.mask_call_operands(record)
                == CORE.mask_call_operands(source)
            )
        )
        if (
            len(source_literals) != EXPECTED_ARITY[record_id]
            or raw_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
            or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[record_id]
            or masked_matches != EXPECTED_BASE_MASKED_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base donor drifted: {record_id}"
            )
        exact = record_id in EXACT_BASE_DONOR
        donor_rows: list[dict[str, Any]] = []
        donor_coordinates: tuple[str, ...]
        base_literals: tuple[str, ...] = ()
        if exact:
            donor_key = EXACT_BASE_DONOR[record_id]
            base_literals = literal_texts(base_source, donor_key)
            donor_coordinates = tuple(
                f"{donor_key[0]}:{donor_key[1]}:{literal_id}"
                for literal_id in range(EXPECTED_ARITY[record_id])
            )
        else:
            donor_coordinates = SEMANTIC_BASE_CONTEXT[record_id]
            for donor_coordinate in donor_coordinates:
                donor = base_rows.get(donor_coordinate)
                if (
                    donor is None
                    or donor.get("semantic_review") != "approved"
                    or donor.get("runtime_review")
                    not in {"verified", "not_required"}
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} semantic context drifted: "
                        f"{donor_coordinate}"
                    )
                donor_rows.append(donor)
        assembled: list[str] = []
        donor_assembled: list[str] = []
        owners: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"{BLOCK_ID}:{record_id}:{literal_id}"
            if exact and coordinate in hidden_set:
                if (
                    source_literals[literal_id] != "\n"
                    or current_literals[literal_id] != "\n"
                    or base_literals[literal_id] != "\n"
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} hidden newline drifted: "
                        f"{coordinate}"
                    )
                seen_hidden.add(coordinate)
                assembled.append("\n")
                donor_assembled.append("\n")
                owners.append("hidden_newline_exact")
                continue
            if exact:
                donor_coordinate = donor_coordinates[literal_id]
                donor = base_rows.get(donor_coordinate)
                if (
                    donor is None
                    or donor.get("semantic_review") != "approved"
                    or donor.get("runtime_review")
                    not in {"verified", "not_required"}
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} exact donor drifted: "
                        f"{donor_coordinate}"
                    )
                donor_rows.append(donor)
                donor_translation = str(donor["translation"])
                donor_assembled.append(donor_translation)
                if coordinate in target_set:
                    if TRANSLATIONS[coordinate] != donor_translation:
                        raise RuntimeError(
                            f"segment {SEGMENT} target donor drifted: "
                            f"{coordinate}"
                        )
                    seen_target.add(coordinate)
                    assembled.append(TRANSLATIONS[coordinate])
                    owners.append("segment_exact")
                    continue
                companion = prefill_rows.get(coordinate)
                if (
                    coordinate not in companion_set
                    or companion is None
                    or companion.get("semantic_review") != "approved"
                    or companion.get("runtime_review") != "pending"
                    or companion["base_exact_reuse_prefill"][
                        "runtime_promotion_authorized"
                    ]
                    is not False
                    or str(companion["translation"]) != donor_translation
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} companion drifted: {coordinate}"
                    )
                seen_companion.add(coordinate)
                assembled.append(str(companion["translation"]))
                owners.append("base_exact_prefill_runtime_pending")
                continue
            if coordinate not in target_set:
                raise RuntimeError(
                    f"segment {SEGMENT} incomplete manual record: "
                    f"{coordinate}"
                )
            seen_target.add(coordinate)
            assembled.append(TRANSLATIONS[coordinate])
            donor_assembled.append("manual_multilingual_semantic_selection")
            owners.append("segment_manual")
        if exact and tuple(assembled) != tuple(donor_assembled):
            raise RuntimeError(
                f"segment {SEGMENT} exact assembly drifted: {record_id}"
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
                donor_coordinates,
                tuple(
                    (
                        str(row["coordinate"]),
                        str(row["translation"]),
                        str(row["semantic_review"]),
                        str(row["runtime_review"]),
                    )
                    for row in donor_rows
                ),
                tuple(
                    coordinate
                    for coordinate in HIDDEN_CURRENT_COMPANION_COORDINATES
                    if coordinate.startswith(f"{BLOCK_ID}:{record_id}:")
                ),
                "complete_exact" if exact else "semantic_context_only",
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(assembled),
                tuple(donor_assembled),
                CORE.runtime_controls(source),
                CORE.runtime_controls(records_by_label["current"][key]),
                (
                    "complete_translation_equals_completed_base_donor"
                    if exact
                    else "manual_pk_semantic_adaptation"
                ),
                "base_runtime_state_not_inherited",
            )
        )
    if (
        seen_target != target_set
        or seen_companion != companion_set
        or seen_hidden != hidden_set
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
        or len(prefilled) != 48
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
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "STATIC_RECORD_IDS": STATIC_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "PREFILL_COMPANION_COORDINATES": PREFILL_COMPANION_COORDINATES,
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
        "queue_evidence": queue_evidence,
        "build_combined_slice_candidate": build_combined_slice_candidate,
    }
    for name, value in values.items():
        setattr(BASE, name, value)
    BASE.BASE.base_and_assembly_evidence = base_and_assembly_evidence


def propagate_base_globals() -> None:
    install_base_globals()
    BASE.patch_base_globals()
    BASE.BASE.base_and_assembly_evidence = base_and_assembly_evidence
    BASE.BASE.patch_parent_globals()


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
    result = list(BASE.build_rows())
    for row in result[1]:
        record_id = coordinate_key(str(row["coordinate"]))[1]
        row["hidden_newline_companion_reviewed"] = any(
            coordinate.startswith(f"{BLOCK_ID}:{record_id}:")
            for coordinate in HIDDEN_CURRENT_COMPANION_COORDINATES
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
    if DISCOVERED_PINS:
        print(
            json.dumps(
                DISCOVERED_PINS,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 2
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
        len(rows) != 19
        or len(validated) != 19
        or counts != Counter({"runtime_fragment_pending": 19})
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
    propagate_base_globals()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B067_S1205",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "target_coordinate_first": TARGET_COORDINATES[0],
                "target_coordinate_last": TARGET_COORDINATES[-1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 67,
                "exact_reuse_prefill_count": 48,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "hidden_current_companion_count":
                len(HIDDEN_CURRENT_COMPANION_COORDINATES),
                "raw_exact_complete_base_donor_record_count":
                sum(
                    bool(EXPECTED_BASE_RAW_MATCHES[record_id])
                    for record_id in TARGET_RECORD_IDS
                ),
                "masked_complete_base_donor_record_count":
                len(EXACT_BASE_DONOR)
                - sum(
                    bool(EXPECTED_BASE_RAW_MATCHES[record_id])
                    for record_id in TARGET_RECORD_IDS
                ),
                "semantic_base_context_record_count":
                len(SEMANTIC_BASE_CONTEXT),
                "source_call_root_count": len(SOURCE_CALL_ROOTS),
                "current_call_root_count": len(CURRENT_CALL_ROOTS),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "unchanged_literal_count": len(rows) - changed,
                "combined_slice_changed_literal_count":
                combined_changed,
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
            },
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
