#!/usr/bin/env python3
"""Build source-redacted PK B064 segment 1199 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch061_segment1192.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B064_S1199.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B064_S1200.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B064_S1201.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1199
QUEUE_BATCH_ID = "pk_msggame-B064"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "7:1990:0",
    "7:1991:0",
    "7:1993:0",
    "7:1995:1",
    "7:1998:1",
    "7:2001:1",
    "7:2006:1",
    "7:2009:1",
    "7:2012:1",
    "7:2014:1",
    "7:2015:1",
    "7:2016:0",
    "7:2016:1",
    "7:2017:0",
    "7:2017:1",
    "7:2018:0",
    "7:2018:2",
    "7:2019:0",
    "7:2019:1",
    "7:2019:2",
    "7:2020:0",
    "7:2020:2",
    "7:2021:0",
    "7:2021:1",
    "7:2022:0",
    "7:2023:0",
    "7:2023:1",
    "7:2024:0",
    "7:2026:1",
)
TRANSLATIONS = {
    "7:1990:0": "그럼—",
    "7:1991:0": "이제—",
    "7:1993:0": "자—",
    "7:1995:1": "(으)로 향한다",
    "7:1998:1": "(으)로 간다",
    "7:2001:1": "(으)로 향한다!",
    "7:2006:1": "(으)로 향한다",
    "7:2009:1": "(으)로 향하자꾸나",
    "7:2012:1": "에 가야 합니다",
    "7:2014:1": "을(를) 격파하라",
    "7:2015:1": "을(를) 치겠다",
    "7:2016:0": "을(를) 저지하고\n",
    "7:2016:1": "을(를) 지킨다",
    "7:2017:0": "은(는) 요지다\n",
    "7:2017:1": "을(를) 쳐라",
    "7:2018:0": "목표—",
    "7:2018:2": "을(를) 지켜라",
    "7:2019:0": "감히—",
    "7:2019:1": "을(를) 공격한 것이\n",
    "7:2019:2": "의 최후다",
    "7:2020:0": "덤벼라—",
    "7:2020:2": "은(는) 지킨다!",
    "7:2021:0": "은(는) 지킨다\n",
    "7:2021:1": "을(를) 쳐라",
    "7:2022:0": "에게는\n",
    "7:2023:0": ", 각오해라!\n",
    "7:2023:1": "은(는) 지킨다!",
    "7:2024:0": "에게\n",
    "7:2026:1": "을(를) 저지한다",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    1990,
    1991,
    1993,
    1995,
    1998,
    2001,
    2006,
    2009,
    2012,
    2014,
    2015,
    2016,
    2017,
    2018,
    2019,
    2020,
    2021,
    2022,
    2023,
    2024,
    2026,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
THREE_LITERAL_RECORD_IDS = (2018, 2019, 2020)
EXPECTED_ARITY = {
    record_id: 3 if record_id in THREE_LITERAL_RECORD_IDS else 2
    for record_id in TARGET_RECORD_IDS
}
PREFILL_COMPANION_COORDINATES = (
    "7:1990:1",
    "7:1991:1",
    "7:1993:1",
    "7:1995:0",
    "7:1998:0",
    "7:2001:0",
    "7:2006:0",
    "7:2009:0",
    "7:2012:0",
    "7:2014:0",
    "7:2015:0",
    "7:2022:1",
    "7:2024:1",
    "7:2026:0",
)
HIDDEN_CURRENT_COMPANION_COORDINATES = ("7:2018:1", "7:2020:1")
FUTURE_COMPANION_COORDINATES: tuple[str, ...] = ()
PRIMARY_BASE_MATCH = {
    1990: (7, 1945),
    1991: (7, 1951),
    1993: (7, 1953),
    1995: (7, 1955),
    1998: (7, 1958),
    2001: (7, 1961),
    2006: (7, 1966),
    2009: (7, 1969),
    2012: (7, 1972),
    2014: (7, 1974),
    2015: (7, 1975),
    2016: (7, 1976),
    2017: (7, 1977),
    2018: (7, 1978),
    2019: (7, 1979),
    2020: (7, 1980),
    2021: (7, 1981),
    2022: (7, 1982),
    2023: (7, 1983),
    2024: (7, 1984),
    2026: (7, 1986),
}
EXPECTED_BASE_MATCHES = {
    record_id: (
        ((7, 1945), (7, 1950))
        if record_id == 1990
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
        if f"7:{record_id}:{literal_id}"
        not in HIDDEN_CURRENT_COMPANION_COORDINATES
    )
    for record_id, base_coordinate in PRIMARY_BASE_MATCH.items()
}
BOUNDARY_RECORD_KEYS = (
    *tuple((7, record_id) for record_id in TARGET_RECORD_IDS),
    (7, 1992),
    (7, 1994),
    (7, 1996),
    (7, 1997),
    (7, 1999),
    (7, 2000),
    (7, 2002),
    (7, 2005),
    (7, 2007),
    (7, 2008),
    (7, 2010),
    (7, 2011),
    (7, 2013),
    (7, 2025),
    (7, 2027),
)
SOURCE_CALL_ROOTS: tuple[int, ...] = ()
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    1990: ((), ("026432",)),
    1991: ((), ("026432",)),
    1993: ((), ("026432",)),
    1995: ((), ("029632",)),
    1998: ((), ("029632",)),
    2001: ((), ("029632",)),
    2006: ((), ("029632",)),
    2009: ((), ("029632",)),
    2012: ((), ("029632",)),
    2014: ((), ("026432", "026E32")),
    2015: ((), ("026432", "026E32")),
    2016: ((), ("026E32", "026432")),
    2017: ((), ("026432", "026E32")),
    2018: ((), ("026E32", "026432")),
    2019: ((), ("026432", "026E32")),
    2020: ((), ("026E32", "026432")),
    2021: ((), ("026432", "026E32")),
    2022: ((), ("026E32", "026432")),
    2023: ((), ("026E32", "026432")),
    2024: ((), ("026E32", "026432")),
    2026: ((), ("026432", "026E32")),
}
SPEAKER_STYLE = (
    (1990, "formal_return_to_defense"),
    (1991, "relieved_defense_strengthening"),
    (1993, "plain_guard_assignment"),
    (1995, "rough_pincer_prevention"),
    (1998, "plain_pincer_assessment"),
    (2001, "imperious_pincer_prevention"),
    (2006, "plain_pincer_prevention"),
    (2009, "elder_pincer_prevention"),
    (2012, "formal_pincer_warning"),
    (2014, "imperious_protect_and_destroy"),
    (2015, "rough_protect_and_attack"),
    (2016, "imperious_block_and_protect"),
    (2017, "imperious_strategic_point"),
    (2018, "imperious_target_and_protect"),
    (2019, "imperious_enemy_doom"),
    (2020, "defiant_protection"),
    (2021, "imperious_protect_and_attack"),
    (2022, "rough_refusal_to_yield"),
    (2023, "defiant_protection"),
    (2024, "imperious_refusal_to_yield"),
    (2026, "plain_block_and_protect"),
)
TERMINOLOGY_POLICY = (
    ("pincer attack", "협격"),
    ("strategic point", "요지"),
    ("defend", "지키다"),
    ("defense", "방어"),
    ("block", "저지하다"),
    ("defeat", "격파하다"),
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
    "EF6669436AF3F074CEA34129DC31D3E67E59D102A7127DB1D64B297B36C5E217"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "4EA2A7611761BC03E08990930BDEA79679542D4D78186A76C66AF030E122FE55"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "A8BE16FB8449BE7B129CE2952DD932E6A7ABE0828CC05FE1AAA39A4A97012FD4"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "45328790D2E7708C9A31583A16B374B97BEF6A3E0D8E08C41DF80153278E84B2"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "1F92C95D8B12EC1F352254D7FAAF5776013CC9A2C33761E1D017EB14B7693D41"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "7DF7530269A919E84F637159E6582246EE4AF6BA01CFF41CC94078839ACCEED0"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "9444A43AA40EBA057B1FB2EA73717DBC9B3DF28ADA3E124BB0F708FD280E1C04"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "551201C95B3F8C970CE46BED4CBF4D3579766A7BD524FCE512A0406F4B18F7B3"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "9CE2F7A3512E00F7B8573C39169D92DEBDAA744337BC88BEF1D5984983A9D5CC"
)
EXPECTED_BOUNDARY_SHA256 = (
    "01881D7F94D90358EEBAE10E528C9C0CE9D0E509ACF756F46103AC2842DA6AA2"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "DED36C077A0D6783FE2689390E63C51351D9FF3D85998E4F4DBA0FE3370B92CD"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "2A20A14150E4E94B499304311C2348A4F93E8732D2FDFEDFC957DD1497ACD0F7"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "057A2CCB285D79CF1CE53DF2D18768F14AB3FE90DE5971A62DE01A8E1371082A"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "B174A9D70D69F779AFEC1118D51132A3CDE129824B0F4C10840A0502327C331D"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "BAF05E09ECD059E1F5F05C7CCFEF4BFF1B545455383860D60E70638C4AED6D4C"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "EF40ED18C4001738FFCD10AD385FFAB73F119D0EDF0AC889DE4B5A94658105B8"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "3E9D0CCE3AC67692ABCCF35767E9C5E87ECB69F182E483C7259A0697D1F3C89B"
)
EXPECTED_CANDIDATE_SHA256 = (
    "083A0E30404C1CF2440C355CBE1BC95199B97A2898E0CF8B351039D7F38F1983"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "443598D5902F6AA69EDAD2D58D03B46D5469E3C6FEEB347680EBD7D200F67F3B"
)
EXPECTED_CHANGED_LITERAL_COUNT = 25

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source authoritative; complete PC EN SC TC context "
    "reviewed where present; all twenty-one complete PK source records "
    "have completed Base byte-exact source donors whose final Korean is "
    "selected only after manual semantic, terminology and register review; "
    "fourteen approved Base-prefilled companions and two source-empty "
    "newline companions are reviewed as complete record assemblies; all "
    "thirty-eight Base prefills in the queue slice are validated; castle "
    "and destination tokens, particles, newlines, protected outer "
    "whitespace, full records, boundaries, two-run reproduction, tamper "
    "rejection, reverse overlays, outside-scope identity and Steam read-"
    "only state are guarded; Base runtime and VM state are not inherited "
    "and every residual remains runtime pending"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1199_base",
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
        len(rows) != 128
        or len(visible) != 200
        or visible[0] != "7:1990:0"
        or visible[-1] != "7:2117:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B064 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "7:1990:0"
        or queue_slice[-1] != "7:2027:0"
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
        len(prefilled) != 38
        or len(residual) != 29
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
        or len(prefilled) != 38
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
        "HIDDEN_CURRENT_COMPANION_COORDINATES":
        HIDDEN_CURRENT_COMPANION_COORDINATES,
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
        record_id = coordinate_key(str(row["coordinate"]))[1]
        row["manual_complete_base_donor_translation_selected"] = True
        row["manual_semantic_base_references_reviewed"] = True
        row["manual_multilingual_translation_selected"] = False
        row["hidden_source_newline_companion_reviewed"] = (
            record_id in {2018, 2020}
        )
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
        len(rows) != 29
        or len(validated) != 29
        or counts != Counter({"runtime_fragment_pending": 29})
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
                "segment": "pk_msggame_B064_S1199",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
                "target_coordinate_first": TARGET_COORDINATES[0],
                "target_coordinate_last": TARGET_COORDINATES[-1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 67,
                "exact_reuse_prefill_count": 38,
                "residual_count": len(rows),
                "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
                "same_slice_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "hidden_current_companion_count":
                len(HIDDEN_CURRENT_COMPANION_COORDINATES),
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
