#!/usr/bin/env python3
"""Build source-redacted PK B045 segment 1147 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch044_segment1144.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B045_S1147.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B045_S1146.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B045_S1148.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1147
QUEUE_BATCH_ID = "pk_msggame-B045"
QUEUE_START = 67
QUEUE_STOP = 134
QUEUE_FIRST_RECORD = 4370
QUEUE_LAST_RECORD = 4467
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751

TARGET_COORDINATES = (
    "6:4414:1",
    "6:4416:0",
    "6:4419:0",
    "6:4420:0",
    "6:4420:5",
    "6:4423:3",
    "6:4425:0",
    "6:4425:3",
    "6:4425:5",
    "6:4426:0",
    "6:4426:1",
    "6:4426:2",
    "6:4427:0",
    "6:4432:0",
    "6:4434:0",
    "6:4435:1",
)
TRANSLATIONS = {
    "6:4414:1": "을(를) 포함한 총",
    "6:4416:0": "에는",
    "6:4419:0": "다행히 「",
    "6:4420:0": "다행히 「",
    "6:4420:5": "까?",
    "6:4423:3": "까?",
    "6:4425:0": "과분한",
    "6:4425:3": "와(과) 「",
    "6:4425:5": "와(과) 「",
    "6:4426:0": "의 성주 「",
    "6:4426:1": "」님과\n",
    "6:4426:2": "의 성주 「",
    "6:4427:0": "알겠",
    "6:4432:0": "와(과) 「",
    "6:4434:0": "이 「",
    "6:4435:1": "지만\n",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()

TARGET_RECORD_IDS = (
    4414,
    4416,
    4419,
    4420,
    4423,
    4425,
    4426,
    4427,
    4432,
    4434,
    4435,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    4414: 3,
    4416: 3,
    4419: 4,
    4420: 6,
    4423: 4,
    4425: 7,
    4426: 5,
    4427: 2,
    4432: 2,
    4434: 3,
    4435: 3,
}
BASE_RECORD_MAPPING = {
    record_id: record_id - 59 for record_id in TARGET_RECORD_IDS
}
RAW_EXACT_BASE_RECORD_IDS = (4414, 4416, 4419, 4432, 4434)
OPERAND_MASKED_BASE_RECORD_IDS = (
    4420,
    4423,
    4425,
    4426,
    4427,
    4435,
)
ALL_COMPANION_COORDINATES = tuple(
    f"6:{record_id}:{literal_id}"
    for record_id in TARGET_RECORD_IDS
    for literal_id in range(EXPECTED_ARITY[record_id])
    if f"6:{record_id}:{literal_id}" not in TARGET_COORDINATES
)
PREFILL_COMPANION_COORDINATES = tuple(
    coordinate
    for coordinate in ALL_COMPANION_COORDINATES
    if coordinate != "6:4425:2"
)
HIDDEN_COMPANION_COORDINATES = ("6:4425:2",)
BASE_TARGET_DONOR_COORDINATES = {
    coordinate:
    (
        f"6:{int(coordinate.split(':')[1]) - 59}:"
        f"{coordinate.split(':')[2]}"
    )
    for coordinate in TARGET_COORDINATES
}
CONTEXT_RECORD_IDS = tuple(
    range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1)
)
BOUNDARY_RECORD_IDS = tuple(
    sorted(
        {
            QUEUE_FIRST_RECORD - 1,
            QUEUE_FIRST_RECORD,
            QUEUE_LAST_RECORD,
            QUEUE_LAST_RECORD + 1,
            4413,
            4414,
            4415,
            4436,
            4437,
            4438,
        }
        | {
            adjacent
            for record_id in TARGET_RECORD_IDS
            for adjacent in (record_id - 1, record_id, record_id + 1)
        }
    )
)

EXPECTED_CONTROLS_BY_RECORD = {
    4414: ((), ("025032", "0232")),
    4416: ((1, 1, 178), ("029632",)),
    4419: ((), ("024833", "02483F", "0233")),
    4420: ((1090,), ("024833", "02483F", "0234", "024833")),
    4423: ((1090,), ("0232", "0233")),
    4425: ((1168, 748, 1, 442), ("024833", "02463F", "02483F")),
    4426: ((1, 1096), ("02483F", "024833", "02493F", "024933")),
    4427: ((538, 958), ()),
    4432: ((), ("025032", "025132")),
    4434: ((160, 322), ("02463F",)),
    4435: ((568, 1), ()),
}
EXPECTED_BASE_CONTROLS_BY_RECORD = {
    4414: ((), ("025032", "0232")),
    4416: ((1, 1, 178), ("029632",)),
    4419: ((), ("024833", "02483F", "0233")),
    4420: ((1078,), ("024833", "02483F", "0234", "024833")),
    4423: ((1078,), ("0232", "0233")),
    4425: ((1156, 736, 1, 436), ("024833", "02463F", "02483F")),
    4426: ((1, 1084), ("02483F", "024833", "02493F", "024933")),
    4427: ((532, 946), ()),
    4432: ((), ("025032", "025132")),
    4434: ((160, 322), ("02463F",)),
    4435: ((556, 1), ()),
}
EXPECTED_CALL_ROOTS = (
    1,
    160,
    178,
    322,
    442,
    538,
    568,
    748,
    958,
    1090,
    1096,
    1168,
)
EXPECTED_TERMINAL_TUPLES = {
    1: (("나",), ("소승",), ("소인",), ("이 몸",), ("저",)),
    160: (("없다",), ("없사옵니다",), ("없습니다",)),
    178: (("있다",), ("있사옵니다",), ("있습니다",)),
    322: (("다오",), ("주소서",), ("주시오",)),
    442: (("하",), ("하옵니다",), ("합니다",)),
    538: (("다",), ("했습니다",)),
    568: (("다",), ("이오",), ("입니다",)),
    748: (("않는다",), ("않습니다",)),
    958: (
        ("명령을 내려 주소서",),
        ("명령해 다오",),
        ("명령해 주십시오",),
        ("명하여 주시게",),
        ("명하여 주십시오",),
    ),
    1090: (("다",), ("합니다",)),
    1096: (("다",), ("하옵니다",), ("합니다",)),
    1168: (("",), ("오",)),
}
CALL_BEARING_RECORD_IDS = (
    4416,
    4420,
    4423,
    4425,
    4426,
    4427,
    4434,
    4435,
)
RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS = (
    4416,
    4420,
    4423,
    4425,
    4426,
    4427,
    4435,
)

SPEAKER_STYLE = {
    4414: "system_alliance_diplomatic_attitude_deterioration",
    4416: "formal_officer_domain_suitability_objection",
    4419: "formal_domain_count_report",
    4420: "formal_domain_grant_confirmation",
    4423: "formal_new_domain_grant_confirmation",
    4425: "formal_domain_gratitude_and_development_pledge",
    4426: "formal_castle_lords_collective_thanks",
    4427: "formal_domain_order_acknowledgement",
    4432: "system_relationship_changed_to_alliance",
    4434: "formal_castle_policy_staffing_warning",
    4435: "formal_assignment_burden_objection",
}
TERMINOLOGY_POLICY = (
    ("alliance", "동맹"),
    ("clan", "우리 가문"),
    ("diplomatic_attitude", "외교 자세"),
    ("county", "군"),
    ("domain", "영지"),
    ("castle_lord", "성주"),
    ("collective_count", "총"),
    ("land_stipend", "지행"),
    ("castle_town", "성하"),
    ("policy", "방침"),
    ("officer", "무장"),
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
    "C2E43D4245A1C88BB84F972EB43680819976424FDA72B577ED74AD27F15B8B31"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "4A364131A6CE283B9E4301485A327DAFE25119E81188C9BCF9112CABBFE80C88"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "5C888E07464C663119A27F5A6F794D50DCD003854E97F5E1B3C8436C104B0555"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "4905F3121F55C7C0F75355E91C703F70C5BECDB686E198F89D3618E25ED8FCB3"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "417A8C43F4F6CF68095C01BFF22AE1F054A20370306559858B3AD8DB5D8DA88F"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "9C086D845C6686E6A6CFE3FF3FBDFED47378D02FF0C90225B90A345952A40C8E"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "BE33E983405A9B4550117871F5EE7F1A2D4D29B14570DC07351E6134214CFA24"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "A0F6485949AB6525C8418A3B52E4390E47B3748A0C8249CBDC89E102EE468ACC"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "7FCFFF9C80BA6B197F86CE888FF911F0E5995DE5A3156561A12466D92D784559"
)
EXPECTED_BOUNDARY_SHA256 = (
    "DBD3ACDB23A3AE41C2972341754ABD395A4FDB2AC760D50DE0F78A99607BAA86"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "DD4A06447496A3CCAFFCE2826643012346460BDF80A91DBC0E04ED81C1C7FFDF"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "B698A52601EFCB1385F399326F3ECBCB314A3163A883ADF2DD54688367C4A384"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "76DFCF63A6880763E2BC05768721F21D9848589EA76FC67DBEE858F7A06F3038"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "66E75DA1AF36847CCF62B95777F25582B3C6737AEB5C753E233BDC86279E37CE"
)
EXPECTED_CANDIDATE_CALL_GRAPH_SHA256 = (
    "66E75DA1AF36847CCF62B95777F25582B3C6737AEB5C753E233BDC86279E37CE"
)
EXPECTED_RUNTIME_CONFLICT_SHA256 = (
    "C920B6659D1D1D4E9E55E01B7E054921CD1CF3D3C0E348D62E58E80CA1CD1B74"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "F6E4E361C7FCE23F2DEE9CF6B6923C3DBB0BCD87293813CA2E2DBE423864AA5C"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "AC6140F30D510D82C382DFD43FAACC088E4BD27795193CD3E0C9F279F93CF1F0"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "F52859182AD59F7473ABF72E243695BB696A70B62113060AA04A578705CA1549"
)
EXPECTED_CANDIDATE_SHA256 = (
    "87DD0FA6A24D1BCDAE64D8319C2F2526D4BBD3009633DA5A285E91D4D24BF182"
)
EXPECTED_CHANGED_LITERAL_COUNT = 15

DISCOVERED_PINS: dict[str, str] = {}

BASIS = (
    "The complete B045 queue universe and zero-based visible ordinal slice "
    "[67,134) are pinned before the sixteen-row residual is derived "
    "against the immutable exact-reuse prefill and every available "
    "independent PK decision output. Eleven complete target records and "
    "their twenty-six same-record companions are reviewed with pristine "
    "PK source, current Korean, PC English, Simplified Chinese, "
    "Traditional Chinese, slice boundaries, and completed Base semantic "
    "donors. The stable source correspondence in this region is "
    "PK-minus-fifty-nine: five records are raw-identical and six preserve "
    "the same literals and masked-gap structure while using different PK "
    "call operands. All target wording follows verified Base decisions, "
    "including dynamic-name quotation, token-safe particles, collective "
    "counts, honorific castle-lord references, and natural confirmation "
    "endings. Base runtime state and VM verification are never inherited. "
    "Twelve live PK call roots are traversed in both current and candidate "
    "archives. Seven records retain pre-existing PK morphology conflicts "
    "where prefilled stems meet incompatible speaker terminals; they are "
    "not promoted. All rows remain runtime pending. Tokens, calls, outer "
    "whitespace, line counts, protected signatures, complete records, "
    "reverse overlay and restoration, outside-scope identity, two-run "
    "reproduction, tamper rejection, and Steam read-only state are "
    "guarded; S1146 and S1148 remain optional."
)


def load_template() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1147_template",
        TEMPLATE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {TEMPLATE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


TEMPLATE = load_template()
ENGINE = TEMPLATE.ENGINE
sha256_bytes = TEMPLATE.sha256_bytes
canonical_sha256 = TEMPLATE.canonical_sha256
coordinate_key = TEMPLATE.coordinate_key
literal_texts = TEMPLATE.literal_texts
gap_bytes = TEMPLATE.gap_bytes
read_jsonl = TEMPLATE.read_jsonl
context_records = TEMPLATE.context_records
mask_call_operands = TEMPLATE.mask_call_operands
archive_records = TEMPLATE.archive_records
reachable_call_graph = TEMPLATE.reachable_call_graph


def patch_template_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
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
        "CONTEXT_RECORD_IDS": CONTEXT_RECORD_IDS,
        "BOUNDARY_RECORD_IDS": BOUNDARY_RECORD_IDS,
        "EXPECTED_CONTROLS_BY_RECORD": EXPECTED_CONTROLS_BY_RECORD,
        "EXPECTED_SOURCE_TARGET_SHA256": EXPECTED_SOURCE_TARGET_SHA256,
        "EXPECTED_CURRENT_TARGET_SHA256": EXPECTED_CURRENT_TARGET_SHA256,
        "EXPECTED_CONTEXT_CORPUS_SHA256": EXPECTED_CONTEXT_CORPUS_SHA256,
        "EXPECTED_GAP_CONTRACT_SHA256": EXPECTED_GAP_CONTRACT_SHA256,
        "EXPECTED_BOUNDARY_SHA256": EXPECTED_BOUNDARY_SHA256,
        "EXPECTED_RUNTIME_CONTROL_SHA256": EXPECTED_RUNTIME_CONTROL_SHA256,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
        "DISCOVERED_PINS": DISCOVERED_PINS,
    }
    for name, value in values.items():
        setattr(TEMPLATE, name, value)
    TEMPLATE.patch_template_globals()


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
    return actual


def runtime_controls(record: Any) -> tuple[tuple[int, ...], tuple[str, ...]]:
    return TEMPLATE.runtime_controls(record)


def assert_queue_and_residual_contract(prepared: Any) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} pinned source input drifted")
    ENGINE.validate_decisions(prepared, PREFILL, require_complete=False)
    queue_rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        str(target["coordinate"])
        for row in queue_rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(queue_rows) != 98
        or len(visible) != 199
        or visible[0] != "6:4370:0"
        or visible[-1] != "6:4467:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B045 queue universe drifted")
    guarded_digest(
        "queue universe",
        visible,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:4414:1"
        or queue_slice[-1] != "6:4437:2"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_rows
    )
    if len(prefilled) != 51:
        raise RuntimeError(f"segment {SEGMENT} prefill slice count drifted")
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
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
                    "pk_source_gap_template_sha256"
                ]
            ),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "translation_utf16le_sha256"
                ]
            ),
        )
        for coordinate in prefilled
    )
    guarded_digest(
        "prefill slice context",
        prefill_context,
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
    )
    existing: dict[str, str] = {}
    for path in sorted(
        DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")
    ):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        ENGINE.validate_decisions(prepared, path, require_complete=False)
        for row in read_jsonl(path):
            coordinate = row.get("coordinate")
            if (
                row.get("resource") != "pk_msggame"
                or not isinstance(coordinate, str)
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} mixed predecessor: {path}"
                )
            previous = existing.setdefault(coordinate, path.name)
            if previous != path.name:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate predecessor: {coordinate}"
                )
    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: {len(residual)} rows"
        )
    optional_present: list[str] = []
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            ENGINE.validate_decisions(prepared, path, require_complete=False)
            optional_present.append(path.name)
    return tuple(optional_present)


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    patch_template_globals()
    TEMPLATE.assert_context_contracts(prepared, records_by_label)


def base_row_is_approved(
    row: dict[str, Any] | None,
) -> bool:
    return bool(
        row is not None
        and row.get("semantic_review") == "approved"
        and row.get("runtime_review") == "verified"
    )


def base_match_kind(record_id: int) -> str:
    if record_id in RAW_EXACT_BASE_RECORD_IDS:
        return "raw_exact"
    if record_id in OPERAND_MASKED_BASE_RECORD_IDS:
        return "operand_masked"
    raise RuntimeError(f"segment {SEGMENT} missing Base match kind")


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
    base_rows = {
        str(row["coordinate"]): row for row in read_jsonl(BASE_PROMOTED)
    }
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    optional_rows: dict[str, dict[str, Any]] = {}
    for path in OPTIONAL_NEIGHBORS:
        if not path.is_file():
            continue
        for row in read_jsonl(path):
            coordinate = str(row["coordinate"])
            if coordinate in optional_rows:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate optional row: {coordinate}"
                )
            optional_rows[coordinate] = row
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_current = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    for record_id in TARGET_RECORD_IDS:
        base_record_id = BASE_RECORD_MAPPING[record_id]
        pk_record = records_by_label["jp"][(BLOCK_ID, record_id)]
        base_record = base_source[(BLOCK_ID, base_record_id)]
        pk_literals = literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, record_id),
        )
        base_literals = literal_texts(
            base_source,
            (BLOCK_ID, base_record_id),
        )
        base_current_literals = literal_texts(
            base_current,
            (BLOCK_ID, base_record_id),
        )
        current_literals = literal_texts(
            records_by_label["current"],
            (BLOCK_ID, record_id),
        )
        if (
            len(pk_literals) != EXPECTED_ARITY[record_id]
            or len(base_literals) != EXPECTED_ARITY[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} target arity drifted: {record_id}"
            )
        kind = base_match_kind(record_id)
        raw_exact = pk_record.data == base_record.data
        literals_equal = pk_literals == base_literals
        masked_equal = (
            mask_call_operands(pk_record)
            == mask_call_operands(base_record)
        )
        if (
            (kind == "raw_exact" and not (raw_exact and literals_equal))
            or (
                kind == "operand_masked"
                and (raw_exact or not literals_equal or not masked_equal)
            )
            or runtime_controls(base_record)
            != EXPECTED_BASE_CONTROLS_BY_RECORD[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base source match drifted: "
                f"{record_id}"
            )
        donor_rows: list[tuple[Any, ...]] = []
        owners: list[str] = []
        translations: list[str] = []
        references: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"6:{record_id}:{literal_id}"
            stable_reference = (
                f"6:{base_record_id}:{literal_id}"
            )
            if coordinate in TRANSLATIONS:
                reference = BASE_TARGET_DONOR_COORDINATES[coordinate]
                base_row = base_rows.get(reference)
                if not base_row_is_approved(base_row):
                    raise RuntimeError(
                        f"segment {SEGMENT} missing verified Base target: "
                        f"{reference}"
                    )
                assert base_row is not None
                actual = TRANSLATIONS[coordinate]
                expected = str(base_row["translation"])
                owner = "segment"
                seen_target.add(coordinate)
            elif coordinate in PREFILL_COMPANION_COORDINATES:
                prefill_row = prefill_rows.get(coordinate)
                if prefill_row is None:
                    raise RuntimeError(
                        f"segment {SEGMENT} missing prefill companion: "
                        f"{coordinate}"
                    )
                prefill_evidence = prefill_row.get(
                    "base_exact_reuse_prefill"
                )
                if not isinstance(prefill_evidence, dict):
                    raise RuntimeError(
                        f"segment {SEGMENT} malformed prefill companion: "
                        f"{coordinate}"
                    )
                reference = str(prefill_evidence["base_coordinate"])
                base_row = base_rows.get(reference)
                if not base_row_is_approved(base_row):
                    raise RuntimeError(
                        f"segment {SEGMENT} invalid prefill donor: "
                        f"{coordinate}"
                    )
                assert base_row is not None
                actual = str(prefill_row["translation"])
                expected = str(base_row["translation"])
                owner = "prefill"
                seen_companion.add(coordinate)
            elif coordinate in HIDDEN_COMPANION_COORDINATES:
                reference = stable_reference
                base_row = base_rows.get(reference)
                actual = current_literals[literal_id]
                expected = base_current_literals[literal_id]
                owner = "hidden_current"
                seen_companion.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} incomplete record owner: "
                    f"{coordinate}"
                )
            if actual != expected:
                raise RuntimeError(
                    f"segment {SEGMENT} complete assembly drifted: "
                    f"{coordinate}"
                )
            optional = optional_rows.get(coordinate)
            if optional is not None and str(optional["translation"]) != actual:
                raise RuntimeError(
                    f"segment {SEGMENT} optional neighbor conflicts: "
                    f"{coordinate}"
                )
            donor_rows.append(
                (
                    coordinate,
                    stable_reference,
                    reference,
                    (
                        str(base_row["translation"])
                        if base_row_is_approved(base_row)
                        and base_row is not None
                        else None
                    ),
                    base_row_is_approved(base_row),
                )
            )
            owners.append(owner)
            translations.append(actual)
            references.append(reference)
        base_evidence.append(
            (
                record_id,
                base_record_id,
                kind,
                sha256_bytes(pk_record.data),
                sha256_bytes(base_record.data),
                pk_literals,
                base_literals,
                base_current_literals,
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(pk_record)
                ),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(base_record)
                ),
                mask_call_operands(pk_record),
                mask_call_operands(base_record),
                EXPECTED_CONTROLS_BY_RECORD[record_id],
                EXPECTED_BASE_CONTROLS_BY_RECORD[record_id],
                tuple(donor_rows),
            )
        )
        assembly_evidence.append(
            (
                record_id,
                base_record_id,
                tuple(owners),
                tuple(translations),
                tuple(references),
                EXPECTED_CONTROLS_BY_RECORD[record_id],
                kind,
                record_id in RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS,
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_companion != set(ALL_COMPANION_COORDINATES)
        or set(PREFILL_COMPANION_COORDINATES)
        | set(HIDDEN_COMPANION_COORDINATES)
        != set(ALL_COMPANION_COORDINATES)
        or set(RAW_EXACT_BASE_RECORD_IDS)
        | set(OPERAND_MASKED_BASE_RECORD_IDS)
        != set(TARGET_RECORD_IDS)
        or set(RAW_EXACT_BASE_RECORD_IDS)
        & set(OPERAND_MASKED_BASE_RECORD_IDS)
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    guarded_digest(
        "Base context",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    guarded_digest(
        "complete assembly",
        tuple(assembly_evidence),
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )


def terminal_literal_set(
    records: dict[tuple[int, int], Any],
    terminals: tuple[tuple[int, int], ...],
) -> set[tuple[str, ...]]:
    return {
        literal_texts(records, coordinate)
        for coordinate in terminals
    }


def assert_call_graphs(prepared: Any, candidate: bytes) -> None:
    current_records = ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )
    candidate_records = archive_records(candidate)
    if len(candidate_records) != PK_RECORD_COUNT:
        raise RuntimeError(f"segment {SEGMENT} candidate graph universe drifted")
    current_evidence: list[tuple[Any, ...]] = []
    candidate_evidence: list[tuple[Any, ...]] = []
    for operand in EXPECTED_CALL_ROOTS:
        root = (operand // 10_000, operand % 10_000)
        current_graph, current_terminals = reachable_call_graph(
            current_records,
            root,
        )
        candidate_graph, candidate_terminals = reachable_call_graph(
            candidate_records,
            root,
        )
        current_literals = tuple(
            literal_texts(current_records, coordinate)
            for coordinate in current_terminals
        )
        candidate_literals = tuple(
            literal_texts(candidate_records, coordinate)
            for coordinate in candidate_terminals
        )
        if (
            not current_graph
            or not candidate_graph
            or not current_terminals
            or current_terminals != candidate_terminals
            or current_graph != candidate_graph
            or terminal_literal_set(current_records, current_terminals)
            != set(EXPECTED_TERMINAL_TUPLES[operand])
            or terminal_literal_set(candidate_records, candidate_terminals)
            != set(EXPECTED_TERMINAL_TUPLES[operand])
        ):
            raise RuntimeError(
                f"segment {SEGMENT} call graph drifted: {operand}"
            )
        current_evidence.append(
            (
                operand,
                root,
                current_graph,
                current_terminals,
                current_literals,
            )
        )
        candidate_evidence.append(
            (
                operand,
                root,
                candidate_graph,
                candidate_terminals,
                candidate_literals,
            )
        )
    guarded_digest(
        "call graph",
        tuple(current_evidence),
        EXPECTED_CALL_GRAPH_SHA256,
    )
    guarded_digest(
        "candidate call graph",
        tuple(candidate_evidence),
        EXPECTED_CANDIDATE_CALL_GRAPH_SHA256,
    )
    conflict_summary = (
        RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS,
        (
            4416,
            (1, 1, 178),
            "prefilled suitability stems meet incompatible PK terminals",
        ),
        (
            (4420, 4423),
            (1090,),
            "grant stems cannot take every PK terminal branch",
        ),
        (
            4425,
            (1168, 748, 1, 442),
            "gratitude and pledge stems conflict with PK speaker branches",
        ),
        (
            4426,
            (1, 1096),
            "collective thanks stem conflicts with full PK terminals",
        ),
        (
            4427,
            (538, 958),
            "acknowledgement prefix works but prefilled order stem conflicts",
        ),
        (
            4435,
            (568, 1),
            "objection stem conflicts with PK copula branches",
        ),
        (
            4434,
            (160, 322),
            "all current PK staffing branches remain grammatical",
        ),
        False,
    )
    guarded_digest(
        "runtime conflict",
        conflict_summary,
        EXPECTED_RUNTIME_CONFLICT_SHA256,
    )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    guarded_digest(
        "target coordinate",
        TARGET_COORDINATES,
        EXPECTED_TARGET_COORDINATE_SHA256,
    )
    guarded_digest(
        "translation policy",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    guarded_digest(
        "speaker style",
        tuple(SPEAKER_STYLE.items()),
        EXPECTED_SPEAKER_STYLE_SHA256,
    )
    guarded_digest(
        "terminology policy",
        TERMINOLOGY_POLICY,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    changed_coordinates = tuple(
        coordinate
        for coordinate, translation in TRANSLATIONS.items()
        if translation
        != literal_texts(
            records_by_label["current"],
            coordinate_key(coordinate)[:2],
        )[coordinate_key(coordinate)[2]]
    )
    expected_changed_coordinates = tuple(
        coordinate
        for coordinate in TARGET_COORDINATES
        if coordinate != "6:4425:0"
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or changed_coordinates != expected_changed_coordinates
        or TRANSLATIONS["6:4414:1"] != "을(를) 포함한 총"
        or TRANSLATIONS["6:4425:3"] != "와(과) 「"
        or TRANSLATIONS["6:4426:1"] != "」님과\n"
        or TRANSLATIONS["6:4427:0"] != "알겠"
        or TRANSLATIONS["6:4435:1"] != "지만\n"
        or ENGINE.KANA_OR_HAN_RE.search(SCRIPT.read_text(encoding="utf-8"))
    ):
        raise RuntimeError(f"segment {SEGMENT} semantic policy drifted")
    for coordinate, translation in TRANSLATIONS.items():
        key = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"],
            key[:2],
        )[key[2]]
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            "runtime_pending",
            coordinate,
        )
        if (
            translation.count("\n") != current_text.count("\n")
            or ENGINE.protected_signature(translation)
            != ENGINE.protected_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} shape drifted: {coordinate}"
            )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_template_globals()
    return TEMPLATE.build_candidate(prepared, records_by_label)


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source = records_by_label["jp"][(BLOCK_ID, record_id)]
    current = records_by_label["current"][(BLOCK_ID, record_id)]
    source_controls = runtime_controls(source)
    current_controls = runtime_controls(current)
    if (
        source_controls != EXPECTED_CONTROLS_BY_RECORD[record_id]
        or current_controls != source_controls
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime evidence drifted")
    conflict = record_id in RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS
    call_bearing = record_id in CALL_BEARING_RECORD_IDS
    return {
        "runtime_category": (
            "pk_live_morphology_conflict"
            if conflict
            else (
                "pk_call_graph_base_semantic_donor"
                if call_bearing
                else "pk_dynamic_fragment_base_semantic_donor"
            )
        ),
        "speaker_style": SPEAKER_STYLE[record_id],
        "source_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(source))
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(current))
        ),
        "source_direct_call_operands": source_controls[0],
        "current_direct_call_operands": current_controls[0],
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal":
        gap_bytes(source) == gap_bytes(current),
        "base_record_coordinate":
        f"6:{BASE_RECORD_MAPPING[record_id]}",
        "base_match_kind": base_match_kind(record_id),
        "complete_record_assembly_reviewed": True,
        "all_same_record_companions_reviewed": True,
        "live_pk_call_graphs_reviewed": call_bearing,
        "runtime_morphology_conflict_detected": conflict,
        "all_speaker_branches_grammatical": not conflict,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_semantic_donor_reviewed": True,
        "base_runtime_state_inherited": False,
        "base_vm_verification_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
    int,
    tuple[str, ...],
]:
    patch_template_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records_by_label = context_records(prepared)
    assert_context_contracts(prepared, records_by_label)
    assert_base_and_complete_assembly(prepared, records_by_label)
    assert_semantics(records_by_label)
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records_by_label,
    )
    assert_call_graphs(prepared, candidate)
    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"],
            (block_id, record_id),
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        reference = BASE_TARGET_DONOR_COORDINATES[coordinate]
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "pk_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256":
                target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256":
                target["current_ko_utf16le_sha256"],
                "translation": TRANSLATIONS[coordinate],
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "runtime_pending",
                "runtime_review": "pending",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "optional_neighbor_outputs_validated_if_present": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "prefill_companions_reviewed": True,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "base_wording_contextually_adapted": False,
                "base_context_reference_coordinate": reference,
                "base_context_reference_coordinates": (reference,),
                "base_context_is_automatic_reuse": False,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "speaker_style": SPEAKER_STYLE[record_id],
                "line_count_before": current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_evidence(records_by_label, record_id),
            }
        )
    return (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        optional_present,
    )


def assert_tamper_rejection(
    prepared: Any,
    rows: list[dict[str, Any]],
    candidate: bytes,
) -> None:
    patch_template_globals()
    TEMPLATE.assert_tamper_rejection(prepared, rows, candidate)


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or optional_present != second[5]
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
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    if (
        len(rows) != 16
        or len(validated) != 16
        or counts != Counter({"runtime_fragment_pending": 16})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["base_vm_verification_inherited"] is not False
            or row["line_count_preserved"] is not True
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B045_S1147",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "slice_first_coordinate": "6:4414:1",
                "slice_last_coordinate": "6:4437:2",
                "first_residual_coordinate": TARGET_COORDINATES[0],
                "last_residual_coordinate": TARGET_COORDINATES[-1],
                "queue_record_count": 98,
                "queue_visible_count": 199,
                "slice_visible_count": 67,
                "exact_reuse_prefill_count": 51,
                "residual_count": len(rows),
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "raw_exact_base_record_count":
                len(RAW_EXACT_BASE_RECORD_IDS),
                "operand_masked_base_record_count":
                len(OPERAND_MASKED_BASE_RECORD_IDS),
                "same_record_companion_count":
                len(ALL_COMPANION_COORDINATES),
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "hidden_companion_count":
                len(HIDDEN_COMPANION_COORDINATES),
                "call_root_count": len(EXPECTED_CALL_ROOTS),
                "runtime_morphology_conflict_record_count":
                len(RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "speaker_style_sha256":
                EXPECTED_SPEAKER_STYLE_SHA256,
                "terminology_policy_sha256":
                EXPECTED_TERMINOLOGY_POLICY_SHA256,
                "call_graph_sha256":
                EXPECTED_CALL_GRAPH_SHA256,
                "candidate_call_graph_sha256":
                EXPECTED_CANDIDATE_CALL_GRAPH_SHA256,
                "runtime_conflict_sha256":
                EXPECTED_RUNTIME_CONFLICT_SHA256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "builder_sha256": sha256_bytes(SCRIPT.read_bytes()),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "full_queue_universe_guarded": True,
                "slice_prefill_context_guarded": True,
                "canonical_base_donors_pinned": True,
                "complete_record_assembly_guarded": True,
                "live_pk_call_graphs_guarded": True,
                "candidate_call_graphs_guarded": True,
                "runtime_morphology_conflicts_guarded": True,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "runtime_promotion_authorized": False,
                "speaker_registers_reviewed": True,
                "historical_terminology_reviewed": True,
                "outside_scope_records_exact": True,
                "runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "steam_read_only": True,
                "steam_write_performed": False,
                "input_root": str(ENGINE.DEFAULT_STEAM_ROOT),
                "output": str(OUTPUT),
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
