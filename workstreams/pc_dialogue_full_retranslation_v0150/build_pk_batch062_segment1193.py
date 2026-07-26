#!/usr/bin/env python3
"""Build source-redacted PK B062 segment 1193 residual decisions."""

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
PARENT_PATH = WORKSTREAM / "build_pk_batch060_segment1190.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B062_S1193.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B062_S1194.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B062_S1195.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1193
QUEUE_BATCH_ID = "pk_msggame-B062"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "7:1694:0",
    "7:1695:1",
    "7:1696:0",
    "7:1698:0",
    "7:1700:0",
    "7:1701:1",
    "7:1702:0",
    "7:1704:1",
    "7:1706:0",
    "7:1707:1",
    "7:1708:0", "7:1708:1",
    "7:1712:0",
    "7:1714:0",
    "7:1715:0",
    "7:1716:1",
    "7:1719:1",
    "7:1720:1",
    "7:1721:1",
    "7:1722:0",
)
TRANSLATIONS = {
    "7:1694:0": "의 성—",
    "7:1695:1": "에게서 빼앗을 성—",
    "7:1696:0": "은(는)—",
    "7:1698:0": "의 성—",
    "7:1700:0": "의 성—",
    "7:1701:1": "에게서 빼앗을 성—",
    "7:1702:0": "의 성—",
    "7:1704:1": "에게서 빼앗을 성—",
    "7:1706:0": "의 성—",
    "7:1707:1": "에게서\n",
    "7:1708:0": "때는 지금이옵니다\n",
    "7:1708:1": "의 성—",
    "7:1712:0": "의 성—",
    "7:1714:0": "에게서—",
    "7:1715:0": "의 성—",
    "7:1716:1": "의 성—",
    "7:1719:1": "의 성—",
    "7:1720:1": "의 성—",
    "7:1721:1": "의 성—",
    "7:1722:0": "에게서\n",
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
    1694: 2,
    1695: 3,
    1696: 2,
    1698: 2,
    1700: 2,
    1701: 3,
    1702: 2,
    1704: 3,
    1706: 2,
    1707: 3,
    1708: 3,
    1712: 2,
    1714: 2,
    1715: 2,
    1716: 3,
    1719: 3,
    1720: 3,
    1721: 3,
    1722: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "7:1694:1",
    "7:1695:0", "7:1695:2",
    "7:1696:1",
    "7:1698:1",
    "7:1700:1",
    "7:1701:0", "7:1701:2",
    "7:1702:1",
    "7:1704:0", "7:1704:2",
    "7:1706:1",
    "7:1707:0", "7:1707:2",
    "7:1708:2",
    "7:1712:1",
    "7:1714:1",
    "7:1715:1",
    "7:1716:0", "7:1716:2",
    "7:1719:0", "7:1719:2",
    "7:1720:0", "7:1720:2",
    "7:1721:0", "7:1721:2",
    "7:1722:1",
)
EXACT_BASE_DONOR = {
    record_id: (7, record_id - 40)
    for record_id in TARGET_RECORD_IDS
}
SEMANTIC_BASE_CONTEXT: dict[int, tuple[str, ...]] = {}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: (EXACT_BASE_DONOR[record_id],)
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (7, record_id)
    for record_id in (
        1693, 1694, 1695, 1696, 1697, 1698, 1700, 1701,
        1702, 1704, 1706, 1707, 1708, 1712, 1714, 1715,
        1716, 1719, 1720, 1721, 1722, 1723, 1833, 1834,
    )
)
SOURCE_CALL_ROOTS: tuple[int, ...] = ()
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: (
        (),
        (
            ("026432", "025032")
            if record_id == 1696
            else ("025032", "026432")
        ),
    )
    for record_id in TARGET_RECORD_IDS
}
SPEAKER_STYLE = (
    (1694, "defensive_weakness_attack_counsel"),
    (1695, "formal_policy_change_counsel"),
    (1696, "confident_capture_counsel"),
    (1698, "opportunistic_capture_counsel"),
    (1700, "nuisance_elimination_counsel"),
    (1701, "formal_policy_withdrawal_counsel"),
    (1702, "current_affairs_invasion_counsel"),
    (1704, "decisive_capture_counsel"),
    (1706, "valuable_castle_counsel"),
    (1707, "formal_policy_change_request"),
    (1708, "formal_immediate_capture_counsel"),
    (1712, "target_opportunity_counsel"),
    (1714, "confident_capture_command_request"),
    (1715, "feasible_capture_counsel"),
    (1716, "formal_policy_review_request"),
    (1719, "collective_policy_change_counsel"),
    (1720, "bold_capture_counsel"),
    (1721, "cautious_policy_change_counsel"),
    (1722, "alternative_capture_counsel"),
)
TERMINOLOGY_POLICY = (
    ("castle", "성"),
    ("policy", "지침"),
    ("capture", "차지"),
    ("seize from", "에게서 빼앗다"),
    ("attack opportunity", "공격할 호기"),
    ("invasion", "침공"),
    ("order", "명"),
    ("dynamic castle delimiter", "—"),
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
    "E9BED04E132FE50D553B932012827D4F754D2B3EA11B253B5D90F7D088BAFB6B"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "77427BEB6E196DADE4BCED58DD44FE1EF7B0D348242C24C1C934889920383282"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "E2A699669020E07E99B76890286EBDDC7881D0BB1DE48884697E4B2F253EBBC3"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "103B08BD5891E8AB4F600446AFA69E1CF21550ADBB81BAD3E46E89F6ECB36609"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "FF9DD8C425F34B7F0EE6F6CB8D9CA298E44C8E122FF6323050E13F877C2941FE"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "EEE9832C7E98E7A2C189FDEEB77927F79AA6B4D581211723AD811617D89DB122"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "783511AA7CB6E48889BF734FC7B171D86926AA9F093FA0EF3FE9BA8238A42D83"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "EF50B0B5E10DE71B1AD8E7E6B7C05C4FB106870AAB8E3B6C4E1CFA93D9DA1B9A"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "3414DE5C68BF7883C80EEBB68D615ED9BFA547CA737ADA400C2055CA7D23D1A1"
)
EXPECTED_BOUNDARY_SHA256 = (
    "13B99299F87E4520A1E844678D7C373F954D9612B2BE749E67E66E79FC51698A"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "617B884C3E928461306756C45BBA3284864FCA73D8B1764539C575B85E9A027D"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "C58CEB0551D722F9CF7D3987A0344353CBB1B32131FF725CFE1C278986714879"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "A008B85D82AECC7B29620F0CC858E2F519F55F0428249EE5F7F678A97EC8E27C"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "1005C170E8B70AAAD0D47268AF465968D193ED5125088899AB55F86F958E102E"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "773669C239BF164BF3E1C29277A25A07274409727AF0B50AE1E12C4B06A4910B"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "6CB266DCE40E1868A514FCE1DE930E5A3892D06F3D02339E74DE65F16CA6D184"
)
EXPECTED_CANDIDATE_SHA256 = (
    "81E5A17890F35BA1783CFEE6F152CCBC7236139017166F1BF3867A8AF42C56A1"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "58FBA5A8D5E6F6A20D3900339B0C33F12FFC53CA404FBA7A4307670B3306A4E0"
)
EXPECTED_CHANGED_LITERAL_COUNT = 20
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 61

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative and complete PK EN SC TC context "
    "was manually reviewed; all nineteen complete PK castle-opportunity "
    "records are raw, literal and operand exact with completed Base records "
    "at a verified minus-forty mapping, while all twenty-seven same-record "
    "companions and the other twenty queue prefills are validated from the "
    "existing Base exact-reuse prefill; Base runtime and VM state are never "
    "inherited; complete records, faction and castle tokens, protected outer "
    "whitespace, source and current gaps, queue and segment boundaries, "
    "two-run reproduction, tamper rejection, reverse overlays, outside-scope "
    "identity, and Steam read-only state are guarded"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1193_parent",
        PARENT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {PARENT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PARENT = load_parent()
CORE = PARENT.CORE
ENGINE = PARENT.ENGINE
sha256_bytes = PARENT.sha256_bytes
coordinate_key = PARENT.coordinate_key
literal_texts = PARENT.literal_texts
gap_bytes = PARENT.gap_bytes
read_jsonl = PARENT.read_jsonl


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
        len(rows) != 141
        or len(visible) != 200
        or visible[0] != "7:1694:0"
        or visible[-1] != "7:1834:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B062 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "7:1694:0"
        or queue_slice[-1] != "7:1722:0"
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
    if len(prefilled) != 47 or residual != TARGET_COORDINATES:
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
        len(replacements) != 67
        or len(prefilled) != 47
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
        "PREFILL_COMPANION_COORDINATES":
        PREFILL_COMPANION_COORDINATES,
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
    PARENT.build_combined_slice_candidate = build_combined_slice_candidate
    PARENT.patch_parent_globals()
    CORE.queue_evidence = queue_evidence


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
    return PARENT.build_rows()


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
        len(rows) != 20
        or len(validated) != 20
        or counts != Counter({"runtime_fragment_pending": 20})
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
        "segment": "pk_msggame_B062_S1193",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "approved": len(rows),
        "scope_classification_counts": dict(counts),
        "queue_slice_visible_count": 67,
        "exact_reuse_prefill_count": 47,
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
    }, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
