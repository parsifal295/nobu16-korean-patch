#!/usr/bin/env python3
"""Build source-redacted PK B046 segment 1149 residual decisions."""

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
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch045_segment1146.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B046_S1149.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B046_S1150.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B046_S1151.private.v1.jsonl",
)

SEGMENT = 1149
QUEUE_BATCH_ID = "pk_msggame-B046"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "6:4468:2",
    "6:4469:2",
    "6:4474:1",
    "6:4480:1",
    "6:4480:2",
    "6:4483:1",
    "6:4485:1",
    "6:4485:2",
    "6:4486:0",
    "6:4486:1",
    "6:4487:2",
    "6:4488:1",
    "6:4490:0",
    "6:4490:2",
    "6:4491:0",
    "6:4491:1",
    "6:4492:0",
    "6:4493:2",
)
TRANSLATIONS = {
    "6:4468:2": "에",
    "6:4469:2": "만…",
    "6:4474:1": "」에는\n",
    "6:4480:1": "\n하지만,",
    "6:4480:2": "…",
    "6:4483:1": "\n분명",
    "6:4485:1": "에게 맡겨",
    "6:4485:2": "면\n신속히 장악을 진행",
    "6:4486:0":
    "성의 수입 기반은 군의 취락에서 나옵니다…\n"
    "장악 진척이 더딘 듯하",
    "6:4486:1": "지만\n",
    "6:4487:2": "면해 주십시오…",
    "6:4488:1": "에게",
    "6:4490:0": "성주 「",
    "6:4490:2": "만…",
    "6:4491:0": "을(를) 배속해 주",
    "6:4491:1": "\n성주 「",
    "6:4492:0": "성주 「",
    "6:4493:2": "…",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    4468,
    4469,
    4474,
    4480,
    4483,
    4485,
    4486,
    4487,
    4488,
    4490,
    4491,
    4492,
    4493,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    4468: 4,
    **{
        record_id: 3
        for record_id in TARGET_RECORD_IDS
        if record_id != 4468
    },
}
BASE_RECORD_MAPPING = {
    record_id: record_id - 59
    for record_id in TARGET_RECORD_IDS
}
RAW_EXACT_BASE_RECORD_IDS = (
    4468,
    4490,
    4491,
    4492,
)
OPERAND_MASKED_BASE_RECORD_IDS = (
    4469,
    4474,
    4480,
    4483,
    4487,
    4488,
    4493,
)
SEMANTIC_SPLIT_BASE_RECORD_IDS = (
    4485,
    4486,
)
SLICE_PREFILL_COORDINATES = (
    "6:4468:0",
    "6:4468:3",
    "6:4469:0",
    "6:4469:1",
    "6:4470:0",
    "6:4470:1",
    "6:4471:0",
    "6:4472:0",
    "6:4472:1",
    "6:4473:0",
    "6:4473:2",
    "6:4474:0",
    "6:4474:2",
    "6:4475:0",
    "6:4475:1",
    "6:4476:0",
    "6:4476:1",
    "6:4476:2",
    "6:4477:0",
    "6:4477:1",
    "6:4478:0",
    "6:4479:0",
    "6:4480:0",
    "6:4481:0",
    "6:4481:1",
    "6:4482:0",
    "6:4483:0",
    "6:4483:2",
    "6:4484:0",
    "6:4484:1",
    "6:4485:0",
    "6:4486:2",
    "6:4487:0",
    "6:4487:1",
    "6:4488:0",
    "6:4488:2",
    "6:4489:0",
    "6:4489:1",
    "6:4490:1",
    "6:4491:2",
    "6:4492:1",
    "6:4492:2",
    "6:4493:0",
    "6:4493:1",
    "6:4494:0",
    "6:4494:1",
    "6:4495:0",
    "6:4496:0",
    "6:4496:1",
)
PREFILL_COMPANION_COORDINATES = (
    "6:4468:0",
    "6:4468:3",
    "6:4469:0",
    "6:4469:1",
    "6:4474:0",
    "6:4474:2",
    "6:4480:0",
    "6:4483:0",
    "6:4483:2",
    "6:4485:0",
    "6:4486:2",
    "6:4487:0",
    "6:4487:1",
    "6:4488:0",
    "6:4488:2",
    "6:4490:1",
    "6:4491:2",
    "6:4492:1",
    "6:4492:2",
    "6:4493:0",
    "6:4493:1",
)
PREFILL_ONLY_COORDINATES = tuple(
    coordinate
    for coordinate in SLICE_PREFILL_COORDINATES
    if coordinate not in PREFILL_COMPANION_COORDINATES
)
BASE_DONOR_COORDINATES = {
    coordinate: (
        f"{BLOCK_ID}:"
        f"{BASE_RECORD_MAPPING[coordinate_key_record]}:"
        f"{coordinate_key_literal}",
    )
    for coordinate in TARGET_COORDINATES
    for _, coordinate_key_record, coordinate_key_literal in (
        tuple(int(part) for part in coordinate.split(":")),
    )
}
BASE_DONOR_COORDINATES.update(
    {
        "6:4485:1": ("6:4426:1",),
        "6:4485:2": ("6:4426:1",),
        "6:4486:0": ("6:4427:0",),
        "6:4486:1": ("6:4427:0",),
    }
)
CONTEXT_RECORD_IDS = tuple(range(4465, 4500))
BOUNDARY_RECORD_IDS = (
    4465,
    4466,
    4467,
    4497,
    4498,
    4499,
)
EXPECTED_CALL_ROOTS = (
    1,
    21,
    82,
    178,
    190,
    226,
    268,
    322,
    562,
    568,
    748,
    1066,
    1096,
    1126,
    1174,
    1198,
)
EXPECTED_CALL_COUNTS = {
    1: (13, 9),
    21: (36, 26),
    **{
        operand: (14, 7)
        for operand in EXPECTED_CALL_ROOTS
        if operand not in (1, 21)
    },
}
EXPECTED_CALL_TERMINAL_SETS = {
    1: {"나", "소승", "소인", "이 몸", "저"},
    21: {
        "공주님",
        "그분",
        "그자",
        "누님",
        "님",
        "도련님",
        "쇼군님",
        "숙모님",
        "숙부님",
        "스님",
        "아버님",
        "어머님",
        "원숭이",
        "이놈",
        "저놈",
        "저놈 녀석",
        "주군",
        "주군님",
        "할머님",
        "할아버님",
        "형님",
    },
    82: {"이옵니다", "입니다", "있다", "있사옵니다", "있습니다"},
    178: {"있다", "있사옵니다", "있습니다"},
    190: {"으", "있사옵니다", "있습니다"},
    226: {
        "생각하오",
        "생각하옵나이다",
        "생각하옵니다",
        "생각한다",
        "생각합니다",
    },
    268: {"이오이까", "인가", "입니까"},
    322: {"다오", "주소서", "주시오"},
    562: {"다", "이오", "이옵니다", "입니다"},
    568: {"다", "이오", "입니다"},
    748: {"않는다", "않습니다"},
    1066: {"듯", "합시다"},
    1096: {"다", "하옵니다", "합니다"},
    1126: {"하리라", "합시다"},
    1174: {"", "고"},
    1198: {"받아", "받으실"},
}
SPEAKER_STYLE = {
    4468: "dynamic_castle_assignment_siege_aptitude_advice",
    4469: "dynamic_civil_assignment_reservation",
    4474: "dynamic_shared_trait_assignment_advice",
    4480: "dynamic_frontline_strategy_assignment_hesitation",
    4483: "dynamic_settlement_control_assignment_reluctance",
    4485: "dynamic_settlement_control_self_recommendation",
    4486: "dynamic_settlement_control_improvement_advice",
    4487: "dynamic_morale_assignment_refusal",
    4488: "dynamic_morale_assignment_request",
    4490: "dynamic_castle_lord_compatibility_hesitation",
    4491: "dynamic_castle_lord_compatibility_self_recommendation",
    4492: "dynamic_castle_lord_compatibility_request",
    4493: "dynamic_frontline_assignment_mismatch_complaint",
}
TERMINOLOGY_POLICY = (
    ("castle_siege", "공성"),
    ("assignment", "배속"),
    ("civil_administration", "정무"),
    ("trait", "특성"),
    ("covert_strategy", "조략"),
    ("settlement_control", "취락 장악"),
    ("morale", "사기"),
    ("castle_lord", "성주"),
    ("front_line", "전선"),
    ("dynamic_names", "「」로 경계 표시"),
)
BASIS = (
    "순정 PK 원문과 PC 영어·간체·번체, 동일 레코드 prefill "
    "조각을 함께 검토했다. Base 완료 번역은 raw-exact, "
    "call-operand-masked 또는 PK split semantic donor로 사용했다. "
    "split 레코드는 호출 경계에 맞춰 조각을 재배치했으며 PK의 "
    "런타임·VM 검증 상태는 승계하지 않았다."
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
EXPECTED_CHANGED_LITERAL_COUNT = 15

EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "87C21DB13F23A3525B814A100911F51B"
    "82066B021B00EC489E8CEDF8427C3BFF"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "7BA6ECC4CC9619109283AEBD40676115"
    "8289D7091543F60F0A6C24B1C761DBBC"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "CFCB331BB5E9A2C4495B79C520B4A8A8"
    "45209F2C941E0950D57D2ACB4BF4C431"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "B298FB458C20CBEFEC29E00698D2D31E"
    "02B9919A5058ECAF68FC94B4768DE7CF"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "B976A61B78D532DAAED09C81C82A3D6F"
    "A2EDC74B4674CCC0069BFEC26C1F5F54"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "67441606169C43E0EB935DF3D2ADB01B"
    "3390402848044F4D587D23114C4EB5AA"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "39A680A14C38975393A844F70E5ADADF"
    "F48899A225C9585C38B4924AD6882005"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "888BDA4C730E2D7BDD8F39230D7D33BD"
    "0EFAF21F114E96973D0DCC323C8D7790"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "29D8031F186EDFD4A09CAD224C4B2D65"
    "5F22093BDFBE427FD79F6BB993B4169E"
)
EXPECTED_BOUNDARY_SHA256 = (
    "5B22C7854334DFFAFE70CE098CA4C178"
    "C702C55FB11B98DF48CAF1176EEAB488"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "8B4096190C77099E6E6A1189D8D4DB5A"
    "4D9A2A86AE94A5BFCFA9F5316F939F27"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "97CE5D48A013C9B6AD69EE89AD8D1332"
    "006C947386FEFB832F40F713E5F9C33F"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "6D00B44DE185D24669C920C58B872EFC"
    "50E0C9D9E831ACF29C347359F7D98CA6"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "DB8D617C31CA7E8BE71F4C55F716B30E"
    "2E0F49AE645F6A42536624D9CB2AD1E2"
)
EXPECTED_RUNTIME_CONFLICT_SHA256 = (
    "CA0B81E77B4443FD3CAF4798DBD1E8DC"
    "88040B7D827CA9A748B07B1917473867"
)
EXPECTED_CANDIDATE_INTEGRITY_SHA256 = (
    "89C1FCA82FAB1A016E2EA06DC6EC54E2"
    "CC5AFB0C6FE0A7B24F384DEFE9264ABA"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "D9E65A8F123A7A4097D3058AA996C4DA"
    "F38307536D777EF5588BBE5122A45ED9"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "9E90745A418C614F8746B9E980239E95"
    "067EE8692541F61EACFBF503A50E78D9"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "3DB32C39BB4B4FF8B0AF741DCDA8E333"
    "888AE89D5DC336A297E1C9A912D4546D"
)
EXPECTED_CANDIDATE_SHA256 = (
    "CF1B451322E2E8613B5DFAA6B53B2A5E"
    "15438AAF1D216F134D74BD68B3B089F5"
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
    "pc_dialogue_full_retranslation_v0150_pk_s1149_template",
    TEMPLATE_PATH,
)
ENGINE = TEMPLATE.ENGINE
CALL_GRAPH = TEMPLATE.CALL_GRAPH
sha256_bytes = TEMPLATE.sha256_bytes
canonical_sha256 = TEMPLATE.canonical_sha256
coordinate_key = TEMPLATE.coordinate_key
literal_texts = TEMPLATE.literal_texts
gap_bytes = TEMPLATE.gap_bytes
read_jsonl = TEMPLATE.read_jsonl
context_records = TEMPLATE.context_records
runtime_controls = TEMPLATE.runtime_controls
mask_call_operands = TEMPLATE.mask_call_operands


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
        "CONTEXT_RECORD_IDS": CONTEXT_RECORD_IDS,
        "BOUNDARY_RECORD_IDS": BOUNDARY_RECORD_IDS,
        "EXPECTED_CHANGED_LITERAL_COUNT":
        EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_SOURCE_TARGET_SHA256":
        EXPECTED_SOURCE_TARGET_SHA256,
        "EXPECTED_CURRENT_TARGET_SHA256":
        EXPECTED_CURRENT_TARGET_SHA256,
        "EXPECTED_CONTEXT_CORPUS_SHA256":
        EXPECTED_CONTEXT_CORPUS_SHA256,
        "EXPECTED_GAP_CONTRACT_SHA256":
        EXPECTED_GAP_CONTRACT_SHA256,
        "EXPECTED_BOUNDARY_SHA256":
        EXPECTED_BOUNDARY_SHA256,
        "EXPECTED_RUNTIME_CONTROL_SHA256":
        EXPECTED_RUNTIME_CONTROL_SHA256,
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
        or len(visible) != 196
        or visible[0] != "6:4468:0"
        or visible[-1] != "6:4565:5"
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
        or queue_slice[0] != "6:4468:0"
        or queue_slice[-1] != "6:4496:1"
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
        len(prefilled) != 49
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
    if record_id in SEMANTIC_SPLIT_BASE_RECORD_IDS:
        return "pk_split_semantic_donor"
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
    manual_donor_values = {
        "6:4426:0":
        "아직 장악하지 못한 취락이 있군요…\n",
        "6:4426:1":
        "에게 맡겨 주신다면\n신속히 장악을 진행하",
        "6:4427:0":
        "성의 수입 기반은 군의 취락에서 나옵니다…\n"
        "장악 진척이 더딘 듯하지만\n",
        "6:4427:1": "에게 맡기시면 개선할 수 있",
    }
    for donor, expected in manual_donor_values.items():
        row = base_rows.get(donor)
        if (
            not base_row_is_approved(row)
            or str(row["translation"]) != expected
        ):
            raise RuntimeError(
                f"segment {SEGMENT} manual donor drifted: {donor}"
            )
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
            or (
                kind == "pk_split_semantic_donor"
                and (
                    raw_exact
                    or literal_exact
                    or len(base_literals) != 2
                )
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base match drifted: "
                f"{record_id}"
            )
        owners: list[str] = []
        translations: list[str] = []
        donor_values: list[tuple[str, ...]] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = (
                f"{BLOCK_ID}:{record_id}:{literal_id}"
            )
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
            if coordinate in BASE_DONOR_COORDINATES:
                refs = BASE_DONOR_COORDINATES[coordinate]
            elif record_id == 4485 and literal_id == 0:
                refs = ("6:4426:0",)
            elif record_id == 4486 and literal_id == 2:
                refs = ("6:4427:1",)
            else:
                refs = (
                    f"{BLOCK_ID}:{base_record_id}:{literal_id}",
                )
            rows = [base_rows.get(ref) for ref in refs]
            if not all(base_row_is_approved(row) for row in rows):
                if (
                    owners[-1] == "reviewed_invisible_companion"
                    and actual == pk_literals[literal_id]
                    and actual == base_current_literals[literal_id]
                ):
                    values = (actual,)
                else:
                    raise RuntimeError(
                        f"segment {SEGMENT} Base row drifted: "
                        f"{coordinate}"
                    )
            else:
                values = tuple(
                    str(row["translation"])
                    for row in rows
                    if row is not None
                )
                if (
                    kind != "pk_split_semantic_donor"
                    and actual != values[0]
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} Base translation drifted: "
                        f"{coordinate}"
                    )
                if (
                    kind == "pk_split_semantic_donor"
                    and coordinate
                    in {"6:4485:0", "6:4486:2"}
                    and actual != values[0]
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} split companion drifted: "
                        f"{coordinate}"
                    )
            translations.append(actual)
            donor_values.append(values)
            if coordinate in TRANSLATIONS:
                base_evidence.append(
                    (
                        coordinate,
                        refs,
                        kind,
                        sha256_bytes(pk_record.data),
                        sha256_bytes(base_record.data),
                        pk_literals[literal_id],
                        current_literals[literal_id],
                        actual,
                        values,
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
    manual_policy = (
        (
            "6:4485",
            TRANSLATIONS["6:4485:1"],
            TRANSLATIONS["6:4485:2"],
            manual_donor_values["6:4426:1"],
        ),
        (
            "6:4486",
            TRANSLATIONS["6:4486:0"],
            TRANSLATIONS["6:4486:1"],
            str(prefill_rows["6:4486:2"]["translation"]),
            manual_donor_values["6:4427:0"],
            manual_donor_values["6:4427:1"],
        ),
    )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
        or len(PREFILL_COMPANION_COORDINATES) != 21
        or len(PREFILL_ONLY_COORDINATES) != 28
    ):
        raise RuntimeError(
            f"segment {SEGMENT} assembly ownership drifted"
        )
    guarded_digest(
        "EXPECTED_BASE_CONTEXT_SHA256",
        (tuple(base_evidence), manual_policy),
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
        or len(TRANSLATIONS) != 18
        or TRANSLATIONS["6:4474:1"] != "」에는\n"
        or TRANSLATIONS["6:4485:1"] != "에게 맡겨"
        or TRANSLATIONS["6:4486:1"] != "지만\n"
        or TRANSLATIONS["6:4491:1"] != "\n성주 「"
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
        expected_graph_count, expected_terminal_count = (
            EXPECTED_CALL_COUNTS[operand]
        )
        if (
            len(graph) != expected_graph_count
            or len(terminals) != expected_terminal_count
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
            4485,
            (1, 1198, 1096),
            "root_1096_stem_repaired_but_root_1198_requires_flatten",
        ),
        (
            4486,
            (562, 1, 1066),
            "sentence_ending_before_connective_and_final_branch_conflicts",
        ),
        (
            4480,
            (1126, 268),
            "immutable_prefill_stem_and_one_question_leaf_conflict",
        ),
        (
            4469,
            (1, 1096),
            "immutable_prefill_action_stem_branch_conflict",
        ),
        "all_target_rows_runtime_pending",
        "base_runtime_state_not_inherited",
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
        "live_pk_call_graphs_reviewed": True,
        "runtime_morphology_conflict_detected": True,
        "all_speaker_branches_grammatical": False,
        "pk_split_semantic_adaptation":
        record_id in SEMANTIC_SPLIT_BASE_RECORD_IDS,
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
    TEMPLATE.assert_context_contracts(records_by_label)
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
                record_id in SEMANTIC_SPLIT_BASE_RECORD_IDS,
                "base_context_reference_coordinate":
                BASE_DONOR_COORDINATES[coordinate][0],
                "base_context_reference_coordinates":
                list(BASE_DONOR_COORDINATES[coordinate]),
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
    tampered_policy["6:4468:2"] += "X"
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
        prefix="s1149_tamper_",
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
        len(rows) != 18
        or len(validated) != 18
        or counts
        != Counter({"runtime_fragment_pending": 18})
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
                "segment": "pk_msggame_B046_S1149",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "slice_first_coordinate": "6:4468:0",
                "slice_last_coordinate": "6:4496:1",
                "slice_visible_count": 67,
                "exact_reuse_prefill_count": 49,
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
                "semantic_split_base_record_count":
                len(SEMANTIC_SPLIT_BASE_RECORD_IDS),
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
                "raw_exact_operand_masked_split_donors_guarded": True,
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
