#!/usr/bin/env python3
"""Build source-redacted PK B052 segment 1168 residual decisions."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B052_S1168.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B052_S1167.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B052_S1169.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1168
QUEUE_BATCH_ID = "pk_msggame-B052"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751

TARGET_COORDINATES = (
    "7:273:1",
    "7:274:1",
    "7:277:2",
    "7:280:0",
    "7:281:0",
    "7:281:1",
    "7:283:0",
    "7:283:1",
    "7:284:0",
    "7:285:0",
    "7:293:0",
    "7:301:0",
)
TRANSLATIONS = {
    "7:273:1": "……\n이후로는 「",
    "7:274:1": "……\n이 「",
    "7:277:2": "으리라",
    "7:280:0": "을(를) 비롯해 총",
    "7:281:0": "이(가) 「",
    "7:281:1": "」에 귀순한다",
    "7:283:0": "을(를) 비롯한 이들이 「",
    "7:283:1": "」에 귀순한다",
    "7:284:0": "님을 비롯한 총",
    "7:285:0": "거절한다",
    "7:293:0": "거절한다",
    "7:301:0": "거절한다!",
}
STATIC_RECORD_IDS = (285, 293, 301)
TARGET_RECORD_IDS = (273, 274, 277, 280, 281, 283, 284, 285, 293, 301)
DYNAMIC_RECORD_IDS = tuple(
    record_id
    for record_id in TARGET_RECORD_IDS
    if record_id not in STATIC_RECORD_IDS
)
STATIC_COORDINATES = {
    coordinate
    for coordinate in TARGET_COORDINATES
    if int(coordinate.split(":")[1]) in STATIC_RECORD_IDS
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
EXPECTED_ARITY = {
    273: 3,
    274: 3,
    277: 3,
    280: 2,
    281: 2,
    283: 2,
    284: 3,
    285: 1,
    293: 1,
    301: 1,
}
PREFILL_COMPANION_COORDINATES = (
    "7:273:0",
    "7:273:2",
    "7:274:0",
    "7:274:2",
    "7:277:0",
    "7:277:1",
    "7:280:1",
    "7:284:1",
    "7:284:2",
)
PRIMARY_BASE_DONOR = {
    273: (7, 269),
    274: (7, 270),
    277: (7, 273),
    280: (7, 276),
    281: (7, 277),
    283: (7, 279),
    284: (7, 280),
    285: (7, 281),
    293: (7, 289),
    301: (7, 297),
}
EXPECTED_BASE_RAW_MATCHES = {
    273: (),
    274: (),
    277: (),
    280: ((7, 276),),
    281: ((7, 277),),
    283: ((7, 279),),
    284: ((7, 280),),
    285: ((7, 281), (7, 289)),
    293: ((7, 281), (7, 289)),
    301: ((7, 297),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    273: ((7, 269),),
    274: ((7, 270),),
    277: ((7, 273),),
    280: ((7, 276),),
    281: ((7, 277),),
    283: ((7, 279),),
    284: ((7, 280),),
    285: ((7, 281), (7, 289)),
    293: ((7, 281), (7, 289)),
    301: ((7, 297),),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (7, record_id)
    for record_id in (
        268, 269, 270, 272, 273, 274, 275, 276, 277, 278,
        279, 280, 281, 282, 283, 284, 285, 286, 292, 293,
        294, 300, 301, 302, 315, 316,
    )
)
SOURCE_CALL_ROOTS = (8, 376, 538, 742, 1066, 1090, 1162)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    273: ((538, 8, 1066), ()),
    274: ((742, 1162), ("024633",)),
    277: ((8, 376, 1090), ()),
    280: ((), ("024633", "0232")),
    281: ((), ("024833", "025032")),
    283: ((), ("024833", "025032")),
    284: ((), ("024833", "0232", "025032")),
    285: ((), ()),
    293: ((), ()),
    301: ((), ()),
}
SPEAKER_STYLE = (
    (273, "defeated_house_retainer_acceptance_register"),
    (274, "defeated_house_retainer_acceptance_register"),
    (277, "spared_captive_retainer_acceptance_register"),
    (280, "recruitment_result_ui"),
    (281, "single_officer_surrender_result_ui"),
    (283, "multiple_officer_surrender_result_ui"),
    (284, "captured_officer_surrender_result_ui"),
    (285, "retainer_refusal_plain_register"),
    (293, "retainer_refusal_plain_register"),
    (301, "retainer_refusal_forceful_register"),
)
TERMINOLOGY_POLICY = (
    ("realm", "천하"),
    ("lord", "주군"),
    ("retainer", "가신"),
    ("surrender allegiance", "귀순"),
    ("recruitment", "등용"),
    ("captured", "포박"),
    ("refuse", "거절한다"),
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
    "3423DC47CAB5B32C64452817ACF6DDB2E33CCA2B995205EC407E96FB9F1FF14B"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "3DCEF06A4CAD96319A5D0D65CC91771FB7B0294760647AD46DAB4BB86978F47D"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "B9FF97FAAD699444D8194E0098AAC10518001F42F8F700DF9E0FFE1E8F06B6DF"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "4DD022BD23A20DF5A8E8288859C9C6632F28E106FC4B898517DFA6D3D49EA4D6"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "B422E42882D799B028169A322BE57E525697BDAC0C5BFE0A2DCE4E4B37B530B0"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "5CF2432BEA4E0C4E7C7A72B6B58C0EE436147106787DA6D1464824C02B9B97C2"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "4B6F15B24771274DEC2711E2E1262F5E34AC1F51DF6F5CDBAD27B9AC321C7781"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "D4A2CFC7ECF92CD2AE329E00CDD6621CE6028CE92D25A08224D841566600EF77"
)
EXPECTED_BOUNDARY_SHA256 = (
    "89D29CA3AA230E28E7F02E76AB2E6864DDEDC26834BF6C6AB74806F64ACDA2A4"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "8827645CB22D1EE79E18F0BBCBC157E4322844D00A12B9486D2AFD5B2B8FF7AB"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "9D797A37F780C1AE4DC17B4B6B1D93CC099E1B20E285322CDED8081B7103EF67"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "8B41BB72BE2A7029F0FE4CF88CE00E0FBA1E4AF05295C557CBDEEB3A5349A74D"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "792FA105FF66E6DDD2EB81DAA5235D8C26BB617F99CF527BA0E4267246C45DD1"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "DDD6631E00BDE4BC33E23ED776272D63CE2860487BD258CEC53F058EC4477C29"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "A190DAB1447A8AA1F3CE6E5F55BF46A6312779433D1B729EE41BBD25E07AA892"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "9348968BCE129F2E3B0163718E099CB310664C547B4A43B86A86E536EB335D01"
)
EXPECTED_CANDIDATE_SHA256 = (
    "80F1F27BD9A09D178898F1448EFBFA054CE5FE824CA7C879BEDBDCE3B9BCA9A6"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "C53B453D4A560E42F1EEC3CC97362DFC1A6D2369D40734402656736AFEFEF5BE"
)
EXPECTED_CHANGED_LITERAL_COUNT = 11
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 52

DISCOVERED_PINS: dict[str, str] = {}
ALL_CALL_RE = re.compile(b"\x01([\x43\x4A])(.{4})", re.DOTALL)
BASIS = (
    "pristine PK JP is authoritative and complete PK EN SC TC records "
    "were reviewed; every residual has a completed Base source donor with "
    "the same complete literal sequence, with seven records byte-exact and "
    "three differing only in guarded direct-call operands; completed Base "
    "Korean wording is manually selected for semantic and terminology "
    "consistency while Base runtime and VM state are never inherited; all "
    "fifty-five queue prefills and the nine same-record companions are "
    "validated; complete records, calls, tokens, particles, quotes, "
    "newlines, protected outer whitespace, queue and segment boundaries, "
    "two-run reproduction, tamper rejection, reverse overlays, outside-"
    "scope identity, and Steam read-only state are guarded"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1168_parent",
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


def patch_parent_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
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
        "STATIC_RECORD_IDS": STATIC_RECORD_IDS,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
    }
    for name, value in values.items():
        setattr(PARENT, name, value)
    PARENT.patch_parent_globals()


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
        len(rows) != 158
        or len(visible) != 200
        or visible[0] != "7:209:0"
        or visible[-1] != "7:366:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B052 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "7:269:0"
        or queue_slice[-1] != "7:315:0"
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
    if len(prefilled) != 55 or residual != TARGET_COORDINATES:
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


def assert_queue_and_residual_contract(prepared: Any) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} pinned source input drifted")
    ENGINE.validate_decisions(prepared, PREFILL, require_complete=False)
    visible, queue_slice, prefilled, prefill_context, _ = queue_evidence(
        prepared
    )
    guarded_digest("queue universe", visible, EXPECTED_QUEUE_UNIVERSE_SHA256)
    guarded_digest("queue slice", queue_slice, EXPECTED_QUEUE_SLICE_SHA256)
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
    guarded_digest(
        "prefill slice context",
        prefill_context,
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
    )
    existing: dict[str, str] = {}
    for path in sorted(DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        ENGINE.validate_decisions(prepared, path, require_complete=False)
        for row in read_jsonl(path):
            coordinate = row.get("coordinate")
            if (
                row.get("resource") != "pk_msggame"
                or not isinstance(coordinate, str)
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} mixed predecessor: {path}"
                )
            previous = existing.setdefault(coordinate, path.name)
            if previous != path.name:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate predecessor: {coordinate}"
                )
    residual = tuple(
        coordinate for coordinate in queue_slice if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: {len(residual)} rows"
        )
    optional_present: list[str] = []
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            ENGINE.validate_decisions(prepared, path, require_complete=False)
            optional_present.append(path.name)
    return tuple(optional_present)


def context_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[str, Any]:
    _, _, _, _, record_keys = queue_evidence(prepared)
    source_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["jp"],
                coordinate_key(coordinate)[:2],
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    current_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["current"],
                coordinate_key(coordinate)[:2],
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    corpus = tuple(
        (
            label,
            key,
            sha256_bytes(records[key].data),
            literal_texts(records, key),
        )
        for label, records in records_by_label.items()
        for key in record_keys
    )
    gaps = tuple(
        (
            record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["jp"][(BLOCK_ID, record_id)]
                )
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["current"][(BLOCK_ID, record_id)]
                )
            ),
        )
        for record_id in TARGET_RECORD_IDS
    )
    boundary = tuple(
        (
            label,
            key,
            sha256_bytes(records_by_label[label][key].data),
            literal_texts(records_by_label[label], key),
            tuple(
                value.hex().upper()
                for value in gap_bytes(records_by_label[label][key])
            ),
        )
        for label in ("jp", "current", "en", "sc", "tc")
        for key in BOUNDARY_RECORD_KEYS
    )
    controls = tuple(
        (
            label,
            record_id,
            runtime_controls(
                records_by_label[label][(BLOCK_ID, record_id)]
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    return {
        "source_target": source_target,
        "current_target": current_target,
        "corpus": corpus,
        "gaps": gaps,
        "boundary": boundary,
        "controls": controls,
    }


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    values = context_evidence(prepared, records_by_label)
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
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_prefill: set[str] = set()
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
            or raw_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
            or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[record_id]
            or masked_matches != EXPECTED_BASE_MASKED_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base donor drifted: {record_id}"
            )
        donor_key = PRIMARY_BASE_DONOR[record_id]
        donor_coordinates = tuple(
            f"{donor_key[0]}:{donor_key[1]}:{literal_id}"
            for literal_id in range(EXPECTED_ARITY[record_id])
        )
        donor_rows: list[dict[str, Any]] = []
        assembled: list[str] = []
        owners: list[str] = []
        for literal_id, donor_coordinate in enumerate(donor_coordinates):
            row = base_rows.get(donor_coordinate)
            if (
                row is None
                or row.get("semantic_review") != "approved"
                or row.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} missing Base donor: "
                    f"{donor_coordinate}"
                )
            donor_rows.append(row)
            coordinate = f"{BLOCK_ID}:{record_id}:{literal_id}"
            if coordinate in TRANSLATIONS:
                assembled.append(TRANSLATIONS[coordinate])
                owners.append("segment_manual")
                seen_target.add(coordinate)
                continue
            prefill = prefill_rows.get(coordinate)
            if (
                prefill is None
                or coordinate not in PREFILL_COMPANION_COORDINATES
                or prefill.get("semantic_review") != "approved"
                or prefill.get("runtime_review") != "pending"
                or prefill["base_exact_reuse_prefill"][
                    "runtime_promotion_authorized"
                ]
                is not False
                or prefill["base_exact_reuse_prefill"]["base_coordinate"]
                != donor_coordinate
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} companion drifted: {coordinate}"
                )
            assembled.append(str(prefill["translation"]))
            owners.append("base_exact_prefill_runtime_pending")
            seen_prefill.add(coordinate)
        donor_translations = tuple(
            str(row["translation"]) for row in donor_rows
        )
        if tuple(assembled) != donor_translations:
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
                donor_key,
                tuple(
                    (
                        coordinate,
                        str(row["translation"]),
                        str(row["semantic_review"]),
                        str(row["runtime_review"]),
                    )
                    for coordinate, row in zip(
                        donor_coordinates,
                        donor_rows,
                    )
                ),
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(assembled),
                donor_translations,
                runtime_controls(source),
                runtime_controls(records_by_label["current"][key]),
                (
                    "raw_complete_record_donor"
                    if raw_matches
                    else "masked_call_operand_complete_record_donor"
                ),
                "base_runtime_state_not_inherited",
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
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


def call_graph_evidence(prepared: Any) -> tuple[Any, ...]:
    evidence: list[tuple[Any, ...]] = []
    for label, archive, roots in (
        (
            "jp",
            prepared.resources["pk_msggame"].pristine_archive,
            SOURCE_CALL_ROOTS,
        ),
        (
            "current",
            prepared.resources["pk_msggame"].current_archive,
            CURRENT_CALL_ROOTS,
        ),
    ):
        records = ENGINE.archive_records(archive)
        for operand in roots:
            graph, terminals = reachable_call_graph(records, (0, operand))
            if not graph or not terminals:
                raise RuntimeError(
                    f"segment {SEGMENT} call graph drifted: "
                    f"{label}:{operand}"
                )
            evidence.append(
                (
                    label,
                    operand,
                    graph,
                    terminals,
                    tuple(
                        literal_texts(records, coordinate)
                        for coordinate in terminals
                    ),
                )
            )
    return tuple(evidence)


def assert_call_graphs(prepared: Any) -> None:
    guarded_digest(
        "call graph",
        call_graph_evidence(prepared),
        EXPECTED_CALL_GRAPH_SHA256,
    )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    guarded_digest(
        "target coordinate",
        TARGET_COORDINATES,
        EXPECTED_TARGET_COORDINATE_SHA256,
    )
    guarded_digest(
        "translation policy",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    guarded_digest(
        "speaker style",
        SPEAKER_STYLE,
        EXPECTED_SPEAKER_STYLE_SHA256,
    )
    guarded_digest(
        "terminology policy",
        TERMINOLOGY_POLICY,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    changed_coordinates = tuple(
        coordinate
        for coordinate, translation in TRANSLATIONS.items()
        if translation
        != literal_texts(
            records_by_label["current"],
            coordinate_key(coordinate)[:2],
        )[coordinate_key(coordinate)[2]]
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES | STATIC_COORDINATES
        != set(TARGET_COORDINATES)
        or DYNAMIC_COORDINATES & STATIC_COORDINATES
        or len(changed_coordinates) != EXPECTED_CHANGED_LITERAL_COUNT
        or ENGINE.KANA_OR_HAN_RE.search(SCRIPT.read_text(encoding="utf-8"))
    ):
        raise RuntimeError(f"segment {SEGMENT} semantic policy drifted")
    for coordinate, translation in TRANSLATIONS.items():
        key = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"],
            key[:2],
        )[key[2]]
        dynamic = coordinate in DYNAMIC_COORDINATES
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            "runtime_pending" if dynamic else "unchanged_from_current",
            coordinate,
        )
        if (
            translation.count("\n") != current_text.count("\n")
            or ENGINE.protected_signature(translation)
            != ENGINE.protected_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} shape drifted: {coordinate}"
            )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_parent_globals()
    candidate, candidate_sha256, changed = PARENT.unchecked_candidate(
        prepared,
        records_by_label,
    )
    if (
        EXPECTED_CANDIDATE_SHA256 != "TO_PIN"
        and candidate_sha256 != EXPECTED_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate drifted: {candidate_sha256}"
        )
    if changed != EXPECTED_CHANGED_LITERAL_COUNT:
        raise RuntimeError(
            f"segment {SEGMENT} changed count drifted: {changed}"
        )
    if EXPECTED_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS["candidate"] = candidate_sha256
    return candidate, candidate_sha256, changed


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
        or len(prefilled) != 55
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
    record_id: int,
) -> dict[str, Any]:
    source = records_by_label["jp"][(BLOCK_ID, record_id)]
    current = records_by_label["current"][(BLOCK_ID, record_id)]
    source_controls = runtime_controls(source)
    current_controls = runtime_controls(current)
    dynamic = record_id in DYNAMIC_RECORD_IDS
    donor_key = PRIMARY_BASE_DONOR[record_id]
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
            if EXPECTED_BASE_RAW_MATCHES[record_id]
            else "literal_and_masked_call_graph_exact"
        ),
        "base_complete_record_coordinate":
        f"{donor_key[0]}:{donor_key[1]}",
        "base_complete_record_match_coordinates": tuple(
            f"{key[0]}:{key[1]}"
            for key in EXPECTED_BASE_LITERAL_MATCHES[record_id]
        ),
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "same_record_prefill_companion_reviewed":
        any(
            coordinate.startswith(f"{BLOCK_ID}:{record_id}:")
            for coordinate in PREFILL_COMPANION_COORDINATES
        ),
        "manual_multilingual_context_reviewed": True,
        "completed_base_donor_reviewed": True,
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
    patch_parent_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records = context_records(prepared)
    assert_context_contracts(prepared, records)
    assert_base_and_complete_assembly(prepared, records)
    assert_call_graphs(prepared)
    assert_semantics(records)
    candidate, candidate_sha256, changed = build_candidate(
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
        current_text = literal_texts(
            records["current"],
            (block_id, record_id),
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        donor_key = PRIMARY_BASE_DONOR[record_id]
        donor_coordinates = tuple(
            f"{donor_key[0]}:{donor_key[1]}:{index}"
            for index in range(EXPECTED_ARITY[record_id])
        )
        dynamic = coordinate in DYNAMIC_COORDINATES
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
                "same_record_prefill_companion_reviewed":
                record_id in {273, 274, 277, 280, 284},
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "completed_base_corpus_searched": True,
                "base_context_reference_coordinate":
                donor_coordinates[literal_id],
                "base_context_reference_coordinates": donor_coordinates,
                "base_context_is_automatic_reuse": False,
                "base_wording_contextually_adapted": False,
                "manual_complete_base_donor_translation_selected": True,
                "base_runtime_state_inherited": False,
                "speaker_style": style_map[record_id],
                "line_count_before": current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_evidence(records, record_id),
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


def assert_tamper_rejection(
    prepared: Any,
    rows: list[dict[str, Any]],
    candidate: bytes,
) -> None:
    patch_parent_globals()
    PARENT.assert_tamper_rejection(prepared, rows, candidate)


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
        print(json.dumps(
            DISCOVERED_PINS,
            sort_keys=True,
            separators=(",", ":"),
        ))
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
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    expected_counts = Counter({
        "runtime_fragment_pending": len(DYNAMIC_COORDINATES),
        "retranslated": len(STATIC_COORDINATES),
    })
    if (
        len(rows) != 12
        or len(validated) != 12
        or counts != expected_counts
        or any(
            row["semantic_review"] != "approved"
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
    assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(json.dumps({
        "status": "ok",
        "segment": "pk_msggame_B052_S1168",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "approved": len(rows),
        "scope_classification_counts": dict(counts),
        "queue_slice_visible_count": 67,
        "exact_reuse_prefill_count": 55,
        "residual_count": len(rows),
        "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
        "same_record_prefill_companion_count":
        len(PREFILL_COMPANION_COORDINATES),
        "raw_exact_complete_base_donor_record_count":
        sum(bool(value) for value in EXPECTED_BASE_RAW_MATCHES.values()),
        "masked_complete_base_donor_record_count":
        sum(not bool(value) for value in EXPECTED_BASE_RAW_MATCHES.values()),
        "source_call_root_count": len(SOURCE_CALL_ROOTS),
        "current_call_root_count": len(CURRENT_CALL_ROOTS),
        "optional_neighbors_present": list(optional_present),
        "changed_literal_count": changed,
        "unchanged_literal_count": len(rows) - changed,
        "combined_slice_changed_literal_count": combined_changed,
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
    }, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
