#!/usr/bin/env python3
"""Build source-redacted PK B072 segment 1222 residual decisions."""

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
PARENT_PATH = WORKSTREAM / "build_pk_batch070_segment1214.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B072_S1222.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B072_S1221.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B073_S1223.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1222
QUEUE_BATCH_ID = "pk_msggame-B072"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 8
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "8:381:0",
    "8:396:0",
    "8:397:0",
    "8:397:1",
    "8:400:0",
    "8:403:2",
    "8:404:0",
    "8:407:1",
    "8:409:0",
    "8:409:2",
    "8:410:0",
    "8:424:0",
    "8:425:1",
    "8:426:0",
    "8:426:1",
)
TRANSLATIONS = {
    "8:381:0": "이(가) 「",
    "8:396:0": "그렇",
    "8:397:0": "…알겠",
    "8:397:1": "\n무언가,",
    "8:400:0": "그것이 「",
    "8:403:2": "…",
    "8:404:0": "이(가) 납득",
    "8:407:1": "…",
    "8:409:0": "알겠",
    "8:409:2": "분부를 내려 주십시오",
    "8:410:0": "삼가 받들겠습니다",
    "8:424:0": "을(를) 비롯한 총",
    "8:425:1": "을(를) 비롯한 총",
    "8:426:0": "영내의 「",
    "8:426:1": "」을(를) 비롯한 총",
}
TARGET_RECORD_IDS = (
    381, 396, 397, 400, 403, 404, 407, 409, 410, 424, 425, 426,
)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    381: 2,
    396: 2,
    397: 3,
    400: 2,
    403: 3,
    404: 2,
    407: 2,
    409: 3,
    410: 2,
    424: 2,
    425: 3,
    426: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "8:381:1",
    "8:396:1",
    "8:397:2",
    "8:400:1",
    "8:403:0",
    "8:403:1",
    "8:404:1",
    "8:407:0",
    "8:409:1",
    "8:410:1",
    "8:424:1",
    "8:425:0",
    "8:425:2",
    "8:426:2",
)
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
SEMANTIC_BASE_RECORD = {
    381: (8, 369),
    396: (8, 384),
    397: (8, 385),
    400: (8, 388),
    403: (8, 391),
    404: (8, 392),
    407: (8, 395),
    409: (8, 397),
    410: (8, 398),
    424: (8, 412),
    425: (8, 413),
    426: (8, 414),
}
EXACT_BASE_DONOR: dict[int, tuple[int, int]] = {}
SEMANTIC_BASE_CONTEXT = {
    record_id: tuple(
        f"{key[0]}:{key[1]}:{literal_id}"
        for literal_id in range(EXPECTED_ARITY[record_id])
    )
    for record_id, key in SEMANTIC_BASE_RECORD.items()
}
PREFILL_COMPANION_DONOR = {
    coordinate: (
        f"8:{SEMANTIC_BASE_RECORD[int(coordinate.split(':')[1])][1]}:"
        f"{coordinate.split(':')[2]}"
    )
    for coordinate in PREFILL_COMPANION_COORDINATES
}
EXPECTED_BASE_RAW_MATCHES = {
    381: ((8, 369),),
    396: ((8, 384),),
    397: (),
    400: ((8, 388),),
    403: ((8, 391),),
    404: (),
    407: (),
    409: (),
    410: (),
    424: ((8, 412),),
    425: ((8, 413),),
    426: ((8, 414),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    record_id: (SEMANTIC_BASE_RECORD[record_id],)
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (8, record_id)
    for record_id in (
        368, 369, 370, 380, 381, 382, 383, 384, 385, 386,
        387, 388, 389, 390, 391, 392, 393, 394, 395, 396,
        397, 398, 399, 400, 401, 402, 403, 404, 405, 406,
        407, 408, 409, 410, 411, 412, 413, 414, 415, 423,
        424, 425, 426,
    )
)
SOURCE_CALL_ROOTS = (
    1, 8, 202, 238, 256, 274, 322, 370, 466, 538, 628, 742,
    1168, 1174,
)
CURRENT_CALL_ROOTS = (
    1, 8, 202, 238, 256, 274, 322, 466, 538, 742, 1168, 1174,
)
EXPECTED_CONTROLS_BY_RECORD = {
    381: ((), ("026E32", "029632")),
    396: ((238, 322), ()),
    397: ((538, 1168, 742), ()),
    400: ((1, 238), ()),
    403: ((202, 274), ()),
    404: ((1, 466, 256), ()),
    407: ((8, 742), ()),
    409: ((538, 1174), ()),
    410: ((628, 370), ()),
    424: ((), ("029632", "0232")),
    425: ((), ("029632", "0232")),
    426: ((), ("029632", "0232")),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = {
    **EXPECTED_SOURCE_CONTROLS_BY_RECORD,
    410: ((), ()),
}
SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS = (410,)
SPEAKER_STYLE = (
    (381, "field_battle_join_notice"),
    (396, "disappointed_reassignment_request"),
    (397, "restrained_reassignment_acceptance"),
    (400, "wounded_evaluation_question"),
    (403, "reluctant_obedience"),
    (404, "concerned_acceptance_question"),
    (407, "resigned_obedience"),
    (409, "dutiful_future_service"),
    (410, "formal_handover_acceptance"),
    (424, "uprising_urgent_report"),
    (425, "delayed_response_uprising_report"),
    (426, "compact_uprising_notice"),
)
TERMINOLOGY_POLICY = (
    ("field battle", "야전"),
    ("replacement land", "대체 영지"),
    ("territory", "영내"),
    ("order", "분부"),
    ("successor", "후임"),
    ("handover", "인계"),
    ("uprising", "잇키"),
    ("county", "군"),
    ("suppress", "진압"),
    ("project name quotes", "「」"),
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
    "2A788504B0BC42A296D732E3BB411B34D4DD217A13E8C3597773054D50029E57"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "6A4A8130E1A63B8990ED31E3E93844D56BC1C1C819E3D8FE9FB5347ABBEA3D2A"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "B01D9116CB8F6081DF16587350352806EF08D17CA834F82A7A310560EB52DBDE"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "932AE40096F7D2D9E93FFF85D315609615F7ADA51495B9EDD7D14B37A4507A6F"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "7E26322871208F4A6B3598127E1458834E9783C51AD113FD61ECAF949FBCB156"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "74EBDF9DE04DE5BA836A513ADA6769C73F121EE4E1C74A4B82C9AD25E10537D9"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "0D9E628E526DADC0CECED984347640067E228D2A477F6E4EBBB3531907A908B0"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "832B31C1337C2303228D45258DC6C68FE67F5C9C729D4330136BA28E02B4AF55"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "704D3B6FA3B37048D33BAA9DF84846D4314CD3D1B3EBD0A47FDA4CD302998D3B"
)
EXPECTED_BOUNDARY_SHA256 = (
    "AD4A6CFE30757F51E873DC5CABB7B10FF178830FC94EA7EF149640EF9CA0285A"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "D55BECE5D08269DDA8889C62DB5D4C485294190CBB7FE8ACEFCA2BE76CCEE892"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "E8EBF5B119F317D201F4DD9F19881113F0698B910EFFEB754C6F091933F2E5F6"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "94933990DE9C2E38546D58E4B238262C2238E4F0CBF46B2CE0E843180B84C3CA"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "0CE8B675EF40E75A48BFE12FF0299813BAD87F8AF03DAF3DBAAC22BD13FE7B0F"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "B51819CAF50B9617E527FC131251EFF61378DD976D0F101FA8FED9EFC43B80DA"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "624214B138EC93B932016A73B3F4887335106D2D834AE9D8EFD8ED1CE9C44364"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "26B92BF63C4EDE5060B29851B7D7DAE85834442FFDD6D8EFA1AD8597E3757837"
)
EXPECTED_CANDIDATE_SHA256 = (
    "11DF840C9D999A9CBA3706DDBCDCD28C524F2EC3933B65B9DB48BDEB46BF72C0"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "0B72B9522B73C0A162DE30ADD5C8287A1BFA21932BAE1498014AD40FE312A372"
)
EXPECTED_CHANGED_LITERAL_COUNT = 13
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 55

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese source authoritative; complete PC English, "
    "Simplified Chinese and Traditional Chinese records were reviewed as "
    "auxiliary context where populated; completed Base records were used "
    "only as semantic and terminology references and their runtime or VM "
    "state was not inherited; all twelve complete PK records were reviewed "
    "with restrained reassignment, formal obedience, handover, field-battle "
    "and urgent uprising registers; fifteen residual translations and "
    "fourteen approved exact-prefill companions assemble the complete "
    "records while name quotes, ellipsis, historical domain, uprising and "
    "county terminology remain consistent; all fifty-one prefills in the "
    "sixty-six-row final slice, source/current gaps, inline tokens, direct "
    "calls, protected whitespace and complete assemblies are guarded; "
    "record 410 source calls are explicitly recorded as already flattened "
    "in current Korean; both overlay orders, byte-exact reversal, two-run "
    "reproduction, "
    "tamper rejection, outside-scope identity and Steam read-only state "
    "are verified; every residual remains PK runtime pending"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1222_parent",
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
CORE = PARENT.CORE
sha256_bytes = PARENT.sha256_bytes
coordinate_key = PARENT.coordinate_key
literal_texts = PARENT.literal_texts
gap_bytes = PARENT.gap_bytes
read_jsonl = PARENT.read_jsonl


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
        len(rows) != 106
        or len(visible) != 200
        or visible[0] != "8:321:0"
        or visible[-1] != "8:426:2"
    ):
        raise RuntimeError(f"segment {SEGMENT} B072 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "8:381:0"
        or queue_slice[-1] != "8:426:2"
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
        len(prefilled) != 51
        or len(residual) != 15
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
        if "translation" in row
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
            coordinate for coordinate, record in base_source.items()
            if record.data == source.data
        )
        literal_matches = tuple(
            coordinate for coordinate in base_source
            if literal_texts(base_source, coordinate) == source_literals
        )
        masked_matches = tuple(
            coordinate for coordinate, record in base_source.items()
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
                f"segment {SEGMENT} Base semantic context drifted: "
                f"{record_id}"
            )
        references = SEMANTIC_BASE_CONTEXT[record_id]
        reference_rows: list[dict[str, Any]] = []
        for reference in references:
            row = base_rows.get(reference)
            if (
                row is None
                or row.get("semantic_review") != "approved"
                or row.get("runtime_review") not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} semantic donor drifted: {reference}"
                )
            reference_rows.append(row)
        assembled: list[str] = []
        owners: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"{BLOCK_ID}:{record_id}:{literal_id}"
            if coordinate in target_set:
                seen_target.add(coordinate)
                assembled.append(TRANSLATIONS[coordinate])
                owners.append("segment_manual_semantic")
                continue
            companion = prefill_rows.get(coordinate)
            expected_companion_runtime = (
                "not_required" if record_id == 410 else "pending"
            )
            if (
                coordinate not in companion_set
                or companion is None
                or companion.get("semantic_review") != "approved"
                or companion.get("runtime_review")
                != expected_companion_runtime
                or companion["base_exact_reuse_prefill"][
                    "runtime_promotion_authorized"
                ]
                is not False
                or str(
                    companion["base_exact_reuse_prefill"]["base_coordinate"]
                )
                != PREFILL_COMPANION_DONOR[coordinate]
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} companion drifted: {coordinate}"
                )
            seen_companion.add(coordinate)
            assembled.append(str(companion["translation"]))
            owners.append("base_exact_prefill_runtime_pending")
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
                references,
                tuple(
                    (
                        str(row["coordinate"]),
                        str(row["translation"]),
                        str(row["semantic_review"]),
                        str(row["runtime_review"]),
                    )
                    for row in reference_rows
                ),
                "semantic_context_only",
                "base_runtime_state_not_inherited",
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(assembled),
                CORE.runtime_controls(source),
                CORE.runtime_controls(records_by_label["current"][key]),
                "manual_pk_semantic_adaptation",
                "base_runtime_state_not_inherited",
            )
        )
    if seen_target != target_set or seen_companion != companion_set:
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    values = CORE.context_evidence(prepared, records_by_label)
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
        CORE.guarded_digest(label, value, expected)
    expected_controls = tuple(
        (
            label,
            record_id,
            (
                EXPECTED_SOURCE_CONTROLS_BY_RECORD[record_id]
                if label == "jp"
                else EXPECTED_CURRENT_CONTROLS_BY_RECORD[record_id]
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    variants = set(SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS)
    if (
        values["controls"] != expected_controls
        or any(
            source != current and record_id not in variants
            for record_id, source, current in values["gaps"]
        )
        or any(
            source == current and record_id in variants
            for record_id, source, current in values["gaps"]
        )
        or any(
            ("pk_msggame", *coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime layout drifted")


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
        or len(prefilled) != 51
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
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "STATIC_RECORD_IDS": STATIC_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "PREFILL_COMPANION_COORDINATES": PREFILL_COMPANION_COORDINATES,
        "HIDDEN_CURRENT_COMPANION_COORDINATES":
        HIDDEN_CURRENT_COMPANION_COORDINATES,
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
        setattr(PARENT, name, value)
    PARENT.PARENT.BASE.base_and_assembly_evidence = (
        base_and_assembly_evidence
    )
    CORE.assert_context_contracts = assert_context_contracts


def propagate_parent_globals() -> None:
    patch_parent_globals()
    PARENT.patch_parent_globals()
    PARENT.PARENT.install_base_globals()
    PARENT.PARENT.BASE.base_and_assembly_evidence = (
        base_and_assembly_evidence
    )
    PARENT.PARENT.BASE.propagate_base_globals()


def build_rows() -> tuple[
    Any, list[dict[str, Any]], bytes, str, int, str, int, tuple[str, ...],
]:
    patch_parent_globals()
    return PARENT.build_rows()


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
        len(rows) != 15
        or len(validated) != 15
        or counts != Counter({"runtime_fragment_pending": 15})
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
            ] is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    propagate_parent_globals()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    if DISCOVERED_PINS:
        raise RuntimeError(f"segment {SEGMENT} pins remained mutable")
    print(json.dumps({
        "status": "ok",
        "segment": "pk_msggame_B072_S1222",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "approved": len(rows),
        "scope_classification_counts": dict(counts),
        "queue_slice_visible_count": 66,
        "exact_reuse_prefill_count": 51,
        "residual_count": len(rows),
        "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
        "same_record_prefill_companion_count":
        len(PREFILL_COMPANION_COORDINATES),
        "raw_exact_complete_base_donor_record_count": 0,
        "masked_complete_base_donor_record_count": 0,
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
        "source_current_gap_contract_guarded": True,
        "source_calls_flattened_in_current_record_count":
        len(SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS),
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
        "discovered_pins_empty": True,
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
