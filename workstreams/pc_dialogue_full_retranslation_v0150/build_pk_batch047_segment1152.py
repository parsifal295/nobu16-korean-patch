#!/usr/bin/env python3
"""Build source-redacted PK B047 segment 1152 residual decisions."""

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
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch046_segment1149.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B047_S1152.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B047_S1153.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B047_S1154.private.v1.jsonl",
)

SEGMENT = 1152
QUEUE_BATCH_ID = "pk_msggame-B047"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = tuple(
    f"{BLOCK_ID}:{record_id}:{literal_id}"
    for record_id, arity in (
        (4566, 6),
        (4567, 3),
        (4568, 4),
        (4569, 4),
        (4570, 3),
        (4571, 4),
        (4572, 4),
        (4573, 2),
        (4574, 3),
        (4575, 3),
        (4576, 3),
        (4577, 5),
        (4578, 5),
        (4579, 5),
        (4580, 6),
        (4581, 6),
        (4582, 1),
    )
    for literal_id in range(arity)
)
TRANSLATIONS = {
    "6:4566:0": "등용을 거절한 「",
    "6:4566:1": "」은(는)\n",
    "6:4566:2": "라는 이명을 지닌 「",
    "6:4566:3": "」의 중신입니다\n",
    "6:4566:4": "께서 설득해 주시",
    "6:4566:5": "?",
    "6:4567:0": "등용한 「",
    "6:4567:1":
    "」에게서 제안이 왔습니다\n"
    "다른 이를 훈련해 주는 대가로\n"
    "바라는 것이 있다고 합니다… 이야기를 들어 보시겠",
    "6:4567:2": "?",
    "6:4568:0": "등용한 「",
    "6:4568:1": "」(이)라 불리는 「",
    "6:4568:2":
    "」에게서\n"
    "다른 이를 훈련하겠다는 제안이 왔습니다\n"
    "대신 바라는 것이 있다고 합니다… 이야기를 들어 보시겠",
    "6:4568:3": "?",
    "6:4569:0": "등용한 「",
    "6:4569:1": "」(이)라 불리는 「",
    "6:4569:2":
    "」에게서\n"
    "다른 이를 훈련하겠다는 제안이 왔습니다\n"
    "대신 바라는 것이 있다고 합니다… 이야기를 들어 보시겠",
    "6:4569:3": "?",
    "6:4570:0": "의 성주 「",
    "6:4570:1":
    "」이(가)\n"
    "저항을 멈추고 우리 가문에 항복하겠다고 합니다\n"
    "더 나은 조건을 얻도록 교섭",
    "6:4570:2": "?",
    "6:4571:0": "(이)라 불리는 「",
    "6:4571:1": "」의 성주\n",
    "6:4571:2":
    "이(가) 우리에게 항복하겠다고 합니다\n"
    "더 나은 조건을 얻도록 교섭",
    "6:4571:3": "?",
    "6:4572:0": "(이)라 불리는 「",
    "6:4572:1": "」의 성주\n",
    "6:4572:2":
    "이(가) 우리에게 항복하겠다고 합니다\n"
    "더 나은 조건을 얻도록 교섭",
    "6:4572:3": "?",
    "6:4573:0":
    "의 빼내기는 순조롭게 진행되었고\n"
    "성째로 귀순할 계책까지 있다고 합니다\n"
    "자세한 내용은 당사자에게 직접 들어 보시는 게",
    "6:4573:1": "고 봅니다",
    "6:4574:0": "은(는) 곧바로 “빼내기 제안에 응했",
    "6:4574:1":
    "”는 보고입니다\n"
    "성째로 귀순할 계책까지 있다고 합니다\n"
    "자세한 내용은 당사자에게 직접 들어 보시는 게",
    "6:4574:2": "고 봅니다",
    "6:4575:0": "라 평가받는 「",
    "6:4575:1":
    "」은(는)\n"
    "빼내기에 응했으며, 성째로 귀순할 계책도 있다고 합니다\n"
    "자세한 내용은 당사자에게 직접 들어 보시는 게",
    "6:4575:2": "고 봅니다",
    "6:4576:0": "라는 이명을 지닌 「",
    "6:4576:1":
    "」은(는)\n"
    "빼내기에 응했으며, 성째로 귀순할 계책도 있다고 합니다\n"
    "자세한 내용은 당사자에게 직접 들어 보시는 게",
    "6:4576:2": "고 봅니다",
    "6:4577:0":
    "의 빼내기가 난항을 겪고 있어\n"
    "이대로라면 실패로 끝날 것",
    "6:4577:1": "…\n",
    "6:4577:2": ",",
    "6:4577:3": "도움",
    "6:4577:4": "?",
    "6:4578:0":
    "은(는) 우리 가문의 빼내기 제안에 마음이 흔들리면서도\n"
    "아직 당장 응할 생각은",
    "6:4578:1":
    "고 하니, 한 번 더 밀어붙여야겠습니다…\n",
    "6:4578:2": ",",
    "6:4578:3": "도움",
    "6:4578:4": "?",
    "6:4579:0": "의 빼내기가 난항을 겪고 있습니",
    "6:4579:1":
    "…\n"
    "요구를 받아들이지 않으면 응하지 않을 모양입니다\n",
    "6:4579:2": ",",
    "6:4579:3": "도움",
    "6:4579:4": "?",
    "6:4580:0": "빼내기에 애를 먹고 있는 「",
    "6:4580:1": "」은(는)\n",
    "6:4580:2": "라 불릴 만큼 뛰어난 인재입니다\n",
    "6:4580:3": ",",
    "6:4580:4": "도움",
    "6:4580:5": "?",
    "6:4581:0": "라는 이명을 지닌",
    "6:4581:1": "\n빼내기에는 응하지",
    "6:4581:2": "만, 포기하기에는 아까운 인재입니다…\n",
    "6:4581:3": ",",
    "6:4581:4": "도움",
    "6:4581:5": "?",
    "6:4582:0":
    "자, 여기까지 주군을 이끌어 드렸습니다만\n"
    "설마 아무 대가 없이 끝내실 생각은 아니시겠지요\n"
    "제 바람을 들어 주시겠습니까?",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = tuple(range(4566, 4583))
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    4566: 6,
    4567: 3,
    4568: 4,
    4569: 4,
    4570: 3,
    4571: 4,
    4572: 4,
    4573: 2,
    4574: 3,
    4575: 3,
    4576: 3,
    4577: 5,
    4578: 5,
    4579: 5,
    4580: 6,
    4581: 6,
    4582: 1,
}
BASE_RECORD_MAPPING: dict[int, int] = {}
CONTEXT_RECORD_IDS = tuple(range(4563, 4586))
BOUNDARY_RECORD_IDS = (
    4563,
    4564,
    4565,
    4583,
    4584,
    4585,
)
SLICE_PREFILL_COORDINATES: tuple[str, ...] = ()
PREFILL_COMPANION_COORDINATES: tuple[str, ...] = ()
PREFILL_ONLY_COORDINATES: tuple[str, ...] = ()


