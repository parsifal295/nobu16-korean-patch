#!/usr/bin/env python3
"""Build source-redacted PK B066 segment 1204 residual decisions."""

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
PARENT_PATH = WORKSTREAM / "build_pk_batch062_segment1194.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B066_S1204.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B066_S1203.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1204
QUEUE_BATCH_ID = "pk_msggame-B066"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "7:2436:2",
    "7:2436:3",
    "7:2438:2",
    "7:2453:0",
    "7:2454:0",
    "7:2455:0",
    "7:2455:1",
    "7:2456:0",
    "7:2456:1",
    "7:2459:0",
    "7:2460:1",
    "7:2461:0",
    "7:2462:0",
    "7:2463:0",
    "7:2464:0",
    "7:2468:0",
)
TRANSLATIONS = {
    "7:2436:2": "(으)로 향",
    "7:2436:3": "!",
    "7:2438:2": "……?",
    "7:2453:0": "지원은",
    "7:2454:0": (
        "방위 거점은 적을 요격할 준비를 하고 있어\n"
        "출진에 필요한 병력을 충분히 마련할 수 없습니다\n"
        "출진시킬 때는 주의하십시오"
    ),
    "7:2455:0": "장군인",
    "7:2455:1": (
        "을(를) 멸망시키면,\n"
        "다른 세력의 외교 자세가 악화될 수 있습니다\n"
        "공격할 때는 주의하십시오"
    ),
    "7:2456:0": "약속은—",
    "7:2456:1": "에 투입할 병력은—",
    "7:2459:0": (
        "와(과) 우리의 힘은 거의 호각\n"
        "승패는 지휘에 달렸다는 것이군"
    ),
    "7:2460:1": (
        "을(를) 함락하기는 어려울 듯합니다\n"
        "주명이시라면 전력을 다해 공격하겠습니다만……"
    ),
    "7:2461:0": (
        "공성전을 치르려면\n"
        "성병의 3배에서 5배에 이르는 병력이 필요하겠군……\n"
        "이번에는 힘겨운 싸움이 되"
    ),
    "7:2462:0": "와(과) 싸우기에는\n충분한 병력",
    "7:2463:0": "와의 전투에는\n충분한 병력",
    "7:2464:0": "와의 전투에는\n충분한 병력",
    "7:2468:0": (
        "공성전을 치르려면\n"
        "성병의 3배에서 5배에 이르는 병력이 필요하겠군……\n"
        "적의 증원까지 고려하면, 공략은 어려운 일"
    ),
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    2436,
    2438,
    2453,
    2454,
    2455,
    2456,
    2459,
    2460,
    2461,
    2462,
    2463,
    2464,
    2468,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    2436: 4,
    2438: 3,
    2453: 3,
    2454: 1,
    2455: 2,
    2456: 3,
    2459: 1,
    2460: 2,
    2461: 1,
    2462: 3,
    2463: 2,
    2464: 1,
    2468: 1,
}
PREFILL_COMPANION_COORDINATES = (
    "7:2436:0",
    "7:2438:0",
    "7:2438:1",
    "7:2453:2",
    "7:2456:2",
    "7:2460:0",
    "7:2462:1",
    "7:2462:2",
    "7:2463:1",
)
INVISIBLE_COMPANION_COORDINATES = (
    "7:2436:1",
    "7:2453:1",
)
FUTURE_COMPANION_COORDINATES: tuple[str, ...] = ()
COMPLETE_DONOR_PRIMARY = {
    2436: (7, 2394),
    2438: (7, 2396),
    2453: (7, 2411),
    2456: (7, 2412),
    2459: (7, 2415),
    2462: (7, 2417),
    2463: (7, 2418),
    2464: (7, 2419),
}
PRIMARY_BASE_MATCH = COMPLETE_DONOR_PRIMARY
EXPECTED_BASE_MATCHES = {
    2436: ((7, 2394),),
    2438: ((7, 2396),),
    2453: ((7, 2411),),
    2454: (),
    2455: (),
    2456: ((7, 2412),),
    2459: ((7, 2415), (7, 2425)),
    2460: (),
    2461: (),
    2462: ((7, 2417),),
    2463: ((7, 2418),),
    2464: ((7, 2419),),
    2468: (),
}
EXPECTED_RAW_BASE_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_LITERAL_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_MASKED_BASE_MATCHES = {
    2436: ((7, 2394),),
    2438: ((7, 2396),),
    2453: ((7, 2411),),
    2454: (),
    2455: (),
    2456: ((7, 2412),),
    2459: ((7, 2415),),
    2460: (),
    2461: (),
    2462: ((7, 2417),),
    2463: ((7, 2418),),
    2464: ((7, 2419),),
    2468: (),
}
COMPLETE_BASE_DONOR_COORDINATES = {
    2436: ("7:2394:0", "7:2394:2", "7:2394:3"),
    2438: ("7:2396:0", "7:2396:1", "7:2396:2"),
    2453: ("7:2411:0", "7:2411:2"),
    2456: ("7:2412:0", "7:2412:1", "7:2412:2"),
    2459: ("7:2415:0",),
    2462: ("7:2417:0", "7:2417:1", "7:2417:2"),
    2463: ("7:2418:0", "7:2418:1"),
    2464: ("7:2419:0",),
}
EXPECTED_BASE_DONOR_COORDINATES = {
    **COMPLETE_BASE_DONOR_COORDINATES,
    2454: ("13:223:0", "9:2925:0"),
    2455: ("6:4354:1", "13:352:0"),
    2460: ("7:2416:0", "7:2416:1", "7:2416:2"),
    2461: ("7:2414:1",),
    2468: ("7:2414:1", "7:2416:1"),
}
BOUNDARY_RECORD_KEYS = (
    (7, 2315),
    (7, 2316),
    (7, 2424),
    (7, 2425),
    (7, 2435),
    (7, 2436),
    (7, 2437),
    (7, 2438),
    (7, 2439),
    (7, 2452),
    (7, 2453),
    (7, 2454),
    (7, 2455),
    (7, 2456),
    (7, 2457),
    (7, 2458),
    (7, 2459),
    (7, 2460),
    (7, 2461),
    (7, 2462),
    (7, 2463),
    (7, 2464),
    (7, 2465),
    (7, 2466),
    (7, 2467),
    (7, 2468),
    (7, 2469),
)
SOURCE_CALL_ROOTS = (
    7,
    160,
    190,
    256,
    466,
    508,
    538,
    550,
    610,
    736,
    904,
    1090,
    1096,
    1126,
    1162,
)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    2436: ((1096, 190, 508), ("026432",)),
    2438: ((538, 256), ()),
    2453: ((904, 7, 466), ()),
    2454: ((), ()),
    2455: ((), ("025032",)),
    2456: ((1162,), ("026432", "0232")),
    2459: ((1126,), ("026E32",)),
    2460: ((7,), ("026432",)),
    2461: ((1126, 736), ()),
    2462: ((550, 1090), ("025032",)),
    2463: ((550, 160), ("025032",)),
    2464: ((550,), ("025032",)),
    2468: ((610,), ()),
}
SPEAKER_STYLE = (
    (2436, "next_castle_attack_destination_declaration"),
    (2438, "objective_complete_return_question"),
    (2453, "support_and_corps_sortie_pledge"),
    (2454, "defense_base_sortie_capacity_warning"),
    (2455, "shogun_force_destruction_diplomacy_warning"),
    (2456, "promised_castle_troop_commitment"),
    (2459, "equal_strength_command_judgment"),
    (2460, "castle_capture_feasibility_reservation"),
    (2461, "siege_force_ratio_hard_battle_warning"),
    (2462, "sufficient_troops_supply_warning"),
    (2463, "sufficient_troops_enemy_supply_shortage"),
    (2464, "sufficient_troops_assessment"),
    (2468, "siege_force_ratio_enemy_reinforcement_warning"),
)
TERMINOLOGY_POLICY = (
    ("defense base", "방위 거점"),
    ("intercept", "요격"),
    ("sortie", "출진"),
    ("shogun", "장군"),
    ("diplomatic stance", "외교 자세"),
    ("siege", "공성전"),
    ("castle troops", "성병"),
    ("field provisions", "휴대 병량"),
    ("capture", "함락"),
    ("reinforcements", "증원"),
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
    "D78F3657FB5A904C73BC74DDF1C2CC0CF6CF28B6D61E4C1FEEFB572DF80ED4D6"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "894874E60D59E9A22E587369A3979C0E9932446C9729ED932BF4A541BD0B3A55"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "C06C903E2093C9B01C2369C368A509C1B1AA006238AC5B2352D50F38DA86AD14"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "D4435EB816E71B0B22FD6FE2020D0129905FE0C7B5AC66054AA21A9B1F93421D"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "80C9C690CB6A5B6A04A1B5CCF86964F8F7EF44D8C9AD22FA19A5868D7A013215"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "5E6230945ADFDA9FB4767D09F5F0A511C1C8CD9F5BADAEC88CBB0366FA920849"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "0DBE184B02184D2661F45D191B394DC37DBE2307E5B166011BC7E13D82298F91"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "CAFA1E4019347AC772FF6B616ED3CC3C1D1CC67AD8DD4B64A4EF5903A0425901"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "B9F735BC4D45721AA7EE353476B853C26647878F7BAD428E2D350374927A5273"
)
EXPECTED_BOUNDARY_SHA256 = (
    "08CFAD8A6D7E4C6BB3A53770B8AD28B60367B1D64E9CA9E333D5DB0A80C86A59"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "F73F9121AEA0195BF191D7635A83C0CA5E4F3548EFB0E44F1005821615F4B642"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "075EC037C884FC8A0EB0FF23F895AACE7F17D05A9D9CCB1AB81629E7671B184B"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "28BEEB0F0434888C002BD581CC3A9B29BCC2CE46365827F297E8391AB1E22667"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "FBEDE67A1DDE22CB77960C011BA6B538078F442A07AA3DDE1CB18D06796745AA"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "591733A509495ACA99D17B3C274DA637E62751DA1B8487BC8414366480B31D3D"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "B21F38F40F8681FD967F48DAA8D17F87D4A61AD24F560F973689EA678AF8BB9E"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "B0296D9231E8A26025B97B7AFBA9D15CF37F8CBC29917BF06B48021F0093F219"
)
EXPECTED_CANDIDATE_SHA256 = (
    "84C60306A230B70887F2320005D060058D486DC256089AA88D0E134537DC078B"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "CCFB5FE6C308E30352F3CD1C8FE35C35341D91E1B3A4511774C99C9E754FD9AA"
)
EXPECTED_CHANGED_LITERAL_COUNT = 14

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese source authoritative; complete PC English, "
    "Simplified Chinese and Traditional Chinese context was reviewed; "
    "eight complete PK records have a completed Base literal and "
    "operand-masked structural donor, while five PK-only records were "
    "translated manually with completed Base terminology and near-match "
    "references used for semantics only; Base runtime and VM status are "
    "never inherited; each complete record is assembled from sixteen "
    "residual translations, nine approved Base-prefilled companions and "
    "two source-identical hidden newline companions; fifteen reachable "
    "call roots, castle, faction and numeric tokens, gaps, punctuation, "
    "line counts and protected outer whitespace are guarded; all fifty "
    "prefills in the sixty-six-row final queue slice are validated and "
    "the combined slice is rebuilt in both orders and reversed "
    "byte-exactly; two-run reproduction, tamper rejection, outside-scope "
    "identity and Steam read-only state are guarded; every residual "
    "remains runtime pending"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1204_parent",
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
        len(rows) != 153
        or len(visible) != 200
        or visible[0] != "7:2316:0"
        or visible[-1] != "7:2468:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B066 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "7:2425:0"
        or queue_slice[-1] != "7:2468:0"
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
        len(prefilled) != 50
        or len(residual) != 16
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
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"7:{record_id}:{literal_id}"
            if coordinate in target_set:
                assembled.append(TRANSLATIONS[coordinate])
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
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} prefill companion drifted: "
                        f"{coordinate}"
                    )
                assembled.append(str(companion["translation"]))
                seen_companion.add(coordinate)
            elif coordinate in invisible_set:
                if (
                    source_literals[literal_id] != "\n"
                    or current_literals[literal_id] != "\n"
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} hidden newline drifted: "
                        f"{coordinate}"
                    )
                assembled.append("\n")
                seen_invisible.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} unowned literal: {coordinate}"
                )
        references: list[tuple[Any, ...]] = []
        for donor_coordinate in EXPECTED_BASE_DONOR_COORDINATES[record_id]:
            donor = base_rows.get(donor_coordinate)
            if donor is None or donor.get("semantic_review") != "approved":
                raise RuntimeError(
                    f"segment {SEGMENT} missing Base reference: "
                    f"{donor_coordinate}"
                )
            references.append(
                (
                    donor_coordinate,
                    str(donor["translation"]),
                    str(donor["semantic_review"]),
                    str(donor["runtime_review"]),
                    "semantic_only",
                    "runtime_vm_not_inherited",
                )
            )
        complete_donor_coordinate = COMPLETE_DONOR_PRIMARY.get(record_id)
        donor_assembled: tuple[str, ...] | None = None
        if complete_donor_coordinate is not None:
            donor_values: list[str] = []
            for literal_id in range(EXPECTED_ARITY[record_id]):
                donor_coordinate = (
                    f"{complete_donor_coordinate[0]}:"
                    f"{complete_donor_coordinate[1]}:{literal_id}"
                )
                if f"7:{record_id}:{literal_id}" in invisible_set:
                    donor_values.append("\n")
                else:
                    donor = base_rows.get(donor_coordinate)
                    if donor is None:
                        raise RuntimeError(
                            f"segment {SEGMENT} missing complete donor: "
                            f"{donor_coordinate}"
                        )
                    donor_values.append(str(donor["translation"]))
            donor_assembled = tuple(donor_values)
            if tuple(assembled) != donor_assembled:
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
                tuple(references),
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(assembled),
                donor_assembled,
                runtime_controls(source),
                runtime_controls(records_by_label["current"][key]),
                (
                    "complete_operand_masked_base_donor_reviewed"
                    if complete_donor_coordinate is not None
                    else "manual_multilingual_complete_record_reviewed"
                ),
                "base_semantics_only",
                "base_runtime_vm_not_inherited",
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


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source = records_by_label["jp"][(BLOCK_ID, record_id)]
    current = records_by_label["current"][(BLOCK_ID, record_id)]
    source_controls = runtime_controls(source)
    current_controls = runtime_controls(current)
    donor = COMPLETE_DONOR_PRIMARY.get(record_id)
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
            "literal_and_operand_masked_only"
            if donor is not None
            else "no_complete_base_match"
        ),
        "base_complete_record_coordinate": (
            f"{donor[0]}:{donor[1]}" if donor is not None else None
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
        "hidden_newline_companion_reviewed":
        any(
            coordinate.startswith(f"7:{record_id}:")
            for coordinate in INVISIBLE_COMPANION_COORDINATES
        ),
        "next_slice_companion_reviewed": False,
        "manual_multilingual_context_reviewed": True,
        "completed_base_corpus_searched": True,
        "completed_base_donor_reviewed": True,
        "base_semantics_only": True,
        "protected_outer_whitespace_preserved": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_runtime_state_inherited": False,
        "base_vm_state_inherited": False,
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
        or len(prefilled) != 50
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
        "INVISIBLE_COMPANION_COORDINATES":
        INVISIBLE_COMPANION_COORDINATES,
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
        "EXPECTED_CONTROLS_BY_RECORD": EXPECTED_CONTROLS_BY_RECORD,
        "SPEAKER_STYLE": SPEAKER_STYLE,
        "TERMINOLOGY_POLICY": TERMINOLOGY_POLICY,
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
    PARENT.base_and_assembly_evidence = base_and_assembly_evidence
    PARENT.assert_base_and_complete_assembly = (
        assert_base_and_complete_assembly
    )
    PARENT.build_combined_slice_candidate = build_combined_slice_candidate
    PARENT.PARENT.runtime_evidence = runtime_evidence


def build_rows() -> tuple[Any, ...]:
    configure_parent()
    result = list(PARENT.build_rows())
    for row in result[1]:
        record_id = coordinate_key(str(row["coordinate"]))[1]
        has_complete_donor = record_id in COMPLETE_DONOR_PRIMARY
        row["manual_complete_base_donor_translation_selected"] = (
            has_complete_donor
        )
        row["manual_semantic_base_references_reviewed"] = True
        row["manual_multilingual_translation_selected"] = (
            not has_complete_donor
        )
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
    counts = Counter(str(row["scope_classification"]) for row in rows)
    if (
        len(rows) != 16
        or len(validated) != 16
        or counts != Counter({"runtime_fragment_pending": 16})
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
        PARENT.PARENT.PARENT.engine_builder().assert_tamper_rejection(
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
                "segment": "pk_msggame_B066_S1204",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "target_coordinate_first": TARGET_COORDINATES[0],
                "target_coordinate_last": TARGET_COORDINATES[-1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 66,
                "exact_reuse_prefill_count": 50,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "same_slice_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "hidden_newline_companion_count":
                len(INVISIBLE_COMPANION_COORDINATES),
                "operand_masked_complete_base_donor_record_count":
                len(COMPLETE_DONOR_PRIMARY),
                "manual_multilingual_record_count":
                len(TARGET_RECORD_IDS) - len(COMPLETE_DONOR_PRIMARY),
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
                "base_vm_state_inherited": False,
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
