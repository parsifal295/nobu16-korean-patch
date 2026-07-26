#!/usr/bin/env python3
"""Build source-redacted PK B063 segment 1197 residual decisions."""

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
PARENT_PATH = WORKSTREAM / "build_pk_batch062_segment1194.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B063_S1197.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B063_S1196.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B063_S1198.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1197
QUEUE_BATCH_ID = "pk_msggame-B063"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "7:1901:0",
    "7:1913:1",
    "7:1915:1",
    "7:1917:1",
    "7:1919:1",
    "7:1925:1",
    "7:1926:1",
    "7:1932:1",
)
TRANSLATIONS = {
    "7:1901:0": "은(는)\n",
    "7:1913:1": "로 돌아가라",
    "7:1915:1": "으로 향한다",
    "7:1917:1": "에 입성한다",
    "7:1919:1": "로 돌아간다",
    "7:1925:1": "로 돌아간다",
    "7:1926:1": "에 입성하라",
    "7:1932:1": "으로 귀환하자",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (1901, 1913, 1915, 1917, 1919, 1925, 1926, 1932)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {record_id: 2 for record_id in TARGET_RECORD_IDS}
PREFILL_COMPANION_COORDINATES = (
    "7:1901:1",
    "7:1913:0",
    "7:1915:0",
    "7:1917:0",
    "7:1919:0",
    "7:1925:0",
    "7:1926:0",
    "7:1932:0",
)
INVISIBLE_COMPANION_COORDINATES: tuple[str, ...] = ()
FUTURE_COMPANION_COORDINATES: tuple[str, ...] = ()
PRIMARY_BASE_MATCH = {
    1901: (7, 1861),
    1913: (7, 1873),
    1915: (7, 1875),
    1917: (7, 1877),
    1919: (7, 1879),
    1925: (7, 1885),
    1926: (7, 1886),
    1932: (7, 1892),
}
EXPECTED_BASE_MATCHES = {
    record_id: (base_coordinate,)
    for record_id, base_coordinate in PRIMARY_BASE_MATCH.items()
}
EXPECTED_RAW_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_LITERAL_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_MASKED_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_BASE_DONOR_COORDINATES = {
    record_id: (
        f"{base_coordinate[0]}:{base_coordinate[1]}:0",
        f"{base_coordinate[0]}:{base_coordinate[1]}:1",
    )
    for record_id, base_coordinate in PRIMARY_BASE_MATCH.items()
}
BOUNDARY_RECORD_KEYS = (
    (7, 1834),
    (7, 1835),
    (7, 1896),
    (7, 1897),
    (7, 1900),
    (7, 1901),
    (7, 1902),
    (7, 1912),
    (7, 1913),
    (7, 1914),
    (7, 1915),
    (7, 1916),
    (7, 1917),
    (7, 1918),
    (7, 1919),
    (7, 1920),
    (7, 1924),
    (7, 1925),
    (7, 1926),
    (7, 1927),
    (7, 1931),
    (7, 1932),
    (7, 1933),
    (7, 1950),
    (7, 1951),
    (7, 1989),
    (7, 1990),
)
SOURCE_CALL_ROOTS = (1,)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    1901: ((1,), ("029632",)),
    1913: ((), ("029632", "023C")),
    1915: ((), ("029632", "023C")),
    1917: ((), ("029632", "023C")),
    1919: ((), ("029632", "023C")),
    1925: ((), ("029632", "023C")),
    1926: ((), ("029632", "023C")),
    1932: ((), ("029632", "023C")),
}
SPEAKER_STYLE = (
    (1901, "territorial_possession_assertion"),
    (1913, "attack_abandonment_order"),
    (1915, "attack_abandonment_march_order"),
    (1917, "occupation_unneeded_entry_order"),
    (1919, "occupation_unneeded_return_order"),
    (1925, "occupation_abandonment_return_order"),
    (1926, "occupation_complete_entry_order"),
    (1932, "new_ally_return_proposal"),
)
TERMINOLOGY_POLICY = (
    ("attack", "공략"),
    ("occupy", "제압"),
    ("enter castle", "입성하다"),
    ("return", "돌아가다"),
    ("withdraw home", "귀환하다"),
    ("ally", "아군"),
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
    "2863D1BFFBC393FE24F65BFC59C42EC68C7B8E0843B0DF36C9693AD1C247CAAD"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "3DB80DA40D9BED46E94E089952A5FA43E6722E2F8AB0E6050315BA74C3AAA0C8"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "4E6B769DB2EBFCB366BAE33002A8B1DCF9C8C4038AF5AB0C8C2B440C204BDEA5"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "02B8D4D7D902E7AAA8C76D77C897DBFF3E4A9C030633B52EDFD7658985F8948F"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "E2EB8A7B4CD884F124664705359C2CF9CADD8C79781487F82B00A06022409838"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "ECACD13E2B8EFCCD84FA5F438C8E4C0E390937FD80DFC49EC2552927CC7587BE"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "61FBCCE9AD51DE5D908A641D71436A05AA80D9F38AE0CFFFB84E9CC312C54F6E"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "A037D693B37823F58078F1638FBD76AE26D953186AC91DEF83A0A45D5B6014C4"
)
EXPECTED_BOUNDARY_SHA256 = (
    "F03D39FBBC9E0C7A5EC4FE40A9E44E4803C34DE45E6BC95FEFB5E9B18F7E076D"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "8007F401FA962765D21F8FA40CDDFFF539761EB87559BE87E8F585F733DCC069"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "F263D39911A62614643D7A378F049DB283DC01B8717BB834C6F94EA7FA64A6D6"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "2C54344D8D1818B88B2FECCFB56045659CE2243A856257C26AA5861E2E6503C5"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "198DDF0969C36ABA0D2F667F27B8F0B14D684DA3A06892B30443AFABA0BD4E62"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "39A115B2F066C9E30B57C118DFAF4921C05FE12B76622CF7AD28477352578EE7"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "6EAA0E00B51E32F5278A1B3924F40C4640920F3C0133EB898024F5E3262F9292"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "CDF972D132D127B305B18409EB5B6D1228917B6141DFF1068E92CB7FA4707D7E"
)
EXPECTED_CANDIDATE_SHA256 = (
    "DC1B3840090105928AE4A42081DDDF6A1FA673A430AAD5BBC7F89CE24E04D184"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "7B048CA2FAA7D973AD3815911C8AD8998297258074ADA8B5E2D73CD9AAF166D7"
)
EXPECTED_CHANGED_LITERAL_COUNT = 7

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese source authoritative; complete PC English, "
    "Simplified Chinese and Traditional Chinese records were reviewed "
    "where present; every complete PK source record has one byte-exact "
    "completed Base donor, whose final Korean was reused only after "
    "manual semantic, terminology and speaker-register review; each "
    "residual fragment is assembled with its approved same-record Base "
    "prefill companion; the shared record-1 call graph, particles, "
    "newlines, protected outer whitespace, complete records, gaps and "
    "inline tokens are guarded; all fifty-nine prefills in the queue "
    "slice are validated and the sixty-seven-row combined slice is "
    "rebuilt in both orders and reversed byte-exactly; two-run "
    "reproduction, tamper rejection, outside-scope identity and Steam "
    "read-only state are guarded; Base runtime and VM state are not "
    "inherited and every residual remains runtime pending"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1197_parent",
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
sha256_bytes = PARENT.sha256_bytes
canonical_sha256 = PARENT.canonical_sha256
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
        len(rows) != 155
        or len(visible) != 200
        or visible[0] != "7:1835:0"
        or visible[-1] != "7:1989:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B063 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "7:1897:0"
        or queue_slice[-1] != "7:1950:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in prefill_rows
    )
    if (
        len(prefilled) != 59
        or len(residual) != 8
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
        len(replacements) != 67
        or len(prefilled) != 59
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


def configure_parent() -> None:
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
        "INVISIBLE_COMPANION_COORDINATES":
        INVISIBLE_COMPANION_COORDINATES,
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
        "DISCOVERED_PINS": DISCOVERED_PINS,
        "BASIS": BASIS,
    }
    for name, value in values.items():
        setattr(PARENT, name, value)
    PARENT.queue_evidence = queue_evidence
    PARENT.build_combined_slice_candidate = build_combined_slice_candidate


def build_rows() -> tuple[Any, ...]:
    configure_parent()
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
        len(rows) != 8
        or len(validated) != 8
        or counts != Counter({"runtime_fragment_pending": 8})
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
        PARENT.PARENT.PARENT.engine_builder().assert_tamper_rejection(
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
                "segment": "pk_msggame_B063_S1197",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "target_coordinate_first": TARGET_COORDINATES[0],
                "target_coordinate_last": TARGET_COORDINATES[-1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 67,
                "exact_reuse_prefill_count": 59,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
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
