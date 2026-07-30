#!/usr/bin/env python3
"""Build source-redacted PK B100 segment 1306 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch051_segment1165.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B100_S1306.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B100_S1304.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B100_S1305.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1306
SEGMENT_NAME = "pk_msggame_B100_S1306"
QUEUE_BATCH_ID = "pk_msggame-B100"
QUEUE_START = 134
QUEUE_STOP = 197
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = tuple(
    """
    9:4144:5
    9:4145:0 9:4145:1
    9:4146:0 9:4146:1 9:4146:2 9:4146:3
    9:4147:0 9:4147:1 9:4147:2 9:4147:3
    10:4:0
    10:5:0 10:5:1 10:5:2
    10:7:0
    12:17:3
    12:18:2
    12:20:0
    12:21:1
    12:30:0
    12:45:1 12:45:2 12:45:4 12:45:5
    """.split()
)
TRANSLATIONS = {
    "9:4144:5": "!",
    "9:4145:0": "이제 와서 항복 따위 받아들일 수 없다",
    "9:4145:1": (
        "!\n이렇게 된 이상 장수는 단 한 명도 놓치지 않겠다…\n"
        "어서 돌아가 죽을 자리를 정해라"
    ),
    "9:4146:0": "각오는 훌륭하다만, 그건 안 된다",
    "9:4146:1": "!\n우리 가문은",
    "9:4146:2": "의 휘하 장수들이야말로 필요하다",
    "9:4146:3": "…\n자, 돌아가 작별의 물잔이라도 나누거라",
    "9:4147:0": "받아들일 리가 없다",
    "9:4147:1": "!\n우리",
    "9:4147:2": (
        "에 배신자 따위 필요 없다!\n성안에서 충신답게 죽어라"
    ),
    "9:4147:3": "!",
    "10:4:0": "+",
    "10:5:0": "+",
    "10:5:1": ",",
    "10:5:2": "+",
    "10:7:0": "와(과)",
    "12:17:3": "!",
    "12:18:2": "）",
    "12:20:0": "뭐라…?\n흐음…",
    "12:21:1": "까…",
    "12:30:0": "관백",
    "12:45:1": "!\n",
    "12:45:2": "오우",
    "12:45:4": ".\n미증유의 쾌거입니다",
    "12:45:5": "!",
}
TARGET_RECORD_KEYS = tuple(
    dict.fromkeys(
        tuple(int(value) for value in coordinate.split(":")[:2])
        for coordinate in TARGET_COORDINATES
    )
)
STATIC_RECORD_KEYS = {(12, 30)}
STATIC_COORDINATES = {
    coordinate
    for coordinate in TARGET_COORDINATES
    if tuple(int(value) for value in coordinate.split(":")[:2])
    in STATIC_RECORD_KEYS
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
EXPECTED_ARITY = {
    (9, 4144): 6,
    (9, 4145): 2,
    (9, 4146): 4,
    (9, 4147): 4,
    (10, 4): 1,
    (10, 5): 3,
    (10, 7): 2,
    (12, 17): 4,
    (12, 18): 3,
    (12, 20): 2,
    (12, 21): 2,
    (12, 30): 1,
    (12, 45): 6,
}
CROSS_SEGMENT_COMPANION_COORDINATES = (
    "9:4144:0",
    "9:4144:1",
    "9:4144:2",
    "9:4144:3",
    "9:4144:4",
)
MANUAL_CROSS_SEGMENT_TRANSLATIONS = {
    "9:4144:0": "물론, 기꺼이 환영한다",
    "9:4144:1": "!\n",
    "9:4144:2": "와(과)",
    "9:4144:3": "이(가) 항복해 준다면\n",
    "9:4144:4": "도 한층 더 번영할 것이다",
}
PREFILL_COMPANION_COORDINATES = (
    "10:7:1",
    "12:17:0",
    "12:17:1",
    "12:17:2",
    "12:18:0",
    "12:18:1",
    "12:20:1",
    "12:21:0",
    "12:45:0",
    "12:45:3",
)
EXACT_BASE_RECORD_KEYS = {
    (10, 4),
    (10, 5),
    (10, 7),
    (12, 17),
    (12, 18),
    (12, 20),
    (12, 21),
    (12, 30),
    (12, 45),
}
EXPECTED_BASE_RAW_MATCHES = {
    (9, 4144): (),
    (9, 4145): (),
    (9, 4146): (),
    (9, 4147): (),
    (10, 4): ((6, 4252), (6, 4273), (10, 4)),
    (10, 5): ((6, 4276), (10, 5)),
    (10, 7): ((10, 7),),
    (12, 17): (),
    (12, 18): (),
    (12, 20): ((12, 20),),
    (12, 21): ((12, 21),),
    (12, 30): ((12, 30),),
    (12, 45): (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    (9, 4144): (),
    (9, 4145): (),
    (9, 4146): (),
    (9, 4147): (),
    (10, 4): (
        (6, 4252),
        (6, 4259),
        (6, 4263),
        (6, 4273),
        (6, 4280),
        (10, 4),
    ),
    (10, 5): ((6, 4276), (10, 5)),
    (10, 7): ((10, 7),),
    (12, 17): ((12, 17),),
    (12, 18): ((12, 18),),
    (12, 20): ((12, 20),),
    (12, 21): ((12, 21),),
    (12, 30): ((12, 30),),
    (12, 45): ((12, 45),),
}
EXPECTED_BASE_MASKED_MATCHES = {
    **EXPECTED_BASE_LITERAL_MATCHES,
    (10, 4): ((6, 4252), (6, 4273), (10, 4)),
}
RECORD_BASE_CONTEXT = {
    (9, 4144): ("7:1370:0",),
    (9, 4145): ("9:1191:0", "9:2745:0"),
    (9, 4146): ("7:2539:1", "7:2769:0"),
    (9, 4147): ("6:473:0", "7:2539:1", "15:1455:0"),
    **{
        key: tuple(
            f"{key[0]}:{key[1]}:{literal_id}"
            for literal_id in range(EXPECTED_ARITY[key])
        )
        for key in EXACT_BASE_RECORD_KEYS
    },
}
BOUNDARY_RECORD_KEYS = (
    (9, 4143),
    (9, 4144),
    (9, 4145),
    (9, 4147),
    (9, 4148),
    (10, 2),
    (10, 3),
    (10, 4),
    (10, 7),
    (10, 8),
    (12, 15),
    (12, 16),
    (12, 17),
    (12, 45),
    (12, 46),
)
SOURCE_CALL_ROOTS = (
    1,
    8,
    148,
    376,
    508,
    520,
    538,
    598,
    610,
    748,
    778,
    814,
    1048,
    1072,
    1078,
    1090,
    1174,
)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
SPEAKER_STYLE = tuple(
    (
        key,
        (
            "hostile_siege_surrender_refusal"
            if key[0] == 9 and key[1] >= 4145
            else "confident_siege_surrender_acceptance"
            if key == (9, 4144)
            else "runtime_ui_fragment"
            if key[0] == 10
            else "court_and_unification_event"
        ),
    )
    for key in TARGET_RECORD_KEYS
)
TERMINOLOGY_POLICY = (
    ("three offices", "삼직"),
    ("chief adviser", "관백"),
    ("ou region", "오우"),
    ("retainers", "휘하 장수"),
    ("water-cup farewell rite", "작별의 물잔"),
    ("unprecedented feat", "미증유의 쾌거"),
    ("dynamic particle pair", "와(과)"),
)
EXPECTED_SOURCE_CURRENT_GAP_EQUALITY = {
    key: key not in {(12, 18), (12, 21), (12, 45)}
    for key in TARGET_RECORD_KEYS
}

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
    "16465EB37A9E84E6A85010F206205CC0F89F8F62024BE6738F8C4E55821EFBC3"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "B25CBF99FFCE3514CC0D27F6E5C5D3A4540506F335491892863B375E71E8335D"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "9B0E2DF4293C0A94E7C6084EDFCC9D3B46E192913184D00B01AB875FB2BA61A6"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "8280FFCFD5DAD1AF33961D7BECD2E2C36D180E4F9D8FF8C120363FD7BE6A8357"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "DC4261A14AAE09E8B798C38C3454CF1B5552F28D3513A93AA8502D09939E9DC5"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "358FCD9772212F36975D1E00F119519ECB111E7FFE15B04CCC777AF858756358"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "D8D45124583B112561E4BA206D6642AAB1DD9163E30F1382A032040539E03951"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "F0C52F91A97DF577CBD26FB29DCED18C22EAB215EB4433B1FE13BA7E8BB28E82"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "E1BF3E2F7A541F73D6304E87630A6B37FF9F9E42611C7DD3058202A01E9CC500"
)
EXPECTED_BOUNDARY_SHA256 = (
    "89B343A02C4B5B8271A7EC11788703F3B393A70A6D76383A20420627DE7F1A8A"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "9D1C514A322F06EBD20216D6C9F8DD181AFBFC016CCFDC11EA3C60400DB67530"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "5D1E9D638B4F1B1BE99AB800EBFE562A9AE96381DF129CB0C6B4E66B9ED4A2B3"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "0F7CE12BE69A96BC368859D7ED533B4479727E815ECC35580976D3D9D3E72CC7"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "69F2697BD3B54D881E1A9E07891EAB64A882579087007CC8107E3024F1344EC2"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "0ABED6FBC2E3B35DA08150B71819AFE742B3EF5B1AE566D4C885DCE44D0711C8"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "DACE404E0F63AF7A5F591DEAFCC3D48DB2F55242C6C2FF472405C9FB09AB5CAE"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "3EEDDA8BEF59CF698A674849EA3F4D377F558692A99A006FC8FEB8F0A24214B9"
)
EXPECTED_CANDIDATE_SHA256 = (
    "90D8969A234759098A89C02EC4D3EF30639DA1E140A2A80A898235EEC812F879"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "E7FA799CE8022FFE3DD5B27722318F519E833E2104DBC312C1FF0A9B82A3EFF0"
)
EXPECTED_CHANGED_LITERAL_COUNT = 14

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese is authoritative; every populated English, "
    "Simplified Chinese and Traditional Chinese auxiliary record and the "
    "completed Base Korean corpus were reviewed; four PK-only surrender "
    "records use Base only as semantic wording context, while nine records "
    "reuse complete approved Base Korean assemblies without inheriting "
    "Base runtime state; the plus signs, comma, neutral particle pair, "
    "three-offices terminology, chief-adviser title, Ou region name, "
    "full-width parenthesis, CR/LF shapes and hostile siege register are "
    "preserved; split record 4144 is fully assembled with five S1305 "
    "companions and this segment's terminal exclamation, with any present "
    "neighbor decision required to agree exactly; all thirty-eight slice "
    "prefills, calls, inline tokens, boundaries, reverse-order overlay, "
    "byte-exact restoration, two-run reproduction, tamper rejection, "
    "outside-scope identity and Steam read-only state are guarded"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1306_base",
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
        "EXPECTED_SPEAKER_STYLE_SHA256": EXPECTED_SPEAKER_STYLE_SHA256,
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


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
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
        len(rows) != 106
        or len(visible) != 197
        or visible[0] != "9:4083:0"
        or visible[-1] != "12:45:5"
    ):
        raise RuntimeError(f"segment {SEGMENT} B100 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 63
        or queue_slice[0] != "9:4144:5"
        or queue_slice[-1] != "12:45:5"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    if (
        len(prefilled) != 38
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
    return visible, queue_slice, prefilled, prefill_context, record_keys


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    values = BASE.context_evidence(prepared, records_by_label)
    for label, value, expected in (
        (
            "source target",
            values["source_target"],
            EXPECTED_SOURCE_TARGET_SHA256,
        ),
        (
            "current target",
            values["current_target"],
            EXPECTED_CURRENT_TARGET_SHA256,
        ),
        (
            "multilingual context",
            values["corpus"],
            EXPECTED_CONTEXT_CORPUS_SHA256,
        ),
        ("gap contract", values["gaps"], EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", values["boundary"], EXPECTED_BOUNDARY_SHA256),
        (
            "runtime control",
            values["controls"],
            EXPECTED_RUNTIME_CONTROL_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)
    actual_equality = {
        key: source == current
        for key, source, current in values["gaps"]
    }
    if (
        actual_equality != EXPECTED_SOURCE_CURRENT_GAP_EQUALITY
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
            context_rows.append(
                (
                    reference,
                    str(row["translation"]),
                    str(row["semantic_review"]),
                    str(row["runtime_review"]),
                )
            )

        owners: list[str] = []
        assembled: list[str] = []
        literal_evidence: list[tuple[Any, ...]] = []
        for literal_id in range(EXPECTED_ARITY[key]):
            coordinate = f"{key[0]}:{key[1]}:{literal_id}"
            if coordinate in TRANSLATIONS:
                translation = TRANSLATIONS[coordinate]
                owner = "segment"
                seen_target.add(coordinate)
            elif coordinate in CROSS_SEGMENT_COMPANION_COORDINATES:
                translation = MANUAL_CROSS_SEGMENT_TRANSLATIONS[coordinate]
                neighbor = neighbor_rows.get(coordinate)
                if neighbor is not None and (
                    neighbor.get("semantic_review") != "approved"
                    or neighbor.get("runtime_review") != "pending"
                    or str(neighbor.get("translation")) != translation
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} neighbor companion drifted: "
                        f"{coordinate}"
                    )
                seen_cross.add(coordinate)
                owner = "s1305_manual_companion"
            elif coordinate in PREFILL_COMPANION_COORDINATES:
                companion = prefill_rows.get(coordinate)
                if (
                    companion is None
                    or companion.get("semantic_review") != "approved"
                    or companion["base_exact_reuse_prefill"][
                        "runtime_promotion_authorized"
                    ]
                    is not False
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} prefill companion drifted: "
                        f"{coordinate}"
                    )
                translation = str(companion["translation"])
                seen_prefill.add(coordinate)
                owner = "base_exact_prefill_companion"
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} unowned companion: {coordinate}"
                )
            owners.append(owner)
            assembled.append(translation)
            literal_evidence.append((coordinate, owner, translation))

        donor_assembled: tuple[str, ...] = ()
        if key in EXACT_BASE_RECORD_KEYS:
            donor_assembled = tuple(
                str(base_rows[f"{key[0]}:{key[1]}:{literal_id}"][
                    "translation"
                ])
                for literal_id in range(EXPECTED_ARITY[key])
            )
            if tuple(assembled) != donor_assembled:
                raise RuntimeError(
                    f"segment {SEGMENT} exact Base assembly drifted: {key}"
                )
        if (
            (gap_bytes(source) == gap_bytes(current))
            != EXPECTED_SOURCE_CURRENT_GAP_EQUALITY[key]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} source/current gap relation drifted: "
                f"{key}"
            )
        base_evidence.append(
            (
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
                (
                    "complete_approved_base_assembly"
                    if key in EXACT_BASE_RECORD_KEYS
                    else "semantic_base_context_only"
                ),
            )
        )
        assembly_evidence.append(
            (
                key,
                tuple(owners),
                tuple(assembled),
                donor_assembled,
                runtime_controls(source),
                runtime_controls(current),
                (
                    "complete_translation_equals_approved_base"
                    if key in EXACT_BASE_RECORD_KEYS
                    else "manual_pk_semantic_adaptation"
                ),
                "base_runtime_state_not_inherited",
            )
        )
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
        len(replacements) != 63
        or len(prefilled) != 38
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
        "base_complete_record_match_kind": (
            "approved_complete_base_assembly"
            if key in EXACT_BASE_RECORD_KEYS
            else "none_semantic_context_only"
        ),
        "base_context_reference_coordinates": RECORD_BASE_CONTEXT[key],
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "cross_segment_companions_reviewed": key == (9, 4144),
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
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": dynamic,
        "runtime_review_required": dynamic,
        "runtime_promotion_authorized": False,
    }


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
    records = context_records(prepared)
    BASE.assert_context_contracts(prepared, records)
    BASE.assert_base_and_complete_assembly(prepared, records)
    BASE.assert_call_graphs(prepared)
    BASE.assert_semantics(records)
    candidate, candidate_sha256, changed = BASE.build_candidate(
        prepared,
        records,
    )
    combined_sha256, combined_changed = build_combined_slice_candidate(
        prepared,
        records,
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
        exact = key in EXACT_BASE_RECORD_KEYS
        references = RECORD_BASE_CONTEXT[key]
        rows.append(
            {
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
                "runtime_review": (
                    "pending" if dynamic else "not_required"
                ),
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "optional_neighbor_outputs_validated_if_present": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "cross_segment_companions_reviewed": key == (9, 4144),
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
                "base_wording_contextually_adapted": not exact,
                "manual_complete_base_donor_translation_selected": exact,
                "base_runtime_state_inherited": False,
                "speaker_style": style_map[key],
                "line_count_before": current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence": runtime_evidence(records, key),
            }
        )
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
    expected_counts = Counter(
        {
            "runtime_fragment_pending": len(DYNAMIC_COORDINATES),
            "retranslated": len(STATIC_COORDINATES),
        }
    )
    if (
        len(rows) != 25
        or len(validated) != 25
        or counts != expected_counts
        or any(
            row["semantic_review"] != "approved"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["line_count_preserved"] is not True
            for row in rows
        )
        or any(
            row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            for row in rows
            if row["scope_classification"] == "runtime_fragment_pending"
        )
        or any(
            row["runtime_review"] != "not_required"
            or row["layout_review"] != "unchanged_from_current"
            for row in rows
            if row["scope_classification"] == "retranslated"
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    if EXPECTED_CANDIDATE_SHA256 != "TO_PIN":
        install_base_globals()
        BASE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": SEGMENT_NAME,
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 63,
                "exact_reuse_prefill_count": 38,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_KEYS),
                "cross_segment_companion_count":
                len(CROSS_SEGMENT_COMPANION_COORDINATES),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "exact_complete_base_assembly_record_count":
                len(EXACT_BASE_RECORD_KEYS),
                "semantic_base_only_record_count":
                len(TARGET_RECORD_KEYS) - len(EXACT_BASE_RECORD_KEYS),
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
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
