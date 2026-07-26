#!/usr/bin/env python3
"""Build source-redacted PK B076 segment 1234 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch076_segment1233.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B076_S1234.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B076_S1233.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1234
QUEUE_BATCH_ID = "pk_msggame-B076"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 8
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "8:966:1",
    "8:967:1",
    "8:968:1",
    "8:969:1",
    "8:970:1",
    "8:971:1",
    "8:972:0",
    "8:973:0",
    "8:974:0",
    "8:975:0",
    "8:976:0",
    "8:977:0",
    "8:977:2",
    "8:978:0",
    "8:978:2",
    "8:979:0",
    "8:979:2",
    "8:980:0",
    "8:980:1",
    "8:984:0",
    "8:985:0",
    "8:986:0",
    "8:988:0",
    "8:988:1",
    "8:989:0",
    "8:989:1",
    "8:991:0",
    "8:991:1",
    "8:992:0",
    "8:992:1",
    "8:994:2",
)
TRANSLATIONS = {
    "8:966:1": "!",
    "8:967:1": "!",
    "8:968:1": "!",
    "8:969:1": "!　",
    "8:970:1": "!　",
    "8:971:1": "!　",
    "8:972:0": "에서 「",
    "8:973:0": "에서 「",
    "8:974:0": "에서 「",
    "8:975:0": "에서 「",
    "8:976:0": "에서 「",
    "8:977:0": "에서 「",
    "8:977:2": "!",
    "8:978:0": "이(가) 「",
    "8:978:2": "……",
    "8:979:0": "에서 「",
    "8:979:2": "……",
    "8:980:0": "이곳은",
    "8:980:1": "에게",
    "8:984:0": "의",
    "8:985:0": "에서 「",
    "8:986:0": "영내의 「",
    "8:988:0": "영내의 「",
    "8:988:1": "」 등 총\n",
    "8:989:0": "영내의 「",
    "8:989:1": "」 등 총",
    "8:991:0": "영내의 「",
    "8:991:1": "」 등 총",
    "8:992:0": ", 맡겨",
    "8:992:1": "\n그리",
    "8:994:2": "」 장악에\n착수",
}
TARGET_RECORD_IDS = (
    966,
    967,
    968,
    969,
    970,
    971,
    972,
    973,
    974,
    975,
    976,
    977,
    978,
    979,
    980,
    984,
    985,
    986,
    988,
    989,
    991,
    992,
    994,
)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    966: 2,
    967: 2,
    968: 2,
    969: 3,
    970: 3,
    971: 3,
    972: 2,
    973: 2,
    974: 2,
    975: 2,
    976: 2,
    977: 3,
    978: 3,
    979: 3,
    980: 3,
    984: 2,
    985: 2,
    986: 2,
    988: 3,
    989: 3,
    991: 3,
    992: 4,
    994: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "8:966:0",
    "8:967:0",
    "8:968:0",
    "8:969:0",
    "8:969:2",
    "8:970:0",
    "8:970:2",
    "8:971:0",
    "8:971:2",
    "8:972:1",
    "8:973:1",
    "8:974:1",
    "8:975:1",
    "8:976:1",
    "8:977:1",
    "8:978:1",
    "8:979:1",
    "8:980:2",
    "8:984:1",
    "8:985:1",
    "8:986:1",
    "8:988:2",
    "8:989:2",
    "8:991:2",
    "8:992:2",
    "8:992:3",
    "8:994:0",
    "8:994:1",
)
CROSS_SEGMENT_DONOR_COMPANION_COORDINATES: tuple[str, ...] = ()
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR = {
    **{record_id: (8, record_id - 12) for record_id in range(969, 981)},
    984: (8, 972),
    985: (8, 973),
    986: (8, 974),
    988: (8, 976),
    989: (8, 977),
    991: (8, 979),
    992: (8, 980),
}
SEMANTIC_BASE_CONTEXT = {
    966: ("8:954:0", "8:954:1"),
    967: ("8:954:0", "8:954:1"),
    968: ("8:954:0", "8:954:1"),
    994: ("8:982:0", "8:982:1", "8:982:2"),
}
EXPECTED_BASE_RAW_MATCHES = {
    966: (),
    967: (),
    968: (),
    969: (),
    970: (),
    971: (),
    972: ((8, 960),),
    973: ((8, 961),),
    974: ((8, 962),),
    975: ((8, 963),),
    976: (),
    977: (),
    978: (),
    979: (),
    980: (),
    984: ((6, 4054), (8, 972)),
    985: ((8, 973),),
    986: ((8, 974),),
    988: ((8, 976),),
    989: ((8, 977),),
    991: ((8, 979),),
    992: (),
    994: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    966: (),
    967: (),
    968: (),
    969: ((8, 957), (8, 958), (8, 959)),
    970: ((8, 957), (8, 958), (8, 959)),
    971: ((8, 957), (8, 958), (8, 959)),
    972: ((8, 960),),
    973: ((8, 961),),
    974: ((8, 962),),
    975: ((8, 963),),
    976: ((8, 964),),
    977: ((8, 965),),
    978: ((8, 966),),
    979: ((8, 967),),
    980: ((8, 968),),
    984: ((6, 4054), (8, 972)),
    985: ((8, 973),),
    986: ((8, 974),),
    988: ((8, 976),),
    989: ((8, 977),),
    991: ((8, 979),),
    992: ((8, 980),),
    994: (),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
BOUNDARY_RECORD_KEYS = (
    (6, 4054),
    *tuple((8, record_id) for record_id in range(953, 999)),
)
SOURCE_CALL_ROOTS = (
    8,
    1012,
    1132,
    550,
    610,
    538,
    1096,
    1,
    904,
    1066,
    862,
    322,
    604,
    226,
    466,
)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    966: ((1012, 1132), ("029632",)),
    967: ((1012, 1132), ("029632",)),
    968: ((1012, 1132), ("029632",)),
    969: ((550, 610), ("029632",)),
    970: ((550, 610), ("029632",)),
    971: ((550, 610), ("029632",)),
    972: ((), ("025032", "029632")),
    973: ((), ("025032", "029632")),
    974: ((), ("029632", "025032")),
    975: ((), ("029632", "025032")),
    976: ((538,), ("029632", "025032")),
    977: ((538,), ("029632", "025032")),
    978: ((1096,), ("029632", "025032")),
    979: ((538,), ("029632", "025032")),
    980: ((1, 904, 1066), ()),
    984: ((), ("029632", "023C")),
    985: ((), ("029632", "023C")),
    986: ((), ("029632",)),
    988: ((), ("029632", "0232")),
    989: ((), ("029632", "0232")),
    991: ((), ("029632", "0232")),
    992: ((862, 322, 604, 226), ("023C",)),
    994: ((1066, 466), ("023C",)),
}
SPEAKER_STYLE = tuple(
    (
        record_id,
        (
            "intrigue_result_ui"
            if record_id <= 980
            else "domain_construction_and_uprising_ui"
        ),
    )
    for record_id in TARGET_RECORD_IDS
)
TERMINOLOGY_POLICY = (
    ("weaken", "약화"),
    ("agitation", "선동"),
    ("plot", "조략"),
    ("spy", "간자"),
    ("uprising", "잇키"),
    ("domain", "영내"),
    ("seize", "장악"),
    ("begin", "착수"),
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
    "57B3BAF28C7DF0DA3799CF1A2FD0DA674BC07C5AA8BB6DB1A809B8B71F9931D2"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "174C924C1DEEEF2A6B80A9053CB1E788BF11446D237E05A13B64909DD4D4605F"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "AD1E041122A28C1D43B2D6297E111C8DFCD9C7DB137E3F4B1CF1BCD3760A006F"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "8FF20050428646996BE6A1003615B0534BBEACE09C707A088CC746C31DF2C6EE"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "2BB19E493C22DE5BAB7E0691EDBBB34904652088E01747F2CB95A63520F473F2"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "A5827BC10F0CB23F4FAEC9ECAFA21FB3AE02AC870B55944776B0E52519BB5CC2"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "82EF442C21BB317F18051CA503ACEEB5DCDB60F7B9853F5910A2FE18216D2492"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "2D6A941B2DA8E250A440BAF54617D686376FF924005831AFBB7F74934502993C"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "A33DB174ED140CE8624E3B2643F86261BD8B3C17046B98265D6DB7C561AA16C5"
)
EXPECTED_BOUNDARY_SHA256 = (
    "54B742CB2DFDEAF7F437AE383F5484E1BC1A8AE810636D0A92E4F432CFE90275"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "69CB196E2F214B9194A2A8DD8744D004CF907D4F2AA0CEBBF719000AD243D648"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "B21DABF71C05C3E2034880C649864F8CB921D0C1C421888C80E378EA28571860"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "4D089E39487D3BF00B26233F2A590E2F22E02BB012BB4F2EA3A328D6AE38E93F"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "F051506A86FC61E3549CA3886AB5955E9DB1C15C13ED53B60A2E93549847BCC0"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "9A35F92254B75F160087A05DD2DBDE61EFE7A4FA9409E218C5D22ABE88FEB683"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "92C931F9F0C7445BE39C8FDA88C2B8CE2C4FB98318266216D6DE652FE84D047F"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "70ABA19A0B8D9BC2E128672020EE962FDBE1060497CEF9028F7DF0FB58A2D311"
)
EXPECTED_CANDIDATE_SHA256 = (
    "65D8572F38F0557B4D6035EF340F31EB08BEEBC8AE29047803DA3AC2C51CB11E"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "A757919FC4860C20A843F192F192EDE05405E40852C4485BCCB4A3FD44BF4FAE"
)
EXPECTED_CHANGED_LITERAL_COUNT = 28
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 56

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative; nineteen records use raw- or "
    "call-masked exact completed Base donors, while three weakening variants "
    "and the PK-only land-development record use completed Base rows only as "
    "semantic and terminology context; all twenty-eight same-record prefill "
    "companions are validated; Base runtime and VM state are never inherited; "
    "intrigue, uprising, construction and domain terminology, ASCII and "
    "ideographic punctuation, dynamic person and place tokens, calls, gaps, "
    "protected whitespace, mutual three-way segment boundaries, two-run "
    "reproduction, tamper rejection, reverse overlays, outside-scope identity "
    "and Steam read-only state are guarded"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1234_base",
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
        len(rows) != 94
        or len(visible) != 200
        or visible[0] != "8:901:0"
        or visible[-1] != "8:994:2"
    ):
        raise RuntimeError(f"segment {SEGMENT} B076 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "8:966:1"
        or queue_slice[-1] != "8:994:2"
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
        len(prefilled) != 35
        or len(residual) != 31
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
        or len(prefilled) != 35
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


OVERRIDES = BASE.OVERRIDES


def install_base_globals() -> None:
    for name in OVERRIDES:
        setattr(BASE, name, globals()[name])


def propagate_for_tamper() -> None:
    install_base_globals()
    BASE.propagate_for_tamper()


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
        print(json.dumps(DISCOVERED_PINS, sort_keys=True, separators=(",", ":")))
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
        len(rows) != 31
        or len(validated) != 31
        or counts != Counter({"runtime_fragment_pending": 31})
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
    if DISCOVERED_PINS:
        raise RuntimeError(f"segment {SEGMENT} pins remained mutable")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B076_S1234",
                "approved": len(rows),
                "queue_slice_visible_count": 66,
                "exact_reuse_prefill_count": 35,
                "residual_count": len(rows),
                "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "cross_segment_donor_companion_count":
                len(CROSS_SEGMENT_DONOR_COMPANION_COORDINATES),
                "semantic_base_context_record_count":
                len(SEMANTIC_BASE_CONTEXT),
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
                "cross_segment_complete_record_guarded": True,
                "three_way_segment_boundaries_guarded": True,
                "second_run_reproduced": True,
                "tamper_rejection_passed": True,
                "reverse_overlay_exact": True,
                "outside_scope_identity_guarded": True,
                "discovered_pins_empty": True,
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
