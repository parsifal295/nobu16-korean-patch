#!/usr/bin/env python3
"""Build source-redacted PK B076 segment 1232 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch073_segment1225.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B076_S1232.private.v1.jsonl"
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

SEGMENT = 1232
QUEUE_BATCH_ID = "pk_msggame-B076"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 8
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "8:901:0",
    "8:902:0",
    "8:903:0",
    "8:903:1",
    "8:916:0",
    "8:917:0",
    "8:919:0",
    "8:921:0",
    "8:923:0",
    "8:925:0",
    "8:929:1",
    "8:930:1",
    "8:931:0",
    "8:931:1",
    "8:932:1",
    "8:933:0",
    "8:933:1",
    "8:933:2",
    "8:934:0",
    "8:935:0",
    "8:935:1",
    "8:935:2",
    "8:936:0",
    "8:936:1",
    "8:936:2",
    "8:937:0",
    "8:937:1",
    "8:937:2",
    "8:938:0",
    "8:938:1",
)
TRANSLATIONS = {
    "8:901:0": "어느덧 제",
    "8:902:0": "의 군 특성 「",
    "8:903:0": "의 「",
    "8:903:1": "」 지행 기간:",
    "8:916:0": "을(를) 포함해 총",
    "8:917:0": "을(를) 포함해 총",
    "8:919:0": "을(를) 포함해 총",
    "8:921:0": "을(를) 포함해 총",
    "8:923:0": "을(를) 포함해 총",
    "8:925:0": "을(를) 포함해 총",
    "8:929:1": ")을 획득",
    "8:930:1": ")을 획득",
    "8:931:0": "이(가) 「",
    "8:931:1": "」(으)로 승진",
    "8:932:1": "」을(를) 실행할 수 있게 됨",
    "8:933:0": "이(가) 「",
    "8:933:1": "」에서 「",
    "8:933:2": "」을(를) 완료",
    "8:934:0": "이(가) 「",
    "8:935:0": "이(가) 「",
    "8:935:1": "」에서 「",
    "8:935:2": "」을(를) 완료",
    "8:936:0": "이(가) 「",
    "8:936:1": "」의 성하로 「",
    "8:936:2": "」하는 데 성공",
    "8:937:0": "이(가) 「",
    "8:937:1": "」에서 「",
    "8:937:2": "」을(를) 시작",
    "8:938:0": "이(가) 「",
    "8:938:1": "」에서 「",
}
TARGET_RECORD_IDS = (
    901,
    902,
    903,
    916,
    917,
    919,
    921,
    923,
    925,
    929,
    930,
    931,
    932,
    933,
    934,
    935,
    936,
    937,
    938,
)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    901: 2,
    902: 2,
    903: 3,
    916: 2,
    917: 2,
    919: 2,
    921: 2,
    923: 2,
    925: 2,
    929: 2,
    930: 2,
    931: 2,
    932: 2,
    933: 3,
    934: 2,
    935: 3,
    936: 3,
    937: 3,
    938: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "8:901:1",
    "8:902:1",
    "8:903:2",
    "8:916:1",
    "8:917:1",
    "8:919:1",
    "8:921:1",
    "8:923:1",
    "8:925:1",
    "8:929:0",
    "8:930:0",
    "8:932:0",
    "8:934:1",
)
CROSS_SEGMENT_DONOR_COMPANION_COORDINATES = ("8:938:2",)
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR = {
    record_id: (8, record_id - 12)
    for record_id in TARGET_RECORD_IDS
}
SEMANTIC_BASE_CONTEXT: dict[int, tuple[str, ...]] = {}
EXPECTED_BASE_RAW_MATCHES = {
    901: ((8, 889),),
    902: ((8, 890),),
    903: ((8, 891),),
    916: ((8, 904),),
    917: ((8, 905),),
    919: ((8, 907),),
    921: ((8, 909),),
    923: ((8, 911),),
    925: ((8, 913),),
    929: ((8, 917),),
    930: ((8, 918),),
    931: ((8, 919),),
    932: ((8, 920),),
    933: ((8, 921),),
    934: ((8, 922),),
    935: ((8, 923),),
    936: ((8, 924),),
    937: ((8, 925), (8, 930)),
    938: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    933: ((8, 921), (8, 923)),
    935: ((8, 921), (8, 923)),
    937: ((8, 925), (8, 926), (8, 928), (8, 930)),
    938: ((8, 925), (8, 926), (8, 928), (8, 930)),
}
EXPECTED_BASE_MASKED_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    938: ((8, 926),),
}
BOUNDARY_RECORD_KEYS = tuple(
    (8, record_id)
    for record_id in (*range(889, 939), 939, 965, 966)
)
SOURCE_CALL_ROOTS = (8,)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    901: ((), ("0232",)),
    902: ((), ("029632", "02BE32")),
    903: ((), ("024633", "029632", "0232", "0233050505")),
    916: ((), ("024633", "0232")),
    917: ((), ("029632", "0232")),
    919: ((), ("024633", "0232")),
    921: ((), ("024633", "0232")),
    923: ((), ("024633", "0232")),
    925: ((), ("024633", "0232")),
    929: ((), ("0232",)),
    930: ((), ("0232",)),
    931: ((), ("024633", "023C")),
    932: ((), ("024633", "023D")),
    933: ((), ("024633", "029632", "023C")),
    934: ((), ("024633", "029632")),
    935: ((), ("024633", "029633", "023C")),
    936: ((), ("024633", "026432", "023C")),
    937: ((), ("024633", "029632", "023C")),
    938: ((80943,), ("029632", "023C")),
}
SPEAKER_STYLE = tuple(
    (
        record_id,
        (
            "service_and_growth_ui"
            if record_id <= 930
            else "promotion_and_work_ui"
        ),
    )
    for record_id in TARGET_RECORD_IDS
)
TERMINOLOGY_POLICY = (
    ("county trait", "군 특성"),
    ("chigyo tenure", "지행 기간"),
    ("merit", "훈공"),
    ("leadership", "통솔"),
    ("valor", "무용"),
    ("intelligence", "지략"),
    ("governance", "정무"),
    ("promotion", "승진"),
    ("castle town", "성하"),
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
    "42D438721410A5897B3D7DA7937BA7C55B5813BF02738EBD3AD7B077520AD1D7"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "3CDC378857B22685E9620F0A47D9E7262D257E1D8775CC353E8108501F6704A7"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "AC5799B46878CAB349A7D3D5504C96BD6661D2BA2FFCC0FD896399B4D4C09546"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "F5539EF2C018F960C61EACF1ED738991BA48C1D58D7CC0E6588F2277883B3148"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "400315EAAF632D8160246D359341CEFF1086F65B41C9EA7CACFF9ED47E5BFAF7"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "B87F48AA76A0F7698D178D34925ADA66FA5FC78F4E00EE10E77D6204C1A6DD7A"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "2D6A941B2DA8E250A440BAF54617D686376FF924005831AFBB7F74934502993C"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "485EA8837AA4D51366C92B8F4A2A1895B538B6B809A0926D6F58A9297C20323B"
)
EXPECTED_BOUNDARY_SHA256 = (
    "66989E02318EF7DE231A6BFCCE4D32EC0354408427913F2B0FCEFF2AC57276EC"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "4AA57250BB5B44963909313D797AC30E724DDCA2E428A55391EA4923CFB2F841"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "A5373C2FC2CBB00C1553EE4AA1B343D455A009E8562DFE32AA9D6B414815FFC4"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "93F744DCF3A60D0B49B80C95528D4483F47664E6FE022E7994C00FD68E6914FB"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "34F168518E1698E7FE9E5BC5D2252B8EBD655E803B6CE7BBC2DB0A0E5D20F05B"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "43D11EE198E7713F0AF0A788CEA60A6FA256A155AEE756E7308C74D30DC5B317"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "665ECBFCF1D0E1B9B57DA8609B1347EAE73883064485F559E0E063982E3AB223"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "CB3B90C5FDA9E55F348FC0C8A5EF4F1B706C91B02C392C99182FCE7C036BFA98"
)
EXPECTED_CANDIDATE_SHA256 = (
    "A0BC1FF43A6272D78935BF69BAFE0A4A5AC3C9B349171CB07959DCA35FE1BB47"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "14E7497742ACC7CA7B706C9051D04DE5287B6BDA61D8D3A9A34A9B1F592CBEAD"
)
EXPECTED_CHANGED_LITERAL_COUNT = 29
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 52

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative and all nineteen complete records use "
    "raw- or call-masked exact completed Base donors; all thirteen same-record "
    "prefill companions and one cross-segment exact donor companion are "
    "validated; Base runtime and VM state are never inherited; growth, chigyo, "
    "promotion and work terminology, dynamic person, place and action tokens, "
    "calls, gaps, protected whitespace, mutual segment boundaries, two-run "
    "reproduction, tamper rejection, reverse overlays, outside-scope identity, "
    "and Steam read-only state are guarded"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1232_base",
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
        len(queue_slice) != 67
        or queue_slice[0] != "8:901:0"
        or queue_slice[-1] != "8:938:1"
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
        len(prefilled) != 37
        or len(residual) != 30
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
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    neighbor_rows: dict[str, dict[str, Any]] = {}
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            for row in read_jsonl(path):
                neighbor_rows[str(row["coordinate"])] = row
    target_set = set(TARGET_COORDINATES)
    companion_set = set(PREFILL_COMPANION_COORDINATES)
    cross_set = set(CROSS_SEGMENT_DONOR_COMPANION_COORDINATES)
    hidden_set = set(HIDDEN_CURRENT_COMPANION_COORDINATES)
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    seen_cross: set[str] = set()
    seen_hidden: set[str] = set()
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        key = (BLOCK_ID, record_id)
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
            len(source_literals) != EXPECTED_ARITY[record_id]
            or raw_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
            or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[record_id]
            or masked_matches != EXPECTED_BASE_MASKED_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base donor drifted: {record_id}"
            )
        exact = record_id in EXACT_BASE_DONOR
        donor_rows: list[dict[str, Any]] = []
        donor_coordinates: tuple[str, ...]
        base_literals: tuple[str, ...] = ()
        if exact:
            donor_key = EXACT_BASE_DONOR[record_id]
            base_literals = literal_texts(base_source, donor_key)
            donor_coordinates = tuple(
                f"{donor_key[0]}:{donor_key[1]}:{literal_id}"
                for literal_id in range(EXPECTED_ARITY[record_id])
            )
        else:
            donor_coordinates = SEMANTIC_BASE_CONTEXT[record_id]
            for donor_coordinate in donor_coordinates:
                donor = base_rows.get(donor_coordinate)
                if (
                    donor is None
                    or donor.get("semantic_review") != "approved"
                    or donor.get("runtime_review")
                    not in {"verified", "not_required"}
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} semantic context drifted: "
                        f"{donor_coordinate}"
                    )
                donor_rows.append(donor)
        assembled: list[str] = []
        donor_assembled: list[str] = []
        owners: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"{BLOCK_ID}:{record_id}:{literal_id}"
            if exact and coordinate in hidden_set:
                if (
                    source_literals[literal_id] != "\n"
                    or current_literals[literal_id] != "\n"
                    or base_literals[literal_id] != "\n"
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} hidden newline drifted: "
                        f"{coordinate}"
                    )
                seen_hidden.add(coordinate)
                assembled.append("\n")
                donor_assembled.append("\n")
                owners.append("hidden_newline_exact")
                continue
            if exact:
                donor_coordinate = donor_coordinates[literal_id]
                donor = base_rows.get(donor_coordinate)
                if (
                    donor is None
                    or donor.get("semantic_review") != "approved"
                    or donor.get("runtime_review")
                    not in {"verified", "not_required"}
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} exact donor drifted: "
                        f"{donor_coordinate}"
                    )
                donor_rows.append(donor)
                donor_translation = str(donor["translation"])
                donor_assembled.append(donor_translation)
                if coordinate in target_set:
                    if TRANSLATIONS[coordinate] != donor_translation:
                        raise RuntimeError(
                            f"segment {SEGMENT} target donor drifted: "
                            f"{coordinate}"
                        )
                    seen_target.add(coordinate)
                    assembled.append(TRANSLATIONS[coordinate])
                    owners.append("segment_exact")
                    continue
                if coordinate in cross_set:
                    neighbor = neighbor_rows.get(coordinate)
                    if neighbor is not None and (
                        neighbor.get("semantic_review") != "approved"
                        or neighbor.get("runtime_review") != "pending"
                        or str(neighbor.get("translation"))
                        != donor_translation
                    ):
                        raise RuntimeError(
                            f"segment {SEGMENT} neighbor drifted: {coordinate}"
                        )
                    seen_cross.add(coordinate)
                    assembled.append(donor_translation)
                    owners.append("neighbor_segment_exact_donor")
                    continue
                companion = prefill_rows.get(coordinate)
                if (
                    coordinate not in companion_set
                    or companion is None
                    or companion.get("semantic_review") != "approved"
                    or companion.get("runtime_review") != "pending"
                    or companion["base_exact_reuse_prefill"][
                        "runtime_promotion_authorized"
                    ]
                    is not False
                    or str(companion["translation"]) != donor_translation
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} companion drifted: {coordinate}"
                    )
                seen_companion.add(coordinate)
                assembled.append(str(companion["translation"]))
                owners.append("base_exact_prefill_runtime_pending")
                continue
            if coordinate in target_set:
                seen_target.add(coordinate)
                assembled.append(TRANSLATIONS[coordinate])
                donor_assembled.append("manual_multilingual_semantic_selection")
                owners.append("segment_manual")
                continue
            companion = prefill_rows.get(coordinate)
            if (
                coordinate not in companion_set
                or companion is None
                or companion.get("semantic_review") != "approved"
                or companion.get("runtime_review") != "pending"
                or companion["base_exact_reuse_prefill"][
                    "runtime_promotion_authorized"
                ]
                is not False
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} incomplete manual record: {coordinate}"
                )
            seen_companion.add(coordinate)
            assembled.append(str(companion["translation"]))
            donor_assembled.append("base_exact_prefill_semantic_companion")
            owners.append("base_exact_prefill_runtime_pending")
        if exact and tuple(assembled) != tuple(donor_assembled):
            raise RuntimeError(
                f"segment {SEGMENT} exact assembly drifted: {record_id}"
            )
        base_evidence.append(
            (
                record_id,
                sha256_bytes(source.data),
                source_literals,
                current_literals,
                tuple(value.hex().upper() for value in gap_bytes(source)),
                raw_matches,
                literal_matches,
                masked_matches,
                donor_coordinates,
                tuple(
                    (
                        str(row["coordinate"]),
                        str(row["translation"]),
                        str(row["semantic_review"]),
                        str(row["runtime_review"]),
                    )
                    for row in donor_rows
                ),
                tuple(
                    coordinate
                    for coordinate in CROSS_SEGMENT_DONOR_COMPANION_COORDINATES
                    if coordinate.startswith(f"{BLOCK_ID}:{record_id}:")
                ),
                "complete_exact" if exact else "semantic_context_only",
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(assembled),
                tuple(donor_assembled),
                CORE.runtime_controls(source),
                CORE.runtime_controls(records_by_label["current"][key]),
                (
                    "complete_translation_equals_completed_base_donor"
                    if exact
                    else "manual_pk_semantic_adaptation_with_prefill_companions"
                ),
                "base_runtime_state_not_inherited",
            )
        )
    if (
        seen_target != target_set
        or seen_companion != companion_set
        or seen_cross != cross_set
        or seen_hidden != hidden_set
    ):
        raise RuntimeError(f"segment {SEGMENT} complete assembly scope drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


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
        or len(prefilled) != 37
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
    "CROSS_SEGMENT_DONOR_COMPANION_COORDINATES",
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
    module = BASE
    while hasattr(module, "BASE"):
        if hasattr(module, "base_and_assembly_evidence"):
            module.base_and_assembly_evidence = base_and_assembly_evidence
        module = module.BASE


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
        len(rows) != 30
        or len(validated) != 30
        or counts != Counter({"runtime_fragment_pending": 30})
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
                "segment": "pk_msggame_B076_S1232",
                "approved": len(rows),
                "queue_slice_visible_count": 67,
                "exact_reuse_prefill_count": 37,
                "residual_count": len(rows),
                "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "cross_segment_donor_companion_count":
                len(CROSS_SEGMENT_DONOR_COMPANION_COORDINATES),
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
                "second_run_reproduced": True,
                "tamper_rejection_passed": True,
                "reverse_overlay_exact": True,
                "outside_scope_identity_guarded": True,
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
