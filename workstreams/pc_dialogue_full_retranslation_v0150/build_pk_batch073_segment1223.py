#!/usr/bin/env python3
"""Build source-redacted PK B073 segment 1223 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch070_segment1216.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B073_S1223.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B073_S1225.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1223
QUEUE_BATCH_ID = "pk_msggame-B073"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 8
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "8:427:0",
    "8:427:1",
    "8:428:0",
    "8:428:1",
    "8:429:1",
    "8:430:0",
    "8:430:1",
    "8:431:0",
    "8:431:1",
    "8:431:2",
    "8:432:0",
    "8:432:1",
    "8:433:0",
    "8:433:1",
    "8:433:2",
    "8:434:1",
    "8:435:0",
    "8:435:1",
    "8:436:0",
    "8:436:1",
    "8:437:1",
    "8:438:0",
    "8:438:1",
    "8:439:0",
    "8:439:1",
    "8:439:2",
    "8:440:0",
    "8:440:1",
    "8:441:0",
    "8:441:1",
    "8:441:2",
    "8:442:0",
    "8:442:1",
    "8:443:0",
    "8:443:1",
    "8:444:0",
    "8:445:0",
    "8:446:0",
    "8:446:1",
    "8:447:0",
    "8:447:1",
    "8:448:0",
    "8:448:1",
    "8:449:0",
    "8:449:1",
    "8:450:0",
    "8:450:1",
    "8:451:0",
    "8:451:1",
    "8:452:0",
    "8:452:1",
)
TRANSLATIONS = {
    "8:427:0": "에게 아들·",
    "8:427:1": "이(가) 탄생",
    "8:428:0": "에게 아들·",
    "8:428:1": "이(가) 탄생",
    "8:429:1": "이(가) 탄생",
    "8:430:0": "일문·",
    "8:430:1": "이(가) 「",
    "8:431:0": "일문·",
    "8:431:1": "에게 아들·",
    "8:431:2": "이(가) 탄생",
    "8:432:0": "휘하·",
    "8:432:1": "이(가) 「",
    "8:433:0": "휘하·",
    "8:433:1": "에게 아들·",
    "8:433:2": "이(가) 탄생",
    "8:434:1": "이(가) 탄생",
    "8:435:0": "에게 딸·",
    "8:435:1": "이(가) 탄생",
    "8:436:0": "에게 딸·",
    "8:436:1": "이(가) 탄생",
    "8:437:1": "이(가) 탄생",
    "8:438:0": "일문·",
    "8:438:1": "이(가) 「",
    "8:439:0": "일문·",
    "8:439:1": "에게 딸·",
    "8:439:2": "이(가) 탄생",
    "8:440:0": "휘하·",
    "8:440:1": "이(가) 「",
    "8:441:0": "휘하·",
    "8:441:1": "에게 딸·",
    "8:441:2": "이(가) 탄생",
    "8:442:0": "의 아들·",
    "8:442:1": "이(가) 「",
    "8:443:0": "의 아들·",
    "8:443:1": "이(가) 「",
    "8:444:0": "이(가) 「",
    "8:445:0": "이(가) 「",
    "8:446:0": "공주·",
    "8:446:1": "이(가) 출가",
    "8:447:0": "공주·",
    "8:447:1": "이(가) 사망",
    "8:448:0": "당주·",
    "8:448:1": "이(가) 사망",
    "8:449:0": "의 당주·",
    "8:449:1": "이(가) 사망",
    "8:450:0": "군단장·",
    "8:450:1": "이(가) 사망",
    "8:451:0": "가신·",
    "8:451:1": "이(가) 사망",
    "8:452:0": "성주·",
    "8:452:1": "이(가) 사망",
}
TARGET_RECORD_IDS = tuple(range(427, 453))
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    427: 2,
    428: 2,
    429: 2,
    430: 3,
    431: 3,
    432: 3,
    433: 3,
    434: 2,
    435: 2,
    436: 2,
    437: 2,
    438: 3,
    439: 3,
    440: 3,
    441: 3,
    442: 3,
    443: 3,
    444: 2,
    445: 2,
    446: 2,
    447: 2,
    448: 2,
    449: 2,
    450: 2,
    451: 2,
    452: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "8:429:0",
    "8:430:2",
    "8:432:2",
    "8:434:0",
    "8:437:0",
    "8:438:2",
    "8:440:2",
    "8:442:2",
    "8:443:2",
    "8:444:1",
    "8:445:1",
)
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR = {
    record_id: (8, record_id - 12)
    for record_id in TARGET_RECORD_IDS
}
SEMANTIC_BASE_CONTEXT: dict[int, tuple[str, ...]] = {}
EXPECTED_BASE_RAW_MATCHES = {
    427: ((8, 415), (8, 416)),
    428: ((8, 415), (8, 416)),
    429: ((8, 417),),
    430: ((8, 418),),
    431: ((8, 419),),
    432: ((8, 420),),
    433: ((8, 421),),
    434: ((8, 422),),
    435: ((8, 423), (8, 424)),
    436: ((8, 423), (8, 424)),
    437: ((8, 425),),
    438: ((8, 426),),
    439: ((8, 427),),
    440: ((8, 428),),
    441: ((8, 429),),
    442: ((8, 430), (8, 431)),
    443: ((8, 430), (8, 431)),
    444: ((8, 432), (8, 433)),
    445: ((8, 432), (8, 433)),
    446: ((8, 434),),
    447: ((8, 435),),
    448: ((8, 436),),
    449: ((8, 437),),
    450: ((8, 438),),
    451: ((8, 439),),
    452: ((8, 440),),
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (8, record_id)
    for record_id in (
        *range(415, 453),
        457,
        458,
        516,
        517,
    )
)
SOURCE_CALL_ROOTS = (8,)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    427: ((), ("024733", "024633")),
    428: ((), ("024733", "024633")),
    429: ((), ("024633",)),
    430: ((), ("024733", "024633")),
    431: ((), ("024733", "024633")),
    432: ((), ("024733", "024633")),
    433: ((), ("024733", "024633")),
    434: ((), ("024633",)),
    435: ((), ("024733", "024633")),
    436: ((), ("024733", "024633")),
    437: ((), ("024633",)),
    438: ((), ("024733", "024633")),
    439: ((), ("024733", "024633")),
    440: ((), ("024733", "024633")),
    441: ((), ("024733", "024633")),
    442: ((), ("024733", "024633", "02463F")),
    443: ((), ("024733", "024633", "02463F")),
    444: ((), ("024633", "02463F")),
    445: ((), ("024633", "02463F")),
    446: ((), ("024633",)),
    447: ((), ("024633",)),
    448: ((), ("024633",)),
    449: ((), ("02463E", "024633")),
    450: ((), ("024633",)),
    451: ((), ("024633",)),
    452: ((), ("024633",)),
}
SPEAKER_STYLE = tuple(
    (
        record_id,
        (
            "family_birth_or_adoption_ui"
            if record_id <= 441
            else "genpuku_ui"
            if record_id <= 445
            else "family_or_officer_death_ui"
        ),
    )
    for record_id in TARGET_RECORD_IDS
)
TERMINOLOGY_POLICY = (
    ("son", "아들"),
    ("daughter", "딸"),
    ("adopted son", "양자"),
    ("adopted daughter", "양녀"),
    ("genpuku coming-of-age", "원복"),
    ("princess", "공주"),
    ("clan head", "당주"),
    ("corps commander", "군단장"),
    ("castle lord", "성주"),
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
    "CAC189E296B414378B7B1F2FB5134E76DBBAAFE4DD2FF26CB8A3041DA0BFAA35"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "D3CB354358DA93DDFC44E49B2AEE7814556D04D534AC66ABB028C31F1D403ED5"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "C3F19D439D0163D000F8E4F2E6126256E75C0BBE6F917401E0BE77F31FD5EE28"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "A794C991BDBC0993C28B97F2F279AA13C0E8110D0A71F556C0DF2F04BEB2F7D5"
)
EXPECTED_ZERO_MIDDLE_PREFILL_SHA256 = (
    "BFB2A6DA97A50CE8D2FED93D93B17879D323ECB7C4345688F53A0DEDC3B55E23"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "98B239C3177722B8E504A53F8FA23A1E380CC6825CD57372507FBE6237477B44"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "5FE2C7E1DC4C76978F990A3C2585EC9F20DB9FFDE7E66EF4910923386A49C298"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "86791B9EE7A3DC9D5004F278508E89144CBA1919A73E4F44B9CB79FD0243B5F3"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "5FD35D89DF4AA689D48185B9B3B27B2DA559550F564662F13A082E72F9B83648"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "F122CEE16FA7D6781CEA67759B675CA82BEA3A810D981A890A4B9F63B1E496E0"
)
EXPECTED_BOUNDARY_SHA256 = (
    "CB2ED3C8D6A4D7F69557E04C18971DB0FFD9A6937BD2B898A7B2563579B64044"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "D20B32CDAC18EE348FF18FC127A46497A3B01E4E3781A7AD4D4AD7EA24237DA6"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "1E85438CF075F48240C1FA3A03C67D12F6C09D9C8C51585CA7DCBDD9BC8B88E6"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "504ABA5DB32359D91A1F142F0CD0F7904D3CD33CC3ED8FC55E90D6018CFA830E"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "34F168518E1698E7FE9E5BC5D2252B8EBD655E803B6CE7BBC2DB0A0E5D20F05B"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "A1C4C22D2F5765A2CF713541982B6AB6881BFDF3080B3748803824705E1D4526"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "D42A48933317AF76D72E32F6497B19916358458DE4B0147A3A96439C38CF5781"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "F077F500BB3BDCC27AA3AC1E72A0AF9C9A42E2C6CB30FF62DC7F0EA0ADCE5D28"
)
EXPECTED_CANDIDATE_SHA256 = (
    "BC83B82FF7042CAC69D0B08FCD5516B611CD7E4735C905A5EBD9AF65A12CBAC8"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "4D71854F30B42B9E7D8417550066C4B0691665D5EA74B590E25BA9B9E22357AF"
)
EXPECTED_CHANGED_LITERAL_COUNT = 38
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 53

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative and all twenty-six complete records are "
    "raw-exact to completed Base donors; all eleven same-record companions, "
    "all sixteen slice prefills, and the zero-residual middle slice of "
    "sixty-seven exact prefills are validated; Base runtime and VM state are "
    "never inherited; birth, adoption, genpuku and death terminology, person "
    "and location tokens, protected outer whitespace, source and current gaps, "
    "zero-middle queue boundaries, two-run reproduction, tamper rejection, "
    "reverse overlays, outside-scope identity, and Steam read-only state are "
    "guarded"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1223_base",
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


def prefill_context_row(
    coordinate: str,
    prefill_rows: dict[str, dict[str, Any]],
) -> tuple[Any, ...]:
    row = prefill_rows[coordinate]
    return (
        coordinate,
        str(row["translation"]),
        str(row["source_record_raw_sha256"]),
        str(row["current_ko_utf16le_sha256"]),
        str(row["semantic_review"]),
        str(row["runtime_review"]),
        str(row["layout_review"]),
        str(row["base_exact_reuse_prefill"]["base_coordinate"]),
        str(
            row["base_exact_reuse_prefill"]["translation_utf16le_sha256"]
        ),
        bool(
            row["base_exact_reuse_prefill"][
                "runtime_promotion_authorized"
            ]
        ),
    )


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
        len(rows) != 140
        or len(visible) != 199
        or visible[0] != "8:427:0"
        or visible[-1] != "8:566:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B073 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "8:427:0"
        or queue_slice[-1] != "8:457:0"
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
        len(prefilled) != 16
        or len(residual) != 51
        or residual != TARGET_COORDINATES
    ):
        raise RuntimeError(f"segment {SEGMENT} prefill slice drifted")
    zero_middle = visible[67:134]
    if (
        len(zero_middle) != 67
        or zero_middle[0] != "8:458:0"
        or zero_middle[-1] != "8:516:0"
        or any(coordinate not in prefill_rows for coordinate in zero_middle)
    ):
        raise RuntimeError(f"segment {SEGMENT} zero middle slice drifted")
    zero_middle_context = tuple(
        prefill_context_row(coordinate, prefill_rows)
        for coordinate in zero_middle
    )
    if any(
        row[4] != "approved"
        or row[5] not in {"pending", "not_required"}
        or row[6] != "unchanged_from_current"
        or row[9] is not False
        for row in zero_middle_context
    ):
        raise RuntimeError(f"segment {SEGMENT} zero middle prefill drifted")
    CORE.guarded_digest(
        "zero middle prefill",
        zero_middle_context,
        EXPECTED_ZERO_MIDDLE_PREFILL_SHA256,
    )
    prefill_context = tuple(
        prefill_context_row(coordinate, prefill_rows)
        for coordinate in prefilled
    )
    record_keys = tuple(
        tuple(int(value) for value in str(row["record_coordinate"]).split(":"))
        for row in rows
    )
    if len(record_keys) != len(set(record_keys)):
        raise RuntimeError(f"segment {SEGMENT} duplicate queue records")
    return visible, queue_slice, prefilled, prefill_context, record_keys


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
        or len(prefilled) != 16
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


OVERRIDES = (
    "SCRIPT",
    "OUTPUT",
    "PREFILL",
    "BASE_PROMOTED",
    "OPTIONAL_NEIGHBORS",
    "STEAM_PK",
    "SEGMENT",
    "QUEUE_BATCH_ID",
    "QUEUE_START",
    "QUEUE_STOP",
    "BLOCK_ID",
    "PK_RECORD_COUNT",
    "TARGET_COORDINATES",
    "TRANSLATIONS",
    "TARGET_RECORD_IDS",
    "STATIC_RECORD_IDS",
    "DYNAMIC_RECORD_IDS",
    "STATIC_COORDINATES",
    "DYNAMIC_COORDINATES",
    "EXPECTED_ARITY",
    "PREFILL_COMPANION_COORDINATES",
    "HIDDEN_CURRENT_COMPANION_COORDINATES",
    "EXACT_BASE_DONOR",
    "SEMANTIC_BASE_CONTEXT",
    "EXPECTED_BASE_RAW_MATCHES",
    "EXPECTED_BASE_LITERAL_MATCHES",
    "EXPECTED_BASE_MASKED_MATCHES",
    "BOUNDARY_RECORD_KEYS",
    "SOURCE_CALL_ROOTS",
    "CURRENT_CALL_ROOTS",
    "EXPECTED_CONTROLS_BY_RECORD",
    "SPEAKER_STYLE",
    "TERMINOLOGY_POLICY",
    "EXPECTED_STEAM_PK_SHA256",
    "EXPECTED_PRISTINE_PK_SHA256",
    "EXPECTED_PREFILL_SHA256",
    "EXPECTED_BASE_PROMOTED_SHA256",
    "EXPECTED_QUEUE_UNIVERSE_SHA256",
    "EXPECTED_QUEUE_SLICE_SHA256",
    "EXPECTED_PREFILLED_COORDINATE_SHA256",
    "EXPECTED_PREFILL_SLICE_CONTEXT_SHA256",
    "EXPECTED_TARGET_COORDINATE_SHA256",
    "EXPECTED_SOURCE_TARGET_SHA256",
    "EXPECTED_CURRENT_TARGET_SHA256",
    "EXPECTED_CONTEXT_CORPUS_SHA256",
    "EXPECTED_GAP_CONTRACT_SHA256",
    "EXPECTED_BOUNDARY_SHA256",
    "EXPECTED_RUNTIME_CONTROL_SHA256",
    "EXPECTED_BASE_SEARCH_SHA256",
    "EXPECTED_COMPLETE_ASSEMBLY_SHA256",
    "EXPECTED_CALL_GRAPH_SHA256",
    "EXPECTED_SPEAKER_STYLE_SHA256",
    "EXPECTED_TERMINOLOGY_POLICY_SHA256",
    "EXPECTED_TRANSLATION_POLICY_SHA256",
    "EXPECTED_CANDIDATE_SHA256",
    "EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256",
    "EXPECTED_CHANGED_LITERAL_COUNT",
    "EXPECTED_COMBINED_CHANGED_LITERAL_COUNT",
    "DISCOVERED_PINS",
    "BASIS",
    "queue_evidence",
    "build_combined_slice_candidate",
)


def install_base_globals() -> None:
    for name in OVERRIDES:
        setattr(BASE, name, globals()[name])


def propagate_for_tamper() -> None:
    install_base_globals()
    module = BASE
    while True:
        if hasattr(module, "install_base_globals"):
            module.install_base_globals()
        if hasattr(module, "propagate_base_globals"):
            module.propagate_base_globals()
            return
        module = module.BASE


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
    return BASE.build_rows()


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
        len(rows) != 51
        or len(validated) != 51
        or counts != Counter({"runtime_fragment_pending": 51})
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
    propagate_for_tamper()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B073_S1223",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "approved": len(rows),
                "queue_slice_visible_count": 67,
                "exact_reuse_prefill_count": 16,
                "zero_middle_exact_prefill_count": 67,
                "residual_count": len(rows),
                "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "raw_exact_complete_base_donor_record_count":
                len(EXACT_BASE_DONOR),
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
                "zero_middle_prefill_guarded": True,
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
