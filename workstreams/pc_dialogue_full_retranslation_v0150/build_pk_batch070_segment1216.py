#!/usr/bin/env python3
"""Build source-redacted PK B070 segment 1216 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch070_segment1215.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B070_S1216.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B070_S1214.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B070_S1215.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1216
QUEUE_BATCH_ID = "pk_msggame-B070"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 8
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "8:203:0",
    "8:213:0",
    "8:216:1",
    "8:218:0",
    "8:224:0",
    "8:225:0",
    "8:227:0",
    "8:229:0",
    "8:230:0",
    "8:232:0",
    "8:233:0",
    "8:234:0",
    "8:236:0",
    "8:236:1",
)
TRANSLATIONS = {
    "8:203:0": "여기가 「",
    "8:213:0": "자, 「",
    "8:216:1": "을(를) 차지하겠다!",
    "8:218:0": "자, 「",
    "8:224:0": "모두, 「",
    "8:225:0": "그럼 「",
    "8:227:0": "자, 「",
    "8:229:0": "자, 「",
    "8:230:0": "여러분, 「",
    "8:232:0": "좋아, 「",
    "8:233:0": "모두, 「",
    "8:234:0": "그럼, 「",
    "8:236:0": "모두!\n",
    "8:236:1": "에 들어간다!",
}
TARGET_RECORD_IDS = (
    203,
    213,
    216,
    218,
    224,
    225,
    227,
    229,
    230,
    232,
    233,
    234,
    236,
)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {record_id: 2 for record_id in TARGET_RECORD_IDS}
PREFILL_COMPANION_COORDINATES = (
    "8:203:1",
    "8:213:1",
    "8:216:0",
    "8:218:1",
    "8:224:1",
    "8:225:1",
    "8:227:1",
    "8:229:1",
    "8:230:1",
    "8:232:1",
    "8:233:1",
    "8:234:1",
)
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR = {
    203: (8, 197),
    213: (8, 207),
    216: (8, 210),
    218: (8, 212),
    224: (8, 218),
    225: (8, 219),
    227: (8, 221),
    229: (8, 223),
    230: (8, 224),
    232: (8, 226),
    233: (8, 227),
    234: (8, 228),
    236: (8, 230),
}
SEMANTIC_BASE_CONTEXT: dict[int, tuple[str, ...]] = {}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: (donor,)
    for record_id, donor in EXACT_BASE_DONOR.items()
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (8, record_id)
    for record_id in (
        190,
        197,
        202,
        203,
        204,
        207,
        210,
        212,
        213,
        216,
        218,
        219,
        221,
        223,
        224,
        225,
        226,
        227,
        228,
        229,
        230,
        231,
        232,
        233,
        234,
        235,
        236,
        237,
    )
)
SOURCE_CALL_ROOTS = (8,)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    203: ((), ("029632",)),
    213: ((), ("026432",)),
    216: ((), ("026432",)),
    218: ((), ("026432",)),
    224: ((), ("029632",)),
    225: ((), ("029632",)),
    227: ((), ("029632",)),
    229: ((), ("026432",)),
    230: ((), ("026432",)),
    232: ((), ("026432",)),
    233: ((), ("026432",)),
    234: ((), ("026432",)),
    236: ((), ("026432",)),
}
SPEAKER_STYLE = (
    (203, "battle_preparation_command"),
    (213, "castle_assault_command"),
    (216, "castle_assault_command"),
    (218, "castle_assault_command"),
    (224, "march_command"),
    (225, "march_command"),
    (227, "march_command"),
    (229, "castle_entry_command"),
    (230, "castle_entry_command"),
    (232, "castle_entry_command"),
    (233, "castle_entry_command"),
    (234, "castle_entry_command"),
    (236, "castle_entry_command"),
)
TERMINOLOGY_POLICY = (
    ("battle preparation", "전투 준비"),
    ("castle assault", "공략"),
    ("capture", "차지하다"),
    ("march", "진격하다"),
    ("enter castle", "입성하다"),
    ("quoted dynamic castle or destination", "「…」"),
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
    "AEA7C7F12C56EE973DF4761FE00037B3CED06F9B2FCA0E0ABBB35D4AF1A9190A"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "98520408189AF2FD7653F6A5E0C60DA175D8C70E8077909C8414EA3988EAC4D1"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "78F0717FDA0E37354EC7B2C36B3B6D9865E6BF0E02B70D5E81B831C9A684F23E"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "5D8F086F2BC7BEB2ECC455CE7063640763998B017901E2DEDCCE54BBFCEBAC37"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "40FF02641BDAD0EC4D608B5603EE3636A9B548799D4BE2DDA196604CF2EDF1F1"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "D541A8B2DD2A89799CA3060964C4BEAB4F640DD027D02FB3DABDC7982EC82BB2"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "069E391B62C48FA51134BEC78AF1670B75FC97C4939A184F43AA1AE029A78394"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "C7F5DE16C15EFEC9908081B036DDC70F6F9B7E193479371432246DAE9C30EAE0"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "9525AED8A9BF3B47D57796CA7646F4FA0DA56ABC23383B796B73CF94E238429B"
)
EXPECTED_BOUNDARY_SHA256 = (
    "1DB46E46218F6EC65B32204F50640AD399050C26231FC85603A9484FCE42F398"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "4204B99448622985B9DC26D6AD9F4D119A9DB1E28523366C10FE96C04FA68D8F"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "BF0E60FB6D86AB2019DBB00917DD5E950BD513657D39FAEA89474E9AEA7207EC"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "FC2FA1E79FDD6AF9474FEB3FCD249D32346F4BE36E2E5736764AB057C5B6A849"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "34F168518E1698E7FE9E5BC5D2252B8EBD655E803B6CE7BBC2DB0A0E5D20F05B"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "62544F9711F034981233C21216E3138CCBCEE1E236A7ED97B8A2439AB5CA19A1"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "49242DA2A7AE6276E37F69273137FEB08BBC9DF12660847DC4C0E0CEBFAE4F1B"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "05702F823A60FF1097B42EAD0B6AB4F000352162B1CF4C92E9D729A05CD1E235"
)
EXPECTED_CANDIDATE_SHA256 = (
    "65389B9D52FDD6ACD5680A584621E5DA8686F75447F850A46F96EECBA4746769"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "B336573CA05DDBA3D8412D175ECAA81DC08EFB5FA60D1C280CF5B69E55F50356"
)
EXPECTED_CHANGED_LITERAL_COUNT = 13
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 58

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative and complete PK EN SC TC context was "
    "reviewed; all thirteen complete records are raw-exact to completed Base "
    "donors and all twelve same-record exact prefill companions are validated; "
    "Base runtime and VM state are never inherited; castle and destination "
    "tokens, protected outer whitespace, source and current gaps, queue and "
    "segment boundaries, two-run reproduction, tamper rejection, reverse "
    "overlays, outside-scope identity, and Steam read-only state are guarded"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1216_base",
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
        len(rows) != 146
        or len(visible) != 200
        or visible[0] != "7:2859:0"
        or visible[-1] != "8:237:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B070 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "8:190:0"
        or queue_slice[-1] != "8:237:0"
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
        len(prefilled) != 52
        or len(residual) != 14
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
        or len(prefilled) != 52
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
        len(rows) != 14
        or len(validated) != 14
        or counts != Counter({"runtime_fragment_pending": 14})
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
    install_base_globals()
    BASE.install_base_globals()
    BASE.BASE.install_base_globals()
    BASE.BASE.BASE.install_base_globals()
    BASE.BASE.BASE.BASE.propagate_base_globals()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B070_S1216",
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
                "exact_reuse_prefill_count": 52,
                "residual_count": len(rows),
                "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "raw_exact_complete_base_donor_record_count":
                len(EXACT_BASE_DONOR),
                "masked_complete_base_donor_record_count": 0,
                "semantic_base_context_record_count": 0,
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
            },
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
