#!/usr/bin/env python3
"""Build source-redacted PK B071 segment 1219 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch071_segment1218.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B071_S1219.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B071_S1217.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B071_S1218.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1219
QUEUE_BATCH_ID = "pk_msggame-B071"
QUEUE_START = 134
QUEUE_STOP = 200
QUEUE_ROW_COUNT = 83
QUEUE_VISIBLE_COUNT = 199
SLICE_VISIBLE_COUNT = 65
SLICE_PREFILL_COUNT = 62
BLOCK_ID = 8
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "8:297:1",
    "8:304:0",
    "8:304:1",
)
TRANSLATIONS = {
    "8:297:1": "다행히\n미리 방책을 마련해 두다니\n",
    "8:304:0": ", 「",
    "8:304:1": (
        "」의 영지에서\n"
        "가뭄이 발생하여\n"
        "토지도 민심도 황폐해져"
    ),
}
TARGET_RECORD_IDS = (297, 304)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    297: 3,
    304: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "8:297:0",
    "8:297:2",
)
PREFILL_COMPANION_DONOR = {
    "8:297:0": "8:289:0",
    "8:297:2": "8:289:3",
}
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR: dict[int, tuple[int, int]] = {}
SEMANTIC_BASE_CONTEXT = {
    297: ("8:289:0", "8:289:1", "8:289:2", "8:289:3"),
    304: (
        "8:295:0",
        "8:295:1",
        "8:296:0",
        "8:296:1",
        "8:296:2",
        "8:297:0",
        "8:297:1",
    ),
}
EXPECTED_BASE_RAW_MATCHES = {
    297: (),
    304: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    297: (),
    304: (),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (8, record_id)
    for record_id in (
        288, 289, 296, 297, 298, 303, 304, 305, 319, 320,
    )
)
SOURCE_CALL_ROOTS = (7, 8, 178, 376, 538)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    297: ((538, 8, 376), ()),
    304: ((8, 7, 178), ()),
}
SPEAKER_STYLE = (
    (297, "drought_foresight_management_praise"),
    (304, "drought_domain_damage_report"),
)
TERMINOLOGY_POLICY = (
    ("drought", "가뭄"),
    ("advance measure", "미리 마련한 방책"),
    ("management", "대처"),
    ("domain", "영지"),
    ("land", "토지"),
    ("popular sentiment", "민심"),
    ("devastation", "황폐"),
    ("project name quotes", "「」"),
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
    "F0CE70C3539C41D234CC21C0678D79783B9BFECD69FBAFE9FC2E0826C8AF6B7F"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "FCC468955B0A53D1397594EBBBBE57173BA322C29274E3A172F077CA3465E2BC"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "971672440DB846BFE3B8979F1AC064249EECC86296436AC4262889AC40735393"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "5EBCD54B5AA49A1568C3EC942DDE028C7636495FA4A4E83610A75EE191DA5766"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "C5BCA258549863ADF09A67D684A4C3904B28A878602FEA9F44B412173C24101B"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "C53A8253C55CDD8779AFE6830C70D7AD10E74460EC520ECCA62FBD0B207EF73F"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "324E9A57D83BB74DD45DC7121CC75765451BBCC581726C42AC7C81EA89CC2F54"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "1E3D9FE04506EC5FD75F2F239F5A4374A5C0AB27B82FE302C27310400C9DA75B"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "C5135FD3DBA2855A3F2EEFEC76D7C646AF521682CD89392F35C2A1667611E0EF"
)
EXPECTED_BOUNDARY_SHA256 = (
    "663081F1AA9F25E33CFE5BD439CD1B9664257246E86C5E5F9407E730AA06887D"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "58F4BD4B065A618D94DC2BA8638FFC245A9351EA63B83B13FA24C6D01F950B62"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "90FBEC603A5386D20A5B4C1F93046F12AD33666703FE024216CF6603AACDAFF3"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "EDF7E81A4036F2DF9EDC4E4221767306A6F8B36BBDF2E7E2BD563E5596E7142F"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "BDFAAEA969DC69D4C91CFFC04331C8A68AA436B1910AA1F049F8B4B57B6E2384"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "BAEAD375E42E3F83C219C683044FCD89E1272DFB29CCA983E0DD448B26C4E628"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "ECEE0C720642E0D91B2BCFA43BE7505D439437D85465EFFDE0125FB6C13495AD"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "9556E328FF4013A9EA94A8CD3B2C53AC35269351947CE449F6683A9CF409A168"
)
EXPECTED_CANDIDATE_SHA256 = (
    "B85774E94D294AF51D5A18B76321E7A1BEB0222FAD652D1B2D96FD24C8BBD8E0"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "97FB265572355261A864A908402208196C2DE3249DA5D40DBC6370DA295D7680"
)
EXPECTED_CHANGED_LITERAL_COUNT = 3
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 60

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative and complete PK EN SC TC context was "
    "manually reviewed; both PK-only drought records have no raw, literal or "
    "call-masked Base match, so completed Base foresight, countermeasure, "
    "domain, land and popular-sentiment wording is semantic context only; "
    "three residuals and two approved prefill companions form two complete "
    "records while all sixty-two slice prefills are preserved; Base runtime "
    "and VM state are never inherited; speaker register, calls, dynamic "
    "persons, project quotes, line counts, protected whitespace, gaps, "
    "two-run reproduction, tamper rejection, reverse overlays, outside-scope "
    "identity and Steam read-only state are guarded"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_b071_s1219_base",
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
base_and_assembly_evidence = BASE.base_and_assembly_evidence


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
        or visible[0] != "8:238:0"
        or visible[-1] != "8:320:2"
    ):
        raise RuntimeError(f"segment {SEGMENT} B071 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != SLICE_VISIBLE_COUNT
        or queue_slice[0] != "8:297:0"
        or queue_slice[-1] != "8:320:2"
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
        "QUEUE_ROW_COUNT": QUEUE_ROW_COUNT,
        "QUEUE_VISIBLE_COUNT": QUEUE_VISIBLE_COUNT,
        "SLICE_VISIBLE_COUNT": SLICE_VISIBLE_COUNT,
        "SLICE_PREFILL_COUNT": SLICE_PREFILL_COUNT,
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
        "base_and_assembly_evidence": base_and_assembly_evidence,
    }
    for name, value in values.items():
        setattr(BASE, name, value)


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
        "segment": "pk_msggame_B071_S1219",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_VISIBLE_COUNT - 1],
        "approved": len(rows),
        "scope_classification_counts": dict(counts),
        "queue_slice_visible_count": SLICE_VISIBLE_COUNT,
        "exact_reuse_prefill_count": SLICE_PREFILL_COUNT,
        "residual_count": len(rows),
        "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
        "same_record_prefill_companion_count":
        len(PREFILL_COMPANION_COORDINATES),
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
