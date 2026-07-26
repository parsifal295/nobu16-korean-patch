#!/usr/bin/env python3
"""Build source-redacted PK B069 segment 1213 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch069_segment1212.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B069_S1213.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B069_S1211.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B069_S1212.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1213
QUEUE_BATCH_ID = "pk_msggame-B069"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "7:2835:1",
    "7:2836:1",
    "7:2836:2",
    "7:2837:0",
    "7:2838:0",
    "7:2838:1",
    "7:2838:2",
    "7:2838:3",
    "7:2839:0",
    "7:2839:1",
    "7:2840:0",
    "7:2841:0",
    "7:2841:1",
    "7:2841:2",
    "7:2842:0",
    "7:2842:1",
    "7:2842:2",
    "7:2842:3",
    "7:2843:0",
    "7:2844:0",
    "7:2845:0",
    "7:2846:0",
    "7:2848:0",
    "7:2848:1",
    "7:2848:2",
    "7:2849:0",
    "7:2849:1",
    "7:2850:0",
    "7:2850:1",
    "7:2851:0",
    "7:2851:1",
    "7:2851:2",
    "7:2852:0",
    "7:2853:0",
    "7:2854:0",
    "7:2855:0",
    "7:2858:0",
    "7:2858:1",
)
TRANSLATIONS = {
    "7:2835:1": "을(를)",
    "7:2836:1": "은(는)",
    "7:2836:2": "에 항복하",
    "7:2837:0": "은(는) 항복",
    "7:2838:0": "우리의",
    "7:2838:1": "인",
    "7:2838:2": "에\n",
    "7:2838:3": "이(가) 공격해 왔습니다!",
    "7:2839:0": "·주변",
    "7:2839:1": "개의 성과",
    "7:2840:0": "·주변",
    "7:2841:0": "·",
    "7:2841:1": "의",
    "7:2841:2": "이(가) 동요하여 출진할 수 없게 됨\n",
    "7:2842:0": "·",
    "7:2842:1": "의",
    "7:2842:2": "등",
    "7:2842:3": "개의 성이 동요하여 출진할 수 없게 됨\n",
    "7:2843:0": "·",
    "7:2844:0": "·",
    "7:2845:0": "·",
    "7:2846:0": "·",
    "7:2848:0": "·주변",
    "7:2848:1": "개의 성과",
    "7:2848:2": "개의 군이",
    "7:2849:0": "·주변",
    "7:2849:1": "개의 군이",
    "7:2850:0": "·우리 가문의",
    "7:2850:1": "이(가) 동요하여 출진할 수 없게 됨\n",
    "7:2851:0": "·우리 가문의",
    "7:2851:1": "등",
    "7:2851:2": "개의 성이 동요하여 출진할 수 없게 됨\n",
    "7:2852:0": "·",
    "7:2853:0": "·",
    "7:2854:0": "·",
    "7:2855:0": "·",
    "7:2858:0": "이(가) 수비를 굳힌",
    "7:2858:1": (
        "은(는)\n"
        "패전에도 굴하지 않고 농성 태세를 보이고 있습니다\n"
        "기세를 탄 우리 가문에 귀부할 기미도 없습니다"
    ),
}
TARGET_RECORD_IDS = (
    2835,
    2836,
    2837,
    2838,
    2839,
    2840,
    2841,
    2842,
    2843,
    2844,
    2845,
    2846,
    2848,
    2849,
    2850,
    2851,
    2852,
    2853,
    2854,
    2855,
    2858,
)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    2835: 3,
    2836: 4,
    2837: 2,
    2838: 4,
    2839: 3,
    2840: 2,
    2841: 3,
    2842: 4,
    2843: 2,
    2844: 3,
    2845: 2,
    2846: 3,
    2848: 4,
    2849: 3,
    2850: 2,
    2851: 3,
    2852: 2,
    2853: 3,
    2854: 2,
    2855: 3,
    2858: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "7:2835:0",
    "7:2835:2",
    "7:2836:0",
    "7:2836:3",
    "7:2837:1",
    "7:2839:2",
    "7:2840:1",
    "7:2843:1",
    "7:2844:1",
    "7:2844:2",
    "7:2845:1",
    "7:2846:1",
    "7:2846:2",
    "7:2848:3",
    "7:2849:2",
    "7:2852:1",
    "7:2853:1",
    "7:2853:2",
    "7:2854:1",
    "7:2855:1",
    "7:2855:2",
)
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR = {
    2835: (7, 2769),
    2836: (7, 2770),
    2837: (7, 2771),
    2843: (7, 2774),
    2844: (7, 2775),
    2845: (7, 2776),
    2846: (7, 2777),
    2852: (7, 2781),
    2853: (7, 2782),
    2854: (7, 2783),
    2855: (7, 2784),
}
SEMANTIC_BASE_CONTEXT = {
    2838: ("7:2772:0", "7:2779:0"),
    2839: ("7:2772:0", "7:2772:1", "7:2772:2", "7:2772:3"),
    2840: ("7:2773:0", "7:2773:1", "7:2773:2"),
    2841: ("7:2774:0", "7:2774:1"),
    2842: ("7:2775:0", "7:2775:1", "7:2775:2"),
    2848: ("7:2779:0", "7:2779:1", "7:2779:2", "7:2779:3"),
    2849: ("7:2780:0", "7:2780:1", "7:2780:2"),
    2850: ("7:2779:0", "7:2779:3"),
    2851: ("7:2779:0", "7:2779:1", "7:2779:3"),
    2858: (
        "7:2769:0",
        "7:2769:1",
        "7:2769:2",
        "7:2770:0",
        "7:2770:1",
        "7:2770:2",
        "7:2770:3",
        "7:2771:0",
        "7:2771:1",
    ),
}
EXPECTED_BASE_RAW_MATCHES = {
    2835: (),
    2836: (),
    2837: (),
    2838: (),
    2839: (),
    2840: (),
    2841: (),
    2842: (),
    2843: ((7, 2774),),
    2844: ((7, 2775),),
    2845: ((7, 2776),),
    2846: ((7, 2777),),
    2848: (),
    2849: (),
    2850: (),
    2851: (),
    2852: ((7, 2781),),
    2853: ((7, 2782),),
    2854: ((7, 2783),),
    2855: ((7, 2784),),
    2858: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    2835: ((7, 2769),),
    2836: ((7, 2770),),
    2837: ((7, 2771),),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (7, record_id)
    for record_id in (
        2769,
        2770,
        2771,
        2772,
        2773,
        2774,
        2775,
        2776,
        2777,
        2779,
        2780,
        2781,
        2782,
        2783,
        2784,
        2833,
        2834,
        2835,
        2836,
        2837,
        2838,
        2839,
        2840,
        2841,
        2842,
        2843,
        2844,
        2845,
        2846,
        2847,
        2848,
        2849,
        2850,
        2851,
        2852,
        2853,
        2854,
        2855,
        2856,
        2857,
        2858,
        2859,
    )
)
SOURCE_CALL_ROOTS = (7, 982, 466)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    2835: ((982,), ("026432", "025032")),
    2836: ((466,), ("026432", "025032")),
    2837: ((466,), ("026432",)),
    2838: ((), ("023C", "026432", "025032")),
    2839: ((), ("0232", "0233")),
    2840: ((), ("0232",)),
    2841: ((), ("025032", "026432")),
    2842: ((), ("025032", "026432", "0232")),
    2843: ((), ("025032",)),
    2844: ((), ("025032", "0232")),
    2845: ((), ("028C32",)),
    2846: ((), ("028C32", "0232")),
    2848: ((), ("0232", "0233", "025032")),
    2849: ((), ("0232", "025032")),
    2850: ((), ("026432",)),
    2851: ((), ("026432", "0232")),
    2852: ((), ("025032",)),
    2853: ((), ("025032", "0232")),
    2854: ((), ("028C32",)),
    2855: ((), ("028C32", "0232")),
    2858: ((), ("025032", "026432")),
}
SPEAKER_STYLE = (
    (2835, "battlefield_surrender_monologue"),
    (2836, "battlefield_surrender_monologue"),
    (2837, "battlefield_surrender_monologue"),
    (2838, "urgent_attack_report"),
    (2839, "authority_effect_ui"),
    (2840, "authority_effect_ui"),
    (2841, "authority_effect_ui"),
    (2842, "authority_effect_ui"),
    (2843, "authority_effect_ui"),
    (2844, "authority_effect_ui"),
    (2845, "authority_effect_ui"),
    (2846, "authority_effect_ui"),
    (2848, "authority_effect_ui"),
    (2849, "authority_effect_ui"),
    (2850, "authority_effect_ui"),
    (2851, "authority_effect_ui"),
    (2852, "authority_effect_ui"),
    (2853, "authority_effect_ui"),
    (2854, "authority_effect_ui"),
    (2855, "authority_effect_ui"),
    (2858, "siege_resistance_report"),
)
TERMINOLOGY_POLICY = (
    ("clan", "가문"),
    ("surrender", "항복"),
    ("castle", "성"),
    ("county", "군"),
    ("authority", "위풍"),
    ("march unavailable", "출진할 수 없게 됨"),
    ("relationship improves", "관계가 호전"),
    ("relationship worsens", "관계가 악화"),
    ("kokujin", "국인중"),
    ("siege posture", "농성 태세"),
    ("submit", "귀부"),
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
    "354BFB11CF3F62EFFFDDDA9AF4C66A8876A027D6DF273DBF6496ACEC50DB6C53"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "7221472CABBE21A1249610B245DFCB077FE5423F5F5D3F594A0FA5F023D729C6"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "F8839D1BB477E55191D6A58640414672493DBFCB89CD6A145698D262212D1C94"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "398F8443F32956340BF18F8FE60DD5CBDD8C533FFEF4451CEEFCC078A44A9B9F"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "564CD0BA38D28BFE9BC468F965D4CF7817F5116959B28FC8EB1D64FB83AD149B"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "6F483C51245470E2E06878F9B3D6070CC050F72D99BDC1B26D5B5126B70FD0F2"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "3E0E8F1C7E1539373314E8454BB8BA610E00F34C68E61D7E14EA2ACCA1CAAEDC"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "AF8A1FE16C106E5C16663F0AFA81C3287B33C4F28EE72F120EBA2E455F2FB1F3"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "3F8E918237D9FBA312259F0BA4BCD5D25D6FB1E6BF3CCC809081C9A24C920CE2"
)
EXPECTED_BOUNDARY_SHA256 = (
    "861A695E8C4E5BCC69D7CF10F46068159F68309946FDAC556AF00D3259C42254"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "BFB8224BC001365E192CC38DFBBE9EEECD9997C027FB6EB401BE35745151A6CC"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "83209345446C5CE9750668585F287FDA3058AE60790B193386B6E00EB7C790D5"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "EA51D0AE918A81A611819B4554E5737301C8014417641F20427C758DA18B129F"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "8285202E5884EB5E90FC24B84CFF6E93AF71D2BC438190F8F5805299C5965A82"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "3F82E2ECC5BF0328099F98F602F17AED288D8F4BEC10E7EC92A6037636DCB485"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "B5F279D33E9730F2B793FE6EDCDF916EDC93FBEEE0EFB7E9392C38BFEA5DC818"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "F157788AF26070879BD0D1D7247A51DB5ED1D8B27C1ED2341B8671B552FE6A39"
)
EXPECTED_CANDIDATE_SHA256 = (
    "55E1B1EA847EF4F240585804A36277343F03EFDA6926CB2809323BA7BCF85C77"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "B972CC8998B3227CF2981F4847C8B605F0205CF2B418969AEA0465A5DCF9F974"
)
EXPECTED_CHANGED_LITERAL_COUNT = 19
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 43

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative and complete PK EN SC TC context "
    "was manually reviewed; eleven complete records use completed Base "
    "donors while ten PK-only complete records use adjacent completed Base "
    "terminology and UI context; all twenty-eight slice prefills and "
    "twenty-one same-record companions are validated; Base runtime and VM "
    "state are never inherited; complete records, calls, faction, castle, "
    "county and count tokens, protected outer whitespace, source and current "
    "gaps, queue and segment boundaries, two-run reproduction, tamper "
    "rejection, reverse overlays, outside-scope identity, and Steam read-only "
    "state are guarded"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1213_base",
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
        len(rows) != 125
        or len(visible) != 200
        or visible[0] != "7:2734:0"
        or visible[-1] != "7:2858:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B069 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "7:2833:1"
        or queue_slice[-1] != "7:2858:1"
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
        len(prefilled) != 28
        or len(residual) != 38
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
    target_set = set(TARGET_COORDINATES)
    companion_set = set(PREFILL_COMPANION_COORDINATES)
    hidden_set = set(HIDDEN_CURRENT_COMPANION_COORDINATES)
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
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
            companion_translation = str(companion["translation"])
            assembled.append(companion_translation)
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
                    for coordinate in HIDDEN_CURRENT_COMPANION_COORDINATES
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
        len(replacements) != 66
        or len(prefilled) != 28
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
    BASE.BASE.base_and_assembly_evidence = base_and_assembly_evidence


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
        len(rows) != 38
        or len(validated) != 38
        or counts != Counter({"runtime_fragment_pending": 38})
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
    BASE.BASE.propagate_base_globals()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    raw_exact_count = sum(
        bool(EXPECTED_BASE_RAW_MATCHES[record_id])
        for record_id in TARGET_RECORD_IDS
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B069_S1213",
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
                "exact_reuse_prefill_count": 28,
                "residual_count": len(rows),
                "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "raw_exact_complete_base_donor_record_count":
                raw_exact_count,
                "masked_complete_base_donor_record_count":
                len(EXACT_BASE_DONOR) - raw_exact_count,
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