def donor_group(record_id: int) -> tuple[str, ...]:
    if record_id == 4566:
        return ("2:250:0", "6:4099:2")
    if record_id in (4567, 4568, 4569):
        return ("2:343:0", "6:4099:2")
    if record_id in (4570, 4571, 4572):
        return ("6:4650:0", "6:1591:0")
    if record_id in (4573, 4574, 4575, 4576):
        return ("6:4555:0", "6:4555:1", "6:4555:2")
    if record_id == 4577:
        return ("6:4557:0", "6:4557:2", "6:4557:3")
    if record_id == 4578:
        return (
            "6:4558:0",
            "6:4558:1",
            "6:4558:2",
            "6:4558:3",
        )
    if record_id == 4579:
        return ("6:4559:0", "6:4559:2", "6:4559:3")
    if record_id == 4580:
        return (
            "6:4557:0",
            "6:4557:2",
            "6:4557:3",
            "15:335:0",
        )
    if record_id == 4581:
        return (
            "6:4557:0",
            "6:4557:2",
            "6:4557:3",
            "6:4559:0",
        )
    if record_id == 4582:
        return ("6:993:0", "0:1579:0")
    raise RuntimeError(f"segment {SEGMENT} missing donor group")


BASE_DONOR_COORDINATES = {
    coordinate: donor_group(int(coordinate.split(":")[1]))
    for coordinate in TARGET_COORDINATES
}
EXPECTED_CALL_ROOTS = (
    8,
    310,
    466,
    538,
    610,
    748,
    760,
    1048,
    1090,
    1168,
    1198,
)
EXPECTED_CALL_COUNTS = {
    8: (42, 32),
    **{
        operand: (14, 7)
        for operand in EXPECTED_CALL_ROOTS
        if operand != 8
    },
}
EXPECTED_CALL_TERMINAL_SETS = {
    8: {
        "공주님",
        "귀공",
        "귀하",
        "그대",
        "너",
        "네놈",
        "놈",
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
        "주군",
        "주군님",
        "할머님",
        "할아버님",
        "형님",
    },
    310: {"다", "하나이다", "합니다"},
    466: {"하다", "합니다", "하겠습니다", "하겠사옵니다"},
    538: {"다", "했습니다"},
    610: {"이겠지", "이겠지요", "이리라"},
    748: {"않는다", "않습니다"},
    760: {"않는다", "없다"},
    1048: {"좋다"},
    1090: {"다", "합니다"},
    1168: {"", "오"},
    1198: {"받아", "받으실"},
}
SPEAKER_STYLE = {
    4566: "dynamic_recruitment_refusal_persuasion_request",
    4567: "dynamic_training_offer_request",
    4568: "dynamic_alias_training_offer_request",
    4569: "dynamic_alias_training_offer_request_variant",
    4570: "dynamic_castle_lord_surrender_negotiation",
    4571: "dynamic_alias_castle_lord_surrender_negotiation",
    4572: "dynamic_alias_castle_lord_surrender_terms",
    4573: "dynamic_castle_wide_defection_success",
    4574: "dynamic_castle_wide_defection_immediate_acceptance",
    4575: "dynamic_alias_castle_wide_defection_success",
    4576: "dynamic_epithet_castle_wide_defection_success",
    4577: "dynamic_extraction_difficulty_support_request",
    4578: "dynamic_extraction_hesitation_support_request",
    4579: "dynamic_extraction_condition_support_request",
    4580: "dynamic_epithet_talent_support_request",
    4581: "dynamic_epithet_extraction_refusal_support_request",
    4582: "static_adviser_compensation_request",
}
TERMINOLOGY_POLICY = (
    ("recruitment", "등용"),
    ("training", "훈련"),
    ("castle_lord", "성주"),
    ("surrender", "항복"),
    ("negotiation", "교섭"),
    ("extraction", "빼내기"),
    ("castle_wide_defection", "성째로 귀순"),
    ("support", "도움·힘을 보태다"),
    ("wish", "바람"),
)
BASIS = (
    "순정 PK 원문과 PC 영어·간체·번체의 완전 레코드 문맥을 "
    "대조하고, 완료된 Base msggame의 등용·훈련·항복 교섭·"
    "빼내기·성째 귀순 용어와 문맥을 semantic donor로 "
    "재사용했다. PK 전용 분절과 호출 경계에는 문맥에 맞춰 "
    "조정했으며 Base 런타임·VM 검증 상태는 승계하지 않았다."
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
EXPECTED_CHANGED_LITERAL_COUNT = 63

EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "FDB0959421161D5F71D70A0FA4FC581A"
    "D0DD07C8CF2670AEA1E5AEB93C902EDD"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "2158DA26073D64C111AF1C407095B8D1"
    "3ECE00934E9FA7680AE88B30C4CBE96C"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "4F53CDA18C2BAA0C0354BB5F9A3ECBE"
    "5ED12AB4D8E11BA873C2F11161202B945"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "2158DA26073D64C111AF1C407095B8D1"
    "3ECE00934E9FA7680AE88B30C4CBE96C"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "BBBD7DB8B90CDDB9A8269EC3F0307A66"
    "9B5D940D644C59F18A05DFE1426ABD6A"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "8D1B3BC4DEFB36620242F02147102A2B"
    "91E44E76465EFB503E52AC3E9E17B07B"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "A928E93CF9F8CD0C73B116CE0787BBFD"
    "BF16B4D83AF84BB2ABA1E005ACD12A78"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "5A55EDB8B21537235010A8AA5483C6F0"
    "5AED2FDA3F5830A3E5BF9ABAEEA49FDA"
)
EXPECTED_BOUNDARY_SHA256 = (
    "497CF2C4912EE0BC45DAD18B5287946E"
    "5A87127619DB865BE7199081DA44F3F6"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "6358B272B883F650CCD41543F283848D"
    "ED3436BF8350733273B2D5A40C2AAA69"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "2943797CFD7C0CA5A3388BAE39D60135"
    "613C1DBC776E20B8CFC447BC1B7EDD48"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "2E9E58A030A3DE3B38A89EB0AA634AE8"
    "59F6136A313806561A4133547DD83231"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "A35E6E7227ADF9D1446C19CF07FFA8D0"
    "E2EC1E35D3B50574E4EE1F25E00A6398"
)
EXPECTED_RUNTIME_CONFLICT_SHA256 = (
    "11EA09D659BD10D6B643292375F9811F"
    "61E235C608F4F91D0053099A13E4E18F"
)
EXPECTED_CANDIDATE_INTEGRITY_SHA256 = (
    "A172C7D0FF79E82E0AE83626B6B8DAF7"
    "D3FA85CEA682E3B27A02BB8546888D32"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "683AC9EA4801B8258CBF309A59384F25"
    "E4DC6AC8238968DBFAEF349CEAA2C767"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "E6BCEF5E3C04DEF75C3832384C81D00E"
    "2FE654B895B6A443CEE76510F48F0427"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "2C2F0317A800015842D3814AF243542D"
    "C1F2114327D91D0C2A992A0307B8CEC6"
)
EXPECTED_CANDIDATE_SHA256 = (
    "7DA23CEB2F088B04959DE1322989BCDC"
    "942C6AD2F19BB974C6E9CD79039AA3A5"
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
    "pc_dialogue_full_retranslation_v0150_pk_s1152_template",
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


def guarded_digest(label: str, value: Any, expected: str) -> str:
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
        len(queue_rows) != 61
        or len(visible) != 199
        or visible[0] != "6:4566:0"
        or visible[-1] != "6:4626:2"
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
        or queue_slice != TARGET_COORDINATES
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
    if prefilled:
        raise RuntimeError(f"segment {SEGMENT} prefill drifted")
    guarded_digest(
        "EXPECTED_PREFILLED_COORDINATE_SHA256",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
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
        if row.get("resource") == "base_msggame"
        and "translation" in row
    }
    donor_evidence: list[tuple[Any, ...]] = []
    for coordinate in TARGET_COORDINATES:
        refs = BASE_DONOR_COORDINATES[coordinate]
        rows = [base_rows.get(ref) for ref in refs]
        if not all(base_row_is_approved(row) for row in rows):
            raise RuntimeError(
                f"segment {SEGMENT} Base donor drifted: "
                f"{coordinate}"
            )
        donor_evidence.append(
            (
                coordinate,
                refs,
                tuple(
                    str(row["translation"])
                    for row in rows
                    if row is not None
                ),
                tuple(
                    str(row["runtime_review"])
                    for row in rows
                    if row is not None
                ),
            )
        )
    guarded_digest(
        "EXPECTED_BASE_CONTEXT_SHA256",
        tuple(donor_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        source = records_by_label["jp"][key]
        source_literals = literal_texts(
            records_by_label["jp"], key
        )
        current_literals = literal_texts(
            records_by_label["current"], key
        )
        translations = tuple(
            TRANSLATIONS[
                f"{BLOCK_ID}:{record_id}:{literal_id}"
            ]
            for literal_id in range(EXPECTED_ARITY[record_id])
        )
        if (
            len(source_literals) != EXPECTED_ARITY[record_id]
            or len(current_literals) != EXPECTED_ARITY[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} arity drifted: {record_id}"
            )
        assembly_evidence.append(
            (
                record_id,
                source_literals,
                current_literals,
                translations,
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(source)
                ),
                runtime_controls(source),
                donor_group(record_id),
                "pk_exclusive_semantic_corpus",
            )
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
        or len(TRANSLATIONS) != 67
        or sum(EXPECTED_ARITY.values()) != 67
        or TRANSLATIONS["6:4566:0"] != "등용을 거절한 「"
        or TRANSLATIONS["6:4573:0"].splitlines()[1]
        != "성째로 귀순할 계책까지 있다고 합니다"
        or TRANSLATIONS["6:4577:0"].splitlines()[1]
        != "이대로라면 실패로 끝날 것"
        or TRANSLATIONS["6:4582:0"].splitlines()[2]
        != "제 바람을 들어 주시겠습니까?"
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
            (4566,),
            (8, 1198, 748),
            "speaker_and_request_suffix_cross_product_conflict",
        ),
        (
            (4567, 4568, 4569),
            (310,),
            "statement_register_leaf_after_question_stem",
        ),
        (
            (4573, 4574, 4575, 4576),
            (1048,),
            "standalone_adjective_requires_protected_space",
        ),
        (
            (4577, 4578, 4579, 4580, 4581),
            (8, 1168, 1198, 748),
            "optional_vocative_and_double_suffix_cross_product",
        ),
        (
            (4574, 4578, 4579),
            (538, 760, 1090),
            "additional_register_leaf_stem_conflict",
        ),
        (
            4582,
            (),
            "static_pk_policy_still_requires_pk_runtime_review",
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
        "runtime_category": (
            "pk_static_literal_manual_retranslation"
            if record_id == 4582
            else "pk_dynamic_fragment_base_semantic_donor"
        ),
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
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal": True,
        "base_match_kind": "pk_exclusive_semantic_corpus",
        "base_semantic_donor_coordinates":
        list(donor_group(record_id)),
        "complete_record_assembly_reviewed": True,
        "all_same_record_literals_reviewed": True,
        "all_slice_rows_reviewed": True,
        "manual_pc_english_simplified_traditional_review": True,
        "live_pk_call_graphs_reviewed": True,
        "runtime_morphology_conflict_detected": True,
        "all_speaker_branches_grammatical": False,
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
    TEMPLATE.TEMPLATE.assert_context_contracts(
        records_by_label
    )
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
                "all_same_record_literals_reviewed": True,
                "all_slice_rows_reviewed": True,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "base_wording_contextually_adapted": True,
                "base_context_reference_coordinate":
                BASE_DONOR_COORDINATES[coordinate][0],
                "base_context_reference_coordinates":
                list(BASE_DONOR_COORDINATES[coordinate]),
                "base_context_is_automatic_reuse": False,
                "base_match_kind":
                "pk_exclusive_semantic_corpus",
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
                    records_by_label, record_id
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
    tampered_policy["6:4566:0"] += "X"
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
        prefix="s1152_tamper_",
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
        len(rows) != 67
        or len(validated) != 67
        or counts
        != Counter({"runtime_fragment_pending": 67})
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
                "segment": "pk_msggame_B047_S1152",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "slice_first_coordinate": TARGET_COORDINATES[0],
                "slice_last_coordinate": TARGET_COORDINATES[-1],
                "slice_visible_count": 67,
                "exact_reuse_prefill_count": 0,
                "residual_count": len(rows),
                "scope_classification_counts": dict(counts),
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "pk_exclusive_record_count":
                len(TARGET_RECORD_IDS),
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
                "manual_pk_jp_pc_en_sc_tc_review": True,
                "complete_multi_literal_records_guarded": True,
                "pk_exclusive_semantic_donors_guarded": True,
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
