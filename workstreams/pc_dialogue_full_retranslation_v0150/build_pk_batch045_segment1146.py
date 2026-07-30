#!/usr/bin/env python3
"""Build source-redacted PK B045 segment 1146 residual decisions."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch044_segment1143.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B045_S1146.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B045_S1147.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B045_S1148.private.v1.jsonl",
)

SEGMENT = 1146
QUEUE_BATCH_ID = "pk_msggame-B045"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "6:4370:0",
    "6:4370:1",
    "6:4370:2",
    "6:4387:0",
    "6:4394:2",
    "6:4396:0",
    "6:4402:0",
    "6:4404:0",
    "6:4406:0",
    "6:4407:1",
    "6:4412:1",
)
TRANSLATIONS = {
    "6:4370:0": "의 「",
    "6:4370:1": "」을(를) LV",
    "6:4370:2": "까지 증축",
    "6:4387:0": "은(는) 임무「",
    "6:4394:2": "?",
    "6:4396:0": "알겠",
    "6:4402:0": ", 「",
    "6:4404:0": "알겠",
    "6:4406:0": "그럼 「",
    "6:4407:1": "」와(과)의 친선을 중단",
    "6:4412:1": "을(를) 포함한 총",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    4370,
    4387,
    4394,
    4396,
    4402,
    4404,
    4406,
    4407,
    4412,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    4370: 3,
    4387: 2,
    4394: 3,
    4396: 3,
    4402: 2,
    4404: 3,
    4406: 2,
    4407: 2,
    4412: 3,
}
BASE_RECORD_MAPPING = {
    record_id: record_id - 59
    for record_id in TARGET_RECORD_IDS
}
RAW_EXACT_BASE_RECORD_IDS = (
    4370,
    4387,
    4394,
    4406,
    4407,
    4412,
)
OPERAND_MASKED_BASE_RECORD_IDS = (
    4396,
    4402,
    4404,
)
ADAPTED_COORDINATES = {"6:4394:2"}
SLICE_PREFILL_COORDINATES = (
    "6:4371:0",
    "6:4372:0",
    "6:4373:0",
    "6:4374:0",
    "6:4375:0",
    "6:4376:0",
    "6:4377:0",
    "6:4378:0",
    "6:4379:0",
    "6:4380:0",
    "6:4381:0",
    "6:4382:0",
    "6:4383:0",
    "6:4384:0",
    "6:4385:0",
    "6:4386:0",
    "6:4387:1",
    "6:4388:0",
    "6:4389:0",
    "6:4390:0",
    "6:4391:0",
    "6:4392:0",
    "6:4393:0",
    "6:4393:1",
    "6:4394:0",
    "6:4394:1",
    "6:4395:0",
    "6:4396:2",
    "6:4397:0",
    "6:4397:1",
    "6:4398:0",
    "6:4398:1",
    "6:4399:0",
    "6:4400:0",
    "6:4400:1",
    "6:4401:0",
    "6:4401:1",
    "6:4402:1",
    "6:4403:0",
    "6:4403:1",
    "6:4404:1",
    "6:4404:2",
    "6:4405:0",
    "6:4406:1",
    "6:4407:0",
    "6:4408:0",
    "6:4408:1",
    "6:4409:0",
    "6:4410:0",
    "6:4411:0",
    "6:4411:1",
    "6:4412:0",
    "6:4412:2",
    "6:4413:0",
    "6:4413:1",
    "6:4414:0",
)
PREFILL_COMPANION_COORDINATES = (
    "6:4387:1",
    "6:4394:0",
    "6:4394:1",
    "6:4396:2",
    "6:4402:1",
    "6:4404:1",
    "6:4404:2",
    "6:4406:1",
    "6:4407:0",
    "6:4412:0",
    "6:4412:2",
)
PREFILL_ONLY_COORDINATES = tuple(
    coordinate
    for coordinate in SLICE_PREFILL_COORDINATES
    if coordinate not in PREFILL_COMPANION_COORDINATES
)
CONTEXT_RECORD_IDS = tuple(range(4367, 4418))
BOUNDARY_RECORD_IDS = (
    4367,
    4368,
    4369,
    4415,
    4416,
    4417,
)
EXPECTED_CALL_ROOTS = (
    364,
    424,
    466,
    538,
    862,
    1126,
)
EXPECTED_CALL_TERMINAL_SETS = {
    364: {"겠습니다", "기로 하지", "이렇게"},
    424: {"하겠다", "하겠습니다", "하자", "합시다"},
    466: {"하겠사옵니다", "하겠습니다", "하다", "합니다"},
    538: {"다", "했습니다"},
    862: {"예"},
    1126: {"하리라", "합시다"},
}
SPEAKER_STYLE = {
    4370: "speaker_independent_facility_expansion_notice",
    4387: "speaker_independent_marriage_mission_cancellation_prompt",
    4394: "dynamic_policy_issue_recommendation",
    4396: "dynamic_policy_issue_acknowledgement",
    4402: "dynamic_policy_revision_acknowledgement",
    4404: "dynamic_policy_improvement_acknowledgement",
    4406: "neutral_alliance_extension_statement",
    4407: "speaker_independent_goodwill_cancellation_notice",
    4412: "speaker_independent_alliance_diplomatic_fallout_notice",
}
TERMINOLOGY_POLICY = (
    ("mission", "임무"),
    ("marriage_alliance", "혼인 동맹"),
    ("policy_issue", "발령"),
    ("policy_revision", "개정"),
    ("facility_expansion", "증축"),
    ("alliance", "동맹"),
    ("goodwill", "친선"),
    ("clan", "가문"),
    ("faction", "세력"),
    ("dynamic_names", "「」로 경계 표시"),
)
BASIS = (
    "순정 PK 원문과 PC 영어·간체·번체의 완전 레코드 문맥, "
    "같은 레코드의 Base exact-reuse prefill 조각을 함께 검토했다. "
    "Base 완료 번역은 raw-exact 또는 call-operand-masked semantic "
    "donor로 사용했다. 호출 종단 앞의 의문 조각 한 곳은 PK 조합에 "
    "맞춰 적응했으며 PK의 런타임·VM 검증 상태는 승계하지 않았다."
)

EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017C"
    "CEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PRISTINE_PK_SHA256 = (
    "31D52FB797EA31CBD75646A2E16078296"
    "35AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A"
    "67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA8"
    "28FA4794509454263170E82ABA3600CF"
)
EXPECTED_CHANGED_LITERAL_COUNT = 11

EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "C2E43D4245A1C88BB84F972EB4368081"
    "9976424FDA72B577ED74AD27F15B8B31"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "C2D2616F2BE36CC4A78E5C9A320CA240"
    "2D78CD8C383D4CDABAF88D0ACC5EFEBB"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "27A97FEAF847DB6B73933EFB19136FDB"
    "67FF7D9A8EA3DB8164B09C7C6AB3FBC2"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "5452FA89B32D0FE1E65AA90890218081"
    "E344B4118EDFE0D56DF179D39E4F6E35"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "0FF10200050642B6026A2FAF903D1BD1"
    "2F7AC0CFFA6E9CC21C5A0A23BA42BD23"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "1D288275D639DB31CFA0FD71BA0F39B9"
    "185B9F5884D7B1E57C4944E2542BE595"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "A3EBAE65AFBFE8AB3C97DEA2A88228D3"
    "7262BAAEEDCE63B7C4BC15172FBC0C9D"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "0BA382CDE444A37175EB545346F1F2F1"
    "BCD80FDAFB1265D2759B8590E58B6D64"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "AC746F064977AC06D72008AAA09AE8AE"
    "120C8A31A752A64024A11F393E2489B0"
)
EXPECTED_BOUNDARY_SHA256 = (
    "38E5A9866007503DC7AE271453C630B0"
    "C69F2C5785E03AF9350A45C4709726B6"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "844E4BEC50D265D60A9A8A32E06A420"
    "642D2B0B1FF06BE034AC6CDCE28E10BAC"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "47B2049B1B0E027A8DFB5824ECE3346D"
    "1E8202EC7B0546590BDD8F8781CB6D33"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "BC61299C783E432FCA6DBFF3534003D1"
    "276674F2AE7D3AF976F244DF338880F3"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "D28A167361A630B35BE1E6151AC05C7B"
    "4A5079A63AE8E646257B4841C87446AB"
)
EXPECTED_RUNTIME_CONFLICT_SHA256 = (
    "33EFC0365F4A51571123B36635E8B398"
    "A9636A40797157020519CA065392625A"
)
EXPECTED_CANDIDATE_INTEGRITY_SHA256 = (
    "E49DF222E68F3F371AE56EC527811B3F"
    "6A353422B9417156706D25CB4A3C45B7"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "97BEBFD0EDDD81F80FC5AD26E679A3F"
    "4D6338BDEE2800DF900DE4A493E2E1728"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "D57D524874A34C993A97B26458644200"
    "9DC02F52AD1FE738FD406CA0826DEC06"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "B0DD6CE80BC18C991A42FB185595CDBD"
    "C86F4AF547C69A3AB5F70977C843FF36"
)
EXPECTED_CANDIDATE_SHA256 = (
    "DBF99F4FF8A257922E52B89A761DCAD"
    "73059E3283CB8A4DF02F206AFDBCF9923"
)

DISCOVERED_PINS: dict[str, str] = {}


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


TEMPLATE = load_module(
    "pc_dialogue_full_retranslation_v0150_pk_s1146_template",
    TEMPLATE_PATH,
)
ENGINE = TEMPLATE.ENGINE
CALL_GRAPH = TEMPLATE.TEMPLATE.CALL_GRAPH
sha256_bytes = TEMPLATE.sha256_bytes
canonical_sha256 = TEMPLATE.canonical_sha256
coordinate_key = TEMPLATE.coordinate_key
literal_texts = TEMPLATE.literal_texts
gap_bytes = TEMPLATE.gap_bytes
read_jsonl = TEMPLATE.read_jsonl
context_records = TEMPLATE.context_records
runtime_controls = TEMPLATE.runtime_controls
mask_call_operands = TEMPLATE.TEMPLATE.mask_call_operands


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
        "BASE_RECORD_MAPPING": BASE_RECORD_MAPPING,
        "EXPECTED_CHANGED_LITERAL_COUNT":
        EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256":
        EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
        "EXPECTED_CANDIDATE_INTEGRITY_SHA256":
        EXPECTED_CANDIDATE_INTEGRITY_SHA256,
        "DISCOVERED_PINS": DISCOVERED_PINS,
    }
    for name, value in values.items():
        setattr(TEMPLATE, name, value)
    TEMPLATE.patch_template_globals()


def guarded_digest(
    label: str,
    value: Any,
    expected: str,
) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


def all_existing_decisions(
    prepared: Any,
) -> dict[str, dict[str, Any]]:
    existing: dict[str, dict[str, Any]] = {}
    owners: dict[str, str] = {}
    for path in sorted(
        DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")
    ):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        ENGINE.validate_decisions(
            prepared, path, require_complete=False
        )
        for row in read_jsonl(path):
            coordinate = row.get("coordinate")
            if (
                row.get("resource") != "pk_msggame"
                or not isinstance(coordinate, str)
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} mixed predecessor: {path}"
                )
            previous = owners.setdefault(coordinate, path.name)
            if previous != path.name:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate predecessor: "
                    f"{coordinate}"
                )
            existing[coordinate] = row
    return existing


def assert_queue_and_residual_contract(
    prepared: Any,
) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} source input drifted")
    ENGINE.validate_decisions(
        prepared, PREFILL, require_complete=False
    )
    queue_rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line
        and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
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
        raise RuntimeError(f"segment {SEGMENT} queue universe drifted")
    guarded_digest(
        "EXPECTED_QUEUE_UNIVERSE_SHA256",
        visible,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:4370:0"
        or queue_slice[-1] != "6:4414:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    guarded_digest(
        "EXPECTED_QUEUE_SLICE_SHA256",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    prefill_rows = {
        str(row["coordinate"]): row
        for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_rows
    )
    if (
        len(prefilled) != 56
        or prefilled != SLICE_PREFILL_COORDINATES
    ):
        raise RuntimeError(f"segment {SEGMENT} prefill drifted")
    guarded_digest(
        "EXPECTED_PREFILLED_COORDINATE_SHA256",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
    prefill_context = tuple(
        (
            coordinate,
            str(prefill_rows[coordinate]["translation"]),
            str(
                prefill_rows[coordinate][
                    "source_record_raw_sha256"
                ]
            ),
            str(
                prefill_rows[coordinate][
                    "current_ko_utf16le_sha256"
                ]
            ),
            str(prefill_rows[coordinate]["semantic_review"]),
            str(prefill_rows[coordinate]["runtime_review"]),
            str(prefill_rows[coordinate]["layout_review"]),
            str(
                prefill_rows[coordinate][
                    "base_exact_reuse_prefill"
                ]["base_coordinate"]
            ),
            str(
                prefill_rows[coordinate][
                    "base_exact_reuse_prefill"
                ]["pk_operand_masked_gap_template_sha256"]
            ),
            str(
                prefill_rows[coordinate][
                    "base_exact_reuse_prefill"
                ]["translation_utf16le_sha256"]
            ),
        )
        for coordinate in prefilled
    )
    guarded_digest(
        "EXPECTED_PREFILL_SLICE_CONTEXT_SHA256",
        prefill_context,
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
    )
    existing = all_existing_decisions(prepared)
    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual drifted: {len(residual)}"
        )
    optional_present: list[str] = []
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            ENGINE.validate_decisions(
                prepared, path, require_complete=False
            )
            optional_present.append(path.name)
    return tuple(optional_present)


def assert_context_contracts(
    records_by_label: dict[
        str, dict[tuple[int, int], Any]
    ],
) -> None:
    source_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["jp"],
                coordinate_key(coordinate)[:2],
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    current_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["current"],
                coordinate_key(coordinate)[:2],
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    corpus = tuple(
        (
            label,
            record_id,
            sha256_bytes(records[(BLOCK_ID, record_id)].data),
            literal_texts(records, (BLOCK_ID, record_id)),
        )
        for label, records in records_by_label.items()
        for record_id in CONTEXT_RECORD_IDS
    )
    gaps = tuple(
        (
            label,
            record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label[label][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    boundaries = tuple(
        (
            label,
            record_id,
            sha256_bytes(
                records_by_label[label][
                    (BLOCK_ID, record_id)
                ].data
            ),
            literal_texts(
                records_by_label[label],
                (BLOCK_ID, record_id),
            ),
        )
        for label in ("jp", "current", "en", "sc", "tc")
        for record_id in BOUNDARY_RECORD_IDS
    )
    controls = tuple(
        (
            label,
            record_id,
            runtime_controls(
                records_by_label[label][
                    (BLOCK_ID, record_id)
                ]
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    for label, value, expected in (
        (
            "EXPECTED_SOURCE_TARGET_SHA256",
            source_target,
            EXPECTED_SOURCE_TARGET_SHA256,
        ),
        (
            "EXPECTED_CURRENT_TARGET_SHA256",
            current_target,
            EXPECTED_CURRENT_TARGET_SHA256,
        ),
        (
            "EXPECTED_CONTEXT_CORPUS_SHA256",
            corpus,
            EXPECTED_CONTEXT_CORPUS_SHA256,
        ),
        (
            "EXPECTED_GAP_CONTRACT_SHA256",
            gaps,
            EXPECTED_GAP_CONTRACT_SHA256,
        ),
        (
            "EXPECTED_BOUNDARY_SHA256",
            boundaries,
            EXPECTED_BOUNDARY_SHA256,
        ),
        (
            "EXPECTED_RUNTIME_CONTROL_SHA256",
            controls,
            EXPECTED_RUNTIME_CONTROL_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)
    for record_id in TARGET_RECORD_IDS:
        source = records_by_label["jp"][
            (BLOCK_ID, record_id)
        ]
        current = records_by_label["current"][
            (BLOCK_ID, record_id)
        ]
        if (
            gap_bytes(source) != gap_bytes(current)
            or runtime_controls(source)
            != runtime_controls(current)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} source/current runtime drifted: "
                f"{record_id}"
            )


def base_row_is_approved(
    row: dict[str, Any] | None,
) -> bool:
    return bool(
        row is not None
        and row.get("semantic_review") == "approved"
        and row.get("runtime_review") in ("verified", "not_required")
    )


def base_match_kind(record_id: int) -> str:
    if record_id in RAW_EXACT_BASE_RECORD_IDS:
        return "raw_exact"
    if record_id in OPERAND_MASKED_BASE_RECORD_IDS:
        return "operand_masked"
    raise RuntimeError(
        f"segment {SEGMENT} missing Base match kind: {record_id}"
    )


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[
        str, dict[tuple[int, int], Any]
    ],
) -> None:
    if (
        sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} Base input drifted")
    base_rows = {
        str(row["coordinate"]): row
        for row in read_jsonl(BASE_PROMOTED)
    }
    prefill_rows = {
        str(row["coordinate"]): row
        for row in read_jsonl(PREFILL)
    }
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_current = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_prefill: set[str] = set()
    for record_id in TARGET_RECORD_IDS:
        pk_key = (BLOCK_ID, record_id)
        base_record_id = BASE_RECORD_MAPPING[record_id]
        base_key = (BLOCK_ID, base_record_id)
        pk_record = records_by_label["jp"][pk_key]
        base_record = base_source[base_key]
        pk_literals = literal_texts(
            records_by_label["jp"], pk_key
        )
        current_literals = literal_texts(
            records_by_label["current"], pk_key
        )
        base_literals = literal_texts(base_source, base_key)
        base_current_literals = literal_texts(
            base_current, base_key
        )
        kind = base_match_kind(record_id)
        raw_exact = pk_record.data == base_record.data
        literal_exact = pk_literals == base_literals
        masked_exact = (
            mask_call_operands(pk_record)
            == mask_call_operands(base_record)
        )
        if (
            len(pk_literals) != EXPECTED_ARITY[record_id]
            or (
                kind == "raw_exact"
                and not (raw_exact and literal_exact)
            )
            or (
                kind == "operand_masked"
                and (
                    raw_exact
                    or not literal_exact
                    or not masked_exact
                )
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base match drifted: "
                f"{record_id}"
            )
        owners: list[str] = []
        translations: list[str] = []
        donor_values: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = (
                f"{BLOCK_ID}:{record_id}:{literal_id}"
            )
            donor = (
                f"{BLOCK_ID}:{base_record_id}:{literal_id}"
            )
            row = base_rows.get(donor)
            if coordinate in TRANSLATIONS:
                actual = TRANSLATIONS[coordinate]
                owners.append("target")
                seen_target.add(coordinate)
            elif coordinate in PREFILL_COMPANION_COORDINATES:
                actual = str(
                    prefill_rows[coordinate]["translation"]
                )
                owners.append("prefill")
                seen_prefill.add(coordinate)
            else:
                actual = current_literals[literal_id]
                owners.append("reviewed_invisible_companion")
            if base_row_is_approved(row):
                assert row is not None
                donor_value = str(row["translation"])
                if (
                    coordinate in ADAPTED_COORDINATES
                    and not (
                        coordinate == "6:4394:2"
                        and donor_value == "인가?"
                        and actual == "?"
                    )
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} adapted Base translation "
                        f"drifted: {coordinate}"
                    )
                if (
                    coordinate not in ADAPTED_COORDINATES
                    and actual != donor_value
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} Base translation drifted: "
                        f"{coordinate}"
                    )
            else:
                donor_value = base_current_literals[literal_id]
                if (
                    coordinate in TRANSLATIONS
                    or coordinate in PREFILL_COMPANION_COORDINATES
                    or actual != donor_value
                    or actual != pk_literals[literal_id]
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} invisible donor drifted: "
                        f"{coordinate}"
                    )
            translations.append(actual)
            donor_values.append(donor_value)
            if coordinate in TRANSLATIONS:
                base_evidence.append(
                    (
                        coordinate,
                        donor,
                        kind,
                        sha256_bytes(pk_record.data),
                        sha256_bytes(base_record.data),
                        pk_literals[literal_id],
                        current_literals[literal_id],
                        base_current_literals[literal_id],
                        actual,
                        str(row["runtime_review"]),
                    )
                )
        assembly_evidence.append(
            (
                record_id,
                base_record_id,
                kind,
                tuple(owners),
                tuple(translations),
                tuple(donor_values),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(pk_record)
                ),
                runtime_controls(pk_record),
                runtime_controls(base_record),
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
        or len(PREFILL_COMPANION_COORDINATES) != 11
        or len(PREFILL_ONLY_COORDINATES) != 45
    ):
        raise RuntimeError(
            f"segment {SEGMENT} assembly ownership drifted"
        )
    guarded_digest(
        "EXPECTED_BASE_CONTEXT_SHA256",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    guarded_digest(
        "EXPECTED_COMPLETE_ASSEMBLY_SHA256",
        tuple(assembly_evidence),
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )


def assert_call_graphs_and_semantics(
    prepared: Any,
    records_by_label: dict[
        str, dict[tuple[int, int], Any]
    ],
) -> None:
    guarded_digest(
        "EXPECTED_TARGET_COORDINATE_SHA256",
        TARGET_COORDINATES,
        EXPECTED_TARGET_COORDINATE_SHA256,
    )
    guarded_digest(
        "EXPECTED_TRANSLATION_POLICY_SHA256",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    guarded_digest(
        "EXPECTED_SPEAKER_STYLE_SHA256",
        tuple(SPEAKER_STYLE.items()),
        EXPECTED_SPEAKER_STYLE_SHA256,
    )
    guarded_digest(
        "EXPECTED_TERMINOLOGY_POLICY_SHA256",
        TERMINOLOGY_POLICY,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or len(TRANSLATIONS) != 11
        or TRANSLATIONS["6:4370:0"] != "의 「"
        or TRANSLATIONS["6:4394:2"] != "?"
        or TRANSLATIONS["6:4402:0"] != ", 「"
        or TRANSLATIONS["6:4412:1"] != "을(를) 포함한 총"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic policy drifted"
        )
    current_records = ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )
    call_evidence: list[tuple[Any, ...]] = []
    for operand in EXPECTED_CALL_ROOTS:
        graph, terminals = CALL_GRAPH.reachable_call_graph(
            current_records, (0, operand)
        )
        terminal_literals = tuple(
            literal_texts(current_records, coordinate)
            for coordinate in terminals
        )
        values = {
            value
            for literals in terminal_literals
            for value in literals
        }
        if (
            len(graph) != 14
            or len(terminals) != 7
            or any(
                len(literals) > 1
                for literals in terminal_literals
            )
            or values != EXPECTED_CALL_TERMINAL_SETS[operand]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} call graph drifted: {operand}"
            )
        call_evidence.append(
            (operand, graph, terminals, terminal_literals)
        )
    guarded_digest(
        "EXPECTED_CALL_GRAPH_SHA256",
        tuple(call_evidence),
        EXPECTED_CALL_GRAPH_SHA256,
    )
    conflict_summary = (
        (
            4394,
            (364,),
            "question_fragment_adapted_but_one_upstream_leaf_conflicts",
        ),
        (
            4396,
            (538, 466),
            "acknowledgement_and_action_stem_branch_conflicts",
        ),
        (
            4402,
            (862, 424),
            "prefix_branch_ok_action_stem_branch_conflict",
        ),
        (
            4404,
            (538, 1126),
            "acknowledgement_and_action_stem_branch_conflicts",
        ),
        "base_runtime_state_not_inherited",
        "all_target_rows_runtime_pending",
    )
    guarded_digest(
        "EXPECTED_RUNTIME_CONFLICT_SHA256",
        conflict_summary,
        EXPECTED_RUNTIME_CONFLICT_SHA256,
    )
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = coordinate_key(
            coordinate
        )
        current_text = literal_texts(
            records_by_label["current"],
            (block_id, record_id),
        )[literal_id]
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            "runtime_pending",
            coordinate,
        )
        if (
            translation.count("\n")
            != current_text.count("\n")
            or ENGINE.protected_signature(translation)
            != ENGINE.protected_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} shape drifted: {coordinate}"
            )


def build_candidate(
    prepared: Any,
    records_by_label: dict[
        str, dict[tuple[int, int], Any]
    ],
) -> tuple[bytes, str, int]:
    patch_template_globals()
    return TEMPLATE.build_candidate(prepared, records_by_label)


def assert_candidate_integrity(
    prepared: Any,
    records_by_label: dict[
        str, dict[tuple[int, int], Any]
    ],
    candidate: bytes,
) -> None:
    patch_template_globals()
    TEMPLATE.assert_candidate_integrity(
        prepared, records_by_label, candidate
    )


def runtime_evidence(
    prepared: Any,
    records_by_label: dict[
        str, dict[tuple[int, int], Any]
    ],
    record_id: int,
) -> dict[str, Any]:
    source_record = records_by_label["jp"][
        (BLOCK_ID, record_id)
    ]
    current_record = records_by_label["current"][
        (BLOCK_ID, record_id)
    ]
    base_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_record = base_records[
        (BLOCK_ID, BASE_RECORD_MAPPING[record_id])
    ]
    source_controls = runtime_controls(source_record)
    current_controls = runtime_controls(current_record)
    conflict = bool(source_controls[0])
    if (
        source_controls != current_controls
        or gap_bytes(source_record) != gap_bytes(current_record)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime evidence drifted: "
            f"{record_id}"
        )
    return {
        "runtime_category":
        "pk_dynamic_fragment_base_semantic_donor",
        "source_record_gap_sha256": canonical_sha256(
            tuple(
                value.hex().upper()
                for value in gap_bytes(source_record)
            )
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(
                value.hex().upper()
                for value in gap_bytes(current_record)
            )
        ),
        "source_direct_call_operands": source_controls[0],
        "current_direct_call_operands": current_controls[0],
        "base_direct_call_operands":
        runtime_controls(base_record)[0],
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal": True,
        "base_record_coordinate":
        f"{BLOCK_ID}:{BASE_RECORD_MAPPING[record_id]}",
        "base_match_kind": base_match_kind(record_id),
        "complete_record_assembly_reviewed": True,
        "all_same_record_prefill_companions_reviewed": True,
        "all_slice_prefill_rows_reviewed": True,
        "manual_pc_english_simplified_traditional_review": True,
        "live_pk_call_graphs_reviewed": conflict,
        "runtime_morphology_conflict_detected": conflict,
        "all_speaker_branches_grammatical": not conflict,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_runtime_state_inherited": False,
        "base_vm_verification_inherited": False,
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
    optional_present = assert_queue_and_residual_contract(
        prepared
    )
    records_by_label = context_records(prepared)
    assert_context_contracts(records_by_label)
    assert_base_and_complete_assembly(
        prepared, records_by_label
    )
    assert_call_graphs_and_semantics(
        prepared, records_by_label
    )
    candidate, candidate_sha256, changed = build_candidate(
        prepared, records_by_label
    )
    assert_candidate_integrity(
        prepared, records_by_label, candidate
    )
    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(
            coordinate
        )
        current_text = literal_texts(
            records_by_label["current"],
            (block_id, record_id),
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
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
                "scope_classification":
                "runtime_fragment_pending",
                "layout_review": "runtime_pending",
                "runtime_review": "pending",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "optional_neighbor_outputs_validated_if_present":
                True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "prefill_companions_reviewed": True,
                "all_slice_prefill_rows_reviewed": True,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "base_wording_contextually_adapted":
                coordinate in ADAPTED_COORDINATES,
                "base_context_reference_coordinate":
                (
                    f"{BLOCK_ID}:"
                    f"{BASE_RECORD_MAPPING[record_id]}:"
                    f"{literal_id}"
                ),
                "base_context_is_automatic_reuse": False,
                "base_match_kind": base_match_kind(record_id),
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "speaker_style": SPEAKER_STYLE[record_id],
                "line_count_before":
                current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_evidence(
                    prepared, records_by_label, record_id
                ),
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
    tampered_policy = dict(TRANSLATIONS)
    tampered_policy["6:4370:0"] += "X"
    if (
        canonical_sha256(tuple(tampered_policy.items()))
        == EXPECTED_TRANSLATION_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} policy tamper accepted"
        )
    tampered_candidate = ENGINE.rebuild_packed_with_literals(
        prepared.resources["pk_msggame"].current_blob,
        {
            coordinate_key(coordinate): translation
            for coordinate, translation
            in tampered_policy.items()
        },
    )
    if (
        tampered_candidate == candidate
        or sha256_bytes(tampered_candidate)
        == EXPECTED_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate tamper accepted"
        )
    tampered_rows = copy.deepcopy(rows)
    tampered_rows[0]["source_record_raw_sha256"] = "0" * 64
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="s1146_tamper_",
        dir=OUTPUT.parent,
    ) as temporary:
        tampered_path = (
            Path(temporary) / "tampered.private.v1.jsonl"
        )
        ENGINE.atomic_write(
            tampered_path, ENGINE.jsonl(tampered_rows)
        )
        try:
            ENGINE.validate_decisions(
                prepared,
                tampered_path,
                require_complete=False,
            )
        except (RuntimeError, ValueError):
            pass
        else:
            raise RuntimeError(
                f"segment {SEGMENT} decision tamper accepted"
            )


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
        raise RuntimeError(
            f"segment {SEGMENT} second-run reproduction drifted"
        )
    if DISCOVERED_PINS:
        print(
            json.dumps(
                {
                    **DISCOVERED_PINS,
                    "changed_literal_count": changed,
                },
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 2
    resource = prepared.resources["pk_msggame"]
    steam_path = resource.current_path
    steam_before = sha256_bytes(steam_path.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: "
            f"{steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared, OUTPUT, require_complete=False
    )
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    if (
        len(rows) != 11
        or len(validated) != 11
        or counts
        != Counter({"runtime_fragment_pending": 11})
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
        raise RuntimeError(
            f"segment {SEGMENT} decision validation drifted"
        )
    assert_tamper_rejection(prepared, rows, candidate)
    if sha256_bytes(steam_path.read_bytes()) != steam_before:
        raise RuntimeError(
            f"segment {SEGMENT} wrote to Steam input"
        )
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B045_S1146",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "slice_first_coordinate": "6:4370:0",
                "slice_last_coordinate": "6:4414:0",
                "slice_visible_count": 67,
                "exact_reuse_prefill_count": 56,
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "prefill_only_count":
                len(PREFILL_ONLY_COORDINATES),
                "residual_count": len(rows),
                "scope_classification_counts": dict(counts),
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "raw_exact_base_record_count":
                len(RAW_EXACT_BASE_RECORD_IDS),
                "operand_masked_base_record_count":
                len(OPERAND_MASKED_BASE_RECORD_IDS),
                "call_root_count": len(EXPECTED_CALL_ROOTS),
                "optional_neighbors_present":
                list(optional_present),
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
                "runtime_conflict_sha256":
                EXPECTED_RUNTIME_CONFLICT_SHA256,
                "decision_sha256":
                sha256_bytes(OUTPUT.read_bytes()),
                "builder_sha256":
                sha256_bytes(SCRIPT.read_bytes()),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "full_queue_universe_guarded": True,
                "slice_prefill_context_guarded": True,
                "manual_pk_jp_pc_en_sc_tc_review": True,
                "complete_multi_literal_records_guarded": True,
                "raw_exact_and_operand_masked_donors_guarded": True,
                "live_pk_call_graphs_guarded": True,
                "remaining_runtime_conflicts_explicit": True,
                "runtime_tokens_and_gaps_guarded": True,
                "speaker_register_guarded": True,
                "historical_terminology_guarded": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "runtime_promotion_authorized": False,
                "steam_read_only": True,
                "steam_write_performed": False,
                "input_root": str(ENGINE.DEFAULT_STEAM_ROOT),
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
