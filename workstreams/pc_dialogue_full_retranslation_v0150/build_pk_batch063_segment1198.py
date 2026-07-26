#!/usr/bin/env python3
"""Build source-redacted PK B063 segment 1198 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch062_segment1195.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B063_S1198.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B063_S1196.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B063_S1197.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1198
QUEUE_BATCH_ID = "pk_msggame-B063"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "7:1954:0",
    "7:1955:0",
    "7:1957:0",
    "7:1961:0",
    "7:1965:0",
    "7:1966:1",
    "7:1967:0",
    "7:1969:0",
    "7:1970:0",
    "7:1971:1",
    "7:1973:0",
    "7:1976:0",
    "7:1978:1",
    "7:1982:0",
    "7:1983:0",
    "7:1985:0",
    "7:1988:0",
)
TRANSLATIONS = {
    "7:1954:0": "자—",
    "7:1955:0": "좋았어—",
    "7:1957:0": "그렇다면—",
    "7:1961:0": "이제—",
    "7:1965:0": "그럼—",
    "7:1966:1": "이다",
    "7:1967:0": "자—",
    "7:1969:0": "그럼—",
    "7:1970:0": "그렇다면—",
    "7:1971:1": "을(를) 공략할 차례다",
    "7:1973:0": "자—",
    "7:1976:0": "그렇다면—",
    "7:1978:1": "의 방어로 돌아간다",
    "7:1982:0": "좋아—",
    "7:1983:0": "그럼—",
    "7:1985:0": "그럼—",
    "7:1988:0": "자—",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    1954,
    1955,
    1957,
    1961,
    1965,
    1966,
    1967,
    1969,
    1970,
    1971,
    1973,
    1976,
    1978,
    1982,
    1983,
    1985,
    1988,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {record_id: 2 for record_id in TARGET_RECORD_IDS}
TARGET_LITERAL_IDS = {
    1966: 1,
    1971: 1,
    1978: 1,
}
PREFILL_COMPANION_COORDINATES = tuple(
    f"7:{record_id}:{0 if record_id in TARGET_LITERAL_IDS else 1}"
    for record_id in TARGET_RECORD_IDS
)
FUTURE_COMPANION_COORDINATES: tuple[str, ...] = ()
PRIMARY_BASE_MATCH = {
    1954: (7, 1914),
    1955: (7, 1915),
    1957: (7, 1917),
    1961: (7, 1921),
    1965: (7, 1925),
    1966: (7, 1926),
    1967: (7, 1927),
    1969: (7, 1929),
    1970: (7, 1930),
    1971: (7, 1931),
    1973: (7, 1933),
    1976: (7, 1936),
    1978: (7, 1938),
    1982: (7, 1942),
    1983: (7, 1943),
    1985: (7, 1945),
    1988: (7, 1948),
}
EXPECTED_BASE_MATCHES = {
    record_id: (
        ((7, 1945), (7, 1950))
        if record_id == 1985
        else (base_coordinate,)
    )
    for record_id, base_coordinate in PRIMARY_BASE_MATCH.items()
}
EXPECTED_RAW_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_LITERAL_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_MASKED_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_BASE_DONOR_COORDINATES = {
    record_id: tuple(
        f"{base_coordinate[0]}:{base_coordinate[1]}:{literal_id}"
        for literal_id in range(EXPECTED_ARITY[record_id])
    )
    for record_id, base_coordinate in PRIMARY_BASE_MATCH.items()
}
BOUNDARY_RECORD_KEYS = (
    (7, 1950),
    (7, 1951),
    *tuple((7, record_id) for record_id in TARGET_RECORD_IDS),
    (7, 1953),
    (7, 1956),
    (7, 1958),
    (7, 1960),
    (7, 1962),
    (7, 1964),
    (7, 1968),
    (7, 1972),
    (7, 1974),
    (7, 1975),
    (7, 1977),
    (7, 1979),
    (7, 1981),
    (7, 1984),
    (7, 1986),
    (7, 1987),
    (7, 1989),
)
SOURCE_CALL_ROOTS: tuple[int, ...] = ()
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ("026432",)) for record_id in TARGET_RECORD_IDS
}
SPEAKER_STYLE = (
    (1954, "plain_attack_resume"),
    (1955, "exuberant_attack_resume"),
    (1957, "formal_attack_resume"),
    (1961, "relieved_attack_resume"),
    (1965, "measured_enemy_cleanup"),
    (1966, "imperious_next_target"),
    (1967, "plain_unfinished_attack"),
    (1969, "elder_attack_resume"),
    (1970, "formal_attack_resume"),
    (1971, "imperious_next_attack"),
    (1973, "deliberate_attack_resume"),
    (1976, "elder_defense_strengthening"),
    (1978, "plain_return_to_defense"),
    (1982, "rough_defense_return"),
    (1983, "formal_defense_continuation"),
    (1985, "formal_return_to_defense"),
    (1988, "plain_return_to_guard"),
)
TERMINOLOGY_POLICY = (
    ("attack", "공략"),
    ("resume", "재개"),
    ("defense", "방어"),
    ("guard", "수비"),
    ("eliminate enemy", "적을 제거하다"),
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
    "11FF5F480F14CB79B43E538864E83DB188AB7F7529A7F638CC1CD15EE5014D38"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "501D88F8DD2549E9A85920227D09C0BC5A804BC2B4C9391A075DE64A2D8EDAFD"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "A8EB3A482B6958C24AD613A598DEF82375B77C5AA5FA5106AAE25A5B3B7EC24B"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "0EECDC197C68B81E408CD611BD140DE9EE7E416CA65F7BA67371E49947132328"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "AB46465893E2AE4E2716168DEFB276F212D4D54653D203D1CB0799239F4E1996"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "1903F3238AF411DB67FF0156EF1A7CC4046B8216E933C864AEB80573F651D330"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "7243B9E42633BB63719D9EF76A1E196E64D45032FE58598F83021EFCF30DFB8F"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "61FBCCE9AD51DE5D908A641D71436A05AA80D9F38AE0CFFFB84E9CC312C54F6E"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "6DF3DDB2FCF4CD5682F5E40958D3AA992B82A7A5DAEB2C23360AE3E433343C1E"
)
EXPECTED_BOUNDARY_SHA256 = (
    "4C1C7F99D07FC86C63196B78FA94EEFD2351102B2CE4BC137646B1F7488896E7"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "4BCAE45EE3832B0620F9E9BDAD7BB8FEA5830F4098A21F19673210FA115398F6"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "F0527C37474A54BBFE312543116D9949B0B46717C6D21D0AE68DB91E359978FA"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "DBAAF94B0B2ED5D37F13B78FFDCA980E92A43EC31D60142E56E512919521D7F2"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "21B6B6D14D66A9009F55ACEFD92546B3ACE7255FBB73CDF22D1415A494EEAA73"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "92C0BA0EF2754EE134074FC9C5004EBF29D7AF5DBC6B80FFE794A7ED2D0E889B"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "A8FED5397FF1A3EDD288B160FB059A6538A905C2458769BB9DA32C4CAC5C40CC"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "76F9AE0A4A5C41360DAA983E7B901847D5C0356AB8E8D5992753F36F5287FE7E"
)
EXPECTED_CANDIDATE_SHA256 = (
    "BD387BFA522EAE0F03C7EE2477B431A65B530426018D4BCA4FB553A5D42D9049"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "E2868BB370817232766C22F5860E86DE5FE459AA8F462201CA54DF65BE9F947B"
)
EXPECTED_CHANGED_LITERAL_COUNT = 17

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source authoritative; complete PC EN SC TC context "
    "reviewed where present; all seventeen complete PK source records have "
    "completed Base byte-exact source donors whose final Korean is selected "
    "only after manual semantic, terminology and register review; each "
    "target literal is assembled with its approved Base-prefilled same-"
    "record companion; all forty-nine Base prefills in the queue slice are "
    "validated; castle tokens, particles, newlines, protected outer "
    "whitespace, full records, boundaries, two-run reproduction, tamper "
    "rejection, reverse overlays, outside-scope identity and Steam read-"
    "only state are guarded; Base runtime and VM state are not inherited "
    "and every residual remains runtime pending"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1198_base",
        BASE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_base()
PARENT = BASE.PARENT
ENGINE = BASE.ENGINE
sha256_bytes = BASE.sha256_bytes
coordinate_key = BASE.coordinate_key
literal_texts = BASE.literal_texts
gap_bytes = BASE.gap_bytes
read_jsonl = BASE.read_jsonl


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
        len(rows) != 155
        or len(visible) != 200
        or visible[0] != "7:1835:0"
        or visible[-1] != "7:1989:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B063 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "7:1951:0"
        or queue_slice[-1] != "7:1989:1"
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
        len(prefilled) != 49
        or len(residual) != 17
        or residual != TARGET_COORDINATES
    ):
        raise RuntimeError(f"segment {SEGMENT} queue residual drifted")
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
        or len(prefilled) != 49
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
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "PREFILL_COMPANION_COORDINATES": PREFILL_COMPANION_COORDINATES,
        "FUTURE_COMPANION_COORDINATES": FUTURE_COMPANION_COORDINATES,
        "PRIMARY_BASE_MATCH": PRIMARY_BASE_MATCH,
        "EXPECTED_BASE_MATCHES": EXPECTED_BASE_MATCHES,
        "EXPECTED_RAW_BASE_MATCHES": EXPECTED_RAW_BASE_MATCHES,
        "EXPECTED_LITERAL_BASE_MATCHES": EXPECTED_LITERAL_BASE_MATCHES,
        "EXPECTED_MASKED_BASE_MATCHES": EXPECTED_MASKED_BASE_MATCHES,
        "EXPECTED_BASE_DONOR_COORDINATES":
        EXPECTED_BASE_DONOR_COORDINATES,
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
        "DISCOVERED_PINS": DISCOVERED_PINS,
        "BASIS": BASIS,
        "queue_evidence": queue_evidence,
        "build_combined_slice_candidate": build_combined_slice_candidate,
    }
    for name, value in values.items():
        setattr(BASE, name, value)


def build_rows() -> tuple[Any, ...]:
    install_base_globals()
    result = list(BASE.build_rows())
    rows = result[1]
    for row in rows:
        row["manual_complete_base_donor_translation_selected"] = True
        row["manual_semantic_base_references_reviewed"] = True
        row["manual_multilingual_translation_selected"] = False
        row["next_slice_companion_reviewed"] = False
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
        len(rows) != 17
        or len(validated) != 17
        or counts != Counter({"runtime_fragment_pending": 17})
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
    if EXPECTED_CANDIDATE_SHA256 != "TO_PIN":
        PARENT.engine_builder().assert_tamper_rejection(
            prepared,
            rows,
            candidate,
        )
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B063_S1198",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
                "target_coordinate_first": TARGET_COORDINATES[0],
                "target_coordinate_last": TARGET_COORDINATES[-1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 66,
                "exact_reuse_prefill_count": 49,
                "residual_count": len(rows),
                "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
                "same_slice_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "raw_exact_complete_base_donor_record_count":
                len(EXPECTED_BASE_MATCHES),
                "source_call_root_count": len(SOURCE_CALL_ROOTS),
                "current_call_root_count": len(CURRENT_CALL_ROOTS),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "unchanged_literal_count": len(rows) - changed,
                "combined_slice_changed_literal_count": combined_changed,
                "candidate_sha256": candidate_sha256,
                "combined_slice_candidate_sha256": combined_sha256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
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
                "second_run_reproduced": True,
                "outside_scope_identity_guarded": True,
                "tamper_rejection_passed":
                EXPECTED_CANDIDATE_SHA256 != "TO_PIN",
                "discovered_pins": DISCOVERED_PINS,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
