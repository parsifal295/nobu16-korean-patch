#!/usr/bin/env python3
"""Build source-redacted PK B071 segment 1217 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch069_segment1211.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B071_S1217.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B071_S1218.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B071_S1219.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1217
QUEUE_BATCH_ID = "pk_msggame-B071"
QUEUE_START = 0
QUEUE_STOP = 67
QUEUE_ROW_COUNT = 83
QUEUE_VISIBLE_COUNT = 199
SLICE_VISIBLE_COUNT = 67
SLICE_PREFILL_COUNT = 52
BLOCK_ID = 8
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "8:238:0",
    "8:239:0",
    "8:241:0",
    "8:245:0",
    "8:245:1",
    "8:245:2",
    "8:246:0",
    "8:249:0",
    "8:252:1",
    "8:252:2",
    "8:254:1",
    "8:256:1",
    "8:259:0",
    "8:260:1",
    "8:263:0",
)
TRANSLATIONS = {
    "8:238:0": "자, 「",
    "8:239:0": "은(는)\n",
    "8:241:0": "자, 「",
    "8:245:0": "바로 「",
    "8:245:1": "」이(가)\n",
    "8:245:2": "을(를) 제압한다!",
    "8:246:0": "자, 「",
    "8:249:0": "이제, 「",
    "8:252:1": "　패배:",
    "8:252:2": ")",
    "8:254:1": "」이(가)\n",
    "8:256:1": "」이(가)\n",
    "8:259:0": ", 기뻐해",
    "8:260:1": "!\n이 또한",
    "8:263:0": ", 봐",
}
TARGET_RECORD_IDS = (
    238, 239, 241, 245, 246, 249, 252, 254, 256, 259, 260, 263,
)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    238: 2,
    239: 2,
    241: 2,
    245: 3,
    246: 2,
    249: 2,
    252: 3,
    254: 3,
    256: 3,
    259: 3,
    260: 3,
    263: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "8:238:1",
    "8:239:1",
    "8:241:1",
    "8:246:1",
    "8:249:1",
    "8:252:0",
    "8:254:0",
    "8:254:2",
    "8:256:0",
    "8:256:2",
    "8:259:1",
    "8:259:2",
    "8:260:0",
    "8:260:2",
    "8:263:1",
)
EXACT_BASE_DONOR = {
    238: (8, 232),
    239: (8, 233),
    241: (8, 235),
    245: (8, 239),
    246: (8, 240),
    249: (8, 243),
    252: (8, 246),
    254: (8, 248),
    256: (8, 250),
    259: (8, 253),
    260: (8, 254),
    263: (8, 257),
}
PREFILL_COMPANION_DONOR = {
    coordinate: (
        f"8:{EXACT_BASE_DONOR[int(coordinate.split(':')[1])][1]}:"
        f"{coordinate.split(':')[2]}"
    )
    for coordinate in PREFILL_COMPANION_COORDINATES
}
SEMANTIC_BASE_CONTEXT: dict[int, tuple[str, ...]] = {}
EXPECTED_BASE_RAW_MATCHES = {
    238: ((8, 232),),
    239: ((8, 233),),
    241: ((8, 235),),
    245: ((8, 239),),
    246: ((8, 240),),
    249: ((8, 243),),
    252: ((8, 246),),
    254: ((8, 248),),
    256: ((8, 250),),
    259: (),
    260: (),
    263: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    record_id: (EXACT_BASE_DONOR[record_id],)
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (8, record_id)
    for record_id in (
        231, 232, 233, 234, 235, 238, 239, 240, 241, 242,
        243, 245, 246, 248, 249, 250, 252, 253, 254, 256,
        257, 258, 259, 260, 263, 264, 267, 268, 269,
    )
)
SOURCE_CALL_ROOTS = (1, 8, 322, 520, 1078)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    238: ((), ("029632",)),
    239: ((1,), ("029632",)),
    241: ((), ("029632",)),
    245: ((), ("024635", "029632")),
    246: ((), ("029632",)),
    249: ((), ("025032",)),
    252: ((), ("023C", "025032", "025132")),
    254: ((), ("025032", "028C32", "025132")),
    256: ((), ("028C32", "025032")),
    259: ((8, 322, 520, 1078), ()),
    260: ((520, 8, 598), ()),
    263: ((8, 322, 520), ()),
}
SPEAKER_STYLE = (
    (238, "castle_capture_rally"),
    (239, "castle_capture_personal_claim"),
    (241, "castle_capture_collective_claim"),
    (245, "castle_capture_personal_domination"),
    (246, "castle_capture_deliberative_rally"),
    (249, "alliance_break_refusal"),
    (252, "battle_authority_result_notice"),
    (254, "vassal_defection_notice"),
    (256, "independent_force_vassalage_notice"),
    (259, "harvest_celebration"),
    (260, "harvest_lordly_praise"),
    (263, "harvest_field_invitation"),
)
TERMINOLOGY_POLICY = (
    ("castle capture", "공략·차지"),
    ("subjugate", "제압"),
    ("side or ally", "편"),
    ("authority", "위풍"),
    ("victory", "승리"),
    ("defeat", "패배"),
    ("vassalage", "종속"),
    ("defection", "편으로 돌아서다"),
    ("bumper harvest", "풍작"),
    ("rice storehouse", "곳간"),
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
    "B58A1BB469BD034ABEE5A1641FC3FB0626BEDCAAC4861833AA068913459D5B80"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "543F0A0AE621EEDE0E6B8A5E0C18FEB67087F15BD389ED3D12527C0AACD1F11A"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "33FE77A0505FDCC8086D13494ED133203E4B63CE11B483AF1B0BAE790D0C051B"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "EC1B123A2ED33CF2FE5876A9DE1F221D1F86D03E7FF1C51F415565EF990F35C7"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "2EC5542998E10614FEB65F185C51E97C5C8B7A8FB171392FEB2B60D31EF0E976"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "7F197408D6398C8E9111AF909C0C556B9BA2D0BC0A61C58749855E60C4456DA9"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "1E3D9FE04506EC5FD75F2F239F5A4374A5C0AB27B82FE302C27310400C9DA75B"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "1F96C5279DE1489EA39D9FF690C822D45BB5468E5DDF70004CDD1FC9A384BC9A"
)
EXPECTED_BOUNDARY_SHA256 = (
    "9FC9D2C0E2C4973A7E20B31C972A1E3C36526D04A5B7ED6408A97943203FFCB6"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "34336AFAC1F9DD02F7822CC984C6104FB733C5AC285F1E6CFCB0C9CA0515DB3C"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "991D317A3D7B229D641992C519E42411F237495D5C1C5ADC86DC848B2A50765E"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "BCCDCC49099ACECBCFA51EE0A954C096CB176EEC1A001EACBA0570E87B27E514"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "CA7BA121520583051F9A74B075AD27CDD1E8F8DFDCED8AEBA1ADBD003473ED14"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "B32BED8F7EBF3F3A4EDC18EACA58D33EC13F7F32317AFEE67B95277C3EF28882"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "EB5B97E4487FBC5863E487CE669679537518CCC6AE7F5828B721465EC9D206E5"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "3058F73AA80E546D4DE8AF79EB7DCE1926F5E4BCB7BA27CB01E0A6E43AE014C5"
)
EXPECTED_CANDIDATE_SHA256 = (
    "9212933562B5F3C8AA187CB34540B9C5471500248B952E6E35AAE6C89DE29710"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "C4E0F4B86454E731BF83375B4DDEA97D39B0B121DC1308CE54B7750BEF87A031"
)
EXPECTED_CHANGED_LITERAL_COUNT = 12
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 56

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative and complete PK EN SC TC context "
    "was reviewed; twelve complete records have manually reviewed completed "
    "Base literal and call-masked donors, with runtime and VM state never "
    "inherited; fifteen residual translations and fifteen same-record Base "
    "prefill companions reproduce the complete Korean donor assemblies; all "
    "fifty-two prefills in the first slice are preserved; castle-capture, "
    "alliance, authority, vassalage and harvest terminology, speaker register, "
    "calls, names, forces, punctuation, newlines, protected whitespace, gaps, "
    "two-run reproduction, tamper rejection, reverse overlays, outside-scope "
    "identity and Steam read-only state are guarded; residuals stay runtime "
    "pending"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_b071_s1217_base",
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
        or visible[0] != "8:238:0"
        or visible[-1] != "8:320:2"
    ):
        raise RuntimeError(f"segment {SEGMENT} B071 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != SLICE_VISIBLE_COUNT
        or queue_slice[0] != "8:238:0"
        or queue_slice[-1] != "8:268:1"
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


def build_rows() -> tuple[Any, ...]:
    install_base_globals()
    return BASE.build_rows()


def propagate_base_globals() -> None:
    install_base_globals()
    BASE.patch_parent_globals()


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
        "segment": "pk_msggame_B071_S1217",
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
        "raw_exact_complete_base_donor_record_count":
        sum(bool(EXPECTED_BASE_RAW_MATCHES[x]) for x in TARGET_RECORD_IDS),
        "masked_complete_base_donor_record_count":
        len(TARGET_RECORD_IDS),
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
