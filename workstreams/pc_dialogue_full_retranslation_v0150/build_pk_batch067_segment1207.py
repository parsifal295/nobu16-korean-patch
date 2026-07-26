#!/usr/bin/env python3
"""Build source-redacted PK B067 segment 1207 residual decision."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch067_segment1205.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B067_S1207.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B067_S1205.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B067_S1206.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1207
QUEUE_BATCH_ID = "pk_msggame-B067"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = ("7:2514:3",)
TRANSLATIONS = {
    "7:2514:3": "무운을 빌",
}
TARGET_RECORD_IDS = (2514,)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {2514: 4}
PREFILL_COMPANION_COORDINATES: tuple[str, ...] = ()
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
OUTSIDE_SLICE_COMPANION_TRANSLATIONS = {
    "7:2514:0": "이번 출진에서는\n우리 군단이",
    "7:2514:1": "도움이 되",
    "7:2514:2": "……\n",
}
EXACT_BASE_DONOR: dict[int, tuple[int, int]] = {}
SEMANTIC_BASE_CONTEXT = {
    2514: (
        "2:556:1",
        "6:2167:0",
        "8:448:0",
        "9:862:0",
        "15:230:1",
    ),
}
EXPECTED_BASE_RAW_MATCHES = {2514: ()}
EXPECTED_BASE_LITERAL_MATCHES = {2514: ()}
EXPECTED_BASE_MASKED_MATCHES = {2514: ()}
BOUNDARY_RECORD_KEYS = (
    (7, 2513),
    (7, 2514),
    (7, 2515),
    (7, 2578),
    (7, 2579),
)
SOURCE_CALL_ROOTS = (142, 670, 1168, 1174)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    2514: ((1168, 670, 1174, 142), ()),
}
SPEAKER_STYLE = (
    (2514, "corps_unavailable_fortune_wish"),
)
TERMINOLOGY_POLICY = (
    ("sortie", "출진"),
    ("corps", "군단"),
    ("assistance", "도움"),
    ("fortune in battle", "무운"),
    ("wish for fortune", "무운을 빌다"),
    ("project ellipsis", "……"),
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
    "B281AAE61073CA662D8CF73248A986683CCD9A5AABCA4C2C60B915C8A8E42956"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "5DB0C9D7C5F7390DD0812725803A7248954C6150A6C38012D5614BA1791302F6"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "88260686E2413491A9E361E96E2A9ED6048B9A060EDF6F687568FA05F5B12C51"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "B234145BA667E9FFD80C6273BBF38D69E7A594B8A273E9E42FE03F5A25CDE61B"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "73AE2886544A3D43907DB2278AEA4D7B9FD72ED3C1CDEDB190FEB2A4F2B893C9"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "18ADE0A0F132AD66B056A7F76978F972E079F752F5548B4ED7B063A44FB1A317"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "0DC1474C54C21DA5A0AA573296BB613D2E721B52AB0C27BCB9E287673ADE5976"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "C3B0810E934D7FF1992057600345EB235D554AAE6ABA95DDDFFF17F3F83E54EB"
)
EXPECTED_BOUNDARY_SHA256 = (
    "86C492B29A58AE2B667C757CD8F5F96D1F23237AC22F9407F8CDA2A45691BB05"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "C8D80E940D4235F3E766ADE9485CDC8A16F3761EDA8FB306574C0AC2B732B2FA"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "D7A143BF902C645DABB0A1875066499339ABA4248405BA073CCCA56E20763AEE"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "50D4FBB3EE9D1D683B4389CD0316160581306049676E1B7C51289214A18A38EB"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "1E94949EC526AF9A22BF631D8FBF8855CA4F313401C4CF33DE11EBB64CE4B02E"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "3E8740C7A90A65F597A88238531D4566E7C8FB9B6C227E3BCCA9AC0C53362E76"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "84AD2A82138010C0325EEE8758F83E55C6F52122F5703254CB70C79C706C2149"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "CF3A835E3670D040C774598354895F3FDAB4FB80A4FF3248645BCC37306450C8"
)
EXPECTED_CANDIDATE_SHA256 = (
    "E0CE586FDCD67C0DD44439A9B2CBD68F1C931E459F5B12A72BC01BBB03F85F55"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "D54213A467BCAF15128DB84524E169EF5EDD26BE7D8EEAB4C5A0F1F33BBF13F8"
)
EXPECTED_CHANGED_LITERAL_COUNT = 1
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 55

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative and complete PK EN SC TC context "
    "was manually reviewed; the PK-only complete record has no raw, literal, "
    "or call-masked Base match, so completed Base call-142 predicate stems, "
    "battle-fortune wording, inability-to-assist wording, and ellipsis usage "
    "are manual semantic context only; the three S1206 boundary companions "
    "are pinned to a complete four-literal assembly and optional S1206 output "
    "must match them if present; all sixty-five slice prefills are validated; "
    "Base runtime and VM state are never inherited; complete records, calls, "
    "protected outer whitespace, source and current gaps, queue and segment "
    "boundaries, two-run reproduction, tamper rejection, reverse overlays, "
    "outside-scope identity, and Steam read-only state are guarded"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1207_base",
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
        len(queue_slice) != 66
        or queue_slice[0] != "7:2514:3"
        or queue_slice[-1] != "7:2579:0"
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
        len(prefilled) != 65
        or len(residual) != 1
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


def optional_companion_rows(
    prepared: Any,
) -> tuple[dict[str, dict[str, Any]], bool]:
    path = OPTIONAL_NEIGHBORS[1]
    if not path.is_file():
        return {}, False
    ENGINE.validate_decisions(prepared, path, require_complete=False)
    rows = {
        str(row["coordinate"]): row
        for row in read_jsonl(path)
        if str(row.get("coordinate"))
        in OUTSIDE_SLICE_COMPANION_TRANSLATIONS
    }
    if set(rows) != set(OUTSIDE_SLICE_COMPANION_TRANSLATIONS):
        raise RuntimeError(f"segment {SEGMENT} optional companion set drifted")
    for coordinate, translation in OUTSIDE_SLICE_COMPANION_TRANSLATIONS.items():
        row = rows[coordinate]
        if (
            row.get("semantic_review") != "approved"
            or row.get("runtime_review") != "pending"
            or row.get("layout_review") != "runtime_pending"
            or row.get("base_runtime_state_inherited") is not False
            or str(row.get("translation")) != translation
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
        ):
            raise RuntimeError(
                f"segment {SEGMENT} optional companion drifted: "
                f"{coordinate}"
            )
    return rows, True


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
    key = (BLOCK_ID, 2514)
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
        len(source_literals) != EXPECTED_ARITY[2514]
        or raw_matches != EXPECTED_BASE_RAW_MATCHES[2514]
        or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[2514]
        or masked_matches != EXPECTED_BASE_MASKED_MATCHES[2514]
    ):
        raise RuntimeError(f"segment {SEGMENT} Base no-match contract drifted")
    semantic_rows: list[dict[str, Any]] = []
    for coordinate in SEMANTIC_BASE_CONTEXT[2514]:
        row = base_rows.get(coordinate)
        if (
            row is None
            or row.get("semantic_review") != "approved"
            or row.get("runtime_review")
            not in {"verified", "not_required"}
        ):
            raise RuntimeError(
                f"segment {SEGMENT} semantic context drifted: {coordinate}"
            )
        semantic_rows.append(row)
    prior_rows, _ = optional_companion_rows(prepared)
    assembled: list[str] = []
    owners: list[str] = []
    for literal_id in range(EXPECTED_ARITY[2514]):
        coordinate = f"{BLOCK_ID}:2514:{literal_id}"
        if coordinate in OUTSIDE_SLICE_COMPANION_TRANSLATIONS:
            translation = OUTSIDE_SLICE_COMPANION_TRANSLATIONS[coordinate]
            if coordinate in prior_rows:
                translation = str(prior_rows[coordinate]["translation"])
            ENGINE.validate_translation_shape(
                current_literals[literal_id],
                translation,
                "runtime_pending",
                coordinate,
            )
            if (
                translation.count("\n")
                != current_literals[literal_id].count("\n")
                or ENGINE.protected_signature(translation)
                != ENGINE.protected_signature(current_literals[literal_id])
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} companion shape drifted: "
                    f"{coordinate}"
                )
            assembled.append(translation)
            owners.append(
                "optional_s1206_companion"
                if coordinate in prior_rows
                else "pinned_s1206_companion_fallback"
            )
            continue
        if coordinate not in TRANSLATIONS:
            raise RuntimeError(
                f"segment {SEGMENT} incomplete manual record: {coordinate}"
            )
        assembled.append(TRANSLATIONS[coordinate])
        owners.append("segment_manual")
    expected_assembly = (
        OUTSIDE_SLICE_COMPANION_TRANSLATIONS["7:2514:0"],
        OUTSIDE_SLICE_COMPANION_TRANSLATIONS["7:2514:1"],
        OUTSIDE_SLICE_COMPANION_TRANSLATIONS["7:2514:2"],
        TRANSLATIONS["7:2514:3"],
    )
    if tuple(assembled) != expected_assembly:
        raise RuntimeError(f"segment {SEGMENT} complete assembly drifted")
    base_evidence = (
        (
            2514,
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
                for row in semantic_rows
            ),
            tuple(OUTSIDE_SLICE_COMPANION_TRANSLATIONS),
            "semantic_context_only",
        ),
    )
    assembly_evidence = (
        (
            2514,
            tuple(owners),
            tuple(assembled),
            tuple(
                "manual_multilingual_semantic_selection"
                for _ in assembled
            ),
            CORE.runtime_controls(source),
            CORE.runtime_controls(records_by_label["current"][key]),
            "manual_pk_semantic_adaptation",
            "base_runtime_state_not_inherited",
        ),
    )
    return base_evidence, assembly_evidence


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
        or len(prefilled) != 65
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
        "base_and_assembly_evidence": base_and_assembly_evidence,
        "build_combined_slice_candidate": build_combined_slice_candidate,
    }
    for name, value in values.items():
        setattr(BASE, name, value)


def propagate_base_globals() -> None:
    install_base_globals()
    BASE.install_base_globals()
    BASE.BASE.base_and_assembly_evidence = base_and_assembly_evidence
    BASE.BASE.patch_base_globals()
    BASE.BASE.BASE.base_and_assembly_evidence = base_and_assembly_evidence
    BASE.BASE.BASE.patch_parent_globals()


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
        row["outside_slice_companion_coordinates"] = tuple(
            OUTSIDE_SLICE_COMPANION_TRANSLATIONS
        )
        row["outside_slice_companions_reviewed"] = True
        row["optional_s1206_output_required"] = False
        row["runtime_assembly_evidence"][
            "outside_slice_companion_coordinates"
        ] = tuple(OUTSIDE_SLICE_COMPANION_TRANSLATIONS)
        row["runtime_assembly_evidence"][
            "outside_slice_companions_reviewed"
        ] = True
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
        len(rows) != 1
        or len(validated) != 1
        or counts != Counter({"runtime_fragment_pending": 1})
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
            or row["outside_slice_companions_reviewed"] is not True
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    propagate_base_globals()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    _, optional_s1206_present = optional_companion_rows(prepared)
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B067_S1207",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "target_coordinate_first": TARGET_COORDINATES[0],
                "target_coordinate_last": TARGET_COORDINATES[-1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 66,
                "exact_reuse_prefill_count": 65,
                "residual_count": len(rows),
                "reviewed_complete_record_count": 1,
                "same_record_prefill_companion_count": 0,
                "outside_slice_companion_count":
                len(OUTSIDE_SLICE_COMPANION_TRANSLATIONS),
                "optional_s1206_output_present":
                optional_s1206_present,
                "raw_exact_complete_base_donor_record_count": 0,
                "masked_complete_base_donor_record_count": 0,
                "semantic_base_context_record_count": 1,
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
