#!/usr/bin/env python3
"""Build source-redacted PK B073 segment 1225 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch073_segment1223.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B073_S1225.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B073_S1223.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1225
QUEUE_BATCH_ID = "pk_msggame-B073"
QUEUE_START = 134
QUEUE_STOP = 199
BLOCK_ID = 8
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "8:518:0",
    "8:521:0",
    "8:521:2",
    "8:521:3",
    "8:522:1",
    "8:523:1",
    "8:524:0",
    "8:524:2",
    "8:527:0",
    "8:527:1",
    "8:527:2",
    "8:532:0",
)
TRANSLATIONS = {
    "8:518:0": "후후…",
    "8:521:0": "의 「",
    "8:521:2": "→",
    "8:521:3": ")",
    "8:522:1": "」로 진화",
    "8:523:1": "」로 퇴화",
    "8:524:0": "의 군 특성 「",
    "8:524:2": "까지 저하",
    "8:527:0": "의 군 특성 「",
    "8:527:1": "」이(가) LV",
    "8:527:2": "까지 성장",
    "8:532:0": "이것이 「",
}
TARGET_RECORD_IDS = (518, 521, 522, 523, 524, 527, 532)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    518: 2,
    521: 4,
    522: 2,
    523: 2,
    524: 3,
    527: 3,
    532: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "8:518:1",
    "8:521:1",
    "8:522:0",
    "8:523:0",
    "8:524:1",
    "8:532:1",
)
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR = {
    record_id: (8, record_id - 12)
    for record_id in TARGET_RECORD_IDS
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
        457,
        458,
        506,
        509,
        510,
        511,
        512,
        515,
        516,
        517,
        518,
        519,
        520,
        521,
        522,
        523,
        524,
        525,
        526,
        527,
        528,
        531,
        532,
        533,
        566,
    )
)
SOURCE_CALL_ROOTS = (8, 1)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    518: ((8,), ()),
    521: ((), ("024633", "023C", "0232", "0233")),
    522: ((), ("029632", "023C")),
    523: ((), ("029632", "023C")),
    524: ((), ("029632", "023C", "0232")),
    527: ((), ("029632", "02BE32", "0232")),
    532: ((1,), ()),
}
SPEAKER_STYLE = (
    (518, "formal_deathbed_retainer"),
    (521, "ability_growth_ui"),
    (522, "county_trait_growth_ui"),
    (523, "county_trait_growth_ui"),
    (524, "county_trait_growth_ui"),
    (527, "county_trait_growth_ui"),
    (532, "chigyo_evaluation_grievance"),
)
TERMINOLOGY_POLICY = (
    ("ability", "능력"),
    ("county trait", "군 특성"),
    ("level", "LV"),
    ("evolve", "진화"),
    ("regress", "퇴화"),
    ("grow", "성장"),
    ("chigyo stipend land", "지행"),
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
    "B5437CF63BACD9D5C10DCE0D5471BE558AA4353A83DBE1292A471FC61333A2F2"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "3B8B95DF8ABADB564A108557BCC4256BC98905DB4D0C0C9EB347CA490497B338"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "9D19A077B54C1E706745272BFD5E1A3E29575521DAAC936B1549097F60BB8263"
)
EXPECTED_ZERO_MIDDLE_PREFILL_SHA256 = (
    "BFB2A6DA97A50CE8D2FED93D93B17879D323ECB7C4345688F53A0DEDC3B55E23"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "8B9D03FEC8661A79EA9084BCE2564D8B4CF1CC2383C4130475B76A109921A7FB"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "4FF9E859CC35583F1DCDDF177CCB8E695A1E3ED52D92492B30251E153BBCD3CD"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "F6ECFC35E5640928766A40CB9CC84293FF34E7E78BDA4ED293A45304C69574B6"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "5FD35D89DF4AA689D48185B9B3B27B2DA559550F564662F13A082E72F9B83648"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "4B4BC82D0176364EF8198A2F963A04C83D58EEB699CB59F0FCB8E0471FD6C208"
)
EXPECTED_BOUNDARY_SHA256 = (
    "9856267614C687577EA3D69A8B9A48A03E8E1AF700F06C32F6A111B09DCC1B4E"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "BD2BC548813F1A2343C6A2EF48AF6B0F96125E79B14156A808A239BD7F59717D"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "1D8213E7A552229577F530AFF100593E496CFE6C645B1C26086077EF11A9F7EB"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "67763BDC647097A46C05F70F8EF97129948F2ACB829DBF5423F2A4ABB18C9559"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "1B3866CBE43B1909CE5551E2342FFF1192EE02E9D508768E4073B564E186B2FA"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "D759645A193C4076357A0F37E0F749F7BF8CB3E5A66A10B6A432274039A300C9"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "780DAD8DC4200DCE2B5A8F4F853C088AADDCA0E2DB8E91CD5E654586F5581A65"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "BCFC7D6DE9CE973C451BAC9F7E7D4CB328609F5382E279A024EDADED053268A5"
)
EXPECTED_CANDIDATE_SHA256 = (
    "DE25F30AE3294D8A3E0EDECB9725FD1841F7FD1B222C7A821B8C2182CC361C9D"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "A00B9BA5204EE3477D4D92B1FAA95F9DC0C0A287433304FAB11F4AAEA8220E15"
)
EXPECTED_CHANGED_LITERAL_COUNT = 4
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 49

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative and complete PK EN SC TC context was "
    "reviewed; all seven complete records are raw-exact to completed Base "
    "donors, all six same-record companions, all fifty-three slice prefills, "
    "and the zero-residual middle slice of sixty-seven exact prefills are "
    "validated; Base runtime and VM state are never inherited; ability, county "
    "trait, level and chigyo terminology, formal deathbed and grievance "
    "registers, dynamic tokens, calls, protected whitespace, gaps, zero-middle "
    "boundaries, two-run reproduction, tamper rejection, reverse overlays, "
    "outside-scope identity, and Steam read-only state are guarded"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1225_base",
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
        len(queue_slice) != 65
        or queue_slice[0] != "8:517:0"
        or queue_slice[-1] != "8:566:0"
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
        len(prefilled) != 53
        or len(residual) != 12
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
        len(replacements) != 65
        or len(prefilled) != 53
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
        len(rows) != 12
        or len(validated) != 12
        or counts != Counter({"runtime_fragment_pending": 12})
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
                "segment": "pk_msggame_B073_S1225",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "approved": len(rows),
                "queue_slice_visible_count": 65,
                "exact_reuse_prefill_count": 53,
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
