#!/usr/bin/env python3
"""Build source-redacted PK B054 segment 1174 residual decisions."""

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
PARENT_PATH = WORKSTREAM / "build_pk_batch053_segment1171.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B054_S1174.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B054_S1173.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B054_S1175.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1174
QUEUE_BATCH_ID = "pk_msggame-B054"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "7:592:0",
    "7:606:0", "7:606:1",
    "7:607:0", "7:607:1", "7:607:2",
    "7:608:0", "7:608:1",
    "7:609:0",
    "7:610:0",
    "7:611:0",
    "7:612:0",
    "7:613:0",
    "7:615:0",
    "7:616:0",
    "7:617:0",
    "7:618:0",
    "7:619:0",
    "7:620:0",
    "7:621:1",
    "7:622:0",
    "7:624:1",
    "7:625:0", "7:625:1",
    "7:626:0",
    "7:627:0",
    "7:628:0",
    "7:630:0",
    "7:631:0",
    "7:632:0",
    "7:634:0",
    "7:635:0",
    "7:636:1",
    "7:637:0",
    "7:638:0",
    "7:639:0",
)
TRANSLATIONS = {
    "7:592:0": "아무리 「",
    "7:606:0": "이(가)",
    "7:606:1": "에 입성",
    "7:607:0": "들",
    "7:607:1": "명이",
    "7:607:2": "에 입성",
    "7:608:0": "설마 「",
    "7:608:1": "」이(가) 함락될 줄이야",
    "7:609:0": "은(는) 반드시 되찾고 말겠다",
    "7:610:0": "을(를) 잃다니 면목이 없구나…",
    "7:611:0": "은(는) 반드시 되찾아 주마!",
    "7:612:0": "을(를) 잃었어도 목숨까지 잃을 수는 없다",
    "7:613:0": "은(는) 언젠가 되찾으러 오겠다",
    "7:615:0": "의 방비를 지나치게 믿었던 것인가…",
    "7:616:0": "이(가) 함락되었나",
    "7:617:0": "은(는) 언젠가 반드시 되찾겠다",
    "7:618:0": "을(를) 잃게 될 줄이야",
    "7:619:0": "은(는) 버릴 수밖에 없겠구나!",
    "7:620:0": "이(가) 함락되다니!",
    "7:621:1": "」은(는) 반드시 되찾겠다!",
    "7:622:0": "을(를) 빼앗긴 건 큰 타격이군…",
    "7:624:1": "」이(가) 함락됐다!",
    "7:625:0": "제기랄, 「",
    "7:625:1": "」은(는) 이제 끝인가!",
    "7:626:0": "이(가) 함락되다니…",
    "7:627:0": "은(는) 반드시 탈환하리라!",
    "7:628:0": "을(를) 빼앗기다니…!",
    "7:630:0": "을(를) 포기할 수밖에 없사옵니다",
    "7:631:0": "언젠가 「",
    "7:632:0": "을(를) 잃다니, 이 무슨 실책인가!",
    "7:634:0": "을(를) 내줄 수밖에 없는가…",
    "7:635:0": "을(를) 빼앗겼는가, 두고 보아라!",
    "7:636:1": "」을(를) 잃게 되다니…!",
    "7:637:0": "언젠가 「",
    "7:638:0": "을(를) 내줄 수밖에 없는가…",
    "7:639:0": "을(를) 잃다니 한심하구나",
}
TARGET_RECORD_IDS = tuple(
    dict.fromkeys(
        int(coordinate.split(":")[1])
        for coordinate in TARGET_COORDINATES
    )
)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    592: 3,
    606: 2,
    607: 3,
    608: 2,
    609: 1,
    610: 1,
    611: 1,
    612: 1,
    613: 1,
    615: 1,
    616: 1,
    617: 1,
    618: 1,
    619: 1,
    620: 1,
    621: 2,
    622: 1,
    624: 2,
    625: 2,
    626: 1,
    627: 1,
    628: 1,
    630: 1,
    631: 2,
    632: 1,
    634: 1,
    635: 1,
    636: 2,
    637: 2,
    638: 1,
    639: 1,
}
PREFILL_COMPANION_COORDINATES = (
    "7:592:1", "7:592:2",
    "7:621:0",
    "7:624:0",
    "7:631:1",
    "7:636:0",
    "7:637:1",
)
PRIMARY_BASE_DONOR = {
    record_id: (7, record_id - 6)
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: (PRIMARY_BASE_DONOR[record_id],)
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES.update({
    606: ((6, 3102), (7, 600)),
    607: ((6, 3103), (7, 601)),
    626: ((7, 620), (7, 634)),
    631: ((7, 625), (7, 635)),
})
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (7, record_id)
    for record_id in (
        544, 545, 546, 589, 590, 591, 592, 593, 605, 606,
        607, 608, 638, 639, 640, 672, 673, 674,
    )
)
SOURCE_CALL_ROOTS: tuple[int, ...] = ()
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ("026432",))
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_CONTROLS_BY_RECORD.update({
    592: ((), ("024733", "025132")),
    606: ((), ("024633", "026432")),
    607: ((), ("024633", "0232", "026432")),
})
SPEAKER_STYLE = tuple(
    (
        record_id,
        (
            "diplomatic_request_refusal_register"
            if record_id == 592
            else "castle_entry_result_ui"
            if record_id in {606, 607}
            else "fallen_castle_reaction_register"
        ),
    )
    for record_id in TARGET_RECORD_IDS
)
TERMINOLOGY_POLICY = (
    ("request", "청"),
    ("enter castle", "입성"),
    ("castle falls", "함락"),
    ("retake", "되찾다"),
    ("recapture", "탈환"),
    ("defense", "방비"),
    ("blunder", "실책"),
    ("give up", "포기"),
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
    "0FBEA3F577B2A20985818B8F31AB2340B14CE652C5FA24B2732306BB088C0C6D"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "F154BFF7097A307EBD0859AB9A1D27ACADCB8A8AFCD1AD050099530BC711435E"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "5A70F7B43331D5874D54EA26C36953B3702B449E3ADD46A15F73C6383BDD1695"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "E273BA3D9878DA2C74EC47CFDD4462C4D70A61B065CA67E5D559C04DBDD73AB5"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "681187CB2628865FA92710010AC7F010141EF00D60FBD496CFEC2CBB459ACB8D"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "B336696EC21F5AC470E99DC656ACA332A889EBB50003BA36F565F8D25E8989C6"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "3A2DE935827EC50FE55BDF9FFDECD2FCC19C8287734330AF5FBFDEE84EF24F43"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "E87DB3C659FC7E3D3484BF4E8CD45CCC6CB62529331141D44D052F69C2926451"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "7E6783F4695DEF2AC2C27C58F9467B94400D92FFC2B7504FB2BEE855B1499927"
)
EXPECTED_BOUNDARY_SHA256 = (
    "A8D7740CD16EF95595FBB621EED1B18F843AA2CC82E7A1EECAF98E63CA0484A3"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "5B11C06EEB98F2C9F868EDD9991FCB0C0B27A91CB7B5080BD78EFBA92E4B4ABA"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "F85C0A5E1A311939F4FE51743D97114146BC9D95C5EE93E7ECA1F9561CF1D115"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "3D763CD892372DBBC94A68E33CCEB09F12FFA93D3420AF873030B22AFEE2EDD2"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "01AA1FA592B0513BE9FF664B6BCBE0B90BF2B4D6F8069E570E03E4FEDA28D6BC"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "BB1EE3B062C879D647B7EA0335A8A9520B4C88779CF3456660D02B8539FBCD72"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "32C3FD6C05A0C55AC9B820FE19535B5E2BD94BA9D85C03BDBD25A85D4F9DBC37"
)
EXPECTED_CANDIDATE_SHA256 = (
    "33E11AB29CBB70C4DDE7DA1B2BCFAAD64000B7B72C6BFE33E1CC93EAF79619AD"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "65E66E784E869F1A2C9BC69319C1EE87159D6C4A21C1C160351B7727484D217A"
)
EXPECTED_CHANGED_LITERAL_COUNT = 34
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 65

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative and complete PK EN SC TC context "
    "was reviewed where present; every residual complete record has a "
    "byte-exact completed Base source donor and its Korean wording is "
    "manually selected for semantic and terminology consistency while Base "
    "runtime and VM state are never inherited; all thirty-one queue "
    "prefills and seven same-record companions are validated; complete "
    "records, person, count, faction and castle tokens, protected outer "
    "whitespace, queue and segment boundaries, two-run reproduction, "
    "tamper rejection, reverse overlays, outside-scope identity, and Steam "
    "read-only state are guarded"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1174_parent",
        PARENT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {PARENT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PARENT = load_parent()
CORE = PARENT.PARENT
ENGINE = PARENT.ENGINE
sha256_bytes = PARENT.sha256_bytes
coordinate_key = PARENT.coordinate_key
literal_texts = PARENT.literal_texts
gap_bytes = PARENT.gap_bytes
read_jsonl = PARENT.read_jsonl
context_records = PARENT.context_records


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
        "STATIC_RECORD_IDS": STATIC_RECORD_IDS,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "PREFILL_COMPANION_COORDINATES":
        PREFILL_COMPANION_COORDINATES,
        "PRIMARY_BASE_DONOR": PRIMARY_BASE_DONOR,
        "EXPECTED_BASE_RAW_MATCHES": EXPECTED_BASE_RAW_MATCHES,
        "EXPECTED_BASE_LITERAL_MATCHES": EXPECTED_BASE_LITERAL_MATCHES,
        "EXPECTED_BASE_MASKED_MATCHES": EXPECTED_BASE_MASKED_MATCHES,
        "BOUNDARY_RECORD_KEYS": BOUNDARY_RECORD_KEYS,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
        "EXPECTED_CONTROLS_BY_RECORD": EXPECTED_CONTROLS_BY_RECORD,
        "SPEAKER_STYLE": SPEAKER_STYLE,
        "TERMINOLOGY_POLICY": TERMINOLOGY_POLICY,
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
        "EXPECTED_COMBINED_CHANGED_LITERAL_COUNT":
        EXPECTED_COMBINED_CHANGED_LITERAL_COUNT,
        "DISCOVERED_PINS": DISCOVERED_PINS,
        "BASIS": BASIS,
    }
    for name, value in values.items():
        setattr(PARENT, name, value)
    PARENT.queue_evidence = queue_evidence
    PARENT.assert_queue_and_residual_contract = (
        assert_queue_and_residual_contract
    )
    PARENT.patch_parent_globals()
    CORE.queue_evidence = queue_evidence


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
        len(rows) != 129
        or len(visible) != 199
        or visible[0] != "7:545:0"
        or visible[-1] != "7:673:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B054 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "7:590:1"
        or queue_slice[-1] != "7:639:0"
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
    if len(prefilled) != 31 or residual != TARGET_COORDINATES:
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
    CORE.guarded_digest(
        "queue universe", visible, EXPECTED_QUEUE_UNIVERSE_SHA256
    )
    CORE.guarded_digest(
        "queue slice", queue_slice, EXPECTED_QUEUE_SLICE_SHA256
    )
    CORE.guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
    CORE.guarded_digest(
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
        or len(prefilled) != 31
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
    CORE.assert_context_contracts(prepared, records)
    CORE.assert_base_and_complete_assembly(prepared, records)
    CORE.assert_call_graphs(prepared)
    CORE.assert_semantics(records)
    candidate, candidate_sha256, changed = CORE.build_candidate(
        prepared,
        records,
    )
    combined_sha256, combined_changed = build_combined_slice_candidate(
        prepared,
        records,
    )
    rows: list[dict[str, Any]] = []
    style_map = dict(SPEAKER_STYLE)
    companion_records = {
        int(coordinate.split(":")[1])
        for coordinate in PREFILL_COMPANION_COORDINATES
    }
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
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "runtime_pending",
                "runtime_review": "pending",
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
                record_id in companion_records,
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
                CORE.runtime_evidence(records, record_id),
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
    if (
        len(rows) != 36
        or len(validated) != 36
        or counts != Counter({"runtime_fragment_pending": 36})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["base_runtime_state_inherited"] is not False
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    patch_parent_globals()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(json.dumps({
        "status": "ok",
        "segment": "pk_msggame_B054_S1174",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "approved": len(rows),
        "scope_classification_counts": dict(counts),
        "queue_slice_visible_count": 67,
        "exact_reuse_prefill_count": 31,
        "residual_count": len(rows),
        "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
        "same_record_prefill_companion_count":
        len(PREFILL_COMPANION_COORDINATES),
        "raw_exact_complete_base_donor_record_count":
        len(TARGET_RECORD_IDS),
        "source_call_root_count": 0,
        "current_call_root_count": 0,
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
