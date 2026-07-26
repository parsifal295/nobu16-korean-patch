#!/usr/bin/env python3
"""Build source-redacted PK B072 segment 1220 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch071_segment1217.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B072_S1220.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B072_S1221.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B072_S1222.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1220
QUEUE_BATCH_ID = "pk_msggame-B072"
QUEUE_START = 0
QUEUE_STOP = 67
QUEUE_ROW_COUNT = 106
QUEUE_VISIBLE_COUNT = 200
SLICE_VISIBLE_COUNT = 67
SLICE_PREFILL_COUNT = 59
BLOCK_ID = 8
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "8:325:1",
    "8:326:1",
    "8:326:2",
    "8:326:3",
    "8:327:0",
    "8:337:2",
    "8:338:1",
    "8:340:1",
)
TRANSLATIONS = {
    "8:325:1": (
        ",\n우리 가문의 방침에 따라 미리 대비한 덕분에\n"
        "일부 지역은 화를 면한 모양"
    ),
    "8:326:1": ",\n",
    "8:326:2": "아소 신사",
    "8:326:3": "의 가호로\n일부 지역은 화를 면한 모양",
    "8:327:0": ", 큰일",
    "8:337:2": "인 것",
    "8:338:1": "\n미리 대책을 마련하고",
    "8:340:1": "\n미리 대비가",
}
TARGET_RECORD_IDS = (325, 326, 327, 337, 338, 340)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    325: 2,
    326: 4,
    327: 2,
    337: 3,
    338: 3,
    340: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "8:325:0",
    "8:326:0",
    "8:327:1",
    "8:337:0",
    "8:337:1",
    "8:338:0",
    "8:338:2",
    "8:340:0",
    "8:340:2",
)
PREFILL_COMPANION_DONOR = {
    "8:325:0": "8:315:0",
    "8:326:0": "8:315:0",
    "8:327:1": "8:317:1",
    "8:337:0": "8:327:0",
    "8:337:1": "8:327:1",
    "8:338:0": "8:328:0",
    "8:338:2": "8:328:2",
    "8:340:0": "8:330:0",
    "8:340:2": "8:330:2",
}
EXACT_BASE_DONOR: dict[int, tuple[int, int]] = {}
SEMANTIC_BASE_CONTEXT = {
    325: ("8:315:0", "8:315:1"),
    326: ("8:315:0", "8:315:1"),
    327: ("8:317:0", "8:317:1"),
    337: ("8:327:0", "8:327:1", "8:327:2"),
    338: ("8:328:0", "8:328:1", "8:328:2"),
    340: ("8:330:0", "8:330:1", "8:330:2"),
}
EXPECTED_BASE_RAW_MATCHES = {
    325: (),
    326: (),
    327: (),
    337: (),
    338: (),
    340: ((8, 330),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    325: (),
    326: (),
    327: ((8, 317),),
    337: ((8, 327),),
    338: ((8, 328),),
    340: ((8, 330),),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (8, record_id)
    for record_id in (
        314, 315, 316, 317, 318, 320, 321, 322, 323, 324,
        325, 326, 327, 328, 329, 330, 331, 332, 333, 334,
        335, 336, 337, 338, 339, 340, 341, 342, 343, 344,
        345, 346, 347, 425, 426,
    )
)
SOURCE_CALL_ROOTS = (7, 8, 70, 136, 178, 274, 376, 538, 562, 568, 712)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    325: ((538, 568), ()),
    326: ((538, 568), ()),
    327: ((8, 562, 178), ()),
    337: ((7, 70, 712, 376), ()),
    338: ((274, 136, 712), ()),
    340: ((376, 274, 70, 376), ()),
}
SPEAKER_STYLE = (
    (325, "flood_policy_preparedness_report"),
    (326, "flood_shrine_blessing_report"),
    (327, "urgent_flood_damage_report"),
    (337, "typhoon_countermeasure_report"),
    (338, "polite_typhoon_mitigation_report"),
    (340, "typhoon_preparedness_report"),
)
TERMINOLOGY_POLICY = (
    ("flood", "홍수"),
    ("territory", "영내"),
    ("our clan", "우리 가문"),
    ("policy", "방침"),
    ("advance preparation", "미리 대비하다"),
    ("Aso Shrine", "아소 신사"),
    ("divine blessing", "가호"),
    ("avoid disaster", "화를 면하다"),
    ("typhoon", "태풍"),
    ("countermeasure", "대책"),
    ("damage", "피해"),
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
    "2A788504B0BC42A296D732E3BB411B34D4DD217A13E8C3597773054D50029E57"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "2A00746F475498D294D997EBAC79E1141FDE252BDEFD39722638642F9E8CE4D1"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "59CE4E76D358462E0760ED099D7DF9475C927ABBB1427F11BC54E545044149F2"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "2682FB9A0F858185F7CB9AAFA42EBCEC087ECD0F9DCCF7B051E9BA002D5AB3A2"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "9DD08BABE42F365DD3A0D0377CC07089F25E33143ED49C01A9E59862351CECC2"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "6C8518645C113BC3F9DAA3CA9E04AD66DB1D8F85F05EF1DA697DDD584F16BF1B"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "304FE99B330041974A4694FF40BE13E728E8BE69179EA0A9B8B5F2FB18750FC8"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "832B31C1337C2303228D45258DC6C68FE67F5C9C729D4330136BA28E02B4AF55"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "D4062C01A40A5DAE25E1C7AD86C735CEEA8DDA4272DBCA910E3E8919F8403B2B"
)
EXPECTED_BOUNDARY_SHA256 = (
    "6EAC15DAFA13F45E2E42079CACCCB7A44E19E1D484D74A50B939A0676D44FAA3"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "8C5C90877098ABACB74F71B529DCD5277E3BD08598FC2294A05E1957CA013500"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "42F048DF5778824E6B1533A5FC29ECA0D175F84AB24897CFE7989E3CDCBB334B"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "DCDA331735CB5A1119B93DFD1A53E33742C7CF8386257A684083E033D17DFAD9"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "AC67DE84A52308FC89BFD629D41F6F2278286915286DDBB3379914ADDF9ECA00"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "4DC232EF4867F8F881F29AD1B78D45E6D27986B6021BCE561F31A287F66F08C3"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "F850D2AB12299087DEC591CA5CAC1377034620CFD445A49D58096C3A57CAD3C0"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "CBEB3C3F12E0B89CF1E735B5984DB495DF2C69FDF6A9EEEAFABE72A73E4FD4BF"
)
EXPECTED_CANDIDATE_SHA256 = (
    "825A7E1143AB3A1FA5857A63AC7CB0016C97FA0EC0EE34818D9D63ADD4FD6552"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "B1411E5418B42D806981E735B30E0D9591E44BB3FEBE3C67D43F1BB468DBDB4C"
)
EXPECTED_CHANGED_LITERAL_COUNT = 6
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 59

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK Japanese is authoritative and complete PK English, "
    "Simplified Chinese and Traditional Chinese records were manually "
    "reviewed; six complete flood and typhoon report records use completed "
    "Base wording only as semantic context, including one observed raw "
    "match, without inheriting completed Base runtime or VM state; eight "
    "residual fragments and nine same-record exact-prefill companions were "
    "reviewed as complete assemblies; flood, territory, clan policy, advance "
    "preparation, Aso Shrine, blessing, typhoon, countermeasure and damage "
    "terminology, report register, calls, punctuation, newlines, protected "
    "outer whitespace and gaps are guarded; all fifty-nine first-slice "
    "prefills, two-run reproduction, tamper rejection, reverse overlays, "
    "outside-scope identity and Steam read-only state are guarded; all "
    "residuals remain PK runtime pending"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_b072_s1220_base",
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
CORE = BASE.CORE
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
        len(rows) != QUEUE_ROW_COUNT
        or len(visible) != QUEUE_VISIBLE_COUNT
        or visible[0] != "8:321:0"
        or visible[-1] != "8:426:2"
    ):
        raise RuntimeError(f"segment {SEGMENT} B072 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != SLICE_VISIBLE_COUNT
        or queue_slice[0] != "8:321:0"
        or queue_slice[-1] != "8:346:0"
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
        len(prefilled) != SLICE_PREFILL_COUNT
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
                and CORE.mask_call_operands(record)
                == CORE.mask_call_operands(source)
            )
        )
        if (
            len(source_literals) != EXPECTED_ARITY[record_id]
            or raw_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
            or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[record_id]
            or masked_matches != EXPECTED_BASE_MASKED_MATCHES[record_id]
            or record_id in EXACT_BASE_DONOR
        ):
            raise RuntimeError(
                f"segment {SEGMENT} semantic Base context drifted: "
                f"{record_id}"
            )
        donor_coordinates = SEMANTIC_BASE_CONTEXT[record_id]
        donor_rows: list[dict[str, Any]] = []
        for donor_coordinate in donor_coordinates:
            row = base_rows.get(donor_coordinate)
            if (
                row is None
                or row.get("semantic_review") != "approved"
                or row.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} missing Base context: "
                    f"{donor_coordinate}"
                )
            donor_rows.append(row)
        assembled: list[str] = []
        owners: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"{BLOCK_ID}:{record_id}:{literal_id}"
            if coordinate in TRANSLATIONS:
                assembled.append(TRANSLATIONS[coordinate])
                owners.append("segment_manual")
                seen_target.add(coordinate)
                continue
            prefill = prefill_rows.get(coordinate)
            if (
                coordinate not in PREFILL_COMPANION_COORDINATES
                or prefill is None
                or prefill.get("semantic_review") != "approved"
                or prefill.get("runtime_review") != "pending"
                or prefill["base_exact_reuse_prefill"][
                    "runtime_promotion_authorized"
                ]
                is not False
                or prefill["base_exact_reuse_prefill"]["base_coordinate"]
                != PREFILL_COMPANION_DONOR[coordinate]
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
                        coordinate,
                        str(row["translation"]),
                        str(row["runtime_review"]),
                    )
                    for coordinate, row in zip(
                        donor_coordinates,
                        donor_rows,
                    )
                ),
                "semantic_context_only",
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(assembled),
                donor_translations,
                CORE.runtime_controls(source),
                CORE.runtime_controls(records_by_label["current"][key]),
                "manual_pk_semantic_adaptation",
                "base_runtime_state_not_inherited",
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
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
        len(replacements) != SLICE_VISIBLE_COUNT
        or len(prefilled) != SLICE_PREFILL_COUNT
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
        and candidate_sha256 != EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} combined candidate drifted: {candidate_sha256}"
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
        "PREFILL_COMPANION_DONOR": PREFILL_COMPANION_DONOR,
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
    module = BASE
    visited: set[int] = set()
    while id(module) not in visited:
        visited.add(id(module))
        setattr(module, "base_and_assembly_evidence", base_and_assembly_evidence)
        next_module = getattr(module, "BASE", None)
        if next_module is None:
            next_module = getattr(module, "PARENT", None)
        if next_module is None:
            break
        module = next_module
    CORE.base_and_assembly_evidence = base_and_assembly_evidence


def build_rows() -> tuple[Any, ...]:
    install_base_globals()
    return BASE.build_rows()


def propagate_base_globals() -> None:
    install_base_globals()
    BASE.propagate_base_globals()


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared, rows, candidate, candidate_sha256, changed,
        combined_sha256, combined_changed, optional_present,
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
            DISCOVERED_PINS, sort_keys=True, separators=(",", ":"),
        ))
        return 2
    steam_before = sha256_bytes(STEAM_PK.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: {steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared, OUTPUT, require_complete=False,
    )
    counts = Counter(str(row["scope_classification"]) for row in rows)
    if (
        len(rows) != len(TARGET_COORDINATES)
        or len(validated) != len(TARGET_COORDINATES)
        or counts != Counter({
            "runtime_fragment_pending": len(TARGET_COORDINATES)
        })
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ] is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    propagate_base_globals()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(json.dumps({
        "status": "ok",
        "segment": "pk_msggame_B072_S1220",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "approved": len(rows),
        "scope_classification_counts": dict(counts),
        "queue_slice_visible_count": SLICE_VISIBLE_COUNT,
        "exact_reuse_prefill_count": SLICE_PREFILL_COUNT,
        "residual_count": len(rows),
        "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
        "same_record_prefill_companion_count":
        len(PREFILL_COMPANION_COORDINATES),
        "automatic_complete_base_donor_record_count": 0,
        "observed_raw_base_match_record_count":
        sum(bool(EXPECTED_BASE_RAW_MATCHES[x]) for x in TARGET_RECORD_IDS),
        "semantic_base_context_record_count":
        len(SEMANTIC_BASE_CONTEXT),
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
        "base_vm_state_inherited": False,
        "complete_record_assemblies_guarded": True,
        "all_slice_prefills_guarded": True,
        "combined_slice_reverse_order_exact": True,
        "source_redacted": True,
        "reverse_order_overlay_exact": True,
        "reverse_overlay_exact": True,
        "outside_scope_identity_guarded": True,
        "second_run_reproduced": True,
        "tamper_rejection_passed": True,
        "discovered_pins": DISCOVERED_PINS,
        "steam_write_performed": False,
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
